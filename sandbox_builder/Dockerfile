FROM python:3.11-slim

RUN useradd --create-home runner

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER runner
