# AI Configurator Installation Guide

## Installation with uvx (Recommended)

The easiest way to install AI Configurator is using `uvx`, which handles Python dependencies automatically:

```bash
# Install uvx if you haven't already
pip install uv

# Install AI Configurator from source
uvx install --from . ai-configurator

# Or install from a git repository
uvx install --from git+https://github.com/your-org/ai-configurator.git ai-configurator
```

## Installation with pip

You can also install using pip:

```bash
# Install from source directory
pip install -e .

# Or install from PyPI (when published)
pip install ai-configurator
```

## Development Installation

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
```

## Quick Start

1. **Check current configuration status:**
   ```bash
   ai-config status
   ```

2. **Create a new YAML profile:**
   ```bash
   ai-config profile create my-profile --format yaml
   ```

3. **Validate configurations:**
   ```bash
   ai-config yaml validate
   ```

4. **Migrate from JSON to YAML:**
   ```bash
   ai-config migrate preview
   ai-config migrate run --all
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

### uvx Installation Issues

If uvx installation fails:

```bash
# Update uv and uvx
pip install --upgrade uv

# Try installing with verbose output
uvx install --from . ai-configurator --verbose
```

## System Requirements

- Python 3.8 or higher
- Operating System: macOS, Linux, or Windows
- Dependencies: See `requirements.txt` for full list

## Support

For issues and questions:
- Check the documentation
- Open an issue on GitHub
- Run `ai-config --help` for command-specific help