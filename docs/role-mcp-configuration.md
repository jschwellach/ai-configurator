# Role MCP Configuration

This document describes how to configure MCP (Model Context Protocol) servers for each role in the AI configurator.

## Overview

Each role can now include an `mcp.json` file alongside its markdown definition to specify:
- Required MCP servers
- Tool permissions and settings
- Role-specific configurations

This makes roles self-contained and eliminates the need for manual CLI configuration.

## File Structure

```
library/roles/role-name/
├── role-name.md      # Role definition and context
└── mcp.json          # MCP server configuration
```

## Configuration Format

The `mcp.json` file follows Q CLI's agent configuration format:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["mcp-package-name"],
      "env": {
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": ["safe-tool-1", "safe-tool-2"]
    }
  },
  "toolsSettings": {
    "fs_write": {
      "allowedPaths": ["./role-specific/**"]
    },
    "@server-name/tool-name": {
      "custom-setting": "value"
    }
  },
  "allowedTools": [
    "fs_read",
    "@server-name/tool-name"
  ]
}
```

## Key Sections

### mcpServers
Defines the MCP servers required by this role:
- `command`: How to start the server (usually "uvx")
- `args`: Server package and arguments
- `env`: Environment variables
- `autoApprove`: Tools that don't require user confirmation

### toolsSettings
Configures permissions and settings for tools:
- Built-in tools: `fs_read`, `fs_write`, `execute_bash`, `use_aws`
- MCP tools: `@server-name/tool-name`

### allowedTools
Lists tools the role can use without prompting.

## Examples

### Software Engineer
Needs git operations, file system access, and testing tools:
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-git"],
      "autoApprove": ["git_status", "git_log", "git_diff"]
    }
  },
  "toolsSettings": {
    "fs_write": {
      "allowedPaths": ["./src/**", "./tests/**"]
    },
    "execute_bash": {
      "allowedCommands": ["npm test", "python -m pytest"]
    }
  }
}
```

### Product Owner
Focuses on documentation and requirements:
```json
{
  "toolsSettings": {
    "fs_write": {
      "allowedPaths": ["./docs/**", "./requirements/**"]
    },
    "fs_read": {
      "allowedPaths": ["./docs/**", "./README.md"]
    }
  },
  "allowedTools": ["fs_read", "fs_write", "thinking"]
}
```

## Benefits

1. **Self-contained**: Roles include all required dependencies
2. **Portable**: Easy to share and version control
3. **Consistent**: Standardized configuration format
4. **Secure**: Role-specific permissions and restrictions
5. **Maintainable**: Clear separation of concerns

## Integration

The AI configurator can use these files to:
1. Generate Q CLI agent configurations
2. Install required MCP servers
3. Set up role-specific permissions
4. Validate role dependencies

## Template

Use `templates/role-mcp-template.json` as a starting point for new roles.

## References

- [Q CLI Built-in Tools](https://github.com/aws/amazon-q-developer-cli/blob/main/docs/built-in-tools.md)
- [Q CLI Agent File Locations](https://github.com/aws/amazon-q-developer-cli/blob/main/docs/agent-file-locations.md)
