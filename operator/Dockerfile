# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm
RUN useradd -m -u 10002 healer
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY healer.py .
USER 10002
CMD ["python", "-u", "healer.py"]
