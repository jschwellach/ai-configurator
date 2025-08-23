# AI Configurator - Current State Documentation

**Last Updated**: 2025-08-23  
**Status**: ✅ Production Ready - Agent-Based Architecture Fully Implemented

## 🎯 Project Overview

AI Configurator is a cross-platform configuration manager for Amazon Q CLI agents. It simplifies the setup and sharing of Amazon Q CLI agent configurations across teams and environments by creating Amazon Q CLI agents instead of managing context files directly.

## 🏗️ Current Architecture

### Agent-Based System (v2.0)
The project has been **completely migrated** from a global context system to Amazon Q Developer CLI's agent-based architecture (August 2023).

**Key Principles:**
- **No Global Contexts**: All context is agent-specific through `resources` field
- **Config Directory**: Library installed to `~/.config/ai-configurator/library/`
- **Direct References**: Agent resources use `file://` paths to library files
- **Base Contexts**: Organizational contexts automatically included in all agents
- **Schema Compliance**: Agent configs match official Amazon Q CLI format

### Core Components

```
ai-configurator/
├── ai_configurator/           # Main package (5 core files only)
│   ├── core/                  # Essential functionality
│   │   ├── agent_installer.py      # Creates Amazon Q CLI agents
│   │   ├── config_library_manager.py  # Manages ~/.config library
│   │   ├── catalog_schema.py       # Agent-based data models
│   │   ├── file_utils.py          # Essential file operations
│   │   └── __init__.py            # Clean module exports
│   └── cli.py                 # Agent-focused CLI interface
├── library/                   # Configuration profiles
│   ├── base-contexts/         # Organizational contexts (auto-included)
│   ├── catalog.json          # Profile and base context definitions
│   └── [profile-dirs]/       # Individual agent profiles
├── scripts/                   # Utilities
│   └── cleanup_old_amazonq.py    # Migration cleanup tool
├── templates/                 # Profile creation templates
└── docs/                      # Documentation
    ├── agentic_plan.md       # Complete migration record
    └── current_state.md      # This file
```

## 🔧 How It Works

### 1. Library Management
- **Source**: Profiles stored in `./library/` directory
- **Installation**: First use copies entire library to `~/.config/ai-configurator/library/`
- **Updates**: `ai-config refresh` re-copies from source

### 2. Agent Creation Process
1. User runs `ai-config install <profile-id>`
2. `ConfigLibraryManager` ensures library is installed in config directory
3. `AgentInstaller` reads profile YAML and builds resource list:
   - Adds all base contexts first (organizational contexts)
   - Adds profile-specific contexts from `contexts/` subdirectory
   - All paths use absolute `file://` references to config library
4. Creates JSON agent config in `~/.aws/amazonq/cli-agents/<profile-id>.json`
5. Agent is ready for use with `q chat --agent <profile-id>`

### 3. Base Contexts (Organizational Contexts)
Base contexts are automatically included in **every** agent and provide organization-wide knowledge:
- **Location**: `library/base-contexts/`
- **Purpose**: Company policies, security guidelines, common standards
- **Implementation**: Added to every agent's `resources` array during installation
- **Priority**: Loaded first (highest priority in catalog)

## 📋 Available Commands

### Core Commands
```bash
ai-config list [--query QUERY]           # List available profiles
ai-config install PROFILE_ID             # Install profile as Amazon Q CLI agent
ai-config remove PROFILE_ID              # Remove installed agent
ai-config info PROFILE_ID                # Show profile details
ai-config agents                         # List installed Amazon Q CLI agents
ai-config refresh                        # Refresh library from source
```

### Output Formats
All commands support `--format json` for programmatic use.

## 📚 Current Profiles

### Available Profiles (as of 2025-08-23)
- **developer-v1**: Software developers with development guidelines
- **solutions-architect-v1**: AWS best practices and architecture patterns
- **engagement-manager-v1**: Client communication and project delivery
- **document-helper-v1**: Document creation and editing guidelines
- **system-administrator-v1**: Infrastructure and operations contexts
- **documentation-v1**: AI Configurator documentation and guides
- **daily-assistant-v1**: General daily assistant profile
- **research-assistant-v1**: Research methodology and citation standards

### Base Contexts (Applied to All Agents)
- **defaults.md**: Basic organizational defaults
- **aws-security-best-practices.md**: AWS security guidelines
- **organizational-policies.md**: Company-wide policies
- **common-abbreviations.md**: Standard terminology

## 🔄 Migration History

### Major Migration (August 2023)
**From**: Global context system with `~/.aws/amazonq/contexts/` and `global_context.json`  
**To**: Agent-based system with `~/.aws/amazonq/cli-agents/` JSON configs

**Key Changes Made:**
1. ✅ **Removed Global Context Support**
   - Deleted `install_global_contexts()` and `remove_global_contexts()` methods
   - Updated catalog schema: `global_contexts` → `base_contexts`
   - Renamed `library/global-contexts/` → `library/base-contexts/`

2. ✅ **Updated Agent Configuration**
   - `AgentConfig` schema matches official Amazon Q CLI format
   - Removed deprecated fields (`useLegacyMcpJson`)
   - Added proper MCP server configuration support
   - Default tools: `["*"]` with `fs_read` pre-approved

3. ✅ **Restructured Installation Process**
   - No more context file copying to Amazon Q directories
   - Direct file references using `file://` paths
   - Library installed to `~/.config/ai-configurator/library/`

4. ✅ **Updated CLI Interface**
   - Replaced `LibraryManager`/`ProfileInstaller` with `ConfigLibraryManager`/`AgentInstaller`
   - Added `agents` and `refresh` commands
   - Updated messaging for agent-based workflow

5. ✅ **Project Cleanup**
   - Removed 70,000+ lines of obsolete code
   - Deleted 15+ backup directories and old files
   - Streamlined from 37+ modules to 5 core files

**Migration Branch**: `feature/agent-migration` (merged to main)  
**Documentation**: Complete plan in `docs/agentic_plan.md`

## 🛠️ Development Setup

### Quick Start
```bash
git clone <repository-url>
cd ai-configurator
pip install -r requirements-dev.txt
pip install -e .

# Test installation
ai-config list
ai-config install documentation-v1
q chat --agent documentation-v1
```

### Testing
```bash
pytest                    # Run test suite
ai-config list           # Test CLI functionality
```

## 📖 Key Files to Understand

### Core Implementation
- **`ai_configurator/cli.py`**: Main CLI interface, all user commands
- **`ai_configurator/core/agent_installer.py`**: Creates Amazon Q CLI agents
- **`ai_configurator/core/config_library_manager.py`**: Manages library installation
- **`ai_configurator/core/catalog_schema.py`**: Data models (AgentConfig, BaseContext, etc.)

### Configuration
- **`library/catalog.json`**: Defines all profiles and base contexts
- **`library/base-contexts/`**: Organizational contexts applied to all agents
- **`library/[profile]/profile.yaml`**: Individual profile configurations

### Documentation
- **`docs/agentic_plan.md`**: Complete migration plan and implementation details
- **`README.md`**: User-facing documentation and quick start guide
- **`templates/`**: Templates for creating new profiles

## 🔮 Future Enhancements

### Planned Features
1. **MCP Server Support**: Add MCP server configuration to profiles
2. **Agent Inheritance**: Allow agents to extend other agents
3. **Profile Versioning**: Better version management system
4. **Validation**: Enhanced agent config validation against Amazon Q CLI schema

### Technical Debt
- Some test files still reference old system (need updating)
- MCP server integration not yet implemented
- Profile creation workflow could be streamlined

## 🚨 Important Notes

### For New Sessions
- **Architecture**: Agent-based system, no global contexts
- **Installation**: Profiles become Amazon Q CLI agents in `~/.aws/amazonq/cli-agents/`
- **Library**: Managed in `~/.config/ai-configurator/library/`
- **Base Contexts**: Automatically included in all agents
- **Usage**: `q chat --agent <profile-id>` to use installed agents

### Migration Status
- ✅ **Complete**: All functionality migrated and tested
- ✅ **Clean**: Project cleaned of obsolete files
- ✅ **Production Ready**: Fully operational on main branch
- ⚠️ **Old Configs**: Users may need to run cleanup script for old installations

### Dependencies
- **Amazon Q Developer CLI**: Must support agent-based architecture (v2+)
- **Python**: 3.8+ required
- **Operating Systems**: Windows, macOS, Linux supported

## 📞 Support & Resources

### Getting Help
- **Documentation Agent**: `ai-config install documentation-v1`
- **Migration Issues**: Use `scripts/cleanup_old_amazonq.py`
- **Development**: See `CONTRIBUTING.md`

### Key Resources
- **Official Amazon Q CLI Docs**: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html
- **Agent Schema**: https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json
- **Context Management**: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-context.html

---

**Status**: ✅ **Production Ready** - Agent-based architecture fully implemented and operational.

**Last Major Update**: August 2023 - Complete migration to agent-based system aligned with Amazon Q Developer CLI v2+.
