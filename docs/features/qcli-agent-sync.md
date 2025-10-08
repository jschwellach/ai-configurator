# Q CLI Agent Synchronization Feature

## Overview

Enable bidirectional synchronization between Q CLI agents and AI Agent Manager, allowing users to import existing Q CLI agents and keep them in sync.

## Current State

- ✅ **Export**: Agents auto-export from AI Agent Manager → Q CLI (`~/.aws/amazonq/cli-agents/`)
- ❌ **Import**: No way to import existing Q CLI agents into AI Agent Manager
- ❌ **Sync**: No detection of external changes to Q CLI agents

## Goals

1. **Import existing Q CLI agents** into AI Agent Manager
2. **Detect conflicts** when agent exists in both locations
3. **Sync changes** made externally to Q CLI agents
4. **Preserve user choice** on sync direction (import, export, or bidirectional)

## User Stories

### US-1: Import Single Agent
**As a user**, I want to import an existing Q CLI agent into AI Agent Manager, so I can manage it through the TUI.

**Acceptance Criteria:**
- [ ] User can select "Import from Q CLI" option in Agent Management
- [ ] System shows list of Q CLI agents not yet in AI Agent Manager
- [ ] User can select agent(s) to import
- [ ] System converts Q CLI format to AgentConfig format
- [ ] Imported agent appears in agent list

### US-2: Bulk Import All Agents
**As a user**, I want to import all my Q CLI agents at once, so I don't have to import them one by one.

**Acceptance Criteria:**
- [ ] User can select "Import All from Q CLI" option
- [ ] System imports all Q CLI agents not yet in AI Agent Manager
- [ ] System shows summary of imported agents
- [ ] User can review and confirm before import

### US-3: Detect Conflicts
**As a user**, when an agent exists in both locations with different content, I want to choose which version to keep.

**Acceptance Criteria:**
- [ ] System detects when agent exists in both locations
- [ ] System compares content and shows differences
- [ ] User can choose: Keep Local, Keep Q CLI, or Merge
- [ ] System applies user's choice

### US-4: Sync External Changes
**As a user**, when I edit a Q CLI agent externally (e.g., manually or through Q CLI), I want AI Agent Manager to detect and sync the changes.

**Acceptance Criteria:**
- [ ] System detects when Q CLI agent has been modified externally
- [ ] User is notified of external changes
- [ ] User can choose to pull changes or ignore
- [ ] System updates local agent with Q CLI version

### US-5: Sync Mode Configuration
**As a user**, I want to configure sync behavior per agent or globally.

**Acceptance Criteria:**
- [ ] User can set sync mode: Manual, Auto-Import, Auto-Export, Bidirectional
- [ ] Manual: No automatic sync, user triggers import/export
- [ ] Auto-Import: Pull changes from Q CLI automatically
- [ ] Auto-Export: Push changes to Q CLI automatically (current behavior)
- [ ] Bidirectional: Sync both ways, prompt on conflicts

## Technical Design

### 1. Q CLI Agent Format

Q CLI agents are stored in `~/.aws/amazonq/cli-agents/<agent-name>.json`:

```json
{
  "name": "my-agent",
  "description": "Agent description",
  "instruction": "System prompt...",
  "resources": [
    {
      "type": "file",
      "path": "/path/to/file.md"
    }
  ],
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### 2. AI Agent Manager Format

Agents stored in `~/.config/ai-configurator/agents/<agent-name>.json`:

```json
{
  "name": "my-agent",
  "description": "Agent description",
  "prompt": "System prompt...",
  "tool_type": "q-cli",
  "resources": ["templates/file.md"],
  "mcp_servers": ["fetch"],
  "settings": {},
  "created_at": "2025-10-08T10:00:00"
}
```

### 3. Conversion Logic

**Q CLI → AI Agent Manager:**
- `instruction` → `prompt`
- `resources[].path` → extract relative path from library
- `mcpServers` → extract server names

**AI Agent Manager → Q CLI:**
- `prompt` → `instruction`
- `resources[]` → resolve to absolute paths
- `mcp_servers[]` → load full server configs from registry

### 4. Sync Service

Create `SyncService` class:

```python
class QCLISyncService:
    def __init__(self, qcli_agents_dir: Path, local_agents_dir: Path):
        self.qcli_dir = qcli_agents_dir
        self.local_dir = local_agents_dir
    
    def list_qcli_agents(self) -> List[str]:
        """List all Q CLI agents."""
        
    def import_agent(self, agent_name: str) -> AgentConfig:
        """Import single agent from Q CLI."""
        
    def import_all(self) -> List[AgentConfig]:
        """Import all Q CLI agents."""
        
    def detect_conflicts(self) -> List[ConflictInfo]:
        """Detect agents that exist in both locations."""
        
    def compare_agents(self, agent_name: str) -> DiffInfo:
        """Compare local and Q CLI versions."""
        
    def sync_from_qcli(self, agent_name: str) -> bool:
        """Pull changes from Q CLI to local."""
        
    def sync_to_qcli(self, agent_name: str) -> bool:
        """Push changes from local to Q CLI (existing behavior)."""
```

### 5. UI Changes

**Agent Management Screen:**
- Add "Import from Q CLI" button (key: `i`)
- Add "Sync All" button (key: `s`)
- Show sync status indicator per agent:
  - ✓ Synced
  - ↑ Local changes (needs export)
  - ↓ Q CLI changes (needs import)
  - ⚠ Conflict (needs resolution)

**Import Screen:**
- List Q CLI agents with checkboxes
- Show which agents already exist locally
- Allow multi-select for bulk import
- Show preview of agent before import

**Conflict Resolution Screen:**
- Side-by-side diff view
- Options: Keep Local, Keep Q CLI, Merge
- Show what will change

### 6. Configuration

Add to agent settings:

```json
{
  "sync_mode": "auto-export",  // manual, auto-import, auto-export, bidirectional
  "last_synced": "2025-10-08T10:00:00",
  "qcli_hash": "abc123..."  // hash of Q CLI version for change detection
}
```

## Implementation Plan

### Phase 1: Basic Import (v0.2.0)
- [ ] Create `QCLISyncService` class
- [ ] Implement `list_qcli_agents()`
- [ ] Implement `import_agent()` with format conversion
- [ ] Add "Import from Q CLI" option to Agent Management
- [ ] Add import screen with agent selection
- [ ] Test import with various agent configurations

### Phase 2: Conflict Detection (v0.3.0)
- [ ] Implement `detect_conflicts()`
- [ ] Implement `compare_agents()` with diff
- [ ] Add conflict resolution screen
- [ ] Add sync status indicators to agent list
- [ ] Test conflict scenarios

### Phase 3: Auto-Sync (v0.4.0)
- [ ] Add sync mode configuration
- [ ] Implement file watching for Q CLI directory
- [ ] Add auto-import on Q CLI changes
- [ ] Add sync status notifications
- [ ] Test bidirectional sync

### Phase 4: Polish (v0.5.0)
- [ ] Add bulk operations (import all, sync all)
- [ ] Add sync history/log
- [ ] Add undo/rollback for sync operations
- [ ] Performance optimization for large agent lists
- [ ] Documentation and user guide

## Open Questions

1. **Resource Path Resolution**: How to handle absolute paths in Q CLI agents that reference files outside the library?
   - ~~Option A: Copy files to library~~
   - ~~Option B: Keep absolute paths, show warning~~
   - **✅ Option C: Ask user per file** (DECIDED)
     - During import, prompt for each external file
     - Options: "Copy to library" or "Keep absolute path"
     - Show file path and size in prompt
     - Remember choice for "Apply to all" option

2. **MCP Server Configs**: Q CLI agents have full MCP configs inline. Should we:
   - **✅ Option A: Extract to registry as new servers** (DECIDED)
     - Create server files in `~/.config/ai-configurator/registry/servers/`
     - If name exists, append number (e.g., `fetch-2.json`, `fetch-3.json`)
     - Agent references by name
     - User can edit/delete/merge duplicates afterwards
   - ~~Option B: Keep inline in agent (duplicate configs)~~
   - ~~Option C: Match by name/command and link to existing~~

3. **Sync Conflicts**: When both versions changed, how to merge?
   - ~~Option A: Manual merge only (user chooses)~~
   - **✅ Option B: Smart merge (combine resources/servers)** (DECIDED)
     - Auto-merge non-conflicting changes:
       - Resources: Union of both lists (combine unique items)
       - MCP servers: Union of both lists
       - Description: Keep local if both changed (prompt user)
       - Prompt: Keep local if both changed (prompt user)
     - Only prompt for actual conflicts (same field, different values)
     - Show what was auto-merged in summary
   - ~~Option C: Three-way merge with common ancestor~~

4. **Performance**: With many agents, should we:
   - **✅ Option A: Sync on-demand only** (DECIDED)
     - User manually triggers "Import from Q CLI"
     - No automatic background operations
     - One-time import workflow (not continuous sync)
     - User manages agents in AI Agent Manager after import
     - Pros: Simple, predictable, no background processes
     - Cons: User must manually re-import if they want to pull Q CLI changes again
   - ~~Option B: Background sync with notifications~~
   - ~~Option C: Configurable sync interval~~

## Success Metrics

- Users can import existing Q CLI agents in < 30 seconds
- Conflict resolution is clear and intuitive
- No data loss during sync operations
- Sync performance: < 1 second for 10 agents

## Related Issues

- Export to Q CLI (implemented in v4.0.0)
- Agent validation
- Library path resolution
