import time
from retry.utils import RetryJob
from job_queue.redis_client import get_redis_client
from job_queue.job_store import mark_job_retry
from config import config
r = get_redis_client()

def retry_worker_loop():
    while True:
        job_json = r.lpop(config.RETRY_QUEUE_KEY)
        if job_json:
            job = RetryJob.model_validate_json(job_json)
            if time.time() >= job.next_retry_time:
                # Re-enqueue to inference queue for processing
                r.rpush(config.INFERENCE_QUEUE_KEY, job.model_dump_json())
                mark_job_retry(job.request_id, job.retry_count, job.next_retry_time)
            else:
                # Not time yet, push back to retry queue
                r.rpush(config.RETRY_QUEUE_KEY, job_json)
                time.sleep(1)
        else:
            time.sleep(1)
