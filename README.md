# Persistent Session Proxy

A Python package that maintains web sessions across machine restarts. Perfect for situations where you need to preserve form data and login state even if your local machine needs to be restarted.

## Features

- Maintains web session cookies and form data across restarts
- Simple REST API for session management
- Persistent storage using SQLite
- Easy to deploy locally or on a remote server

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Start the proxy server:

```python
from persistent_session_proxy.api import run_server

run_server(host='0.0.0.0', port=5000)
```

2. Create a new session:

```bash
curl -X POST http://localhost:5000/session
```

3. Submit form data:

```bash
curl -X POST http://localhost:5000/session/<session_id>/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/form",
    "form_data": {
      "field1": "value1",
      "field2": "value2"
    }
  }'
```

4. Retrieve session state (even after restart):

```bash
curl http://localhost:5000/session/<session_id>
```

## Deployment Options

1. Local Deployment
   - Run on your local machine
   - Data stored in ~/.persistent_sessions/sessions.db

2. Remote Server (recommended)
   - Deploy on a cheap VPS (DigitalOcean, Linode, etc.)
   - Run behind nginx for SSL termination
   - Use supervisor or systemd for process management

3. Docker Deployment (coming soon)
   - Easy containerized deployment
   - Persistent volume for session data

## Security Considerations

- The proxy server should be run on a trusted network or behind a VPN
- Use HTTPS when deploying on a remote server
- Implement authentication if needed (coming soon)

## License

MIT License
