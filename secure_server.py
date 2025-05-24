#!/usr/bin/env python3
"""
Secure API server for xBlock backend.
This is a standalone server that doesn't expose ANY sensitive information.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class SecureAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set secure headers
        self.send_response(503)  # Service Unavailable
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "default-src 'none'")
        self.send_header('Access-Control-Allow-Origin', 'https://brain.xblock.ai')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        # Return a secure error message as JSON
        response = {
            'status': 'error',
            'message': 'API service temporarily unavailable',
            'details': 'The API is currently in maintenance mode. Please try again later.',
            'support': 'contact@xblock.ai'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'https://brain.xblock.ai')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()
        
    def log_message(self, format, *args):
        # Customize logging to avoid exposing sensitive information
        sys.stderr.write("[%s] %s - %s\n" % (
            self.log_date_time_string(),
            self.address_string(),
            format % args
        ))

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SecureAPIHandler)
    print(f"Starting secure API server on port {port}...")
    httpd.serve_forever()
