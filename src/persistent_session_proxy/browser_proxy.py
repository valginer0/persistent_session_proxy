"""HTTP proxy server for maintaining persistent web sessions."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import ssl
import json
import socket
from typing import Dict, Optional
import threading
import select
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

    def do_CONNECT(self):
        """Handle HTTPS CONNECT requests."""
        try:
            # Get the target host and port
            host, port = self.path.split(':')
            port = int(port)
            
            # Create a connection to the target server
            target = socket.create_connection((host, port))
            
            # Send 200 Connection Established to the client
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            # Create session for this host
            session = self._get_session(host)
            
            # Start forwarding data between client and target
            client = self.connection
            
            def forward(source, destination):
                try:
                    while True:
                        data = source.recv(4096)
                        if not data:
                            break
                        destination.send(data)
                except (ConnectionError, socket.error):
                    pass
                
            # Create threads for bidirectional forwarding
            client_to_target = threading.Thread(
                target=forward, args=(client, target))
            target_to_client = threading.Thread(
                target=forward, args=(target, client))
            
            client_to_target.daemon = True
            target_to_client.daemon = True
            
            client_to_target.start()
            target_to_client.start()
            
            # Wait for either thread to finish
            while client_to_target.is_alive() and target_to_client.is_alive():
                client_to_target.join(0.1)
                target_to_client.join(0.1)
            
        except Exception as e:
            self.send_error(500, str(e))
            return
        finally:
            try:
                target.close()
            except:
                pass

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
    import signal
    import sys

    server_address = (host, port)
    httpd = HTTPServer(server_address, PersistentSessionProxy)

    def signal_handler(signum, frame):
        print("\nShutting down proxy server...")
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request

    print(f"Starting proxy server on {host}:{port}")
    print("To use this proxy:")
    print(f"1. Set your browser's proxy settings to {host}:{port}")
    print("2. Your sessions will be automatically persisted")
    print("3. If you restart your computer, just reconnect to the same proxy")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy server...")
        httpd.shutdown()
        httpd.server_close()
        sys.exit(0)
