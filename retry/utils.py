from pydantic import BaseModel

class RetryJob(BaseModel):
    request_id: str
    input: str
    model_id: str
    retry_count: int = 0
    next_retry_time: int = 0

RETRY_QUEUE_KEY = "retry_queue"