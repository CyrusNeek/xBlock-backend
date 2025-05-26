"""
Minimal Flask application for Cloud Run
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'xBlock Debug Server is running'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/env')
def environment():
    # Filter out sensitive environment variables
    env_vars = {}
    for key, value in os.environ.items():
        if any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']):
            env_vars[key] = '[REDACTED]'
        else:
            env_vars[key] = value
    return jsonify(env_vars)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
