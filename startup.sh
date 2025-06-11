#!/bin/bash
rm -rf /tmp/prometheus_multiproc
mkdir -p /tmp/prometheus_multiproc
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level warning