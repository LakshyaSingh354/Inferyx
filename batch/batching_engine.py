import json
import time
import logging

from job_queue.job_store import mark_job_waiting, mark_job_failed
from job_queue.redis_client import get_redis_client
from metrics.metrics import jobs_failure_total, batches_processed_total, batch_size_hist
from retry.retry import handle_job_failure
from config import config
logger = logging.getLogger(__name__)

r = get_redis_client()


def batching_loop():
    logger.info("[Batching Engine] Starting batching loop...")
    while True:
        batch = []
        start_time = time.time()

        while len(batch) < config.MAX_BATCH_SIZE:
            job_str = r.lpop(config.INFERENCE_QUEUE_KEY)
            if job_str:
                try:
                    job = json.loads(job_str)
                    batch.append(job)
                except Exception as e:
                    logger.error(f"[Batching Engine] Error parsing job: {e}")

            else:
                time.sleep(0.01)

            if time.time() - start_time > config.MAX_WAIT_TIME:
                break

        if batch:
            logger.info(f"[Batching Engine] Batching {len(batch)} jobs...")
            try:
                for job in batch:
                    mark_job_waiting(job["request_id"])
                r.rpush(config.WORKER_QUEUE_KEY, json.dumps(batch))
                batch_size_hist.observe(len(batch))
                batches_processed_total.inc()
            except Exception as e:
                logger.error(f"[Batching Engine] Error processing batch: {e}")
                for job in batch:
                    mark_job_failed(job["request_id"])
                    jobs_failure_total.inc(len(batch))
                    handle_job_failure(job)

if __name__ == "__main__":
    batching_loop()