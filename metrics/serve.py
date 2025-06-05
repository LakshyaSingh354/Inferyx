from prometheus_client import start_http_server
import time

from job_queue.redis_client import get_redis_client
from metrics.metrics import queue_size_gauge

r = get_redis_client()

def start_metrics_server():
    print("[Metrics] Starting Prometheus exporter at :8080/metrics")
    start_http_server(8080)
    while True:
        try:
            qlen = r.llen("inference_queue")
            queue_size_gauge.set(qlen)
        except:
            pass
        time.sleep(1)
