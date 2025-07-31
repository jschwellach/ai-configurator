#!/usr/bin/env python3
"""Integration tests for profile loading workflows."""

import pytest
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.profile_manager import ProfileManager


class TestProfileLoadingWorkflow:
    """Integration tests for complete profile loading workflow."""
    
    def setup_method(self):
        """Set up test environment with realistic configurations."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(exist_ok=True)
        (self.test_dir / 'hooks').mkdir(exist_ok=True)
        (self.test_dir / 'contexts').mkdir(exist_ok=True)
        (self.test_dir / 'contexts' / 'shared').mkdir(exist_ok=True)
        
        # Initialize components
        self.loader = YamlConfigLoader(self.test_dir)
        self.validator = ConfigurationValidator(self.test_dir)
        self.profile_manager = ProfileManager(self.test_dir)
        
        self._create_test_configurations()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_configurations(self):
        """Create realistic test configurations."""
        # Create context files
        dev_context = self.test_dir / 'contexts' / 'development.md'
        dev_context.write_text("""---
tags: [development, setup]
priority: 1
---

# Development Guidelines

Best practices for development work.
""")
        
        shared_context = self.test_dir / 'contexts' / 'shared' / 'common.md'
        shared_context.write_text("""---
tags: [common, shared]
priority: 0
---

# Common Context

Shared context across all profiles.
""")
        
        # Create hook configurations
        setup_hook = {
            'name': 'setup-dev-env',
            'description': 'Initialize development environment',
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
        
        with open(self.test_dir / 'hooks' / 'setup-dev-env.yaml', 'w') as f:
            yaml.dump(setup_hook, f)
        
        context_hook = {
            'name': 'context-enhancer',
            'description': 'Enhance context for messages',
            'type': 'context',
            'trigger': 'per_user_message',
            'timeout': 15,
            'enabled': True,
            'context': {
                'sources': ['contexts/shared/common.md'],
                'tags': ['enhancement'],
                'priority': 2
            }
        }
        
        with open(self.test_dir / 'hooks' / 'context-enhancer.yaml', 'w') as f:
            yaml.dump(context_hook, f)
        
        # Create profile configurations
        developer_profile = {
            'name': 'developer',
            'description': 'Development environment profile',
            'version': '1.0',
            'contexts': [
                'contexts/development.md',
                'contexts/shared/common.md'
            ],
            'hooks': {
                'on_session_start': [
                    {'name': 'setup-dev-env', 'enabled': True}
                ],
                'per_user_message': [
                    {'name': 'context-enhancer', 'enabled': True}
                ]
            },
            'mcp_servers': ['core', 'development'],
            'settings': {
                'auto_backup': True,
                'validation_level': 'strict'
            }
        }
        
        with open(self.test_dir / 'profiles' / 'developer.yaml', 'w') as f:
            yaml.dump(developer_profile, f)
        
        minimal_profile = {
            'name': 'minimal',
            'description': 'Minimal profile for testing'
        }
        
        with open(self.test_dir / 'profiles' / 'minimal.yaml', 'w') as f:
            yaml.dump(minimal_profile, f)
    
    def test_complete_profile_loading_workflow(self):
        """Test complete workflow from discovery to loading."""
        # Step 1: Discover configurations
        discovered = self.loader.discover_configurations()
        
        assert 'profiles' in discovered
        assert 'hooks' in discovered
        assert 'contexts' in discovered
        assert len(discovered['profiles']) >= 2
        assert len(discovered['hooks']) >= 2
        
        # Step 2: Validate all configurations
        validation_report = self.validator.validate_all_configurations()
        
        assert validation_report.is_valid is True
        assert len(validation_report.errors) == 0
        
        # Step 3: Load specific profile
        developer_profile = self.loader.load_profile('developer')
        
        assert developer_profile.name == 'developer'
        assert developer_profile.description == 'Development environment profile'
        assert len(developer_profile.contexts) == 2
        assert 'contexts/development.md' in developer_profile.contexts
        assert 'contexts/shared/common.md' in developer_profile.contexts
        
        # Step 4: Verify hooks are properly referenced
        assert 'on_session_start' in developer_profile.hooks
        assert 'per_user_message' in developer_profile.hooks
        
        setup_hook_ref = developer_profile.hooks['on_session_start'][0]
        assert setup_hook_ref['name'] == 'setup-dev-env'
        assert setup_hook_ref['enabled'] is True
        
        # Step 5: Load referenced hooks
        setup_hook = self.loader.load_hook('setup-dev-env')
        context_hook = self.loader.load_hook('context-enhancer')
        
        assert setup_hook.name == 'setup-dev-env'
        assert setup_hook.trigger == 'on_session_start'
        assert context_hook.name == 'context-enhancer'
        assert context_hook.trigger == 'per_user_message'
        
        # Step 6: Verify context files exist
        for context_path in developer_profile.contexts:
            full_path = self.test_dir / context_path
            assert full_path.exists(), f"Context file should exist: {context_path}"
    
    def test_profile_validation_workflow(self):
        """Test profile validation workflow with various scenarios."""
        # Test valid profile validation
        valid_result = self.validator.validate_configuration_file(
            self.test_dir / 'profiles' / 'developer.yaml'
        )
        
        assert valid_result.is_valid is True
        assert len(valid_result.errors) == 0
        
        # Create and test invalid profile
        invalid_profile = {
            'description': 'Missing name field',
            'contexts': ['contexts/nonexistent.md']
        }
        
        invalid_file = self.test_dir / 'profiles' / 'invalid.yaml'
        with open(invalid_file, 'w') as f:
            yaml.dump(invalid_profile, f)
        
        invalid_result = self.validator.validate_configuration_file(invalid_file)
        
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) > 0
        
        # Should have schema validation error for missing name
        schema_errors = [e for e in invalid_result.errors if e.error_type == "SchemaValidationError"]
        assert len(schema_errors) > 0
        
        # Should have file reference error for nonexistent context
        ref_errors = [e for e in invalid_result.errors if e.error_type == "MissingFileReference"]
        assert len(ref_errors) > 0
    
    def test_hook_loading_workflow(self):
        """Test hook loading workflow."""
        # Discover hooks
        discovered = self.loader.discover_configurations()
        hook_files = discovered['hooks']
        
        assert len(hook_files) >= 2
        
        # Load each discovered hook
        for hook_file in hook_files:
            hook_name = Path(hook_file).stem
            hook = self.loader.load_hook(hook_name)
            
            assert hook.name == hook_name
            assert hook.type in ['context', 'script', 'hybrid']
            assert hook.trigger in ['on_session_start', 'per_user_message', 'on_file_change']
        
        # Validate hook configurations
        for hook_file in hook_files:
            hook_path = self.test_dir / 'hooks' / Path(hook_file).name
            result = self.validator.validate_configuration_file(hook_path)
            
            assert result.is_valid is True, f"Hook {hook_file} should be valid"
    
    def test_profile_manager_integration(self):
        """Test integration with ProfileManager."""
        # List available profiles
        profiles = self.profile_manager.list_profiles()
        
        assert len(profiles) >= 2
        assert any(p['name'] == 'developer' for p in profiles)
        assert any(p['name'] == 'minimal' for p in profiles)
        
        # Load profile through ProfileManager
        developer_profile = self.profile_manager.load_profile('developer')
        
        assert developer_profile.name == 'developer'
        assert len(developer_profile.contexts) == 2
        
        # Verify ProfileManager validates before loading
        # (This assumes ProfileManager uses the validator internally)
        minimal_profile = self.profile_manager.load_profile('minimal')
        assert minimal_profile.name == 'minimal'
    
    def test_error_propagation_workflow(self):
        """Test that errors are properly propagated through the workflow."""
        # Create profile with syntax error
        syntax_error_file = self.test_dir / 'profiles' / 'syntax-error.yaml'
        syntax_error_file.write_text("""
name: syntax-error
description: Has syntax error
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
""")
        
        # Validation should catch syntax error
        result = self.validator.validate_configuration_file(syntax_error_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        syntax_error = result.errors[0]
        assert syntax_error.error_type == "YAMLSyntaxError"
        assert syntax_error.line_number is not None
        assert str(syntax_error_file) in syntax_error.file_path
        
        # Loading should fail with appropriate error
        with pytest.raises(Exception):
            self.loader.load_profile('syntax-error')
    
    def test_caching_across_workflow(self):
        """Test that caching works across the entire workflow."""
        # Load profile multiple times
        profile1 = self.loader.load_profile('developer')
        profile2 = self.loader.load_profile('developer')
        
        # Check cache statistics
        cache_stats = self.loader.get_cache_stats()
        assert cache_stats['config_cache_size'] > 0
        
        # Profiles should be identical (cached)
        assert profile1.name == profile2.name
        assert profile1.description == profile2.description
        
        # Clear cache and reload
        self.loader.clear_cache()
        profile3 = self.loader.load_profile('developer')
        
        # Should still work after cache clear
        assert profile3.name == 'developer'
        
        # Cache should be repopulated
        cache_stats_after = self.loader.get_cache_stats()
        assert cache_stats_after['config_cache_size'] > 0
    
    def test_comprehensive_validation_workflow(self):
        """Test comprehensive validation of entire configuration set."""
        # Run comprehensive validation
        report = self.validator.validate_all_configurations()
        
        # Should be valid since we created valid configurations
        assert report.is_valid is True
        assert len(report.errors) == 0
        
        # Check summary information
        assert 'total_files' in report.summary
        assert 'valid_files' in report.summary
        assert 'invalid_files' in report.summary
        assert report.summary['total_files'] >= 4  # 2 profiles + 2 hooks
        assert report.summary['valid_files'] == report.summary['total_files']
        assert report.summary['invalid_files'] == 0
        
        # Should have configuration summary info
        summary_info = [i for i in report.info if i.error_type == "ConfigurationSummary"]
        if summary_info:  # If summary is implemented
            summary_message = summary_info[0].message
            assert "Configuration Summary:" in summary_message
            assert "Profiles:" in summary_message
            assert "Hooks:" in summary_message


if __name__ == '__main__':
    pytest.main([__file__])