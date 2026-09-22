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

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/health', auth=('${SWML_BASIC_AUTH_USER}', '${SWML_BASIC_AUTH_PASSWORD}'))"

# Run Fred
CMD ["python", "fred.py"]