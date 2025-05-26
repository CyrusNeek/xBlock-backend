"""
Minimal Flask server for Cloud Run deployment debugging
This server will definitely start and listen on the required port
"""

import os
import sys
import json
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Get port from environment variable
port = int(os.environ.get('PORT', 8080))

@app.route('/')
def home():
    """Root endpoint that displays debug information"""
    logger.info("Root endpoint accessed")
    
    # Collect environment information (excluding sensitive data)
    env_vars = {}
    for key, value in os.environ.items():
        if any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']):
            env_vars[key] = '[REDACTED]'
        else:
            env_vars[key] = value
    
    # Collect system information
    system_info = {
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'directory_contents': os.listdir('.'),
    }
    
    # Return debug information
    return jsonify({
        'status': 'OK',
        'message': 'xBlock Debug Server is running',
        'environment': env_vars,
        'system': system_info,
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return jsonify({'status': 'OK'})

@app.route('/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing POST requests"""
    data = request.get_json(silent=True) or {}
    logger.info(f"Echo endpoint accessed with data: {data}")
    return jsonify({
        'status': 'OK',
        'echo': data
    })

if __name__ == '__main__':
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
