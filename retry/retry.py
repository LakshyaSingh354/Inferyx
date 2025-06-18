from retry.utils import RetryJob
import time
from job_queue.job_store import mark_job_retry, mark_job_failed, expire_job
from job_queue.redis_client import get_redis_client
from metrics.metrics import retries_total, jobs_failed_after_retries_total, retry_count_hist
from config import config
r = get_redis_client()



def handle_job_failure(job):
    if job.get("retry_count", 0) < config.MAX_RETRIES:
        retry_count = job.get("retry_count", 0) + 1
        retries_total.inc()
        # Exponential backoff: base * (2 ** (retry_count - 1))
        backoff = min(config.RETRY_BACKOFF_SECONDS * (2 ** (retry_count - 1)), config.MAX_BACKOFF_SECONDS)
        # backoff = 1
        retry_job = RetryJob(
            request_id=job["request_id"],
            input=job["input"],
            model_id=job["model_id"],
            timestamp=job["timestamp"],
            retry_count=retry_count,
            next_retry_time=int(time.time()) + backoff
        )
        r.rpush(config.RETRY_QUEUE_KEY, retry_job.model_dump_json())
    else:
        retry_count_hist.observe(job.get("retry_count", 0))
        jobs_failed_after_retries_total.inc()
        expire_job(job["request_id"])

