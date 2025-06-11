import os
import shutil
from prometheus_client import start_http_server, CollectorRegistry, multiprocess, generate_latest
import time
import logging

from job_queue.redis_client import get_redis_client
from metrics.metrics import inference_queue_size_gauge, worker_queue_size_gauge, retry_queue_size_gauge

logger = logging.getLogger(__name__)

r = get_redis_client()

def start_metrics_server():
    logger.info("[Metrics] Starting Prometheus exporter at :8080/metrics")
    if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = None
    start_http_server(8080, registry=registry if registry else None)
    while True:
        inference_queue_size_gauge.set(r.llen("inference_queue"))
        worker_queue_size_gauge.set(r.llen("worker_queue"))
        retry_queue_size_gauge.set(r.llen("retry_queue"))
        time.sleep(1)
