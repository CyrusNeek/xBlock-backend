#!/bin/bash
# Very simple entrypoint for debugging Cloud Run startup
set -e

# Print all environment variables (excluding sensitive ones)
echo "============ ENVIRONMENT VARIABLES ============"
env | grep -v -E 'PASSWORD|SECRET|KEY' | sort

# Create a simple HTTP server that responds on port 8080
echo "Starting a simple HTTP server on port ${PORT:-8080}"

# First check if Python is working
echo "Python version:"
python --version

# Write a simple HTTP server in Python
cat > simple_server.py << 'EOF'
import http.server
import socketserver
import os

PORT = int(os.environ.get('PORT', 8080))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Debug Server Running</h1><pre>")
        self.wfile.write(b"Environment Variables:\n")
        for k, v in os.environ.items():
            if not any(secret in k.lower() for secret in ['password', 'secret', 'key']):
                self.wfile.write(f"{k}={v}\n".encode())
        self.wfile.write(b"</pre></body></html>")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
EOF

# Run the simple server
exec python simple_server.py
