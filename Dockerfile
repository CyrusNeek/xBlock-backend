# Stage 1: Install dependencies
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create a non-root user
RUN adduser --disabled-password appuser
RUN chown -R appuser /app
USER appuser

EXPOSE 8080

CMD ["./entrypoint.sh"]
