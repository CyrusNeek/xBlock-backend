#!/bin/bash
# Fallback script for Cloud Run that runs if entrypoint.sh fails
# This will start a simple debug server to help diagnose issues

echo "===== ENTRYPOINT FAILED - STARTING FALLBACK DEBUG SERVER ====="
echo "This server is only for debugging purposes!"

# Print environment for debugging (excluding secrets)
echo "Environment variables:"
env | grep -v -E "SECRET|PASSWORD|KEY" | sort

# Start the debug server
python debug_server.py
