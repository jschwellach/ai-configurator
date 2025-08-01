"""Unit tests for template validation system."""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.ai_configurator.core.template_validator import (
    TemplateValidator,
    TemplateMetadata,
    ProfileTemplateSchema,
    ContextTemplateSchema,
    HookTemplateSchema
)
from src.ai_configurator.core.models import ConfigurationError


class TestTemplateMetadata:
    """Test template metadata validation."""
    
    def test_valid_metadata(self):
        """Test valid metadata creation."""
        metadata = TemplateMetadata(
            name="test-template",
            description="A test template",
            category="basic",
            complexity="low",
            created="2024-01-01"
        )
        assert metadata.name == "test-template"
        assert metadata.category == "basic"
        assert metadata.complexity == "low"
    
    def test_invalid_category(self):
        """Test invalid category validation."""
        with pytest.raises(ValueError, match="Category must be one of"):
            TemplateMetadata(
                name="test",
                description="test",
                category="invalid",
                complexity="low",
                created="2024-01-01"
            )
    
    def test_invalid_complexity(self):
        """Test invalid complexity validation."""
        with pytest.raises(ValueError, match="Complexity must be one of"):
            TemplateMetadata(
                name="test",
                description="test",
                category="basic",
                complexity="invalid",
                created="2024-01-01"
            )
    
    def test_invalid_date_format(self):
        """Test invalid date format validation."""
        with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
            TemplateMetadata(
                name="test",
                description="test",
                category="basic",
                complexity="low",
                created="invalid-date"
            )


class TestProfileTemplateSchema:
    """Test profile template schema validation."""
    
    def test_valid_profile_template(self):
        """Test valid profile template."""
        metadata = TemplateMetadata(
            name="test-profile",
            description="A test profile",
            category="basic",
            complexity="low",
            created="2024-01-01"
        )
        
        profile = ProfileTemplateSchema(
            metadata=metadata,
            paths=["contexts/test.md"],
            hooks={"test-hook": {"enabled": True}},
            settings={"auto_reload": True}
        )
        
        assert profile.metadata.name == "test-profile"
        assert len(profile.paths) == 1
        assert "test-hook" in profile.hooks
    
    def test_absolute_path_validation(self):
        """Test that absolute paths are flagged as warnings."""
        metadata = TemplateMetadata(
            name="test-profile",
            description="A test profile",
            category="basic",
            complexity="low",
            created="2024-01-01"
        )
        
        with pytest.raises(ValueError, match="Absolute paths are not recommended"):
            ProfileTemplateSchema(
                metadata=metadata,
                paths=["/absolute/path/to/context.md"]
            )


class TestContextTemplateSchema:
    """Test context template schema validation."""
    
    def test_valid_context_template(self):
        """Test valid context template."""
        metadata = TemplateMetadata(
            name="test-context",
            description="A test context",
            category="basic",
            complexity="low",
            created="2024-01-01"
        )
        
        context = ContextTemplateSchema(
            metadata=metadata,
            content="This is a comprehensive context with substantial content that provides meaningful guidance.",
            tags=["test", "example"],
            categories=["development"]
        )
        
        assert context.metadata.name == "test-context"
        assert len(context.content) > 50
        assert "test" in context.tags
    
    def test_insufficient_content(self):
        """Test validation of insufficient content."""
        with pytest.raises(ValueError, match="Context content must be substantial"):
            ContextTemplateSchema(
                content="Short content"
            )


class TestHookTemplateSchema:
    """Test hook template schema validation."""
    
    def test_valid_hook_template(self):
        """Test valid hook template."""
        metadata = TemplateMetadata(
            name="test-hook",
            description="A test hook",
            category="basic",
            complexity="low",
            created="2024-01-01"
        )
        
        hook = HookTemplateSchema(
            name="test-hook",
            description="A test hook",
            type="context",
            trigger="on_session_start",
            timeout=30,
            metadata=metadata
        )
        
        assert hook.name == "test-hook"
        assert hook.type == "context"
        assert hook.trigger == "on_session_start"
    
    def test_invalid_hook_type(self):
        """Test invalid hook type validation."""
        with pytest.raises(ValueError, match="Hook type must be one of"):
            HookTemplateSchema(
                name="test-hook",
                type="invalid",
                trigger="on_session_start"
            )
    
    def test_invalid_trigger(self):
        """Test invalid trigger validation."""
        with pytest.raises(ValueError, match="Hook trigger must be one of"):
            HookTemplateSchema(
                name="test-hook",
                type="context",
                trigger="invalid_trigger"
            )
    
    def test_invalid_timeout(self):
        """Test invalid timeout validation."""
        with pytest.raises(ValueError, match="Timeout must be between 1 and 300 seconds"):
            HookTemplateSchema(
                name="test-hook",
                type="context",
                trigger="on_session_start",
                timeout=500
            )


class TestTemplateValidator:
    """Test template validator functionality."""
    
    @pytest.fixture
    def temp_examples_dir(self):
        """Create a temporary examples directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "hooks" / "enhancement").mkdir(parents=True)
            
            yield examples_dir
    
    @pytest.fixture
    def validator(self, temp_examples_dir):
        """Create a template validator with temporary directory."""
        return TemplateValidator(temp_examples_dir)
    
    def test_validator_initialization(self, temp_examples_dir):
        """Test validator initialization."""
        validator = TemplateValidator(temp_examples_dir)
        assert validator.base_path == temp_examples_dir
        assert isinstance(validator._template_registry, dict)
    
    def test_determine_template_type(self, validator, temp_examples_dir):
        """Test template type determination."""
        # Profile template
        profile_path = temp_examples_dir / "profiles" / "basic" / "test.json"
        assert validator._determine_template_type(profile_path) == "profile"
        
        # Context template
        context_path = temp_examples_dir / "contexts" / "domains" / "test.md"
        assert validator._determine_template_type(context_path) == "context"
        
        # Hook template
        hook_path = temp_examples_dir / "hooks" / "automation" / "test.yaml"
        assert validator._determine_template_type(hook_path) == "hook"
        
        # Unknown template
        unknown_path = temp_examples_dir / "unknown" / "test.txt"
        assert validator._determine_template_type(unknown_path) == "unknown"
    
    def test_discover_template_files(self, validator, temp_examples_dir):
        """Test template file discovery."""
        # Create some test files
        (temp_examples_dir / "profiles" / "basic" / "test.json").touch()
        (temp_examples_dir / "contexts" / "domains" / "test.md").touch()
        (temp_examples_dir / "hooks" / "automation" / "test.yaml").touch()
        
        files = validator._discover_template_files()
        
        assert len(files) == 3
        assert any(f.name == "test.json" for f in files)
        assert any(f.name == "test.md" for f in files)
        assert any(f.name == "test.yaml" for f in files)
    
    def test_parse_json_with_comments(self, validator):
        """Test JSON parsing with comments."""
        json_content = '''
        {
            // This is a comment
            "name": "test",
            "description": "A test template", // Another comment
            "paths": [
                "context1.md" // Path comment
            ]
        }
        '''
        
        result = validator._parse_json_with_comments(json_content, Path("test.json"), [])
        
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test template"
        assert result["paths"] == ["context1.md"]
    
    def test_parse_json_with_syntax_error(self, validator):
        """Test JSON parsing with syntax errors."""
        json_content = '''
        {
            "name": "test",
            "description": "A test template"
            // Missing comma above
            "paths": []
        }
        '''
        
        errors = []
        result = validator._parse_json_with_comments(json_content, Path("test.json"), errors)
        
        assert result is None
        assert len(errors) == 1
        assert errors[0].error_type == "JSONSyntaxError"
    
    def test_parse_yaml_with_errors(self, validator):
        """Test YAML parsing with error handling."""
        yaml_content = '''
        name: test-hook
        description: A test hook
        type: context
        trigger: on_session_start
        '''
        
        result = validator._parse_yaml_with_errors(yaml_content, Path("test.yaml"), [])
        
        assert result is not None
        assert result["name"] == "test-hook"
        assert result["type"] == "context"
    
    def test_parse_yaml_with_syntax_error(self, validator):
        """Test YAML parsing with syntax errors."""
        yaml_content = '''
        name: test-hook
        description: A test hook
        type: context
        trigger: on_session_start
        invalid_yaml: [unclosed list
        '''
        
        errors = []
        result = validator._parse_yaml_with_errors(yaml_content, Path("test.yaml"), errors)
        
        assert result is None
        assert len(errors) == 1
        assert errors[0].error_type == "YAMLSyntaxError"
    
    def test_parse_markdown_frontmatter(self, validator):
        """Test markdown frontmatter parsing."""
        markdown_content = '''---
name: test-context
description: A test context
tags: [test, example]
---

# Test Context

This is the main content of the context.
'''
        
        frontmatter, content = validator._parse_markdown_frontmatter(markdown_content)
        
        assert frontmatter is not None
        assert frontmatter["name"] == "test-context"
        assert "test" in frontmatter["tags"]
        assert content.startswith("# Test Context")
    
    def test_parse_markdown_without_frontmatter(self, validator):
        """Test markdown parsing without frontmatter."""
        markdown_content = '''# Test Context

This is a context without frontmatter.
'''
        
        frontmatter, content = validator._parse_markdown_frontmatter(markdown_content)
        
        assert frontmatter is None
        assert content == markdown_content
    
    def test_validate_naming_conventions(self, validator):
        """Test naming convention validation."""
        errors = []
        warnings = []
        
        # Valid kebab-case name
        validator._validate_naming_conventions(
            Path("test-template.json"), "profile", errors, warnings
        )
        assert len(warnings) == 0
        
        # Invalid naming (camelCase)
        validator._validate_naming_conventions(
            Path("testTemplate.json"), "profile", errors, warnings
        )
        assert len(warnings) == 1
        assert warnings[0].error_type == "NamingConvention"
        
        # Invalid file extension
        validator._validate_naming_conventions(
            Path("test-profile.yaml"), "profile", errors, warnings
        )
        assert len(errors) == 1
        assert errors[0].error_type == "InvalidFileExtension"
    
    def test_validate_profile_rules(self, validator):
        """Test profile-specific validation rules."""
        errors = []
        warnings = []
        info = []
        
        profile_data = {
            "metadata": {
                "name": "test-profile",
                "description": "Short desc",  # Too short
                "category": "basic",
                "complexity": "low",
                "created": "2024-01-01"
            },
            "paths": [],  # Empty paths
            "hooks": {}
        }
        
        validator._validate_profile_rules(
            Path("test.json"), profile_data, errors, warnings, info
        )
        
        assert len(warnings) == 2  # Empty paths + insufficient documentation
        assert any(w.error_type == "EmptyPaths" for w in warnings)
        assert any(w.error_type == "InsufficientDocumentation" for w in warnings)
    
    def test_validate_context_rules(self, validator):
        """Test context-specific validation rules."""
        errors = []
        warnings = []
        info = []
        
        # Short content without header
        short_content = "This is short content without proper structure."
        
        validator._validate_context_rules(
            Path("test.md"), short_content, None, errors, warnings, info
        )
        
        assert len(warnings) == 2  # Short content + missing header
        assert any(w.error_type == "ShortContent" for w in warnings)
        assert any(w.error_type == "MissingMainHeader" for w in warnings)
        
        # Technical content without code examples
        technical_content = "# Development Guidelines\n\nThis context covers programming best practices and code development."
        
        errors.clear()
        warnings.clear()
        info.clear()
        
        validator._validate_context_rules(
            Path("dev.md"), technical_content, None, errors, warnings, info
        )
        
        assert any(w.error_type == "MissingCodeExamples" for w in warnings)
    
    def test_validate_hook_rules(self, validator, temp_examples_dir):
        """Test hook-specific validation rules."""
        errors = []
        warnings = []
        info = []
        
        hook_data = {
            "name": "test-hook",
            "type": "script",
            "trigger": "on_file_save",
            "timeout": 150,  # Long timeout
            "script": "nonexistent_script.py",  # Missing script
            "context": {
                "sources": ["nonexistent_context.md"]  # Missing context
            }
        }
        
        hook_path = temp_examples_dir / "hooks" / "test.yaml"
        
        validator._validate_hook_rules(
            hook_path, hook_data, errors, warnings, info
        )
        
        assert len(errors) == 2  # Missing script + missing context
        assert len(warnings) == 1  # Long timeout
        assert any(e.error_type == "MissingScriptFile" for e in errors)
        assert any(e.error_type == "MissingTemplateReference" for e in errors)
        assert any(w.error_type == "LongTimeout" for w in warnings)
    
    def test_validate_template_file_not_found(self, validator):
        """Test validation of non-existent file."""
        report = validator.validate_template_file("nonexistent.json")
        
        assert not report.is_valid
        assert len(report.errors) == 1
        assert report.errors[0].error_type == "FileNotFound"
    
    def test_get_template_category(self, validator, temp_examples_dir):
        """Test template category determination."""
        basic_path = temp_examples_dir / "profiles" / "basic" / "test.json"
        assert validator._get_template_category(basic_path) == "basic"
        
        professional_path = temp_examples_dir / "profiles" / "professional" / "test.json"
        assert validator._get_template_category(professional_path) == "professional"
        
        workflow_path = temp_examples_dir / "workflows" / "test" / "profile.json"
        assert validator._get_template_category(workflow_path) == "workflow"
        
        unknown_path = temp_examples_dir / "other" / "test.json"
        assert validator._get_template_category(unknown_path) == "unknown"


class TestTemplateValidatorIntegration:
    """Integration tests for template validator."""
    
    @pytest.fixture
    def temp_examples_with_files(self):
        """Create temporary examples directory with actual template files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            
            # Create valid profile template
            profile_content = {
                "metadata": {
                    "name": "test-profile",
                    "description": "A comprehensive test profile for validation",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01",
                    "tags": ["test", "example"]
                },
                "paths": ["contexts/domains/test-context.md"],
                "hooks": {},
                "settings": {"auto_reload": True}
            }
            
            profile_file = examples_dir / "profiles" / "basic" / "test-profile.json"
            with open(profile_file, 'w') as f:
                json.dump(profile_content, f, indent=2)
            
            # Create valid context template
            context_content = '''---
name: test-context
description: A test context template
category: basic
complexity: low
created: "2024-01-01"
tags: [test, development]
---

# Test Context

This is a comprehensive test context that provides substantial guidance for development practices.

## Overview

This context demonstrates proper structure and content for template validation.

## Best Practices

- Follow established patterns
- Include comprehensive documentation
- Provide practical examples

```python
# Example code snippet
def example_function():
    return "This demonstrates code examples in contexts"
```

## Conclusion

This context provides sufficient content and structure for validation testing.
'''
            
            context_file = examples_dir / "contexts" / "domains" / "test-context.md"
            with open(context_file, 'w') as f:
                f.write(context_content)
            
            # Create valid hook template
            hook_content = {
                "name": "test-hook",
                "description": "A test hook for validation",
                "version": "1.0",
                "type": "context",
                "trigger": "on_session_start",
                "timeout": 30,
                "enabled": True,
                "metadata": {
                    "name": "test-hook",
                    "description": "A comprehensive test hook for validation",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01",
                    "tags": ["test", "automation"]
                },
                "context": {
                    "sources": ["contexts/domains/test-context.md"],
                    "tags": ["test"],
                    "priority": 1
                }
            }
            
            hook_file = examples_dir / "hooks" / "automation" / "test-hook.yaml"
            with open(hook_file, 'w') as f:
                yaml.dump(hook_content, f, default_flow_style=False)
            
            yield examples_dir
    
    def test_validate_all_templates_success(self, temp_examples_with_files):
        """Test successful validation of all templates."""
        validator = TemplateValidator(temp_examples_with_files)
        report = validator.validate_all_templates()
        
        assert report.is_valid
        assert len(report.errors) == 0
        assert len(report.files_checked) == 3
        assert report.summary["total_files"] == 3
        assert report.summary["valid_files"] == 3
    
    def test_validate_specific_template_types(self, temp_examples_with_files):
        """Test validation of specific template types."""
        validator = TemplateValidator(temp_examples_with_files)
        
        # Test profile validation
        profile_path = temp_examples_with_files / "profiles" / "basic" / "test-profile.json"
        profile_report = validator.validate_profile_template(profile_path)
        assert profile_report.is_valid
        
        # Test context validation
        context_path = temp_examples_with_files / "contexts" / "domains" / "test-context.md"
        context_report = validator.validate_context_template(context_path)
        assert context_report.is_valid
        
        # Test hook validation
        hook_path = temp_examples_with_files / "hooks" / "automation" / "test-hook.yaml"
        hook_report = validator.validate_hook_template(hook_path)
        assert hook_report.is_valid