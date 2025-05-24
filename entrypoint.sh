#!/bin/bash
# Ultra-simple entrypoint for debugging Cloud Run startup

# Ensure we continue even if commands fail
set +e

# Make sure we can see what's happening
echo "================ STARTING CONTAINER ================" 
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "PORT environment variable: $PORT"

# Create the absolute simplest HTTP server possible
echo "Creating minimal HTTP server..."
cat > minimal_server.py << 'EOF'
#!/usr/bin/env python3
import os
import socket
import sys

# Get port from environment with fallback to 8080
port = int(os.environ.get("PORT", 8080))

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow reuse of the address
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # Bind to all interfaces on the specified port
    sock.bind(("0.0.0.0", port))
    print(f"Successfully bound to port {port}")
    
    # Start listening
    sock.listen(5)
    print(f"Server is listening on port {port}")
    
    print("Ready for connections")
    
    # Main server loop
    while True:
        # Accept a connection
        client, addr = sock.accept()
        print(f"Connection from {addr}")
        
        try:
            # Read the request (but we don't need to parse it for this test)
            data = client.recv(1024)
            
            # Basic HTTP response
            response = b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
            response += b"<html><body><h1>Cloud Run Debug Server</h1>"
            response += b"<p>Container is running!</p>"
            response += b"<p>This confirms the container can bind to the port.</p>"
            response += b"</body></html>"
            
            # Send the response
            client.sendall(response)
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            # Close the connection
            client.close()
            
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

# Make it executable
chmod +x minimal_server.py

# Run the server
python minimal_server.py
