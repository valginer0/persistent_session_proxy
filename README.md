# Persistent Session Proxy

A Python package that maintains web sessions across machine restarts using mitmproxy. Perfect for situations where you need to preserve form data and login state even if your local machine needs to be restarted.

## Features

- Maintains web session cookies and form data across restarts
- Built on mitmproxy for robust HTTPS support
- Automatic certificate handling
- Persistent storage using SQLite
- Support for both HTTP and HTTPS traffic
- Session persistence across browser restarts

## Requirements

- Python 3.8+
- mitmproxy 11.0.2+

## Installation

1. Install the package and dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the proxy server:
```bash
python run_proxy.py
```

By default, the proxy runs on `127.0.0.1:8080`. You can customize the host and port:
```bash
python run_proxy.py --host 127.0.0.1 --port 8888
```

2. Configure your browser proxy:
   - Open your browser's network/proxy settings
   - Set HTTP Proxy (or just "Proxy") to `127.0.0.1:8080` (or your custom host:port)
   - Apply the settings
   - Note: This single proxy setting will handle both HTTP and HTTPS traffic

3. First-time certificate setup:
   - With proxy configured, visit any HTTPS website
   - You'll see a security warning about the certificate
   - Follow the browser's prompts to install mitmproxy's certificate
   - This is a one-time setup required for HTTPS interception
   - After installing the certificate, HTTPS sites will work normally

Now all your web traffic (both HTTP and HTTPS) will go through the proxy and sessions will be automatically persisted.

## How It Works

The proxy uses mitmproxy to intercept HTTP/HTTPS traffic and:
1. Stores cookies and form submissions in a SQLite database
2. Automatically restores session state when revisiting sites
3. Maintains separate sessions for different domains
4. Persists all data in `~/.persistent_sessions/sessions.db`

## Development

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

## Security Considerations

- The proxy can see all traffic (including HTTPS) - only use it on trusted networks
- Session data is stored unencrypted in the SQLite database
- Default configuration only listens on localhost for security
- Use with caution on public networks

## License

MIT License - see LICENSE file for details
