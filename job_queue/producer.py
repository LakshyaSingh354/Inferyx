
from job_queue.schema import Job
from job_queue.redis_client import get_redis_client

def enqueue_job(job: Job):
    redis_client = get_redis_client()
    redis_client.rpush("queue", job.model_dump_json())