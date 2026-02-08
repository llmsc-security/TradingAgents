#!/bin/bash
# Build and run script for TradingAgents Docker container
# Maps host port 11360 to container port 11360

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building TradingAgents Docker image..."
docker build -t tradingagents:latest .

echo ""
echo "Starting TradingAgents container..."
echo "Container will be available at http://localhost:11360"
echo ""

docker run \
    --rm \
    -p 11360:11360 \
    --name tradingagents \
    -v "$(pwd):/app:ro" \
    --env-file .env \
    tradingagents:latest
