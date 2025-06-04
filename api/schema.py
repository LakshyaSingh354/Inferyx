from pydantic import BaseModel
from typing import List, Optional

class InferRequest(BaseModel):
    batch_inputs: List[str]
    model_id: Optional[str] = "mock"
