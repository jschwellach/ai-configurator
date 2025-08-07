# Global Contexts

Global contexts are shared context files that are automatically applied to all profiles when installed. They provide organization-wide knowledge, policies, and standards that should be available regardless of the specific profile being used.

## Overview

Global contexts are designed to:
- Provide consistent organizational policies across all profiles
- Share common knowledge and best practices
- Ensure security guidelines are always applied
- Maintain standard terminology and abbreviations

## How Global Contexts Work

When you install any profile using AI Configurator, the system automatically:

1. **Loads global contexts** from the library catalog
2. **Sorts them by priority** (highest priority first)
3. **Copies them to the Amazon Q contexts directory** with a `global-` prefix
4. **Includes them in the profile's context.json** before profile-specific contexts

## Priority System

Global contexts use a priority system to control their loading order:

- **Higher numbers = Higher priority** (loaded first)
- **Same priority** = Sorted alphabetically by name
- **Typical priority ranges:**
  - 100+ : Critical security and compliance contexts
  - 50-99 : Organizational policies and standards
  - 1-49  : General knowledge and terminology
  - 0     : Default priority

## Managing Global Contexts

### List Global Contexts

```bash
# View all global contexts in a table
ai-config list-global

# View as JSON
ai-config list-global --format json
```

### View Global Context Details

```bash
# View detailed information about a specific global context
ai-config info-global aws-security-best-practices

# View as JSON
ai-config info-global aws-security-best-practices --format json
```

## File Structure

Global contexts are stored in the library under:

```
library/
├── global-contexts/
│   ├── aws-security-best-practices.md
│   ├── organizational-policies.md
│   └── common-abbreviations.md
└── catalog.json
```

## Catalog Configuration

Global contexts are defined in the `catalog.json` file:

```json
{
  "version": "1.0.0",
  "global_contexts": [
    {
      "id": "aws-security-best-practices",
      "name": "AWS Security Best Practices",
      "description": "Global security guidelines and best practices for AWS services",
      "version": "1.0.0",
      "file_path": "global-contexts/aws-security-best-practices.md",
      "priority": 100
    }
  ],
  "profiles": [...]
}
```

### Required Fields

- **id**: Unique identifier for the global context
- **name**: Human-readable name
- **description**: Brief description of the context's purpose
- **version**: Semantic version (MAJOR.MINOR.PATCH)
- **file_path**: Relative path from library root to the context file

### Optional Fields

- **priority**: Loading priority (default: 0)

## Installation Behavior

When installing a profile:

1. **Global contexts are copied first** (by priority order)
2. **Profile-specific contexts are copied second**
3. **All contexts are included** in the profile's `context.json`
4. **Global contexts get a `global-` prefix** in the filename

Example resulting structure:
```
~/.aws/amazonq/
├── contexts/
│   ├── global-aws-security-best-practices.md
│   ├── global-organizational-policies.md
│   ├── global-common-abbreviations.md
│   └── basic.md
└── profiles/
    └── default/
        └── context.json
```

## Removal Behavior

When removing a profile:

1. **Global contexts are removed** (files with `global-` prefix)
2. **Profile-specific contexts are removed**
3. **Profile directory is deleted**

## Best Practices

### Content Guidelines

1. **Keep contexts focused** - Each global context should have a single, clear purpose
2. **Use clear headings** - Structure content with markdown headers
3. **Include examples** - Provide concrete examples where applicable
4. **Keep it current** - Regularly update contexts to reflect current practices

### Priority Guidelines

1. **Security contexts** should have the highest priority (100+)
2. **Compliance contexts** should have high priority (80-99)
3. **Organizational policies** should have medium-high priority (50-79)
4. **General knowledge** should have lower priority (1-49)

### File Naming

1. Use **kebab-case** for file names
2. Use **descriptive names** that clearly indicate the content
3. Use **.md extension** for markdown files

## Example Global Contexts

The AI Configurator includes these sample global contexts:

### AWS Security Best Practices (Priority: 100)
- IAM best practices
- Data encryption guidelines
- Network security standards
- Monitoring and logging requirements

### Organizational Policies (Priority: 90)
- Code quality standards
- Documentation requirements
- Compliance guidelines
- Resource management policies

### Common Abbreviations (Priority: 10)
- AWS service abbreviations
- Technical terminology
- Business terms
- Communication standards

## Troubleshooting

### Global Context Not Applied

If a global context isn't being applied:

1. Check if it's listed in `ai-config list-global`
2. Verify the file exists at the specified path
3. Check the catalog.json syntax
4. Reinstall the profile to refresh contexts

### Priority Not Working

If contexts aren't loading in the expected order:

1. Verify priority values in catalog.json
2. Remember: higher numbers = higher priority
3. Check for duplicate priorities (sorted alphabetically)
4. Reinstall the profile to refresh order

### File Not Found Errors

If you get file not found errors:

1. Verify the file_path in catalog.json is correct
2. Check that the file exists in the library
3. Ensure proper file permissions
4. Check for typos in the file path

## Development

### Adding New Global Contexts

1. Create the context file in `library/global-contexts/`
2. Add an entry to `catalog.json` in the `global_contexts` array
3. Set appropriate priority based on content type
4. Test with `ai-config list-global`
5. Test installation with a profile

### Modifying Existing Contexts

1. Update the context file content
2. Consider updating the version in catalog.json
3. Test with profile reinstallation
4. Document changes in version control

### Schema Validation

The catalog schema validates:
- Required fields are present
- Version follows semantic versioning
- File paths are strings
- Priority is an integer

---

Global contexts provide a powerful way to ensure consistent knowledge and policies across all your Amazon Q CLI profiles. Use them to maintain organizational standards while allowing profile-specific customization.
