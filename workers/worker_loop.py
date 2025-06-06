import json
import time
import redis
from model.infer import InferenceFailure, infer_batch
from job_queue.job_store import mark_job_processing, mark_job_done, mark_job_failed
from job_queue.redis_client import get_redis_client
from metrics.metrics import inference_latency, jobs_processed_total, jobs_failure_total, worker_queue_size_gauge, worker_status_gauge

r = get_redis_client()

def worker_loop(worker_id):
    worker_key = f"worker_status:{worker_id}"
    print(f"[Worker-{worker_id}] Starting worker loop...")
    while True:
        try:
            r.set(worker_key, json.dumps({"status": "idle", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(0)  # idle
            _, batch_raw = r.blpop("worker_queue")
            r.set(worker_key, json.dumps({"status": "busy", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(1)  # busy
            batch = json.loads(batch_raw)
            print(f"[Worker-{worker_id}] Received batch of {len(batch)} jobs")

            for job in batch:
                mark_job_processing(job["request_id"])
            print(f"[Worker-{worker_id}] Jobs marked as processing")
            inputs = [job["input"] for job in batch]
            model_id = batch[0]["model_id"]
            print(f"[Worker-{worker_id}] Model ID: {model_id}")
            try:
                start_time = time.time()
                outputs = infer_batch(inputs, model_id)
                print(f"[Worker-{worker_id}] Outputs Received")
                for job, output in zip(batch, outputs):
                    mark_job_done(job["request_id"], output)
                inference_latency.observe(time.time() - start_time)
                print(f"[Worker-{worker_id}] Inference latency: {time.time() - start_time}")
                jobs_processed_total.inc(len(batch))

            except MemoryError as e:
                print(f"[Worker-{worker_id}] OOM error")
                for job in batch:
                    mark_job_failed(job["request_id"], "OOM error")
                jobs_failure_total.inc(len(batch))
            except InferenceFailure as e:
                print(f"[Worker-{worker_id}] Inference failed: {str(e)}")
                for job in batch:
                    mark_job_failed(job["request_id"], "Inference failed [MOCK]")
                jobs_failure_total.inc(len(batch))
            except Exception as e:
                print(f"[Worker-{worker_id}] Inference failed: {str(e)}")
                for job in batch:
                    mark_job_failed(job["request_id"], "Inference failed [UNKNOWN]")
        
        except Exception as e:
            print(f"[Worker-{worker_id}] Fatal error: {str(e)}")
            r.set(worker_key, json.dumps({"status": "error", "timestamp": time.time(), "error": str(e)}))
            time.sleep(2)  # optional cooldown
        finally:
            r.set(worker_key, json.dumps({"status": "idle", "timestamp": time.time()}))
            worker_status_gauge.labels(worker_id=worker_id).set(0)  # idle