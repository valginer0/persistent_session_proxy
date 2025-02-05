"""Run the proxy server."""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = str(Path(__file__).parent / 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from persistent_session_proxy.browser_proxy import run_proxy

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Start the persistent session proxy server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    
    args = parser.parse_args()
    run_proxy(args.host, args.port)
