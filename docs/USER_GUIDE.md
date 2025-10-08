# AI Configurator User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Library Management](#library-management)
3. [Agent Creation & Management](#agent-creation--management)
4. [Local File Integration](#local-file-integration)
5. [MCP Server Management](#mcp-server-management)
6. [Interactive Wizards](#interactive-wizards)
7. [Templates](#templates)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Install AI Configurator**
   ```bash
   pip install ai-configurator
   ```

2. **Run Quick Start Wizard**
   ```bash
   ai-config wizard quick-start
   ```
   This will guide you through:
   - Creating your first agent
   - Setting up MCP servers (optional)
   - Exporting to Q CLI for immediate use

3. **Check System Status**
   ```bash
   ai-config status
   ```

### Understanding the System

AI Configurator manages:
- **Base Library**: Shared knowledge files (read-only)
- **Personal Library**: Your customizations and overrides
- **Agents**: AI agent configurations for different tools
- **MCP Servers**: Tool integrations and capabilities
- **Templates**: Pre-built agent configurations

## Library Management

### Checking Library Status

```bash
# View overall system status
ai-config status

# Detailed library sync status
ai-config library status
```

### Synchronizing Libraries

The library sync system keeps your personal customizations while updating shared knowledge:

```bash
# Check what would be synced (safe preview)
ai-config library sync --dry-run

# Perform actual sync with conflict resolution
ai-config library sync

# View differences between base and personal libraries
ai-config library diff

# Quick update (accepts all changes)
ai-config library update --force
```

### Handling Conflicts

When both base and personal libraries have changes to the same file:

1. **Automatic Detection**: Conflicts are detected and displayed clearly
2. **Interactive Resolution**: Choose how to resolve each conflict:
   - **Keep Local**: Keep your personal version
   - **Accept Remote**: Use the updated base version
   - **Manual Merge**: Open in editor for manual resolution
3. **Backup Protection**: Automatic backup before any changes

Example conflict resolution:
```
⚠️  Found 2 conflicts:

📄 Diff for roles/software-engineer/software-engineer.md:
--- base/roles/software-engineer/software-engineer.md
+++ personal/roles/software-engineer/software-engineer.md
@@ -10,7 +10,7 @@
 ## Responsibilities
 
-You are responsible for implementing software solutions.
+You are responsible for implementing and testing software solutions.

Resolution options:
1. Keep local (personal) version
2. Accept remote (base) version  
3. Manual merge (open editor)

Choose resolution (1-3): 1
```

## Agent Creation & Management

### Creating Agents

#### Method 1: Interactive Wizard (Recommended)
```bash
ai-config wizard create-agent
```
Guides you through:
- Agent name and description
- Tool type selection (Q CLI, Claude, etc.)
- Template selection (optional)
- Resource selection from library

#### Method 2: Direct Creation
```bash
ai-config create-agent --name my-agent --tool q-cli --description "My custom agent"
```

### Managing Existing Agents

```bash
# List all agents
ai-config list-agents

# View agent details
ai-config show-agent my-agent

# Interactive management (add/remove resources, MCP servers)
ai-config manage-agent my-agent

# Export agent for use with Q CLI
ai-config export-agent my-agent --save
```

### Agent Configuration

Agents consist of:
- **Name & Description**: Basic identification
- **Tool Type**: Target AI tool (Q CLI, Claude, etc.)
- **Resources**: Knowledge files from library or local files
- **MCP Servers**: Tool integrations and capabilities

## Local File Integration

### Adding Project Files to Agents

Include files from your current project in agent configurations:

```bash
# Scan for files (preview without adding)
ai-config files scan-files my-agent --pattern "**/*.md" --base-path .

# Add files using glob patterns
ai-config files add-files my-agent --pattern "./docs/**/*.md"
ai-config files add-files my-agent --pattern "./rules/*.txt"

# Add files from specific directory
ai-config files add-files my-agent --pattern "**/*.py" --base-path ./src
```

### File Patterns

Supported glob patterns:
- `**/*.md` - All markdown files recursively
- `./docs/**/*.md` - Markdown files in docs directory
- `*.txt` - Text files in current directory
- `rules/**/*` - All files in rules directory

### File Watching (Advanced)

Enable automatic updates when local files change:

```bash
# Enable file watching for an agent
ai-config files watch-files my-agent --enable --pattern "**/*.md"

# Check watching status
ai-config files watch-files my-agent --status

# Disable watching
ai-config files watch-files my-agent --disable
```

## MCP Server Management

### Discovering Servers

```bash
# Browse all available servers
ai-config mcp browse

# Browse by category
ai-config mcp browse --category development

# Search for specific servers
ai-config mcp search git
ai-config mcp search "file system"
ai-config mcp search database
```

### Installing Servers

```bash
# Install a server
ai-config mcp install filesystem

# Install with confirmation
ai-config mcp install git --dry-run  # Preview first
ai-config mcp install git            # Actually install

# Check installation status
ai-config mcp status --installed
```

### Managing Server Registry

```bash
# Check registry status
ai-config mcp status

# Create sample servers for testing
ai-config mcp create-sample

# Sync with remote registry (when available)
ai-config mcp sync
```

### Available Server Categories

- **System**: File system, process management
- **Development**: Git, code analysis, build tools
- **Data**: Databases, APIs, data processing
- **Communication**: Slack, email, notifications

## Interactive Wizards

### Quick Start Wizard

Perfect for new users:
```bash
ai-config wizard quick-start
```

Walks through:
1. Creating your first agent
2. Selecting knowledge resources
3. Setting up MCP servers (optional)
4. Exporting to Q CLI

### Agent Creation Wizard

Detailed agent setup:
```bash
ai-config wizard create-agent
```

Features:
- Template selection from library
- Interactive resource selection
- MCP server configuration
- Validation and testing

### MCP Setup Wizard

Configure MCP servers for existing agents:
```bash
ai-config wizard setup-mcp my-agent
```

Includes:
- Server discovery and browsing
- Installation with dependency checking
- Configuration validation

## Templates

### Using Templates

Templates provide pre-configured agent setups for common roles:

```bash
# Templates are automatically offered during agent creation
ai-config wizard create-agent

# Available templates:
# - Software Engineer: Development tools and practices
# - Software Architect: Architecture and design patterns  
# - System Administrator: Infrastructure and operations
# - Daily Assistant: General productivity
# - Product Owner: Product management
```

### Template Locations

Templates are stored in the library system:
- **Base Templates**: `library/templates/`
- **Personal Templates**: `personal/templates/` (your customizations)

### Creating Custom Templates

1. **Copy Existing Role**:
   ```bash
   cp library/roles/my-role/my-role.md library/templates/my-template-q-cli.md
   ```

2. **Edit Template**: Customize the content for your needs

3. **Use Template**: Available in wizard during agent creation

### Template Naming Convention

Templates follow the pattern: `{name}-{tool}.md`
- `software-engineer-q-cli.md` - Software engineer for Q CLI
- `data-analyst-claude.md` - Data analyst for Claude
- `custom-role-q-cli.md` - Custom role for Q CLI

## Advanced Usage

### Batch Operations

```bash
# Export all agents
for agent in $(ai-config list-agents --names-only); do
  ai-config export-agent $agent --save
done

# Add same files to multiple agents
ai-config files add-files agent1 --pattern "**/*.md"
ai-config files add-files agent2 --pattern "**/*.md"
```

### Configuration Backup

```bash
# Backups are automatic, but you can check status
ai-config status  # Shows backup information

# Manual backup before major changes
ai-config library sync  # Creates backup automatically
```

### Integration with Development Workflow

```bash
# Project-specific agent setup
cd my-project
ai-config wizard create-agent  # Creates agent with project context
ai-config files add-files project-agent --pattern "./docs/**/*.md"
ai-config files add-files project-agent --pattern "./README.md"
ai-config files watch-files project-agent --enable
```

## Best Practices

### Library Management
- **Sync Regularly**: Run `ai-config library sync` to get updates
- **Review Conflicts**: Don't blindly accept all changes
- **Backup Important**: Personal customizations are backed up automatically

### Agent Organization
- **Descriptive Names**: Use clear, descriptive agent names
- **Role-Based**: Create agents for specific roles or projects
- **Resource Selection**: Include only relevant knowledge files

### File Integration
- **Pattern Specificity**: Use specific patterns to avoid including unwanted files
- **Regular Updates**: Use file watching for active projects
- **Documentation Focus**: Prioritize documentation and rule files

### MCP Servers
- **Start Simple**: Begin with basic servers (filesystem, git)
- **Test First**: Use `--dry-run` options when available
- **Category Organization**: Organize servers by functionality

## Troubleshooting

See the [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues and solutions.

---

**Need Help?**
- Run `ai-config --help` for command reference
- Use `ai-config <command> --help` for specific command help
- Check system status with `ai-config status`
- Try the quick start wizard: `ai-config wizard quick-start`
