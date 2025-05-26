#!/usr/bin/env python
"""
Debug server for Cloud Run deployments.
This script creates a simple HTTP server that displays environment information
and helps diagnose deployment issues.
"""

import os
import sys
import socket
import platform
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import traceback

PORT = int(os.environ.get('PORT', 8080))


class DebugHandler(BaseHTTPRequestHandler):
    """Handler for debug server requests"""

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Basic HTML styling
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>xBlock Debug Information</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #666; margin-top: 20px; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
                .error { color: red; }
                .success { color: green; }
                .section { margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>xBlock Debug Information</h1>
            <div class="section">
                <h2>System Information</h2>
                <pre>
        """

        # System information
        html += f"Python Version: {sys.version}\n"
        html += f"Platform: {platform.platform()}\n"
        html += f"Hostname: {socket.gethostname()}\n"
        html += f"Current Directory: {os.getcwd()}\n"
        html += f"Directory Contents: {', '.join(os.listdir('.'))}\n"
        html += "</pre></div>"

        # Environment variables (filtering out sensitive info)
        html += """
            <div class="section">
                <h2>Environment Variables</h2>
                <pre>
        """
        for key, value in sorted(os.environ.items()):
            # Filter out sensitive information
            if any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']):
                value = "[REDACTED]"
            html += f"{key}={value}\n"
        html += "</pre></div>"

        # Django check
        html += """
            <div class="section">
                <h2>Django Check</h2>
                <pre>
        """
        try:
            import django
            html += f"Django Version: {django.get_version()}\n"
            
            # Try to import settings
            try:
                from django.conf import settings
                html += f"Django settings are configured. DEBUG={settings.DEBUG}\n"
                html += f"ALLOWED_HOSTS={settings.ALLOWED_HOSTS}\n"
                html += f"DATABASES Engine={settings.DATABASES['default']['ENGINE']}\n"
                html += f"INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}\n"
                html += "<span class='success'>Django settings loaded successfully.</span>\n"
            except Exception as e:
                html += f"<span class='error'>Django settings are not configured: {str(e)}</span>\n"
                html += f"<span class='error'>{traceback.format_exc()}</span>\n"
        except ImportError:
            html += "<span class='error'>Django is not installed.</span>\n"
        html += "</pre></div>"

        # Database check
        html += """
            <div class="section">
                <h2>Database Check</h2>
                <pre>
        """
        try:
            from django.db import connections
            from django.db.utils import OperationalError
            
            for alias in connections:
                try:
                    connection = connections[alias]
                    connection.ensure_connection()
                    html += f"<span class='success'>Connection '{alias}' is working.</span>\n"
                    connection.close()
                except OperationalError as e:
                    html += f"<span class='error'>Connection '{alias}' failed: {str(e)}</span>\n"
        except Exception as e:
            html += f"<span class='error'>Database check failed: {str(e)}</span>\n"
        html += "</pre></div>"

        # Installed packages
        html += """
            <div class="section">
                <h2>Installed Python Packages</h2>
                <pre>
        """
        try:
            import pkg_resources
            installed_packages = sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set])
            html += "\n".join(installed_packages)
        except Exception as e:
            html += f"<span class='error'>Failed to list packages: {str(e)}</span>\n"
        html += "</pre></div>"

        # Close HTML
        html += """
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())


def run_server():
    """Run the debug HTTP server"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, DebugHandler)
    print(f"Starting debug server on port {PORT}...")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
