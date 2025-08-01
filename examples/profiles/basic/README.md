# Basic Profile Examples

This directory contains basic profile examples designed for users who are new to the AI Configurator system. These profiles demonstrate fundamental concepts and provide starting points for common use cases.

## Available Profiles

### minimal.json

A bare-bones profile that demonstrates the essential structure and configuration options needed to get started with the AI Configurator.

**Use Case**: Perfect for beginners who want to understand the basic profile structure without complexity.

**What it includes**:

- Basic development guidelines context
- Project README context
- Comprehensive inline documentation
- Optional hooks section (disabled by default)
- Essential settings with sensible defaults

### content-creator.json _(Coming Soon)_

A profile optimized for content creators, writers, and documentation specialists.

### student.json _(Coming Soon)_

A profile designed for academic and learning scenarios.

## Getting Started with the Minimal Profile

### 1. Installation

Copy the minimal profile to your AI Configurator profiles directory:

```bash
# Copy to your profiles directory
cp examples/profiles/basic/minimal.json ~/.kiro/profiles/my-minimal-profile.json

# Or copy to a project-specific location
cp examples/profiles/basic/minimal.json .kiro/profiles/minimal.json
```

### 2. Activation

Activate the profile using the AI Configurator CLI:

```bash
# Activate globally
ai-configurator profile activate my-minimal-profile

# Or activate for current project
ai-configurator profile activate minimal --local
```

### 3. Verification

Verify the profile is working correctly:

```bash
# Check active profile
ai-configurator profile status

# List loaded contexts
ai-configurator context list

# Test configuration
ai-configurator validate
```

## Customization Guide

### Adding More Contexts

To add additional context files to your profile:

1. **Single file**: Add the path to the `paths` array

   ```json
   "paths": [
     "contexts/development-guidelines.md",
     "README.md",
     "contexts/my-custom-context.md"
   ]
   ```

2. **Multiple files with patterns**: Use glob patterns

   ```json
   "paths": [
     "contexts/**/*.md",
     "docs/guidelines/*.md"
   ]
   ```

3. **Conditional contexts**: Reference contexts that may not always exist
   ```json
   "paths": [
     "contexts/development-guidelines.md",
     "?contexts/optional-context.md"  // ? makes it optional
   ]
   ```

### Enabling Hooks

To enable automation hooks:

1. **Enable an existing hook**:

   ```json
   "hooks": {
     "auto-documentation": {
       "enabled": true,
       "config": {
         "watch_patterns": ["src/**/*.py"],
         "output_format": "markdown"
       }
     }
   }
   ```

2. **Add a new hook**:
   ```json
   "hooks": {
     "my-custom-hook": {
       "enabled": true,
       "script": "hooks/my-script.py",
       "trigger": "on_file_save",
       "config": {
         "file_patterns": ["*.py", "*.js"]
       }
     }
   }
   ```

### Adjusting Settings

Common settings you might want to modify:

```json
"settings": {
  // Increase if you have many context files
  "max_contexts": 100,

  // Disable auto-reload for better performance
  "auto_reload": false,

  // Enable debug logging for troubleshooting
  "log_level": "debug",

  // Skip context validation for faster loading
  "validate_contexts": false
}
```

## Common Use Cases

### Personal Development Setup

```json
{
  "metadata": {
    "name": "personal-dev",
    "description": "My personal development profile"
  },
  "paths": [
    "contexts/development-guidelines.md",
    "contexts/personal-coding-standards.md",
    "README.md",
    "CONTRIBUTING.md"
  ],
  "settings": {
    "auto_reload": true,
    "log_level": "info"
  }
}
```

### Team Project Setup

```json
{
  "metadata": {
    "name": "team-project",
    "description": "Shared team project configuration"
  },
  "paths": [
    "contexts/development-guidelines.md",
    "contexts/team-standards.md",
    "contexts/project-specific-rules.md",
    "README.md",
    "docs/architecture.md"
  ],
  "hooks": {
    "code-quality-check": {
      "enabled": true,
      "config": {
        "run_on_commit": true
      }
    }
  }
}
```

## Troubleshooting

### Profile Not Loading

1. **Check file syntax**: Ensure your JSON is valid

   ```bash
   ai-configurator validate profile my-profile.json
   ```

2. **Verify paths**: Make sure all context paths exist

   ```bash
   ai-configurator context validate
   ```

3. **Check permissions**: Ensure files are readable
   ```bash
   ls -la ~/.kiro/profiles/
   ```

### Contexts Not Found

1. **Use absolute paths** for debugging:

   ```json
   "paths": [
     "/full/path/to/contexts/development-guidelines.md"
   ]
   ```

2. **Check working directory**: Relative paths are resolved from the profile location

3. **Use optional syntax** for contexts that might not exist:
   ```json
   "paths": [
     "?contexts/optional-file.md"
   ]
   ```

### Performance Issues

1. **Limit context files**:

   ```json
   "settings": {
     "max_contexts": 20
   }
   ```

2. **Disable auto-reload**:

   ```json
   "settings": {
     "auto_reload": false
   }
   ```

3. **Use specific paths** instead of broad glob patterns

## Next Steps

Once you're comfortable with the minimal profile:

1. **Explore other basic profiles**: Try `content-creator.json` or `student.json`
2. **Check professional profiles**: Look at `examples/profiles/professional/`
3. **Learn about hooks**: Explore `examples/hooks/` for automation examples
4. **Create custom contexts**: Write your own context files in `contexts/`

## Support

For additional help:

- Check the main documentation: `docs/profiles.md`
- View example contexts: `examples/contexts/`
- See hook examples: `examples/hooks/`
- Join the community discussions
