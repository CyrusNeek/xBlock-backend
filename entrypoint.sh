#!/bin/bash
# Fixed line endings for Linux container (LF not CRLF)

set -x  # Show each command

echo "DEBUG: Starting container"
echo "PORT: $PORT"

# Dummy server that binds to $PORT
# This confirms that the container listens properly
echo "Starting test Python server on $PORT"

# Check if python3 command exists, otherwise use python
if command -v python3 &> /dev/null; then
    echo "Using python3 command"
    python3 -m http.server "$PORT"
else
    echo "Using python command"
    python -m http.server "$PORT"
fi
