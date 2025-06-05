from prometheus_client import Counter, Gauge, Histogram

inference_requests_total = Counter("inference_requests_total", "Total number of inference requests")
jobs_processed_total = Counter("jobs_processed_total", "Total number of jobs processed")
batches_processed_total = Counter("batches_processed_total", "Total number of batches processed")
jobs_failure_total = Counter("jobs_failure_total", "Total number of jobs failed")

batch_size_hist = Histogram("batch_size_hist", "Histogram of batch sizes")
inference_latency = Histogram("inference_latency_seconds", "Latency of inference requests")

queue_size_gauge = Gauge("queue_size_gauge", "Size of the inference queue")