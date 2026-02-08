# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create non-root user for security
RUN groupadd -r tradingagents && \
    useradd -r -g tradingagents -u 1000 -m -d /home/tradingagents tradingagents && \
    chown -R tradingagents:tradingagents /app

# Switch to non-root user
USER tradingagents

# Set working directory
WORKDIR /app

# Expose the port from port_mapping_50_gap10.json
EXPOSE 11360

# Default command - runs the HTTP server
CMD ["python", "http_server.py"]
