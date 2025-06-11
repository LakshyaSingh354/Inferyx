import requests
import time
import random
import threading
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

url = "http://localhost:8000/infer"
headers = {"Authorization": "Bearer 1234567890"}

total_requests = 1000
base_rps_range = (10, 15)  # requests per second
spike_rps_range = (30, 50)
spike_chance_per_second = 0.05  # ~2% chance per second to spike
spike_duration_range = (2, 5)  # seconds

def send_request(i):
    sample_test_inputs = ["test input", "test input 2", "test input 3", "test input 4", "test input 5"]
    data = {"input": random.choice(sample_test_inputs), "model_id": "mock"} if random.random() < 0.7 else {"input": f"test input {i*random.random()/random.random()}", "model_id": "mock"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=2)
    except Exception as e:
        pass  # Optionally log errors

i = 0
while i < total_requests:
    # Decide if this second will be a spike
    if random.random() < spike_chance_per_second:
        spike_rps = random.randint(*spike_rps_range)
        spike_duration = random.randint(*spike_duration_range)
        logger.info(f"Spike! {spike_rps} rps for {spike_duration}s")
        for _ in range(spike_duration):
            threads = []
            for _ in range(spike_rps):
                if i >= total_requests:
                    break
                t = threading.Thread(target=send_request, args=(i,))
                t.start()
                threads.append(t)
                i += 1
            for t in threads:
                t.join()
            logger.info(f"Processed {i} requests")
            time.sleep(1)
    else:
        base_rps = random.randint(*base_rps_range)
        threads = []
        for _ in range(base_rps):
            if i >= total_requests:
                break
            t = threading.Thread(target=send_request, args=(i,))
            t.start()
            threads.append(t)
            i += 1
        for t in threads:
            t.join()
        logger.info(f"Processed {i} requests")
        time.sleep(1)