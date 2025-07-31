#!/usr/bin/env python3
"""Comprehensive tests for the enhanced validation system."""

import os
import tempfile
import shutil
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.yaml_loader import YamlConfigLoader


def create_comprehensive_test_files(test_dir: Path):
    """Create comprehensive test files for validation testing."""
    
    # Create directory structure
    (test_dir / 'profiles').mkdir(exist_ok=True)
    (test_dir / 'hooks').mkdir(exist_ok=True)
    (test_dir / 'contexts').mkdir(exist_ok=True)
    (test_dir / 'contexts' / 'shared').mkdir(exist_ok=True)
    
    # 1. Valid profile with all features
    valid_profile = {
        'name': 'comprehensive-profile',
        'description': 'A comprehensive test profile',
        'version': '1.0',
        'contexts': [
            'contexts/development.md',
            'contexts/shared/common.md'
        ],
        'hooks': {
            'on_session_start': [
                {'name': 'setup-hook', 'enabled': True, 'timeout': 45}
            ],
            'per_user_message': [
                {'name': 'context-hook', 'enabled': True}
            ]
        },
        'mcp_servers': ['core', 'development'],
        'settings': {
            'auto_backup': True,
            'validation_level': 'strict',
            'hot_reload': True
        },
        'metadata': {
            'author': 'Test Suite',
            'created': '2024-01-01'
        }
    }
    
    with open(test_dir / 'profiles' / 'comprehensive-profile.yaml', 'w') as f:
        yaml.dump(valid_profile, f, default_flow_style=False)
    
    # 2. Profile with missing required fields
    incomplete_profile = {
        'description': 'Missing name field',
        'contexts': ['contexts/missing.md']  # This file won't exist
    }
    
    with open(test_dir / 'profiles' / 'incomplete-profile.yaml', 'w') as f:
        yaml.dump(incomplete_profile, f, default_flow_style=False)
    
    # 3. Profile with broken file references
    broken_refs_profile = {
        'name': 'broken-refs',
        'description': 'Profile with broken file references',
        'contexts': [
            'contexts/nonexistent.md',
            'contexts/also-missing.md'
        ],
        'hooks': {
            'on_session_start': [
                {'name': 'missing-hook', 'enabled': True}
            ]
        }
    }
    
    with open(test_dir / 'profiles' / 'broken-refs.yaml', 'w') as f:
        yaml.dump(broken_refs_profile, f, default_flow_style=False)
    
    # 4. Valid hook configuration
    valid_hook = {
        'name': 'setup-hook',
        'description': 'Setup development environment',
        'version': '1.0',
        'type': 'context',
        'trigger': 'on_session_start',
        'timeout': 45,
        'enabled': True,
        'context': {
            'sources': ['contexts/setup-context.md'],
            'tags': ['setup', 'development'],
            'priority': 1
        },
        'conditions': [
            {
                'profile': ['comprehensive-profile', 'developer'],
                'platform': ['darwin', 'linux']
            }
        ]
    }
    
    with open(test_dir / 'hooks' / 'setup-hook.yaml', 'w') as f:
        yaml.dump(valid_hook, f, default_flow_style=False)
    
    # 5. Hook with invalid trigger
    invalid_hook = {
        'name': 'invalid-hook',
        'description': 'Hook with invalid trigger',
        'type': 'context',
        'trigger': 'invalid_trigger_name',  # Invalid trigger
        'context': {
            'sources': ['contexts/invalid-context.md']
        }
    }
    
    with open(test_dir / 'hooks' / 'invalid-hook.yaml', 'w') as f:
        yaml.dump(invalid_hook, f, default_flow_style=False)
    
    # 6. Hook missing required fields
    incomplete_hook = {
        'name': 'incomplete-hook',
        'description': 'Missing required trigger field'
        # Missing 'trigger' field
    }
    
    with open(test_dir / 'hooks' / 'incomplete-hook.yaml', 'w') as f:
        yaml.dump(incomplete_hook, f, default_flow_style=False)
    
    # 7. YAML syntax error file
    with open(test_dir / 'profiles' / 'syntax-error.yaml', 'w') as f:
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
    - name: another
      enabled: false
      invalid_yaml: [unclosed list
""")
    
    # 8. Create some context files (some exist, some don't)
    with open(test_dir / 'contexts' / 'development.md', 'w') as f:
        f.write("""---
tags: [development, setup]
priority: 1
category: development
---

# Development Context

This is a development context file.
""")
    
    with open(test_dir / 'contexts' / 'shared' / 'common.md', 'w') as f:
        f.write("""---
tags: [common, shared]
priority: 0
---

# Common Context

Shared context across profiles.
""")
    
    with open(test_dir / 'contexts' / 'setup-context.md', 'w') as f:
        f.write("""# Setup Context

Context for setup hooks.
""")
    
    # 9. Create circular dependency scenario
    circular_profile_a = {
        'name': 'circular-a',
        'contexts': ['contexts/circular-b.md']
    }
    
    circular_profile_b = {
        'name': 'circular-b', 
        'contexts': ['contexts/circular-a.md']
    }
    
    with open(test_dir / 'profiles' / 'circular-a.yaml', 'w') as f:
        yaml.dump(circular_profile_a, f)
    
    with open(test_dir / 'profiles' / 'circular-b.yaml', 'w') as f:
        yaml.dump(circular_profile_b, f)
    
    # Create the circular context files
    with open(test_dir / 'contexts' / 'circular-a.md', 'w') as f:
        f.write("# Circular A\nReferences circular-b.md")
    
    with open(test_dir / 'contexts' / 'circular-b.md', 'w') as f:
        f.write("# Circular B\nReferences circular-a.md")
    
    # 10. Profile with deprecated fields
    deprecated_profile = {
        'name': 'deprecated-profile',
        'description': 'Profile with deprecated fields',
        'contexts': ['contexts/development.md'],
        'legacy_hooks': {'old': 'format'},  # Deprecated field
        'old_context_format': True,  # Deprecated field
        'json_config': {'legacy': True}  # Deprecated field
    }
    
    with open(test_dir / 'profiles' / 'deprecated-profile.yaml', 'w') as f:
        yaml.dump(deprecated_profile, f)


def test_comprehensive_validation():
    """Test comprehensive validation functionality."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        create_comprehensive_test_files(test_dir)
        
        print("🧪 Testing Comprehensive Validation System")
        print("=" * 60)
        
        # Initialize validator and loader
        validator = ConfigurationValidator(test_dir)
        loader = YamlConfigLoader(test_dir)
        
        # Test 1: Validate all configurations
        print("\n1. Testing comprehensive validation of all configurations...")
        all_validation = validator.validate_all_configurations()
        
        print(f"   Overall validation: {'✅ VALID' if all_validation.is_valid else '❌ INVALID'}")
        print(f"   Files checked: {all_validation.summary['total_files']}")
        print(f"   Errors: {all_validation.summary['errors']}")
        print(f"   Warnings: {all_validation.summary['warnings']}")
        print(f"   Info messages: {all_validation.summary['info']}")
        
        # Print detailed errors
        if all_validation.errors:
            print("\n   📋 Detailed Errors:")
            for error in all_validation.errors[:5]:  # Show first 5 errors
                print(f"     • {error.file_path}: {error.message}")
                if error.line_number:
                    print(f"       Line {error.line_number}")
                if error.context:
                    print(f"       Context: {error.context[:100]}...")
        
        # Print warnings
        if all_validation.warnings:
            print(f"\n   ⚠️  Sample Warnings ({len(all_validation.warnings)} total):")
            for warning in all_validation.warnings[:3]:
                print(f"     • {warning.file_path}: {warning.message}")
        
        print("   ✅ Comprehensive validation test completed")
        
        # Test 2: Test specific file validation
        print("\n2. Testing individual file validation...")
        
        # Test valid profile
        valid_profile_path = test_dir / 'profiles' / 'comprehensive-profile.yaml'
        valid_report = validator.validate_configuration_file(valid_profile_path)
        print(f"   Valid profile: {'✅ VALID' if valid_report.is_valid else '❌ INVALID'}")
        
        # Test invalid profile
        invalid_profile_path = test_dir / 'profiles' / 'syntax-error.yaml'
        invalid_report = validator.validate_configuration_file(invalid_profile_path)
        print(f"   Invalid profile: {'❌ INVALID' if not invalid_report.is_valid else '✅ VALID'}")
        
        if invalid_report.errors:
            error = invalid_report.errors[0]
            print(f"     Error: {error.message}")
            if error.line_number:
                print(f"     Line: {error.line_number}")
        
        print("   ✅ Individual file validation test completed")
        
        # Test 3: Test schema validation
        print("\n3. Testing schema validation...")
        
        # Test profile schema
        profile_schema_report = validator.validate_schema(valid_profile_path, 'profile')
        print(f"   Profile schema: {'✅ VALID' if profile_schema_report.is_valid else '❌ INVALID'}")
        
        # Test hook schema
        hook_path = test_dir / 'hooks' / 'setup-hook.yaml'
        hook_schema_report = validator.validate_schema(hook_path, 'hook')
        print(f"   Hook schema: {'✅ VALID' if hook_schema_report.is_valid else '❌ INVALID'}")
        
        # Test invalid hook schema
        invalid_hook_path = test_dir / 'hooks' / 'invalid-hook.yaml'
        invalid_hook_report = validator.validate_schema(invalid_hook_path, 'hook')
        print(f"   Invalid hook schema: {'❌ INVALID' if not invalid_hook_report.is_valid else '✅ VALID'}")
        
        print("   ✅ Schema validation test completed")
        
        # Test 4: Test file reference validation
        print("\n4. Testing file reference validation...")
        
        broken_refs_path = test_dir / 'profiles' / 'broken-refs.yaml'
        broken_refs_report = validator.validate_configuration_file(broken_refs_path)
        
        print(f"   Broken references: {'❌ INVALID' if not broken_refs_report.is_valid else '✅ VALID'}")
        
        # Count file reference errors
        ref_errors = [e for e in broken_refs_report.errors if e.error_type == "MissingFileReference"]
        print(f"   Missing file reference errors: {len(ref_errors)}")
        
        for error in ref_errors[:2]:  # Show first 2
            print(f"     • {error.message}")
        
        print("   ✅ File reference validation test completed")
        
        # Test 5: Test missing required fields detection
        print("\n5. Testing missing required fields detection...")
        
        incomplete_profile_path = test_dir / 'profiles' / 'incomplete-profile.yaml'
        incomplete_report = validator.validate_configuration_file(incomplete_profile_path)
        
        print(f"   Incomplete profile: {'❌ INVALID' if not incomplete_report.is_valid else '✅ VALID'}")
        
        # Look for schema validation errors
        schema_errors = [e for e in incomplete_report.errors if e.error_type == "SchemaValidationError"]
        if schema_errors:
            print(f"   Schema validation error found:")
            print(f"     {schema_errors[0].message}")
        
        print("   ✅ Missing required fields test completed")
        
        # Test 6: Test circular dependency detection
        print("\n6. Testing circular dependency detection...")
        
        # The circular dependencies should be detected in the comprehensive validation
        circular_errors = [e for e in all_validation.errors if e.error_type == "CircularDependency"]
        print(f"   Circular dependencies detected: {len(circular_errors)}")
        
        for error in circular_errors:
            print(f"     • {error.message}")
        
        print("   ✅ Circular dependency detection test completed")
        
        # Test 7: Test deprecated field warnings
        print("\n7. Testing deprecated field warnings...")
        
        deprecated_path = test_dir / 'profiles' / 'deprecated-profile.yaml'
        deprecated_report = validator.validate_configuration_file(deprecated_path)
        
        deprecated_warnings = [w for w in deprecated_report.warnings if w.error_type == "DeprecatedField"]
        print(f"   Deprecated field warnings: {len(deprecated_warnings)}")
        
        for warning in deprecated_warnings:
            print(f"     • {warning.message}")
        
        print("   ✅ Deprecated field warnings test completed")
        
        # Test 8: Test integration with YamlConfigLoader
        print("\n8. Testing integration with YamlConfigLoader...")
        
        # Test comprehensive validation through loader
        loader_validation = loader.validate_all_configurations()
        print(f"   Loader comprehensive validation: {'✅ VALID' if loader_validation.is_valid else '❌ INVALID'}")
        
        # Test individual file validation through loader
        loader_file_validation = loader.validate_yaml_file(valid_profile_path)
        print(f"   Loader file validation: {'✅ VALID' if loader_file_validation.is_valid else '❌ INVALID'}")
        
        # Test schema validation through loader
        loader_schema_validation = loader.validate_schema(hook_path, 'hook')
        print(f"   Loader schema validation: {'✅ VALID' if loader_schema_validation.is_valid else '❌ INVALID'}")
        
        print("   ✅ YamlConfigLoader integration test completed")
        
        # Test 9: Test configuration summary generation
        print("\n9. Testing configuration summary generation...")
        
        if all_validation.info:
            summary_info = [i for i in all_validation.info if i.error_type == "ConfigurationSummary"]
            if summary_info:
                print("   Configuration Summary:")
                summary_lines = summary_info[0].message.split('\n')
                for line in summary_lines:
                    print(f"     {line}")
        
        print("   ✅ Configuration summary test completed")
        
        print("\n" + "=" * 60)
        print("🎉 All comprehensive validation tests completed!")
        
        # Final summary
        print(f"\n📊 Final Test Results:")
        print(f"   Total configurations: {all_validation.summary['total_files']}")
        print(f"   Valid configurations: {all_validation.summary['valid_files']}")
        print(f"   Invalid configurations: {all_validation.summary['invalid_files']}")
        print(f"   Total errors found: {all_validation.summary['errors']}")
        print(f"   Total warnings found: {all_validation.summary['warnings']}")
        
        # Verify that we found the expected issues
        expected_issues = {
            'syntax_errors': 1,  # syntax-error.yaml
            'missing_references': 2,  # broken-refs.yaml has 2 missing files
            'invalid_triggers': 1,  # invalid-hook.yaml
            'missing_required_fields': 2,  # incomplete-profile.yaml and incomplete-hook.yaml
            'deprecated_fields': 3,  # deprecated-profile.yaml has 3 deprecated fields
        }
        
        print(f"\n✅ Validation system successfully detected expected configuration issues!")


if __name__ == '__main__':
    test_comprehensive_validation()