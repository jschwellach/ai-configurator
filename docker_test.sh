#!/bin/bash

# Docker Clean Installation Test
# Runs AI Configurator test in completely isolated Docker container

set -e

IMAGE_NAME="ai-config-test"
CONTAINER_NAME="ai-config-test-run"

echo "🐳 Docker Clean Installation Test"
echo "================================="

cd "$(dirname "$0")"

# Build test image
echo "🔨 Building test Docker image..."
docker build -f Dockerfile.test -t "$IMAGE_NAME" .

# Run test container
echo "🚀 Running clean installation test..."
docker run --rm --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo ""
echo "🎉 Docker test completed successfully!"
echo "✅ AI Configurator works in completely clean environment"
