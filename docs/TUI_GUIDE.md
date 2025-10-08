# TUI User Guide

## Overview

AI Configurator v4.0 includes a Terminal User Interface (TUI) that provides a visual, menu-driven way to manage agents, libraries, and MCP servers.

## Launching TUI

```bash
# Launch TUI (default)
ai-config

# Or explicitly
ai-config tui
```

## Main Menu

The main menu shows:
- System status (agents, library files, MCP servers)
- Navigation buttons
- Keyboard shortcuts

### Navigation
- Press `1` or click "Agent Management"
- Press `2` or click "Library Management"
- Press `3` or click "MCP Servers"
- Press `4` or click "Settings"

## Global Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `?` | Show help |
| `Escape` | Go back / Cancel |
| `Ctrl+R` | Refresh current screen |
| `F5` | Refresh data |
| `Tab` | Move between elements |
| `Enter` | Select / Confirm |

## Agent Management

### Viewing Agents
- Navigate to Agent Management
- See list of all agents with details
- Use arrow keys to select an agent

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `n` | Create new agent |
| `e` | Edit selected agent |
| `d` | Delete selected agent |
| `x` | Export selected agent |

### Creating an Agent
1. Press `n` or click "New"
2. Follow the creation wizard
3. Agent is created and appears in list

### Editing an Agent
1. Select agent from list
2. Press `e` or click "Edit"
3. Modify configuration
4. Save changes

### Deleting an Agent
1. Select agent from list
2. Press `d` or click "Delete"
3. Confirm deletion
4. Agent is removed

### Exporting an Agent
1. Select agent from list
2. Press `x` or click "Export"
3. Agent is exported to target tool

## Library Management

### Viewing Library Status
- Navigate to Library Management
- See library version, file count, last sync

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `s` | Sync library |
| `d` | Show differences |
| `u` | Update from base |

### Syncing Library
1. Press `s` or click "Sync"
2. Wait for sync to complete
3. If conflicts found, resolve them
4. Sync completes

### Viewing Differences
1. Press `d` or click "Diff"
2. See list of changed files
3. Review differences

### Updating Library
1. Press `u` or click "Update"
2. Library updates from base
3. Status refreshes

## MCP Server Management

### Viewing Installed Servers
- Navigate to MCP Servers
- See list of installed servers

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `b` | Browse registry |
| `i` | Install server |
| `c` | Configure server |

### Browsing Registry
1. Press `b` or click "Browse"
2. See available servers
3. Select servers to install

### Installing a Server
1. Browse registry or select from list
2. Press `i` or click "Install"
3. Server is downloaded and configured
4. Appears in installed list

### Configuring a Server
1. Select server from list
2. Press `c` or click "Configure"
3. Edit server parameters
4. Save configuration

## Settings

Navigate to Settings to view and modify:
- General settings (theme, editor)
- Library settings (auto-sync, conflict resolution)
- MCP settings (registry URL, auto-update)

## Help

Press `?` at any time to see:
- Keyboard shortcuts
- Navigation help
- Feature documentation

## Tips

### Efficient Navigation
- Use number keys (1-4) for quick navigation
- Use keyboard shortcuts instead of clicking
- Press `Escape` to go back quickly

### Data Refresh
- Press `F5` to refresh current screen
- Press `Ctrl+R` to refresh all data

### Getting Unstuck
- Press `Escape` to cancel operations
- Press `?` to see help
- Press `q` to quit

## Troubleshooting

### TUI Won't Launch
```bash
# Check dependencies
pip install textual

# Try explicit launch
ai-config tui
```

### Display Issues
- Ensure terminal supports colors
- Try different terminal emulator
- Check terminal size (minimum 80x24)

### Keyboard Shortcuts Not Working
- Check terminal key bindings
- Try alternative shortcuts
- Use mouse/click instead

## Advanced Usage

### Over SSH
TUI works over SSH connections:
```bash
ssh user@host
ai-config
```

### In tmux/screen
TUI works in terminal multiplexers:
```bash
tmux
ai-config
```

### Custom Terminal
TUI adapts to terminal colors and capabilities automatically.

---

**Version**: 4.0.0  
**Date**: October 5, 2025
