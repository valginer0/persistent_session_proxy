"""HTTP proxy server for maintaining persistent web sessions."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import ssl
import json
import socket
from typing import Dict, Optional
import threading
import select
import logging
from .proxy_session import ProxySession
from .session_store import SessionStore

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global shutdown flag
is_shutting_down = threading.Event()

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
        if is_shutting_down.is_set():
            return
            
        try:
            # Get the target host and port
            host, port = self.path.split(':')
            port = int(port)
            
            logger.info(f"CONNECT request for {host}:{port}")
            
            # Create a connection to the target server
            logger.debug(f"Creating connection to {host}:{port}")
            target = socket.create_connection((host, port))
            target.settimeout(1)  # 1 second timeout
            logger.debug(f"Connection established to {host}:{port}")
            
            # Send 200 Connection Established to the client
            self.send_response(200, 'Connection Established')
            self.end_headers()
            logger.debug("Sent 200 Connection Established to client")
            
            # Create session for this host
            session = self._get_session(host)
            logger.debug(f"Created/retrieved session for {host}")
            
            # Start forwarding data between client and target
            client = self.connection
            client.settimeout(1)  # 1 second timeout
            
            def forward(source, destination, direction):
                try:
                    while not is_shutting_down.is_set():
                        try:
                            data = source.recv(4096)
                            if not data:
                                break
                            destination.send(data)
                            if not is_shutting_down.is_set():  # Only log if not shutting down
                                logger.debug(f"{direction}: Forwarded {len(data)} bytes")
                        except socket.timeout:
                            continue
                        except (ConnectionError, socket.error) as e:
                            if not is_shutting_down.is_set():  # Only log if not shutting down
                                logger.error(f"{direction}: Connection error - {str(e)}")
                            break
                finally:
                    try:
                        source.close()
                    except:
                        pass
                
            # Create threads for bidirectional forwarding
            client_to_target = threading.Thread(
                target=forward, args=(client, target, "Client → Target"))
            target_to_client = threading.Thread(
                target=forward, args=(target, client, "Target → Client"))
            
            client_to_target.daemon = True
            target_to_client.daemon = True
            
            logger.debug("Starting forwarding threads")
            client_to_target.start()
            target_to_client.start()
            
            # Wait for either thread to finish or shutdown signal
            while (client_to_target.is_alive() and 
                   target_to_client.is_alive() and 
                   not is_shutting_down.is_set()):
                client_to_target.join(0.1)
                target_to_client.join(0.1)
            
            if not is_shutting_down.is_set():
                logger.info(f"CONNECT tunnel closed for {host}:{port}")
            
        except Exception as e:
            if not is_shutting_down.is_set():  # Only log if not shutting down
                logger.error(f"Error in CONNECT: {str(e)}")
            self.send_error(500, str(e))
            return
        finally:
            try:
                target.close()
                if not is_shutting_down.is_set():  # Only log if not shutting down
                    logger.debug(f"Closed connection to {host}:{port}")
            except:
                pass

    def do_GET(self):
        """Handle GET requests."""
        if is_shutting_down.is_set():
            return
            
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
            if not is_shutting_down.is_set():  # Only log if not shutting down
                logger.error(f"Error in GET: {str(e)}")
            self.send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests."""
        if is_shutting_down.is_set():
            return
            
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
            if not is_shutting_down.is_set():  # Only log if not shutting down
                logger.error(f"Error in POST: {str(e)}")
            self.send_error(500, str(e))


def run_proxy(host: str = '0.0.0.0', port: int = 8080):
    """Run the proxy server."""
    import signal
    import sys
    import threading
    import os
    import atexit

    # Reset shutdown flag
    is_shutting_down.clear()

    server_address = (host, port)
    httpd = HTTPServer(server_address, PersistentSessionProxy)
    httpd.timeout = 1  # Set socket timeout to 1 second

    def force_shutdown(signum=None, frame=None):
        print("\nShutting down proxy server...")
        os._exit(0)  # Force immediate exit

    # Set up signal handlers
    signal.signal(signal.SIGINT, force_shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, force_shutdown)  # Termination request
    atexit.register(force_shutdown)  # Register for normal exit

    print(f"Starting proxy server on {host}:{port}")
    print("To use this proxy:")
    print(f"1. Set your browser's proxy settings to {host}:{port}")
    print("2. Your sessions will be automatically persisted")
    print("3. If you restart your computer, just reconnect to the same proxy")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        force_shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}")
        force_shutdown()
