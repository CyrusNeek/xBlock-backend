"""
Debug server for xBlock backend.
This server is used as a fallback when Django fails to start.
It provides basic diagnostic information without exposing sensitive data.
"""

import os
import sys
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json

class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>xBlock Debug Information</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
                .error { color: red; }
                .warning { color: orange; }
            </style>
        </head>
        <body>
            <h1>xBlock Debug Information</h1>
            
            <h2>Environment Variables</h2>
            <pre>
            """
        
        # Only show non-sensitive environment variables
        safe_vars = [
            'ALLOWED_HOSTS', 'CLOUD_RUN_TIMEOUT_SECONDS', 'DEBUG', 
            'DJANGO_LOG_LEVEL', 'DJANGO_SETTINGS_MODULE', 'HOME',
            'K_CONFIGURATION', 'K_REVISION', 'K_SERVICE', 'LANG',
            'PATH', 'PORT', 'PWD', 'PYTHONDONTWRITEBYTECODE',
            'PYTHONUNBUFFERED', 'PYTHON_SHA256', 'PYTHON_VERSION', 'SHLVL'
        ]
        
        for key in safe_vars:
            if key in os.environ:
                html += f"{key}={os.environ.get(key)}\n"
        
        # For sensitive variables, just show that they are set but not their values
        sensitive_prefixes = [
            'DATABASE_', 'SECRET_', 'API_KEY', 'PASSWORD', 'REDIS_', 
            'OPENAI_', 'QB_', 'STRIPE_', 'GOOGLE_', 'SENDGRID_'
        ]
        
        for key in os.environ:
            if any(key.startswith(prefix) or prefix in key for prefix in sensitive_prefixes):
                if key not in safe_vars:
                    html += f"{key}=**********[REDACTED]**********\n"
        
        html += """
            </pre>
            
            <h2>System Information</h2>
            <pre>
Python version: {python_version}
Platform: {platform}
Current directory: {cwd}
Directory contents: {dir_contents}
            </pre>
            
            <h2>Django Check</h2>
            <pre>
            """
        
        try:
            import django
            html += f"Django version: {django.get_version()}\n"
            
            try:
                from django.conf import settings
                if settings.configured:
                    html += "Django settings are configured\n"
                    html += f"DEBUG setting: {settings.DEBUG}\n"
                    html += f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}\n"
                else:
                    html += "<span class='error'>Django settings are not configured</span>\n"
            except Exception as e:
                html += f"<span class='error'>Error checking Django settings: {str(e)}</span>\n"
                
        except ImportError:
            html += "<span class='error'>Django is not installed</span>\n"
        
        html += """
            </pre>
            
            <h2>Network Information</h2>
            <pre>
Hostname: {hostname}
            </pre>
            
            <p>This is a debug page. If you're seeing this in production, something is wrong with the application configuration.</p>
        </body>
        </html>
        """
        
        # Format the HTML with actual values
        formatted_html = html.format(
            python_version=sys.version,
            platform=platform.platform(),
            cwd=os.getcwd(),
            dir_contents=str(os.listdir('.')),
            hostname=socket.gethostname()
        )
        
        self.wfile.write(formatted_html.encode())

def run_debug_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DebugHandler)
    print(f"Starting debug server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8080))
    run_debug_server(port)
