from pydantic import BaseModel
from typing import List, Optional

class InferRequest(BaseModel):
    input: str
    model_id: Optional[str] = "mock"
