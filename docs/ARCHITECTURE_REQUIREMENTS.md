# Architecture Requirements - MCP Registry Enhancement

## Current State

The AI Configurator has a robust MCP server management system with the following components:

### Existing MCP System
- **Agent-level MCP servers**: Direct addition to specific agents via `ai-config mcp add` and `ai-config wizard add-mcp-json <agent>`
- **Sample registry**: Pre-defined servers via `ai-config mcp create-sample`
- **Registry browsing**: Discovery of sample servers via `ai-config mcp browse`
- **JSON wizard**: Handles fastmcp.me format and JSON fragments with auto-fixing

### Current Limitation
The `ai-config wizard add-mcp-json` command without an agent parameter processes and validates JSON but **does not persist user-added servers to the registry**.

## Required Enhancement: User-Added Server Registry

### Problem Statement
Users expect that when they run:
```bash
ai-config wizard add-mcp-json  # No agent specified
```
The servers should be added to the registry for future discovery and use by any agent.

### Current Behavior vs Expected Behavior

**Current:**
```bash
ai-config wizard add-mcp-json
# → Validates JSON, shows "Registry addition not yet implemented"
# → Server config is lost

ai-config wizard add-mcp-json assistant  
# → Adds directly to agent, works perfectly
```

**Expected:**
```bash
ai-config wizard add-mcp-json
# → Adds to registry, available for all agents
# → Shows in `ai-config mcp browse`
# → Can be installed via `ai-config wizard setup-mcp <agent>`
```

### Technical Requirements

#### 1. Registry Service Enhancement
**File:** `ai_configurator/services/registry_service.py`

**Required Methods:**
```python
def add_user_server(self, server_config: MCPServerConfig, server_name: str) -> bool:
    """Add user-defined server to registry."""
    
def get_user_servers(self) -> List[MCPServer]:
    """Get all user-added servers."""
    
def remove_user_server(self, server_name: str) -> bool:
    """Remove user-added server from registry."""
```

#### 2. Registry Storage Structure
**Location:** `~/.config/ai-configurator/registry/`

**Proposed Structure:**
```
registry/
├── sample_servers.json     # Built-in sample servers
├── user_servers.json       # User-added servers (NEW)
└── installed_servers.json  # Installation tracking
```

#### 3. Registry Model Updates
**File:** `ai_configurator/models/registry_models.py`

**Required Updates:**
- Support for user-added server metadata
- Differentiation between sample and user servers
- Persistence layer for user servers

#### 4. Integration Points

**Browse Command Enhancement:**
```bash
ai-config mcp browse
# Should show both sample AND user-added servers
# With clear indication of source (sample vs user-added)
```

**Setup Wizard Enhancement:**
```bash
ai-config wizard setup-mcp assistant
# Should include user-added servers in selection
```

### Implementation Approach

#### Phase 1: Core Registry Enhancement
1. **Extend RegistryService** with user server methods
2. **Create user_servers.json** storage mechanism
3. **Update MCPServerRegistry model** to handle both server types

#### Phase 2: Integration
1. **Update JSON wizard** to call `add_user_server()` when no agent specified
2. **Enhance browse command** to show user servers
3. **Update setup wizard** to include user servers in selection

#### Phase 3: Management
1. **Add removal commands** for user servers
2. **Add editing capabilities** for user servers
3. **Add export/import** for sharing user server configs

### User Experience Impact

**Before Enhancement:**
- Users must specify agent for every server addition
- No central registry of user-discovered servers
- Servers from fastmcp.me must be re-added for each agent

**After Enhancement:**
- Users can build personal MCP server registry
- One-time addition, multiple agent usage
- Central discovery of all available servers
- Seamless workflow: discover → add to registry → use in agents

### Success Criteria

1. ✅ `ai-config wizard add-mcp-json` (no agent) adds to registry
2. ✅ `ai-config mcp browse` shows user-added servers
3. ✅ `ai-config wizard setup-mcp <agent>` includes user servers
4. ✅ User servers persist across sessions
5. ✅ Clear distinction between sample and user servers

### Priority: High
This enhancement addresses a key user expectation and completes the MCP server management workflow. The current implementation is 80% complete - this fills the final gap.

---

**Architect Notes:**
- Leverage existing MCPServerConfig and MCPServer models
- Maintain backward compatibility with current registry structure  
- Consider future multi-user scenarios in design
- Ensure atomic operations for registry updates
