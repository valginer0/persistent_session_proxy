FROM python:3.10-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY run_proxy.py .

# Create directory for persistent data
RUN mkdir -p /data
VOLUME /data

# Expose proxy port
EXPOSE 8080

# Run proxy
CMD ["python", "run_proxy.py", "--host", "0.0.0.0"]
