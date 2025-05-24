#!/bin/bash
# Phased entrypoint script for debugging Cloud Run startup
set -e
set -x  # Enable command tracing for debugging

# Print all environment variables (excluding sensitive ones)
echo "============ ENVIRONMENT VARIABLES ============"
env | grep -v -E 'PASSWORD|SECRET|KEY' | sort

# Load environment variables from .env file if it exists (for local development)
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if we're running in Cloud Run (environment variables will be set via Secret Manager)
if [ -z "$K_SERVICE" ]; then
    echo "Running in local environment"
else
    echo "Running in Cloud Run environment with service: $K_SERVICE"
    
    # Create directory for credentials if it doesn't exist
    mkdir -p /tmp/keys
    
    # Write GCP credentials to file if provided as environment variable
    if [ ! -z "$GCP_CREDENTIALS" ]; then
        echo "Writing GCP credentials to file..."
        echo "$GCP_CREDENTIALS" > /tmp/keys/gcp-credentials.json
        echo "GCP credentials written to /tmp/keys/gcp-credentials.json"
    else
        echo "WARNING: GCP_CREDENTIALS environment variable not set"
    fi
fi

# Check for basic file existence
echo "Checking for essential files..."
ls -la
echo "Contents of xblock directory:"
ls -la xblock/ || echo "xblock directory not found"

# List all available Python packages to diagnose import issues
echo "Installed Python packages:"
pip list

# Start a simple HTTP server for initial testing
echo "Starting debug server to confirm basic functionality..."
cat > debug_server.py << 'EOF'
import http.server
import socketserver
import os
import sys
import json
import traceback

PORT = int(os.environ.get('PORT', 8080))

class DebugHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        output = ["<html><body><h1>xBlock Debug Information</h1>"]
        
        # Environment variables
        output.append("<h2>Environment Variables</h2><pre>")
        for k, v in sorted(os.environ.items()):
            if not any(secret in k.lower() for secret in ['password', 'secret', 'key']):
                output.append(f"{k}={v}")
        output.append("</pre>")
        
        # System information
        output.append("<h2>System Information</h2><pre>")
        output.append(f"Python version: {sys.version}")
        output.append(f"Platform: {sys.platform}")
        output.append(f"Current directory: {os.getcwd()}")
        output.append(f"Directory contents: {os.listdir('.')}")
        output.append("</pre>")
        
        # Try to import Django
        output.append("<h2>Django Check</h2><pre>")
        try:
            import django
            output.append(f"Django version: {django.get_version()}")
            
            # Try to initialize Django settings
            try:
                from django.conf import settings
                if settings.configured:
                    output.append("Django settings are configured")
                    output.append(f"DEBUG setting: {settings.DEBUG}")
                    output.append(f"SECRET_KEY exists: {'Yes' if hasattr(settings, 'SECRET_KEY') else 'No'}")
                    
                    # Try to get database info
                    try:
                        db_info = settings.DATABASES.get('default', {})
                        output.append(f"Database engine: {db_info.get('ENGINE', 'Not set')}")
                        output.append(f"Database name: {db_info.get('NAME', 'Not set')}")
                        output.append(f"Database host: {db_info.get('HOST', 'Not set')}")
                    except Exception as e:
                        output.append(f"Error getting database info: {str(e)}")
                else:
                    output.append("Django settings are not configured")
            except Exception as e:
                output.append(f"Error importing Django settings: {str(e)}")
                output.append(traceback.format_exc())
        except ImportError as e:
            output.append(f"Could not import Django: {str(e)}")
            
        output.append("</pre></body></html>")
        self.wfile.write("\n".join(output).encode())

print(f"Starting debug server on port {PORT}")
try:
    with socketserver.TCPServer(("", PORT), DebugHandler) as httpd:
        print(f"Debug server running on port {PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"Error starting debug server: {str(e)}")
    traceback.print_exc()
EOF

# Start the debug server
exec python debug_server.py
