"""
Simple HTTP server for static HTML
"""
import http.server
import socketserver

# Set port
PORT = 5000

# Custom handler to add CORS headers
class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
        
    def do_GET(self):
        # Always serve the static HTML file regardless of the path
        if self.path == '/' or self.path == '/index.html':
            self.path = '/static.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Create server with custom handler
Handler = CORSHTTPRequestHandler
httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)

print(f"Serving static trading dashboard at http://localhost:{PORT}")
httpd.serve_forever()