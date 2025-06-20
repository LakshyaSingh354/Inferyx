from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, multiprocess
import os

if "PROMETHEUS_MULTIPROC_DIR" in os.environ:
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
else:
    registry = None

buckets=[
    0.1, 0.25, 0.5, 0.75, 1,
    1.5, 2, 3, 5, 7.5,
    10, 15, 20, 30, 45, 60, 70, 80, 90, 100, 120, 150, 170, 200, 250, 300
]


inference_requests_total = Counter("inference_requests_total", "Total number of inference requests", registry=registry if registry else None)
jobs_processed_total = Counter("jobs_processed_total", "Total number of jobs processed", registry=registry if registry else None)
batches_processed_total = Counter("batches_processed_total", "Total number of batches processed", registry=registry if registry else None)
jobs_failure_total = Counter("jobs_failure_total", "Total number of jobs failed", registry=registry if registry else None)
jobs_skipped_total = Counter("jobs_skipped_total", "Total number of jobs skipped", registry=registry if registry else None)
jobs_failed_after_retries_total = Counter("jobs_failed_after_retries_total", "Jobs failed after all retries", registry=registry if registry else None)

batch_size_hist = Histogram("batch_size_hist", "Histogram of batch sizes", registry=registry if registry else None)
inference_latency = Histogram("inference_latency_seconds", "Latency of inference requests", registry=registry if registry else None, buckets=buckets)

inference_queue_size_gauge = Gauge("inference_queue_size_gauge", "Size of the inference queue", registry=registry if registry else None)
worker_queue_size_gauge = Gauge("worker_queue_size_gauge", "Size of the worker queue", registry=registry if registry else None)

worker_status_gauge = Gauge("worker_status", "Status of each worker (0=idle, 1=busy)", ["worker_id"], registry=registry if registry else None)

retries_total = Counter("retries_total", "Total number of job retries", registry=registry if registry else None)

retry_queue_size_gauge = Gauge("retry_queue_size_gauge", "Current size of the retry queue", registry=registry if registry else None)

retry_count_hist = Histogram("retry_count_hist", "Histogram of retry counts per job", registry=registry if registry else None)

cache_hits_total = Counter("cache_hits_total", "Total number of cache hits", registry=registry if registry else None)
cache_misses_total = Counter("cache_misses_total", "Total number of cache misses", registry=registry if registry else None)