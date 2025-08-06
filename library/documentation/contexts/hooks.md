---
title: "Custom Hook Development Guide"
description: "Complete guide to developing and managing custom hooks in AI Configurator"
category: "user"
tags: ["hooks", "development", "automation", "customization"]
version: "1.1"
last_updated: "2025-07-31"
related_docs:
  - "docs/configuration.md"
  - "docs/profiles.md"
  - "docs/development/architecture.md"
---

# Custom Hook Development Guide

Hooks in AI Configurator allow you to extend functionality by executing custom scripts at specific trigger points. This guide covers everything you need to know about creating, configuring, and managing hooks.

## What are Hooks?

Hooks are automated scripts that execute at specific trigger points in your AI Configurator workflow. The current implementation supports two main types of hooks:

- **Python Hooks**: Python scripts that can perform complex operations, data processing, and integrations
- **Shell Hooks**: Bash/shell scripts for system operations, file processing, and command execution

### Hook Triggers

Hooks can be triggered at various points (implementation varies by hook type):

| Trigger            | Description                | Use Cases                                 |
| ------------------ | -------------------------- | ----------------------------------------- |
| `on_session_start` | When Q chat session begins | Environment setup, context loading        |
| `per_user_message` | Before each user message   | Dynamic context, message preprocessing    |
| `on_file_change`   | When files are modified    | Auto-formatting, validation, testing      |
| `on_project_open`  | When opening a project     | Project-specific setup, dependency checks |
| `on_error`         | When errors occur          | Error logging, recovery actions           |

## Creating Hooks

### Using AI Configurator CLI

The easiest way to create hooks is using the built-in CLI commands:

```bash
# Create a Python hook (default)
ai-config hooks create my-python-hook

# Create a Python hook explicitly
ai-config hooks create my-python-hook --type python

# Create a shell script hook
ai-config hooks create my-shell-hook --type shell
```

This will create template files in your hooks directory (`~/.aws/amazonq/hooks/`) with helpful boilerplate code.

### Python Hook Template

When you create a Python hook, you get a template like this:

```python
#!/usr/bin/env python3
"""
my-python-hook Hook Script

This is an auto-generated hook template.
Customize this script to perform your desired actions.
"""

import sys
import os
from pathlib import Path

def main():
    """Main hook function."""
    print(f"Executing my-python-hook hook...")
    
    # Access environment variables
    config_dir = os.getenv("AMAZONQ_CONFIG_DIR", "")
    hooks_dir = os.getenv("AI_CONFIGURATOR_HOOKS_DIR", "")
    hook_name = os.getenv("HOOK_NAME", "my-python-hook")
    
    print(f"Config directory: {config_dir}")
    print(f"Hooks directory: {hooks_dir}")
    print(f"Hook name: {hook_name}")
    
    # Add your custom logic here
    # Example: Read configuration files, process data, etc.
    
    # Return success
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Shell Hook Template

When you create a shell hook, you get a template like this:

```bash
#!/bin/bash
#
# my-shell-hook Hook Script
#
# This is an auto-generated hook template.
# Customize this script to perform your desired actions.
#

set -e  # Exit on error

echo "Executing my-shell-hook hook..."

# Access environment variables
echo "Config directory: $AMAZONQ_CONFIG_DIR"
echo "Hooks directory: $AI_CONFIGURATOR_HOOKS_DIR"
echo "Hook name: $HOOK_NAME"

# Add your custom logic here
# Example: Process files, run commands, etc.

echo "my-shell-hook hook completed successfully"
exit 0
```

### Available Environment Variables

All hooks have access to these environment variables:

- `AMAZONQ_CONFIG_DIR`: Path to the Amazon Q configuration directory
- `AI_CONFIGURATOR_HOOKS_DIR`: Path to the hooks directory
- `HOOK_NAME`: Name of the current hook being executed

## Practical Hook Examples

### Example 1: Project Information Hook

Create a Python hook that gathers project information:

```bash
ai-config hooks create project-info --type python
```

Edit the generated `project-info.py`:

```python
#!/usr/bin/env python3
"""
Project Information Hook

Gathers and displays project information for AI context.
"""

import sys
import os
import json
from pathlib import Path

def get_project_type():
    """Determine project type based on files present."""
    if Path('package.json').exists():
        return 'nodejs'
    elif Path('requirements.txt').exists() or Path('pyproject.toml').exists():
        return 'python'
    elif Path('Cargo.toml').exists():
        return 'rust'
    elif Path('go.mod').exists():
        return 'go'
    elif Path('pom.xml').exists():
        return 'java'
    else:
        return 'unknown'

def get_dependencies():
    """Get project dependencies."""
    project_type = get_project_type()
    
    if project_type == 'nodejs' and Path('package.json').exists():
        with open('package.json', 'r') as f:
            data = json.load(f)
            deps = list(data.get('dependencies', {}).keys())
            dev_deps = list(data.get('devDependencies', {}).keys())
            return {'dependencies': deps, 'devDependencies': dev_deps}
    
    elif project_type == 'python' and Path('requirements.txt').exists():
        with open('requirements.txt', 'r') as f:
            deps = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
            return {'dependencies': deps}
    
    return {}

def main():
    """Main hook function."""
    print("=== Project Information ===")
    
    # Basic project info
    project_type = get_project_type()
    print(f"Project Type: {project_type}")
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Project Directory: {current_dir}")
    
    # Get dependencies
    deps = get_dependencies()
    if deps:
        print("Dependencies:")
        for dep_type, dep_list in deps.items():
            print(f"  {dep_type}: {', '.join(dep_list[:5])}")  # Show first 5
            if len(dep_list) > 5:
                print(f"    ... and {len(dep_list) - 5} more")
    
    # Check for common files
    common_files = ['README.md', 'LICENSE', '.gitignore', 'Dockerfile']
    present_files = [f for f in common_files if Path(f).exists()]
    if present_files:
        print(f"Common files present: {', '.join(present_files)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Example 2: Git Status Hook

Create a shell hook that shows git status:

```bash
ai-config hooks create git-status --type shell
```

Edit the generated `git-status.sh`:

```bash
#!/bin/bash
#
# Git Status Hook
#
# Shows current git repository status
#

set -e

echo "=== Git Repository Status ==="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Not in a git repository"
    exit 0
fi

# Show current branch
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# Show status
echo ""
echo "Repository status:"
git status --porcelain | head -10

# Show recent commits
echo ""
echo "Recent commits:"
git log --oneline -5

# Show remote info
echo ""
echo "Remote information:"
git remote -v

echo "Git status check completed"
exit 0
```

### Example 3: Environment Setup Hook

Create a Python hook for environment setup:

```bash
ai-config hooks create env-setup --type python
```

Edit the generated `env-setup.py`:

```python
#!/usr/bin/env python3
"""
Environment Setup Hook

Sets up development environment and checks prerequisites.
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def check_command(command):
    """Check if a command is available."""
    return shutil.which(command) is not None

def check_prerequisites():
    """Check for required tools."""
    tools = {
        'git': 'Git version control',
        'node': 'Node.js runtime',
        'npm': 'Node package manager',
        'python': 'Python interpreter',
        'pip': 'Python package manager'
    }
    
    print("Checking prerequisites...")
    missing = []
    
    for tool, description in tools.items():
        if check_command(tool):
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                version = result.stdout.strip().split('\n')[0]
                print(f"  ✓ {tool}: {version}")
            except:
                print(f"  ✓ {tool}: Available")
        else:
            print(f"  ✗ {tool}: Not found ({description})")
            missing.append(tool)
    
    return missing

def setup_git_hooks():
    """Set up git hooks if in a git repository."""
    if not Path('.git').exists():
        return
    
    hooks_dir = Path('.git/hooks')
    if not hooks_dir.exists():
        return
    
    # Example: Create a simple pre-commit hook
    pre_commit = hooks_dir / 'pre-commit'
    if not pre_commit.exists():
        pre_commit.write_text('''#!/bin/bash
# Simple pre-commit hook
echo "Running pre-commit checks..."

# Check for Python syntax errors
if command -v python3 &> /dev/null; then
    find . -name "*.py" -exec python3 -m py_compile {} \;
fi

echo "Pre-commit checks passed"
''')
        pre_commit.chmod(0o755)
        print("  ✓ Created git pre-commit hook")

def main():
    """Main hook function."""
    print("=== Environment Setup ===")
    
    # Check prerequisites
    missing = check_prerequisites()
    
    if missing:
        print(f"\nMissing tools: {', '.join(missing)}")
        print("Please install missing tools before proceeding.")
        return 1
    
    # Setup git hooks
    print("\nSetting up git hooks...")
    setup_git_hooks()
    
    # Environment variables
    config_dir = os.getenv("AMAZONQ_CONFIG_DIR", "")
    if config_dir:
        print(f"\nAmazon Q Config Directory: {config_dir}")
    
    print("\nEnvironment setup completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Example 4: Code Quality Check Hook

Create a shell hook for code quality checks:

```bash
ai-config hooks create code-quality --type shell
```

Edit the generated `code-quality.sh`:

```bash
#!/bin/bash
#
# Code Quality Check Hook
#
# Runs various code quality checks
#

set -e

echo "=== Code Quality Checks ==="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Python checks
if find . -name "*.py" -type f | head -1 | grep -q .; then
    echo "Found Python files, running Python checks..."
    
    if command_exists flake8; then
        echo "Running flake8..."
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    fi
    
    if command_exists black; then
        echo "Checking black formatting..."
        black --check . || echo "Consider running: black ."
    fi
    
    if command_exists mypy; then
        echo "Running mypy type checking..."
        mypy . || true
    fi
fi

# JavaScript/TypeScript checks
if find . -name "*.js" -o -name "*.ts" -type f | head -1 | grep -q .; then
    echo "Found JavaScript/TypeScript files, running JS checks..."
    
    if command_exists eslint; then
        echo "Running ESLint..."
        eslint . || true
    fi
    
    if command_exists prettier; then
        echo "Checking Prettier formatting..."
        prettier --check . || echo "Consider running: prettier --write ."
    fi
fi

# General checks
echo "Running general checks..."

# Check for TODO/FIXME comments
echo "Checking for TODO/FIXME comments:"
grep -r "TODO\|FIXME" --include="*.py" --include="*.js" --include="*.ts" . | head -5 || echo "No TODO/FIXME found"

# Check file permissions
echo "Checking for executable files:"
find . -type f -executable -not -path "./.git/*" | head -5

echo "Code quality checks completed"
exit 0
```

## Hook Management

### Listing Hooks

View available hooks:

```bash
# List all hooks
ai-config hooks list
```

### Testing Hooks

Test hook functionality:

```bash
# Test specific hook
ai-config hooks test my-hook.py

# Test shell hook
ai-config hooks test my-hook.sh
```

### Running Hooks

Execute hooks manually:

```bash
# Run a Python hook
ai-config hooks run my-hook.py

# Run a shell hook
ai-config hooks run my-hook.sh

# Run with arguments
ai-config hooks run my-hook.py --args "arg1 arg2"

# Run with timeout
ai-config hooks run my-hook.py --timeout 60
```

### Hook Validation

Validate hook configurations:

```bash
# Validate all hooks
ai-config hooks validate
```

### Hook Configuration

View hook configuration:

```bash
# Show hook configuration
ai-config hooks config
```

### Context Loading

Load context using hooks:

```bash
# Load context from hook
ai-config hooks context my-context
```

## Hook Best Practices

### Development Guidelines

1. **Keep hooks focused**: Each hook should have a single, clear purpose
2. **Handle errors gracefully**: Always include error handling in scripts
3. **Use appropriate exit codes**: Return 0 for success, non-zero for failure
4. **Test thoroughly**: Test hooks in different environments and scenarios
5. **Document behavior**: Include clear descriptions and usage examples
6. **Make scripts executable**: Ensure shell scripts have proper permissions

### Python Hook Best Practices

```python
#!/usr/bin/env python3
"""
Well-structured hook with proper error handling.
"""

import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main hook function with error handling."""
    try:
        # Your hook logic here
        logger.info("Hook started successfully")
        
        # Access environment variables safely
        config_dir = os.getenv("AMAZONQ_CONFIG_DIR")
        if not config_dir:
            logger.warning("AMAZONQ_CONFIG_DIR not set")
            return 1
        
        # Perform operations
        result = perform_operations()
        
        if result:
            logger.info("Hook completed successfully")
            return 0
        else:
            logger.error("Hook failed")
            return 1
            
    except Exception as e:
        logger.error(f"Hook failed with error: {e}")
        return 1

def perform_operations():
    """Perform the actual hook operations."""
    # Your implementation here
    return True

if __name__ == "__main__":
    sys.exit(main())
```

### Shell Hook Best Practices

```bash
#!/bin/bash
#
# Well-structured shell hook with proper error handling
#

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Function for logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >&2
}

# Function for error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Main function
main() {
    log "Hook started"
    
    # Check prerequisites
    command -v git >/dev/null 2>&1 || error_exit "git not found"
    
    # Your hook logic here
    if perform_operations; then
        log "Hook completed successfully"
        exit 0
    else
        error_exit "Hook operations failed"
    fi
}

perform_operations() {
    # Your implementation here
    return 0
}

# Run main function
main "$@"
```

### Performance Considerations

1. **Optimize execution time**: Keep hook execution fast (< 30 seconds for most hooks)
2. **Cache results**: Cache expensive operations when possible
3. **Limit resource usage**: Monitor memory and CPU usage
4. **Use timeouts**: Set reasonable timeout values for external commands
5. **Avoid blocking operations**: Don't wait indefinitely for external resources

### Security Best Practices

1. **Validate inputs**: Always validate user inputs and environment variables
2. **Use secure paths**: Avoid using user-controlled paths
3. **Limit permissions**: Run hooks with minimal required permissions
4. **Sanitize outputs**: Clean sensitive information from outputs
5. **Use subprocess safely**: Use proper subprocess handling in Python

## Troubleshooting Hooks

### Common Issues

#### Hook Not Found

**Symptoms:**
- "Hook not found" error when running
- Hook doesn't appear in `ai-config hooks list`

**Solutions:**
```bash
# Check if hook file exists
ls -la ~/.aws/amazonq/hooks/

# Verify file permissions
ls -la ~/.aws/amazonq/hooks/my-hook.py

# Make sure file is executable (for shell scripts)
chmod +x ~/.aws/amazonq/hooks/my-hook.sh
```

#### Permission Denied Errors

**Symptoms:**
- "Permission denied" when running hook
- Script fails to execute

**Solutions:**
```bash
# Make script executable
chmod +x ~/.aws/amazonq/hooks/my-hook.sh

# Check file permissions
ls -la ~/.aws/amazonq/hooks/my-hook.sh

# For Python scripts, ensure Python is executable
which python3
```

#### Script Execution Errors

**Symptoms:**
- Script fails with error codes
- Import errors in Python scripts
- Command not found errors in shell scripts

**Solutions:**
```bash
# Test script manually
python3 ~/.aws/amazonq/hooks/my-hook.py

# Check Python path and imports
python3 -c "import sys; print(sys.path)"

# For shell scripts, check command availability
which command_name

# Test with verbose output
ai-config hooks test my-hook.py
```

#### Environment Variable Issues

**Symptoms:**
- Environment variables not available
- Unexpected variable values

**Solutions:**
```bash
# Check available environment variables
env | grep AMAZONQ
env | grep AI_CONFIGURATOR

# Test hook with debug output
export DEBUG=true
ai-config hooks run my-hook.py
```

### Debug Mode

Enable detailed logging in your hooks:

**Python Debug Example:**
```python
import os
import logging

# Enable debug logging if DEBUG environment variable is set
if os.getenv('DEBUG'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    logger.debug("Debug mode enabled")
    logger.info("Hook starting...")
    # Your code here
```

**Shell Debug Example:**
```bash
#!/bin/bash

# Enable debug mode if DEBUG is set
if [[ "${DEBUG:-}" == "true" ]]; then
    set -x  # Print commands as they're executed
fi

echo "Hook starting..."
# Your code here
```

### Testing Hooks

Always test your hooks before deploying:

```bash
# Test hook execution
ai-config hooks test my-hook.py

# Test with different environments
DEBUG=true ai-config hooks test my-hook.py

# Test error conditions
# (modify your hook to simulate errors)

# Test performance
time ai-config hooks run my-hook.py
```

### Hook Monitoring

Monitor hook performance and execution:

```bash
# Check hook execution logs (if available)
tail -f ~/.aws/amazonq/logs/hooks.log

# Monitor system resources during hook execution
top -p $(pgrep -f my-hook.py)

# Time hook execution
time ai-config hooks run my-hook.py
```

## Quick Reference

### CLI Commands

```bash
# Create hooks
ai-config hooks create my-hook --type python    # Create Python hook
ai-config hooks create my-hook --type shell     # Create shell hook

# Manage hooks
ai-config hooks list                            # List all hooks
ai-config hooks test my-hook.py                 # Test a hook
ai-config hooks run my-hook.py                  # Run a hook
ai-config hooks validate                        # Validate all hooks
ai-config hooks config                          # Show hook configuration
ai-config hooks context my-context              # Load context from hook
```

### Hook File Locations

- **Hooks Directory**: `~/.aws/amazonq/hooks/`
- **Python Hooks**: `~/.aws/amazonq/hooks/hook-name.py`
- **Shell Hooks**: `~/.aws/amazonq/hooks/hook-name.sh`

### Environment Variables

Available in all hooks:
- `AMAZONQ_CONFIG_DIR`: Amazon Q configuration directory
- `AI_CONFIGURATOR_HOOKS_DIR`: Hooks directory path
- `HOOK_NAME`: Current hook name

### Hook Template Structure

**Python Hook:**
```python
#!/usr/bin/env python3
import sys
import os

def main():
    # Your hook logic here
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Shell Hook:**
```bash
#!/bin/bash
set -e

echo "Hook starting..."
# Your hook logic here
echo "Hook completed"
exit 0
```

This updated guide reflects the current implementation of AI Configurator hooks and provides practical examples and troubleshooting advice for the actual CLI commands and functionality.
