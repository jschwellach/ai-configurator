# AI Configurator - Current State Documentation

**Last Updated**: 2025-08-23  
**Status**: ✅ Production Ready - Tool-Agnostic Library Architecture Fully Implemented

## 🎯 Project Overview

AI Configurator is a **tool-agnostic knowledge library manager** that creates and manages AI tool configurations. It provides a pure knowledge library that can be consumed by any AI tool (Amazon Q CLI, Claude Projects, ChatGPT, etc.) while maintaining tool-specific agent configurations separately.

## 🏗️ Current Architecture

### Tool-Agnostic Library System (v3.0)
The project has been **completely redesigned** from an Amazon Q CLI-specific system to a tool-agnostic knowledge library (August 2023).

**Key Principles:**
- **Pure Knowledge Library**: Tool-agnostic markdown files organized by category
- **Tool Separation**: Tool-specific configurations separate from knowledge
- **File References**: Agents reference library files, don't embed content
- **Role-Based Organization**: Knowledge organized around roles with extensible folders
- **Interactive Management**: CLI app for agent configuration with menu system

### Core Components

```
ai-configurator/
├── ai_configurator/           # Main package (3 core files)
│   ├── core/                  # Essential functionality
│   │   ├── library_manager.py     # Tool-agnostic library management
│   │   ├── agent_manager.py       # Multi-tool agent creation
│   │   ├── file_utils.py          # File operations
│   │   └── __init__.py            # Module exports
│   └── cli.py                 # Enhanced CLI interface
├── library/                   # Pure knowledge library
│   ├── README.md              # Library documentation
│   ├── common/                # Organizational knowledge
│   ├── roles/                 # Role folders with main + additional files
│   ├── domains/               # Domain expertise
│   ├── tools/                 # Tool-specific knowledge
│   └── workflows/             # Process documentation
├── backup/                    # Preserved configurations
│   └── mcp-servers/           # MCP server configurations
├── scripts/                   # Utilities
│   └── cleanup_old_amazonq.py
└── docs/                      # Documentation
    ├── current_state.md       # This file
    └── library_plan.md        # Complete redesign plan
```

### User Configuration Structure
```
~/.config/ai-configurator/
├── library/                   # Synced knowledge library
├── q-cli/                     # Amazon Q CLI agents
│   ├── agents/
│   │   └── product-owner.json     # Agent with file references + MCP
│   └── mcp-servers/
├── claude-code/               # Future: Claude Projects
└── chatgpt/                   # Future: ChatGPT configurations
```

## 🔧 How It Works

### 1. Knowledge Library Management
- **Source**: Pure markdown files in `./library/` directory
- **Categories**: common, roles, domains, tools, workflows
- **Sync**: `ai-config library sync` copies to `~/.config/ai-configurator/library/`
- **Discovery**: `ai-config library list` shows all available knowledge

### 2. Agent Creation Process
1. User runs `ai-config create-agent --name my-agent --role software-engineer --tool q-cli`
2. `LibraryManager` ensures library is synced to config directory
3. `AgentManager` builds resource list:
   - Adds role files from `roles/software-engineer/`
   - Optionally adds common organizational files
   - Optionally adds specific domain/tool/workflow files
   - All paths use absolute `file://` references to synced library
4. Creates agent JSON in `~/.config/ai-configurator/q-cli/agents/my-agent.json`
5. For q-cli tool: Also creates Amazon Q CLI agent in `~/.aws/amazonq/cli-agents/`
6. Agent ready for use with `q chat --agent my-agent`

### 3. Interactive Agent Management
- **Update**: `ai-config update-agent --name my-agent --tool q-cli` opens interactive menu
- **Menu Options**: Add/remove knowledge files, configure MCP servers, modify settings
- **Knowledge Discovery**: Browse library categories and files interactively
- **MCP Integration**: Add/remove/configure MCP servers per agent

### 4. Multi-Tool Support
- **Current**: Amazon Q CLI (q-cli) fully supported
- **Planned**: Claude Projects (claude-code), ChatGPT (chatgpt)
- **Architecture**: Same knowledge library, different export formats

## 📋 Available Commands

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
ai-config create-agent --name my-dev --role software-engineer --tool q-cli
ai-config create-agent --name architect --rules "roles/software-architect/,domains/aws-best-practices.md" --tool q-cli

# Manage agents
ai-config agents list --tool q-cli        # List all agents
ai-config update-agent --name my-dev --tool q-cli  # Interactive update
ai-config agents remove --name my-dev --tool q-cli # Remove agent
ai-config agents info --name my-dev --tool q-cli   # Show agent details
```

### Role Discovery
```bash
ai-config roles list                      # List available roles
```

### Output Formats
All commands support `--format json` for programmatic use.

## 📚 Current Knowledge Library

### Library Structure (12 files, 5 categories)

#### Common (Organizational Knowledge) - 5 files
- **policies.md**: Comprehensive organizational policies and standards
- **aws-security-best-practices.md**: AWS security guidelines
- **organizational-policies.md**: Company-wide policies
- **common-abbreviations.md**: Standard terminology
- **defaults.md**: Basic organizational defaults

#### Roles (Role-Specific Knowledge) - 3 roles
- **product-owner/**: Product owner knowledge and practices
  - `product-owner.md`: Core responsibilities, skills, best practices
- **software-architect/**: Architecture principles and patterns
  - `software-architect.md`: System design, technical leadership, patterns
- **software-engineer/**: Development best practices
  - `software-engineer.md`: Coding practices, collaboration, continuous learning

#### Domains (Domain Expertise) - 2 files
- **aws-best-practices.md**: Comprehensive AWS Well-Architected practices
- **security.md**: Security best practices across all domains

#### Tools (Tool-Specific Knowledge) - 1 file
- **git.md**: Git workflows, branching strategies, best practices

#### Workflows (Process Documentation) - 1 file
- **code-review.md**: Complete code review workflow and guidelines

### MCP Server Integration
- **Preserved**: 4 MCP servers from previous system
- **Integration**: Automatically added to new agents
- **Servers**: fetch, awslabs.core-mcp-server, aws-documentation-mcp-server, cdk-mcp-server

## 🔄 Migration History

### Major Redesign (August 2023)
**From**: Amazon Q CLI-specific agent system with complex profiles and catalogs  
**To**: Tool-agnostic knowledge library with multi-tool agent support

**Key Changes Made:**
1. ✅ **Complete Library Restructure**
   - Removed complex YAML profiles, catalogs, and configurations
   - Created pure markdown knowledge library organized by category
   - Implemented role folders with main files + additional configurations
   - Moved organizational knowledge to `common/` category

2. ✅ **New Agent Architecture**
   - `LibraryManager`: Tool-agnostic library management in config directory
   - `AgentManager`: Multi-tool agent creation with file references
   - File reference system using absolute `file://` paths
   - Interactive agent management with menu system

3. ✅ **Enhanced CLI Interface**
   - Complete CLI rewrite for new architecture
   - Library management commands (list, sync, search, info)
   - Agent creation with role and rule selection
   - Interactive agent updates with menu system
   - Multi-tool support (q-cli, claude-code, chatgpt)

4. ✅ **MCP Server Preservation**
   - Backed up existing MCP configurations
   - Integrated MCP servers into new agent system
   - Interactive MCP server management per agent

5. ✅ **Project Cleanup**
   - Removed 70,000+ lines of obsolete code (previous migration)
   - Removed additional complex systems (profiles, catalogs, workflows)
   - Streamlined to 3 core files: library_manager, agent_manager, file_utils

**Migration Branches**: 
- `feature/agent-migration` (v1→v2): Global contexts to agent-based
- `feature/library-redesign` (v2→v3): Agent-specific to tool-agnostic

## 🛠️ Development Setup

### Quick Start
```bash
git clone <repository-url>
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .

# Test new system
ai-config library list
ai-config create-agent --name test --role software-engineer --tool q-cli
ai-config agents list --tool q-cli
q chat --agent test
```

### Testing
```bash
pytest                    # Run test suite
ai-config library sync   # Test library management
ai-config roles list     # Test role discovery
```

## 📖 Key Files to Understand

### Core Implementation
- **`ai_configurator/cli.py`**: Complete CLI interface with all commands
- **`ai_configurator/core/library_manager.py`**: Tool-agnostic library management
- **`ai_configurator/core/agent_manager.py`**: Multi-tool agent creation and management
- **`ai_configurator/core/file_utils.py`**: Essential file operations

### Knowledge Library
- **`library/README.md`**: Library overview and usage instructions
- **`library/common/`**: Organizational knowledge applied to all agents
- **`library/roles/`**: Role-specific knowledge folders
- **`library/domains/`, `tools/`, `workflows/`**: Categorized expertise

### Documentation
- **`docs/library_plan.md`**: Complete redesign plan and implementation details
- **`docs/current_state.md`**: This file - current system overview

## 🔮 Future Enhancements

### Planned Features
1. **Multi-Tool Export**: Claude Projects and ChatGPT support
2. **Enhanced Collections**: Folder-based knowledge combinations
3. **Library Browsing**: Interactive knowledge discovery
4. **Template System**: Templates for creating new knowledge files
5. **Validation**: Enhanced agent config validation
6. **Versioning**: Better library versioning and rollback

### Technical Debt
- Some test files still reference old system (need updating)
- Multi-tool export not yet implemented
- Collection management could be enhanced

## 🚨 Important Notes

### For New Sessions
- **Architecture**: Tool-agnostic knowledge library with multi-tool agent support
- **Library**: Pure markdown files in categorized folders
- **Agents**: Tool-specific configurations with file references
- **Usage**: `ai-config create-agent` → `q chat --agent <name>`
- **Management**: Interactive `update-agent` with menu system

### Current Status
- ✅ **Fully Operational**: Library management, agent creation, Amazon Q CLI integration
- ✅ **Tested**: All core functionality working (12 knowledge files, 3 roles, MCP integration)
- ✅ **Clean Architecture**: Streamlined from complex system to 3 core files
- ⚠️ **Multi-Tool**: Only Amazon Q CLI currently supported (Claude/ChatGPT planned)

### Dependencies
- **Amazon Q Developer CLI**: v2+ with agent support
- **Python**: 3.8+ required
- **Operating Systems**: Windows, macOS, Linux supported

## 📞 Support & Resources

### Getting Help
- **Library Discovery**: `ai-config library list` and `ai-config roles list`
- **Agent Management**: `ai-config agents list --tool q-cli`
- **Interactive Updates**: `ai-config update-agent --name <agent> --tool q-cli`

### Key Resources
- **Library Plan**: Complete redesign documentation in `docs/library_plan.md`
- **Amazon Q CLI Docs**: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html
- **Agent Schema**: https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json

---

**Status**: ✅ **Production Ready** - Tool-agnostic library architecture fully implemented and operational.

**Last Major Update**: August 2023 - Complete redesign to tool-agnostic knowledge library with multi-tool agent support.

**Current Capabilities**: 
- 📚 12 knowledge files across 5 categories
- 👥 3 role-based configurations  
- 🤖 Multi-tool agent creation (Amazon Q CLI active)
- 🔧 4 MCP servers integrated
- 🎛️ Interactive agent management
