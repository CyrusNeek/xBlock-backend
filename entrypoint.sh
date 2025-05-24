#!/bin/bash

# This is an absolute minimal entrypoint for Cloud Run debugging
echo "DEBUG: Starting minimal entrypoint script"
echo "DEBUG: PORT=$PORT"
echo "DEBUG: User=$(whoami)"
echo "DEBUG: Current directory=$(pwd)"
echo "DEBUG: Directory contents=$(ls -la)"

# Create a simple Python socket server that just binds to PORT
cat > server.py << 'EOF'
import socket
import os
import time

print("Python server starting")

# Get the port from environment variable
port = int(os.environ.get("PORT", 8080))
print(f"Using port: {port}")

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to all interfaces on the specified port
print(f"Binding to 0.0.0.0:{port}")
s.bind(("0.0.0.0", port))

# Listen for connections
print("Listening for connections")
s.listen(1)

while True:
    print("Waiting for a connection")
    connection, client_address = s.accept()
    
    try:
        print(f"Connection from {client_address}")
        
        # Send a simple HTTP response
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nServer is running!\n"
        connection.sendall(response.encode('utf-8'))
    finally:
        # Clean up the connection
        connection.close()
EOF

# Run the server
echo "DEBUG: Starting Python server"
exec python server.py
