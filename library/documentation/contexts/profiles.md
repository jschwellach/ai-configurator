---
title: "Profile Management Guide"
description: "Complete guide to managing configuration profiles in AI Configurator"
category: "user"
tags: ["profiles", "management", "configuration"]
version: "1.0"
last_updated: "2025-01-31"
related_docs:
  - "docs/configuration.md"
  - "docs/hooks.md"
  - "docs/mcp-servers.md"
---

# Profile Management Guide

Profiles in AI Configurator allow you to create different configuration sets for various use cases, environments, or team roles. This guide covers everything you need to know about creating, managing, and using profiles effectively.

## What are Profiles?

Profiles are named configuration sets that define:

- **Context files** to load for AI assistance
- **Hooks** to execute at specific triggers
- **MCP servers** to enable
- **Settings** for behavior customization

Think of profiles as different "modes" for your AI assistant - you might have a "developer" profile for coding work, an "architect" profile for system design, or a "documentation" profile for writing tasks.

## Profile Types and Formats

### YAML Profiles (Recommended)

Modern YAML format with advanced features:

```yaml
name: "developer"
description: "Full-stack development profile"
version: "1.2"

contexts:
  - "contexts/development-guidelines.md"
  - "contexts/coding-standards.md"
  - "contexts/aws-best-practices.md"

hooks:
  on_session_start:
    - name: "setup-dev-env"
      enabled: true
  per_user_message:
    - name: "code-reviewer"
      enabled: true

mcp_servers:
  - "awslabs.core-mcp-server"
  - "fetch"

settings:
  auto_backup: true
  validation_level: "strict"
  hot_reload: true
```

### JSON Profiles (Legacy)

Simpler JSON format for backward compatibility:

```json
{
  "paths": [
    "contexts/development-guidelines.md",
    "contexts/aws-best-practices.md"
  ],
  "description": "Development environment profile"
}
```

## Managing Profiles

### Listing Profiles

View all available profiles:

```bash
# List all profiles in table format
ai-config profile list

# List with detailed information
ai-config profile list --format json

# Show YAML format
ai-config profile list --format yaml
```

Example output:

```
┌─────────────────┬────────────┬──────────┐
│ Profile         │ Format     │ Status   │
├─────────────────┼────────────┼──────────┤
│ default         │ YAML       │ ✅ Active │
│ developer       │ YAML       │          │
│ solutions-arch  │ JSON       │          │
│ engagement-mgr  │ YAML+JSON  │          │
└─────────────────┴────────────┴──────────┘
```

### Creating Profiles

#### Create YAML Profile (Recommended)

```bash
# Create basic profile
ai-config profile create my-profile

# Create with description
ai-config profile create my-profile --description "My custom profile"

# Create from template
ai-config profile create my-profile --template developer

# Create JSON profile (legacy)
ai-config profile create my-profile --format json
```

#### Profile Creation Examples

**Developer Profile:**

```bash
ai-config profile create developer --description "Full-stack development environment"
```

**Solutions Architect Profile:**

```bash
ai-config profile create solutions-architect --description "AWS architecture and design"
```

**Documentation Profile:**

```bash
ai-config profile create documentation --description "Technical writing and documentation"
```

### Validating Profiles

Ensure your profiles are correctly configured:

```bash
# Validate specific profile
ai-config profile validate developer

# Validate all profiles
ai-config profile validate --all

# Strict validation
ai-config validate --strict
```

### Converting Between Formats

Convert profiles between YAML and JSON:

```bash
# Convert JSON to YAML
ai-config profile convert old-profile --to-format yaml --backup

# Convert YAML to JSON
ai-config profile convert new-profile --to-format json --backup
```

## Profile Structure Deep Dive

### Complete YAML Profile Example

```yaml
# Profile identification
name: "full-stack-developer"
description: "Comprehensive development environment for full-stack projects"
version: "2.1"

# Context files to load
contexts:
  # Specific files
  - "contexts/development-guidelines.md"
  - "contexts/coding-standards.md"
  - "contexts/aws-best-practices.md"

  # Pattern matching
  - "contexts/frameworks/*.md"
  - "contexts/languages/javascript/*.md"

  # Conditional contexts
  - path: "contexts/docker-guidelines.md"
    condition:
      environment:
        DOCKER_ENABLED: "true"

# Hook configurations
hooks:
  # Session start hooks
  on_session_start:
    - name: "setup-dev-env"
      enabled: true
      priority: 1
      config:
        auto_install_deps: true
        setup_git_hooks: true

    - name: "load-project-context"
      enabled: true
      priority: 2
      config:
        scan_package_json: true
        detect_frameworks: true

  # Per-message hooks
  per_user_message:
    - name: "code-reviewer"
      enabled: true
      config:
        check_style: true
        suggest_improvements: true

    - name: "security-scanner"
      enabled: true
      config:
        scan_dependencies: true
        check_vulnerabilities: true

  # File change hooks
  on_file_change:
    - name: "auto-formatter"
      enabled: true
      config:
        formats: ["js", "ts", "py", "yaml"]
        run_linter: true

# MCP server references
mcp_servers:
  - "awslabs.core-mcp-server"
  - "awslabs.cdk-mcp-server"
  - "fetch"
  - "filesystem"

# Profile settings
settings:
  auto_backup: true
  validation_level: "strict"
  hot_reload: true
  cache_enabled: true
  timeout: 45
  max_context_size: 75000

  # Advanced settings
  context_processing:
    enable_templates: true
    variable_substitution: true
    markdown_extensions: ["tables", "fenced_code", "toc"]

# Metadata
metadata:
  created_date: "2025-01-31"
  author: "development-team"
  tags: ["development", "full-stack", "aws"]
  version_history:
    - version: "1.0"
      date: "2025-01-15"
      changes: "Initial version"
    - version: "2.0"
      date: "2025-01-25"
      changes: "Added security scanning hooks"
    - version: "2.1"
      date: "2025-01-31"
      changes: "Enhanced context processing"

  # Custom metadata
  team: "platform-engineering"
  environment: "development"
  compliance_level: "standard"
```

### Context Configuration

#### Basic Context Paths

```yaml
contexts:
  # Direct file references
  - "contexts/aws-best-practices.md"
  - "contexts/security-guidelines.md"

  # Relative paths
  - "team-docs/coding-standards.md"
  - "../shared-contexts/company-policies.md"
```

#### Pattern Matching

```yaml
contexts:
  # All markdown files in a directory
  - "contexts/development/*.md"

  # Recursive pattern matching
  - "contexts/**/*.md"

  # Specific file patterns
  - "contexts/aws-*.md"
  - "contexts/*-guidelines.md"
```

#### Conditional Contexts

```yaml
contexts:
  # Platform-specific contexts
  - path: "contexts/linux-specific.md"
    condition:
      platform: ["linux"]

  # Environment-based contexts
  - path: "contexts/production-guidelines.md"
    condition:
      environment:
        NODE_ENV: "production"
        ENVIRONMENT: "prod"

  # File existence conditions
  - path: "contexts/docker-guidelines.md"
    condition:
      file_exists: "Dockerfile"

  # Combined conditions
  - path: "contexts/advanced-config.md"
    condition:
      platform: ["linux", "macos"]
      environment:
        ADVANCED_MODE: "true"
      file_exists: "advanced.config.js"
```

### Hook Configuration

#### Hook Reference Types

```yaml
hooks:
  on_session_start:
    # Simple string reference
    - "basic-setup"

    # Object reference with configuration
    - name: "advanced-setup"
      enabled: true
      priority: 10
      config:
        parameter1: "value1"
        parameter2: true

      # Hook-specific conditions
      conditions:
        - platform: ["linux", "macos"]
          environment:
            DEBUG: "true"
```

#### Hook Priorities

Control execution order with priorities:

```yaml
hooks:
  on_session_start:
    - name: "first-hook"
      priority: 1 # Executes first

    - name: "second-hook"
      priority: 5 # Executes second

    - name: "third-hook"
      priority: 10 # Executes third

    - name: "default-hook"
      # No priority = 0, executes last
```

### MCP Server Configuration

Reference MCP servers defined in your global configuration:

```yaml
mcp_servers:
  # Core AWS services
  - "awslabs.core-mcp-server"
  - "awslabs.aws-documentation-mcp-server"
  - "awslabs.cdk-mcp-server"

  # Utility servers
  - "fetch"
  - "filesystem"
  - "git"

  # Custom servers
  - "company-internal-server"
  - "project-specific-server"
```

## Profile Use Cases and Examples

### Development Profiles

#### Frontend Developer

```yaml
name: "frontend-developer"
description: "Frontend development with React/Vue/Angular"

contexts:
  - "contexts/frontend-guidelines.md"
  - "contexts/ui-ux-principles.md"
  - "contexts/accessibility-standards.md"
  - "contexts/frameworks/react/*.md"

hooks:
  on_session_start:
    - name: "setup-node-env"
    - name: "check-dependencies"

  per_user_message:
    - name: "ui-reviewer"
    - name: "accessibility-checker"

mcp_servers:
  - "fetch"
  - "filesystem"
```

#### Backend Developer

```yaml
name: "backend-developer"
description: "Backend development with APIs and databases"

contexts:
  - "contexts/api-design-guidelines.md"
  - "contexts/database-best-practices.md"
  - "contexts/security-standards.md"
  - "contexts/aws-services/*.md"

hooks:
  on_session_start:
    - name: "setup-database-connection"
    - name: "load-api-schemas"

  per_user_message:
    - name: "api-validator"
    - name: "security-scanner"

mcp_servers:
  - "awslabs.core-mcp-server"
  - "awslabs.aws-documentation-mcp-server"
```

#### DevOps Engineer

```yaml
name: "devops-engineer"
description: "Infrastructure and deployment automation"

contexts:
  - "contexts/infrastructure-as-code.md"
  - "contexts/ci-cd-best-practices.md"
  - "contexts/monitoring-guidelines.md"
  - "contexts/aws-services/*.md"

hooks:
  on_session_start:
    - name: "check-aws-credentials"
    - name: "load-terraform-state"

  on_file_change:
    - name: "validate-terraform"
    - name: "check-security-policies"

mcp_servers:
  - "awslabs.core-mcp-server"
  - "awslabs.cdk-mcp-server"
```

### Role-Based Profiles

#### Solutions Architect

```yaml
name: "solutions-architect"
description: "AWS solutions architecture and design"

contexts:
  - "contexts/aws-well-architected.md"
  - "contexts/architecture-patterns.md"
  - "contexts/cost-optimization.md"
  - "contexts/security-architecture.md"

hooks:
  on_session_start:
    - name: "load-architecture-templates"
    - name: "check-compliance-requirements"

  per_user_message:
    - name: "architecture-reviewer"
    - name: "cost-analyzer"

settings:
  validation_level: "strict"
  max_context_size: 100000
```

#### Technical Writer

```yaml
name: "technical-writer"
description: "Documentation and technical writing"

contexts:
  - "contexts/writing-style-guide.md"
  - "contexts/documentation-standards.md"
  - "contexts/api-documentation-templates.md"

hooks:
  on_session_start:
    - name: "load-writing-templates"

  per_user_message:
    - name: "grammar-checker"
    - name: "style-validator"

  on_file_change:
    - name: "spell-checker"
    - name: "link-validator"

settings:
  context_processing:
    enable_templates: true
    markdown_extensions: ["tables", "toc", "footnotes"]
```

### Environment-Specific Profiles

#### Development Environment

```yaml
name: "development"
description: "Local development environment"

contexts:
  - "contexts/development-guidelines.md"
  - "contexts/debugging-tips.md"
  - "contexts/local-setup.md"

hooks:
  on_session_start:
    - name: "setup-dev-tools"
      config:
        install_missing: true
        update_existing: false

settings:
  hot_reload: true
  cache_enabled: true
  validation_level: "normal"
```

#### Production Support

```yaml
name: "production-support"
description: "Production environment support and troubleshooting"

contexts:
  - "contexts/production-guidelines.md"
  - "contexts/troubleshooting-runbooks.md"
  - "contexts/incident-response.md"

hooks:
  on_session_start:
    - name: "check-system-health"
    - name: "load-monitoring-dashboards"

settings:
  validation_level: "strict"
  auto_backup: true
  timeout: 60
```

## Profile Best Practices

### Naming Conventions

Use clear, descriptive names:

```bash
# Good examples
developer-python
architect-aws
writer-technical
support-production

# Avoid
dev
arch
writer
prod
```

### Organization Strategies

#### By Role

```
profiles/
├── developer.yaml
├── architect.yaml
├── devops.yaml
├── writer.yaml
└── manager.yaml
```

#### By Technology Stack

```
profiles/
├── python-developer.yaml
├── javascript-developer.yaml
├── aws-architect.yaml
├── kubernetes-operator.yaml
└── data-scientist.yaml
```

#### By Environment

```
profiles/
├── local-development.yaml
├── staging-support.yaml
├── production-support.yaml
└── testing-qa.yaml
```

### Context Management

1. **Keep contexts focused**: Each context file should serve a specific purpose
2. **Use descriptive filenames**: `aws-lambda-best-practices.md` vs `lambda.md`
3. **Organize by category**: Group related contexts in subdirectories
4. **Avoid duplication**: Use shared contexts across multiple profiles

### Hook Management

1. **Start simple**: Begin with basic hooks and add complexity gradually
2. **Test thoroughly**: Validate hooks work correctly before deploying
3. **Document behavior**: Add descriptions to complex hook configurations
4. **Handle failures gracefully**: Ensure hooks don't break the system if they fail

### Version Control

Track profile changes:

```yaml
metadata:
  version_history:
    - version: "1.0"
      date: "2025-01-15"
      changes: "Initial version"
    - version: "1.1"
      date: "2025-01-20"
      changes: "Added security contexts"
    - version: "1.2"
      date: "2025-01-31"
      changes: "Enhanced hook configuration"
```

## Troubleshooting Profiles

### Common Issues

#### Profile Not Loading

```bash
# Check if profile exists
ai-config profile list

# Validate profile configuration
ai-config profile validate my-profile

# Check for syntax errors
ai-config validate --strict
```

#### Context Files Not Found

```bash
# Validate all references
ai-config profile validate my-profile

# Check file paths
ls ~/.amazonq/contexts/
```

#### Hooks Not Executing

```bash
# Test hook individually
ai-config hooks test my-hook

# Check hook conditions
ai-config hooks validate my-hook

# Review hook logs
ai-config logs --component hooks
```

### Debug Mode

Enable detailed logging:

```bash
export AI_CONFIGURATOR_LOG_LEVEL=DEBUG
ai-config profile validate my-profile
```

### Profile Recovery

If a profile becomes corrupted:

```bash
# Create backup first
ai-config backup create "before-profile-fix"

# Reset profile to template
ai-config profile create my-profile --template default --force

# Restore from backup if needed
ai-config backup restore backup-id
```

## Advanced Profile Features

### Template Variables

Use environment variables in profiles:

```yaml
contexts:
  - "contexts/${TEAM:-default}/*.md"
  - "contexts/${ENVIRONMENT:-development}-specific.md"

settings:
  timeout: ${TIMEOUT:-30}
  max_context_size: ${MAX_CONTEXT_SIZE:-50000}
```

### Conditional Loading

Load profiles based on conditions:

```yaml
# In global configuration
profile_selection:
  auto_detect: true
  conditions:
    - profile: "developer"
      condition:
        file_exists: "package.json"
    - profile: "python-developer"
      condition:
        file_exists: "requirements.txt"
    - profile: "aws-architect"
      condition:
        environment:
          AWS_PROFILE: "*"
```

### Profile Inheritance

Extend existing profiles:

```yaml
name: "senior-developer"
extends: "developer" # Inherit from base profile

# Override or add to inherited configuration
contexts:
  - "contexts/senior-developer-guidelines.md"
  - "contexts/mentoring-guidelines.md"

hooks:
  on_session_start:
    - name: "team-lead-setup"
      enabled: true

settings:
  validation_level: "strict" # Override inherited setting
```

### Dynamic Profile Generation

Generate profiles programmatically:

```bash
# Generate profile from project structure
ai-config profile generate --from-project --name auto-detected

# Generate from team template
ai-config profile generate --from-template team-standard --name my-team-profile
```

This comprehensive guide should help you effectively create, manage, and use profiles in AI Configurator. Remember to validate your profiles regularly and keep them updated as your needs evolve.
