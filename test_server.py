from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import threading
import socket

class DisconnectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send initial response headers
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        # Send some initial data
        self.wfile.write(b"Connection established...\n")
        self.wfile.flush()
        
        # Wait 5 seconds
        time.sleep(5)
        
        # Force an abrupt connection close by shutting down the socket
        try:
            self.wfile.write(b"About to force disconnect...\n")
            self.wfile.flush()
            self.connection.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            self.connection.close()

def run_server():
    server = HTTPServer(('localhost', 8081), DisconnectHandler)
    print("Test server started at http://localhost:8081")
    print("It will forcibly disconnect after 5 seconds")
    server.serve_forever()

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
