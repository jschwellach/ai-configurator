# Design Document

## Overview

This design transforms the AI Configurator from a complex JSON/Python-based configuration system to a simplified YAML + Markdown approach. The new system will maintain backward compatibility while providing an intuitive way to define profiles, hooks, and contexts using declarative configuration files.

The core principle is to replace programmatic configuration with declarative files that are easier to read, write, and maintain. Users will be able to create new profiles and hooks by simply adding YAML files to designated directories, with optional Markdown files for documentation and context.

## Architecture

### Current vs New Structure

**Current Structure:**
```
configs/
├── profiles/
│   └── {profile}/
│       ├── context.json
│       └── hooks.json
hooks/
├── config.yaml
├── context_loader.py
└── {hook_name}.py
```

**New Structure:**
```
profiles/
├── {profile}.yaml
└── {profile}.md (optional)
hooks/
├── {hook}.yaml
└── {hook}.md (optional)
contexts/
├── {context}.md
└── shared/
    └── {shared_context}.md
```

### Configuration Loading Strategy

The system will implement a layered configuration loading approach:

1. **Discovery Phase**: Scan directories for YAML files using naming conventions
2. **Parsing Phase**: Load YAML with frontmatter support for Markdown files
3. **Validation Phase**: Validate against schemas with detailed error reporting
4. **Merge Phase**: Combine configurations with precedence rules
5. **Cache Phase**: Cache parsed configurations with file watching for hot-reload

## Components and Interfaces

### YamlConfigLoader

Primary component responsible for loading and parsing YAML configurations.
**Key Me
thods:**
- `load_profile(profile_name: str) -> ProfileConfig`
- `load_hook(hook_name: str) -> HookConfig`
- `discover_configurations() -> Dict[str, List[str]]`
- `validate_yaml_file(file_path: Path) -> ValidationResult`

### MarkdownProcessor

Handles Markdown files with YAML frontmatter support.

**Key Methods:**
- `parse_frontmatter(content: str) -> Tuple[Dict, str]`
- `load_context_file(file_path: Path) -> ContextFile`
- `extract_metadata(markdown_content: str) -> Dict[str, Any]`

### ConfigurationMerger

Manages merging of legacy JSON configs with new YAML configs.

**Key Methods:**
- `merge_profile_configs(yaml_config: Dict, json_config: Dict) -> ProfileConfig`
- `detect_conflicts(configs: List[Dict]) -> List[ConflictReport]`
- `apply_precedence_rules(configs: List[Dict]) -> Dict`

### FileWatcher

Provides hot-reload functionality for development.

**Key Methods:**
- `watch_directory(path: Path, callback: Callable)`
- `start_watching() -> None`
- `stop_watching() -> None`

## Data Models

### New YAML Schema Definitions

**Profile YAML Schema:**
```yaml
# profile-name.yaml
name: "developer"
description: "Development environment profile"
version: "1.0"

contexts:
  - "contexts/development-guidelines.md"
  - "contexts/aws-best-practices.md"
  - "shared/*.md"

hooks:
  on_session_start:
    - name: "setup-dev-env"
      enabled: true
      timeout: 30
  per_user_message:
    - name: "context-enhancer"
      enabled: true

mcp_servers:
  - "development"
  - "core"

settings:
  auto_backup: true
  validation_level: "strict"
```

**Hook YAML Schema:**
```yaml
# hook-name.yaml
name: "setup-dev-env"
description: "Initialize development environment"
version: "1.0"
type: "context"  # context, script, or hybrid

trigger: "on_session_start"
timeout: 30
enabled: true

context:
  sources:
    - "contexts/development-setup.md"
    - "contexts/troubleshooting.md"
  
script:
  command: "python"
  args: ["scripts/setup.py"]
  env:
    DEV_MODE: "true"

conditions:
  - profile: ["developer", "solutions-architect"]
  - platform: ["darwin", "linux"]
```

### Enhanced Models

**ProfileConfig (Enhanced):**
```python
class ProfileConfig(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    contexts: List[str] = Field(default_factory=list)
    hooks: Dict[str, List[HookReference]] = Field(default_factory=dict)
    mcp_servers: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**HookConfig (New):**
```python
class HookConfig(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    type: Literal["context", "script", "hybrid"] = "context"
    trigger: str
    timeout: int = 30
    enabled: bool = True
    context: Optional[ContextConfig] = None
    script: Optional[ScriptConfig] = None
    conditions: List[ConditionConfig] = Field(default_factory=list)
```

## Error Handling

### Validation Strategy

1. **Schema Validation**: Use Pydantic models with detailed error messages
2. **File Reference Validation**: Check that all referenced files exist
3. **Circular Dependency Detection**: Prevent infinite loops in context inclusion
4. **Syntax Error Reporting**: Provide line numbers and context for YAML errors

### Error Recovery

- **Graceful Degradation**: Continue loading valid configurations when some fail
- **Fallback Mechanisms**: Use default configurations when custom ones fail
- **Error Aggregation**: Collect and report all errors at once rather than failing fast
- **Partial Loading**: Allow profiles to load even if some hooks fail

## Testing Strategy

### Unit Testing Approach

1. **Configuration Loading Tests**: Test YAML parsing with various valid/invalid inputs
2. **Validation Tests**: Ensure proper error reporting for malformed configurations
3. **Merge Logic Tests**: Verify correct precedence handling between JSON and YAML
4. **File Watching Tests**: Test hot-reload functionality with mock file system events

### Integration Testing

1. **End-to-End Profile Loading**: Test complete profile activation workflow
2. **Hook Execution Tests**: Verify hooks execute correctly with new configuration format
3. **Migration Tests**: Test conversion from JSON to YAML configurations
4. **Performance Tests**: Ensure configuration loading remains fast with new format

### Test Data Structure

```
tests/
├── fixtures/
│   ├── profiles/
│   │   ├── valid/
│   │   └── invalid/
│   ├── hooks/
│   │   ├── valid/
│   │   └── invalid/
│   └── contexts/
├── unit/
│   ├── test_yaml_loader.py
│   ├── test_markdown_processor.py
│   └── test_config_merger.py
└── integration/
    ├── test_profile_loading.py
    └── test_migration.py
```

## Migration Strategy

### Backward Compatibility

The system will support both formats simultaneously during a transition period:

1. **Dual Loading**: Load both JSON and YAML configurations
2. **Precedence Rules**: YAML takes precedence over JSON when both exist
3. **Conversion Utility**: Provide `ai-config migrate` command to convert JSON to YAML
4. **Deprecation Warnings**: Log warnings when JSON configurations are used

### Migration Command Design

```bash
ai-config migrate --from json --to yaml --profile developer
ai-config migrate --all --backup
ai-config migrate --dry-run --verbose
```

The migration process will:
1. Create backups of existing configurations
2. Convert JSON structures to equivalent YAML
3. Validate converted configurations
4. Optionally remove old JSON files after successful conversion

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load configurations only when needed
2. **Caching**: Cache parsed configurations with file modification time checks
3. **Parallel Loading**: Load multiple configuration files concurrently
4. **Memory Management**: Use generators for large context file processing

### File Watching Efficiency

- **Debouncing**: Prevent excessive reloads during rapid file changes
- **Selective Watching**: Only watch directories that contain configuration files
- **Resource Cleanup**: Properly dispose of file watchers when not needed

This design provides a foundation for transforming the AI Configurator into a more user-friendly, maintainable system while preserving existing functionality and providing a smooth migration path.