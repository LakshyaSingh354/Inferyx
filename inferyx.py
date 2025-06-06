import requests
import time
from tqdm import tqdm
url = "http://localhost:8000/infer"
headers = {"Authorization": "Bearer 1234567890"}

for i in tqdm(range(1000)):
    data = {"input": f"test input {i}", "model_id": "mock"}
    response = requests.post(url, json=data, headers=headers)
    time.sleep(0.02)