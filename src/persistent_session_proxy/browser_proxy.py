"""HTTP proxy server for maintaining persistent web sessions."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import ssl
import json
from typing import Dict, Optional
import threading
from .proxy_session import ProxySession
from .session_store import SessionStore

class PersistentSessionProxy(BaseHTTPRequestHandler):
    # Class-level session store
    session_store = SessionStore()
    active_sessions: Dict[str, ProxySession] = {}

    def _get_session(self, host: str) -> ProxySession:
        """Get or create session for a host."""
        if host not in self.active_sessions:
            # Try to load existing session for this host
            session = ProxySession(session_id=host, store=self.session_store)
            self.active_sessions[host] = session
        return self.active_sessions[host]

    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse the requested URL
            url = self.path
            if url.startswith('http'):
                # Full URL provided
                parsed = urlparse(url)
                host = parsed.netloc
            else:
                # Relative URL, get host from headers
                host = self.headers.get('Host', '')
                parsed = urlparse(f"http://{host}{url}")
                
            # Get session for this host
            session = self._get_session(host)
            
            # Forward the request through our session
            response = session.get(
                url,
                headers={k: v for k, v in self.headers.items()
                        if k.lower() not in ['host', 'proxy-connection']}
            )
            
            # Send response back to client
            self.send_response(response.status_code)
            
            # Forward response headers
            for key, value in response.headers.items():
                if key.lower() not in ['transfer-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests."""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse the requested URL
            url = self.path
            if url.startswith('http'):
                parsed = urlparse(url)
                host = parsed.netloc
            else:
                host = self.headers.get('Host', '')
                parsed = urlparse(f"http://{host}{url}")
            
            # Get session for this host
            session = self._get_session(host)
            
            # Forward the request through our session
            response = session.post(
                url,
                data=post_data,
                headers={k: v for k, v in self.headers.items()
                        if k.lower() not in ['host', 'proxy-connection']}
            )
            
            # Send response back to client
            self.send_response(response.status_code)
            
            # Forward response headers
            for key, value in response.headers.items():
                if key.lower() not in ['transfer-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_error(500, str(e))


def run_proxy(host: str = '0.0.0.0', port: int = 8080):
    """Run the proxy server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PersistentSessionProxy)
    print(f"Starting proxy server on {host}:{port}")
    print("To use this proxy:")
    print(f"1. Set your browser's proxy settings to {host}:{port}")
    print("2. Your sessions will be automatically persisted")
    print("3. If you restart your computer, just reconnect to the same proxy")
    httpd.serve_forever()
