# Design Document: Example Templates System

## Overview

The Example Templates System will provide a comprehensive collection of pre-defined profiles, contexts, and hooks that serve as starting points and learning resources for users of the AI Configurator. The system will include both basic examples for learning and advanced examples demonstrating real-world integration patterns.

Based on the current system analysis, we have:

- **Profiles**: JSON-based configuration files that define context paths and hooks
- **Contexts**: Markdown files containing domain-specific guidance and best practices
- **Hooks**: YAML configuration files and Python scripts for automation workflows

The design will expand the existing examples while maintaining consistency with current patterns and introducing new categories to cover common use cases.

## Architecture

### Directory Structure

```
examples/
├── profiles/
│   ├── basic/
│   │   ├── minimal.json
│   │   ├── content-creator.json
│   │   └── student.json
│   ├── professional/
│   │   ├── data-scientist.json
│   │   ├── devops-engineer.json
│   │   ├── security-specialist.json
│   │   └── technical-writer.json
│   └── advanced/
│       ├── multi-team-lead.json
│       └── consulting-architect.json
├── contexts/
│   ├── domains/
│   │   ├── data-science-best-practices.md
│   │   ├── devops-methodologies.md
│   │   ├── security-guidelines.md
│   │   ├── technical-writing-standards.md
│   │   ├── content-creation-guidelines.md
│   │   └── academic-research-methods.md
│   ├── workflows/
│   │   ├── code-review-process.md
│   │   ├── incident-response.md
│   │   ├── documentation-workflow.md
│   │   └── testing-strategies.md
│   └── integrations/
│       ├── aws-integration-patterns.md
│       ├── ci-cd-best-practices.md
│       └── monitoring-and-observability.md
├── hooks/
│   ├── automation/
│   │   ├── auto-documentation.yaml
│   │   ├── code-quality-check.yaml
│   │   └── environment-setup.yaml
│   ├── enhancement/
│   │   ├── context-switcher.yaml
│   │   ├── smart-suggestions.yaml
│   │   └── workflow-optimizer.yaml
│   └── integration/
│       ├── git-workflow.yaml
│       ├── slack-notifications.yaml
│       └── jira-integration.yaml
└── workflows/
    ├── complete-dev-setup/
    │   ├── profile.json
    │   ├── contexts/
    │   └── hooks/
    └── content-creation-suite/
        ├── profile.json
        ├── contexts/
        └── hooks/
```

### Template Categories

#### 1. Basic Examples

- **Purpose**: Learning and getting started
- **Complexity**: Simple, single-purpose configurations
- **Documentation**: Extensive inline comments and explanations
- **Target Users**: New users, students, individual contributors

#### 2. Professional Examples

- **Purpose**: Real-world professional use cases
- **Complexity**: Moderate, role-specific configurations
- **Documentation**: Best practices and customization guides
- **Target Users**: Working professionals, specialists

#### 3. Advanced Examples

- **Purpose**: Complex integration scenarios
- **Complexity**: High, multi-component workflows
- **Documentation**: Architecture explanations and extension guides
- **Target Users**: Team leads, architects, power users

#### 4. Complete Workflows

- **Purpose**: End-to-end example implementations
- **Complexity**: Full integration of profiles, contexts, and hooks
- **Documentation**: Complete setup and customization guides
- **Target Users**: Teams implementing comprehensive solutions

## Components and Interfaces

### Template Metadata System

Each template will include standardized metadata:

```json
{
  "metadata": {
    "name": "template-name",
    "description": "Brief description of the template",
    "category": "basic|professional|advanced",
    "version": "1.0.0",
    "author": "AI Configurator Team",
    "created": "2024-01-01",
    "updated": "2024-01-01",
    "tags": ["tag1", "tag2"],
    "complexity": "low|medium|high",
    "prerequisites": ["requirement1", "requirement2"],
    "related_templates": ["template1", "template2"]
  }
}
```

### Documentation Standards

#### Inline Documentation

- **Profiles**: JSON comments explaining each configuration option
- **Contexts**: Markdown headers and sections explaining content purpose
- **Hooks**: YAML comments describing triggers and actions

#### Template Documentation

Each template directory will include:

- `README.md`: Overview, setup instructions, customization guide
- `EXAMPLES.md`: Usage examples and common modifications
- `TROUBLESHOOTING.md`: Common issues and solutions

### Integration Patterns

#### Profile-Context Integration

```json
{
  "paths": [
    "examples/contexts/domains/data-science-best-practices.md",
    "examples/contexts/workflows/code-review-process.md"
  ],
  "metadata": {
    "context_relationships": {
      "primary": "data-science-best-practices.md",
      "supporting": ["code-review-process.md"],
      "optional": ["aws-integration-patterns.md"]
    }
  }
}
```

#### Hook-Profile Integration

```yaml
name: "smart-data-context"
description: "Dynamically load data science contexts based on project type"
trigger: "on_session_start"
conditions:
  - profile: ["data-scientist", "ml-engineer"]
    project_type: ["machine-learning", "data-analysis"]
```

## Data Models

### Template Registry

```python
@dataclass
class TemplateInfo:
    name: str
    path: str
    category: str
    template_type: str  # profile, context, hook, workflow
    metadata: Dict[str, Any]
    dependencies: List[str]
    related_templates: List[str]

@dataclass
class TemplateRegistry:
    templates: Dict[str, TemplateInfo]
    categories: Dict[str, List[str]]
    relationships: Dict[str, List[str]]
```

### Template Validation Schema

```python
PROFILE_TEMPLATE_SCHEMA = {
    "type": "object",
    "required": ["metadata", "paths"],
    "properties": {
        "metadata": {"$ref": "#/definitions/metadata"},
        "paths": {"type": "array", "items": {"type": "string"}},
        "hooks": {"type": "object"},
        "settings": {"type": "object"}
    }
}

CONTEXT_TEMPLATE_SCHEMA = {
    "type": "object",
    "required": ["metadata", "content"],
    "properties": {
        "metadata": {"$ref": "#/definitions/metadata"},
        "content": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}}
    }
}
```

## Error Handling

### Template Validation

- **Schema Validation**: Ensure all templates conform to defined schemas
- **Dependency Checking**: Verify all referenced files exist
- **Circular Dependency Detection**: Prevent infinite loops in template relationships
- **Version Compatibility**: Check template versions against system requirements

### Runtime Error Handling

- **Missing Dependencies**: Graceful degradation when referenced templates are unavailable
- **Permission Issues**: Clear error messages for file access problems
- **Malformed Templates**: Detailed validation error reporting
- **Hook Execution Failures**: Fallback mechanisms for failed hook execution

### Error Recovery Strategies

```python
class TemplateErrorHandler:
    def handle_missing_dependency(self, template_name: str, missing_dep: str):
        # Log warning and continue with available templates
        pass

    def handle_validation_error(self, template_path: str, errors: List[str]):
        # Provide detailed error report and suggestions
        pass

    def handle_execution_error(self, hook_name: str, error: Exception):
        # Implement fallback behavior and error reporting
        pass
```

## Testing Strategy

### Unit Testing

- **Template Validation**: Test schema validation for all template types
- **Metadata Processing**: Verify metadata parsing and validation
- **Dependency Resolution**: Test template relationship resolution
- **Error Handling**: Validate error handling for various failure scenarios

### Integration Testing

- **Template Loading**: Test complete template loading workflows
- **Profile-Context Integration**: Verify context loading from profiles
- **Hook Execution**: Test hook triggering and execution
- **Cross-Template Dependencies**: Validate complex template relationships

### End-to-End Testing

- **Complete Workflows**: Test full workflow examples from start to finish
- **User Scenarios**: Simulate common user interaction patterns
- **Performance Testing**: Ensure template loading doesn't impact system performance
- **Compatibility Testing**: Verify templates work across different system configurations

### Template Quality Assurance

```python
class TemplateQualityChecker:
    def check_documentation_completeness(self, template_path: str) -> bool:
        # Verify all required documentation is present
        pass

    def validate_example_accuracy(self, template_path: str) -> bool:
        # Ensure examples work as documented
        pass

    def check_best_practices_compliance(self, template_path: str) -> bool:
        # Verify templates follow established best practices
        pass
```

### Automated Testing Pipeline

- **Template Validation**: Automated validation of all templates on commit
- **Documentation Generation**: Auto-generate template catalogs and documentation
- **Example Verification**: Automated testing of all example configurations
- **Performance Benchmarking**: Regular performance testing of template loading
