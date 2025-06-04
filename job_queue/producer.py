from job_queue.schema import Job
from job_queue.redis_client import get_redis_client
from job_queue.job_store import init_job_status

def enqueue_job(job: Job):
    redis_client = get_redis_client()
    request_id = job.request_id
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.rpush("inference_queue", job.model_dump_json())
        init_job_status(request_id)
        pipe.execute()