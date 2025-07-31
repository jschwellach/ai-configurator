---
title: "Configuration Reference"
description: "Complete configuration reference for AI Configurator"
category: "user"
tags: ["configuration", "reference", "setup"]
version: "1.0"
last_updated: "2025-01-31"
related_docs:
  - "docs/profiles.md"
  - "docs/mcp-servers.md"
  - "docs/hooks.md"
---

# Configuration Reference

AI Configurator provides flexible configuration management for Amazon Q CLI through both YAML and JSON formats. This guide covers all configuration options and file structures.

## Configuration Directory Structure

AI Configurator creates and manages configurations in your Amazon Q CLI configuration directory:

```
~/.amazonq/
├── profiles/                    # Profile configurations
│   ├── default.yaml            # YAML profile format
│   ├── developer.yaml          # Custom profiles
│   └── legacy-profile/         # JSON profile format (legacy)
│       ├── context.json
│       └── hooks.json
├── contexts/                   # Context files
│   ├── aws-best-practices.md
│   ├── development-guidelines.md
│   └── custom-context.md
├── hooks/                      # Hook configurations
│   ├── setup-dev-env.yaml
│   ├── context-enhancer.yaml
│   └── custom-hook.md
├── mcp.json                    # MCP server configuration
├── global_context.json        # Global context settings
└── backups/                    # Automatic backups
    └── backup_2025-01-31/
```

## Configuration Formats

### YAML Format (Recommended)

YAML is the preferred format for new configurations, offering better readability and advanced features:

```yaml
# Profile configuration example
name: "developer"
description: "Development environment profile"
version: "1.0"

contexts:
  - "contexts/development-guidelines.md"
  - "contexts/aws-best-practices.md"
  - "contexts/custom/*.md"

hooks:
  on_session_start:
    - name: "setup-dev-env"
      enabled: true
      config:
        auto_install: true
  per_user_message:
    - name: "context-enhancer"
      enabled: true

mcp_servers:
  - "awslabs.core-mcp-server"
  - "fetch"

settings:
  auto_backup: true
  validation_level: "normal"
  hot_reload: true
  cache_enabled: true

metadata:
  created_date: "2025-01-31"
  author: "ai-configurator"
```

### JSON Format (Legacy)

JSON format is supported for backward compatibility:

```json
{
  "paths": [
    "contexts/development-guidelines.md",
    "contexts/aws-best-practices.md"
  ],
  "description": "Development environment profile"
}
```

## Global Configuration

### MCP Server Configuration (`mcp.json`)

Configure Model Context Protocol servers:

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
    },
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

#### MCP Server Options

- **command**: Executable command to run the server
- **args**: Command line arguments array
- **env**: Environment variables object
- **disabled**: Boolean to enable/disable the server
- **autoApprove**: Array of tool names to auto-approve

### Global Context Configuration (`global_context.json`)

Set global context preferences:

```json
{
  "default_contexts": ["contexts/aws-best-practices.md"],
  "context_priority": "profile_first",
  "max_context_size": 50000,
  "auto_reload": true,
  "validation": {
    "strict_mode": false,
    "check_file_existence": true
  }
}
```

## Profile Configuration

### YAML Profile Structure

```yaml
# Required fields
name: "profile-name" # Profile identifier
description: "Profile description"
version: "1.0" # Configuration version

# Context configuration
contexts:
  - "contexts/specific-context.md"
  - "contexts/shared/*.md" # Glob patterns supported
  - "contexts/conditional.md" # Conditional loading

# Hook configuration
hooks:
  on_session_start: # Trigger type
    - name: "hook-name" # Hook reference
      enabled: true # Enable/disable
      config: # Hook-specific config
        parameter: "value"
  per_user_message:
    - name: "another-hook"
      enabled: false
  on_file_change:
    - name: "file-watcher"
      enabled: true

# MCP server references
mcp_servers:
  - "server-name-1"
  - "server-name-2"

# Profile settings
settings:
  auto_backup: true # Create backups automatically
  validation_level: "normal" # normal, strict, minimal
  hot_reload: true # Reload on file changes
  cache_enabled: true # Enable configuration caching
  timeout: 30 # Operation timeout in seconds

# Metadata (optional)
metadata:
  created_date: "2025-01-31"
  author: "username"
  tags: ["development", "aws"]
  notes: "Custom profile for development work"
```

### Context Path Patterns

Context paths support various patterns:

```yaml
contexts:
  # Specific files
  - "contexts/aws-best-practices.md"

  # Glob patterns
  - "contexts/development/*.md"
  - "contexts/**/*.md"

  # Conditional contexts (advanced)
  - path: "contexts/platform-specific.md"
    condition:
      platform: ["linux", "macos"]
      environment:
        NODE_ENV: "development"
```

### Hook References

Hook references can be simple strings or detailed configurations:

```yaml
hooks:
  on_session_start:
    # Simple reference
    - name: "basic-hook"

    # Detailed configuration
    - name: "advanced-hook"
      enabled: true
      priority: 10
      config:
        custom_param: "value"
        timeout: 60
      conditions:
        - platform: ["linux"]
          environment:
            DEBUG: "true"
```

## Settings Reference

### Profile Settings

| Setting            | Type    | Default           | Description                                    |
| ------------------ | ------- | ----------------- | ---------------------------------------------- |
| `auto_backup`      | boolean | `true`            | Create automatic backups before changes        |
| `validation_level` | string  | `"normal"`        | Validation strictness: minimal, normal, strict |
| `hot_reload`       | boolean | `true`            | Automatically reload on file changes           |
| `cache_enabled`    | boolean | `true`            | Enable configuration caching                   |
| `timeout`          | integer | `30`              | Default timeout for operations (seconds)       |
| `max_context_size` | integer | `50000`           | Maximum context file size in characters        |
| `context_priority` | string  | `"profile_first"` | Context loading priority                       |

### Validation Levels

- **minimal**: Basic syntax validation only
- **normal**: Standard validation with warnings for missing references
- **strict**: Comprehensive validation with errors for any issues

## Environment Variables

AI Configurator respects these environment variables:

| Variable                           | Description                       | Default                    |
| ---------------------------------- | --------------------------------- | -------------------------- |
| `AMAZONQ_CONFIG_DIR`               | Override default config directory | `~/.amazonq`               |
| `AI_CONFIGURATOR_LOG_LEVEL`        | Logging level                     | `INFO`                     |
| `AI_CONFIGURATOR_CACHE_DIR`        | Cache directory                   | `~/.cache/ai-configurator` |
| `AI_CONFIGURATOR_BACKUP_RETENTION` | Backup retention days             | `30`                       |

## Configuration Migration

### Automatic Migration

AI Configurator automatically detects and migrates configurations:

```bash
# Check for migration opportunities
ai-config migrate check

# Migrate JSON profiles to YAML
ai-config migrate profiles --to-yaml

# Migrate all configurations
ai-config migrate all --backup
```

### Manual Migration

Convert individual profiles:

```bash
# Convert specific profile
ai-config profile convert my-profile --to-format yaml --backup

# Validate after conversion
ai-config profile validate my-profile
```

## Configuration Validation

### Validation Commands

```bash
# Validate all configurations
ai-config validate

# Validate specific profile
ai-config profile validate developer

# Validate with strict checking
ai-config validate --strict

# Check configuration status
ai-config status
```

### Common Validation Issues

1. **Missing Context Files**

   ```
   Warning: Context file not found: contexts/missing-file.md
   ```

   Solution: Create the missing file or remove the reference

2. **Invalid Hook References**

   ```
   Error: Hook 'non-existent-hook' not found
   ```

   Solution: Create the hook or fix the reference

3. **MCP Server Configuration**
   ```
   Warning: MCP server 'unknown-server' not configured
   ```
   Solution: Add server to MCP configuration or remove reference

## Best Practices

### Organization

1. **Use descriptive profile names**: `developer-python`, `aws-architect`
2. **Group related contexts**: Keep similar contexts in subdirectories
3. **Version your configurations**: Use semantic versioning in profiles
4. **Document custom configurations**: Add descriptions and metadata

### Performance

1. **Limit context file sizes**: Keep individual files under 10KB
2. **Use specific paths**: Avoid overly broad glob patterns
3. **Enable caching**: Keep `cache_enabled: true` for better performance
4. **Regular cleanup**: Remove unused profiles and contexts

### Security

1. **Avoid sensitive data**: Don't store secrets in configuration files
2. **Use environment variables**: For dynamic or sensitive values
3. **Regular backups**: Enable `auto_backup` for important configurations
4. **Validate regularly**: Run validation checks periodically

## Troubleshooting

### Common Issues

1. **Configuration not loading**

   - Check file permissions
   - Validate YAML/JSON syntax
   - Verify file paths

2. **Hooks not executing**

   - Check hook configuration
   - Verify hook file exists
   - Review hook conditions

3. **Context files not found**
   - Verify file paths are relative to config directory
   - Check for typos in file names
   - Ensure files exist and are readable

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export AI_CONFIGURATOR_LOG_LEVEL=DEBUG
ai-config status
```

### Configuration Reset

Reset to default configuration:

```bash
# Create backup first
ai-config backup create "before-reset"

# Reset to defaults
ai-config reset --confirm

# Restore from backup if needed
ai-config backup restore backup-id
```

## Advanced Configuration

### Custom Context Processing

Configure advanced context processing:

```yaml
settings:
  context_processing:
    markdown_extensions: ["tables", "fenced_code"]
    frontmatter_processing: true
    variable_substitution: true
    template_engine: "jinja2"
```

### Hook Conditions

Advanced hook conditions:

```yaml
hooks:
  on_session_start:
    - name: "platform-specific"
      conditions:
        - platform: ["linux", "macos"]
          environment:
            DEVELOPMENT: "true"
          file_exists: "package.json"
```

### Dynamic Configuration

Use environment variable substitution:

```yaml
contexts:
  - "contexts/${ENVIRONMENT:-development}/*.md"

settings:
  timeout: ${TIMEOUT:-30}
  cache_enabled: ${CACHE_ENABLED:-true}
```

## Configuration Schema

For advanced users, AI Configurator provides JSON schemas for validation:

- Profile schema: `schemas/profile.schema.json`
- Hook schema: `schemas/hook.schema.json`
- MCP schema: `schemas/mcp.schema.json`

Use with your editor for autocompletion and validation.
