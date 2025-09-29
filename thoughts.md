# Thoughts on Adding MCP Configuration per Role

## Current State
- Roles are defined via markdown files in `library/roles/`
- Each role has specific context and capabilities
- Configuration is currently done via command line tools

## Proposed Enhancement
Add `mcp.json` files for each role to make them self-contained with their required MCP servers.

## Benefits
1. **Self-contained roles**: Each role includes its required tools and servers
2. **Portability**: Roles can be shared with all dependencies defined
3. **Declarative configuration**: No need for manual CLI setup
4. **Version control**: MCP configurations tracked alongside role definitions
5. **Consistency**: Standardized way to define role capabilities

## Implementation Plan
1. Create `mcp.json` template based on existing template
2. Add role-specific MCP configurations
3. Update role structure to include both `.md` and `mcp.json`
4. Consider integration with the agent manager

## Example Structure
```
library/roles/software-engineer/
├── software-engineer.md
└── mcp.json
```

This aligns with Q CLI's agent-based MCP configuration approach.
