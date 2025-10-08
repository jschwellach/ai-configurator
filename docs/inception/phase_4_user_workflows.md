# User Workflows - TUI Mode

## Overview

This document describes common user workflows in the new TUI interface, comparing them with CLI equivalents.

## Workflow Categories

1. **First-Time Setup**: New user onboarding
2. **Agent Management**: Creating and managing agents
3. **Library Operations**: Syncing and managing knowledge
4. **MCP Configuration**: Installing and configuring servers
5. **Daily Operations**: Common tasks

---

## 1. First-Time Setup

### Workflow: Complete Initial Setup

**User Goal**: Set up AI Configurator for the first time

#### TUI Flow

```
1. Launch: $ ai-config
   
2. Welcome Screen appears
   ┌─────────────────────────────────────────┐
   │ Welcome to AI Configurator!             │
   │                                         │
   │ Let's get you set up in 3 steps:       │
   │                                         │
   │ [Start Setup]  [Skip]                   │
   └─────────────────────────────────────────┘

3. Step 1: Initialize Library
   ┌─────────────────────────────────────────┐
   │ Step 1/3: Initialize Library            │
   │                                         │
   │ Clone base library from:                │
   │ [https://github.com/org/library.git]    │
   │                                         │
   │ Or use local path:                      │
   │ [/path/to/library]                      │
   │                                         │
   │ [Next]  [Skip]                          │
   └─────────────────────────────────────────┘
   
4. Step 2: Create First Agent
   ┌─────────────────────────────────────────┐
   │ Step 2/3: Create Your First Agent       │
   │                                         │
   │ Agent Name: [my-assistant]              │
   │                                         │
   │ Choose Template:                        │
   │ ( ) Software Engineer                   │
   │ (•) Daily Assistant                     │
   │ ( ) System Administrator                │
   │                                         │
   │ [Next]  [Back]                          │
   └─────────────────────────────────────────┘

5. Step 3: Add MCP Servers
   ┌─────────────────────────────────────────┐
   │ Step 3/3: Add MCP Servers               │
   │                                         │
   │ Recommended servers:                    │
   │ [✓] filesystem - File operations        │
   │ [✓] git - Git operations                │
   │ [ ] brave-search - Web search           │
   │                                         │
   │ [Finish]  [Back]                        │
   └─────────────────────────────────────────┘

6. Setup Complete!
   → Automatically navigates to Main Menu
```

**Time**: ~2 minutes  
**Interactions**: 8 clicks/keypresses

#### CLI Equivalent

```bash
# Step 1: Initialize
$ ai-config init --repo https://github.com/org/library.git

# Step 2: Create agent
$ ai-config agent create my-assistant --template daily-assistant

# Step 3: Add MCP servers
$ ai-config mcp add my-assistant filesystem
$ ai-config mcp add my-assistant git

# Step 4: Export
$ ai-config agent export my-assistant
```

**Time**: ~1 minute (if you know the commands)  
**Interactions**: 4 commands

---

## 2. Agent Management

### Workflow 2.1: Create New Agent from Scratch

**User Goal**: Create a custom agent with specific resources

#### TUI Flow

```
1. From Main Menu → Select "Agent Management"

2. Agent List Screen
   Press 'N' for New Agent

3. Agent Creation Form
   ┌─────────────────────────────────────────┐
   │ Create New Agent                        │
   │                                         │
   │ Name: [dev-helper]                      │
   │ Description: [Development assistant]    │
   │                                         │
   │ Tool Type:                              │
   │ (•) Amazon Q CLI                        │
   │ ( ) Claude Projects                     │
   │ ( ) ChatGPT                             │
   │                                         │
   │ [Next]  [Cancel]                        │
   └─────────────────────────────────────────┘

4. Select Resources
   ┌─────────────────────────────────────────┐
   │ Select Knowledge Resources              │
   │                                         │
   │ Roles:                                  │
   │ [✓] software-engineer.md                │
   │ [ ] software-architect.md               │
   │ [ ] system-administrator.md             │
   │                                         │
   │ Domains:                                │
   │ [✓] aws-best-practices.md               │
   │ [✓] security.md                         │
   │                                         │
   │ Tools:                                  │
   │ [✓] git.md                              │
   │                                         │
   │ [Next]  [Back]                          │
   └─────────────────────────────────────────┘

5. Select MCP Servers
   ┌─────────────────────────────────────────┐
   │ Select MCP Servers                      │
   │                                         │
   │ [✓] filesystem - File operations        │
   │ [✓] git - Git operations                │
   │ [ ] brave-search - Web search           │
   │ [ ] postgres - Database access          │
   │                                         │
   │ [Create]  [Back]                        │
   └─────────────────────────────────────────┘

6. Agent Created!
   → Returns to Agent List with new agent selected
   → Shows success notification
```

**Time**: ~3 minutes  
**Interactions**: 15-20 clicks/keypresses

#### CLI Equivalent

```bash
# Create agent interactively
$ ai-config agent create dev-helper --interactive

# Or non-interactively
$ ai-config agent create dev-helper \
  --tool qcli \
  --resources roles/software-engineer.md,domains/aws-best-practices.md \
  --mcp filesystem,git
```

**Time**: ~1 minute (interactive), ~10 seconds (non-interactive)

### Workflow 2.2: Edit Existing Agent

**User Goal**: Add MCP server to existing agent

#### TUI Flow

```
1. From Agent List → Select agent → Press 'E' for Edit

2. Agent Editor
   ┌─────────────────────────────────────────┐
   │ Edit Agent: dev-helper                  │
   │                                         │
   │ [General] [Resources] [MCP Servers]     │
   │                                         │
   │ Current MCP Servers:                    │
   │ • filesystem                            │
   │ • git                                   │
   │                                         │
   │ [Add Server]  [Remove]  [Configure]     │
   └─────────────────────────────────────────┘

3. Press 'Add Server'
   → Opens server browser
   → Select 'brave-search'
   → Press 'Add'

4. Server Added
   → Returns to editor
   → Shows updated list
   → Press 'Save'

5. Changes Saved
   → Returns to Agent List
   → Shows success notification
```

**Time**: ~1 minute  
**Interactions**: 5-7 clicks/keypresses

#### CLI Equivalent

```bash
$ ai-config mcp add dev-helper brave-search
```

**Time**: ~5 seconds

---

## 3. Library Operations

### Workflow 3.1: Sync Library with Conflicts

**User Goal**: Update library and resolve conflicts

#### TUI Flow

```
1. From Main Menu → Select "Library Management"

2. Library Status Screen
   ┌─────────────────────────────────────────┐
   │ Library Status                          │
   │                                         │
   │ Base Library: 127 files                 │
   │ Personal Library: 15 files              │
   │ Last Sync: 2 hours ago                  │
   │                                         │
   │ Status: 3 conflicts detected            │
   │                                         │
   │ [Sync Now]  [View Conflicts]            │
   └─────────────────────────────────────────┘

3. Press 'Sync Now'
   → Shows progress indicator
   → Detects conflicts

4. Conflict Resolution Screen
   ┌─────────────────────────────────────────┐
   │ Resolve Conflicts (1/3)                 │
   │                                         │
   │ File: roles/software-engineer.md        │
   │                                         │
   │ Base (Remote):    Personal (Local):     │
   │ ┌──────────────┐ ┌──────────────┐      │
   │ │ # Engineer   │ │ # Engineer   │      │
   │ │ - Python     │ │ - Python     │      │
   │ │ - JavaScript │ │ - TypeScript │ ←Diff│
   │ │              │ │ - Rust       │ ←Add │
   │ └──────────────┘ └──────────────┘      │
   │                                         │
   │ Resolution:                             │
   │ ( ) Keep Local                          │
   │ ( ) Use Remote                          │
   │ (•) Merge Both                          │
   │                                         │
   │ [Next]  [Skip]  [Cancel]                │
   └─────────────────────────────────────────┘

5. Resolve each conflict (3 total)
   → Choose resolution for each
   → Press 'Next' to move to next conflict

6. Apply Resolutions
   ┌─────────────────────────────────────────┐
   │ Apply Resolutions?                      │
   │                                         │
   │ Summary:                                │
   │ • 1 file: Keep Local                    │
   │ • 1 file: Use Remote                    │
   │ • 1 file: Merge Both                    │
   │                                         │
   │ [Apply]  [Review]  [Cancel]             │
   └─────────────────────────────────────────┘

7. Sync Complete!
   → Shows success notification
   → Returns to Library Status
```

**Time**: ~5 minutes (depends on conflicts)  
**Interactions**: 10-15 clicks/keypresses

#### CLI Equivalent

```bash
# Interactive sync
$ ai-config library sync --interactive

# Or auto-resolve
$ ai-config library sync --strategy merge
```

**Time**: ~2 minutes (interactive)

### Workflow 3.2: Discover and Add Local Files

**User Goal**: Add project-specific files to agent

#### TUI Flow

```
1. From Agent List → Select agent → Press 'E' for Edit

2. Agent Editor → Select [Resources] tab

3. Resources View
   ┌─────────────────────────────────────────┐
   │ Agent Resources                         │
   │                                         │
   │ Library Files: 12                       │
   │ Local Files: 0                          │
   │                                         │
   │ [Add Library Files]  [Add Local Files]  │
   └─────────────────────────────────────────┘

4. Press 'Add Local Files'
   ┌─────────────────────────────────────────┐
   │ Add Local Files                         │
   │                                         │
   │ Pattern: [./docs/**/*.md]               │
   │ Base Path: [/home/user/project]         │
   │                                         │
   │ [Scan]                                  │
   └─────────────────────────────────────────┘

5. Press 'Scan'
   → Shows discovered files
   ┌─────────────────────────────────────────┐
   │ Found 8 files                           │
   │                                         │
   │ [✓] docs/README.md                      │
   │ [✓] docs/api.md                         │
   │ [✓] docs/architecture.md                │
   │ [ ] docs/internal/secrets.md            │
   │ ...                                     │
   │                                         │
   │ [Add Selected]  [Cancel]                │
   └─────────────────────────────────────────┘

6. Select files → Press 'Add Selected'
   → Files added to agent
   → Returns to Resources View
```

**Time**: ~2 minutes  
**Interactions**: 8-10 clicks/keypresses

#### CLI Equivalent

```bash
$ ai-config library files "./docs/**/*.md" --agent dev-helper
```

**Time**: ~10 seconds

---

## 4. MCP Configuration

### Workflow 4.1: Browse and Install MCP Servers

**User Goal**: Discover and install new MCP servers

#### TUI Flow

```
1. From Main Menu → Select "MCP Server Management"

2. MCP Browser
   ┌─────────────────────────────────────────┐
   │ MCP Server Registry                     │
   │                                         │
   │ Category: [All ▼]  Search: [____]       │
   │                                         │
   │ [ ] filesystem      File operations     │
   │ [✓] git             Git operations      │
   │ [ ] brave-search    Web search          │
   │ [ ] postgres        Database access     │
   │ [ ] slack           Slack integration   │
   │ [✓] github          GitHub API          │
   │                                         │
   │ [Space] Select  [I] Install  [?] Info   │
   └─────────────────────────────────────────┘

3. Navigate to 'brave-search' → Press '?' for Info
   ┌─────────────────────────────────────────┐
   │ Server Details: brave-search            │
   │                                         │
   │ Description: Web search via Brave       │
   │ Command: uvx mcp-server-brave-search    │
   │ Category: Search                        │
   │ Status: Not Installed                   │
   │                                         │
   │ Configuration:                          │
   │ • Requires API key                      │
   │ • Environment: BRAVE_API_KEY            │
   │                                         │
   │ [Install]  [Close]                      │
   └─────────────────────────────────────────┘

4. Press 'Install'
   → Shows installation progress
   → Prompts for API key if needed
   ┌─────────────────────────────────────────┐
   │ Configure brave-search                  │
   │                                         │
   │ API Key: [**********************]       │
   │                                         │
   │ [Save]  [Cancel]                        │
   └─────────────────────────────────────────┘

5. Installation Complete
   → Returns to browser
   → Server now marked as installed
```

**Time**: ~3 minutes  
**Interactions**: 8-12 clicks/keypresses

#### CLI Equivalent

```bash
# Browse
$ ai-config mcp browse

# Install
$ ai-config mcp install brave-search

# Configure
$ ai-config mcp configure brave-search
```

**Time**: ~1 minute

---

## 5. Daily Operations

### Workflow 5.1: Quick Status Check

**User Goal**: Check system status

#### TUI Flow

```
1. Launch: $ ai-config
   → Main Menu shows status automatically

Main Menu (Dashboard)
┌─────────────────────────────────────────┐
│ AI Configurator v4.0.0                  │
│                                         │
│ 📊 System Status                        │
│ ├─ Agents: 5 (4 healthy, 1 warning)    │
│ ├─ Library: 127 files, synced 2h ago   │
│ └─ MCP Servers: 8 installed             │
│                                         │
│ 📋 Recent Activity:                     │
│ • Agent 'dev-helper' exported           │
│ • Library synced successfully           │
│ • MCP 'filesystem' installed            │
│                                         │
│ [Agent Management]                      │
│ [Library Management]                    │
│ [MCP Management]                        │
│ [Settings]                              │
└─────────────────────────────────────────┘
```

**Time**: Instant  
**Interactions**: 0 (just launch)

#### CLI Equivalent

```bash
$ ai-config status
```

**Time**: ~1 second

### Workflow 5.2: Export Agent to Q CLI

**User Goal**: Export agent for use

#### TUI Flow

```
1. From Agent List → Select agent → Press 'X' for Export

2. Export Confirmation
   ┌─────────────────────────────────────────┐
   │ Export Agent: dev-helper                │
   │                                         │
   │ Export to: Amazon Q CLI                 │
   │ Location: ~/.config/amazonq/agents/     │
   │                                         │
   │ This will:                              │
   │ • Create agent configuration            │
   │ • Copy MCP server settings              │
   │ • Update Q CLI config                   │
   │                                         │
   │ [Export]  [Cancel]                      │
   └─────────────────────────────────────────┘

3. Press 'Export'
   → Shows progress
   → Export complete

4. Success Notification
   ┌─────────────────────────────────────────┐
   │ ✓ Agent exported successfully!          │
   │                                         │
   │ You can now use it with:                │
   │ $ q chat --agent dev-helper             │
   │                                         │
   │ [OK]                                    │
   └─────────────────────────────────────────┘
```

**Time**: ~30 seconds  
**Interactions**: 3 clicks/keypresses

#### CLI Equivalent

```bash
$ ai-config agent export dev-helper
```

**Time**: ~2 seconds

---

## Comparison Summary

### TUI Advantages

1. **Discoverability**: See all options without knowing commands
2. **Visual Feedback**: Real-time status and progress
3. **Guided Workflows**: Step-by-step processes
4. **Error Prevention**: Validation before actions
5. **Context Awareness**: See related information
6. **Multi-select**: Easy bulk operations

### CLI Advantages

1. **Speed**: Faster for known operations
2. **Scriptability**: Can automate workflows
3. **Remote Access**: Works over SSH
4. **Low Resource**: Minimal memory/CPU
5. **Composability**: Pipe commands together
6. **Documentation**: Easy to share commands

### When to Use Each

**Use TUI When**:
- Learning the tool
- Exploring features
- Complex multi-step operations
- Visual comparison needed (diffs, conflicts)
- Bulk operations with selection

**Use CLI When**:
- Automating tasks
- Scripting workflows
- Quick single operations
- Remote/SSH access
- CI/CD pipelines
- Documentation/tutorials

---

## Keyboard Shortcuts Reference

### Global Shortcuts

| Key | Action |
|-----|--------|
| `?` | Show help |
| `q` | Quit application |
| `Esc` | Go back / Cancel |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Confirm / Select |
| `Space` | Toggle checkbox |

### Navigation

| Key | Action |
|-----|--------|
| `↑↓` | Navigate lists |
| `←→` | Navigate tabs |
| `Home` | First item |
| `End` | Last item |
| `PgUp/PgDn` | Page up/down |

### Agent Management

| Key | Action |
|-----|--------|
| `n` | New agent |
| `e` | Edit agent |
| `d` | Delete agent |
| `x` | Export agent |
| `v` | Validate agent |
| `r` | Refresh list |

### Library Management

| Key | Action |
|-----|--------|
| `s` | Sync library |
| `d` | Show diff |
| `f` | Find files |
| `r` | Refresh |

### MCP Management

| Key | Action |
|-----|--------|
| `b` | Browse registry |
| `i` | Install server |
| `a` | Add to agent |
| `c` | Configure server |
| `r` | Refresh |

---

**Next Steps**: Begin implementation with Sprint 1 (CLI Simplification)
