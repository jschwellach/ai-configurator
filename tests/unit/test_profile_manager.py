"""Tests for ProfileManager functionality."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

# Add src to path for imports
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.profile_manager import ProfileManager
from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.models import EnhancedProfileConfig, ValidationReport


class TestProfileManager(unittest.TestCase):
    """Test cases for ProfileManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.profiles_dir = self.test_dir / 'profiles'
        self.hooks_dir = self.test_dir / 'hooks'
        self.contexts_dir = self.test_dir / 'contexts'
        
        # Create directory structure
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ProfileManager
        self.profile_manager = ProfileManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def create_test_profile(self, name: str, **kwargs) -> Path:
        """Create a test profile file."""
        profile_data = {
            'name': name,
            'description': f'Test profile {name}',
            'version': '1.0',
            'contexts': [],
            'hooks': {},
            'mcp_servers': [],
            'settings': {
                'auto_backup': True,
                'validation_level': 'normal'
            },
            **kwargs
        }
        
        profile_file = self.profiles_dir / f'{name}.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        return profile_file
    
    def create_test_context(self, name: str, content: str = "Test context") -> Path:
        """Create a test context file."""
        context_file = self.contexts_dir / f'{name}.md'
        context_file.write_text(content)
        return context_file
    
    def create_test_hook(self, name: str, **kwargs) -> Path:
        """Create a test hook file."""
        hook_data = {
            'name': name,
            'description': f'Test hook {name}',
            'type': 'context',
            'trigger': 'on_session_start',
            **kwargs
        }
        
        hook_file = self.hooks_dir / f'{name}.yaml'
        with open(hook_file, 'w') as f:
            yaml.dump(hook_data, f)
        
        return hook_file
    
    def test_initialization(self):
        """Test ProfileManager initialization."""
        # Test with default path
        pm = ProfileManager()
        self.assertIsInstance(pm.yaml_loader, YamlConfigLoader)
        self.assertTrue(pm.profiles_dir.exists())
        
        # Test with custom path
        pm = ProfileManager(self.test_dir)
        self.assertEqual(pm.base_path, self.test_dir)
        self.assertEqual(pm.profiles_dir, self.test_dir / 'profiles')
    
    def test_discover_profiles_empty(self):
        """Test profile discovery with no profiles."""
        profiles = self.profile_manager.discover_profiles()
        self.assertEqual(profiles, [])
    
    def test_discover_profiles_with_files(self):
        """Test profile discovery with multiple profiles."""
        # Create test profiles
        self.create_test_profile('developer')
        self.create_test_profile('production')
        self.create_test_profile('testing')
        
        profiles = self.profile_manager.discover_profiles()
        self.assertEqual(sorted(profiles), ['developer', 'production', 'testing'])
    
    def test_discover_profiles_different_extensions(self):
        """Test profile discovery with different YAML extensions."""
        # Create profiles with different extensions
        (self.profiles_dir / 'profile1.yaml').write_text('name: profile1')
        (self.profiles_dir / 'profile2.yml').write_text('name: profile2')
        (self.profiles_dir / 'profile3.txt').write_text('name: profile3')  # Should be ignored
        
        profiles = self.profile_manager.discover_profiles()
        self.assertEqual(sorted(profiles), ['profile1', 'profile2'])
    
    def test_discover_profiles_caching(self):
        """Test profile discovery caching mechanism."""
        self.create_test_profile('test')
        
        # First call should populate cache
        profiles1 = self.profile_manager.discover_profiles()
        self.assertEqual(profiles1, ['test'])
        
        # Second call should use cache
        profiles2 = self.profile_manager.discover_profiles()
        self.assertEqual(profiles2, ['test'])
        
        # Force refresh should bypass cache
        self.create_test_profile('test2')
        profiles3 = self.profile_manager.discover_profiles(force_refresh=True)
        self.assertEqual(sorted(profiles3), ['test', 'test2'])
    
    def test_load_profile_success(self):
        """Test successful profile loading."""
        self.create_test_profile('developer', contexts=['contexts/dev.md'])
        
        profile = self.profile_manager.load_profile('developer')
        
        self.assertIsInstance(profile, EnhancedProfileConfig)
        self.assertEqual(profile.name, 'developer')
        self.assertEqual(profile.description, 'Test profile developer')
        self.assertEqual(profile.contexts, ['contexts/dev.md'])
    
    def test_load_profile_not_found(self):
        """Test loading non-existent profile."""
        with self.assertRaises(FileNotFoundError):
            self.profile_manager.load_profile('nonexistent')
    
    def test_load_profile_invalid_yaml(self):
        """Test loading profile with invalid YAML."""
        profile_file = self.profiles_dir / 'invalid.yaml'
        profile_file.write_text('invalid: yaml: content: [')
        
        with self.assertRaises(yaml.YAMLError):
            self.profile_manager.load_profile('invalid')
    
    def test_load_profile_caching(self):
        """Test profile loading caching."""
        self.create_test_profile('cached')
        
        # First load
        profile1 = self.profile_manager.load_profile('cached')
        
        # Second load should use cache
        profile2 = self.profile_manager.load_profile('cached', use_cache=True)
        
        # Should be the same object from cache
        self.assertIs(profile1, profile2)
        
        # Force reload should bypass cache
        profile3 = self.profile_manager.load_profile('cached', use_cache=False)
        self.assertIsNot(profile1, profile3)
        self.assertEqual(profile1.name, profile3.name)
    
    def test_validate_profile_success(self):
        """Test successful profile validation."""
        self.create_test_profile('valid')
        
        report = self.profile_manager.validate_profile('valid')
        
        self.assertIsInstance(report, ValidationReport)
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.errors), 0)
    
    def test_validate_profile_not_found(self):
        """Test validation of non-existent profile."""
        report = self.profile_manager.validate_profile('nonexistent')
        
        self.assertFalse(report.is_valid)
        self.assertEqual(len(report.errors), 1)
        self.assertEqual(report.errors[0].error_type, 'FileNotFound')
    
    def test_validate_profile_with_missing_references(self):
        """Test validation with missing context/hook references."""
        # Create profile with missing references
        self.create_test_profile('with_refs', 
                                contexts=['contexts/missing.md'],
                                hooks={'on_session_start': [{'name': 'missing_hook', 'enabled': True}]})
        
        report = self.profile_manager.validate_profile('with_refs')
        
        # Should still be valid (missing references are warnings, not errors)
        self.assertTrue(report.is_valid)
        self.assertGreater(len(report.warnings), 0)
        
        # Check for specific warning types
        warning_types = [w.error_type for w in report.warnings]
        self.assertIn('MissingContextReference', warning_types)
        self.assertIn('MissingHookReference', warning_types)
    
    def test_validate_all_profiles(self):
        """Test validation of all profiles."""
        # Create mix of valid and invalid profiles
        self.create_test_profile('valid1')
        self.create_test_profile('valid2')
        
        # Create invalid profile
        invalid_file = self.profiles_dir / 'invalid.yaml'
        invalid_file.write_text('invalid: yaml: [')
        
        report = self.profile_manager.validate_all_profiles()
        
        self.assertFalse(report.is_valid)  # Should be invalid due to syntax error
        self.assertGreater(len(report.errors), 0)
        self.assertEqual(report.summary['profiles_checked'], 3)
    
    def test_list_profiles_basic(self):
        """Test basic profile listing."""
        self.create_test_profile('profile1')
        self.create_test_profile('profile2')
        
        profiles = self.profile_manager.list_profiles(include_descriptions=False)
        
        self.assertEqual(len(profiles), 2)
        self.assertIn('profile1', profiles)
        self.assertIn('profile2', profiles)
        
        for profile_info in profiles.values():
            self.assertIn('name', profile_info)
            self.assertIn('file_path', profile_info)
            self.assertIn('exists', profile_info)
    
    def test_list_profiles_with_descriptions(self):
        """Test profile listing with descriptions."""
        self.create_test_profile('detailed', 
                                description='Detailed profile',
                                contexts=['ctx1.md', 'ctx2.md'])
        
        profiles = self.profile_manager.list_profiles(include_descriptions=True)
        
        profile_info = profiles['detailed']
        self.assertEqual(profile_info['description'], 'Detailed profile')
        self.assertEqual(profile_info['version'], '1.0')
        self.assertEqual(profile_info['contexts_count'], 2)
    
    def test_get_profile_summary(self):
        """Test getting detailed profile summary."""
        # Create context and hook files for references
        self.create_test_context('test_context')
        self.create_test_hook('test_hook')
        
        self.create_test_profile('summary_test',
                                contexts=['contexts/test_context.md'],
                                hooks={'on_session_start': [{'name': 'test_hook', 'enabled': True}]})
        
        summary = self.profile_manager.get_profile_summary('summary_test')
        
        self.assertEqual(summary['name'], 'summary_test')
        self.assertIn('file_path', summary)
        self.assertIn('contexts', summary)
        self.assertIn('hooks', summary)
        self.assertIn('validation', summary)
        self.assertIn('file_stats', summary)
    
    def test_create_profile_template(self):
        """Test creating a new profile template."""
        profile_file = self.profile_manager.create_profile_template('new_profile', 'New test profile')
        
        self.assertTrue(profile_file.exists())
        
        # Load and verify template
        with open(profile_file, 'r') as f:
            data = yaml.safe_load(f)
        
        self.assertEqual(data['name'], 'new_profile')
        self.assertEqual(data['description'], 'New test profile')
        self.assertEqual(data['version'], '1.0')
        self.assertIn('contexts', data)
        self.assertIn('hooks', data)
        self.assertIn('settings', data)
    
    def test_create_profile_template_already_exists(self):
        """Test creating template when profile already exists."""
        self.create_test_profile('existing')
        
        with self.assertRaises(FileExistsError):
            self.profile_manager.create_profile_template('existing')
    
    def test_delete_profile_success(self):
        """Test successful profile deletion."""
        self.create_test_profile('to_delete')
        
        # Verify profile exists
        self.assertIn('to_delete', self.profile_manager.discover_profiles())
        
        # Delete profile
        result = self.profile_manager.delete_profile('to_delete')
        
        self.assertTrue(result)
        self.assertNotIn('to_delete', self.profile_manager.discover_profiles(force_refresh=True))
    
    def test_delete_profile_with_backup(self):
        """Test profile deletion with backup creation."""
        self.create_test_profile('backup_test')
        
        result = self.profile_manager.delete_profile('backup_test', create_backup=True)
        
        self.assertTrue(result)
        
        # Check backup was created
        backup_dir = self.test_dir / 'backups' / 'profiles'
        self.assertTrue(backup_dir.exists())
        
        backup_files = list(backup_dir.glob('backup_test_*.yaml'))
        self.assertEqual(len(backup_files), 1)
    
    def test_delete_profile_not_found(self):
        """Test deleting non-existent profile."""
        result = self.profile_manager.delete_profile('nonexistent')
        self.assertFalse(result)
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        self.create_test_profile('cached')
        
        # Load profile to populate cache
        self.profile_manager.load_profile('cached')
        
        # Verify cache is populated
        self.assertIn('cached', self.profile_manager._profile_cache)
        
        # Clear specific profile cache
        self.profile_manager.clear_cache('cached')
        self.assertNotIn('cached', self.profile_manager._profile_cache)
        
        # Load again and clear all cache
        self.profile_manager.load_profile('cached')
        self.profile_manager.clear_cache()
        self.assertEqual(len(self.profile_manager._profile_cache), 0)
    
    def test_get_cache_stats(self):
        """Test cache statistics retrieval."""
        self.create_test_profile('stats_test')
        self.profile_manager.load_profile('stats_test')
        
        stats = self.profile_manager.get_cache_stats()
        
        self.assertIn('profile_cache_size', stats)
        self.assertIn('cached_profiles', stats)
        self.assertIn('discovery_cache_valid', stats)
        self.assertIn('yaml_loader_stats', stats)
        
        self.assertEqual(stats['profile_cache_size'], 1)
        self.assertIn('stats_test', stats['cached_profiles'])
    
    def test_get_profile_file_path(self):
        """Test profile file path resolution."""
        # Create profiles with different extensions
        yaml_file = self.profiles_dir / 'test.yaml'
        yml_file = self.profiles_dir / 'test2.yml'
        
        yaml_file.write_text('name: test')
        yml_file.write_text('name: test2')
        
        # Test existing files
        self.assertEqual(self.profile_manager._get_profile_file_path('test'), yaml_file)
        self.assertEqual(self.profile_manager._get_profile_file_path('test2'), yml_file)
        
        # Test non-existing file (should return preferred path)
        expected_path = self.profiles_dir / 'nonexistent.yaml'
        self.assertEqual(self.profile_manager._get_profile_file_path('nonexistent'), expected_path)
    
    def test_validate_profile_references(self):
        """Test profile reference validation."""
        # Create some context and hook files
        self.create_test_context('existing_context')
        self.create_test_hook('existing_hook')
        
        # Create MCP server config
        mcp_dir = self.test_dir / 'configs' / 'mcp-servers'
        mcp_dir.mkdir(parents=True, exist_ok=True)
        mcp_config = {
            'mcpServers': {
                'test_server': {'command': 'test'},
                'another_server': {'command': 'another'}
            }
        }
        with open(mcp_dir / 'test.json', 'w') as f:
            json.dump(mcp_config, f)
        
        # Create profile with mixed references
        profile_data = {
            'name': 'ref_test',
            'contexts': [
                'contexts/existing_context.md',
                'contexts/missing_context.md',
                'contexts/*.md'  # Glob pattern - should be skipped
            ],
            'hooks': {
                'on_session_start': [
                    {'name': 'existing_hook', 'enabled': True},
                    {'name': 'missing_hook', 'enabled': True}
                ]
            },
            'mcp_servers': ['test_server', 'missing_server']
        }
        
        profile = EnhancedProfileConfig(**profile_data)
        errors, warnings = self.profile_manager._validate_profile_references(profile)
        
        # Should have warnings for missing references
        self.assertEqual(len(errors), 0)  # No errors, just warnings
        self.assertGreater(len(warnings), 0)
        
        warning_types = [w.error_type for w in warnings]
        self.assertIn('MissingContextReference', warning_types)
        self.assertIn('MissingHookReference', warning_types)
        self.assertIn('UnknownMCPServer', warning_types)


if __name__ == '__main__':
    unittest.main()