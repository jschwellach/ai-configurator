"""Comprehensive unit tests for template validation system."""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

from src.ai_configurator.core.template_validator import (
    TemplateValidator,
    TemplateMetadata,
    ProfileTemplateSchema,
    ContextTemplateSchema,
    HookTemplateSchema
)
from src.ai_configurator.core.models import ConfigurationError, ValidationReport


class TestTemplateValidatorComprehensive:
    """Comprehensive tests for template validator functionality."""
    
    @pytest.fixture
    def temp_examples_dir(self):
        """Create a comprehensive temporary examples directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create comprehensive directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "profiles" / "advanced").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "contexts" / "integrations").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "hooks" / "enhancement").mkdir(parents=True)
            (examples_dir / "hooks" / "integration").mkdir(parents=True)
            (examples_dir / "workflows" / "complete-setup").mkdir(parents=True)
            (examples_dir / "workflows" / "content-creation").mkdir(parents=True)
            
            yield examples_dir
    
    @pytest.fixture
    def validator(self, temp_examples_dir):
        """Create a template validator with comprehensive test directory."""
        return TemplateValidator(temp_examples_dir)
    
    def test_comprehensive_template_discovery(self, validator, temp_examples_dir):
        """Test comprehensive template file discovery across all categories."""
        # Create test files in all categories
        test_files = [
            # Profiles
            temp_examples_dir / "profiles" / "basic" / "minimal.json",
            temp_examples_dir / "profiles" / "professional" / "data-scientist.json",
            temp_examples_dir / "profiles" / "advanced" / "architect.json",
            # Contexts
            temp_examples_dir / "contexts" / "domains" / "data-science.md",
            temp_examples_dir / "contexts" / "workflows" / "code-review.md",
            temp_examples_dir / "contexts" / "integrations" / "aws-patterns.md",
            # Hooks
            temp_examples_dir / "hooks" / "automation" / "auto-doc.yaml",
            temp_examples_dir / "hooks" / "enhancement" / "smart-suggest.yaml",
            temp_examples_dir / "hooks" / "integration" / "git-workflow.yaml",
            # Workflows
            temp_examples_dir / "workflows" / "complete-setup" / "profile.json",
            temp_examples_dir / "workflows" / "content-creation" / "hooks.yaml",
        ]
        
        for file_path in test_files:
            file_path.touch()
        
        discovered_files = validator._discover_template_files()
        
        assert len(discovered_files) == len(test_files)
        
        # Verify all file types are discovered
        json_files = [f for f in discovered_files if f.suffix == '.json']
        md_files = [f for f in discovered_files if f.suffix == '.md']
        yaml_files = [f for f in discovered_files if f.suffix in ['.yaml', '.yml']]
        
        assert len(json_files) == 2  # 2 profile + 1 workflow profile
        assert len(md_files) == 3
        assert len(yaml_files) == 4  # 3 hooks + 1 workflow hook
    
    def test_template_type_determination_edge_cases(self, validator, temp_examples_dir):
        """Test template type determination for edge cases."""
        # Test various file path patterns
        test_cases = [
            (temp_examples_dir / "profiles" / "nested" / "deep" / "test.json", "profile"),
            (temp_examples_dir / "contexts" / "test.md", "context"),
            (temp_examples_dir / "hooks" / "test.yml", "hook"),
            (temp_examples_dir / "workflows" / "test" / "profile.json", "profile"),
            (temp_examples_dir / "workflows" / "test" / "hook.yaml", "hook"),
            (temp_examples_dir / "other" / "test.json", "unknown"),
            (temp_examples_dir / "profiles" / "test.txt", "unknown"),
        ]
        
        for file_path, expected_type in test_cases:
            result = validator._determine_template_type(file_path)
            assert result == expected_type, f"Failed for {file_path}: expected {expected_type}, got {result}"
    
    def test_json_parsing_with_complex_comments(self, validator):
        """Test JSON parsing with complex comment patterns."""
        complex_json = '''
        {
            // Single line comment
            "name": "test",
            /* Multi-line
               comment */
            "description": "A test // not a comment in string",
            "paths": [
                "path1.md", // Comment after value
                /* Another comment */ "path2.md"
            ],
            // Nested object with comments
            "metadata": {
                "version": "1.0.0", // Version comment
                /* Complex
                   multi-line
                   comment */
                "tags": ["tag1", "tag2"]
            }
        }
        '''
        
        result = validator._parse_json_with_comments(complex_json, Path("test.json"), [])
        
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test // not a comment in string"
        assert len(result["paths"]) == 2
        assert result["metadata"]["version"] == "1.0.0"
        assert len(result["metadata"]["tags"]) == 2
    
    def test_json_parsing_error_handling(self, validator):
        """Test JSON parsing with various error conditions."""
        error_cases = [
            ('{"name": "test",}', "trailing comma"),
            ('{"name": "test" "missing": "comma"}', "missing comma"),
            ('{"name": "test", "unclosed": "string}', "unclosed string"),
            ('{"name": "test", "invalid": }', "invalid value"),
            ('{"name": "test", "duplicate": 1, "duplicate": 2}', "duplicate keys"),
        ]
        
        for json_content, description in error_cases:
            errors = []
            result = validator._parse_json_with_comments(json_content, Path("test.json"), errors)
            
            assert result is None, f"Should fail for {description}"
            assert len(errors) == 1, f"Should have one error for {description}"
            assert errors[0].error_type == "JSONSyntaxError"
    
    def test_yaml_parsing_with_complex_structures(self, validator):
        """Test YAML parsing with complex structures and edge cases."""
        complex_yaml = '''
        name: test-hook
        description: |
          Multi-line description
          with special characters: @#$%^&*()
          and unicode: 🚀 ✨ 🎯
        
        config:
          nested:
            deeply:
              nested: value
          list:
            - item1
            - item2:
                sub_item: value
          boolean_values:
            - true
            - false
            - yes
            - no
        
        # YAML comment
        metadata:
          tags: [tag1, tag2, tag3]
          numbers:
            integer: 42
            float: 3.14
            scientific: 1.23e-4
        '''
        
        result = validator._parse_yaml_with_errors(complex_yaml, Path("test.yaml"), [])
        
        assert result is not None
        assert result["name"] == "test-hook"
        assert "Multi-line description" in result["description"]
        assert result["config"]["nested"]["deeply"]["nested"] == "value"
        assert len(result["config"]["list"]) == 2
        assert result["metadata"]["numbers"]["integer"] == 42
        assert result["metadata"]["numbers"]["float"] == 3.14
    
    def test_yaml_parsing_error_conditions(self, validator):
        """Test YAML parsing with various error conditions."""
        error_cases = [
            ('name: test\n  invalid_indent: value', "invalid indentation"),
            ('name: test\nlist:\n  - item1\n - item2', "inconsistent indentation"),
            ('name: test\ninvalid: [unclosed list', "unclosed bracket"),
            ('name: test\ninvalid: {unclosed: dict', "unclosed brace"),
            ('name: test\ninvalid: |', "incomplete literal block"),
        ]
        
        for yaml_content, description in error_cases:
            errors = []
            result = validator._parse_yaml_with_errors(yaml_content, Path("test.yaml"), errors)
            
            assert result is None, f"Should fail for {description}"
            assert len(errors) == 1, f"Should have one error for {description}"
            assert errors[0].error_type == "YAMLSyntaxError"
    
    def test_markdown_frontmatter_parsing_edge_cases(self, validator):
        """Test markdown frontmatter parsing with edge cases."""
        test_cases = [
            # Standard frontmatter
            ('---\ntitle: Test\n---\n# Content', {"title": "Test"}, "# Content"),
            # Frontmatter with complex YAML
            ('---\nmetadata:\n  tags: [a, b]\n  nested:\n    value: 42\n---\nContent', 
             {"metadata": {"tags": ["a", "b"], "nested": {"value": 42}}}, "Content"),
            # No frontmatter
            ('# Just content\nNo frontmatter here', None, '# Just content\nNo frontmatter here'),
            # Empty frontmatter
            ('---\n---\n# Content', {}, "# Content"),
            # Frontmatter without closing marker
            ('---\ntitle: Test\n# Content', None, '---\ntitle: Test\n# Content'),
            # Multiple frontmatter-like sections
            ('---\ntitle: Test\n---\n# Content\n---\nNot frontmatter\n---', 
             {"title": "Test"}, "# Content\n---\nNot frontmatter\n---"),
        ]
        
        for content, expected_frontmatter, expected_content in test_cases:
            frontmatter, main_content = validator._parse_markdown_frontmatter(content)
            
            assert frontmatter == expected_frontmatter
            assert main_content.strip() == expected_content.strip()
    
    def test_profile_validation_comprehensive(self, validator):
        """Test comprehensive profile validation with various scenarios."""
        test_cases = [
            # Valid comprehensive profile
            {
                "data": {
                    "metadata": {
                        "name": "comprehensive-profile",
                        "description": "A comprehensive test profile with all fields",
                        "category": "professional",
                        "version": "2.1.0",
                        "author": "Test Author",
                        "created": "2024-01-01",
                        "updated": "2024-02-01",
                        "tags": ["test", "comprehensive", "example"],
                        "complexity": "high",
                        "prerequisites": ["basic-knowledge", "tools-installed"],
                        "related_templates": ["related-profile", "another-profile"]
                    },
                    "paths": [
                        "contexts/domains/data-science.md",
                        "contexts/workflows/ml-pipeline.md"
                    ],
                    "hooks": {
                        "auto-documentation": {"enabled": true},
                        "quality-check": {"enabled": false}
                    },
                    "settings": {
                        "auto_reload": true,
                        "max_contexts": 100,
                        "validation_level": "strict"
                    }
                },
                "should_pass": True,
                "expected_warnings": 0
            },
            # Profile with minimal required fields
            {
                "data": {
                    "metadata": {
                        "name": "minimal-profile",
                        "description": "Minimal profile",
                        "category": "basic",
                        "complexity": "low",
                        "created": "2024-01-01"
                    },
                    "paths": ["contexts/basic.md"]
                },
                "should_pass": True,
                "expected_warnings": 0
            },
            # Profile with validation issues
            {
                "data": {
                    "metadata": {
                        "name": "problematic-profile",
                        "description": "Bad",  # Too short
                        "category": "basic",
                        "complexity": "low",
                        "created": "2024-01-01"
                    },
                    "paths": []  # Empty paths
                },
                "should_pass": True,  # Schema validation passes
                "expected_warnings": 2  # Short description + empty paths
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            errors = []
            warnings = []
            info = []
            
            validator._validate_profile_rules(
                Path(f"test{i}.json"), 
                test_case["data"], 
                errors, 
                warnings, 
                info
            )
            
            if test_case["should_pass"]:
                assert len(errors) == 0, f"Test case {i} should not have errors"
            
            assert len(warnings) == test_case["expected_warnings"], \
                f"Test case {i} expected {test_case['expected_warnings']} warnings, got {len(warnings)}"
    
    def test_context_validation_comprehensive(self, validator):
        """Test comprehensive context validation scenarios."""
        test_cases = [
            # Excellent context
            {
                "content": """# Comprehensive Development Guide

## Overview

This comprehensive guide provides detailed information about development best practices,
covering everything from initial setup to advanced deployment strategies. It includes
practical examples, code snippets, and real-world scenarios.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following tools installed:

- Python 3.8 or higher
- Git version control
- Docker for containerization

### Installation

```bash
# Clone the repository
git clone https://github.com/example/project.git

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

## Best Practices

### Code Quality

1. **Write Clean Code**: Follow PEP 8 guidelines
2. **Add Documentation**: Document all functions and classes
3. **Test Everything**: Maintain high test coverage

```python
def calculate_metrics(data: List[Dict]) -> Dict[str, float]:
    \"\"\"Calculate performance metrics from data.
    
    Args:
        data: List of data dictionaries
        
    Returns:
        Dictionary containing calculated metrics
    \"\"\"
    return {"accuracy": 0.95, "precision": 0.92}
```

### Testing Strategies

For instance, when writing unit tests, consider these scenarios:
- Happy path testing
- Edge case validation
- Error condition handling

Such as in situations where you need to test API endpoints:

```python
def test_api_endpoint():
    response = client.get("/api/data")
    assert response.status_code == 200
```

## Advanced Topics

### Performance Optimization

When you encounter performance issues, consider:
- Database query optimization
- Caching strategies
- Asynchronous processing

### Security Considerations

In real-world applications, always:
- Validate user input
- Use HTTPS for all communications
- Implement proper authentication

## Conclusion

This guide provides a comprehensive foundation for development practices.
Follow these guidelines to ensure high-quality, maintainable code.
""",
                "frontmatter": {
                    "name": "comprehensive-guide",
                    "description": "Comprehensive development guide",
                    "tags": ["development", "best-practices", "guide"],
                    "categories": ["development", "documentation"]
                },
                "expected_warnings": 0
            },
            # Short, poorly structured context
            {
                "content": """Development tips:
- Write code
- Test code
- Deploy code""",
                "frontmatter": None,
                "expected_warnings": 4  # Short content, missing header, missing code examples, missing structure
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            errors = []
            warnings = []
            info = []
            
            validator._validate_context_rules(
                Path(f"test{i}.md"),
                test_case["content"],
                test_case["frontmatter"],
                errors,
                warnings,
                info
            )
            
            assert len(warnings) == test_case["expected_warnings"], \
                f"Test case {i} expected {test_case['expected_warnings']} warnings, got {len(warnings)}"
    
    def test_hook_validation_comprehensive(self, validator, temp_examples_dir):
        """Test comprehensive hook validation scenarios."""
        test_cases = [
            # Excellent hook configuration
            {
                "data": {
                    "name": "comprehensive-hook",
                    "description": "A comprehensive hook with all features configured properly",
                    "version": "2.0.0",
                    "type": "context",
                    "trigger": "on_session_start",
                    "timeout": 45,
                    "enabled": True,
                    "metadata": {
                        "name": "comprehensive-hook",
                        "description": "Comprehensive hook for testing",
                        "category": "automation",
                        "complexity": "medium",
                        "created": "2024-01-01",
                        "tags": ["automation", "comprehensive"]
                    },
                    "context": {
                        "sources": ["contexts/existing-context.md"],
                        "tags": ["development"],
                        "priority": 1
                    },
                    "conditions": [
                        {"profile": ["data-scientist", "developer"]},
                        {"project_type": ["machine-learning"]}
                    ]
                },
                "create_dependencies": True,
                "expected_errors": 0,
                "expected_warnings": 0
            },
            # Hook with missing dependencies
            {
                "data": {
                    "name": "problematic-hook",
                    "type": "script",
                    "trigger": "on_file_save",
                    "timeout": 200,  # Too long
                    "script": "nonexistent_script.py",
                    "context": {
                        "sources": ["nonexistent_context.md"]
                    }
                },
                "create_dependencies": False,
                "expected_errors": 2,  # Missing script + missing context
                "expected_warnings": 1  # Long timeout
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            # Create dependencies if needed
            if test_case["create_dependencies"]:
                context_file = temp_examples_dir / "contexts" / "existing-context.md"
                context_file.parent.mkdir(parents=True, exist_ok=True)
                context_file.write_text("# Existing Context\n\nThis context exists.")
                
                if "script" in test_case["data"]:
                    script_file = temp_examples_dir / "hooks" / test_case["data"]["script"]
                    script_file.parent.mkdir(parents=True, exist_ok=True)
                    script_file.write_text("# Script content")
            
            errors = []
            warnings = []
            info = []
            
            hook_path = temp_examples_dir / "hooks" / f"test{i}.yaml"
            
            validator._validate_hook_rules(
                hook_path,
                test_case["data"],
                errors,
                warnings,
                info
            )
            
            assert len(errors) == test_case["expected_errors"], \
                f"Test case {i} expected {test_case['expected_errors']} errors, got {len(errors)}"
            assert len(warnings) == test_case["expected_warnings"], \
                f"Test case {i} expected {test_case['expected_warnings']} warnings, got {len(warnings)}"
    
    def test_cross_template_reference_validation(self, validator, temp_examples_dir):
        """Test validation of cross-template references."""
        # Create a profile that references contexts and hooks
        profile_data = {
            "metadata": {
                "name": "test-profile",
                "description": "Profile with references",
                "category": "basic",
                "complexity": "low",
                "created": "2024-01-01"
            },
            "paths": [
                "contexts/domains/existing-context.md",
                "contexts/workflows/missing-context.md"  # This one doesn't exist
            ],
            "hooks": {
                "existing-hook": {"enabled": True},
                "missing-hook": {"enabled": True}  # This one doesn't exist
            }
        }
        
        # Create only some of the referenced files
        existing_context = temp_examples_dir / "contexts" / "domains" / "existing-context.md"
        existing_context.parent.mkdir(parents=True, exist_ok=True)
        existing_context.write_text("# Existing Context")
        
        existing_hook = temp_examples_dir / "hooks" / "automation" / "existing-hook.yaml"
        existing_hook.parent.mkdir(parents=True, exist_ok=True)
        existing_hook.write_text("name: existing-hook\ntrigger: on_session_start")
        
        profile_file = temp_examples_dir / "profiles" / "basic" / "test-profile.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        # Validate the profile
        report = validator.validate_profile_template(profile_file)
        
        # Should have warnings about missing references
        missing_ref_warnings = [
            w for w in report.warnings 
            if w.error_type == "MissingTemplateReference"
        ]
        
        assert len(missing_ref_warnings) >= 1, "Should warn about missing template references"
    
    def test_validation_report_aggregation(self, validator, temp_examples_dir):
        """Test comprehensive validation report aggregation."""
        # Create multiple templates with various issues
        templates = [
            # Valid profile
            ("profiles/basic/valid.json", {
                "metadata": {
                    "name": "valid-profile",
                    "description": "A valid profile template",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01"
                },
                "paths": ["contexts/test.md"]
            }),
            # Invalid profile (missing required fields)
            ("profiles/basic/invalid.json", {
                "name": "invalid-profile"  # Missing metadata structure
            }),
        ]
        
        # Create context with issues
        context_content = "# Short Context\nToo short."
        
        # Create hook with issues
        hook_content = """name: problematic-hook
trigger: invalid_trigger
timeout: 500"""
        
        # Write all test files
        for file_path, data in templates:
            full_path = temp_examples_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                json.dump(data, f)
        
        context_file = temp_examples_dir / "contexts" / "domains" / "short.md"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text(context_content)
        
        hook_file = temp_examples_dir / "hooks" / "automation" / "problematic.yaml"
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        hook_file.write_text(hook_content)
        
        # Run comprehensive validation
        report = validator.validate_all_templates()
        
        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert "total_files" in report.summary
        assert "errors" in report.summary
        assert "warnings" in report.summary
        assert "valid_files" in report.summary
        assert "invalid_files" in report.summary
        
        # Should have some errors and warnings
        assert len(report.errors) > 0, "Should have validation errors"
        assert len(report.warnings) > 0, "Should have validation warnings"
        
        # Verify file tracking
        assert len(report.files_checked) > 0, "Should track checked files"
        assert report.summary["total_files"] == len(set(report.files_checked))
    
    def test_error_recovery_and_resilience(self, validator, temp_examples_dir):
        """Test validator resilience to various error conditions."""
        # Create files with various issues that shouldn't crash the validator
        problematic_files = [
            # Binary file with .json extension
            ("profiles/basic/binary.json", b"\x00\x01\x02\x03"),
            # File with encoding issues
            ("contexts/domains/encoding.md", "# Test\n\xff\xfe Invalid UTF-8"),
            # Extremely large file
            ("contexts/domains/large.md", "# Large File\n" + "x" * 100000),
            # File with null bytes
            ("hooks/automation/null.yaml", "name: test\x00null: value"),
        ]
        
        for file_path, content in problematic_files:
            full_path = temp_examples_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                try:
                    full_path.write_text(content, encoding='utf-8')
                except UnicodeEncodeError:
                    full_path.write_bytes(content.encode('utf-8', errors='ignore'))
        
        # Validator should handle these gracefully without crashing
        try:
            report = validator.validate_all_templates()
            # Should complete without raising exceptions
            assert isinstance(report, ValidationReport)
            # May have errors, but shouldn't crash
        except Exception as e:
            pytest.fail(f"Validator should handle problematic files gracefully, but raised: {e}")
    
    def test_performance_with_large_dataset(self, validator, temp_examples_dir):
        """Test validator performance with a large number of templates."""
        # Create a large number of templates
        num_templates = 50
        
        for i in range(num_templates):
            # Create profiles
            profile_data = {
                "metadata": {
                    "name": f"profile-{i}",
                    "description": f"Test profile number {i}",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01"
                },
                "paths": [f"contexts/context-{i}.md"]
            }
            
            profile_file = temp_examples_dir / "profiles" / "basic" / f"profile-{i}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f)
            
            # Create contexts
            context_content = f"""# Context {i}

## Overview

This is test context number {i} with sufficient content for validation.
It includes multiple sections and adequate length for testing purposes.

## Details

Context {i} provides comprehensive guidance for testing scenario {i}.
This ensures that the validator can handle multiple templates efficiently.

## Examples

```python
def example_{i}():
    return "Example for context {i}"
```

## Conclusion

Context {i} demonstrates proper structure and content organization.
"""
            
            context_file = temp_examples_dir / "contexts" / "domains" / f"context-{i}.md"
            context_file.parent.mkdir(parents=True, exist_ok=True)
            context_file.write_text(context_content)
        
        # Measure validation time (should complete reasonably quickly)
        import time
        start_time = time.time()
        
        report = validator.validate_all_templates()
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Validation should complete within reasonable time (adjust threshold as needed)
        assert validation_time < 30, f"Validation took too long: {validation_time} seconds"
        
        # Verify all templates were processed
        assert report.summary["total_files"] == num_templates * 2  # profiles + contexts
        assert len(report.files_checked) == num_templates * 2