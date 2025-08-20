# Template Usage Examples

This guide provides comprehensive usage examples for all template categories in the AI Configurator system, including step-by-step guides for common customization scenarios and troubleshooting information.

## Table of Contents

- [Profile Templates](#profile-templates)
- [Context Templates](#context-templates)
- [Hook Templates](#hook-templates)
- [Workflow Templates](#workflow-templates)
- [Common Customization Scenarios](#common-customization-scenarios)
- [Troubleshooting Guide](#troubleshooting-guide)

## Profile Templates

Profile templates define which contexts and hooks to load for specific use cases. They serve as the main configuration entry point for the AI Configurator.

### Basic Profiles

#### Minimal Profile Example

**Use Case**: Getting started with AI Configurator, learning the basics

**File**: `examples/profiles/basic/minimal.json`

**Step-by-Step Setup**:

1. **Copy the template**:

   ```bash
   cp examples/profiles/basic/minimal.json ~/.kiro/profiles/my-minimal.json
   ```

2. **Customize the context paths**:

   ```json
   {
     "paths": [
       "contexts/development-guidelines.md",
       "README.md",
       "contexts/my-custom-context.md" // Add your own context
     ]
   }
   ```

3. **Enable your first hook** (optional):

   ```json
   {
     "hooks": {
       "auto-documentation": {
         "enabled": true,
         "config": {
           "watch_patterns": ["src/**/*.py"],
           "output_format": "markdown"
         }
       }
     }
   }
   ```

4. **Activate the profile**:
   ```bash
   ai-configurator profile activate my-minimal
   ```

**Common Customizations**:

- Add project-specific contexts by including your README.md or docs files
- Adjust the `max_contexts` setting if you have many context files
- Enable `auto_reload` for development environments

#### Content Creator Profile Example

**Use Case**: Writers, bloggers, documentation specialists, content marketers

**File**: `examples/profiles/basic/content-creator.json`

**Step-by-Step Setup**:

1. **Copy and customize**:

   ```bash
   cp examples/profiles/basic/content-creator.json ~/.kiro/profiles/my-content.json
   ```

2. **Add your content directories**:

   ```json
   {
     "paths": [
       "contexts/domains/content-creation-guidelines.md",
       "contexts/domains/technical-writing-standards.md",
       "blog/**/*.md", // Include your blog posts
       "docs/**/*.md", // Include documentation
       "content-style-guide.md" // Your style guide
     ]
   }
   ```

3. **Configure content-specific hooks**:
   ```json
   {
     "hooks": {
       "spell-check": {
         "enabled": true,
         "config": {
           "languages": ["en-US"],
           "ignore_technical_terms": true
         }
       },
       "seo-optimizer": {
         "enabled": true,
         "config": {
           "target_keywords": ["your", "keywords"],
           "readability_target": "general"
         }
       }
     }
   }
   ```

**Common Customizations**:

- Add brand-specific style guides and tone of voice documents
- Include SEO guidelines and keyword research
- Configure automated publishing workflows

### Professional Profiles

#### Data Scientist Profile Example

**Use Case**: Machine learning engineers, data analysts, research scientists

**File**: `examples/profiles/professional/data-scientist.json`

**Step-by-Step Setup**:

1. **Copy the template**:

   ```bash
   cp examples/profiles/professional/data-scientist.json ~/.kiro/profiles/my-ds.json
   ```

2. **Add your data science contexts**:

   ```json
   {
     "paths": [
       "contexts/domains/data-science-best-practices.md",
       "contexts/workflows/testing-strategies.md",
       "notebooks/**/*.ipynb", // Include Jupyter notebooks
       "data/README.md", // Data documentation
       "models/model-cards/*.md" // Model documentation
     ]
   }
   ```

3. **Configure ML-specific hooks**:
   ```json
   {
     "hooks": {
       "model-validation": {
         "enabled": true,
         "config": {
           "validation_metrics": ["accuracy", "precision", "recall"],
           "threshold_alerts": true
         }
       },
       "experiment-tracking": {
         "enabled": true,
         "config": {
           "mlflow_uri": "http://localhost:5000",
           "auto_log_params": true
         }
       }
     }
   }
   ```

**Common Customizations**:

- Add domain-specific contexts (healthcare, finance, etc.)
- Configure data pipeline monitoring
- Include model governance and compliance contexts

#### DevOps Engineer Profile Example

**Use Case**: Infrastructure engineers, site reliability engineers, platform engineers

**File**: `examples/profiles/professional/devops-engineer.json`

**Step-by-Step Setup**:

1. **Copy and customize**:

   ```bash
   cp examples/profiles/professional/devops-engineer.json ~/.kiro/profiles/my-devops.json
   ```

2. **Add infrastructure contexts**:

   ```json
   {
     "paths": [
       "contexts/domains/devops-methodologies.md",
       "contexts/workflows/incident-response.md",
       "infrastructure/**/*.tf", // Terraform files
       "k8s/**/*.yaml", // Kubernetes manifests
       "monitoring/runbooks/*.md" // Operational runbooks
     ]
   }
   ```

3. **Configure DevOps automation**:
   ```json
   {
     "hooks": {
       "infrastructure-validation": {
         "enabled": true,
         "config": {
           "terraform_validate": true,
           "security_scan": true
         }
       },
       "deployment-tracker": {
         "enabled": true,
         "config": {
           "slack_webhook": "your-webhook-url",
           "track_rollbacks": true
         }
       }
     }
   }
   ```

**Common Customizations**:

- Add cloud provider-specific contexts (AWS, GCP, Azure)
- Configure monitoring and alerting integrations
- Include compliance and security scanning contexts

## Context Templates

Context templates provide domain-specific guidance and best practices to the AI assistant.

### Domain Contexts

#### Data Science Best Practices Context

**Use Case**: Providing ML lifecycle guidance, coding standards, ethical AI practices

**File**: `examples/contexts/domains/data-science-best-practices.md`

**Usage Examples**:

1. **Reference in profiles**:

   ```json
   {
     "paths": ["contexts/domains/data-science-best-practices.md"]
   }
   ```

2. **Customize for your domain**:

   ```markdown
   # My Company Data Science Best Practices

   ## Company-Specific Guidelines

   - Use our internal ML platform: [platform-name]
   - Follow our data governance policies: [link]
   - All models must pass bias testing before deployment

   ## Standard Practices

   #[[file:examples/contexts/domains/data-science-best-practices.md]]
   ```

3. **Create domain-specific variants**:
   - `healthcare-ml-practices.md` for healthcare applications
   - `financial-ml-practices.md` for financial services
   - `retail-ml-practices.md` for e-commerce and retail

**Common Customizations**:

- Add company-specific tools and platforms
- Include regulatory compliance requirements
- Add domain-specific ethical considerations

#### Security Guidelines Context

**Use Case**: Security best practices, compliance requirements, threat modeling

**File**: `examples/contexts/domains/security-guidelines.md`

**Usage Examples**:

1. **Basic security context**:

   ```json
   {
     "paths": ["contexts/domains/security-guidelines.md"]
   }
   ```

2. **Extend with company policies**:

   ```markdown
   # Company Security Guidelines

   ## Our Security Standards

   - All code must pass SAST scanning
   - Use approved cryptographic libraries only
   - Follow our incident response procedures

   ## Industry Best Practices

   #[[file:examples/contexts/domains/security-guidelines.md]]
   ```

**Common Customizations**:

- Add compliance frameworks (SOC2, HIPAA, PCI-DSS)
- Include company-specific security tools
- Add threat modeling templates

### Workflow Contexts

#### Code Review Process Context

**Use Case**: Standardizing code review practices, quality gates, team collaboration

**File**: `examples/contexts/workflows/code-review-process.md`

**Usage Examples**:

1. **Team code review standards**:

   ```json
   {
     "paths": [
       "contexts/workflows/code-review-process.md",
       "team-specific-review-checklist.md"
     ]
   }
   ```

2. **Customize review criteria**:

   ```markdown
   # Our Code Review Process

   ## Team-Specific Requirements

   - All PRs require 2 approvals
   - Security team review for auth changes
   - Performance testing for API changes

   ## Standard Process

   #[[file:examples/contexts/workflows/code-review-process.md]]
   ```

**Common Customizations**:

- Add language-specific review criteria
- Include automated testing requirements
- Add security and performance review checklists

## Hook Templates

Hook templates define automation workflows and triggers for various development tasks.

### Automation Hooks

#### Auto-Documentation Hook

**Use Case**: Automatically generate and update project documentation

**File**: `examples/hooks/automation/auto-documentation.yaml`

**Step-by-Step Setup**:

1. **Copy the hook**:

   ```bash
   cp examples/hooks/automation/auto-documentation.yaml ~/.kiro/hooks/my-docs.yaml
   cp examples/hooks/automation/auto_documentation.py ~/.kiro/hooks/my_docs.py
   ```

2. **Customize file patterns**:

   ```yaml
   config:
     watch_patterns:
       - "src/**/*.py" # Python source files
       - "lib/**/*.js" # JavaScript files
       - "api/**/*.yaml" # API specifications
       - "docs/**/*.md" # Existing documentation
   ```

3. **Configure output formats**:

   ```yaml
   config:
     output_formats:
       - "markdown" # For GitHub/GitLab
       - "html" # For internal wikis
       - "confluence" # For Confluence integration
   ```

4. **Enable in profile**:
   ```json
   {
     "hooks": {
       "my-docs": {
         "enabled": true,
         "config": {
           "auto_commit": true,
           "commit_message": "docs: auto-update documentation"
         }
       }
     }
   }
   ```

**Common Customizations**:

- Add API documentation generation
- Configure different output destinations
- Add documentation quality checks

#### Code Quality Check Hook

**Use Case**: Automated code analysis, linting, security scanning

**File**: `examples/hooks/automation/code-quality-check.yaml`

**Step-by-Step Setup**:

1. **Copy and customize**:

   ```bash
   cp examples/hooks/automation/code-quality-check.yaml ~/.kiro/hooks/quality.yaml
   ```

2. **Configure quality tools**:

   ```yaml
   config:
     tools:
       python:
         - "flake8" # Linting
         - "black" # Formatting
         - "mypy" # Type checking
         - "bandit" # Security
       javascript:
         - "eslint" # Linting
         - "prettier" # Formatting
         - "audit" # Security
   ```

3. **Set quality gates**:
   ```yaml
   config:
     thresholds:
       code_coverage: 80
       complexity_score: 10
       security_issues: 0
   ```

**Common Customizations**:

- Add language-specific tools
- Configure CI/CD integration
- Add custom quality metrics

### Enhancement Hooks

#### Context Switcher Hook

**Use Case**: Dynamically load contexts based on project type or current work

**File**: `examples/hooks/enhancement/context-switcher.yaml`

**Step-by-Step Setup**:

1. **Configure project detection**:

   ```yaml
   config:
     project_patterns:
       python_ml:
         files: ["requirements.txt", "setup.py", "*.ipynb"]
         contexts: ["data-science-best-practices.md"]
       react_app:
         files: ["package.json", "src/App.js"]
         contexts: ["frontend-best-practices.md"]
   ```

2. **Add time-based switching**:
   ```yaml
   config:
     time_based:
       morning:
         time: "09:00-12:00"
         contexts: ["standup-notes.md", "daily-priorities.md"]
       afternoon:
         time: "13:00-17:00"
         contexts: ["code-review-checklist.md"]
   ```

**Common Customizations**:

- Add git branch-based context switching
- Configure user activity-based switching
- Add team-specific context rules

## Workflow Templates

Workflow templates combine profiles, contexts, and hooks for complete use case solutions.

### Complete Development Setup

**Use Case**: Full development environment with automation, documentation, and quality checks

**Directory**: `examples/workflows/complete-dev-setup/`

**Step-by-Step Setup**:

1. **Copy the entire workflow**:

   ```bash
   cp -r examples/workflows/complete-dev-setup ~/.kiro/workflows/my-dev-setup
   ```

2. **Customize the profile**:

   ```json
   {
     "metadata": {
       "name": "my-dev-setup",
       "description": "My customized development workflow"
     },
     "paths": [
       "workflows/my-dev-setup/contexts/development-guidelines.md",
       "workflows/my-dev-setup/contexts/code-review-process.md",
       "README.md",
       "CONTRIBUTING.md"
     ]
   }
   ```

3. **Configure development hooks**:

   ```json
   {
     "hooks": {
       "pre-commit-checks": {
         "enabled": true,
         "config": {
           "run_tests": true,
           "format_code": true,
           "security_scan": true
         }
       },
       "auto-documentation": {
         "enabled": true
       }
     }
   }
   ```

4. **Activate the workflow**:
   ```bash
   ai-configurator workflow activate my-dev-setup
   ```

**Common Customizations**:

- Add team-specific development practices
- Configure CI/CD integration
- Add project-specific quality gates

### Content Creation Suite

**Use Case**: Complete content creation workflow with writing assistance, SEO optimization, and publishing automation

**Directory**: `examples/workflows/content-creation-suite/`

**Step-by-Step Setup**:

1. **Copy and customize**:

   ```bash
   cp -r examples/workflows/content-creation-suite ~/.kiro/workflows/my-content-suite
   ```

2. **Configure content contexts**:

   ```json
   {
     "paths": [
       "workflows/my-content-suite/contexts/content-guidelines.md",
       "workflows/my-content-suite/contexts/seo-best-practices.md",
       "brand-style-guide.md",
       "content-calendar.md"
     ]
   }
   ```

3. **Set up publishing automation**:
   ```json
   {
     "hooks": {
       "content-optimizer": {
         "enabled": true,
         "config": {
           "seo_check": true,
           "readability_score": true,
           "brand_compliance": true
         }
       },
       "social-publisher": {
         "enabled": true,
         "config": {
           "platforms": ["twitter", "linkedin"],
           "schedule_posts": true
         }
       }
     }
   }
   ```

**Common Customizations**:

- Add brand-specific style guides
- Configure multiple publishing platforms
- Add content performance tracking

## Common Customization Scenarios

### Scenario 1: Adding Company-Specific Contexts

**Problem**: You want to include your company's specific guidelines and practices.

**Solution**:

1. **Create company context directory**:

   ```bash
   mkdir -p ~/.kiro/contexts/company
   ```

2. **Add company-specific contexts**:

   ```markdown
   # Company Development Guidelines

   ## Our Standards

   - Use our internal libraries: [list]
   - Follow our API design principles
   - All code must pass our security review

   ## Industry Best Practices

   #[[file:examples/contexts/domains/development-guidelines.md]]
   ```

3. **Reference in profiles**:
   ```json
   {
     "paths": [
       "contexts/company/development-guidelines.md",
       "contexts/company/security-policies.md"
     ]
   }
   ```

### Scenario 2: Creating Team-Specific Profiles

**Problem**: Different teams need different configurations.

**Solution**:

1. **Create team profiles**:

   ```bash
   mkdir -p ~/.kiro/profiles/teams
   ```

2. **Frontend team profile**:

   ```json
   {
     "metadata": {
       "name": "frontend-team",
       "description": "Configuration for frontend developers"
     },
     "paths": [
       "contexts/domains/frontend-best-practices.md",
       "contexts/workflows/ui-review-process.md"
     ],
     "hooks": {
       "accessibility-check": { "enabled": true },
       "performance-audit": { "enabled": true }
     }
   }
   ```

3. **Backend team profile**:
   ```json
   {
     "metadata": {
       "name": "backend-team",
       "description": "Configuration for backend developers"
     },
     "paths": [
       "contexts/domains/api-design-guidelines.md",
       "contexts/workflows/database-review-process.md"
     ],
     "hooks": {
       "api-documentation": { "enabled": true },
       "security-scan": { "enabled": true }
     }
   }
   ```

### Scenario 3: Environment-Specific Configurations

**Problem**: You need different configurations for development, staging, and production.

**Solution**:

1. **Create environment-specific profiles**:

   ```json
   {
     "metadata": {
       "name": "development-env"
     },
     "settings": {
       "auto_reload": true,
       "log_level": "debug",
       "validate_contexts": false
     },
     "hooks": {
       "hot-reload": { "enabled": true },
       "debug-logger": { "enabled": true }
     }
   }
   ```

2. **Production profile**:
   ```json
   {
     "metadata": {
       "name": "production-env"
     },
     "settings": {
       "auto_reload": false,
       "log_level": "error",
       "validate_contexts": true
     },
     "hooks": {
       "performance-monitor": { "enabled": true },
       "error-tracker": { "enabled": true }
     }
   }
   ```

### Scenario 4: Multi-Language Project Support

**Problem**: Your project uses multiple programming languages.

**Solution**:

1. **Create language-specific contexts**:

   ```markdown
   # Multi-Language Project Guidelines

   ## Python Components

   #[[file:contexts/languages/python-best-practices.md]]

   ## JavaScript Components

   #[[file:contexts/languages/javascript-best-practices.md]]

   ## Shared Standards

   - Use consistent naming conventions across languages
   - Maintain unified documentation standards
   ```

2. **Configure multi-language hooks**:
   ```yaml
   name: "multi-language-quality"
   config:
     languages:
       python:
         tools: ["flake8", "mypy", "black"]
       javascript:
         tools: ["eslint", "prettier", "jest"]
       shared:
         tools: ["git-hooks", "documentation"]
   ```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Profile Not Loading

**Symptoms**:

- Profile activation fails
- Contexts not being loaded
- Hooks not executing

**Diagnosis**:

```bash
ai-configurator profile validate my-profile
ai-configurator profile debug my-profile
```

**Solutions**:

1. **Check file paths**:

   ```json
   {
     "paths": [
       "contexts/file-that-exists.md", // ✓ Correct
       "contexts/missing-file.md" // ✗ Will cause issues
     ]
   }
   ```

2. **Validate JSON syntax**:

   ```bash
   python -m json.tool my-profile.json
   ```

3. **Check permissions**:
   ```bash
   ls -la ~/.kiro/profiles/my-profile.json
   chmod 644 ~/.kiro/profiles/my-profile.json
   ```

#### Issue 2: Context Files Not Found

**Symptoms**:

- Warning messages about missing contexts
- Incomplete guidance from AI assistant

**Diagnosis**:

```bash
ai-configurator context list
ai-configurator context validate
```

**Solutions**:

1. **Use absolute paths for debugging**:

   ```json
   {
     "paths": ["/full/path/to/context.md"]
   }
   ```

2. **Check file encoding**:

   ```bash
   file -bi context-file.md
   # Should show: text/plain; charset=utf-8
   ```

3. **Verify file permissions**:
   ```bash
   find ~/.kiro/contexts -name "*.md" -not -readable
   ```

#### Issue 3: Hooks Not Executing

**Symptoms**:

- Automation not working
- No hook execution logs
- Expected actions not happening

**Diagnosis**:

```bash
ai-configurator hook list
ai-configurator hook test my-hook
ai-configurator hook logs my-hook
```

**Solutions**:

1. **Check hook configuration**:

   ```yaml
   name: "my-hook"
   enabled: true # Must be true
   trigger: "on_file_save" # Must be valid trigger
   script: "my_script.py" # Script must exist
   ```

2. **Verify script permissions**:

   ```bash
   chmod +x ~/.kiro/hooks/my_script.py
   ```

3. **Test hook manually**:
   ```bash
   python ~/.kiro/hooks/my_script.py
   ```

#### Issue 4: Performance Issues

**Symptoms**:

- Slow profile loading
- High memory usage
- Timeouts during context loading

**Diagnosis**:

```bash
ai-configurator profile benchmark my-profile
ai-configurator context stats
```

**Solutions**:

1. **Limit context files**:

   ```json
   {
     "settings": {
       "max_contexts": 20, // Reduce if needed
       "validate_contexts": false // Disable for performance
     }
   }
   ```

2. **Use specific file patterns**:

   ```json
   {
     "paths": [
       "docs/important/*.md", // ✓ Specific
       "docs/**/*.md" // ✗ Too broad
     ]
   }
   ```

3. **Enable caching**:
   ```json
   {
     "settings": {
       "cache_contexts": true,
       "cache_duration": 3600
     }
   }
   ```

#### Issue 5: Template Conflicts

**Symptoms**:

- Conflicting guidance from different contexts
- Hooks interfering with each other
- Inconsistent behavior

**Solutions**:

1. **Use context priorities**:

   ```json
   {
     "contexts": [
       {
         "path": "high-priority-context.md",
         "priority": 1
       },
       {
         "path": "low-priority-context.md",
         "priority": 10
       }
     ]
   }
   ```

2. **Disable conflicting hooks**:

   ```json
   {
     "hooks": {
       "conflicting-hook": {
         "enabled": false,
         "reason": "Conflicts with primary-hook"
       }
     }
   }
   ```

3. **Create unified contexts**:

   ```markdown
   # Unified Guidelines

   ## Primary Standards

   [Your main guidelines here]

   ## Exceptions and Overrides

   [Specific cases where different rules apply]
   ```

### Getting Help

#### Debug Commands

```bash
# Profile debugging
ai-configurator profile debug my-profile
ai-configurator profile validate my-profile
ai-configurator profile benchmark my-profile

# Context debugging
ai-configurator context validate
ai-configurator context list --verbose
ai-configurator context stats

# Hook debugging
ai-configurator hook test my-hook
ai-configurator hook logs my-hook --tail 50
ai-configurator hook validate my-hook

# System debugging
ai-configurator system info
ai-configurator system logs --level debug
```

#### Log Analysis

```bash
# View recent logs
tail -f ~/.kiro/logs/ai-configurator.log

# Search for errors
grep -i error ~/.kiro/logs/ai-configurator.log

# Filter by component
grep "profile" ~/.kiro/logs/ai-configurator.log
grep "context" ~/.kiro/logs/ai-configurator.log
grep "hook" ~/.kiro/logs/ai-configurator.log
```

#### Community Resources

- **Documentation**: [Link to main docs]
- **GitHub Issues**: [Link to issue tracker]
- **Community Forum**: [Link to discussions]
- **Example Repository**: [Link to examples repo]

This comprehensive guide should help you effectively use and customize all template types in the AI Configurator system. Remember to start simple and gradually add complexity as you become more familiar with the system.
