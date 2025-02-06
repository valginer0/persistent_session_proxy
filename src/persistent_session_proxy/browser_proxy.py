"""HTTP proxy server for maintaining persistent web sessions using mitmproxy."""
from mitmproxy import ctx, http
from mitmproxy.tools.main import mitmdump
import sys
import json
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
        host = flow.request.pretty_host
        session = self._get_session(host)
        
        # Apply session cookies
        for cookie_name, cookie_value in session.cookies.items():
            flow.request.cookies[cookie_name] = cookie_value
            
        # Handle POST form data
        if flow.request.method == "POST" and flow.request.urlencoded_form:
            session._save_session(form_data=dict(flow.request.urlencoded_form))

    def response(self, flow: http.HTTPFlow) -> None:
        """Process responses to maintain session persistence."""
        host = flow.request.pretty_host
        session = self._get_session(host)
        
        # Update session cookies from response
        if flow.response.cookies:
            for cookie_name, cookie_value in flow.response.cookies.items():
                session.session.cookies.set(cookie_name, cookie_value[0])
            session._save_session()

# Required by mitmproxy for addon loading
addons = [PersistentSessionInterceptor()]

def run_proxy(host: str = '0.0.0.0', port: int = 8080):
    """Run the mitmproxy server."""
    # Build mitmdump arguments
    args = [
        '--listen-host', host,
        '--listen-port', str(port),
        '--quiet',  # Reduce console output
    ]
    
    # Run mitmdump with our addon
    try:
        mitmdump(args)
    except KeyboardInterrupt:
        sys.exit(0)
