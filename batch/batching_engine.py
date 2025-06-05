import json
import time

from job_queue.job_store import mark_job_processing, mark_job_done, mark_job_failed
from job_queue.redis_client import get_redis_client
from model.infer import infer_batch
from metrics.metrics import jobs_processed_total, jobs_failure_total, batches_processed_total, batch_size_hist, inference_latency

r = get_redis_client()

INFERENCE_QUEUE_KEY = "inference_queue"
MAX_BATCH_SIZE = 4
MAX_WAIT_TIME = 1.0

def batching_loop():
    print("[Batching Engine] Starting batching loop...")
    while True:
        batch = []
        start_time = time.time()

        while len(batch) < MAX_BATCH_SIZE:
            job_str = r.lpop(INFERENCE_QUEUE_KEY)
            if job_str:
                try:
                    job = json.loads(job_str)
                    batch.append(job)
                except Exception as e:
                    print(f"[Batching Engine] Error parsing job: {e}")

            else:
                time.sleep(0.01)

            if time.time() - start_time > MAX_WAIT_TIME:
                break

        if batch:
            print(f"[Batching Engine] Batching {len(batch)} jobs...")
            try:
                for job in batch:
                    mark_job_processing(job["request_id"])
                inputs = [job["input"] for job in batch]
                start = time.time()
                results = infer_batch(inputs)
                inference_latency.observe(time.time() - start)

                for job, result in zip(batch, results):
                    mark_job_done(job["request_id"], result)
                    jobs_processed_total.inc(len(batch))
                batches_processed_total.inc()
                batch_size_hist.observe(len(batch))
            except Exception as e:
                print(f"[Batching Engine] Error processing batch: {e}")
                for job in batch:
                    mark_job_failed(job["request_id"])
                    jobs_failure_total.inc(len(batch))

if __name__ == "__main__":
    batching_loop()