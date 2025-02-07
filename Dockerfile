FROM python:3.10-slim

WORKDIR /app

# Install required system packages and CA certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY run_proxy.py .

# Create directory for persistent data and certificates
RUN mkdir -p /data/.mitmproxy
VOLUME /data

# Copy certificates to the persistent volume
COPY certs/mitmproxy-ca* /data/.mitmproxy/

# Install certificate into system store (Linux equivalent of 'certutil -addstore')
RUN cp /data/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy-ca.crt && \
    update-ca-certificates

# Set environment variable for mitmproxy to use the new certificate location
ENV MITMPROXY_HOME=/data/.mitmproxy

# Expose proxy port
EXPOSE 8080

# Run proxy
CMD ["python", "run_proxy.py", "--host", "0.0.0.0"]
