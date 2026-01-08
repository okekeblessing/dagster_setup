FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../clickhouse/requirements.txt /app/clickhouse_requirements.txt
COPY ../data_source/requirements.txt /app/data_source_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir \
    -r /app/clickhouse_requirements.txt \
    -r /app/data_source_requirements.txt

# Copy application code
COPY ../clickhouse /app/clickhouse
COPY ../data_source /app/data_source

ENV PYTHONPATH=/app

CMD ["python", "--version"]
