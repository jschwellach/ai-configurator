---
title: "Installation Guide"
description: "Complete installation guide for AI Configurator"
category: "user"
tags: ["installation", "setup", "getting-started"]
version: "1.0"
last_updated: "2025-01-31"
related_docs:
  - "development/setup.md"
  - "troubleshooting.md"
---

# AI Configurator Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Dependencies**: See `requirements.txt` for full list

## Installation Methods

### Using uv (Recommended)

The easiest way to install AI Configurator is using `uv`, which handles Python dependencies automatically:

```bash
# Install uv if you haven't already
pip install uv

# Install AI Configurator from source
uv tool install --from . ai-configurator

# Or install from a git repository
uv tool install --from git+https://github.com/your-org/ai-configurator.git ai-configurator

# Run directly without installing
uv run --from . ai-configurator --help
```

### Using pip

You can also install using pip:

```bash
# Install from source directory
pip install -e .

# Or install from PyPI (when published)
pip install ai-configurator

# Install dependencies separately if needed
pip install -r requirements.txt
```

### Development Installation

For development, install with development dependencies:

```bash
# Clone the repository
git clone https://github.com/your-org/ai-configurator.git
cd ai-configurator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

## Verify Installation

After installation, verify that AI Configurator is working:

```bash
# Check version and help
ai-config --version
ai-config --help

# Show configuration formats
ai-config formats

# Show available commands
ai-config profile --help
ai-config yaml --help
ai-config migrate --help

# Check installation status
ai-config status
```

## Quick Start

1. **Check current configuration status:**

   ```bash
   ai-config status
   ```

2. **Install base configuration:**

   ```bash
   ai-config install
   ```

3. **Install with specific profile:**

   ```bash
   ai-config install --profile solutions-architect
   ```

4. **Create a new YAML profile:**

   ```bash
   ai-config profile create my-profile --format yaml
   ```

5. **Validate configurations:**

   ```bash
   ai-config yaml validate
   ```

6. **Migrate from JSON to YAML:**
   ```bash
   ai-config migrate preview
   ai-config migrate run --all
   ```

## Platform-Specific Instructions

### Windows

```cmd
# Using Command Prompt
pip install uv
uv tool install --from . ai-configurator

# Using PowerShell
python -m pip install uv
uv tool install --from . ai-configurator
```

### macOS

```bash
# Using Homebrew (if available)
brew install uv
uv tool install --from . ai-configurator

# Using pip
pip install uv
uv tool install --from . ai-configurator
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
python3 -m pip install uv
uv tool install --from . ai-configurator

# CentOS/RHEL/Fedora
sudo yum install python3-pip  # or dnf
python3 -m pip install uv
uv tool install --from . ai-configurator
```

## Troubleshooting

### Missing Dependencies

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Virtual Environment Issues

If the `ai-config` command doesn't work after installation, try:

```bash
# Reinstall in the current environment
pip uninstall ai-configurator -y
pip install -e .

# Or run directly with Python
python -m ai_configurator.cli --help
```

### uv Installation Issues

If uv installation fails:

```bash
# Update uv
pip install --upgrade uv

# Try installing with verbose output
uv tool install --from . ai-configurator --verbose

# Clear uv cache if needed
uv cache clean
```

### Permission Issues

On Unix-like systems, if you encounter permission errors:

```bash
# Install to user directory
pip install --user -e .

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Python Version Issues

If you have multiple Python versions:

```bash
# Use specific Python version
python3.8 -m pip install uv
python3.8 -m uv tool install --from . ai-configurator

# Or specify Python in virtual environment
python3.8 -m venv venv
source venv/bin/activate
pip install -e .
```

## Uninstallation

To remove AI Configurator:

```bash
# If installed with uv
uv tool uninstall ai-configurator

# If installed with pip
pip uninstall ai-configurator

# Remove configuration files (optional)
rm -rf ~/.ai-configurator
```

## Next Steps

After successful installation:

1. Read the [Configuration Guide](configuration.md) to understand how to customize AI Configurator
2. Check out [Profile Management](profiles.md) to learn about switching between different configurations
3. See [MCP Server Setup](mcp-servers.md) for setting up MCP servers
4. Visit [Troubleshooting](troubleshooting.md) if you encounter any issues

## Support

For installation issues and questions:

- Check the [Troubleshooting Guide](troubleshooting.md)
- Open an issue on [GitHub Issues](https://github.com/your-org/ai-configurator/issues)
- Run `ai-config --help` for command-specific help
- Join our [Discussions](https://github.com/your-org/ai-configurator/discussions)
