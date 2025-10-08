#!/bin/bash

# Isolated Clean Installation Test
# Creates a temporary isolated environment for testing

set -e

TEMP_DIR="/tmp/ai-config-clean-test-$$"
BACKUP_HOME="$HOME"

echo "🧪 AI Configurator Isolated Clean Test"
echo "====================================="

# Create isolated environment
echo "📁 Creating isolated test environment..."
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Copy source code (not config)
echo "📦 Copying source code..."
cp -r /home/jschwellach/git/ai-configurator ./ai-configurator
cd ai-configurator

# Create fake HOME to avoid using host config
export HOME="$TEMP_DIR/fake-home"
mkdir -p "$HOME"

echo "🏠 Using isolated HOME: $HOME"
echo "📂 Working directory: $(pwd)"

# Clean any existing config
rm -rf "$HOME/.config/ai-configurator" 2>/dev/null || true
rm -rf "$HOME/.local/share/ai-configurator" 2>/dev/null || true

echo "🔧 Installing in isolated environment..."

# Create virtual environment
python -m venv "$HOME/venv"
source "$HOME/venv/bin/activate"

# Install dependencies
pip install -e .

echo "✅ Installation complete in isolated environment"

echo "🧪 Testing basic functionality..."

# Test commands
echo "Testing: ai-config --help"
ai-config --help > /dev/null
echo "✅ Help works"

echo "Testing: ai-config status"
ai-config status
echo "✅ Status works"

echo "Testing: ai-config production environments"
ai-config production environments
echo "✅ Production commands work"

echo "Testing: ai-config monitoring setup"
ai-config monitoring setup
echo "✅ Monitoring setup works"

echo "Testing: ai-config monitoring health"
ai-config monitoring health
echo "✅ Health check works"

echo "Testing: ai-config cache benchmark"
ai-config cache benchmark
echo "✅ Performance test works"

echo ""
echo "🎉 Isolated Clean Test PASSED!"
echo "=========================="
echo "✅ All functionality working in clean environment"
echo "📁 Test HOME: $HOME"
echo "📁 Config created: $HOME/.config/ai-configurator"
echo "📁 Logs created: $HOME/.local/share/ai-configurator/logs"

# Restore original HOME
export HOME="$BACKUP_HOME"

echo ""
echo "🧹 Cleanup: rm -rf $TEMP_DIR"
echo "💡 Test completed successfully!"
