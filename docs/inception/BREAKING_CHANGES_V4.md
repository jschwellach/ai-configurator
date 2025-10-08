# Breaking Changes in v4.0.0

## Overview

Version 4.0.0 is a **complete redesign** with breaking changes. Since the tool is not yet in production use, we're taking a clean break approach rather than maintaining backward compatibility.

## What's Changing

### 1. CLI Command Structure

**Old (v3.x)**:
```bash
ai-config create-agent my-agent
ai-config list-agents
ai-config manage-agent my-agent
ai-config export-agent my-agent
ai-config files scan-files my-agent
ai-config wizard create-agent
```

**New (v4.0)**:
```bash
ai-config agent create my-agent
ai-config agent list
ai-config agent edit my-agent
ai-config agent export my-agent
ai-config library files "**/*.md"
ai-config agent create --interactive
```

### 2. New TUI Interface

**Launch TUI**:
```bash
ai-config          # Launches TUI by default
ai-config tui      # Explicit TUI launch
```

**Use CLI**:
```bash
ai-config agent list              # Direct command execution
ai-config library sync            # No TUI, just runs command
```

## Command Mapping

### Agent Management
| Old | New |
|-----|-----|
| `create-agent` | `agent create` |
| `list-agents` | `agent list` |
| `manage-agent` | `agent edit` |
| `export-agent` | `agent export` |

### Library Management
| Old | New |
|-----|-----|
| `files scan-files` | `library files` |
| `files add-files` | `library add` |
| `files watch-files` | `library watch` |

### MCP Management
| Old | New |
|-----|-----|
| `mcp status` | `mcp list` |
| `mcp create-sample` | `mcp init-registry` |

### Wizards (Removed)
| Old | New |
|-----|-----|
| `wizard create-agent` | `agent create --interactive` |
| `wizard setup-mcp` | `mcp add --interactive` |
| `wizard quick-start` | `init --interactive` |

### System Commands
| Old | New |
|-----|-----|
| `cache stats` | `stats` |
| `monitoring health` | `health` |
| `monitoring logs` | `logs` |

## Why Breaking Changes?

1. **Not in Production**: Tool not yet widely used
2. **Better UX**: Consistent, intuitive command structure
3. **Cleaner Code**: No legacy compatibility layer
4. **Faster Development**: Simpler implementation
5. **Future-Proof**: Better foundation for growth

## Migration Path

Since there are no production users:
- **No migration needed**
- **Clean slate** with v4.0.0
- **Better documentation** from the start
- **Simpler onboarding** for new users

## Timeline

- **Week 1-2**: Implement new CLI (breaking changes)
- **Week 3-8**: Build TUI on new foundation
- **Week 9**: Polish and release v4.0.0

## Benefits

✅ **Consistent Commands**: All follow `<resource> <action>` pattern  
✅ **Visual Interface**: TUI for exploration and learning  
✅ **Fast CLI**: Simplified commands for automation  
✅ **Clean Codebase**: No legacy code to maintain  
✅ **Better UX**: Intuitive from day one  

---

**Decision**: Approved for breaking changes in v4.0.0  
**Rationale**: No production users, better long-term architecture  
**Impact**: None (no existing users to migrate)
