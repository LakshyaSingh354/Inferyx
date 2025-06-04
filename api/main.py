from fastapi import FastAPI, Request, Response, Depends
from model.infer import infer_batch, InferenceFailure
import uvicorn
from fastapi.responses import JSONResponse
from api.schema import InferRequest
from api.auth import verify_api_key
from job_queue.utils import create_job

from job_queue.producer import enqueue_job



app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Inferyx is running"}

@app.post("/infer")
async def infer(
    request: InferRequest,
    api_key: str = Depends(verify_api_key)
):
    job = create_job(request.input, request.model_id)
    enqueue_job(job)
    return JSONResponse(content={"request_id": job["request_id"], "status": "queued"}, status_code=200)

@app.get("/result/{request_id}")
async def get_result(request_id: str):
    return {"result": "queued"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)