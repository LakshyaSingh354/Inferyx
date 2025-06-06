from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, multiprocess
import os

if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
else:
    registry = None

inference_requests_total = Counter("inference_requests_total", "Total number of inference requests", registry=registry if registry else None)
jobs_processed_total = Counter("jobs_processed_total", "Total number of jobs processed", registry=registry if registry else None)
batches_processed_total = Counter("batches_processed_total", "Total number of batches processed", registry=registry if registry else None)
jobs_failure_total = Counter("jobs_failure_total", "Total number of jobs failed", registry=registry if registry else None)

batch_size_hist = Histogram("batch_size_hist", "Histogram of batch sizes", registry=registry if registry else None)
inference_latency = Histogram("inference_latency_seconds", "Latency of inference requests", registry=registry if registry else None)

inference_queue_size_gauge = Gauge("inference_queue_size_gauge", "Size of the inference queue", registry=registry if registry else None)
worker_queue_size_gauge = Gauge("worker_queue_size_gauge", "Size of the worker queue", registry=registry if registry else None)