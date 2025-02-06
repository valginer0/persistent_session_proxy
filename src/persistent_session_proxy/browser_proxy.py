"""HTTP proxy server for maintaining persistent web sessions using mitmproxy."""
from mitmproxy import ctx, http
from mitmproxy.tools.main import mitmdump
import sys
import json
import asyncio
import platform
from typing import Dict
from .proxy_session import ProxySession
from .session_store import SessionStore

class PersistentSessionInterceptor:
    def __init__(self):
        self.session_store = SessionStore()
        self.active_sessions: Dict[str, ProxySession] = {}
    
    def _get_session(self, host: str) -> ProxySession:
        """Get or create session for a host."""
        if host not in self.active_sessions:
            session = ProxySession(session_id=host, store=self.session_store)
            self.active_sessions[host] = session
        return self.active_sessions[host]

    def request(self, flow: http.HTTPFlow) -> None:
        """Process and modify requests to maintain session persistence."""
        try:
            host = flow.request.pretty_host
            session = self._get_session(host)
            
            # Apply session cookies
            for cookie_name, cookie_value in session.cookies.items():
                flow.request.cookies[cookie_name] = cookie_value
                
            # Handle POST form data
            if flow.request.method == "POST" and flow.request.urlencoded_form:
                session._save_session(form_data=dict(flow.request.urlencoded_form))
        except Exception as e:
            ctx.log.warn(f"Error processing request: {str(e)}")

    def response(self, flow: http.HTTPFlow) -> None:
        """Process responses to maintain session persistence."""
        try:
            host = flow.request.pretty_host
            session = self._get_session(host)
            
            # Update session cookies from response
            if flow.response.cookies:
                for cookie_name, cookie_value in flow.response.cookies.items():
                    session.session.cookies.set(cookie_name, cookie_value[0])
                session._save_session()
        except Exception as e:
            ctx.log.warn(f"Error processing response: {str(e)}")

    def error(self, flow: http.HTTPFlow) -> None:
        """Handle any proxy errors gracefully."""
        try:
            if flow.error:
                error_str = str(flow.error)
                host = flow.request.pretty_host if flow.request else "unknown"
                
                # Identify error type
                if any(x in error_str.lower() for x in ['connection reset', 'forcibly closed']):
                    # Browser disconnected
                    ctx.log.debug(f"Browser disconnected from {host} (normal behavior)")
                elif any(x in error_str.lower() for x in ['timeout', 'connection refused', 'no route']):
                    # Server-side issue
                    ctx.log.error(f"Server connection issue with {host}: {error_str}")
                else:
                    # Unknown error
                    ctx.log.error(f"Unknown error with {host}: {error_str}")
        except Exception as e:
            ctx.log.warn(f"Error in error handler: {str(e)}")

# Required by mitmproxy for addon loading
addons = [PersistentSessionInterceptor()]

def handle_asyncio_exception(loop, context):
    """Custom exception handler for asyncio errors."""
    exc = context.get('exception')
    if isinstance(exc, ConnectionResetError) and exc.winerror == 10054:
        # This is a normal Windows connection reset, we can ignore it
        return
    # For other errors, use the default handler
    loop.default_exception_handler(context)

def run_proxy(host: str = '0.0.0.0', port: int = 8080):
    """Run the mitmproxy server."""
    # Set up asyncio error handling for Windows
    if platform.system() == 'Windows':
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handle_asyncio_exception)
    
    # Build mitmdump arguments
    args = [
        '--listen-host', host,
        '--listen-port', str(port),
        '--quiet',  # Reduce console output
        '--set', 'connection_strategy=lazy',  # More graceful connection handling
        '--set', 'stream_large_bodies=1m',  # Better handling of large responses
    ]
    
    # Run mitmdump with our addon
    try:
        mitmdump(args)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        ctx.log.error(f"Proxy error: {str(e)}")
        sys.exit(1)
