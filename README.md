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

## Docker Installation

### Prerequisites
- Docker
- Docker Compose

### Setup
1. Clone the repository:
```bash
git clone https://github.com/valginer0/persistent_session_proxy.git
cd persistent_session_proxy
```

2. Copy your existing mitmproxy certificates:
```bash
mkdir certs
cp ~/.mitmproxy/mitmproxy-ca* certs/
```

3. Build and start the container:
```bash
docker-compose up -d
```

The proxy will be available at `localhost:8080`.

### Docker Volumes
The Docker setup uses two persistent volumes:
- `proxy_data`: Stores the SQLite database with session data
- `mitmproxy_certs`: Stores mitmproxy certificates

These volumes ensure your data persists even if the container is removed and recreated.

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

## Session Persistence Testing

The proxy has been successfully tested with GitHub:
1. Start the proxy
2. Configure browser to use localhost:8080
3. Visit github.com and log in
4. Close browser completely
5. Open new browser
6. Visit github.com
7. Verify: Still logged in without re-authentication

This demonstrates the proxy's ability to maintain session persistence across browser restarts, even with complex authentication systems involving 2FA.

## Troubleshooting

1. HTTPS Not Working:
   - Verify certificate installation
   - Some sites with HSTS may require manual certificate installation
   - Restart browser after certificate installation

2. Session Not Persisting:
   - Check if proxy is running
   - Verify proxy settings in browser
   - Ensure database directory is writable

## Testing Tools

### Test Server
The repository includes a test server (`test_server.py`) that helps test proxy behavior with different connection scenarios:

```bash
# Start the test server (runs on port 8081)
python test_server.py
```

The test server will:
1. Accept connections at `http://localhost:8081`
2. Send initial "Connection established" message
3. Wait 5 seconds
4. Force disconnect the connection

This helps test how the proxy handles various connection scenarios and server disconnections.

Note: The proxy handles these disconnections gracefully as expected, demonstrating its robustness in real-world scenarios.

## Development

### Running Tests
To run the tests, set your PYTHONPATH to include the src directory:

```bash
# Windows (Git Bash)
export PYTHONPATH=src\;$PYTHONPATH
pytest tests/

# Windows (CMD)
set PYTHONPATH=src;%PYTHONPATH%
pytest tests/

# Linux/Mac
export PYTHONPATH=src:$PYTHONPATH
pytest tests/
```

Note: Never use `pip install -e .` for development. Instead, use PYTHONPATH as shown above.

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
   - **Supports Docker deployment**

## Cloud Deployment (Fly.io)

The proxy can be deployed to Fly.io for cloud access. The deployed version is available at `persistent-session-proxy.fly.dev:8080`.

### Prerequisites
1. Install [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Sign up for Fly.io account: `flyctl auth signup`
3. Login: `flyctl auth login`

### Deployment Steps
1. Clone this repository
2. Navigate to the project directory
3. Create a volume for persistent data:
   ```bash
   flyctl volumes create data --size 1
   ```
4. Deploy the application:
   ```bash
   flyctl deploy
   ```

### Using the Cloud Proxy

1. Import the certificate:
   - Open Chrome/Edge and go to `chrome://certificate-manager/clientcerts` (or `edge://certificate-manager/clientcerts`)
   - Click "Import"
   - Select the certificate file from `certs/mitmproxy-ca-cert.pem`
   - Choose "Automatically select the certificate store based on the type of certificate"
   - Accept any security warnings

2. Configure your browser to use the proxy:
   - Go to browser settings
   - Search for "proxy"
   - Open system proxy settings
   - Set proxy server to:
     - Address: `persistent-session-proxy.fly.dev`
     - Port: `8080`

3. Test the proxy by visiting any HTTPS website. Your sessions will persist even after browser restarts.

### Features
- Persistent session storage using mounted volume
- Automatic HTTPS certificate handling
- Auto-scaling with minimum 1 instance
- 1GB RAM allocation
- Accessible from anywhere
