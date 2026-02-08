#!/bin/bash
# Entrypoint script for TradingAgents Docker container
# Starts the TradingAgents HTTP server

set -e

echo "Starting TradingAgents HTTP server..."

# Set environment variables
export PYTHONUNBUFFERED=1

# Change to app directory
cd /app

# Run the HTTP server
exec python http_server.py "$@"
