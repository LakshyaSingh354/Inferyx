from job_queue.schema import Job
from job_queue.redis_client import get_redis_client
from job_queue.job_store import init_job_status, mark_job_skipped
from metrics.metrics import jobs_skipped_total

MAX_QUEUE_SIZE = 500

def enqueue_job(job: Job):
    redis_client = get_redis_client()
    request_id = job.request_id
    with redis_client.pipeline() as pipe:
        pipe.multi()
        if redis_client.llen("inference_queue") < MAX_QUEUE_SIZE:
            pipe.rpush("inference_queue", job.model_dump_json())
        else:
            mark_job_skipped(job.request_id)
            log_file = open("skipped_jobs.log", "a")
            log_file.write(f"{job.request_id}\n")
            log_file.close()
            jobs_skipped_total.inc()

            return False
        init_job_status(request_id)
        pipe.execute()
        return True