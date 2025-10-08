# CLI Command Structure Simplification

## Current State Analysis

### Current Command Patterns (Mixed)

The current CLI has inconsistent command patterns:

```bash
# Top-level commands
ai-config status
ai-config create-agent
ai-config list-agents
ai-config manage-agent <name>
ai-config export-agent <name>

# Grouped commands
ai-config library status
ai-config library sync
ai-config library diff
ai-config library update

ai-config files scan-files <agent>
ai-config files add-files <agent>
ai-config files watch-files <agent>

ai-config mcp browse
ai-config mcp search <query>
ai-config mcp install <name>
ai-config mcp status
ai-config mcp create-sample

ai-config wizard create-agent
ai-config wizard setup-mcp <agent>
ai-config wizard quick-start

# Phase 3 commands
ai-config git clone <url>
ai-config git pull
ai-config git push
ai-config git status
ai-config git sync

ai-config sync all
ai-config sync source <name>
ai-config sync status

ai-config cache stats
ai-config cache benchmark
ai-config cache preload
ai-config cache clear

ai-config production show
ai-config production environments
ai-config production validate
ai-config production generate

ai-config monitoring health
ai-config monitoring logs
ai-config monitoring stats
ai-config monitoring setup
```

### Problems with Current Structure

1. **Inconsistent Patterns**: Mix of `verb-noun` and `noun verb` patterns
2. **Redundant Prefixes**: `create-agent`, `list-agents`, `manage-agent`
3. **Unclear Grouping**: Some commands grouped, others not
4. **Wizard Confusion**: Wizard commands duplicate functionality
5. **Discovery Issues**: Hard to find related commands

## New Simplified Structure

### Design Principles

1. **Resource-Based**: Commands organized by resource type
2. **Consistent Pattern**: `ai-config <resource> <action> [arguments] [options]`
3. **Intuitive Grouping**: Related commands together
4. **Clear Hierarchy**: Easy to discover and remember
5. **Backward Compatible**: Old commands work with deprecation warnings

### Command Pattern

```
ai-config <resource> <action> [arguments] [options]
         └─────┬────┘ └───┬───┘ └────┬────┘ └───┬───┘
           Resource    Action    Required    Optional
           (noun)      (verb)    Args        Flags
```

## New Command Structure

### Agent Management

```bash
ai-config agent list                          # List all agents
ai-config agent show <name>                   # Show agent details
ai-config agent create <name> [options]       # Create new agent
ai-config agent edit <name>                   # Edit agent (interactive)
ai-config agent delete <name>                 # Delete agent
ai-config agent export <name> [--tool qcli]   # Export to tool
ai-config agent validate <name>               # Validate configuration
ai-config agent copy <source> <dest>          # Copy agent
```

**Options**:
```bash
--tool <type>        # Tool type (qcli, claude, chatgpt)
--template <name>    # Use template
--interactive        # Interactive mode
--force              # Force operation
```

### Library Management

```bash
ai-config library status                      # Show library status
ai-config library sync [--interactive]        # Sync with conflict resolution
ai-config library diff [file]                 # Show differences
ai-config library update                      # Update from base
ai-config library files <pattern>             # Discover files
ai-config library add <path>                  # Add file to library
ai-config library remove <path>               # Remove file
ai-config library search <query>              # Search library content
```

**Options**:
```bash
--interactive        # Interactive conflict resolution
--dry-run            # Show what would change
--force              # Force overwrite
--pattern <glob>     # File pattern
```

### MCP Server Management

```bash
ai-config mcp list [--agent <name>]           # List servers
ai-config mcp browse [--category <cat>]       # Browse registry
ai-config mcp search <query>                  # Search servers
ai-config mcp show <name>                     # Show server details
ai-config mcp install <name>                  # Install server
ai-config mcp uninstall <name>                # Uninstall server
ai-config mcp add <agent> <server>            # Add server to agent
ai-config mcp remove <agent> <server>         # Remove from agent
ai-config mcp configure <name>                # Configure server
ai-config mcp test <name>                     # Test server
```

**Options**:
```bash
--agent <name>       # Filter by agent
--category <cat>     # Filter by category
--installed          # Show only installed
--available          # Show only available
```

### System Commands (Top-Level)

```bash
ai-config status                              # System overview
ai-config init [--repo <url>]                 # Initialize configuration
ai-config tui                                 # Launch TUI interface
ai-config version                             # Show version
ai-config help [command]                      # Show help
```

### Backup & Restore

```bash
ai-config backup create [--name <name>]       # Create backup
ai-config backup list                         # List backups
ai-config backup restore <id>                 # Restore backup
ai-config backup delete <id>                  # Delete backup
ai-config backup show <id>                    # Show backup details
```

### Configuration Management

```bash
ai-config config show                         # Show configuration
ai-config config set <key> <value>            # Set config value
ai-config config get <key>                    # Get config value
ai-config config reset                        # Reset to defaults
ai-config config validate                     # Validate configuration
```

### Git Operations (Simplified)

```bash
ai-config git status                          # Show Git status
ai-config git sync                            # Pull and push
ai-config git pull                            # Pull updates
ai-config git push                            # Push changes
ai-config git clone <url>                     # Clone repository
```

### Diagnostics & Monitoring

```bash
ai-config health                              # System health check
ai-config logs [--tail <n>]                   # View logs
ai-config stats                               # Show statistics
ai-config debug <command>                     # Run command in debug mode
```

## New Command Structure

All commands follow the pattern: `ai-config <resource> <action> [arguments] [options]`

This is a **breaking change** from v3.x - old commands are removed.

## Implementation Strategy

### Clean Implementation (Week 1)

**Goal**: Replace old CLI with new structure

```python
# ai_configurator/cli_enhanced.py
import click
from click_default_group import DefaultGroup

@click.group(cls=DefaultGroup, default='status')
def cli():
    """AI Configurator v4.0.0"""
    pass

# Agent commands
@cli.group()
def agent():
    """Agent management commands."""
    pass

@agent.command('list')
def agent_list():
    """List all agents."""
    # Implementation

@agent.command('create')
@click.argument('name')
@click.option('--interactive', is_flag=True)
def agent_create(name: str, interactive: bool):
    """Create new agent."""
    # Implementation

# No old commands - clean break
```

### Documentation Update (Week 2)

**Goal**: Update all documentation to use new commands

- README.md
- USER_GUIDE.md
- All examples
- Help text

## Help System Updates

### Improved Help Text

```bash
$ ai-config --help
Usage: ai-config [OPTIONS] COMMAND [ARGS]...

  AI Configurator v4.0.0 - Tool-agnostic knowledge library manager

Commands:
  agent     Agent management commands
  library   Library management commands
  mcp       MCP server management commands
  backup    Backup and restore commands
  config    Configuration management
  git       Git operations
  
  status    Show system status
  init      Initialize configuration
  tui       Launch TUI interface
  health    System health check
  logs      View logs
  stats     Show statistics

Run 'ai-config COMMAND --help' for more information.
```

### Group Help

```bash
$ ai-config agent --help
Usage: ai-config agent [OPTIONS] COMMAND [ARGS]...

  Agent management commands

Commands:
  list       List all agents
  show       Show agent details
  create     Create new agent
  edit       Edit agent configuration
  delete     Delete agent
  export     Export agent to tool
  validate   Validate agent configuration
  copy       Copy agent

Options:
  --help  Show this message and exit.
```

### Command Help

```bash
$ ai-config agent create --help
Usage: ai-config agent create [OPTIONS] NAME

  Create new agent

Arguments:
  NAME  Agent name

Options:
  --tool TEXT        Tool type (qcli, claude, chatgpt)
  --template TEXT    Use template
  --interactive      Interactive mode
  --force            Force operation
  --help             Show this message and exit.

Examples:
  ai-config agent create my-agent
  ai-config agent create my-agent --template software-engineer
  ai-config agent create my-agent --interactive
```

## Shell Completion

### Bash Completion

```bash
# Generate completion script
ai-config --completion bash > ~/.ai-config-completion.bash
source ~/.ai-config-completion.bash

# Add to .bashrc
echo 'source ~/.ai-config-completion.bash' >> ~/.bashrc
```

### Zsh Completion

```bash
# Generate completion script
ai-config --completion zsh > ~/.ai-config-completion.zsh
source ~/.ai-config-completion.zsh

# Add to .zshrc
echo 'source ~/.ai-config-completion.zsh' >> ~/.zshrc
```

### Fish Completion

```bash
# Generate completion script
ai-config --completion fish > ~/.config/fish/completions/ai-config.fish
```

## Alias Support

### Common Aliases

Users can create aliases for frequently used commands:

```bash
# In .bashrc or .zshrc
alias aic='ai-config'
alias aic-ls='ai-config agent list'
alias aic-new='ai-config agent create'
alias aic-sync='ai-config library sync'
```

## Testing Strategy

### CLI Command Tests

```python
# tests/cli/test_agent_commands.py
from click.testing import CliRunner
from ai_configurator.cli_enhanced import cli

def test_agent_list():
    """Test new agent list command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['agent', 'list'])
    assert result.exit_code == 0

def test_agent_create():
    """Test new agent create command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['agent', 'create', 'test-agent'])
    assert result.exit_code == 0
    assert 'Created agent' in result.output

def test_deprecated_create_agent():
    """Test deprecated command still works."""
    runner = CliRunner()
    result = runner.invoke(cli, ['create-agent', 'test-agent'])
    assert result.exit_code == 0
    assert 'deprecated' in result.output.lower()
```

### Help Text Tests

```python
def test_help_text():
    """Test help text is clear and complete."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert 'agent' in result.output
    assert 'library' in result.output
    assert 'mcp' in result.output

def test_agent_help():
    """Test agent group help."""
    runner = CliRunner()
    result = runner.invoke(cli, ['agent', '--help'])
    assert 'list' in result.output
    assert 'create' in result.output
    assert 'edit' in result.output
```

## Release Plan

### Week 1-2: Implementation
- Implement new command structure
- Remove all old commands
- Update tests
- Update all documentation

### Week 3+: TUI Development
- Build TUI on top of new CLI
- Both interfaces use same commands
- Clean, simple codebase

### Release v4.0.0
- Breaking changes clearly documented
- New command structure only
- Clean slate for TUI integration

## Success Metrics

- [ ] All commands follow consistent pattern
- [ ] Help text is clear and complete
- [ ] Shell completion works
- [ ] Migration guide is comprehensive
- [ ] User confusion decreases
- [ ] Support tickets about commands decrease

---

**Status**: Ready for implementation
**Timeline**: 2 weeks for core implementation
**Priority**: High - Foundation for TUI
