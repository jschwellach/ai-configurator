"""Integration tests for ProfileManager with the broader system."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

# Add src to path for imports
import sys
sys.path.insert(0, 'src')

from ai_configurator.core import ProfileManager, YamlConfigLoader, ConfigurationMerger


class TestProfileManagerIntegration(unittest.TestCase):
    """Integration test cases for ProfileManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(parents=True, exist_ok=True)
        (self.test_dir / 'hooks').mkdir(parents=True, exist_ok=True)
        (self.test_dir / 'contexts').mkdir(parents=True, exist_ok=True)
        (self.test_dir / 'configs' / 'mcp-servers').mkdir(parents=True, exist_ok=True)
        
        # Initialize ProfileManager
        self.profile_manager = ProfileManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_end_to_end_profile_workflow(self):
        """Test complete profile management workflow."""
        print("\n=== ProfileManager Integration Test ===")
        
        # 1. Create a comprehensive profile template
        print("\n1. Creating profile template...")
        profile_file = self.profile_manager.create_profile_template(
            'integration-test',
            'Integration test profile with comprehensive features'
        )
        self.assertTrue(profile_file.exists())
        print(f"   Created: {profile_file}")
        
        # 2. Discover profiles
        print("\n2. Discovering profiles...")
        profiles = self.profile_manager.discover_profiles()
        self.assertIn('integration-test', profiles)
        print(f"   Found profiles: {profiles}")
        
        # 3. Load and validate the profile
        print("\n3. Loading and validating profile...")
        profile = self.profile_manager.load_profile('integration-test')
        self.assertEqual(profile.name, 'integration-test')
        print(f"   Profile loaded: {profile.name} v{profile.version}")
        
        validation_report = self.profile_manager.validate_profile('integration-test')
        self.assertTrue(validation_report.is_valid)
        print(f"   Validation: {'✓ PASSED' if validation_report.is_valid else '✗ FAILED'}")
        
        # 4. Create supporting files (contexts and hooks)
        print("\n4. Creating supporting files...")
        
        # Create context files
        context_file = self.test_dir / 'contexts' / 'integration-context.md'
        context_file.write_text("""---
tags: [integration, testing]
priority: 10
---

# Integration Test Context

This is a test context file for integration testing.
""")
        
        # Create hook file
        hook_data = {
            'name': 'integration-hook',
            'description': 'Integration test hook',
            'type': 'context',
            'trigger': 'on_session_start',
            'context': {
                'sources': ['contexts/integration-context.md']
            }
        }
        hook_file = self.test_dir / 'hooks' / 'integration-hook.yaml'
        with open(hook_file, 'w') as f:
            yaml.dump(hook_data, f)
        
        # Create MCP server config
        mcp_config = {
            'mcpServers': {
                'integration-server': {
                    'command': 'test-command',
                    'args': ['--test'],
                    'disabled': False
                }
            }
        }
        mcp_file = self.test_dir / 'configs' / 'mcp-servers' / 'integration.json'
        with open(mcp_file, 'w') as f:
            json.dump(mcp_config, f)
        
        print(f"   Created context: {context_file}")
        print(f"   Created hook: {hook_file}")
        print(f"   Created MCP config: {mcp_file}")
        
        # 5. Update profile with references
        print("\n5. Updating profile with references...")
        updated_profile_data = {
            'name': 'integration-test',
            'description': 'Updated integration test profile',
            'version': '1.1',
            'contexts': [
                'contexts/integration-context.md'
            ],
            'hooks': {
                'on_session_start': [
                    {
                        'name': 'integration-hook',
                        'enabled': True,
                        'timeout': 60
                    }
                ]
            },
            'mcp_servers': ['integration-server'],
            'settings': {
                'auto_backup': True,
                'validation_level': 'strict',
                'hot_reload': True,
                'cache_enabled': True
            },
            'metadata': {
                'updated': '2024-01-01T00:00:00Z',
                'test_run': True
            }
        }
        
        with open(profile_file, 'w') as f:
            yaml.dump(updated_profile_data, f)
        
        # Clear cache to reload updated profile
        self.profile_manager.clear_cache('integration-test')
        
        # 6. Load updated profile and validate references
        print("\n6. Loading updated profile...")
        updated_profile = self.profile_manager.load_profile('integration-test')
        self.assertEqual(updated_profile.version, '1.1')
        self.assertEqual(len(updated_profile.contexts), 1)
        self.assertEqual(len(updated_profile.mcp_servers), 1)
        print(f"   Updated profile: v{updated_profile.version}")
        print(f"   Contexts: {updated_profile.contexts}")
        print(f"   MCP servers: {updated_profile.mcp_servers}")
        
        # Validate with references
        validation_report = self.profile_manager.validate_profile('integration-test')
        print(f"   Validation with references: {'✓ PASSED' if validation_report.is_valid else '✗ FAILED'}")
        if validation_report.warnings:
            print(f"   Warnings: {len(validation_report.warnings)}")
        
        # 7. Get profile summary
        print("\n7. Getting profile summary...")
        summary = self.profile_manager.get_profile_summary('integration-test')
        self.assertIn('validation', summary)
        self.assertIn('file_stats', summary)
        print(f"   Summary keys: {list(summary.keys())}")
        
        # 8. List all profiles with descriptions
        print("\n8. Listing all profiles...")
        all_profiles = self.profile_manager.list_profiles(include_descriptions=True)
        self.assertIn('integration-test', all_profiles)
        profile_info = all_profiles['integration-test']
        print(f"   Profile info: {profile_info['name']} - {profile_info['description']}")
        
        # 9. Test cache functionality
        print("\n9. Testing cache functionality...")
        cache_stats_before = self.profile_manager.get_cache_stats()
        
        # Load profile again (should use cache)
        cached_profile = self.profile_manager.load_profile('integration-test')
        # Should be the same profile data, but might be different objects due to cache invalidation
        self.assertEqual(updated_profile.name, cached_profile.name)
        self.assertEqual(updated_profile.version, cached_profile.version)
        
        cache_stats_after = self.profile_manager.get_cache_stats()
        print(f"   Cache stats: {cache_stats_after['profile_cache_size']} profiles cached")
        
        # 10. Test validation of all profiles
        print("\n10. Validating all profiles...")
        all_validation = self.profile_manager.validate_all_profiles()
        print(f"   Overall validation: {'✓ PASSED' if all_validation.is_valid else '✗ FAILED'}")
        print(f"   Profiles checked: {all_validation.summary.get('profiles_checked', 0)}")
        
        # 11. Create backup and delete profile
        print("\n11. Testing profile deletion with backup...")
        delete_result = self.profile_manager.delete_profile('integration-test', create_backup=True)
        self.assertTrue(delete_result)
        
        # Verify profile is gone
        profiles_after_delete = self.profile_manager.discover_profiles(force_refresh=True)
        self.assertNotIn('integration-test', profiles_after_delete)
        
        # Verify backup exists
        backup_dir = self.test_dir / 'backups' / 'profiles'
        backup_files = list(backup_dir.glob('integration-test_*.yaml'))
        self.assertEqual(len(backup_files), 1)
        print(f"   Profile deleted, backup created: {backup_files[0].name}")
        
        print("\n=== Integration Test Complete ===")
    
    def test_yaml_loader_integration(self):
        """Test ProfileManager integration with YamlConfigLoader."""
        # Create a profile with complex structure
        complex_profile = {
            'name': 'complex-test',
            'description': 'Complex profile for testing YAML loader integration',
            'version': '2.0',
            'contexts': [
                'contexts/shared/*.md',
                'contexts/specific/test.md'
            ],
            'hooks': {
                'on_session_start': [
                    {'name': 'startup-hook', 'enabled': True, 'timeout': 30},
                    {'name': 'init-hook', 'enabled': False}
                ],
                'per_user_message': [
                    {'name': 'message-processor', 'enabled': True}
                ]
            },
            'mcp_servers': ['core', 'development', 'testing'],
            'settings': {
                'auto_backup': False,
                'validation_level': 'permissive',
                'hot_reload': False,
                'cache_enabled': True,
                'max_context_size': 50000
            },
            'metadata': {
                'created_by': 'integration_test',
                'tags': ['complex', 'testing', 'integration'],
                'priority': 5
            }
        }
        
        profile_file = self.test_dir / 'profiles' / 'complex-test.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(complex_profile, f)
        
        # Test loading through ProfileManager
        profile = self.profile_manager.load_profile('complex-test')
        
        # Verify all fields are correctly loaded and validated
        self.assertEqual(profile.name, 'complex-test')
        self.assertEqual(profile.version, '2.0')
        self.assertEqual(len(profile.contexts), 2)
        self.assertEqual(len(profile.hooks), 2)  # Two trigger types
        self.assertEqual(len(profile.mcp_servers), 3)
        self.assertEqual(profile.settings.validation_level.value, 'permissive')
        self.assertEqual(profile.settings.max_context_size, 50000)
        self.assertIn('tags', profile.metadata)
        
        # Test validation
        validation_report = self.profile_manager.validate_profile('complex-test')
        # Should be valid despite missing referenced files (warnings only)
        self.assertTrue(validation_report.is_valid)
        
        print(f"Complex profile loaded successfully: {profile.name} v{profile.version}")
        print(f"Hooks: {sum(len(hooks) for hooks in profile.hooks.values())} total")
        print(f"Validation: {'✓ PASSED' if validation_report.is_valid else '✗ FAILED'}")


if __name__ == '__main__':
    unittest.main(verbosity=2)