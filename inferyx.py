import requests
import time
import random
import threading
import logging
import string

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

url = "http://localhost:8000/infer"
headers = {"Authorization": "Bearer 1234567890"}

total_requests = 2500
base_rps_range = (5, 10)  # requests per second
spike_rps_range = (30, 50)
spike_chance_per_second = 0.1  # ~10% chance per second to spike
spike_duration_range = (2, 5)  # seconds

def mutate_string(s):
    s = list(s)
    mutation_type = random.choice(["insert", "swap", "replace"])
    if mutation_type == "insert":
        pos = random.randint(0, len(s))
        s.insert(pos, random.choice(string.ascii_letters))
        if random.random() < 0.5:
            pos = random.randint(0, len(s))
            s.insert(pos, random.choice(string.ascii_letters))
    elif mutation_type == "swap" and len(s) > 1:
        pos = random.randint(0, len(s) - 2)
        s[pos], s[pos+1] = s[pos+1], s[pos]
    elif mutation_type == "replace":
        pos = random.randint(0, len(s) - 1)
        s[pos] = random.choice(string.ascii_letters)
    return "".join(s)

def send_request(i):
    sample_test_inputs = ["Google", "Apple", "Microsoft", "Amazon", "Facebook", "Tesla", "Nvidia", "AMD", "Intel", "Samsung", "LG", "Sony", "Panasonic", "Sharp", "Toshiba", "Hitachi", "JBL", "Bose", "Sony", "Panasonic", "Sharp", "Toshiba", "Hitachi", "JBL", "Bose"]
    base_input = random.choice(sample_test_inputs)
    # 70%: normal, 20%: mutated (cache miss), 10%: weird float
    r = random.random()
    if r < 0.7:
        data = {"input": base_input, "model_id": "fabsa"}
    elif r < 0.9:
        data = {"input": mutate_string(base_input), "model_id": "fabsa"}
    else:
        data = {"input": f"{base_input}c{(int(random.random()*10)/random.random())}", "model_id": "fabsa"}
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