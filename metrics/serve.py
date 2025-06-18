import os
import shutil
from prometheus_client import start_http_server, CollectorRegistry, multiprocess, generate_latest
import time
import logging

from job_queue.redis_client import get_redis_client
from metrics.metrics import inference_queue_size_gauge, worker_queue_size_gauge, retry_queue_size_gauge
from config import config
logger = logging.getLogger(__name__)

r = get_redis_client()

def start_metrics_server():
    logger.info(f"[Metrics] Starting Prometheus exporter at :{config.METRICS_PORT}/metrics")
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = None
    start_http_server(config.METRICS_PORT, registry=registry if registry else None)
    while True:
        inference_queue_size_gauge.set(r.llen(config.INFERENCE_QUEUE_KEY))
        worker_queue_size_gauge.set(r.llen(config.WORKER_QUEUE_KEY))
        retry_queue_size_gauge.set(r.llen(config.RETRY_QUEUE_KEY))
        time.sleep(1)
