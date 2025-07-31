#!/usr/bin/env python3
"""Test script for YamlConfigLoader implementation."""

import os
import tempfile
import shutil
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.models import EnhancedProfileConfig, HookConfig


def create_test_files(test_dir: Path):
    """Create test YAML files for testing."""
    
    # Create directory structure
    (test_dir / 'profiles').mkdir(exist_ok=True)
    (test_dir / 'hooks').mkdir(exist_ok=True)
    (test_dir / 'contexts').mkdir(exist_ok=True)
    
    # Create a valid profile YAML
    profile_config = {
        'name': 'test-profile',
        'description': 'Test profile for validation',
        'version': '1.0',
        'contexts': ['contexts/test-context.md'],
        'hooks': {
            'on_session_start': [
                {'name': 'test-hook', 'enabled': True}
            ]
        },
        'mcp_servers': ['core', 'development'],
        'settings': {
            'auto_backup': True,
            'validation_level': 'normal'
        }
    }
    
    with open(test_dir / 'profiles' / 'test-profile.yaml', 'w') as f:
        yaml.dump(profile_config, f, default_flow_style=False)
    
    # Create a valid hook YAML
    hook_config = {
        'name': 'test-hook',
        'description': 'Test hook for validation',
        'version': '1.0',
        'type': 'context',
        'trigger': 'on_session_start',
        'timeout': 30,
        'enabled': True,
        'context': {
            'sources': ['contexts/hook-context.md'],
            'tags': ['test', 'development'],
            'priority': 1
        }
    }
    
    with open(test_dir / 'hooks' / 'test-hook.yaml', 'w') as f:
        yaml.dump(hook_config, f, default_flow_style=False)
    
    # Create an invalid YAML file (syntax error)
    with open(test_dir / 'profiles' / 'invalid-profile.yaml', 'w') as f:
        f.write("""
name: invalid-profile
description: This has a syntax error
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
""")
    
    # Create a context file
    with open(test_dir / 'contexts' / 'test-context.md', 'w') as f:
        f.write("""---
tags: [test, context]
priority: 1
---

# Test Context

This is a test context file.
""")


def test_yaml_loader():
    """Test the YamlConfigLoader functionality."""
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_test_files(test_dir)
        
        # Initialize loader
        loader = YamlConfigLoader(test_dir)
        
        print("🧪 Testing YamlConfigLoader")
        print("=" * 50)
        
        # Test 1: Discovery
        print("\n1. Testing configuration discovery...")
        discovered = loader.discover_configurations()
        print(f"   Discovered configurations: {discovered}")
        
        assert 'profiles' in discovered
        assert 'hooks' in discovered
        assert 'contexts' in discovered
        assert len(discovered['profiles']) >= 2  # test-profile.yaml and invalid-profile.yaml
        assert len(discovered['hooks']) >= 1    # test-hook.yaml
        print("   ✅ Discovery test passed")
        
        # Test 2: Load valid profile
        print("\n2. Testing valid profile loading...")
        try:
            profile = loader.load_profile('test-profile')
            print(f"   Loaded profile: {profile.name}")
            print(f"   Description: {profile.description}")
            print(f"   Contexts: {profile.contexts}")
            print(f"   MCP Servers: {profile.mcp_servers}")
            assert isinstance(profile, EnhancedProfileConfig)
            assert profile.name == 'test-profile'
            print("   ✅ Valid profile loading test passed")
        except Exception as e:
            print(f"   ❌ Profile loading failed: {e}")
            raise
        
        # Test 3: Load valid hook
        print("\n3. Testing valid hook loading...")
        try:
            hook = loader.load_hook('test-hook')
            print(f"   Loaded hook: {hook.name}")
            print(f"   Type: {hook.type}")
            print(f"   Trigger: {hook.trigger}")
            assert isinstance(hook, HookConfig)
            assert hook.name == 'test-hook'
            print("   ✅ Valid hook loading test passed")
        except Exception as e:
            print(f"   ❌ Hook loading failed: {e}")
            raise
        
        # Test 4: Validation of valid file
        print("\n4. Testing validation of valid file...")
        valid_file = test_dir / 'profiles' / 'test-profile.yaml'
        validation_result = loader.validate_yaml_file(valid_file)
        print(f"   Validation result: Valid={validation_result.is_valid}")
        print(f"   Errors: {len(validation_result.errors)}")
        print(f"   Warnings: {len(validation_result.warnings)}")
        print(f"   Info: {len(validation_result.info)}")
        
        if validation_result.errors:
            for error in validation_result.errors:
                print(f"     Error: {error.message}")
        
        assert validation_result.is_valid
        print("   ✅ Valid file validation test passed")
        
        # Test 5: Validation of invalid file
        print("\n5. Testing validation of invalid file...")
        invalid_file = test_dir / 'profiles' / 'invalid-profile.yaml'
        validation_result = loader.validate_yaml_file(invalid_file)
        print(f"   Validation result: Valid={validation_result.is_valid}")
        print(f"   Errors: {len(validation_result.errors)}")
        
        if validation_result.errors:
            for error in validation_result.errors:
                print(f"     Error: {error.message}")
                if error.line_number:
                    print(f"     Line: {error.line_number}")
                if error.context:
                    print(f"     Context:\n{error.context}")
        
        assert not validation_result.is_valid
        assert len(validation_result.errors) > 0
        print("   ✅ Invalid file validation test passed")
        
        # Test 6: Caching
        print("\n6. Testing caching functionality...")
        # Load the same profile twice
        profile1 = loader.load_profile('test-profile')
        profile2 = loader.load_profile('test-profile')
        
        # Check cache stats
        cache_stats = loader.get_cache_stats()
        print(f"   Cache stats: {cache_stats}")
        assert cache_stats['config_cache_size'] > 0
        print("   ✅ Caching test passed")
        
        # Test 7: Non-existent file
        print("\n7. Testing non-existent file handling...")
        try:
            loader.load_profile('non-existent-profile')
            print("   ❌ Should have raised FileNotFoundError")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            print(f"   Expected error caught: {e}")
            print("   ✅ Non-existent file test passed")
        
        # Test 8: Cache clearing
        print("\n8. Testing cache clearing...")
        loader.clear_cache()
        cache_stats_after = loader.get_cache_stats()
        print(f"   Cache stats after clearing: {cache_stats_after}")
        assert cache_stats_after['config_cache_size'] == 0
        print("   ✅ Cache clearing test passed")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")


if __name__ == '__main__':
    test_yaml_loader()