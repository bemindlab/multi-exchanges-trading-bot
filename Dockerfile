# Multi-stage Dockerfile for Trading Bot
# =====================================

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    pkg-config \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements_hummingbot.txt ./

# Install Python dependencies (skip TA-Lib for now)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create non-root user
RUN groupadd -r trading && useradd -r -g trading trading
RUN chown -R trading:trading /app

# =============================================================================
# Development stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install -r requirements_hummingbot.txt
RUN pip install -e ".[dev]"

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    net-tools \
    telnet \
    && rm -rf /var/lib/apt/lists/*

# Create directories for development
RUN mkdir -p /app/logs /app/temp /app/test-results
RUN chown -R trading:trading /app/logs /app/temp /app/test-results

# Switch to non-root user
USER trading

# Expose ports
EXPOSE 8000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "main.py", "--mode", "webhook"]

# =============================================================================
# Production stage
# =============================================================================
FROM base as production

# Install only production dependencies
RUN pip install -r requirements_hummingbot.txt

# Remove development packages and clean up
RUN apt-get update && apt-get remove -y \
    build-essential \
    git \
    wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

# Create production directories
RUN mkdir -p /app/logs /app/temp
RUN chown -R trading:trading /app/logs /app/temp

# Copy only necessary files
COPY --chown=trading:trading src/ ./src/
COPY --chown=trading:trading config/ ./config/
COPY --chown=trading:trading main.py cli.py ./

# Switch to non-root user
USER trading

# Expose only necessary port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["python", "main.py", "--mode", "webhook"]

# =============================================================================
# Test stage
# =============================================================================
FROM base as test

# Install all dependencies including test dependencies
RUN pip install -r requirements_hummingbot.txt
RUN pip install -e ".[dev]"

# Install additional testing tools
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create test directories
RUN mkdir -p /app/test-results /app/test-data /app/coverage
RUN chown -R trading:trading /app/test-results /app/test-data /app/coverage

# Copy test files
COPY --chown=trading:trading tests/ ./tests/
COPY --chown=trading:trading pytest.ini ./

# Switch to non-root user
USER trading

# Default test command
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=html", "--cov-report=xml"]

# =============================================================================
# Hummingbot stage
# =============================================================================
FROM hummingbot/hummingbot:latest as hummingbot

# Install additional dependencies for MQTT integration
USER root
RUN apt-get update && apt-get install -y \
    python3-pip \
    && pip3 install paho-mqtt \
    && rm -rf /var/lib/apt/lists/*

# Copy MQTT integration scripts
COPY --chown=hummingbot:hummingbot scripts/hummingbot-mqtt/ /home/hummingbot/scripts/

# Switch back to hummingbot user
USER hummingbot

# Default command
CMD ["./bin/hummingbot_quickstart.py"]

# =============================================================================
# Monitoring stage (Prometheus + Grafana)
# =============================================================================
FROM prom/prometheus:latest as monitoring

# Copy monitoring configuration
COPY config/prometheus/ /etc/prometheus/

# Expose Prometheus port
EXPOSE 9090

# =============================================================================
# Nginx stage
# =============================================================================
FROM nginx:alpine as nginx

# Install additional tools
RUN apk add --no-cache \
    curl \
    openssl

# Copy nginx configuration
COPY config/nginx/ /etc/nginx/

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1 