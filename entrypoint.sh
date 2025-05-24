#!/bin/bash

# Ultra minimal entrypoint just to verify container can start
echo "Container started at $(date)"
echo "Running as user: $(whoami)"
echo "PORT env variable: $PORT"
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la | grep -v password)"

# Start a minimal HTTP server that actually binds to PORT
PORT_VALUE=${PORT:-8080}
echo "Starting a Python HTTP server on port $PORT_VALUE"

# Create minimal HTTP server file
cat > simple_server.py << 'EOF'
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Container is running!</h1></body></html>")

port = int(os.environ.get("PORT", 8080))
print(f"Server starting on port {port}")
server = HTTPServer(("", port), SimpleHandler)
server.serve_forever()
EOF

# Run the server
exec python simple_server.py
