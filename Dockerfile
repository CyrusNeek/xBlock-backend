# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Speed up builds by reducing logs and skipping cache
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential libpq-dev && apt-get clean

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY . .

# Stage 2: Runtime image
FROM python:3.11-slim as runner

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Entrypoint
RUN chmod +x ./entrypoint.sh
EXPOSE 8080
CMD ["./entrypoint.sh"]
