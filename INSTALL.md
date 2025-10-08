# AI Configurator Installation Guide

This guide covers installation methods for AI Configurator v4.0.0 with Phase 3 production features.

## 🚀 Quick Installation

### Method 1: Direct Installation (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd ai-configurator

# Install with pip
pip install -e .

# Verify installation
ai-config --help
```

### Method 2: From PyPI (When Available)
```bash
# Install from PyPI
pip install ai-configurator

# Verify installation
ai-config --help
```

## 🐳 Testing with Distrobox

For a completely clean test environment:

```bash
# Run the automated distrobox test
./distrobox_test.sh
```

Or manually:

```bash
# Create Ubuntu container
distrobox create --name ai-config-test --image ubuntu:22.04

# Enter container
distrobox enter ai-config-test

# Inside container: install prerequisites
sudo apt update && sudo apt install -y python3 python3-pip git

# Clone and install
git clone <repository-url>
cd ai-configurator
pip install -e .

# Test installation
./test_clean_install.sh
```

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB for installation, additional space for libraries

### Python Dependencies
All dependencies are automatically installed:
- click>=8.0.0 (CLI framework)
- rich>=13.0.0 (Rich terminal UI)
- pydantic>=2.0.0 (Data validation)
- pyyaml>=6.0.0 (YAML configuration)
- gitpython>=3.1.0 (Git integration)
- watchdog>=3.0.0 (File monitoring)
- And more...

## 🔧 Post-Installation Setup

### 1. Initial Configuration
```bash
# Check system status
ai-config status

# Setup production logging
ai-config monitoring setup

# Run health check
ai-config monitoring health
```

### 2. Quick Start Wizard
```bash
# Interactive setup for new users
ai-config wizard quick-start
```

### 3. Performance Optimization
```bash
# Preload cache for better performance
ai-config cache preload

# Run performance benchmark
ai-config cache benchmark
```

## 🏗️ Development Installation

For contributors and developers:

```bash
# Clone repository
git clone <repository-url>
cd ai-configurator

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Run tests
pytest

# Run with coverage
pytest --cov=ai_configurator
```

## 🌍 Environment-Specific Setup

### Development Environment
```bash
# Set environment
export AI_CONFIG_ENVIRONMENT=development

# Generate development config
ai-config production generate --env development

# Check configuration
ai-config production show
```

### Production Environment
```bash
# Set environment variables
export AI_CONFIG_ENVIRONMENT=production
export AI_CONFIG_SECRET_KEY=your-secret-key
export AI_CONFIG_HOST=0.0.0.0
export AI_CONFIG_PORT=8000

# Generate production config
ai-config production generate --env production

# Validate production readiness
ai-config production validate --env production
```

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check Python version
python --version  # Should be 3.9+

# Check installation
pip list | grep ai-configurator

# Reinstall if needed
pip uninstall ai-configurator
pip install -e .
```

#### Permission Errors
```bash
# Check config directory permissions
ls -la ~/.config/ai-configurator

# Fix permissions if needed
chmod -R 755 ~/.config/ai-configurator
```

#### Git Integration Issues
```bash
# Check Git availability
git --version

# Test Git operations
ai-config git status
```

### Health Diagnostics
```bash
# Run comprehensive health check
ai-config monitoring health

# Check system configuration
ai-config production show

# View recent logs
ai-config monitoring logs --lines 20
```

### Performance Issues
```bash
# Check cache statistics
ai-config cache stats

# Clear cache if needed
ai-config cache clear

# Run performance benchmark
ai-config cache benchmark
```

## 📁 Directory Structure

After installation, AI Configurator creates:

```
~/.config/ai-configurator/          # Main configuration
├── config-development.yaml         # Environment configs
├── config-production.yaml
├── library/                        # Knowledge library
├── personal/                       # Personal overrides
├── agents/                         # Agent configurations
├── registry/                       # MCP server registry
└── backups/                        # Automatic backups

~/.local/share/ai-configurator/     # Data and logs
├── logs/                           # Application logs
│   ├── ai-configurator.log        # Main log
│   ├── errors.log                 # Error log
│   └── structured.log             # JSON structured log
└── cache/                          # Performance cache
```

## 🔄 Upgrading

### From Previous Versions
```bash
# Backup existing configuration
ai-config library sync

# Update installation
git pull origin main
pip install -e . --upgrade

# Run migration if needed
ai-config wizard quick-start --upgrade
```

### Version Compatibility
- **v4.0.0**: Full Phase 3 features (current)
- **v3.x**: Phase 2 features (backward compatible)
- **v2.x**: Phase 1 features (migration required)

## 🆘 Getting Help

### Documentation
- **README.md**: Overview and quick start
- **docs/USER_GUIDE.md**: Comprehensive user guide
- **docs/TROUBLESHOOTING.md**: Detailed troubleshooting

### Commands
```bash
# General help
ai-config --help

# Command-specific help
ai-config production --help
ai-config monitoring --help
ai-config git --help
```

### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and questions
- **Documentation**: Inline help and guides

## ✅ Verification Checklist

After installation, verify these work:

- [ ] `ai-config --help` shows help text
- [ ] `ai-config status` shows system status
- [ ] `ai-config monitoring health` passes all checks
- [ ] `ai-config production environments` lists environments
- [ ] `ai-config cache stats` shows cache information
- [ ] `ai-config sync status` shows library status

If all items pass, your installation is successful! 🎉
