# AI Configurator Example Templates

This directory contains example templates for profiles, contexts, hooks, and complete workflows to help users understand and implement AI Configurator features.

## Directory Structure

```
examples/
├── profiles/           # Profile configuration examples
│   ├── basic/         # Simple, learning-focused profiles
│   └── professional/ # Real-world professional use cases
├── contexts/          # Context file examples
│   ├── domains/      # Domain-specific contexts (data science, DevOps, etc.)
│   └── workflows/    # Workflow-specific contexts (code review, testing, etc.)
├── hooks/            # Hook automation examples
│   └── automation/   # Automation hook examples
└── workflows/        # Complete integrated workflow examples
```

## Template Categories

### Basic Examples

- **Purpose**: Learning and getting started
- **Complexity**: Simple, single-purpose configurations
- **Target Users**: New users, students, individual contributors

### Professional Examples

- **Purpose**: Real-world professional use cases
- **Complexity**: Moderate, role-specific configurations
- **Target Users**: Working professionals, specialists

### Advanced Examples

- **Purpose**: Complex integration scenarios
- **Complexity**: High, multi-component workflows
- **Target Users**: Team leads, architects, power users

## Template Metadata

All templates include standardized metadata with the following structure:

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

## Usage

1. Browse the appropriate category directory for your use case
2. Copy the template files to your AI Configurator configuration directory
3. Customize the templates according to your specific needs
4. Refer to the inline documentation and README files for guidance

## Template Validation

All templates are validated using the built-in template validation system:

```python
from ai_configurator.core.template_validator import TemplateValidator

validator = TemplateValidator()
result = validator.validate_template_file(Path("path/to/template.json"))

if result.is_valid:
    print("Template is valid!")
else:
    print(f"Validation errors: {result.errors}")
```

## Contributing

When adding new templates:

1. Follow the established directory structure
2. Include complete metadata in all templates
3. Add comprehensive inline documentation
4. Test templates using the validation system
5. Update this README if adding new categories

## Template Infrastructure

The template system is built on:

- **Template Models**: Base classes and interfaces for all template types
- **Template Validator**: Schema validation and quality checking
- **Template Registry**: Management and discovery of available templates

For more information, see the source code in `src/ai_configurator/core/template_*.py`.
