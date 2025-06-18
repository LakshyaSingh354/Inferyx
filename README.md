[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/LakshyaSingh354/Inferyx?style=social)](https://github.com/LakshyaSingh354/Inferyx)


# Inferyx - A Production-Grade AI Inference Engine ⚙️🔥

**Inferyx** is a no-BS simulation of a real-world AI inference system — built from the ground up to mirror the insane complexity and pressure of production-scale ML deployment.  
From batching and retry queues to observability and dynamic worker pools, Inferyx doesn’t play around.

It mimics what happens *after* a `/predict` API is called: job queuing, batching, caching, retrying, worker pooling, and full observability, just like you’d expect in a real world deployment powering millions of requests.

> 🧠 Built to demonstrate real-world AI Systems Engineering skills — infra, latency, load, and failure handling — **not just another model deployment.**

---

## ⚡ TL;DR

Inferyx is a containerized AI inference simulation system built for infra engineers.  
It features async queuing, batching, GPU-style worker pools, retry queues, Prometheus metrics, Grafana dashboards, and dynamic scaling — designed to showcase real-world system design skills under pressure.  
Built for the kind of AI engineers who know that getting a `/predict` call to survive production is a blood sport.

---

## 🚀 Features

- 🔁 **Async Inference Queue** with Redis-based queuing
- 📦 **Batching Engine** that groups jobs for optimal throughput
- 🔨 **Simulated GPU Worker Pool** (with dynamic scaling up and down)
- ❌ **Failure Simulation + Retry Queue** with exponential backoff
- ⚠️ **Rate Limiting** by setting a maximum queue size to prevent abuse and overload.
- ⚡ **Redis Cache Layer** with hit/miss metrics
- 📈 **Prometheus + Grafana Monitoring** (latency, retries, throughput, worker state)
- 🔥 **Load Testing Utility** to simulate thousands of requests
- 🧪 **Multi-model Routing** (based on `model_id`)
- 🐳 Fully **containerized** with Docker + Docker Compose

---

## 🎥 Live Demo: Dynamic Worker Scaling

> 👀 Watch Inferyx respond to real-time load:
> Incoming requests flood the queue → Batches form → Workers scale up dynamically → Throughput spikes → System auto-scales back to idle.

![dynamic-workers](workers.gif)
> 🔁 Dynamic Worker Scaling in Action:  
> As the inference load increases, the worker pool automatically scales up to handle the demand — then scales down when idle, saving resources.

---

## System Architecture

### 🙋 Who Should Look at This?

- **MLEs** looking for real-world systems that go beyond toy deployments  
- **Backend Engineers** interested in infra-level AI serving  
- **Hiring Managers** looking for infra-first AI engineers who know their Redis from their retry queues  
- **Students** trying to learn how *actual AI infrastructure works* in prod

![system architecture](image.png)
> 🧠 Inferyx System Architecture: Shows the full inference flow — from `/infer` request to batching, worker pool execution, retry logic, and Redis-backed observability.


---
## 📊 Real-Time Observability
![grafana-screenshot](grafana.png)
> 📊 Real-Time Observability: Metrics include queue sizes, latency percentiles, retry dynamics, failures/sec, throughput, and cache effectiveness. Designed to simulate production stress.


---

## ❓ Why This Matters

Most AI projects stop at “deploy a model on FastAPI.”  
Inferyx goes beyond — it asks: what happens **after** the first 1000 clients hammer your system?

- How do you batch without starving?
- How do you scale workers dynamically?
- How do you track failures, retries, and throughput in real time?

This is the difference between a Kaggle notebook and real-world ML systems engineering.

---

## 📦 How to Run (Local Dev)

### ✅ Prerequisites
- Docker
- Docker Compose

### 🛠️ One-Command Boot

```bash
docker-compose up --build
```

This will spin up:
- FastAPI App
- Batching Engine
- Worker Pool
- Retry Worker
- Redis
- Prometheus
- Grafana

---

> NOTE: The real model integrated is a Financial Aspect Based Sentiment Analysis model. For more training and model details, see [here.](https://github.com/LakshyaSingh354/FABSA/tree/main/fabsa-model)

> Kindly download the `onnx` model and put it in the root directory with name "onnx". Download the model from [here](https://www.kaggle.com/models/lakshyasingh354/fabsa).

## 🧪 Test It

### 🔄 Send Inference Request

```bash
curl -X POST http://localhost:8000/infer \
    -H "Content-Type: application/json" \
    -d '{"input": "your text here", "model_id": "mock"}'
```
> Or make automatic requests using [`inferyx.py`](https://github.com/LakshyaSingh354/Inferyx/blob/main/inferyx.py). Configure the variables according to the testing parameters.

### 📊 Monitor the System

- **Prometheus**: [http://localhost:9090](http://localhost:9090)  
- **Grafana**: [http://localhost:3000](http://localhost:3000)  
    - Login: `admin` / `admin`
    - Dashboard: [*Inferyx*](http://localhost:3000/d/inferyx/inferyx)

---

## 📈 Metrics Tracked

- 🔁 `inference_queue_size`, `worker_queue_size`, `retry_queue_size`
- 📦 `batch_size`, `batches_processed`
- 🧠 `worker_utilization`
- 🐢 `latency_p50`, `latency_p95`, `latency_p99`
- 🔁 `retry_attempts`, `failed_jobs`
- 💥 `cache_hits`, `cache_misses`
- 🔂 `requests_per_second`

---

## ⚠️ Failure Handling

- X% of jobs are simulated to fail (configurable)
- Failed jobs pushed to a **retry queue**
- Retry loop uses **exponential backoff**
- Max retry attempts configurable
- Observability baked in (retry delay, attempts)

---

## 🔧 Configurable Constants

Set via [`config.py`](https://github.com/LakshyaSingh354/Inferyx/blob/main/config/config.py):

```python
# Batching
INFERENCE_QUEUE_KEY = "inference_queue"
WORKER_QUEUE_KEY = "worker_queue"
MAX_BATCH_SIZE = 4
MAX_WAIT_TIME = 1.0

# Queue
MAX_QUEUE_SIZE = 500

# Retry
RETRY_QUEUE_KEY = "retry_queue"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
MAX_BACKOFF_SECONDS = 30

# Workers
MAX_WORKERS = 16
MIN_WORKERS = 1
JOBS_PER_WORKER = 10
CHECK_INTERVAL = 5

# Metrics
PROMETHEUS_MULTIPROC_DIR = "/tmp/prometheus_multiproc"
METRICS_PORT = 8080
```

---
## 📁 Repo Structure
```.
└── Inferyx/
    ├── api/
    │   ├── auth.py
    │   ├── main.py
    │   └── schema.py
    ├── batch/
    │   └── batching_engine.py
    ├── caching/
    │   └── cache_inference.py
    ├── config/
    │   └── config.py
    ├── job_queue/
    │   ├── job_store.py
    │   ├── producer.py
    │   ├── redis_client.py
    │   ├── schema.py
    │   └── utils.py
    ├── metrics/
    │   ├── metrics.py
    │   └── serve.py
    ├── model/
    │   ├── FABSA.py
    │   ├── infer.py
    │   └── test_infer.py
    ├── retry/
    │   ├── retry.py
    │   ├── retry_worker.py
    │   └── utils.py
    ├── workers/
    │   ├── worker_loop.py
    │   └── worker_pool.py
    ├── onnx/
    ├── README.md
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── inferyx.py
    ├── prometheus.yaml
    ├── pyproject.toml
    ├── requirements.txt
    ├── startup.sh
    ├── uv.lock
    └── .python-version
```
---
## 🧾 TODO (Future Work)

- [ ] gRPC Gateway
- [ ] Model Registry Integration
- [ ] Kubernetes + HPA
- [ ] Triton Inference Server integration

---
## Contribute or Learn More

Open issues, ask questions, or suggest features.  
Let’s build resilient AI infra together!  
⭐ Star this repo if it helped you or inspired your own system designs.