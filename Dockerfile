FROM python:3.10-slim

# Set working directory
WORKDIR /app

# (Optional) Add a simple HTTP server as a placeholder
RUN echo "from http.server import SimpleHTTPRequestHandler, test; test(SimpleHTTPRequestHandler, port=8080)" > server.py

# Copy your backend files (if any)
# COPY . .

# Expose port expected by Cloud Run
EXPOSE 8080

# Start the Python HTTP server
CMD ["python", "server.py"]
