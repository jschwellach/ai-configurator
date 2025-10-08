#!/bin/bash

# Distrobox Clean Installation Test
# This script creates a fresh Ubuntu container and tests AI Configurator installation

set -e

CONTAINER_NAME="ai-config-test"
IMAGE="ubuntu:22.04"

echo "🐳 Setting up Distrobox test environment"
echo "======================================="

# Check if distrobox is available
if ! command -v distrobox &> /dev/null; then
    echo "❌ Distrobox not found. Please install distrobox first."
    exit 1
fi

# Remove existing container if it exists
if distrobox list | grep -q "$CONTAINER_NAME"; then
    echo "🗑️  Removing existing container..."
    distrobox rm -f "$CONTAINER_NAME"
fi

# Create new container
echo "📦 Creating fresh Ubuntu container..."
distrobox create --name "$CONTAINER_NAME" --image "$IMAGE"

# Enter container and run tests
echo "🚀 Entering container and running installation test..."
distrobox enter "$CONTAINER_NAME" -- bash -c "
    set -e
    echo '📋 Installing prerequisites...'
    apt update && apt install -y python3 python3-pip git
    
    echo '📁 Setting up project...'
    cd /tmp
    cp -r /host$(pwd) ./ai-configurator
    cd ai-configurator
    
    echo '🧪 Running clean installation test...'
    bash test_clean_install.sh
"

echo ""
echo "🎉 Distrobox test completed successfully!"
echo "Container '$CONTAINER_NAME' is ready for further testing."
echo ""
echo "To enter the container manually:"
echo "  distrobox enter $CONTAINER_NAME"
echo ""
echo "To clean up:"
echo "  distrobox rm -f $CONTAINER_NAME"
