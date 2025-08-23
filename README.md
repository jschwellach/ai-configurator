# AI Configurator

Cross-platform configuration manager for Amazon Q CLI agents, contexts, and profiles.

## 🎯 Purpose

Simplify the setup and sharing of Amazon Q CLI agent configurations across teams and environments. Whether you're setting up a new machine, onboarding team members, or standardizing configurations across your organization, AI Configurator makes it seamless.

## ✨ Features

- **Agent-Based**: Creates Amazon Q CLI agents instead of copying context files
- **Simple Commands**: Essential commands for profiles and agent management
- **Profile Management**: Install profiles as Amazon Q CLI agents
- **Base Contexts**: Organizational contexts automatically included in all agents
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Context Sharing**: Share knowledge bases and contexts across teams
- **Config Directory**: Installs library to `~/.config/ai-configurator/library`

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

# Install a profile as an Amazon Q CLI agent
ai-config install developer-v1

# Use the agent
q chat --agent developer-v1

# Check installed agents
ai-config agents

# Remove an agent
ai-config remove developer-v1
```

## 📋 Commands

### Profile Management
```bash
ai-config list [--query QUERY]           # List available profiles
ai-config install PROFILE_ID             # Install a profile as an agent
ai-config remove PROFILE_ID              # Remove an installed agent
ai-config info PROFILE_ID                # Show profile details
ai-config agents                         # List installed agents
ai-config refresh                        # Refresh library from source
```

All commands support `--format json` for programmatic use.

## 🤖 Agent-Based Architecture

AI Configurator now creates **Amazon Q CLI agents** instead of copying context files. This aligns with the latest Amazon Q Developer CLI architecture:

### How It Works

1. **Profiles** are stored in the library (`~/.config/ai-configurator/library/`)
2. **Installing** a profile creates an Amazon Q CLI agent configuration in `~/.aws/amazonq/cli-agents/`
3. **Base contexts** (organizational contexts) are automatically included in every agent
4. **Agent resources** reference context files directly from the library using `file://` paths
5. **Using agents** is done via `q chat --agent <agent-name>`

### Agent Configuration

Each installed profile becomes an Amazon Q CLI agent with:
- **All tools enabled** (`"tools": ["*"]`)
- **Pre-approved file reading** (`"allowedTools": ["fs_read"]`)
- **Base contexts** automatically included
- **Profile-specific contexts** added as resources
- **Proper schema validation**

## 🌍 Base Contexts

Base contexts are automatically applied to all agents and provide organization-wide knowledge:

- **Organizational Policies** - Company-wide policies and standards
- **Common Guidelines** - Shared development practices and conventions
- **Security Best Practices** - Security guidelines for all projects

These contexts are automatically included when installing any profile, ensuring consistent organizational knowledge across all agents.

## 📚 Available Profiles

### Role-Based Profiles
- **developer-v1** - Complete profile for software developers with development guidelines and best practices
- **solutions-architect-v1** - Complete profile for solutions architects with AWS best practices and architecture patterns
- **engagement-manager-v1** - Complete profile for engagement managers with client communication and project delivery contexts

### Task-Based Profiles
- **document-helper-v1** - Profile for document writers with guidelines for creating and editing documents effectively
- **system-administrator-v1** - Profile for system administrators with infrastructure and operations contexts

### Meta Profiles
- **documentation-v1** - Complete documentation profile for AI Configurator itself with installation guides and development docs

## 🏗️ Project Structure

```
ai-configurator/
├── ai_configurator/               # Main package
│   ├── core/                      # Core functionality
│   │   ├── config_library_manager.py  # Library management in config dir
│   │   ├── agent_installer.py     # Agent installation
│   │   ├── file_utils.py          # File utilities
│   │   └── catalog_schema.py      # Data models
│   └── cli.py                     # Command-line interface
├── library/                       # Configuration profiles
│   ├── base-contexts/             # Base contexts (applied to all agents)
│   ├── developer/                 # Developer profile
│   ├── solutions-architect/       # Solutions architect profile
│   └── documentation/             # Documentation profile
├── scripts/                       # Utility scripts
│   └── cleanup_old_amazonq.py     # Cleanup old Amazon Q config
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

1. **Library Installation**: First use copies the entire library to `~/.config/ai-configurator/library/`
2. **Agent Creation**: Installing a profile creates a JSON agent configuration in `~/.aws/amazonq/cli-agents/`
3. **Resource References**: Agent resources point directly to library files using `file://` paths
4. **Base Context Inclusion**: All agents automatically include base contexts for organizational consistency
5. **Amazon Q Integration**: Use agents with `q chat --agent <name>` command

## 🔄 Migration from Old System

If you were using the old context-based system:

1. **Clean up old configuration**:
   ```bash
   python scripts/cleanup_old_amazonq.py
   ```

2. **Reinstall profiles as agents**:
   ```bash
   ai-config list
   ai-config install <profile-id>
   ```

3. **Use new agent syntax**:
   ```bash
   q chat --agent <profile-id>
   ```

## 📖 Documentation

For comprehensive documentation, install the documentation profile:

```bash
ai-config install documentation-v1
q chat --agent documentation-v1
```

This provides detailed guides for:
- Installation and setup
- Agent configuration
- Profile creation
- Development setup
- Migration from old system

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- [GitHub Issues](https://github.com/your-org/ai-configurator/issues)
- [Documentation Agent](ai-config install documentation-v1)
- [Discussions](https://github.com/your-org/ai-configurator/discussions)

---

**Status**: ✅ Agent-Based Architecture Implemented

**Migration**: Successfully migrated from context-based to agent-based architecture aligned with Amazon Q Developer CLI v2+.
