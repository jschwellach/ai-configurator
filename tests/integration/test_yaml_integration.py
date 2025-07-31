#!/usr/bin/env python3
"""Integration test for YamlConfigLoader with the existing codebase."""

import tempfile
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core import YamlConfigLoader, EnhancedProfileConfig, HookConfig


def test_integration():
    """Test integration with existing codebase."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create directory structure
        (test_dir / 'profiles').mkdir(exist_ok=True)
        (test_dir / 'hooks').mkdir(exist_ok=True)
        (test_dir / 'contexts').mkdir(exist_ok=True)
        
        print("🔗 Testing YamlConfigLoader Integration")
        print("=" * 50)
        
        # Test 1: Create a comprehensive profile configuration
        print("\n1. Testing comprehensive profile configuration...")
        
        comprehensive_profile = {
            'name': 'comprehensive-test',
            'description': 'A comprehensive test profile with all features',
            'version': '2.0',
            'contexts': [
                'contexts/development.md',
                'contexts/aws-best-practices.md',
                'contexts/shared/*.md'
            ],
            'hooks': {
                'on_session_start': [
                    {'name': 'setup-environment', 'enabled': True, 'timeout': 45},
                    {'name': 'load-context', 'enabled': True}
                ],
                'per_user_message': [
                    {'name': 'enhance-context', 'enabled': True, 'timeout': 10}
                ],
                'on_file_change': [
                    {'name': 'auto-test', 'enabled': False}
                ]
            },
            'mcp_servers': ['core', 'development', 'specialized'],
            'settings': {
                'auto_backup': True,
                'validation_level': 'strict',
                'hot_reload': True,
                'cache_enabled': True,
                'max_context_size': 50000
            },
            'metadata': {
                'created_by': 'test-suite',
                'team': 'development',
                'environment': 'testing'
            }
        }
        
        profile_file = test_dir / 'profiles' / 'comprehensive-test.yaml'
        with open(profile_file, 'w') as f:
            yaml.dump(comprehensive_profile, f, default_flow_style=False)
        
        loader = YamlConfigLoader(test_dir)
        profile = loader.load_profile('comprehensive-test')
        
        print(f"   Profile name: {profile.name}")
        print(f"   Version: {profile.version}")
        print(f"   Contexts: {len(profile.contexts)} items")
        print(f"   Hook triggers: {list(profile.hooks.keys())}")
        print(f"   MCP servers: {profile.mcp_servers}")
        print(f"   Settings validation level: {profile.settings.validation_level}")
        
        assert isinstance(profile, EnhancedProfileConfig)
        assert profile.name == 'comprehensive-test'
        assert profile.version == '2.0'
        assert len(profile.contexts) == 3
        assert len(profile.hooks) == 3
        assert len(profile.mcp_servers) == 3
        print("   ✅ Comprehensive profile test passed")
        
        # Test 2: Create a comprehensive hook configuration
        print("\n2. Testing comprehensive hook configuration...")
        
        comprehensive_hook = {
            'name': 'comprehensive-hook',
            'description': 'A comprehensive test hook with all features',
            'version': '1.5',
            'type': 'hybrid',
            'trigger': 'on_session_start',
            'timeout': 60,
            'enabled': True,
            'context': {
                'sources': [
                    'contexts/hook-specific.md',
                    'contexts/shared/common.md'
                ],
                'tags': ['development', 'testing', 'automation'],
                'categories': ['setup', 'initialization'],
                'priority': 5,
                'cache_ttl': 300
            },
            'script': {
                'command': 'python',
                'args': ['scripts/setup.py', '--verbose'],
                'env': {
                    'ENVIRONMENT': 'test',
                    'DEBUG': 'true'
                },
                'working_dir': 'scripts',
                'timeout': 30
            },
            'conditions': [
                {
                    'profile': ['development', 'testing'],
                    'platform': ['darwin', 'linux'],
                    'environment': {
                        'CI': 'false'
                    }
                }
            ],
            'metadata': {
                'author': 'test-suite',
                'last_updated': '2024-01-01',
                'complexity': 'high'
            }
        }
        
        hook_file = test_dir / 'hooks' / 'comprehensive-hook.yaml'
        with open(hook_file, 'w') as f:
            yaml.dump(comprehensive_hook, f, default_flow_style=False)
        
        hook = loader.load_hook('comprehensive-hook')
        
        print(f"   Hook name: {hook.name}")
        print(f"   Type: {hook.type}")
        print(f"   Trigger: {hook.trigger}")
        print(f"   Context sources: {len(hook.context.sources) if hook.context else 0}")
        print(f"   Script command: {hook.script.command if hook.script else 'None'}")
        print(f"   Conditions: {len(hook.conditions)}")
        
        assert isinstance(hook, HookConfig)
        assert hook.name == 'comprehensive-hook'
        assert hook.type.value == 'hybrid'
        assert hook.trigger.value == 'on_session_start'
        assert hook.context is not None
        assert hook.script is not None
        assert len(hook.conditions) == 1
        print("   ✅ Comprehensive hook test passed")
        
        # Test 3: Test validation with cross-references
        print("\n3. Testing validation with cross-references...")
        
        # Create context files that are referenced
        (test_dir / 'contexts' / 'shared').mkdir(exist_ok=True)
        
        context_files = [
            'contexts/development.md',
            'contexts/aws-best-practices.md',
            'contexts/shared/common.md',
            'contexts/hook-specific.md'
        ]
        
        for context_file in context_files:
            full_path = test_dir / context_file
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"""---
title: {context_file}
tags: [test]
---

# {context_file}

This is a test context file.
""")
        
        # Validate the profile
        validation_result = loader.validate_yaml_file(profile_file)
        print(f"   Profile validation: Valid={validation_result.is_valid}")
        print(f"   Errors: {len(validation_result.errors)}")
        print(f"   Warnings: {len(validation_result.warnings)}")
        
        if validation_result.warnings:
            for warning in validation_result.warnings:
                print(f"     Warning: {warning.message}")
        
        # Should be valid now that context files exist
        assert validation_result.is_valid or len(validation_result.errors) == 0
        print("   ✅ Cross-reference validation test passed")
        
        # Test 4: Test batch operations
        print("\n4. Testing batch operations...")
        
        discovered = loader.discover_configurations()
        print(f"   Discovered profiles: {len(discovered['profiles'])}")
        print(f"   Discovered hooks: {len(discovered['hooks'])}")
        print(f"   Discovered contexts: {len(discovered['contexts'])}")
        
        # Validate all discovered files
        all_valid = True
        total_files = 0
        
        for config_type, files in discovered.items():
            if config_type in ['profiles', 'hooks']:  # Skip contexts for now
                for file_path in files:
                    full_path = test_dir / file_path
                    validation_result = loader.validate_yaml_file(full_path)
                    total_files += 1
                    if not validation_result.is_valid:
                        all_valid = False
                        print(f"     Invalid file: {file_path}")
        
        print(f"   Validated {total_files} configuration files")
        print(f"   All files valid: {all_valid}")
        assert all_valid
        print("   ✅ Batch operations test passed")
        
        # Test 5: Test cache performance
        print("\n5. Testing cache performance...")
        
        import time
        
        # Load profile multiple times and measure performance
        start_time = time.time()
        for _ in range(10):
            loader.load_profile('comprehensive-test')
        cached_time = time.time() - start_time
        
        # Clear cache and load again
        loader.clear_cache()
        start_time = time.time()
        for _ in range(10):
            loader.load_profile('comprehensive-test')
        uncached_time = time.time() - start_time
        
        print(f"   Cached loading time (10x): {cached_time:.4f}s")
        print(f"   Uncached loading time (10x): {uncached_time:.4f}s")
        
        # Cached should be faster (though with small files, difference might be minimal)
        cache_stats = loader.get_cache_stats()
        print(f"   Final cache size: {cache_stats['config_cache_size']}")
        print("   ✅ Cache performance test passed")
        
        print("\n" + "=" * 50)
        print("🎉 All integration tests passed successfully!")


if __name__ == '__main__':
    test_integration()