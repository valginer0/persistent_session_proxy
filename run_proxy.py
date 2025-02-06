"""Run the mitmproxy-based persistent session proxy server."""
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
    
    # Print startup info
    print("\nStarting mitmproxy-based persistent session proxy...")
    print(f"Python version: {sys.version}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print("\nNOTE: First time users need to:")
    print("1. Install mitmproxy's certificate (will be prompted in browser)")
    print("2. Configure browser proxy settings to use {args.host}:{args.port}")
    print("\nPress Ctrl+C to stop the proxy")
    
    try:
        run_proxy(args.host, args.port)
    except KeyboardInterrupt:
        print("\nProxy server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting proxy: {e}")
        sys.exit(1)
