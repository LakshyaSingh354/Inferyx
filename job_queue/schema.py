from pydantic import BaseModel

class Job(BaseModel):
    request_id: str
    input: str
    model_id: str
    timestamp: str