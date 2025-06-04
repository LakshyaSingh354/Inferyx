import uuid
from datetime import datetime, timezone

from job_queue.schema import Job


def create_job(input_text: str, model_id: str = "mock") -> Job:
    return Job(
        request_id=str(uuid.uuid4()),
        input=input_text,
        model_id=model_id,
        timestamp=datetime.now(timezone.utc).isoformat()
    )