---
title: "MCP Server Setup Guide"
description: "Complete guide to setting up and managing Model Context Protocol servers"
category: "user"
tags: ["mcp", "servers", "setup", "configuration"]
version: "1.0"
last_updated: "2025-01-31"
related_docs:
  - "docs/configuration.md"
  - "docs/profiles.md"
  - "docs/troubleshooting.md"
---

# MCP Server Setup Guide

Model Context Protocol (MCP) servers extend AI Configurator's capabilities by providing specialized tools and context. This guide covers everything you need to know about setting up, configuring, and managing MCP servers.

## What are MCP Servers?

MCP servers are external processes that provide:

- **Tools**: Functions the AI can call to perform actions
- **Resources**: Access to external data sources
- **Context**: Additional information for AI responses

Common MCP servers include:

- **AWS Documentation**: Access to AWS service documentation
- **File System**: File operations and content access
- **Web Fetch**: HTTP requests and web content retrieval
- **Git**: Version control operations
- **Database**: Query and data access tools

## Prerequisites

### Install UV and UVX

Most MCP servers use `uvx` for execution, which requires `uv` (Python package manager):

#### macOS (Homebrew)

```bash
brew install uv
```

#### Linux/macOS (curl)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Python pip

```bash
pip install uv
```

Verify installation:

```bash
uv --version
uvx --version
```

### Amazon Q CLI

Ensure Amazon Q CLI is installed and configured:

```bash
q --version
q auth login
```

## MCP Configuration Structure

MCP servers are configured in `~/.amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package-name@version"],
      "env": {
        "ENVIRONMENT_VAR": "value"
      },
      "disabled": false,
      "autoApprove": ["tool1", "tool2"]
    }
  }
}
```

### Configuration Options

| Option        | Type    | Description                                      |
| ------------- | ------- | ------------------------------------------------ |
| `command`     | string  | Executable command (usually `uvx`)               |
| `args`        | array   | Command arguments including package name         |
| `env`         | object  | Environment variables for the server             |
| `disabled`    | boolean | Enable/disable the server                        |
| `autoApprove` | array   | Tools to automatically approve without prompting |

## Core MCP Servers

### AWS Documentation Server

Access comprehensive AWS service documentation:

```json
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Capabilities:**

- Search AWS service documentation
- Get detailed service information
- Access API references
- Find best practices and examples

**Usage Example:**

```
User: How do I configure an S3 bucket for static website hosting?
AI: [Uses AWS docs server to fetch current S3 static hosting documentation]
```

### Core MCP Server

Essential AWS tools and utilities:

```json
{
  "mcpServers": {
    "awslabs.core-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.core-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Capabilities:**

- AWS CLI command generation
- Resource management helpers
- Configuration validation
- Common AWS operations

### CDK MCP Server

AWS Cloud Development Kit support:

```json
{
  "mcpServers": {
    "awslabs.cdk-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.cdk-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Capabilities:**

- CDK construct examples
- Stack templates
- Best practices guidance
- Deployment helpers

### Fetch Server

HTTP requests and web content access:

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Capabilities:**

- HTTP GET/POST requests
- Web page content retrieval
- API endpoint testing
- Content parsing

## Server Groups and Profiles

AI Configurator organizes MCP servers into groups for easy management:

### Core Group (`configs/mcp-servers/core.json`)

Essential servers for basic functionality:

- `awslabs.core-mcp-server`
- `awslabs.aws-documentation-mcp-server`
- `awslabs.cdk-mcp-server`
- `fetch`

### Development Group (`configs/mcp-servers/development.json`)

Development-focused servers:

- `filesystem`
- `git`
- `database`
- `testing-tools`

### Specialized Group (`configs/mcp-servers/specialized.json`)

Domain-specific servers:

- `kubernetes`
- `terraform`
- `monitoring`
- `security-scanner`

## Installation and Setup

### Using AI Configurator

Install with specific server groups:

```bash
# Install with core servers
ai-config install --mcp-servers core

# Install with multiple groups
ai-config install --mcp-servers core,development

# Install all available servers
ai-config install --mcp-servers all
```

### Manual Configuration

1. **Create or edit MCP configuration:**

```bash
# Edit MCP configuration
nano ~/.amazonq/mcp.json
```

2. **Add server configuration:**

```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "uvx",
      "args": ["my-mcp-package@latest"],
      "env": {
        "API_KEY": "your-api-key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

3. **Test the configuration:**

```bash
ai-config validate
```

4. **Restart Amazon Q CLI:**

```bash
# The servers will be loaded on next Q session
q chat
```

## Server Management

### Listing Servers

View configured servers:

```bash
# List all configured servers
ai-config mcp list

# Show server status
ai-config mcp status

# Show detailed server information
ai-config mcp info server-name
```

### Enabling/Disabling Servers

```bash
# Disable a server
ai-config mcp disable server-name

# Enable a server
ai-config mcp enable server-name

# Toggle server state
ai-config mcp toggle server-name
```

### Testing Servers

Verify server functionality:

```bash
# Test specific server
ai-config mcp test server-name

# Test all servers
ai-config mcp test --all

# Test with verbose output
ai-config mcp test server-name --verbose
```

## Custom MCP Servers

### Creating a Custom Server

1. **Create server package structure:**

```
my-mcp-server/
├── pyproject.toml
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       └── server.py
└── README.md
```

2. **Define server capabilities:**

```python
# src/my_mcp_server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("my-custom-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="custom_tool",
            description="My custom tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "custom_tool":
        result = f"Processed: {arguments.get('input', '')}"
        return [TextContent(type="text", text=result)]
```

3. **Configure pyproject.toml:**

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
dependencies = ["mcp"]

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"
```

4. **Publish and configure:**

```bash
# Publish to PyPI or install locally
pip install -e .

# Add to MCP configuration
{
  "mcpServers": {
    "my-custom-server": {
      "command": "my-mcp-server",
      "args": [],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Local Development Server

For development and testing:

```json
{
  "mcpServers": {
    "dev-server": {
      "command": "python",
      "args": ["/path/to/my-server.py"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
      },
      "disabled": false,
      "autoApprove": ["debug_tool"]
    }
  }
}
```

## Environment Configuration

### Environment Variables

Common environment variables for MCP servers:

```json
{
  "mcpServers": {
    "server-name": {
      "env": {
        "LOG_LEVEL": "INFO",
        "FASTMCP_LOG_LEVEL": "ERROR",
        "API_KEY": "your-api-key",
        "BASE_URL": "https://api.example.com",
        "TIMEOUT": "30",
        "CACHE_ENABLED": "true"
      }
    }
  }
}
```

### Secure Configuration

Store sensitive data securely:

```bash
# Use environment variables
export MCP_API_KEY="your-secret-key"
```

```json
{
  "mcpServers": {
    "secure-server": {
      "env": {
        "API_KEY": "${MCP_API_KEY}"
      }
    }
  }
}
```

## Auto-Approval Configuration

Configure tools to run without user confirmation:

```json
{
  "mcpServers": {
    "trusted-server": {
      "autoApprove": ["read_file", "list_directory", "get_documentation"]
    }
  }
}
```

### Auto-Approval Best Practices

1. **Only approve read-only operations**
2. **Avoid auto-approving destructive actions**
3. **Review auto-approved tools regularly**
4. **Use specific tool names, not wildcards**

## Troubleshooting

### Common Issues

#### Server Not Starting

**Symptoms:**

- Server appears offline in status
- Tools not available in Q chat
- Connection errors in logs

**Solutions:**

```bash
# Check server configuration
ai-config mcp validate

# Test server manually
uvx package-name@latest

# Check logs
ai-config logs --component mcp

# Verify uvx installation
uvx --version
```

#### Permission Errors

**Symptoms:**

- "Permission denied" errors
- Server fails to execute commands
- File access issues

**Solutions:**

```bash
# Check file permissions
ls -la ~/.amazonq/mcp.json

# Fix permissions
chmod 600 ~/.amazonq/mcp.json

# Check uvx permissions
which uvx
ls -la $(which uvx)
```

#### Network Issues

**Symptoms:**

- Package download failures
- Connection timeouts
- DNS resolution errors

**Solutions:**

```bash
# Test network connectivity
curl -I https://pypi.org

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Use specific package versions
"args": ["package-name@1.2.3"]
```

#### Environment Variable Issues

**Symptoms:**

- Authentication failures
- Missing configuration
- Server behaves unexpectedly

**Solutions:**

```bash
# Check environment variables
env | grep MCP

# Test variable expansion
echo $MCP_API_KEY

# Use absolute paths
"env": {
  "CONFIG_PATH": "/absolute/path/to/config"
}
```

### Debug Mode

Enable detailed logging:

```json
{
  "mcpServers": {
    "debug-server": {
      "env": {
        "LOG_LEVEL": "DEBUG",
        "FASTMCP_LOG_LEVEL": "DEBUG",
        "MCP_DEBUG": "true"
      }
    }
  }
}
```

### Server Health Checks

Monitor server health:

```bash
# Check all servers
ai-config mcp health

# Monitor specific server
ai-config mcp monitor server-name

# Get server metrics
ai-config mcp metrics
```

## Advanced Configuration

### Conditional Server Loading

Load servers based on conditions:

```json
{
  "mcpServers": {
    "development-only": {
      "command": "uvx",
      "args": ["dev-tools@latest"],
      "env": {
        "NODE_ENV": "development"
      },
      "disabled": false,
      "conditions": {
        "environment": {
          "NODE_ENV": "development"
        }
      }
    }
  }
}
```

### Server Profiles

Different server configurations for different profiles:

```yaml
# In profile configuration
mcp_servers:
  - "awslabs.core-mcp-server"
  - "fetch"

# Development profile
mcp_servers:
  - "awslabs.core-mcp-server"
  - "fetch"
  - "filesystem"
  - "git"

# Production support profile
mcp_servers:
  - "awslabs.core-mcp-server"
  - "awslabs.aws-documentation-mcp-server"
  - "monitoring-tools"
```

### Load Balancing and Failover

Configure multiple instances:

```json
{
  "mcpServers": {
    "primary-server": {
      "command": "uvx",
      "args": ["server@latest"],
      "env": { "INSTANCE": "primary" },
      "priority": 1
    },
    "backup-server": {
      "command": "uvx",
      "args": ["server@latest"],
      "env": { "INSTANCE": "backup" },
      "priority": 2,
      "fallback_for": "primary-server"
    }
  }
}
```

## Best Practices

### Performance Optimization

1. **Use specific versions**: Pin server versions for consistency
2. **Enable caching**: Use server-side caching when available
3. **Limit auto-approval**: Only auto-approve necessary tools
4. **Monitor resource usage**: Track server memory and CPU usage

### Security

1. **Principle of least privilege**: Only enable necessary servers
2. **Secure credentials**: Use environment variables for secrets
3. **Regular updates**: Keep servers updated to latest versions
4. **Audit auto-approvals**: Review auto-approved tools regularly

### Maintenance

1. **Regular testing**: Test servers periodically
2. **Monitor logs**: Check server logs for issues
3. **Update configurations**: Keep configurations current
4. **Backup settings**: Include MCP config in backups

### Documentation

1. **Document custom servers**: Maintain documentation for custom implementations
2. **Track dependencies**: Document server dependencies and requirements
3. **Version control**: Track configuration changes
4. **Share configurations**: Share working configurations with team members

This comprehensive guide should help you effectively set up and manage MCP servers in AI Configurator. Remember to test your configurations thoroughly and monitor server performance regularly.
