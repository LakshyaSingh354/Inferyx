from datetime import datetime, timezone
import json
import time
import redis
import logging
from model.infer import InferenceFailure, infer_batch
from job_queue.job_store import mark_job_processing, mark_job_done, mark_job_failed
from job_queue.redis_client import get_redis_client
from metrics.metrics import inference_latency, jobs_processed_total, jobs_failure_total, worker_queue_size_gauge, worker_status_gauge
from retry.retry import handle_job_failure

logger = logging.getLogger(__name__)

r = get_redis_client()

def worker_loop(worker_id):
    worker_key = f"worker_status:{worker_id}"
    logger.info(f"[Worker-{worker_id}] Starting worker loop...")
    while True:
        try:
            r.set(worker_key, json.dumps({"status": "idle", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(0)  # idle
            _, batch_raw = r.blpop("worker_queue")
            r.set(worker_key, json.dumps({"status": "busy", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(1)  # busy
            batch = json.loads(batch_raw)

            for job in batch:
                mark_job_processing(job["request_id"])
            inputs = [job["input"] for job in batch]
            model_id = batch[0]["model_id"]
            try:
                outputs = infer_batch(inputs, model_id)
                for job, output in zip(batch, outputs):
                    job_start_time = datetime.fromisoformat(job["timestamp"])
                    job_end_time = datetime.now(timezone.utc)

                    inference_latency.observe((job_end_time - job_start_time).total_seconds())
                    # print(f"[Worker-{worker_id}] Inference latency: {(job_end_time - job_start_time).total_seconds()}")
                    mark_job_done(job["request_id"], output)
                jobs_processed_total.inc(len(batch))

            except MemoryError as e:
                logger.error(f"[Worker-{worker_id}] OOM error")
                for job in batch:
                    mark_job_failed(job["request_id"], "OOM error")
                    handle_job_failure(job)
                jobs_failure_total.inc(len(batch))
            except InferenceFailure as e:
                logger.error(f"[Worker-{worker_id}] Inference failed: {str(e)}")
                for job in batch:
                    mark_job_failed(job["request_id"], "Inference failed [MOCK]")
                    handle_job_failure(job)
                jobs_failure_total.inc(len(batch))
            except Exception as e:
                logger.error(f"[Worker-{worker_id}] Inference failed: {str(e)}")
                print(e)
                for job in batch:
                    mark_job_failed(job["request_id"], "Inference failed [UNKNOWN]")
        except Exception as e:
            logger.error(f"[Worker-{worker_id}] Fatal error: {str(e)}")
            r.set(worker_key, json.dumps({"status": "error", "timestamp": time.time(), "error": str(e)}))
            time.sleep(2)  # optional cooldown
        finally:
            r.set(worker_key, json.dumps({"status": "idle", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(0)  # idle

            status = r.hget("worker_status", worker_id)
            if status == "terminating" or status == "delete":
                worker_status_gauge.labels(worker_id=worker_id).set(-1)
                logger.info(f"[Worker-{worker_id}] Terminating worker")
                r.hset("worker_status", worker_id, "delete")

                break