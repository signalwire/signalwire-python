# Appendix: Docker Deployment Guide

This guide covers deploying Fred using Docker for production-ready containerization.

## Table of Contents

1. [Why Docker?](#why-docker)
2. [Docker Files Overview](#docker-files-overview)
3. [Basic Dockerfile](#basic-dockerfile)
4. [Multi-Stage Build](#multi-stage-build)
5. [Docker Compose Setup](#docker-compose-setup)
6. [Building and Running](#building-and-running)
7. [Production Best Practices](#production-best-practices)

---

## Why Docker?

Docker provides several benefits for deploying Fred:

- **Consistency**: Same environment everywhere
- **Isolation**: No dependency conflicts
- **Scalability**: Easy to deploy multiple instances
- **Portability**: Runs on any Docker-enabled host
- **Security**: Contained environment with limited access

## Docker Files Overview

We'll create three Docker-related files:

1. **Dockerfile** - Basic single-stage build
2. **Dockerfile.multi** - Optimized multi-stage build
3. **docker-compose.yml** - Orchestration configuration

## Basic Dockerfile

This simple Dockerfile gets Fred running quickly:

### File: `Dockerfile`

```dockerfile
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Fred application
COPY fred.py .

# Create non-root user for security
RUN useradd -m -u 1000 freduser && chown -R freduser:freduser /app

# Switch to non-root user
USER freduser

# Expose the port Fred runs on
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/health', auth=('${SWML_BASIC_AUTH_USER}', '${SWML_BASIC_AUTH_PASSWORD}'))"

# Run Fred
CMD ["python", "fred.py"]
```

## Multi-Stage Build

For smaller, more secure images, use a multi-stage build:

### File: `Dockerfile.multi`

```dockerfile
# Stage 1: Build environment
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to a specific directory
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps:$PYTHONPATH

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/deps /app/deps

# Copy application
COPY fred.py .

# Create non-root user
RUN useradd -m -u 1000 freduser && chown -R freduser:freduser /app

# Switch to non-root user
USER freduser

# Expose port
EXPOSE 3000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health').read()"

# Run Fred
CMD ["python", "fred.py"]
```

## Docker Compose Setup

For easier management and configuration:

### File: `docker-compose.yml`

```yaml
version: '3.8'

services:
  fred:
    # Build from local Dockerfile
    build:
      context: .
      dockerfile: Dockerfile
    
    # Container name
    container_name: fred-bot
    
    # Restart policy
    restart: unless-stopped
    
    # Port mapping
    ports:
      - "3000:3000"
    
    # Environment variables
    environment:
      # Authentication
      - SWML_BASIC_AUTH_USER=${FRED_AUTH_USER:-fred_user}
      - SWML_BASIC_AUTH_PASSWORD=${FRED_AUTH_PASSWORD:-secure_password_123}
      
      # SignalWire configuration
      - SWML_PROXY_URL_BASE=${PROXY_URL:-}
      
      # Python settings
      - PYTHONUNBUFFERED=1
      
      # Timezone
      - TZ=America/New_York
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:3000/health', auth=('${SWML_BASIC_AUTH_USER:-fred_user}', '${SWML_BASIC_AUTH_PASSWORD:-secure_password_123}'))"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
```

### File: `.env` (Environment Configuration)

```bash
# Authentication
FRED_AUTH_USER=fred_prod
FRED_AUTH_PASSWORD=your_secure_password_here

# Proxy configuration (if needed)
# PROXY_URL=https://your-domain.com

# Other settings
TZ=America/New_York
```

## Building and Running

### Using Docker Directly

```bash
# Build the image
docker build -t fred-bot:latest .

# Run with environment variables
docker run -d \
  --name fred \
  -p 3000:3000 \
  -e SWML_BASIC_AUTH_USER=fred_user \
  -e SWML_BASIC_AUTH_PASSWORD=secure_password \
  fred-bot:latest

# View logs
docker logs -f fred

# Stop Fred
docker stop fred

# Remove container
docker rm fred
```

### Using Docker Compose

```bash
# Start Fred (builds if needed)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop Fred
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Scale to multiple instances
docker-compose up -d --scale fred=3
```

## Production Best Practices

### 1. Security Hardening

Create a more secure Dockerfile:

```dockerfile
# Use distroless base image for minimal attack surface
FROM python:3.9-slim as builder
# ... build steps ...

FROM gcr.io/distroless/python3-debian11
COPY --from=builder /app /app
WORKDIR /app
EXPOSE 3000
ENTRYPOINT ["python", "fred.py"]
```

### 2. Secrets Management

Never hardcode credentials. Keep them out of the compose file by loading an
environment file that is not committed to source control:

```yaml
# docker-compose using an env file for secrets
version: '3.8'

services:
  fred:
    # ... other config ...
    env_file:
      - ./secrets/fred.env   # not committed; holds SWML_BASIC_AUTH_PASSWORD=...
```

```bash
# ./secrets/fred.env
SWML_BASIC_AUTH_USER=fred
SWML_BASIC_AUTH_PASSWORD=your-secure-password
```

The SDK reads `SWML_BASIC_AUTH_USER` / `SWML_BASIC_AUTH_PASSWORD` directly from
the process environment.

### 3. Reverse Proxy Setup

Add nginx for SSL termination:

```yaml
# docker-compose with nginx
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - fred
  
  fred:
    # Remove external port exposure
    expose:
      - "3000"
    # ... rest of config ...
```

### 4. Monitoring and Logging

Add Prometheus metrics and centralized logging:

```yaml
# Enhanced docker-compose
version: '3.8'

services:
  fred:
    # ... fred config ...
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=3000"
      - "prometheus.io/path=/metrics"
  
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
```

### 5. Auto-restart and Updates

Use Watchtower for automatic updates:

```yaml
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  command: --interval 300 fred-bot
```

## Container Registry Deployment

Push to a registry for cloud deployment:

```bash
# Tag for registry
docker tag fred-bot:latest myregistry.com/fred-bot:latest

# Push to registry
docker push myregistry.com/fred-bot:latest

# Deploy from registry
docker run -d \
  --name fred \
  -p 3000:3000 \
  --env-file .env \
  myregistry.com/fred-bot:latest
```

## Kubernetes Deployment

For Kubernetes, create a deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fred-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fred-bot
  template:
    metadata:
      labels:
        app: fred-bot
    spec:
      containers:
      - name: fred
        image: myregistry.com/fred-bot:latest
        ports:
        - containerPort: 3000
        env:
        - name: SWML_BASIC_AUTH_USER
          valueFrom:
            secretKeyRef:
              name: fred-secrets
              key: username
        - name: SWML_BASIC_AUTH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fred-secrets
              key: password
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

## Troubleshooting Docker Deployments

### Check Container Status

```bash
# List containers
docker ps -a

# Inspect container
docker inspect fred

# Check resource usage
docker stats fred
```

### Debug Inside Container

```bash
# Execute shell in running container
docker exec -it fred /bin/bash

# Run one-off command
docker exec fred python -c "import signalwire_agents; print(signalwire_agents.__version__)"
```

### Common Issues

1. **Port conflicts**: Change host port in mapping
2. **Permission errors**: Ensure fred.py is executable
3. **Memory issues**: Increase limits in docker-compose
4. **Network issues**: Check Docker network configuration

## Summary

Docker deployment provides a robust, scalable way to run Fred in production. Start with the basic Dockerfile for development, then move to multi-stage builds and orchestration for production deployments.

---

[← Back to Overview](README.md) | [← Previous: Complete Code](appendix-complete-code.md)