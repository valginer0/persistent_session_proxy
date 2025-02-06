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

# Set up mitmproxy certificates
RUN mkdir -p /root/.mitmproxy /usr/local/share/ca-certificates
COPY certs/mitmproxy-ca* /root/.mitmproxy/

# Install certificate into system store (Linux equivalent of 'certutil -addstore')
# 1. Copy certificate to system certificate directory (like certutil)
# 2. Update system certificate store (like certutil does automatically)
RUN cp /root/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy-ca.crt && \
    update-ca-certificates

# Create directory for persistent data
RUN mkdir -p /data
VOLUME /data

# Expose proxy port
EXPOSE 8080

# Run proxy
CMD ["python", "run_proxy.py", "--host", "0.0.0.0"]
