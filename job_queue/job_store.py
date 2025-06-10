from job_queue.redis_client import get_redis_client
from fastapi.responses import JSONResponse

r = get_redis_client()

def init_job_status(request_id: str):
    """
    Initialize job status as pending.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "pending",
        "result": ""
    })

def mark_job_waiting(request_id: str):
    """
    Update job status to waiting.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "waiting",
        "result": ""
    })

def mark_job_processing(request_id: str):
    """
    Update job status to processing.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "processing",
        "result": ""
    })

def mark_job_done(request_id: str, result: str):
    """
    Update job status to done and store result.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "done",
        "result": result
    })

def mark_job_failed(request_id: str, error: str = "error"):
    """
    Update job status to failed and optionally store error message.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "failed",
        "result": error
    })

def mark_job_retry(request_id: str, retry_count: int, next_retry_time: int):
    """
    Update job status to retry.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "retry",
        "result": "",
        "retry_count": retry_count,
        "next_retry_time": next_retry_time
    })

def mark_job_skipped(request_id: str):
    """
    Update job status to skipped.
    """
    r.hset(f"job:{request_id}", mapping={
        "status": "skipped",
        "result": ""
    })
def get_job_status(request_id: str):
    """
    Fetch status and result of a job.
    Returns dict with keys: status, result
    """
    data = r.hgetall(f"job:{request_id}")
    if not data:
        return JSONResponse(content={"status": "not_found"}, status_code=404)
    return data

def expire_job(request_id: str, ttl_seconds: int = 60):
    """
    Optional: set expiry for job metadata
    """
    r.expire(f"job:{request_id}", ttl_seconds)