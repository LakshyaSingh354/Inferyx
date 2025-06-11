import time
import logging
from collections import deque
from multiprocessing import Process
from workers.worker_loop import worker_loop
from job_queue.redis_client import get_redis_client
from metrics.metrics import worker_status_gauge

MAX_WORKERS = 16
MIN_WORKERS = 4
JOBS_PER_WORKER = 10
CHECK_INTERVAL = 5

logger = logging.getLogger(__name__)

def start_worker_pool():
    # Pre-allocate fixed worker IDs
    worker_ids = list(range(MAX_WORKERS))
    free_worker_ids = deque(worker_ids)
    active_workers = {}  # worker_id: Process
    redis_client = get_redis_client()

    # Initialize all worker statuses to terminated (-1)
    for worker_id in worker_ids:
        worker_status_gauge.labels(worker_id=worker_id).set(-1)

    try:
        while True:
            # Calculate desired workers based on queue size
            queue_size = redis_client.llen("worker_queue")
            desired_workers = min(
                MAX_WORKERS,
                max(MIN_WORKERS, (queue_size + JOBS_PER_WORKER - 1) // JOBS_PER_WORKER)
            )

            # Spawn new workers if needed
            while len(active_workers) < desired_workers and free_worker_ids:
                worker_id = free_worker_ids.popleft()
                p = Process(target=worker_loop, args=(worker_id,))
                p.start()
                active_workers[worker_id] = p
                logger.info(f"[Pool] Spawned worker {worker_id}")

            # Terminate excess workers
            while len(active_workers) > desired_workers:
                # Terminate least recently used worker
                worker_id = max(active_workers.keys())
                p = active_workers.pop(worker_id)
                
                # Immediately mark as terminating in Redis
                redis_client.hset("worker_status", worker_id, "terminating")
                
                
                max_wait = 30  # seconds
                start = time.time()
                while p.is_alive():
                    if redis_client.hget("worker_status", worker_id) == b"delete":
                        p.terminate()
                        p.join()
                        break
                    elif time.time() - start > max_wait:
                        logger.warning(f"Worker {worker_id} did not exit in time, force terminating.")
                        p.terminate()
                        p.join()
                        break
                    else:
                        time.sleep(0.1)
                
                # Clean up Redis status
                redis_client.hdel("worker_status", worker_id)
                free_worker_ids.append(worker_id)
                
                # Update metric to terminated state
                worker_status_gauge.labels(worker_id=worker_id).set(-1)
                logger.info(f"[Pool] Terminated worker {worker_id}")

            # Update metrics from Redis
            all_statuses = redis_client.hgetall("worker_status")
            for worker_id in worker_ids:
                # Only update metrics for active workers
                if worker_id in active_workers:
                    status = all_statuses.get(str(worker_id).encode(), b'idle').decode()
                    
                    # Map status to metric value
                    status_value = {
                        "idle": 0,
                        "busy": 1,
                        "terminating": -1
                    }.get(status, -1)  # default to terminated
                    
                    worker_status_gauge.labels(worker_id=worker_id).set(status_value)

            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("[Pool] Shutting down all workers...")
        for worker_id, p in active_workers.items():
            # Mark as terminating
            redis_client.hset("worker_status", worker_id, "terminating")
            worker_status_gauge.labels(worker_id=worker_id).set(-1)
            
            # Graceful shutdown
            p.terminate()
            p.join()
            
            # Clean up Redis
            redis_client.hdel("worker_status", worker_id)