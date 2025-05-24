#!/bin/bash

set -x  # Show each command

echo "DEBUG: Starting container"
echo "PORT: $PORT"

# Dummy server that binds to $PORT
# This confirms that the container listens properly
echo "Starting test Python server on $PORT"
python3 -m http.server "$PORT"
