# Appendix B: Docker Deployment

A container packages Fred with its Python version and dependencies, so it runs the same way on your machine and on a server. This appendix covers the Docker files in `tutorial/fred/`, how to build and run them, and what changes in production.

## Table of Contents

1. [Why Docker?](#why-docker)
2. [Docker Files Overview](#docker-files-overview)
3. [Basic Dockerfile](#basic-dockerfile)
4. [Multi-Stage Build](#multi-stage-build)
5. [Docker Compose Setup](#docker-compose-setup)
6. [Building and Running](#building-and-running)
7. [Production Best Practices](#production-best-practices)
8. [Container Registry Deployment](#container-registry-deployment)
9. [Kubernetes Deployment](#kubernetes-deployment)
10. [Troubleshooting Docker Deployments](#troubleshooting-docker-deployments)

---

## Why Docker?

Running Fred in a container has five benefits:

- **Consistency**: the same environment everywhere
- **Isolation**: Fred's dependencies can't conflict with other software
- **Scalability**: more copies of Fred start from the same image
- **Portability**: the image runs on any host with Docker
- **Security**: the process runs as an unprivileged user, with limited access to the host

## Docker Files Overview

The tutorial directory includes four Docker-related files:

1. **`Dockerfile`**: a single-stage build
2. **`Dockerfile.multi`**: a multi-stage build that produces a smaller image
3. **`docker-compose.yml`**: settings for running Fred with Docker Compose
4. **`.env.example`**: the settings Compose reads, to copy to `.env`

## Basic Dockerfile

### File: `Dockerfile`

The single-stage `Dockerfile` installs the requirements and runs Fred as an unprivileged user:

```dockerfile
# Use official Python runtime as base image
FROM python:3.11-slim

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

# Health check: /health needs no credentials, and urlopen fails on an error status
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')"

# Run Fred
CMD ["python", "fred.py"]
```

The health check calls `/health`, which needs no credentials. `urlopen` raises an error for a failed request, so Docker marks the container unhealthy when Fred stops answering.

## Multi-Stage Build

### File: `Dockerfile.multi`

A multi-stage build installs the dependencies in one image and copies only the result into the final one, which leaves the build tools out:

```dockerfile
# Stage 1: Build environment
FROM python:3.11-slim AS builder

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
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/deps

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

### File: `docker-compose.yml`

Compose keeps the settings for running Fred in one file:

```yaml
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
      # Authentication: Compose refuses to start without a password
      - SWML_BASIC_AUTH_USER=${FRED_AUTH_USER:-fred}
      - SWML_BASIC_AUTH_PASSWORD=${FRED_AUTH_PASSWORD:?Set FRED_AUTH_PASSWORD in .env}
      
      # Request signatures, and one tool-token secret for every copy of Fred
      - SIGNALWIRE_SIGNING_KEY=${SIGNALWIRE_SIGNING_KEY:-}
      - SIGNALWIRE_SWAIG_SECRET=${SIGNALWIRE_SWAIG_SECRET:-}
      
      # SignalWire configuration
      - SWML_PROXY_URL_BASE=${PROXY_URL:-}
      
      # Python settings
      - PYTHONUNBUFFERED=1
      
      # Timezone
      - TZ=America/New_York
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')"]
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

Compose refuses to start until `FRED_AUTH_PASSWORD` has a value, so Fred never runs with a password someone could guess.

### File: `.env`

Compose reads `.env` from the same directory. Copy `.env.example` to `.env` and fill in the values:

```bash
# Fred Bot Docker Environment Configuration
# Copy this file to .env and update with your values

# Authentication
FRED_AUTH_USER=fred
FRED_AUTH_PASSWORD=a-long-random-password

# Your project's signing key, from the SignalWire dashboard. With it set,
# Fred rejects requests SignalWire didn't sign.
SIGNALWIRE_SIGNING_KEY=

# The secret behind Fred's tool tokens. Set it so calls in progress survive
# a restart, and use the same value for every copy of Fred.
SIGNALWIRE_SWAIG_SECRET=

# Proxy configuration (if needed)
# PROXY_URL=https://your-domain.com

# Other settings
TZ=America/New_York
```

Keep `.env` out of version control.

## Building and Running

You can run Fred with Docker directly, or with Compose.

### Using Docker Directly

Build the image, then run it with the credentials as environment variables:

```bash
# Build the image
docker build -t fred-bot:latest .

# Run with environment variables
docker run -d \
  --name fred \
  -p 3000:3000 \
  -e SWML_BASIC_AUTH_USER=fred \
  -e SWML_BASIC_AUTH_PASSWORD=a-long-random-password \
  fred-bot:latest

# View logs
docker logs -f fred

# Stop Fred
docker stop fred

# Remove container
docker rm fred
```

### Using Docker Compose

Compose builds the image when it needs to:

```bash
# Start Fred (builds if needed)
docker compose up -d

# View logs
docker compose logs -f

# Stop Fred
docker compose down

# Rebuild and restart
docker compose up -d --build
```

## Production Best Practices

A production deployment adds five things to these files.

### 1. Security Hardening

The images already run Fred as the unprivileged `freduser`, and copy only `requirements.txt` and `fred.py`, so no secrets end up in the image. Build production images from `Dockerfile.multi`, which leaves the compiler out of the final image.

### 2. Secrets Management

Keep secrets out of the Compose file and the image. Load them from an environment file that isn't committed to source control:

```yaml
# docker-compose using an env file for secrets
services:
  fred:
    # ... other config ...
    env_file:
      - ./secrets/fred.env   # not committed
```

The file sets the variables the SDK reads:

```bash
# ./secrets/fred.env
SWML_BASIC_AUTH_USER=fred
SWML_BASIC_AUTH_PASSWORD=a-long-random-password
SIGNALWIRE_SIGNING_KEY=your-signing-key
SIGNALWIRE_SWAIG_SECRET=another-long-random-string
```

The SDK reads these variables from the process environment. [Lesson 6](06-running-testing.md#production-considerations) explains what each one protects.

### 3. Reverse Proxy Setup

A reverse proxy such as nginx terminates HTTPS in front of Fred:

```yaml
# docker-compose with nginx
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

Set `SWML_PROXY_URL_BASE` to Fred's public HTTPS address, so the function URLs in its SWML point at the proxy.

### 4. Logging

Fred logs to standard output, so `docker logs` and your platform's log collector see everything. The Compose file's `json-file` driver keeps three files of up to 10 MB each.

### 5. Running More Than One Copy

Every copy of Fred must use the same `SIGNALWIRE_SWAIG_SECRET`. A function's token is signed with that secret, and SignalWire may send the call's next request to a different copy. With different secrets, those requests are refused.

To run several copies with Compose, remove `container_name` and the fixed port mapping, and put a load balancer in front of them.

## Container Registry Deployment

To deploy from a registry, tag and push the image, then run it on the server with the secrets file:

```bash
# Tag for registry
docker tag fred-bot:latest myregistry.com/fred-bot:latest

# Push to registry
docker push myregistry.com/fred-bot:latest

# Deploy from registry
docker run -d \
  --name fred \
  -p 3000:3000 \
  --env-file ./secrets/fred.env \
  myregistry.com/fred-bot:latest
```

## Kubernetes Deployment

On Kubernetes, a Deployment runs the copies and reads the secrets from a Secret named `fred-secrets`:

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
        - name: SIGNALWIRE_SIGNING_KEY
          valueFrom:
            secretKeyRef:
              name: fred-secrets
              key: signing-key
        - name: SIGNALWIRE_SWAIG_SECRET
          valueFrom:
            secretKeyRef:
              name: fred-secrets
              key: swaig-secret
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

All three replicas read `SIGNALWIRE_SWAIG_SECRET` from the same Secret, so any replica can check a token another one issued.

## Troubleshooting Docker Deployments

These commands show what a container is doing.

### Check Container Status

List, inspect and measure the container:

```bash
# List containers
docker ps -a

# Inspect container
docker inspect fred

# Check resource usage
docker stats fred
```

### Debug Inside Container

Open a shell in the container, or run one command in it:

```bash
# Execute shell in running container
docker exec -it fred /bin/bash

# Run one-off command
docker exec fred python -c "import signalwire; print(signalwire.__version__)"
```

### Common Issues

Four problems come up most often:

1. **Port conflicts**: another program uses port 3000. Change the host side of the port mapping, for example `-p 3001:3000`.
2. **Permission errors**: Fred runs as `freduser`, which can only write to directories it owns, such as `/app`.
3. **Memory limits**: if the container is killed for using too much memory, raise the limit in `docker-compose.yml`.
4. **Refused tool calls**: with more than one copy, check that every copy has the same `SIGNALWIRE_SWAIG_SECRET`.

## Next Steps

Start with the single-stage `Dockerfile` while you develop, and move to `Dockerfile.multi` and a secrets file for production. To build an agent whose actions have consequences, continue with the [Full-Guardrails Agent tutorial](../../full-guardrails-agent/tutorial/README.md).

---

[Previous: Complete Code](appendix-complete-code.md) | [Overview](README.md)
