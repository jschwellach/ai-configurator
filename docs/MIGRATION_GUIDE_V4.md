# Migration Guide: v3.x to v4.0

## Overview

Version 4.0 is a **breaking change release** that introduces a dual-mode interface (TUI + CLI) and simplifies the command structure.

## What's New

### 1. TUI (Terminal User Interface)
- Launch with: `ai-config` (no arguments)
- Visual, menu-driven interface
- Keyboard shortcuts for all operations
- Real-time status updates

### 2. Simplified CLI
- New pattern: `ai-config <resource> <action>`
- Consistent command structure
- Better discoverability
- Automation-friendly

## Command Changes

### Agent Management

| Old (v3.x) | New (v4.0) |
|------------|------------|
| `ai-config create-agent <name>` | `ai-config agent create <name>` |
| `ai-config list-agents` | `ai-config agent list` |
| `ai-config manage-agent <name>` | `ai-config agent edit <name>` |
| `ai-config export-agent <name>` | `ai-config agent export <name>` |

### Library Management

| Old (v3.x) | New (v4.0) |
|------------|------------|
| `ai-config library status` | `ai-config library status` ✓ |
| `ai-config library sync` | `ai-config library sync` ✓ |
| `ai-config files scan-files <agent>` | `ai-config library files <pattern>` |
| `ai-config files add-files <agent>` | `ai-config library add <pattern> <agent>` |

### MCP Management

| Old (v3.x) | New (v4.0) |
|------------|------------|
| `ai-config mcp browse` | `ai-config mcp browse` ✓ |
| `ai-config mcp search <query>` | `ai-config mcp search <query>` ✓ |
| `ai-config mcp install <name>` | `ai-config mcp install <name>` ✓ |
| `ai-config mcp status` | `ai-config mcp list` |
| `ai-config mcp create-sample` | `ai-config mcp init-registry` |

### Wizards (Removed)

| Old (v3.x) | New (v4.0) |
|------------|------------|
| `ai-config wizard create-agent` | `ai-config agent create --interactive` |
| `ai-config wizard setup-mcp` | Use TUI: `ai-config` |
| `ai-config wizard quick-start` | `ai-config init --interactive` |

### System Commands

| Old (v3.x) | New (v4.0) |
|------------|------------|
| `ai-config status` | `ai-config status` ✓ |
| `ai-config cache stats` | `ai-config stats` |
| `ai-config monitoring health` | `ai-config health` |
| `ai-config monitoring logs` | `ai-config logs` |

## New Features

### TUI Mode
```bash
# Launch TUI
ai-config

# Or explicitly
ai-config tui
```

### Interactive Flags
```bash
# Interactive agent creation
ai-config agent create my-agent --interactive

# Interactive library sync
ai-config library sync --interactive

# Interactive MCP installation
ai-config mcp install filesystem --interactive
```

## Migration Steps

### 1. Update Installation
```bash
pip install --upgrade ai-configurator
```

### 2. Update Scripts
Replace old commands with new ones in your scripts:

**Before:**
```bash
ai-config create-agent my-agent
ai-config list-agents
```

**After:**
```bash
ai-config agent create my-agent
ai-config agent list
```

### 3. Try TUI Mode
```bash
# Launch TUI to explore new interface
ai-config
```

## Breaking Changes

### Removed Commands
- All `wizard` commands (replaced by `--interactive` flags)
- `create-agent`, `list-agents`, etc. (use resource-based pattern)
- `files scan-files` (use `library files`)

### Changed Behavior
- `ai-config` with no args now launches TUI (not status)
- `mcp status` renamed to `mcp list`
- `cache stats` renamed to `stats`

## Compatibility

### Not Backward Compatible
- Old command syntax will **not work**
- Scripts must be updated
- No deprecation warnings

### Data Compatibility
- All data formats unchanged
- Agents, library, and MCP configs work as before
- No data migration needed

## Getting Help

### In TUI
- Press `?` for help
- Press `Escape` to go back
- Press `q` to quit

### In CLI
```bash
ai-config --help
ai-config agent --help
ai-config library --help
ai-config mcp --help
```

## Quick Reference

### Common Tasks

**Create an agent:**
```bash
# CLI
ai-config agent create my-agent --tool q-cli

# TUI
ai-config  # Navigate to Agent Management > New
```

**Sync library:**
```bash
# CLI
ai-config library sync

# TUI
ai-config  # Navigate to Library Management > Sync
```

**Browse MCP servers:**
```bash
# CLI
ai-config mcp browse

# TUI
ai-config  # Navigate to MCP Servers > Browse
```

## Support

If you encounter issues:
1. Check this migration guide
2. Run `ai-config --help`
3. Try TUI mode: `ai-config`
4. Report issues on GitHub

---

**Version**: 4.0.0  
**Date**: October 5, 2025
