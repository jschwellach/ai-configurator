# AI Configurator

Cross-platform configuration manager for Amazon Q CLI, contexts, profiles, and MCP servers.

## 🎯 Purpose

Simplify the setup and sharing of Amazon Q CLI configurations across teams and environments. Whether you're setting up a new machine, onboarding team members, or standardizing configurations across your organization, AI Configurator makes it seamless.

## ✨ Features

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modular Configuration**: Pick and choose components you need
- **Profile Management**: Switch between different work contexts easily
- **Safe Operations**: Automatic backups and rollback capabilities
- **MCP Server Management**: Install and manage MCP servers effortlessly
- **Context Sharing**: Share knowledge bases and contexts across teams
- **Hook System**: Automate workflows with custom hooks

## 📦 Installation

### Using uvx (Recommended)

```bash
# Install uv/uvx if you haven't already
pip install uv

# Install AI Configurator from source
uvx install --from . ai-configurator

# Or run directly without installing
uvx run --from . uvx_install.py --help
```

### Using pip

```bash
# Install from source
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Verify installation
ai-config --help
```

### Development Installation

```bash
# Clone and install for development
git clone <repository-url>
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .

# Run tests
python test_install.py
```

## 🚀 Quick Start

```bash
# Install via pip
pip install ai-configurator

# Install base configuration
ai-config install

# Install with specific profile
ai-config install --profile solutions-architect

# Switch between profiles
ai-config profile switch development
```

## 📋 Commands

```bash
ai-config install [--profile PROFILE]     # Install configuration
ai-config update [--preserve-personal]    # Update existing config
ai-config profile list                    # List available profiles
ai-config profile switch PROFILE          # Switch to profile
ai-config backup                          # Backup current config
ai-config restore BACKUP_ID               # Restore from backup
ai-config validate                        # Validate current setup
ai-config status                          # Show configuration status
```

## 🏗️ Project Structure

```
ai-configurator/
├── src/ai_configurator/           # Main package
│   ├── commands/                  # CLI command implementations
│   ├── core/                      # Core functionality
│   └── utils/                     # Utility functions
├── configs/                       # Configuration templates
│   ├── mcp-servers/              # MCP server definitions
│   └── profiles/                 # Profile templates
├── contexts/                      # Shared context files
├── hooks/                        # Hook scripts
└── templates/                    # Configuration templates
```

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/your-org/ai-configurator.git
cd ai-configurator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/
```

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Profile Management](docs/profiles.md)
- [MCP Server Setup](docs/mcp-servers.md)
- [Custom Hooks](docs/hooks.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- [GitHub Issues](https://github.com/your-org/ai-configurator/issues)
- [Documentation](https://ai-configurator.readthedocs.io)
- [Discussions](https://github.com/your-org/ai-configurator/discussions)

---

**Status**: 🚧 Under Development - Alpha Release
