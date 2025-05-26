import http.server
import socketserver
import mimetypes

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        """Guess the type of a file based on its filename."""
        if path.endswith('.css'):
            return 'text/css'
        return super().guess_type(path)

    def end_headers(self):
        """Send CORS headers before ending the headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    initial_port = 3000
    max_retries = 10
    
    for port in range(initial_port, initial_port + max_retries):
        try:
            Handler = CustomHTTPRequestHandler
            with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                print(f"Serving at port {port}")
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                if port == initial_port + max_retries - 1:
                    print(f"Could not find an available port in range {initial_port}-{port}")
                    raise
                print(f"Port {port} is in use, trying next port...")
                continue
            raise
