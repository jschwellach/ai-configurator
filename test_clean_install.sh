#!/bin/bash

# Clean Installation Test Script for AI Configurator
# This script tests a clean installation in a fresh environment

set -e  # Exit on any error

echo "🧪 AI Configurator Clean Installation Test"
echo "=========================================="

# Check if we're in a clean environment
if [ -d "$HOME/.config/ai-configurator" ]; then
    echo "⚠️  Found existing AI Configurator config. This may not be a clean test."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Step 1: Installing AI Configurator..."
pip install -e .

echo "✅ Installation complete!"

echo "🔧 Step 2: Testing basic commands..."

# Test help command
echo "Testing: ai-config --help"
ai-config --help > /dev/null
echo "✅ Help command works"

# Test status command
echo "Testing: ai-config status"
ai-config status
echo "✅ Status command works"

# Test production commands
echo "Testing: ai-config production environments"
ai-config production environments
echo "✅ Production commands work"

# Test monitoring setup
echo "Testing: ai-config monitoring setup"
ai-config monitoring setup
echo "✅ Monitoring setup works"

# Test health check
echo "Testing: ai-config monitoring health"
ai-config monitoring health
echo "✅ Health check works"

# Test cache commands
echo "Testing: ai-config cache stats"
ai-config cache stats
echo "✅ Cache commands work"

# Test sync commands
echo "Testing: ai-config sync status"
ai-config sync status
echo "✅ Sync commands work"

echo "🎉 All basic tests passed!"

echo "🧙 Step 3: Testing wizard (optional)..."
read -p "Run interactive wizard test? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running quick-start wizard..."
    ai-config wizard quick-start
    echo "✅ Wizard completed"
fi

echo "📊 Step 4: Performance test..."
echo "Running cache benchmark..."
ai-config cache benchmark

echo "🏥 Step 5: Final health check..."
ai-config monitoring health

echo ""
echo "🎉 Clean Installation Test Complete!"
echo "=================================="
echo "✅ All core functionality working"
echo "✅ Production features operational"
echo "✅ Performance optimization active"
echo ""
echo "📁 Configuration created at: $HOME/.config/ai-configurator"
echo "📄 Logs available at: $HOME/.local/share/ai-configurator/logs"
echo ""
echo "Next steps:"
echo "1. Create your first agent: ai-config wizard create-agent"
echo "2. Set up Git library: ai-config git configure <repo-url>"
echo "3. Explore MCP servers: ai-config mcp browse"
