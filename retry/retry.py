from retry.utils import RETRY_QUEUE_KEY
from retry.utils import RetryJob
import time
from job_queue.job_store import mark_job_retry, mark_job_failed, expire_job
from job_queue.redis_client import get_redis_client
from metrics.metrics import retries_total, jobs_failed_after_retries_total, retry_count_hist

r = get_redis_client()

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
MAX_BACKOFF_SECONDS = 30  # 5 minutes, for example

def handle_job_failure(job):
    if job.get("retry_count", 0) < MAX_RETRIES:
        retry_count = job.get("retry_count", 0) + 1
        retries_total.inc()
        # Exponential backoff: base * (2 ** (retry_count - 1))
        backoff = min(RETRY_BACKOFF_SECONDS * (2 ** (retry_count - 1)), MAX_BACKOFF_SECONDS)
        # backoff = 1
        retry_job = RetryJob(
            request_id=job["request_id"],
            input=job["input"],
            model_id=job["model_id"],
            timestamp=job["timestamp"],
            retry_count=retry_count,
            next_retry_time=int(time.time()) + backoff
        )
        r.rpush(RETRY_QUEUE_KEY, retry_job.model_dump_json())
    else:
        retry_count_hist.observe(job.get("retry_count", 0))
        jobs_failed_after_retries_total.inc()
        expire_job(job["request_id"])

