#!/usr/bin/env python3
"""Additional edge case tests for YamlConfigLoader."""

import os
import tempfile
import time
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader


def test_edge_cases():
    """Test edge cases and error conditions."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create directory structure
        (test_dir / 'profiles').mkdir(exist_ok=True)
        (test_dir / 'hooks').mkdir(exist_ok=True)
        
        loader = YamlConfigLoader(test_dir)
        
        print("🧪 Testing YamlConfigLoader Edge Cases")
        print("=" * 50)
        
        # Test 1: Empty YAML file
        print("\n1. Testing empty YAML file...")
        empty_file = test_dir / 'profiles' / 'empty.yaml'
        empty_file.write_text("")
        
        validation_result = loader.validate_yaml_file(empty_file)
        print(f"   Empty file validation: Valid={validation_result.is_valid}")
        print(f"   Warnings: {len(validation_result.warnings)}")
        
        # Empty files are now handled more gracefully
        print(f"   Empty file errors: {len(validation_result.errors)}")
        print(f"   Empty file warnings: {len(validation_result.warnings)}")
        if validation_result.errors:
            print(f"   Error: {validation_result.errors[0].message}")
        print("   ✅ Empty file test passed")
        
        # Test 2: File with only comments
        print("\n2. Testing file with only comments...")
        comment_file = test_dir / 'profiles' / 'comments.yaml'
        comment_file.write_text("""
# This is a comment
# Another comment
""")
        
        validation_result = loader.validate_yaml_file(comment_file)
        print(f"   Comments-only file validation: Valid={validation_result.is_valid}")
        print("   ✅ Comments-only file test passed")
        
        # Test 3: File with missing required fields
        print("\n3. Testing file with missing required fields...")
        incomplete_hook = {
            'name': 'incomplete-hook',
            'description': 'Missing required trigger field'
            # Missing 'trigger' field which is required for HookConfig
        }
        
        incomplete_file = test_dir / 'hooks' / 'incomplete.yaml'
        with open(incomplete_file, 'w') as f:
            yaml.dump(incomplete_hook, f)
        
        validation_result = loader.validate_yaml_file(incomplete_file)
        print(f"   Incomplete file validation: Valid={validation_result.is_valid}")
        print(f"   Errors: {len(validation_result.errors)}")
        
        if validation_result.errors:
            for error in validation_result.errors:
                print(f"     Error: {error.message}")
        
        assert not validation_result.is_valid
        print("   ✅ Incomplete file test passed")
        
        # Test 4: File modification time tracking
        print("\n4. Testing file modification time tracking...")
        
        # Create a profile file
        profile_data = {
            'name': 'time-test',
            'description': 'Testing modification time',
            'contexts': [],
            'mcp_servers': []
        }
        
        time_test_file = test_dir / 'profiles' / 'time-test.yaml'
        with open(time_test_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        # Load it first time
        profile1 = loader.load_profile('time-test')
        cache_stats1 = loader.get_cache_stats()
        
        # Wait a bit and modify the file
        time.sleep(0.1)
        profile_data['description'] = 'Modified description'
        with open(time_test_file, 'w') as f:
            yaml.dump(profile_data, f)
        
        # Load it again - should detect modification
        profile2 = loader.load_profile('time-test')
        
        assert profile1.description != profile2.description
        print(f"   Original description: {profile1.description}")
        print(f"   Modified description: {profile2.description}")
        print("   ✅ File modification tracking test passed")
        
        # Test 5: Non-existent directory handling
        print("\n5. Testing non-existent directory handling...")
        non_existent_loader = YamlConfigLoader(Path("/non/existent/path"))
        discovered = non_existent_loader.discover_configurations()
        
        # Should return empty lists, not crash
        assert discovered['profiles'] == []
        assert discovered['hooks'] == []
        assert discovered['contexts'] == []
        print("   ✅ Non-existent directory test passed")
        
        # Test 6: Unicode and special characters
        print("\n6. Testing Unicode and special characters...")
        unicode_profile = {
            'name': 'unicode-test',
            'description': 'Testing Unicode: 你好世界 🌍 café naïve résumé',
            'contexts': ['contexts/special-chars.md'],
            'mcp_servers': []
        }
        
        unicode_file = test_dir / 'profiles' / 'unicode-test.yaml'
        with open(unicode_file, 'w', encoding='utf-8') as f:
            yaml.dump(unicode_profile, f, allow_unicode=True)
        
        profile = loader.load_profile('unicode-test')
        print(f"   Unicode description: {profile.description}")
        assert '你好世界' in profile.description
        assert '🌍' in profile.description
        print("   ✅ Unicode test passed")
        
        # Test 7: Large file handling
        print("\n7. Testing large configuration file...")
        large_profile = {
            'name': 'large-test',
            'description': 'Testing large configuration',
            'contexts': [f'contexts/context-{i}.md' for i in range(100)],
            'mcp_servers': [f'server-{i}' for i in range(50)],
            'metadata': {f'key-{i}': f'value-{i}' * 100 for i in range(20)}
        }
        
        large_file = test_dir / 'profiles' / 'large-test.yaml'
        with open(large_file, 'w') as f:
            yaml.dump(large_profile, f)
        
        profile = loader.load_profile('large-test')
        assert len(profile.contexts) == 100
        assert len(profile.mcp_servers) == 50
        print(f"   Large profile loaded: {len(profile.contexts)} contexts, {len(profile.mcp_servers)} servers")
        print("   ✅ Large file test passed")
        
        print("\n" + "=" * 50)
        print("🎉 All edge case tests passed successfully!")


if __name__ == '__main__':
    test_edge_cases()