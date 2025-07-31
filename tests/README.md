# AI Configurator Test Suite

This directory contains the comprehensive test suite for the AI Configurator YAML configuration system.

## Test Structure

### Unit Tests (`tests/unit/`)
- `test_yaml_loader.py` - Unit tests for YamlConfigLoader functionality
- `test_validator.py` - Unit tests for ConfigurationValidator functionality
- `test_config_merger.py` - Unit tests for ConfigurationMerger functionality
- `test_context_manager_markdown.py` - Unit tests for context manager markdown processing
- `test_directory_manager.py` - Unit tests for directory management functionality
- `test_file_watcher.py` - Unit tests for file watching functionality
- `test_hook_manager_enhanced.py` - Unit tests for enhanced hook manager
- `test_markdown_processor.py` - Unit tests for markdown processing
- `test_profile_manager.py` - Unit tests for profile management
- `test_yaml_loader_edge_cases.py` - Edge case tests for YAML loading

### Integration Tests (`tests/integration/`)
- `test_profile_loading_workflow.py` - Integration tests for profile loading workflows
- `test_hook_loading_workflow.py` - Integration tests for hook loading workflows
### Test Fixtures (`tests/fixtures/`)
- `profiles/valid/` - Valid profile configurations for testing
- `profiles/invalid/` - Invalid profile configurations for error testing
- `hooks/valid/` - Valid hook configurations for testing
- `hooks/invalid/` - Invalid hook configurations for error testing
- `contexts/` - Context files referenced by profiles and hooks

## Test Coverage

The test suite covers the following requirements from task 12:

### ✅ Unit Tests for YAML Loading
- Configuration discovery functionality
- Profile and hook loading with caching
- Error handling for malformed YAML
- File not found scenarios
- Null value handling

### ✅ Unit Tests for Validation
- YAML syntax validation with line numbers
- Schema validation for profiles and hooks
- Missing required field detection
- Invalid field value detection
- File reference validation

### ✅ Integration Tests for Workflows
- Complete profile loading workflow
- Hook loading and validation workflow
- Error propagation through the system
- Caching across workflow components

### ✅ Test Fixtures with Valid and Invalid Configurations
- **Valid Configurations:**
  - `developer.yaml` - Full-featured development profile
  - `solutions-architect.yaml` - AWS-focused profile
  - `minimal.yaml` - Minimal valid profile
  - `setup-dev-env.yaml` - Context hook for development setup
  - `context-enhancer.yaml` - Message enhancement hook

- **Invalid Configurations:**
  - `missing-name.yaml` - Profile missing required name field
  - `syntax-error.yaml` - YAML with syntax errors
  - `broken-references.yaml` - Profile with broken file references
  - `missing-trigger.yaml` - Hook missing required trigger field
  - `invalid-trigger.yaml` - Hook with invalid trigger value

### ✅ Error Handling Tests
- YAML syntax errors with file names and line numbers (Requirement 1.3)
- Missing required fields listed in single error message (Requirement 2.4)
- Broken file references reported with specific file names (Requirement 6.1)
- Configuration summary when validation passes (Requirement 6.4)

## Running Tests

### Run All Tests
```bash
python tests/test_comprehensive_suite.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python tests/test_comprehensive_suite.py --category unit

# Integration tests only
python tests/test_comprehensive_suite.py --category integration

# YAML loader tests only
python tests/test_comprehensive_suite.py --category yaml

# Validation tests only
python tests/test_comprehensive_suite.py --category validation
```

### Run Individual Test Files
```bash
# Comprehensive validation tests
python -m pytest tests/test_comprehensive_yaml_validation.py -v

# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

### Validate Test Environment
```bash
python tests/test_comprehensive_suite.py --validate-env
```

## Test Results Summary

The comprehensive test suite successfully validates:

1. **YAML Loading Functionality** - All core loading operations work correctly
2. **Validation System** - Comprehensive error detection and reporting
3. **Error Handling** - Proper error messages with context and line numbers
4. **File Reference Validation** - Detection of missing referenced files
5. **Schema Validation** - Enforcement of required fields and valid values
6. **Caching System** - Performance optimization through caching
7. **Integration Workflows** - End-to-end functionality across components

## Coverage Statistics

The test suite achieves significant code coverage across the core modules:
- `yaml_loader.py` - 52-60% coverage
- `validator.py` - 66-75% coverage  
- `models.py` - 93-98% coverage

## Test Configuration

Tests use pytest with the following configuration:
- Temporary directories for isolated test environments
- Comprehensive fixtures with realistic configurations
- Detailed error reporting and context validation
- Coverage reporting when available
- Proper cleanup of test resources