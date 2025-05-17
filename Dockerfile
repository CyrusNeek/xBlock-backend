# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Add a very simple hello-world Python server
RUN echo "from http.server import SimpleHTTPRequestHandler, test; test(SimpleHTTPRequestHandler)" > server.py

# Run the simple server
CMD ["python", "server.py"]
