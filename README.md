# AI Configurator

Cross-platform configuration manager for Amazon Q CLI, contexts, profiles, and MCP servers.

## 🎯 Purpose

Simplify the setup and sharing of Amazon Q CLI configurations across teams and environments. Whether you're setting up a new machine, onboarding team members, or standardizing configurations across your organization, AI Configurator makes it seamless.

## ✨ Features

- **Simple Commands**: Just 4 essential commands - list, install, remove, info
- **Profile Management**: Switch between different work contexts easily
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Context Sharing**: Share knowledge bases and contexts across teams
- **Safe Operations**: Simple installation to Amazon Q directory

## 📦 Installation

### Quick Install

```bash
# Using pip
pip install ai-configurator

# Verify installation
ai-config --help
```

### Development Setup

```bash
# Clone and setup for development
git clone <repository-url>
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .
```

## 🚀 Quick Start

```bash
# List available profiles
ai-config list

# Install a profile
ai-config install developer-v1

# Check profile details
ai-config info developer-v1

# Remove a profile
ai-config remove developer-v1
```

## 📋 Commands

```bash
ai-config list [--query QUERY]           # List available profiles
ai-config install PROFILE_ID             # Install a profile
ai-config remove PROFILE_ID              # Remove an installed profile
ai-config info PROFILE_ID                # Show profile details
```

## 📚 Available Profiles

### Role-Based Profiles
- **developer-v1** - Complete profile for software developers with development guidelines and best practices
- **solutions-architect-v1** - Complete profile for solutions architects with AWS best practices and architecture patterns
- **engagement-manager-v1** - Complete profile for engagement managers with client communication and project delivery contexts

### Task-Based Profiles
- **document-helper-v1** - Profile for document writers with guidelines for creating and editing documents effectively
- **default-v1** - Basic profile configuration with minimal context for general use

### Meta Profiles
- **documentation-v1** - Complete documentation profile for AI Configurator itself with installation guides and development docs

## 🏗️ Project Structure

```
ai-configurator/
├── ai_configurator/               # Main package
│   ├── core/                      # Core functionality
│   │   ├── library_manager.py     # Library operations
│   │   ├── profile_installer.py   # Profile installation
│   │   ├── file_utils.py          # File utilities
│   │   └── catalog_schema.py      # Data models
│   └── cli.py                     # Command-line interface
├── library/                       # Configuration profiles
│   ├── default/                   # Default profile
│   ├── developer/                 # Developer profile
│   ├── solutions-architect/       # Solutions architect profile
│   └── documentation/             # Documentation profile
└── tests/                         # Test files
```

## 🛠️ Development

```bash
# Quick development setup
git clone https://github.com/your-org/ai-configurator.git
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .

# Run tests
pytest

# Test CLI
ai-config list
```

## 🔧 How It Works

1. **Profiles** are stored in the `/library/` directory
2. Each profile contains contexts (markdown files) and configuration
3. **Installing** a profile copies its contexts to `~/.aws/amazonq/contexts/`
4. **Amazon Q CLI** automatically picks up contexts from this directory
5. **Removing** a profile deletes its contexts from the Amazon Q directory

## 📖 Documentation

For comprehensive documentation, install the documentation profile:

```bash
ai-config install documentation-v1
```

This provides detailed guides for:
- Installation and setup
- Configuration management
- Profile creation
- Development setup
- MCP server configuration
- Hooks and automation

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- [GitHub Issues](https://github.com/your-org/ai-configurator/issues)
- [Documentation Profile](ai-config install documentation-v1)
- [Discussions](https://github.com/your-org/ai-configurator/discussions)

---

**Status**: ✅ Simplified and Ready for Use

**Architecture**: Dramatically simplified from 37 core modules to 5, and 10+ CLI commands to 4 essential ones.
