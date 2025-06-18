from pydantic import BaseModel

class RetryJob(BaseModel):
    request_id: str
    input: str
    timestamp: str
    model_id: str
    retry_count: int = 0
    next_retry_time: int = 0

