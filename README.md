# AI Configurator

**Tool-agnostic knowledge library manager for AI tools and systems.**

## 🎯 Purpose

AI Configurator provides a pure knowledge library that can be consumed by any AI tool (Amazon Q CLI, Claude Projects, ChatGPT, etc.) while maintaining tool-specific agent configurations separately. Whether you're setting up agents for development teams, standardizing knowledge across tools, or sharing expertise across organizations, AI Configurator makes it seamless.

## ✨ Features

- **Tool-Agnostic Library**: Pure markdown knowledge that works with any AI tool
- **Role-Based Organization**: Knowledge organized around roles with extensible folders
- **Multi-Tool Agent Support**: Create agents for Amazon Q CLI, Claude Projects, ChatGPT (planned)
- **Interactive Management**: CLI app for agent configuration with menu system
- **File References**: Agents reference library files without content duplication
- **MCP Integration**: Preserved MCP server configurations with per-agent management
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Knowledge Discovery**: Search and browse library content interactively

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
# Sync knowledge library
ai-config library sync

# List available knowledge
ai-config library list

# Discover roles
ai-config roles list

# Create an agent
ai-config create-agent --name my-dev --role software-engineer --include-common --tool q-cli

# Use the agent (Amazon Q CLI)
q chat --agent my-dev

# Manage agents
ai-config agents list --tool q-cli
ai-config update-agent --name my-dev --tool q-cli  # Interactive menu
```

## 📋 Commands

### Library Management
```bash
ai-config library list                    # List all knowledge files
ai-config library sync                    # Sync library from source
ai-config library info                    # Show library information
ai-config library search "aws security"   # Search library content
```

### Agent Creation & Management
```bash
# Create agents
ai-config create-agent --name NAME --role ROLE --tool TOOL
ai-config create-agent --name architect --rules "roles/software-architect/,domains/aws-best-practices.md" --tool q-cli

# Manage agents
ai-config agents list --tool TOOL         # List all agents
ai-config update-agent --name NAME --tool TOOL  # Interactive update menu
ai-config agents remove --name NAME --tool TOOL # Remove agent
ai-config agents info --name NAME --tool TOOL   # Show agent details
```

### Role Discovery
```bash
ai-config roles list                      # List available roles
```

All commands support `--format json` for programmatic use.

## 🏗️ Architecture

### Tool-Agnostic Knowledge Library
```
library/
├── README.md              # Library documentation
├── common/                # Organizational knowledge (5 files)
│   ├── policies.md
│   ├── aws-security-best-practices.md
│   └── ...
├── roles/                 # Role-specific knowledge (3 roles)
│   ├── product-owner/
│   │   └── product-owner.md
│   ├── software-architect/
│   │   └── software-architect.md
│   └── software-engineer/
│       └── software-engineer.md
├── domains/               # Domain expertise (2 files)
│   ├── aws-best-practices.md
│   └── security.md
├── tools/                 # Tool-specific knowledge (1 file)
│   └── git.md
└── workflows/             # Process documentation (1 file)
    └── code-review.md
```

### User Configuration
```
~/.config/ai-configurator/
├── library/               # Synced knowledge library
├── q-cli/                 # Amazon Q CLI agents
│   ├── agents/
│   │   └── my-dev.json        # Agent with file references + MCP
│   └── mcp-servers/
├── claude-code/           # Future: Claude Projects
└── chatgpt/               # Future: ChatGPT configurations
```

### How It Works

1. **Knowledge Library**: Pure markdown files organized by category
2. **Agent Creation**: Combines knowledge files with tool-specific configuration
3. **File References**: Agents reference library files using `file://` paths
4. **Multi-Tool Support**: Same knowledge, different export formats
5. **Interactive Management**: Menu-driven agent configuration

## 🤖 Available Knowledge

### Current Library (12 files, 5 categories)

#### Roles (3 available)
- **product-owner**: Product management, stakeholder communication, roadmap planning
- **software-architect**: System design, technical leadership, architecture patterns
- **software-engineer**: Development practices, code quality, collaboration

#### Common (Organizational Knowledge)
- Comprehensive organizational policies and standards
- AWS security guidelines and best practices
- Company-wide policies and procedures
- Standard terminology and abbreviations

#### Domains (Expertise Areas)
- **AWS**: Well-Architected Framework, service best practices, cost optimization
- **Security**: Application security, infrastructure security, compliance

#### Tools (Tool-Specific Knowledge)
- **Git**: Workflows, branching strategies, collaboration best practices

#### Workflows (Process Documentation)
- **Code Review**: Complete workflow, guidelines, and best practices

### MCP Server Integration
- **4 MCP servers** preserved from previous system
- **Automatic integration** into new agents
- **Per-agent configuration** through interactive menu
- **Servers**: fetch, awslabs.core-mcp-server, aws-documentation-mcp-server, cdk-mcp-server

## 🛠️ Multi-Tool Support

### Currently Supported
- **Amazon Q CLI (q-cli)**: Full support with agent creation and MCP integration

### Planned Support
- **Claude Projects (claude-code)**: Export knowledge for Claude Projects
- **ChatGPT (chatgpt)**: Export as custom instructions

### Creating Agents for Different Tools
```bash
# Amazon Q CLI (current)
ai-config create-agent --name my-dev --role software-engineer --tool q-cli
q chat --agent my-dev

# Claude Projects (planned)
ai-config create-agent --name my-dev --role software-engineer --tool claude-code

# ChatGPT (planned)
ai-config create-agent --name my-dev --role software-engineer --tool chatgpt
```

## 📚 Usage Examples

### Create a Product Owner Agent
```bash
# Create with role and common knowledge
ai-config create-agent --name product-owner --role product-owner --include-common --tool q-cli

# Use with Amazon Q CLI
q chat --agent product-owner
```

### Create a Custom Developer Agent
```bash
# Create with specific knowledge files
ai-config create-agent \
  --name full-stack-dev \
  --rules "roles/software-engineer/,domains/aws-best-practices.md,tools/git.md,workflows/code-review.md" \
  --tool q-cli \
  --description "Full-stack developer with AWS and Git expertise"

# Update interactively
ai-config update-agent --name full-stack-dev --tool q-cli
```

### Interactive Agent Management
```bash
ai-config update-agent --name my-agent --tool q-cli

# Opens interactive menu:
# 1. Add/Remove Knowledge Files
# 2. Configure MCP Servers
# 3. Modify Agent Settings
# 4. Save and Exit
```

### Knowledge Discovery
```bash
# Browse all knowledge
ai-config library list

# Search for specific topics
ai-config library search "security"
ai-config library search "aws lambda"

# Explore roles
ai-config roles list
```

## 🔧 Development

### Quick Development Setup
```bash
git clone <repository-url>
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .

# Test the system
ai-config library sync
ai-config create-agent --name test --role software-engineer --tool q-cli
ai-config agents list --tool q-cli
```

### Adding New Knowledge
1. **Add markdown files** to appropriate library categories
2. **Sync library**: `ai-config library sync`
3. **Create agents** using new knowledge
4. **Test with AI tools**

### Project Structure
```
ai-configurator/
├── ai_configurator/           # Main package (6 files)
│   ├── core/                  # Core functionality
│   │   ├── library_manager.py     # Library management
│   │   ├── agent_manager.py       # Agent creation
│   │   └── file_utils.py          # File operations
│   └── cli.py                 # CLI interface
├── library/                   # Knowledge library
├── backup/                    # Preserved configurations
├── scripts/                   # Utility scripts
└── docs/                      # Documentation
```

## 🔄 Migration from Previous Versions

### From v2.0 (Agent-Based)
The system has been completely redesigned for tool-agnostic use. Previous Amazon Q CLI agents will need to be recreated:

```bash
# Clean up old configuration (optional)
python scripts/cleanup_old_amazonq.py

# Recreate agents with new system
ai-config create-agent --name my-agent --role software-engineer --tool q-cli
```

### Key Changes
- **Library**: Pure markdown files instead of YAML profiles
- **Agents**: File references instead of content copying
- **Multi-Tool**: Support for multiple AI tools, not just Amazon Q CLI
- **Interactive**: Menu-driven agent management

## 📖 Documentation

### Complete Documentation
- **Library Plan**: `docs/library_plan.md` - Complete redesign documentation
- **Current State**: `docs/current_state.md` - System overview and architecture
- **Development**: `CONTRIBUTING.md` - Development guidelines

### Getting Help
```bash
# Library discovery
ai-config library list
ai-config roles list

# Agent management
ai-config agents list --tool q-cli
ai-config update-agent --name <agent> --tool q-cli

# Search functionality
ai-config library search "topic"
```

## 🤝 Contributing

We welcome contributions! The tool-agnostic architecture makes it easy to:
- **Add knowledge**: Create markdown files in library categories
- **Add tools**: Implement new tool exporters
- **Improve CLI**: Enhance the interactive experience

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **GitHub Issues**: Report bugs and request features
- **Library Search**: `ai-config library search "topic"`
- **Interactive Help**: `ai-config update-agent --name <agent> --tool q-cli`

---

**Status**: ✅ **Production Ready** - Tool-agnostic library architecture fully implemented

**Current Version**: v3.0 - Multi-tool knowledge library manager

**Capabilities**: 
- 📚 12 knowledge files across 5 categories
- 👥 3 role-based configurations  
- 🤖 Multi-tool agent creation (Amazon Q CLI active)
- 🔧 4 MCP servers integrated
- 🎛️ Interactive agent management
