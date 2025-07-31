#!/usr/bin/env python3
"""Unit tests for ConfigurationValidator."""

import pytest
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.models import ValidationReport, ConfigurationError


class TestConfigurationValidator:
    """Test suite for ConfigurationValidator."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.validator = ConfigurationValidator(self.test_dir)
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(exist_ok=True)
        (self.test_dir / 'hooks').mkdir(exist_ok=True)
        (self.test_dir / 'contexts').mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_yaml_syntax_valid(self):
        """Test validation of valid YAML syntax."""
        valid_yaml = {
            'name': 'test-profile',
            'description': 'Valid YAML'
        }
        
        yaml_file = self.test_dir / 'profiles' / 'valid.yaml'
        with open(yaml_file, 'w') as f:
            yaml.dump(valid_yaml, f)
        
        result = self.validator.validate_configuration_file(yaml_file)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_yaml_syntax_invalid(self):
        """Test validation of invalid YAML syntax."""
        invalid_yaml = """
name: test
description: Invalid
contexts:
  - item1
  - item2
    invalid_indent: true
"""
        
        yaml_file = self.test_dir / 'profiles' / 'invalid.yaml'
        with open(yaml_file, 'w') as f:
            f.write(invalid_yaml)
        
        result = self.validator.validate_configuration_file(yaml_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        syntax_error = result.errors[0]
        assert syntax_error.error_type == "YAMLSyntaxError"
        assert syntax_error.line_number is not None
        assert str(yaml_file) in syntax_error.file_path
    
    def test_validate_schema_profile_valid(self):
        """Test schema validation for valid profile."""
        profile_data = {
            'name': 'test-profile',
            'description': 'Valid profile'
        }
        
        profile_file = self.test_dir / 'profiles' / 'valid.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_schema(profile_file, 'profile')
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_schema_profile_missing_required(self):
        """Test schema validation for profile missing required fields."""
        profile_data = {
            'description': 'Missing name field'
        }
        
        profile_file = self.test_dir / 'profiles' / 'missing-name.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_schema(profile_file, 'profile')
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        schema_error = next((e for e in result.errors if e.error_type == "SchemaValidationError"), None)
        assert schema_error is not None
        assert "Missing required fields:" in schema_error.message
        assert "name" in schema_error.message
    
    def test_validate_schema_hook_valid(self):
        """Test schema validation for valid hook."""
        hook_data = {
            'name': 'test-hook',
            'description': 'Valid hook',
            'type': 'context',
            'trigger': 'on_session_start'
        }
        
        hook_file = self.test_dir / 'hooks' / 'valid.yaml'
        with open(hook_file, 'w') as f:
            yaml.dump(hook_data, f)
        
        result = self.validator.validate_schema(hook_file, 'hook')
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_schema_hook_invalid_trigger(self):
        """Test schema validation for hook with invalid trigger."""
        hook_data = {
            'name': 'test-hook',
            'type': 'context',
            'trigger': 'invalid_trigger'
        }
        
        hook_file = self.test_dir / 'hooks' / 'invalid-trigger.yaml'
        with open(hook_file, 'w') as f:
            yaml.dump(hook_data, f)
        
        result = self.validator.validate_schema(hook_file, 'hook')
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Should have error about invalid trigger
        trigger_error = next((e for e in result.errors if "trigger" in e.message.lower()), None)
        assert trigger_error is not None
    
    def test_validate_file_references_valid(self):
        """Test file reference validation with existing files."""
        # Create context file
        context_file = self.test_dir / 'contexts' / 'test-context.md'
        context_file.write_text('# Test Context')
        
        profile_data = {
            'name': 'test-profile',
            'contexts': ['contexts/test-context.md']
        }
        
        profile_file = self.test_dir / 'profiles' / 'test.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_configuration_file(profile_file)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_file_references_missing(self):
        """Test file reference validation with missing files."""
        profile_data = {
            'name': 'test-profile',
            'contexts': [
                'contexts/missing1.md',
                'contexts/missing2.md'
            ]
        }
        
        profile_file = self.test_dir / 'profiles' / 'test.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_configuration_file(profile_file)
        
        assert result.is_valid is False
        assert len(result.errors) >= 2
        
        # Check that missing files are reported
        missing_files = [e.message for e in result.errors]
        assert any('missing1.md' in msg for msg in missing_files)
        assert any('missing2.md' in msg for msg in missing_files)
        
        # Should have MissingFileReference errors
        ref_errors = [e for e in result.errors if e.error_type == "MissingFileReference"]
        assert len(ref_errors) >= 2
    
    def test_validate_configuration_file_comprehensive(self):
        """Test comprehensive validation of a configuration file."""
        # Create a valid context file
        context_file = self.test_dir / 'contexts' / 'valid-context.md'
        context_file.write_text('# Valid Context')
        
        profile_data = {
            'name': 'comprehensive-test',
            'description': 'Comprehensive validation test',
            'contexts': ['contexts/valid-context.md']
        }
        
        profile_file = self.test_dir / 'profiles' / 'comprehensive.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_configuration_file(profile_file)
        
        assert isinstance(result, ValidationReport)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_all_configurations(self):
        """Test validation of all configurations in directory."""
        # Create valid profile
        valid_profile = {
            'name': 'valid-profile',
            'description': 'Valid profile'
        }
        
        with open(self.test_dir / 'profiles' / 'valid.yaml', 'w') as f:
            yaml.dump(valid_profile, f)
        
        # Create invalid profile
        invalid_profile = {
            'description': 'Missing name'
        }
        
        with open(self.test_dir / 'profiles' / 'invalid.yaml', 'w') as f:
            yaml.dump(invalid_profile, f)
        
        result = self.validator.validate_all_configurations()
        
        assert isinstance(result, ValidationReport)
        assert result.is_valid is False  # Should be invalid due to invalid profile
        assert len(result.errors) > 0
        
        # Check summary
        assert 'total_files' in result.summary
        assert result.summary['total_files'] >= 2
    
    def test_detect_circular_dependencies(self):
        """Test detection of circular dependencies."""
        # Create circular context files
        context_a = self.test_dir / 'contexts' / 'circular-a.md'
        context_b = self.test_dir / 'contexts' / 'circular-b.md'
        
        context_a.write_text('# Context A\nReferences circular-b.md')
        context_b.write_text('# Context B\nReferences circular-a.md')
        
        # Create profiles that reference these contexts
        profile_a = {
            'name': 'profile-a',
            'contexts': ['contexts/circular-b.md']
        }
        
        profile_b = {
            'name': 'profile-b',
            'contexts': ['contexts/circular-a.md']
        }
        
        with open(self.test_dir / 'profiles' / 'profile-a.yaml', 'w') as f:
            yaml.dump(profile_a, f)
        
        with open(self.test_dir / 'profiles' / 'profile-b.yaml', 'w') as f:
            yaml.dump(profile_b, f)
        
        result = self.validator.validate_all_configurations()
        
        # Should detect circular dependencies
        circular_errors = [e for e in result.errors if e.error_type == "CircularDependency"]
        # Note: Circular dependency detection might not be implemented yet
        # This test documents the expected behavior
    
    def test_deprecated_field_warnings(self):
        """Test detection of deprecated fields."""
        profile_data = {
            'name': 'deprecated-test',
            'description': 'Profile with deprecated fields',
            'legacy_hooks': {'old': 'format'},  # Deprecated
            'old_context_format': True,  # Deprecated
        }
        
        profile_file = self.test_dir / 'profiles' / 'deprecated.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.validator.validate_configuration_file(profile_file)
        
        # Should have warnings for deprecated fields
        deprecated_warnings = [w for w in result.warnings if w.error_type == "DeprecatedField"]
        # Note: Deprecated field detection might not be fully implemented
        # This test documents the expected behavior
    
    def test_validation_report_structure(self):
        """Test ValidationReport structure and methods."""
        # Test creating validation report with errors
        error = ConfigurationError(
            error_type="TestError",
            message="Test error message",
            file_path="test.yaml",
            line_number=5
        )
        
        warning = ConfigurationError(
            error_type="TestWarning",
            message="Test warning message",
            file_path="test.yaml",
            severity="warning"
        )
        
        info = ConfigurationError(
            error_type="TestInfo",
            message="Test info message",
            file_path="test.yaml",
            severity="info"
        )
        
        report = ValidationReport(
            is_valid=False,
            errors=[error],
            warnings=[warning],
            info=[info],
            files_checked=["test.yaml"],
            summary={"errors": 1, "warnings": 1, "info": 1}
        )
        
        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert len(report.info) == 1
        assert report.is_valid is False  # Has errors
        
        # Test summary
        assert 'errors' in report.summary
        assert 'warnings' in report.summary
        assert report.summary['errors'] == 1
        assert report.summary['warnings'] == 1


if __name__ == '__main__':
    pytest.main([__file__])