#!/bin/bash
# FounderOS Quick Start Script

set -e

echo "=== FounderOS Quick Start ==="

# Check for .env
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your API keys before running."
    echo "   Required: FIREWORKS_API_KEY, GOOGLE_API_KEY"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
echo "📋 Detected architecture: $ARCH"

if [ "$ARCH" = "arm64" ]; then
    echo "🍎 Apple Silicon detected. Building for linux/amd64..."
    docker buildx build --platform linux/amd64 --tag founderos:latest --load .
else
    echo "🐧 AMD64 detected. Building..."
    docker build -t founderos:latest .
fi

echo "🚀 Starting FounderOS..."
docker compose up -d

echo ""
echo "✅ FounderOS is running at http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "📖 API docs: http://localhost:8000/docs"
echo ""
echo "To stop: docker compose down"
echo "To view logs: docker compose logs -f"