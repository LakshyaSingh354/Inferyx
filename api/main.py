import os
import shutil

PROMETHEUS_MULTIPROC_DIR = "/tmp/prometheus_multiproc"
os.environ["PROMETHEUS_MULTIPROC_DIR"] = PROMETHEUS_MULTIPROC_DIR

from fastapi import FastAPI, Request, Response, Depends
from model.infer import infer_batch, InferenceFailure
import uvicorn
from fastapi.responses import JSONResponse
from api.schema import InferRequest
from api.auth import verify_api_key
from job_queue.utils import create_job
from metrics.metrics import inference_requests_total
from job_queue.producer import enqueue_job
from job_queue.job_store import init_job_status, get_job_status
from batch.batching_engine import batching_loop
import dotenv
import threading
from metrics.serve import start_metrics_server
from contextlib import asynccontextmanager
from workers.worker_pool import start_worker_pool
import sys

# logfile = open("output.log", "a")
# sys.stdout = logfile
# sys.stderr = logfile


dotenv.load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=start_metrics_server, daemon=True).start()
    threading.Thread(target=batching_loop, daemon=True).start()
    threading.Thread(target=start_worker_pool, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

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
    print("Incrementing inference requests total")
    inference_requests_total.inc()
    return JSONResponse(content={"request_id": job.request_id, "status": "queued"}, status_code=200)



@app.get("/result/{request_id}")
async def get_result(request_id: str):
    return get_job_status(request_id)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)