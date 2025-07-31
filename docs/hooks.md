---
title: "Custom Hook Development Guide"
description: "Complete guide to developing and managing custom hooks in AI Configurator"
category: "user"
tags: ["hooks", "development", "automation", "customization"]
version: "1.0"
last_updated: "2025-01-31"
related_docs:
  - "docs/configuration.md"
  - "docs/profiles.md"
  - "docs/development/architecture.md"
---

# Custom Hook Development Guide

Hooks in AI Configurator allow you to extend functionality by executing custom code at specific trigger points. This guide covers everything you need to know about creating, configuring, and managing hooks.

## What are Hooks?

Hooks are automated scripts or context providers that execute at specific trigger points:

- **Context Hooks**: Provide additional context to the AI
- **Script Hooks**: Execute commands or scripts
- **Hybrid Hooks**: Combine context and script functionality

### Hook Triggers

Hooks can be triggered at various points:

| Trigger            | Description                | Use Cases                                 |
| ------------------ | -------------------------- | ----------------------------------------- |
| `on_session_start` | When Q chat session begins | Environment setup, context loading        |
| `per_user_message` | Before each user message   | Dynamic context, message preprocessing    |
| `on_file_change`   | When files are modified    | Auto-formatting, validation, testing      |
| `on_project_open`  | When opening a project     | Project-specific setup, dependency checks |
| `on_error`         | When errors occur          | Error logging, recovery actions           |

## Hook Types

### Context Hooks

Provide additional context information to the AI:

```yaml
name: "project-context"
description: "Load project-specific context information"
type: "context"
trigger: "on_session_start"
enabled: true

context:
  sources:
    - "hooks/project-context.md"
    - "README.md"
    - "package.json"
  tags: ["project", "setup"]
  categories: ["development"]
  priority: 5

conditions:
  - file_exists: "package.json"
```

### Script Hooks

Execute commands or scripts:

```yaml
name: "setup-dev-env"
description: "Set up development environment"
type: "script"
trigger: "on_session_start"
enabled: true

script:
  command: "python"
  args: ["scripts/setup-dev.py"]
  working_dir: "."
  timeout: 60
  env:
    DEBUG: "true"
    PROJECT_ROOT: "${PWD}"

conditions:
  - platform: ["linux", "macos"]
    environment:
      NODE_ENV: "development"
```

### Hybrid Hooks

Combine context and script functionality:

```yaml
name: "enhanced-context"
description: "Load context and process it with script"
type: "hybrid"
trigger: "per_user_message"
enabled: true

context:
  sources:
    - "contexts/dynamic-context.md"
  priority: 10

script:
  command: "python"
  args: ["scripts/process-context.py"]
  timeout: 30

conditions:
  - environment:
      ENHANCED_MODE: "true"
```

## Hook Configuration Structure

### Complete Hook Example

```yaml
# Hook identification
name: "comprehensive-hook"
description: "Example of a comprehensive hook configuration"
version: "1.2"
type: "hybrid"
trigger: "on_session_start"
enabled: true
timeout: 45

# Context configuration (for context and hybrid hooks)
context:
  sources:
    - "hooks/comprehensive-hook.md"
    - "contexts/shared-context.md"
    - "project-docs/*.md"

  # Context processing options
  tags: ["comprehensive", "example"]
  categories: ["development", "automation"]
  priority: 10

  # Advanced context options
  processing:
    enable_templates: true
    variable_substitution: true
    markdown_extensions: ["tables", "fenced_code"]

# Script configuration (for script and hybrid hooks)
script:
  command: "python"
  args: ["scripts/comprehensive-script.py", "--mode", "full"]
  working_dir: "."
  timeout: 60

  # Environment variables
  env:
    HOOK_NAME: "comprehensive-hook"
    DEBUG_MODE: "true"
    PROJECT_ROOT: "${PWD}"
    CONFIG_PATH: "${AMAZONQ_CONFIG_DIR}"

# Execution conditions
conditions:
  - platform: ["linux", "macos"]
    environment:
      NODE_ENV: "development"
      COMPREHENSIVE_MODE: "enabled"
    file_exists: "package.json"

  - platform: ["windows"]
    environment:
      DEVELOPMENT: "true"
    file_exists: "requirements.txt"

# Hook metadata
metadata:
  author: "development-team"
  created_date: "2025-01-31"
  tags: ["automation", "development"]
  documentation: "docs/hooks/comprehensive-hook.md"

  # Version history
  version_history:
    - version: "1.0"
      date: "2025-01-15"
      changes: "Initial implementation"
    - version: "1.1"
      date: "2025-01-25"
      changes: "Added Windows support"
    - version: "1.2"
      date: "2025-01-31"
      changes: "Enhanced context processing"
```

## Creating Hooks

### Using AI Configurator CLI

Create hook templates:

```bash
# Create basic context hook
ai-config hooks create my-context-hook --type context

# Create script hook with specific trigger
ai-config hooks create my-script-hook --type script --trigger on_file_change

# Create hybrid hook
ai-config hooks create my-hybrid-hook --type hybrid --trigger per_user_message
```

### Manual Hook Creation

1. **Create hook directory structure:**

```bash
mkdir -p ~/.amazonq/hooks
cd ~/.amazonq/hooks
```

2. **Create YAML configuration:**

```bash
# Create hook configuration
nano my-hook.yaml
```

3. **Create companion files:**

```bash
# For context hooks, create markdown file
nano my-hook.md

# For script hooks, create script file
mkdir -p scripts
nano scripts/my-hook.py
```

## Hook Development Examples

### Context Hook Example

**Configuration (`project-analyzer.yaml`):**

```yaml
name: "project-analyzer"
description: "Analyze project structure and provide context"
type: "context"
trigger: "on_session_start"
enabled: true

context:
  sources:
    - "hooks/project-analyzer.md"
  priority: 8

conditions:
  - file_exists: "package.json"
```

**Context File (`project-analyzer.md`):**

```markdown
---
title: "Project Analysis Context"
tags: ["project", "analysis"]
priority: 8
---

# Project Analysis

## Project Structure

This project appears to be a Node.js application based on the presence of package.json.

## Key Files

- package.json: Contains project dependencies and scripts
- README.md: Project documentation
- src/: Source code directory

## Development Guidelines

- Follow the coding standards defined in .eslintrc.js
- Run tests before committing: `npm test`
- Use semantic versioning for releases

## Common Tasks

- Start development server: `npm run dev`
- Build for production: `npm run build`
- Run tests: `npm test`
- Lint code: `npm run lint`
```

### Script Hook Example

**Configuration (`auto-formatter.yaml`):**

```yaml
name: "auto-formatter"
description: "Automatically format code files on change"
type: "script"
trigger: "on_file_change"
enabled: true

script:
  command: "python"
  args: ["scripts/auto-formatter.py"]
  timeout: 30
  env:
    FORMATTER_CONFIG: "configs/formatter.json"

conditions:
  - file_exists: ".prettierrc"
```

**Script File (`scripts/auto-formatter.py`):**

```python
#!/usr/bin/env python3
"""Auto-formatter hook script."""

import os
import sys
import subprocess
import json
from pathlib import Path

def main():
    """Main formatter function."""
    # Get environment variables
    config_path = os.environ.get('FORMATTER_CONFIG', 'configs/formatter.json')
    changed_file = os.environ.get('CHANGED_FILE', '')

    if not changed_file:
        print("No file specified for formatting")
        return 0

    # Load formatter configuration
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"formats": ["js", "ts", "py", "yaml"]}

    # Check if file should be formatted
    file_path = Path(changed_file)
    if file_path.suffix[1:] not in config.get("formats", []):
        print(f"Skipping {changed_file} - not in format list")
        return 0

    # Format the file
    try:
        if file_path.suffix in ['.js', '.ts']:
            subprocess.run(['prettier', '--write', changed_file], check=True)
        elif file_path.suffix == '.py':
            subprocess.run(['black', changed_file], check=True)
        elif file_path.suffix in ['.yaml', '.yml']:
            subprocess.run(['yamlfmt', '-w', changed_file], check=True)

        print(f"Formatted {changed_file}")
        return 0

    except subprocess.CalledProcessError as e:
        print(f"Error formatting {changed_file}: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"Formatter not found: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Hybrid Hook Example

**Configuration (`intelligent-context.yaml`):**

```yaml
name: "intelligent-context"
description: "Dynamically generate context based on user message"
type: "hybrid"
trigger: "per_user_message"
enabled: true

context:
  sources:
    - "hooks/intelligent-context.md"
  priority: 15

script:
  command: "python"
  args: ["scripts/intelligent-context.py"]
  timeout: 20
  env:
    CONTEXT_DB: "data/context.db"
    AI_MODEL: "gpt-4"

conditions:
  - environment:
      INTELLIGENT_MODE: "enabled"
```

**Context File (`intelligent-context.md`):**

```markdown
---
title: "Intelligent Context"
dynamic: true
---

# Intelligent Context System

This context is dynamically generated based on the user's message and project state.

## Context Generation

The system analyzes:

- User message intent
- Current project files
- Recent changes
- Development patterns

## Available Context Types

- Code analysis
- Documentation references
- Best practices
- Error solutions
```

**Script File (`scripts/intelligent-context.py`):**

```python
#!/usr/bin/env python3
"""Intelligent context generation script."""

import os
import sys
import json
import sqlite3
from pathlib import Path

def analyze_user_message(message):
    """Analyze user message to determine context needs."""
    keywords = {
        'error': ['debugging', 'troubleshooting'],
        'deploy': ['deployment', 'production'],
        'test': ['testing', 'quality'],
        'security': ['security', 'authentication'],
        'performance': ['optimization', 'monitoring']
    }

    message_lower = message.lower()
    relevant_contexts = []

    for keyword, contexts in keywords.items():
        if keyword in message_lower:
            relevant_contexts.extend(contexts)

    return relevant_contexts

def load_project_context():
    """Load relevant project context."""
    project_info = {}

    # Check for common project files
    if Path('package.json').exists():
        project_info['type'] = 'nodejs'
        with open('package.json', 'r') as f:
            package_data = json.load(f)
            project_info['dependencies'] = list(package_data.get('dependencies', {}).keys())

    if Path('requirements.txt').exists():
        project_info['type'] = 'python'
        with open('requirements.txt', 'r') as f:
            project_info['dependencies'] = [line.strip() for line in f if line.strip()]

    return project_info

def generate_context(user_message, project_info):
    """Generate intelligent context based on analysis."""
    context_parts = []

    # Add message-specific context
    relevant_contexts = analyze_user_message(user_message)
    if relevant_contexts:
        context_parts.append(f"## Relevant Context Areas\n{', '.join(relevant_contexts)}")

    # Add project-specific context
    if project_info.get('type'):
        context_parts.append(f"## Project Type\n{project_info['type']}")

    if project_info.get('dependencies'):
        deps = ', '.join(project_info['dependencies'][:5])  # Limit to first 5
        context_parts.append(f"## Key Dependencies\n{deps}")

    return '\n\n'.join(context_parts)

def main():
    """Main function."""
    # Get user message from environment
    user_message = os.environ.get('USER_MESSAGE', '')
    if not user_message:
        print("No user message provided")
        return 0

    # Analyze project and generate context
    project_info = load_project_context()
    context = generate_context(user_message, project_info)

    # Output generated context
    print("Generated Context:")
    print(context)

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Hook Management

### Listing Hooks

View available hooks:

```bash
# List all hooks
ai-config hooks list

# List hooks by type
ai-config hooks list --type context

# List hooks by trigger
ai-config hooks list --trigger on_session_start

# Show detailed hook information
ai-config hooks info hook-name
```

### Testing Hooks

Test hook functionality:

```bash
# Test specific hook
ai-config hooks test my-hook

# Test all hooks for a trigger
ai-config hooks test --trigger on_session_start

# Test with verbose output
ai-config hooks test my-hook --verbose

# Dry run (don't execute, just validate)
ai-config hooks test my-hook --dry-run
```

### Enabling/Disabling Hooks

Control hook execution:

```bash
# Disable hook
ai-config hooks disable my-hook

# Enable hook
ai-config hooks enable my-hook

# Toggle hook state
ai-config hooks toggle my-hook
```

### Hook Validation

Validate hook configurations:

```bash
# Validate specific hook
ai-config hooks validate my-hook

# Validate all hooks
ai-config hooks validate --all

# Strict validation
ai-config hooks validate --strict
```

## Advanced Hook Features

### Conditional Execution

Control when hooks execute:

```yaml
conditions:
  # Platform-specific execution
  - platform: ["linux", "macos"]

  # Environment variable conditions
  - environment:
      NODE_ENV: "development"
      DEBUG: "true"

  # File existence conditions
  - file_exists: "package.json"

  # Combined conditions (AND logic within condition)
  - platform: ["linux"]
    environment:
      DEVELOPMENT: "true"
    file_exists: "Dockerfile"

  # Multiple conditions (OR logic between conditions)
  - platform: ["windows"]
  - environment:
      WINDOWS_MODE: "enabled"
```

### Hook Priorities

Control execution order:

```yaml
# Higher priority executes first
context:
  priority: 10 # Executes before priority 5

# In profile configuration
hooks:
  on_session_start:
    - name: "first-hook"
      priority: 1
    - name: "second-hook"
      priority: 5
    - name: "third-hook"
      priority: 10
```

### Environment Variables

Access system and custom environment variables:

```yaml
script:
  env:
    # System variables
    PROJECT_ROOT: "${PWD}"
    CONFIG_DIR: "${AMAZONQ_CONFIG_DIR}"
    HOME_DIR: "${HOME}"

    # Custom variables
    HOOK_NAME: "my-hook"
    DEBUG_MODE: "true"
    API_ENDPOINT: "https://api.example.com"

    # Conditional variables
    LOG_LEVEL: "${DEBUG:-INFO}"
    TIMEOUT: "${HOOK_TIMEOUT:-30}"
```

### Template Processing

Use templates in context files:

```markdown
---
title: "Dynamic Context"
template: true
---

# Project: {{ project_name }}

## Current Environment

- Platform: {{ platform }}
- User: {{ user }}
- Date: {{ current_date }}

## Project Information

{% if project_type == "nodejs" %}
This is a Node.js project with the following dependencies:
{% for dep in dependencies %}

- {{ dep }}
  {% endfor %}
  {% endif %}

## Custom Variables

- Debug Mode: {{ debug_mode | default("false") }}
- Environment: {{ environment | default("development") }}
```

## Hook Best Practices

### Development Guidelines

1. **Keep hooks focused**: Each hook should have a single, clear purpose
2. **Handle errors gracefully**: Always include error handling in scripts
3. **Use appropriate timeouts**: Set reasonable timeout values
4. **Test thoroughly**: Test hooks in different environments
5. **Document behavior**: Include clear descriptions and examples

### Performance Considerations

1. **Optimize execution time**: Keep hook execution fast
2. **Cache results**: Cache expensive operations when possible
3. **Use conditions wisely**: Avoid unnecessary hook executions
4. **Limit resource usage**: Monitor memory and CPU usage

### Security Best Practices

1. **Validate inputs**: Always validate user inputs and environment variables
2. **Use secure paths**: Avoid using user-controlled paths
3. **Limit permissions**: Run hooks with minimal required permissions
4. **Sanitize outputs**: Clean sensitive information from outputs

### Maintenance

1. **Version your hooks**: Use semantic versioning
2. **Track dependencies**: Document external dependencies
3. **Regular testing**: Test hooks periodically
4. **Update documentation**: Keep documentation current

## Troubleshooting Hooks

### Common Issues

#### Hook Not Executing

**Symptoms:**

- Hook doesn't run at expected trigger
- No output or logs from hook
- Hook appears disabled

**Solutions:**

```bash
# Check hook status
ai-config hooks list

# Validate hook configuration
ai-config hooks validate my-hook

# Test hook manually
ai-config hooks test my-hook

# Check conditions
ai-config hooks info my-hook
```

#### Script Execution Errors

**Symptoms:**

- Script fails with error codes
- Permission denied errors
- Command not found errors

**Solutions:**

```bash
# Check script permissions
ls -la scripts/my-script.py
chmod +x scripts/my-script.py

# Test script manually
python scripts/my-script.py

# Check environment variables
env | grep HOOK
```

#### Context Loading Issues

**Symptoms:**

- Context files not found
- Empty context loaded
- Template processing errors

**Solutions:**

```bash
# Check file paths
ls -la hooks/my-context.md

# Validate markdown syntax
ai-config validate --component contexts

# Test template processing
ai-config hooks test my-hook --verbose
```

### Debug Mode

Enable detailed logging:

```yaml
script:
  env:
    DEBUG: "true"
    LOG_LEVEL: "DEBUG"
    HOOK_DEBUG: "true"
```

```bash
# Run with debug logging
export AI_CONFIGURATOR_LOG_LEVEL=DEBUG
ai-config hooks test my-hook
```

### Hook Monitoring

Monitor hook performance:

```bash
# View hook execution logs
ai-config logs --component hooks

# Monitor hook performance
ai-config hooks monitor

# Get hook statistics
ai-config hooks stats
```

## Integration with Profiles

### Profile Hook Configuration

Reference hooks in profiles:

```yaml
# In profile configuration
hooks:
  on_session_start:
    - name: "setup-environment"
      enabled: true
      config:
        profile_specific: true

    - name: "load-project-context"
      enabled: true
      priority: 5

  per_user_message:
    - name: "enhance-context"
      enabled: true
      config:
        enhancement_level: "high"
```

### Profile-Specific Hooks

Create hooks that adapt to profiles:

```yaml
# Hook configuration
name: "profile-aware-hook"
type: "script"
trigger: "on_session_start"

script:
  command: "python"
  args: ["scripts/profile-aware.py"]
  env:
    CURRENT_PROFILE: "${ACTIVE_PROFILE}"
    PROFILE_CONFIG: "${AMAZONQ_CONFIG_DIR}/profiles/${ACTIVE_PROFILE}.yaml"
```

This comprehensive guide should help you create powerful, custom hooks to extend AI Configurator's functionality. Remember to test your hooks thoroughly and follow best practices for security and performance.
