# syntax=docker/dockerfile:1
FROM gcc:12-bookworm AS builder
WORKDIR /build
COPY forwarder.c .
RUN gcc -O2 -o forwarder forwarder.c

FROM python:3.11-slim-bookworm
RUN useradd -m -u 10001 cnf && apt-get update && apt-get install -y --no-install-recommends procps iproute2 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=builder /build/forwarder ./forwarder
COPY cnf-agent.py .
USER 10001
EXPOSE 8080
ENV FORWARDER_BIN=/app/forwarder
HEALTHCHECK --interval=10s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz')" || exit 1
CMD ["sh", "-c", "./forwarder & exec gunicorn -b 0.0.0.0:8080 cnf-agent:app --workers 1 --timeout 30"]
