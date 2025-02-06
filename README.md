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

2. Configure Browser Proxy Settings:
   - Each browser needs its own proxy configuration:
     - Chrome/Edge: Settings -> System -> Open your computer's proxy settings
     - Firefox: Settings -> Network Settings -> Manual proxy configuration
   - Set HTTP Proxy (or just "Proxy") to `127.0.0.1:8080` (or your custom host:port)
   - Apply the settings
   - Note: This single proxy setting will handle both HTTP and HTTPS traffic

3. Certificate Installation:
   - When you first start the proxy, it automatically creates certificates in `%USERPROFILE%\.mitmproxy\`
   
   For Chrome/Edge (Windows):
   - Option 1: Visit http://mitm.it through the proxy and follow browser prompts
     - This might not work initially with some browsers due to HSTS
   - Option 2: Manual Installation (recommended):
     ```cmd
     # Run in administrator command prompt
     certutil -addstore root "%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer"
     ```
   
   For Firefox:
   - Firefox uses its own certificate store
   - Visit http://mitm.it through the proxy
   - Click the Firefox icon and follow the prompts
   - Or manually: Settings -> Certificates -> View Certificates -> Import -> select `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer`
   
   After installing the certificate:
     1. Close all browser windows completely
     2. Reopen browser with proxy settings enabled
     3. HTTPS sites should now work without warnings

4. Testing the Setup:
   - Visit any website requiring login
   - Log in through the proxy
   - Close the browser completely
   - Reopen the browser (with proxy settings still enabled)
   - Visit the same site - you should still be logged in

## How It Works

The proxy:
1. Intercepts web traffic using mitmproxy
2. Stores cookies and form data in a SQLite database
3. Automatically restores sessions when you revisit sites
4. Handles both HTTP and HTTPS traffic seamlessly

## Storage

Sessions are stored in `~/.persistent_sessions/sessions.db` using SQLite. Each domain gets its own session storage.

## Security Notes

- The proxy stores session data unencrypted in the SQLite database
- The mitmproxy certificate allows the proxy to decrypt HTTPS traffic
- Only use on trusted networks and for trusted sites
- Consider security implications before using with sensitive data

## Troubleshooting

1. HTTPS Not Working:
   - Verify certificate installation
   - Some sites with HSTS may require manual certificate installation
   - Restart browser after certificate installation

2. Session Not Persisting:
   - Check if proxy is running
   - Verify proxy settings in browser
   - Ensure database directory is writable

## Cloud Deployment Options

For running the proxy in the cloud, these platforms offer good options:

1. PythonAnywhere (Recommended)
   - Specifically designed for Python applications
   - Free tier available
   - Hacker plan $5/month
   - Built-in persistent storage
   - Simple setup process

2. Railway.app
   - Free trial available
   - Starts at $5/month
   - Good for small projects
   - Automatic GitHub deployments

3. Fly.io
   - Free tier available
   - Pay-as-you-go pricing
   - Global deployment options
