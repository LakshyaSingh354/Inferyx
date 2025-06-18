import os
import logging
import time

from caching.cache_inference import make_cache_key
from config import config

os.environ["PROMETHEUS_MULTIPROC_DIR"] = config.PROMETHEUS_MULTIPROC_DIR

print("Starting Inferyx!!!")

from fastapi import FastAPI, Request, Response, Depends
from model.infer import infer_batch, InferenceFailure
import uvicorn
from fastapi.responses import JSONResponse
from api.schema import InferRequest
from api.auth import verify_api_key
from job_queue.utils import create_job
from metrics.metrics import inference_requests_total, cache_hits_total, cache_misses_total, jobs_processed_total, inference_latency
from job_queue.producer import enqueue_job
from job_queue.job_store import init_job_status, get_job_status, mark_job_done
from batch.batching_engine import batching_loop
import dotenv
import threading
from metrics.serve import start_metrics_server
from contextlib import asynccontextmanager
from workers.worker_pool import start_worker_pool
import sys
from retry.retry_worker import retry_worker_loop
from job_queue.redis_client import get_redis_client

logging.basicConfig(level=logging.INFO)

logging.getLogger("model.infer").setLevel(logging.INFO)
logging.getLogger("inferyx").setLevel(logging.INFO)
logging.getLogger("batch.batching_engine").setLevel(logging.WARNING)
logging.getLogger("metrics.serve").setLevel(logging.WARNING)
logging.getLogger("workers.worker_pool").setLevel(logging.INFO)
# logging.getLogger("workers.worker_loop").setLevel(logging.INFO)


dotenv.load_dotenv()

r = get_redis_client()

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=start_metrics_server, daemon=True).start()
    threading.Thread(target=batching_loop, daemon=True).start()
    threading.Thread(target=start_worker_pool, daemon=True).start()
    threading.Thread(target=retry_worker_loop, daemon=True).start()
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
    start_time = time.time()
    job = create_job(request.input, request.model_id)

    # 🚨 Check cache first
    cache_key = make_cache_key(request.input, request.model_id)
    cached_result = r.get(cache_key)
    inference_requests_total.inc()
    if cached_result:
        # 🔥 Skip the queue — just mark as done
        mark_job_done(job.request_id, cached_result)
        inference_latency.observe(time.time() - start_time)
        cache_hits_total.inc()
        jobs_processed_total.inc()
        return JSONResponse(
            content={"request_id": job.request_id, "status": "done", "cached": True},
            status_code=200
        )

    # 🚀 Not cached → enqueue
    if enqueue_job(job):
        cache_misses_total.inc()
        return JSONResponse(
            content={"request_id": job.request_id, "status": "queued"},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"request_id": job.request_id, "status": "skipped"},
            status_code=429
        )


@app.get("/result/{request_id}")
async def get_result(request_id: str):
    return get_job_status(request_id)

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)