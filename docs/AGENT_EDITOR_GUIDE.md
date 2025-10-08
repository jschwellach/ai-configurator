# Agent Editor Guide

## Overview

The Agent Editor provides a dual-pane interface for managing agent resources and MCP servers. The left pane allows multi-selection of items to add, while the right pane shows the current agent configuration.

## Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Edit Agent: my-agent                                            │
│ Space=Select  Ctrl+S=Save  Esc=Cancel                           │
├──────────────────────────────┬──────────────────────────────────┤
│ Available Library Files      │ Agent Resources (Current)        │
├──────────────────────────────┼──────────────────────────────────┤
│ [ ] common/defaults.md       │ roles/software-engineer/role.md  │
│ [X] common/policies.md       │                                  │
│ [X] domains/aws-best.md      │                                  │
│ [ ] domains/security.md      │                                  │
│ [ ] tools/git.md             │                                  │
├──────────────────────────────┼──────────────────────────────────┤
│ Available MCP Servers        │ Agent MCP Servers (Current)      │
├──────────────────────────────┼──────────────────────────────────┤
│ [X] filesystem               │ brave-search                     │
│ [ ] github                   │                                  │
│ [ ] postgres                 │                                  │
└──────────────────────────────┴──────────────────────────────────┘
```

## How It Works

### Left Pane: Selection Area
Multi-select items to add to the agent:
- **Available Library Files:** All library files with checkboxes
- **Available MCP Servers:** All installed servers with checkboxes
- `[X]` = Selected (will be added when you save)
- `[ ]` = Not selected

### Right Pane: Current State (View Only)
Shows what's currently in the agent:
- **Agent Resources:** Current knowledge files
- **Agent MCP Servers:** Current MCP servers
- Read-only display for reference

## Usage

### Multi-Select Workflow

1. **Navigate** to left pane (Available items)
2. **Select items** with `Space` (toggle checkbox)
3. **Continue selecting** multiple items
4. **Save** with `Ctrl+S` to apply all selections
5. Right pane updates to show new configuration

### Navigation

- `Tab` - Switch between tables
- `↑/↓` - Move cursor within a table
- `Space` - Toggle selection (add/remove checkbox)
- `Ctrl+S` - Save all selected items
- `Escape` - Cancel without saving

## Example Workflow

### Scenario: Configure a Software Engineer Agent

1. **Open Agent Manager** (from main menu)
2. **Select your agent** and press `e` to edit
3. **Select Resources:**
   - Navigate to "Available Library Files"
   - Move to `roles/software-engineer/role.md`
   - Press `Space` (checkbox appears: `[X]`)
   - Move to `tools/git.md`
   - Press `Space` (checkbox appears: `[X]`)
   - Move to `common/policies.md`
   - Press `Space` (checkbox appears: `[X]`)
4. **Select MCP Servers:**
   - Tab to "Available MCP Servers"
   - Move to `github`
   - Press `Space` (checkbox appears: `[X]`)
   - Move to `filesystem`
   - Press `Space` (checkbox appears: `[X]`)
5. **Review:**
   - Check right pane to see current state
   - Left pane shows your selections with `[X]`
6. **Save:**
   - Press `Ctrl+S`
   - All selected items are added to agent
   - Right pane updates to show new configuration

## Tips

### Efficient Selection

**Multi-select is fast:**
- Select multiple items before saving
- No need to save after each selection
- Review all selections before committing

### Deselecting Items

**To remove a selection:**
- Navigate to the item with `[X]`
- Press `Space` to toggle off
- Checkbox changes to `[ ]`

### Starting Fresh

**To replace all resources:**
1. Note current items in right pane
2. Select only the new items you want
3. Save - agent will have only selected items
4. Previous items are replaced (not merged)

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `Tab` | Navigate between tables |
| `↑` | Move cursor up |
| `↓` | Move cursor down |
| `Space` | Toggle selection (checkbox) |
| `Ctrl+S` | Save all selections |
| `Escape` | Cancel and return |

## Troubleshooting

### Checkbox doesn't toggle

**Cause:** Wrong table is focused (right pane is view-only)

**Solution:** Use `Tab` to switch to left pane tables

### Changes aren't saved

**Cause:** Forgot to press `Ctrl+S`

**Solution:** Always press `Ctrl+S` to save. `Escape` cancels all changes.

### Can't see what's selected

**Cause:** Checkboxes might be off-screen

**Solution:** Scroll through the list to see all items and their checkboxes

### Right pane doesn't update

**Cause:** Haven't saved yet

**Solution:** Right pane shows current state. It updates only after you save with `Ctrl+S`

## Advanced Usage

### Bulk Configuration

For agents that need many resources:

1. Create a "base" agent with common resources
2. Export it: `ai-config agent export base-agent`
3. Copy the JSON file
4. Modify the copy with additional resources
5. Import as new agent: `ai-config agent import new-agent.json`

### Template Agents

Create template agents for common roles:

```bash
# Create templates
ai-config agent create developer-template
ai-config agent create researcher-template
ai-config agent create devops-template

# Configure them once with common resources
# Then clone when needed
```

## Related Documentation

- [TUI Guide](TUI_GUIDE.md) - General TUI usage
- [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md) - All shortcuts
- [User Guide](USER_GUIDE.md) - Complete user documentation
- [Agent Editor Fixes](construction/agent_editor_fixes.md) - Technical details
