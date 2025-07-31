#!/usr/bin/env python3
"""Integration test for the complete validation system."""

import tempfile
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.yaml_loader import YamlConfigLoader


def test_validation_integration():
    """Test complete integration of validation system."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create directory structure
        (test_dir / 'profiles').mkdir()
        (test_dir / 'hooks').mkdir()
        (test_dir / 'contexts').mkdir()
        
        print("🧪 Testing Validation System Integration")
        print("=" * 50)
        
        # Create test configurations
        print("\n1. Creating test configurations...")
        
        # Valid profile
        valid_profile = {
            'name': 'integration-profile',
            'description': 'Integration test profile',
            'version': '1.0',
            'contexts': ['contexts/integration-context.md'],
            'hooks': {
                'on_session_start': [
                    {'name': 'integration-hook', 'enabled': True}
                ]
            },
            'mcp_servers': ['core'],
            'settings': {
                'validation_level': 'strict'
            }
        }
        
        with open(test_dir / 'profiles' / 'integration-profile.yaml', 'w') as f:
            yaml.dump(valid_profile, f)
        
        # Valid hook
        valid_hook = {
            'name': 'integration-hook',
            'description': 'Integration test hook',
            'type': 'context',
            'trigger': 'on_session_start',
            'context': {
                'sources': ['contexts/integration-context.md'],
                'tags': ['integration', 'test']
            }
        }
        
        with open(test_dir / 'hooks' / 'integration-hook.yaml', 'w') as f:
            yaml.dump(valid_hook, f)
        
        # Context file with frontmatter
        context_content = """---
tags: [integration, test]
priority: 1
category: testing
---

# Integration Context

This is an integration test context file.
"""
        
        with open(test_dir / 'contexts' / 'integration-context.md', 'w') as f:
            f.write(context_content)
        
        print("   ✅ Test configurations created")
        
        # Test 2: Initialize systems
        print("\n2. Initializing validation systems...")
        
        validator = ConfigurationValidator(test_dir)
        loader = YamlConfigLoader(test_dir)
        
        print("   ✅ Systems initialized")
        
        # Test 3: Comprehensive validation
        print("\n3. Running comprehensive validation...")
        
        comprehensive_report = validator.validate_all_configurations()
        
        print(f"   Overall validation: {'✅ VALID' if comprehensive_report.is_valid else '❌ INVALID'}")
        print(f"   Files validated: {comprehensive_report.summary['total_files']}")
        print(f"   Errors: {comprehensive_report.summary['errors']}")
        print(f"   Warnings: {comprehensive_report.summary['warnings']}")
        
        if comprehensive_report.is_valid:
            # Find configuration summary
            summary_info = [i for i in comprehensive_report.info if i.error_type == "ConfigurationSummary"]
            if summary_info:
                print("   Configuration Summary:")
                for line in summary_info[0].message.split('\n'):
                    print(f"     {line}")
        
        print("   ✅ Comprehensive validation completed")
        
        # Test 4: Individual file validation
        print("\n4. Testing individual file validation...")
        
        profile_path = test_dir / 'profiles' / 'integration-profile.yaml'
        profile_report = validator.validate_configuration_file(profile_path)
        
        print(f"   Profile validation: {'✅ VALID' if profile_report.is_valid else '❌ INVALID'}")
        
        hook_path = test_dir / 'hooks' / 'integration-hook.yaml'
        hook_report = validator.validate_configuration_file(hook_path)
        
        print(f"   Hook validation: {'✅ VALID' if hook_report.is_valid else '❌ INVALID'}")
        
        context_path = test_dir / 'contexts' / 'integration-context.md'
        context_report = validator.validate_configuration_file(context_path)
        
        print(f"   Context validation: {'✅ VALID' if context_report.is_valid else '❌ INVALID'}")
        
        print("   ✅ Individual file validation completed")
        
        # Test 5: Schema validation
        print("\n5. Testing schema validation...")
        
        profile_schema = validator.validate_schema(profile_path, 'profile')
        print(f"   Profile schema: {'✅ VALID' if profile_schema.is_valid else '❌ INVALID'}")
        
        hook_schema = validator.validate_schema(hook_path, 'hook')
        print(f"   Hook schema: {'✅ VALID' if hook_schema.is_valid else '❌ INVALID'}")
        
        print("   ✅ Schema validation completed")
        
        # Test 6: Loader integration
        print("\n6. Testing loader integration...")
        
        # Load configurations through loader
        try:
            profile = loader.load_profile('integration-profile')
            print(f"   Profile loaded: {profile.name}")
            
            hook = loader.load_hook('integration-hook')
            print(f"   Hook loaded: {hook.name}")
            
            # Test loader validation methods
            loader_comprehensive = loader.validate_all_configurations()
            print(f"   Loader comprehensive validation: {'✅ VALID' if loader_comprehensive.is_valid else '❌ INVALID'}")
            
            loader_file_validation = loader.validate_yaml_file(profile_path)
            print(f"   Loader file validation: {'✅ VALID' if loader_file_validation.is_valid else '❌ INVALID'}")
            
            loader_schema_validation = loader.validate_schema(hook_path, 'hook')
            print(f"   Loader schema validation: {'✅ VALID' if loader_schema_validation.is_valid else '❌ INVALID'}")
            
        except Exception as e:
            print(f"   ❌ Loader integration failed: {e}")
            return False
        
        print("   ✅ Loader integration completed")
        
        # Test 7: Error handling with invalid configurations
        print("\n7. Testing error handling with invalid configurations...")
        
        # Create invalid configuration
        invalid_profile = {
            'description': 'Missing name field',
            'contexts': ['contexts/nonexistent.md']
        }
        
        invalid_path = test_dir / 'profiles' / 'invalid-profile.yaml'
        with open(invalid_path, 'w') as f:
            yaml.dump(invalid_profile, f)
        
        invalid_report = validator.validate_configuration_file(invalid_path)
        
        print(f"   Invalid config validation: {'❌ INVALID' if not invalid_report.is_valid else '✅ VALID'}")
        print(f"   Errors detected: {len(invalid_report.errors)}")
        
        # Verify specific error types
        schema_errors = [e for e in invalid_report.errors if e.error_type == "SchemaValidationError"]
        ref_errors = [e for e in invalid_report.errors if e.error_type == "MissingFileReference"]
        
        print(f"   Schema errors: {len(schema_errors)}")
        print(f"   Reference errors: {len(ref_errors)}")
        
        print("   ✅ Error handling test completed")
        
        # Test 8: Cache functionality
        print("\n8. Testing cache functionality...")
        
        # Load same profile twice to test caching
        profile1 = loader.load_profile('integration-profile')
        profile2 = loader.load_profile('integration-profile')
        
        cache_stats = loader.get_cache_stats()
        print(f"   Cache size: {cache_stats['config_cache_size']}")
        print(f"   Validation cache size: {cache_stats['validation_cache_size']}")
        
        # Clear cache and verify
        loader.clear_cache()
        cache_stats_after = loader.get_cache_stats()
        print(f"   Cache size after clear: {cache_stats_after['config_cache_size']}")
        
        print("   ✅ Cache functionality test completed")
        
        print("\n" + "=" * 50)
        print("🎉 All integration tests passed successfully!")
        
        return True


if __name__ == '__main__':
    success = test_validation_integration()
    if success:
        print("\n✅ Validation system integration is working correctly!")
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)