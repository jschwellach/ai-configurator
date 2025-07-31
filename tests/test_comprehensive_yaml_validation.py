#!/usr/bin/env python3
"""Comprehensive test for YAML loading, validation, and error handling as specified in task 12."""

import pytest
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.validator import ConfigurationValidator


class TestComprehensiveYAMLValidation:
    """Comprehensive test suite for YAML loading, validation, and error handling."""
    
    def setup_method(self):
        """Set up test environment with comprehensive test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(exist_ok=True)
        (self.test_dir / 'hooks').mkdir(exist_ok=True)
        (self.test_dir / 'contexts').mkdir(exist_ok=True)
        
        # Initialize components
        self.loader = YamlConfigLoader(self.test_dir)
        self.validator = ConfigurationValidator(self.test_dir)
        
        self._create_comprehensive_test_fixtures()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_comprehensive_test_fixtures(self):
        """Create comprehensive test fixtures with valid and invalid configurations."""
        
        # Valid configurations
        self._create_valid_fixtures()
        
        # Invalid configurations
        self._create_invalid_fixtures()
        
        # Context files
        self._create_context_fixtures()
    
    def _create_valid_fixtures(self):
        """Create valid YAML configuration fixtures."""
        
        # Valid profile with all features
        valid_profile = {
            'name': 'comprehensive-profile',
            'description': 'A comprehensive test profile',
            'version': '1.0',
            'contexts': [
                'contexts/development.md',
                'contexts/shared.md'
            ],
            'hooks': {
                'on_session_start': [
                    {'name': 'setup-hook', 'enabled': True}
                ],
                'per_user_message': [
                    {'name': 'context-hook', 'enabled': True}
                ]
            },
            'mcp_servers': ['core', 'development'],
            'settings': {
                'auto_backup': True,
                'validation_level': 'strict'
            }
        }
        
        with open(self.test_dir / 'profiles' / 'comprehensive-profile.yaml', 'w') as f:
            yaml.dump(valid_profile, f)
        
        # Minimal valid profile
        minimal_profile = {
            'name': 'minimal-profile',
            'description': 'Minimal valid profile'
        }
        
        with open(self.test_dir / 'profiles' / 'minimal-profile.yaml', 'w') as f:
            yaml.dump(minimal_profile, f)
        
        # Valid hook configurations
        valid_hook = {
            'name': 'setup-hook',
            'description': 'Setup development environment',
            'type': 'context',
            'trigger': 'on_session_start',
            'timeout': 30,
            'enabled': True,
            'context': {
                'sources': ['contexts/development.md'],
                'tags': ['setup', 'development'],
                'priority': 1
            }
        }
        
        with open(self.test_dir / 'hooks' / 'setup-hook.yaml', 'w') as f:
            yaml.dump(valid_hook, f)
        
        context_hook = {
            'name': 'context-hook',
            'description': 'Context enhancement hook',
            'type': 'context',
            'trigger': 'per_user_message',
            'enabled': True,
            'context': {
                'sources': ['contexts/shared.md']
            }
        }
        
        with open(self.test_dir / 'hooks' / 'context-hook.yaml', 'w') as f:
            yaml.dump(context_hook, f)
    
    def _create_invalid_fixtures(self):
        """Create invalid YAML configuration fixtures."""
        
        # Profile missing required name field
        missing_name_profile = {
            'description': 'Profile missing required name field',
            'contexts': ['contexts/test.md']
        }
        
        with open(self.test_dir / 'profiles' / 'missing-name.yaml', 'w') as f:
            yaml.dump(missing_name_profile, f)
        
        # Profile with broken file references
        broken_refs_profile = {
            'name': 'broken-refs',
            'description': 'Profile with broken file references',
            'contexts': [
                'contexts/nonexistent1.md',
                'contexts/nonexistent2.md'
            ]
        }
        
        with open(self.test_dir / 'profiles' / 'broken-refs.yaml', 'w') as f:
            yaml.dump(broken_refs_profile, f)
        
        # YAML syntax error file
        with open(self.test_dir / 'profiles' / 'syntax-error.yaml', 'w') as f:
            f.write("""
name: syntax-error
description: This file has syntax errors
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
hooks:
  on_session_start:
    - name: test
      enabled: true
    - name: broken
      enabled: false
      invalid_yaml: [unclosed_list
""")
        
        # Hook missing required fields
        incomplete_hook = {
            'name': 'incomplete-hook',
            'description': 'Missing required trigger field'
            # Missing 'trigger' field
        }
        
        with open(self.test_dir / 'hooks' / 'incomplete-hook.yaml', 'w') as f:
            yaml.dump(incomplete_hook, f)
        
        # Hook with invalid trigger
        invalid_trigger_hook = {
            'name': 'invalid-trigger-hook',
            'description': 'Hook with invalid trigger',
            'type': 'context',
            'trigger': 'invalid_trigger_name',
            'context': {
                'sources': ['contexts/test.md']
            }
        }
        
        with open(self.test_dir / 'hooks' / 'invalid-trigger-hook.yaml', 'w') as f:
            yaml.dump(invalid_trigger_hook, f)
    
    def _create_context_fixtures(self):
        """Create context file fixtures."""
        
        # Valid context files
        dev_context = self.test_dir / 'contexts' / 'development.md'
        dev_context.write_text("""---
tags: [development, setup]
priority: 1
---

# Development Context

Development guidelines and best practices.
""")
        
        shared_context = self.test_dir / 'contexts' / 'shared.md'
        shared_context.write_text("""---
tags: [shared, common]
priority: 0
---

# Shared Context

Common context across all profiles.
""")
    
    def test_yaml_loading_valid_configurations(self):
        """Test YAML loading for valid configurations."""
        
        # Test profile loading
        comprehensive_profile = self.loader.load_profile('comprehensive-profile')
        assert comprehensive_profile.name == 'comprehensive-profile'
        assert comprehensive_profile.description == 'A comprehensive test profile'
        assert len(comprehensive_profile.contexts) == 2
        assert 'contexts/development.md' in comprehensive_profile.contexts
        
        minimal_profile = self.loader.load_profile('minimal-profile')
        assert minimal_profile.name == 'minimal-profile'
        assert minimal_profile.description == 'Minimal valid profile'
        
        # Test hook loading
        setup_hook = self.loader.load_hook('setup-hook')
        assert setup_hook.name == 'setup-hook'
        assert setup_hook.type == 'context'
        assert setup_hook.trigger == 'on_session_start'
        
        context_hook = self.loader.load_hook('context-hook')
        assert context_hook.name == 'context-hook'
        assert context_hook.trigger == 'per_user_message'
    
    def test_yaml_syntax_error_handling(self):
        """Test YAML syntax error detection with file names and line numbers."""
        
        syntax_error_file = self.test_dir / 'profiles' / 'syntax-error.yaml'
        result = self.validator.validate_configuration_file(syntax_error_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Find syntax error
        syntax_errors = [e for e in result.errors if e.error_type == "YAMLSyntaxError"]
        assert len(syntax_errors) > 0
        
        syntax_error = syntax_errors[0]
        assert str(syntax_error_file) in syntax_error.file_path
        assert syntax_error.line_number is not None
        assert syntax_error.line_number > 0
        
        print(f"✅ Detected YAML syntax error at {syntax_error.file_path}:{syntax_error.line_number}")
        print(f"   Error: {syntax_error.message}")
    
    def test_missing_required_fields_validation(self):
        """Test detection of missing required fields in single error message."""
        
        # Test profile missing name
        missing_name_file = self.test_dir / 'profiles' / 'missing-name.yaml'
        result = self.validator.validate_configuration_file(missing_name_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Find schema validation errors
        schema_errors = [e for e in result.errors if e.error_type == "SchemaValidationError"]
        assert len(schema_errors) > 0
        
        # Should mention missing required fields
        error_messages = [e.message for e in schema_errors]
        assert any("Missing required fields:" in msg for msg in error_messages)
        assert any("name" in msg for msg in error_messages)
        
        print(f"✅ Detected missing required fields: {schema_errors[0].message}")
        
        # Test hook missing trigger
        incomplete_hook_file = self.test_dir / 'hooks' / 'incomplete-hook.yaml'
        hook_result = self.validator.validate_configuration_file(incomplete_hook_file)
        
        assert hook_result.is_valid is False
        hook_schema_errors = [e for e in hook_result.errors if e.error_type == "SchemaValidationError"]
        assert len(hook_schema_errors) > 0
        
        hook_error_messages = [e.message for e in hook_schema_errors]
        assert any("trigger" in msg for msg in hook_error_messages)
        
        print(f"✅ Detected missing hook trigger field: {hook_schema_errors[0].message}")
    
    def test_broken_file_references_validation(self):
        """Test reporting of broken file references."""
        
        broken_refs_file = self.test_dir / 'profiles' / 'broken-refs.yaml'
        result = self.validator.validate_configuration_file(broken_refs_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Find file reference errors
        ref_errors = [e for e in result.errors if e.error_type == "MissingFileReference"]
        assert len(ref_errors) >= 2  # Should have at least 2 missing file errors
        
        # Check that specific missing files are reported
        error_messages = [e.message for e in ref_errors]
        assert any('nonexistent1.md' in msg for msg in error_messages)
        assert any('nonexistent2.md' in msg for msg in error_messages)
        
        print(f"✅ Detected {len(ref_errors)} broken file references:")
        for error in ref_errors:
            print(f"   • {error.message}")
    
    def test_invalid_field_values_validation(self):
        """Test validation of invalid field values."""
        
        invalid_trigger_file = self.test_dir / 'hooks' / 'invalid-trigger-hook.yaml'
        result = self.validator.validate_configuration_file(invalid_trigger_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Should have schema validation error for invalid trigger
        schema_errors = [e for e in result.errors if e.error_type == "SchemaValidationError"]
        trigger_errors = [e for e in schema_errors if "trigger" in e.message.lower()]
        assert len(trigger_errors) > 0
        
        print(f"✅ Detected invalid trigger value: {trigger_errors[0].message}")
    
    def test_comprehensive_validation_workflow(self):
        """Test complete validation workflow for all configurations."""
        
        # Run comprehensive validation
        all_validation = self.validator.validate_all_configurations()
        
        # Should be invalid due to invalid configurations
        assert all_validation.is_valid is False
        assert len(all_validation.errors) > 0
        
        # Check summary
        assert 'total_files' in all_validation.summary
        assert all_validation.summary['total_files'] >= 8  # At least 8 config files
        
        # Categorize errors by type
        error_types = {}
        for error in all_validation.errors:
            error_type = error.error_type
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        print(f"✅ Comprehensive validation found {len(all_validation.errors)} errors:")
        for error_type, count in error_types.items():
            print(f"   • {error_type}: {count}")
        
        # Should have various types of errors
        expected_error_types = ["YAMLSyntaxError", "SchemaValidationError", "MissingFileReference"]
        for expected_type in expected_error_types:
            assert expected_type in error_types, f"Expected {expected_type} errors"
    
    def test_validation_caching_and_performance(self):
        """Test validation caching and performance."""
        
        # Load same configuration multiple times
        profile1 = self.loader.load_profile('comprehensive-profile')
        profile2 = self.loader.load_profile('comprehensive-profile')
        
        # Should be cached
        cache_stats = self.loader.get_cache_stats()
        assert cache_stats['config_cache_size'] > 0
        
        # Profiles should be identical
        assert profile1.name == profile2.name
        assert profile1.description == profile2.description
        
        # Test cache clearing
        self.loader.clear_cache()
        cache_stats_after = self.loader.get_cache_stats()
        assert cache_stats_after['config_cache_size'] == 0
        
        print("✅ Caching functionality working correctly")
    
    def test_configuration_discovery(self):
        """Test configuration discovery functionality."""
        
        discovered = self.loader.discover_configurations()
        
        assert 'profiles' in discovered
        assert 'hooks' in discovered
        assert 'contexts' in discovered
        
        # Should discover all created files
        assert len(discovered['profiles']) >= 4  # At least 4 profile files
        assert len(discovered['hooks']) >= 3     # At least 3 hook files
        assert len(discovered['contexts']) >= 2  # At least 2 context files
        
        print(f"✅ Discovered configurations:")
        print(f"   • Profiles: {len(discovered['profiles'])}")
        print(f"   • Hooks: {len(discovered['hooks'])}")
        print(f"   • Contexts: {len(discovered['contexts'])}")
    
    def test_error_context_and_details(self):
        """Test that errors provide sufficient context and details."""
        
        # Test syntax error context
        syntax_error_file = self.test_dir / 'profiles' / 'syntax-error.yaml'
        result = self.validator.validate_configuration_file(syntax_error_file)
        
        syntax_errors = [e for e in result.errors if e.error_type == "YAMLSyntaxError"]
        if syntax_errors:
            syntax_error = syntax_errors[0]
            
            # Should have file path
            assert syntax_error.file_path is not None
            assert str(syntax_error_file) in syntax_error.file_path
            
            # Should have line number
            assert syntax_error.line_number is not None
            assert syntax_error.line_number > 0
            
            # Should have descriptive message
            assert len(syntax_error.message) > 10
            
            print(f"✅ Syntax error provides context:")
            print(f"   • File: {syntax_error.file_path}")
            print(f"   • Line: {syntax_error.line_number}")
            print(f"   • Message: {syntax_error.message}")
    
    def test_integration_with_profile_and_hook_loading(self):
        """Test integration between validation and loading workflows."""
        
        # Valid configurations should load successfully after validation
        valid_profile_file = self.test_dir / 'profiles' / 'comprehensive-profile.yaml'
        validation_result = self.validator.validate_configuration_file(valid_profile_file)
        
        if validation_result.is_valid:
            # Should be able to load successfully
            profile = self.loader.load_profile('comprehensive-profile')
            assert profile.name == 'comprehensive-profile'
            
            # Referenced hooks should also be loadable
            setup_hook = self.loader.load_hook('setup-hook')
            assert setup_hook.name == 'setup-hook'
            
            print("✅ Valid configurations load successfully after validation")
        
        # Invalid configurations should be caught by validation
        invalid_profile_file = self.test_dir / 'profiles' / 'missing-name.yaml'
        invalid_result = self.validator.validate_configuration_file(invalid_profile_file)
        
        assert invalid_result.is_valid is False
        print("✅ Invalid configurations properly caught by validation")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])