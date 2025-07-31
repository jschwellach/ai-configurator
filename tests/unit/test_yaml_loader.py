#!/usr/bin/env python3
"""Unit tests for YamlConfigLoader."""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.models import EnhancedProfileConfig, HookConfig, ValidationReport


class TestYamlConfigLoader:
    """Test suite for YamlConfigLoader."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.loader = YamlConfigLoader(self.test_dir)
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(exist_ok=True)
        (self.test_dir / 'hooks').mkdir(exist_ok=True)
        (self.test_dir / 'contexts').mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_discover_configurations(self):
        """Test configuration discovery functionality."""
        # Create test files
        profile_data = {'name': 'test-profile', 'description': 'Test'}
        hook_data = {'name': 'test-hook', 'type': 'context', 'trigger': 'on_session_start'}
        
        with open(self.test_dir / 'profiles' / 'test.yaml', 'w') as f:
            yaml.dump(profile_data, f)
        
        with open(self.test_dir / 'hooks' / 'test.yaml', 'w') as f:
            yaml.dump(hook_data, f)
        
        with open(self.test_dir / 'contexts' / 'test.md', 'w') as f:
            f.write('# Test Context')
        
        discovered = self.loader.discover_configurations()
        
        assert 'profiles' in discovered
        assert 'hooks' in discovered
        assert 'contexts' in discovered
        assert len(discovered['profiles']) == 1
        assert len(discovered['hooks']) == 1
        assert len(discovered['contexts']) == 1
        assert 'test.yaml' in discovered['profiles'][0]
    
    def test_load_profile_valid(self):
        """Test loading a valid profile."""
        profile_data = {
            'name': 'test-profile',
            'description': 'Test profile',
            'version': '1.0',
            'contexts': ['contexts/test.md'],
            'mcp_servers': ['core']
        }
        
        with open(self.test_dir / 'profiles' / 'test-profile.yaml', 'w') as f:
            yaml.dump(profile_data, f)
        
        profile = self.loader.load_profile('test-profile')
        
        assert isinstance(profile, EnhancedProfileConfig)
        assert profile.name == 'test-profile'
        assert profile.description == 'Test profile'
        assert profile.version == '1.0'
        assert 'contexts/test.md' in profile.contexts
    
    def test_load_profile_nonexistent(self):
        """Test loading a non-existent profile raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_profile('nonexistent')
    
    def test_load_hook_valid(self):
        """Test loading a valid hook."""
        hook_data = {
            'name': 'test-hook',
            'description': 'Test hook',
            'type': 'context',
            'trigger': 'on_session_start',
            'enabled': True,
            'context': {
                'sources': ['contexts/test.md']
            }
        }
        
        with open(self.test_dir / 'hooks' / 'test-hook.yaml', 'w') as f:
            yaml.dump(hook_data, f)
        
        hook = self.loader.load_hook('test-hook')
        
        assert isinstance(hook, HookConfig)
        assert hook.name == 'test-hook'
        assert hook.type == 'context'
        assert hook.trigger == 'on_session_start'
        assert hook.enabled is True
    
    def test_validate_yaml_file_valid(self):
        """Test validation of a valid YAML file."""
        profile_data = {
            'name': 'valid-profile',
            'description': 'Valid test profile'
        }
        
        profile_file = self.test_dir / 'profiles' / 'valid.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        result = self.loader.validate_yaml_file(profile_file)
        
        assert isinstance(result, ValidationReport)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_yaml_file_syntax_error(self):
        """Test validation of YAML file with syntax error."""
        invalid_yaml = """
name: test
description: Invalid YAML
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
"""
        
        invalid_file = self.test_dir / 'profiles' / 'invalid.yaml'
        with open(invalid_file, 'w') as f:
            f.write(invalid_yaml)
        
        result = self.loader.validate_yaml_file(invalid_file)
        
        assert isinstance(result, ValidationReport)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any(error.error_type == "YAMLSyntaxError" for error in result.errors)
    
    def test_caching_functionality(self):
        """Test that caching works correctly."""
        profile_data = {'name': 'cached-profile', 'description': 'Test caching'}
        
        with open(self.test_dir / 'profiles' / 'cached.yaml', 'w') as f:
            yaml.dump(profile_data, f)
        
        # Load profile twice
        profile1 = self.loader.load_profile('cached')
        profile2 = self.loader.load_profile('cached')
        
        # Check cache stats
        cache_stats = self.loader.get_cache_stats()
        assert cache_stats['config_cache_size'] > 0
        
        # Profiles should be identical (from cache)
        assert profile1.name == profile2.name
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        profile_data = {'name': 'test-profile', 'description': 'Test'}
        
        with open(self.test_dir / 'profiles' / 'test.yaml', 'w') as f:
            yaml.dump(profile_data, f)
        
        # Load profile to populate cache
        self.loader.load_profile('test')
        
        # Verify cache has content
        cache_stats = self.loader.get_cache_stats()
        assert cache_stats['config_cache_size'] > 0
        
        # Clear cache
        self.loader.clear_cache()
        
        # Verify cache is empty
        cache_stats_after = self.loader.get_cache_stats()
        assert cache_stats_after['config_cache_size'] == 0
    
    def test_yaml_loading_error_handling(self):
        """Test error handling during YAML loading."""
        # Create file with invalid YAML structure
        with open(self.test_dir / 'profiles' / 'malformed.yaml', 'w') as f:
            f.write('{ invalid json/yaml hybrid }')
        
        # This should load successfully as it's valid YAML (just unusual structure)
        # The validation would catch semantic issues, not syntax issues
        profile = self.loader.load_profile('malformed')
        assert profile.name == 'malformed'
    
    def test_file_not_found_handling(self):
        """Test handling of missing files."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_profile('missing-file')
        
        with pytest.raises(FileNotFoundError):
            self.loader.load_hook('missing-hook')
    
    def test_empty_yaml_file(self):
        """Test handling of empty YAML files."""
        empty_file = self.test_dir / 'profiles' / 'empty.yaml'
        empty_file.touch()
        
        result = self.loader.validate_yaml_file(empty_file)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_yaml_with_null_values(self):
        """Test handling of YAML with null values."""
        profile_data = {
            'name': 'null-test',
            'description': None,
            # Don't include contexts as None since it expects a list
        }
        
        with open(self.test_dir / 'profiles' / 'null-test.yaml', 'w') as f:
            yaml.dump(profile_data, f)
        
        profile = self.loader.load_profile('null-test')
        assert profile.name == 'null-test'
        assert profile.description is None


if __name__ == '__main__':
    pytest.main([__file__])