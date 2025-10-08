# Phase 4: TUI Redesign - Software Architect Plan

## Planning Date: October 5, 2025

## Executive Summary

Phase 4 transforms AI Configurator from a command-based CLI to a modern Terminal User Interface (TUI) while maintaining backward compatibility with simplified CLI commands. This redesign dramatically improves user experience through visual navigation, discoverability, and intuitive workflows.

## Problem Statement

### Current UX Challenges
1. **Low Discoverability**: Users must know commands to use features
2. **Command Complexity**: Current structure mixes patterns (`ai-config status` vs `ai-config wizard create-agent`)
3. **Multi-step Friction**: Complex workflows require multiple command invocations
4. **Learning Curve**: New users struggle to understand available features
5. **Context Switching**: Moving between operations requires exiting and re-running commands

### User Feedback
- "I don't know what commands are available"
- "Too many commands to remember"
- "Wish I could see all options in one place"
- "Hard to understand what the tool can do"

## Solution: Dual-Mode Interface

### Mode 1: TUI (Primary Interactive Mode)
**Launch**: `ai-config` or `ai-config tui`

**Features**:
- Persistent menu navigation
- Visual component selection (checkboxes, lists)
- Built-in editor for configurations
- Real-time status display
- Contextual help panels
- Keyboard shortcuts

### Mode 2: Simplified CLI (Automation & Scripting)
**Pattern**: `ai-config <resource> <action> [options]`

**Examples**:
```bash
ai-config agent list
ai-config agent create <name>
ai-config agent export <name>
ai-config library sync
ai-config mcp browse
```

## Architecture Overview

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point (main)                       │
│              Detects mode: TUI vs CLI                       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │   TUI Mode     │         │   CLI Mode     │
        │   (Textual)    │         │   (Click)      │
        └───────┬────────┘         └───────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │     Service Layer         │
                │  (Unchanged - Reused)     │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │      Data Layer           │
                │  (Unchanged - Reused)     │
                └───────────────────────────┘
```

## TUI Component Architecture

### Main Application Structure

```python
class AIConfiguratorApp(App):
    """Main TUI application using Textual."""
    
    SCREENS = {
        "main_menu": MainMenuScreen,
        "agent_manager": AgentManagerScreen,
        "library_manager": LibraryManagerScreen,
        "mcp_manager": MCPManagerScreen,
        "settings": SettingsScreen,
    }
```

### Screen Hierarchy

```
MainMenuScreen (Dashboard)
├── AgentManagerScreen
│   ├── AgentListView
│   ├── AgentCreateView
│   ├── AgentEditView
│   └── AgentExportView
├── LibraryManagerScreen
│   ├── LibraryStatusView
│   ├── LibrarySyncView
│   ├── ConflictResolutionView
│   └── FileDiscoveryView
├── MCPManagerScreen
│   ├── MCPBrowseView
│   ├── MCPInstallView
│   ├── MCPConfigureView
│   └── RegistryManageView
└── SettingsScreen
    ├── ConfigurationView
    ├── BackupView
    └── LogsView
```

## Simplified CLI Structure

### Resource-Based Command Pattern

**Format**: `ai-config <resource> <action> [arguments] [options]`

### Command Mapping

#### Agent Management
```bash
ai-config agent list                    # List all agents
ai-config agent show <name>             # Show agent details
ai-config agent create <name>           # Create new agent
ai-config agent edit <name>             # Edit agent (opens editor)
ai-config agent delete <name>           # Delete agent
ai-config agent export <name>           # Export to Q CLI
ai-config agent validate <name>         # Validate configuration
```

#### Library Management
```bash
ai-config library status                # Show library status
ai-config library sync                  # Sync with conflict resolution
ai-config library diff                  # Show differences
ai-config library update                # Update from base
ai-config library files <pattern>       # Discover files
```

#### MCP Management
```bash
ai-config mcp list                      # List installed servers
ai-config mcp browse                    # Browse registry
ai-config mcp search <query>            # Search servers
ai-config mcp install <name>            # Install server
ai-config mcp add <agent> <server>      # Add server to agent
ai-config mcp remove <agent> <server>   # Remove from agent
```

#### System Commands
```bash
ai-config status                        # System overview (special case)
ai-config tui                           # Launch TUI mode
ai-config init                          # Initialize configuration
ai-config backup                        # Create backup
ai-config restore <backup-id>           # Restore backup
```

### Migration from Current Commands

| Current Command | New Command | Notes |
|----------------|-------------|-------|
| `ai-config status` | `ai-config status` | Unchanged |
| `ai-config create-agent` | `ai-config agent create` | Simplified |
| `ai-config list-agents` | `ai-config agent list` | Simplified |
| `ai-config manage-agent <name>` | `ai-config agent edit <name>` | Clearer |
| `ai-config export-agent <name>` | `ai-config agent export <name>` | Consistent |
| `ai-config library sync` | `ai-config library sync` | Unchanged |
| `ai-config files scan-files` | `ai-config library files` | Simplified |
| `ai-config mcp browse` | `ai-config mcp browse` | Unchanged |
| `ai-config wizard create-agent` | `ai-config agent create` (interactive) | Merged |

## TUI Screen Designs

### 1. Main Menu Screen (Dashboard)

```
┌─────────────────────────────────────────────────────────────┐
│ AI Configurator v4.0.0                          [?] Help    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 System Status                                           │
│  ├─ Agents: 5 (4 healthy, 1 warning)                       │
│  ├─ Library: 127 files, synced 2 hours ago                 │
│  └─ MCP Servers: 8 installed, 3 in registry                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 Agent Management          [Enter]              │   │
│  │  📚 Library Management         [Enter]              │   │
│  │  🔧 MCP Server Management      [Enter]              │   │
│  │  ⚙️  Settings                  [Enter]              │   │
│  │  📋 View Logs                  [Enter]              │   │
│  │  ❌ Exit                        [Esc/Q]             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Recent Activity:                                           │
│  • Agent 'dev-assistant' exported to Q CLI                  │
│  • Library synced successfully                              │
│  • MCP server 'filesystem' installed                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ↑↓: Navigate  Enter: Select  ?: Help  Q: Quit              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Agent Manager Screen

```
┌─────────────────────────────────────────────────────────────┐
│ Agent Management                           [←] Back  [?] Help│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Actions: [N]ew  [E]dit  [D]elete  [X]port  [R]efresh      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Name              Tool    Resources  Status         │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ ▶ dev-assistant   Q CLI   12         ✓ Healthy     │   │
│  │   architect       Q CLI   8          ✓ Healthy     │   │
│  │   sysadmin        Q CLI   6          ⚠ Warning     │   │
│  │   daily-helper    Q CLI   15         ✓ Healthy     │   │
│  │   product-owner   Q CLI   5          ✓ Healthy     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Selected: dev-assistant                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Details:                                            │   │
│  │ • Created: 2025-09-15                               │   │
│  │ • Resources: 12 files from library                  │   │
│  │ • MCP Servers: filesystem, git, brave-search        │   │
│  │ • Last exported: 2025-10-05 14:30                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ↑↓: Navigate  Enter: Edit  N: New  X: Export  Esc: Back    │
└─────────────────────────────────────────────────────────────┘
```

### 3. MCP Manager Screen

```
┌─────────────────────────────────────────────────────────────┐
│ MCP Server Management                  [←] Back  [?] Help   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [B]rowse Registry  [I]nstall  [C]onfigure  [A]dd to Agent │
│                                                             │
│  Registry Servers:                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [ ] filesystem      File operations                 │   │
│  │ [✓] git             Git operations                  │   │
│  │ [✓] brave-search    Web search                      │   │
│  │ [ ] postgres        Database access                 │   │
│  │ [ ] slack           Slack integration               │   │
│  │ [✓] github          GitHub API                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Selected: git                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Description: Git repository operations              │   │
│  │ Command: uvx mcp-server-git                         │   │
│  │ Status: Installed                                   │   │
│  │ Used by: dev-assistant, architect                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Actions:                                                   │
│  • [Space] Toggle selection                                 │
│  • [I] Install selected servers                             │
│  • [A] Add to agent                                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Space: Select  I: Install  A: Add to Agent  Esc: Back      │
└─────────────────────────────────────────────────────────────┘
```

### 4. Library Sync Screen

```
┌─────────────────────────────────────────────────────────────┐
│ Library Synchronization                [←] Back  [?] Help   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Status: 3 conflicts detected                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ File: roles/software-engineer.md                    │   │
│  │                                                     │   │
│  │ Base (Remote):        Personal (Local):            │   │
│  │ ┌─────────────────┐  ┌─────────────────┐          │   │
│  │ │ # Software Eng  │  │ # Software Eng  │          │   │
│  │ │ Expert in...    │  │ Expert in...    │          │   │
│  │ │ - Python        │  │ - Python        │          │   │
│  │ │ - JavaScript    │  │ - TypeScript    │ ← Diff   │   │
│  │ │                 │  │ - Rust          │ ← Added  │   │
│  │ └─────────────────┘  └─────────────────┘          │   │
│  │                                                     │   │
│  │ Resolution:                                         │   │
│  │ ( ) Keep Local   ( ) Use Remote   (•) Merge        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [N]ext Conflict  [P]revious  [A]pply All  [C]ancel        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ←→: Choose  N/P: Navigate  A: Apply  C: Cancel              │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack Updates

### New Dependencies

```python
# TUI Framework
textual>=0.40.0           # Modern TUI framework built on Rich
textual-dev>=1.0.0        # Development tools for Textual

# Enhanced Editing
click-default-group>=1.2  # Better CLI grouping
```

### Existing Dependencies (Retained)
- click>=8.0.0 (CLI commands)
- rich>=13.0.0 (Textual uses Rich internally)
- pydantic>=2.0.0 (Data models)
- All other Phase 1-3 dependencies

## Implementation Phases

### Sprint 1: CLI Simplification (Week 1-2)
**Goal**: Restructure CLI to resource-based pattern

**Tasks**:
- [ ] Create new CLI structure with Click groups
- [ ] Implement `agent` command group
- [ ] Implement `library` command group
- [ ] Implement `mcp` command group
- [ ] Add deprecation warnings for old commands
- [ ] Update all documentation

**Deliverables**:
- Simplified CLI with consistent pattern
- Backward compatibility layer
- Updated help text

### Sprint 2: TUI Foundation (Week 3-4)
**Goal**: Build core TUI infrastructure

**Tasks**:
- [ ] Set up Textual application structure
- [ ] Create MainMenuScreen (dashboard)
- [ ] Implement screen navigation system
- [ ] Create base screen components (header, footer, status bar)
- [ ] Add keyboard shortcut system
- [ ] Implement help system

**Deliverables**:
- Working TUI shell
- Main menu navigation
- Basic screen switching

### Sprint 3: Agent Management TUI (Week 5-6)
**Goal**: Complete agent management screens

**Tasks**:
- [ ] Create AgentManagerScreen
- [ ] Implement agent list view with selection
- [ ] Create agent creation wizard (TUI)
- [ ] Build agent editor with form validation
- [ ] Add agent export functionality
- [ ] Implement agent deletion with confirmation

**Deliverables**:
- Full agent management in TUI
- Interactive forms and wizards
- Real-time validation

### Sprint 4: Library & MCP TUI (Week 7-8)
**Goal**: Complete library and MCP screens

**Tasks**:
- [ ] Create LibraryManagerScreen
- [ ] Implement sync with visual conflict resolution
- [ ] Build file discovery interface
- [ ] Create MCPManagerScreen
- [ ] Implement server browsing with checkboxes
- [ ] Add server installation progress

**Deliverables**:
- Library management in TUI
- MCP server management in TUI
- Visual conflict resolution

### Sprint 5: Polish & Integration (Week 9-10)
**Goal**: Complete integration and polish

**Tasks**:
- [ ] Add settings screen
- [ ] Implement log viewer
- [ ] Add keyboard shortcuts help
- [ ] Create onboarding tutorial
- [ ] Add themes (dark/light)
- [ ] Performance optimization
- [ ] Comprehensive testing

**Deliverables**:
- Complete TUI application
- Settings and configuration
- Help and documentation
- Performance tuning

## User Workflows in TUI

### Workflow 1: Create New Agent
1. Launch TUI: `ai-config`
2. Select "Agent Management" from main menu
3. Press `N` for new agent
4. Fill form:
   - Name: [text input]
   - Description: [text input]
   - Tool: [dropdown: Q CLI, Claude, ChatGPT]
   - Template: [list: software-engineer, architect, etc.]
5. Select resources from library [checkbox list]
6. Select MCP servers [checkbox list]
7. Review and confirm
8. Agent created and exported

**CLI Equivalent**: `ai-config agent create my-agent --interactive`

### Workflow 2: Sync Library with Conflicts
1. Launch TUI: `ai-config`
2. Select "Library Management"
3. Press `S` for sync
4. View conflicts in split-pane view
5. For each conflict:
   - See diff side-by-side
   - Choose: Keep Local / Use Remote / Merge
6. Apply all resolutions
7. Sync complete

**CLI Equivalent**: `ai-config library sync --interactive`

### Workflow 3: Browse and Install MCP Servers
1. Launch TUI: `ai-config`
2. Select "MCP Server Management"
3. Browse registry (arrow keys)
4. Press `Space` to select multiple servers
5. Press `I` to install selected
6. See installation progress
7. Press `A` to add to agent
8. Select target agent
9. Servers configured

**CLI Equivalent**: `ai-config mcp install filesystem git`

## Breaking Changes Approach

### Clean Break Strategy
1. **Week 1-2**: Implement new CLI structure, remove all old commands
2. **Week 3-10**: TUI development with new CLI
3. **No Migration Period**: Direct switch to new commands
4. **Version**: Jump to v4.0.0 indicating breaking changes

### No Deprecation Needed
- Remove all old command implementations
- Clean codebase without legacy code
- Simpler implementation and maintenance

## Testing Strategy

### TUI Testing
- **Unit Tests**: Test screen logic independently
- **Integration Tests**: Test screen navigation and data flow
- **Snapshot Tests**: Visual regression testing
- **Manual Testing**: User acceptance testing

### CLI Testing
- **Command Tests**: Test all new CLI commands
- **Backward Compatibility**: Test old commands still work
- **Help Text**: Verify all help messages
- **Error Handling**: Test error scenarios

## Success Metrics

### User Experience
- [ ] New users can create agent without reading docs
- [ ] All features discoverable through TUI menus
- [ ] Common workflows complete in < 5 interactions
- [ ] Zero commands needed for basic usage

### Technical
- [ ] TUI launches in < 1 second
- [ ] All Phase 1-3 features available in TUI
- [ ] CLI commands follow consistent pattern
- [ ] 100% backward compatibility maintained

### Adoption
- [ ] 80% of users prefer TUI over CLI
- [ ] Support tickets decrease by 50%
- [ ] Onboarding time reduced by 60%

## Risk Management

### High Risk
1. **TUI Complexity**: Textual learning curve
   - **Mitigation**: Start with simple screens, iterate
   
2. **Performance**: TUI may be slower than CLI
   - **Mitigation**: Async operations, progress indicators

### Medium Risk
1. **Breaking Changes**: CLI restructure may confuse users
   - **Mitigation**: Deprecation warnings, clear migration guide
   
2. **Testing Complexity**: TUI harder to test
   - **Mitigation**: Good separation of concerns, snapshot tests

## Next Steps

1. **Review and Approve**: Get stakeholder approval for plan
2. **Sprint 1 Kickoff**: Begin CLI simplification
3. **Prototype**: Create TUI proof-of-concept
4. **Iterate**: Gather feedback and refine

---

**Status**: 📋 **PLANNED** - Ready for review and approval
**Timeline**: 10 weeks (2.5 months)
**Priority**: High - Addresses critical UX issues
**Dependencies**: Phase 1-3 complete (✅)
