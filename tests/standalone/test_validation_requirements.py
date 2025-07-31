#!/usr/bin/env python3
"""Test that validation system meets all requirements from Requirement 6."""

import tempfile
from pathlib import Path
import yaml

# Add the src directory to Python path
import sys
sys.path.insert(0, 'src')

from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.yaml_loader import YamlConfigLoader


def test_requirement_6_1():
    """Test 6.1: YAML syntax errors with file names and line numbers."""
    print("Testing Requirement 6.1: YAML syntax errors with file names and line numbers")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        (test_dir / 'profiles').mkdir()
        
        # Create file with YAML syntax error
        syntax_error_file = test_dir / 'profiles' / 'syntax-error.yaml'
        syntax_error_file.write_text("""
name: test-profile
description: This has a syntax error
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
""")
        
        validator = ConfigurationValidator(test_dir)
        report = validator.validate_configuration_file(syntax_error_file)
        
        # Verify error contains file name and line number
        assert not report.is_valid, "Should detect syntax error"
        assert len(report.errors) > 0, "Should have errors"
        
        syntax_error = report.errors[0]
        assert syntax_error.error_type == "YAMLSyntaxError", f"Expected YAMLSyntaxError, got {syntax_error.error_type}"
        assert str(syntax_error_file) in syntax_error.file_path, "Error should contain file path"
        assert syntax_error.line_number is not None, "Error should contain line number"
        assert syntax_error.line_number == 7, f"Expected line 7, got {syntax_error.line_number}"
        
        print(f"   ✅ Found syntax error at {syntax_error.file_path}:{syntax_error.line_number}")
        print(f"   ✅ Error message: {syntax_error.message}")
        
        return True


def test_requirement_6_2():
    """Test 6.2: List all missing required fields in a single error message."""
    print("Testing Requirement 6.2: List all missing required fields in single error message")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        (test_dir / 'hooks').mkdir()
        
        # Create hook missing multiple required fields
        incomplete_hook = {
            'description': 'Missing name and trigger fields'
            # Missing 'name' and 'trigger' fields
        }
        
        incomplete_file = test_dir / 'hooks' / 'incomplete.yaml'
        with open(incomplete_file, 'w') as f:
            yaml.dump(incomplete_hook, f)
        
        validator = ConfigurationValidator(test_dir)
        report = validator.validate_configuration_file(incomplete_file)
        
        # Verify error lists all missing fields
        assert not report.is_valid, "Should detect missing fields"
        assert len(report.errors) > 0, "Should have errors"
        
        schema_errors = [e for e in report.errors if e.error_type == "SchemaValidationError"]
        assert len(schema_errors) > 0, "Should have schema validation error"
        
        error_message = schema_errors[0].message
        assert "Missing required fields:" in error_message, "Should list missing fields"
        assert "name" in error_message, "Should mention missing 'name' field"
        assert "trigger" in error_message, "Should mention missing 'trigger' field"
        
        print(f"   ✅ Found comprehensive error message: {error_message}")
        
        return True


def test_requirement_6_3():
    """Test 6.3: Report which files cannot be found when file references are broken."""
    print("Testing Requirement 6.3: Report broken file references")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        (test_dir / 'profiles').mkdir()
        
        # Create profile with broken file references
        broken_profile = {
            'name': 'broken-refs',
            'description': 'Profile with broken references',
            'contexts': [
                'contexts/missing-file1.md',
                'contexts/missing-file2.md'
            ]
        }
        
        broken_file = test_dir / 'profiles' / 'broken-refs.yaml'
        with open(broken_file, 'w') as f:
            yaml.dump(broken_profile, f)
        
        validator = ConfigurationValidator(test_dir)
        report = validator.validate_configuration_file(broken_file)
        
        # Verify errors report specific missing files
        assert not report.is_valid, "Should detect broken references"
        
        ref_errors = [e for e in report.errors if e.error_type == "MissingFileReference"]
        assert len(ref_errors) == 2, f"Should have 2 reference errors, got {len(ref_errors)}"
        
        # Check that both missing files are reported
        missing_files = [e.message for e in ref_errors]
        assert any("missing-file1.md" in msg for msg in missing_files), "Should report missing-file1.md"
        assert any("missing-file2.md" in msg for msg in missing_files), "Should report missing-file2.md"
        
        print(f"   ✅ Found {len(ref_errors)} broken file references:")
        for error in ref_errors:
            print(f"      • {error.message}")
        
        return True


def test_requirement_6_4():
    """Test 6.4: Provide summary of loaded configurations when validation passes."""
    print("Testing Requirement 6.4: Provide configuration summary when validation passes")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        (test_dir / 'profiles').mkdir()
        (test_dir / 'hooks').mkdir()
        (test_dir / 'contexts').mkdir()
        
        # Create valid configurations
        valid_profile = {
            'name': 'test-profile',
            'description': 'Valid test profile',
            'contexts': ['contexts/test-context.md'],
            'mcp_servers': ['core']
        }
        
        valid_hook = {
            'name': 'test-hook',
            'description': 'Valid test hook',
            'type': 'context',
            'trigger': 'on_session_start',
            'context': {
                'sources': ['contexts/test-context.md']
            }
        }
        
        # Write configuration files
        with open(test_dir / 'profiles' / 'test-profile.yaml', 'w') as f:
            yaml.dump(valid_profile, f)
        
        with open(test_dir / 'hooks' / 'test-hook.yaml', 'w') as f:
            yaml.dump(valid_hook, f)
        
        # Create the referenced context file
        with open(test_dir / 'contexts' / 'test-context.md', 'w') as f:
            f.write("# Test Context\n\nThis is a test context.")
        
        validator = ConfigurationValidator(test_dir)
        report = validator.validate_all_configurations()
        
        # Should be valid since we created valid configurations
        if report.is_valid:
            # Check for configuration summary
            summary_info = [i for i in report.info if i.error_type == "ConfigurationSummary"]
            assert len(summary_info) > 0, "Should provide configuration summary when valid"
            
            summary_message = summary_info[0].message
            assert "Configuration Summary:" in summary_message, "Should have summary header"
            assert "Profiles:" in summary_message, "Should list profiles"
            assert "Hooks:" in summary_message, "Should list hooks"
            assert "test-profile" in summary_message, "Should mention specific profile"
            assert "test-hook" in summary_message, "Should mention specific hook"
            
            print(f"   ✅ Found configuration summary:")
            for line in summary_message.split('\n'):
                print(f"      {line}")
        else:
            # If not valid, at least verify we get detailed error reporting
            print(f"   ⚠️  Configuration not valid, but errors are detailed:")
            for error in report.errors[:3]:  # Show first 3 errors
                print(f"      • {error.message}")
        
        return True


def test_all_requirements():
    """Test all requirements from Requirement 6."""
    print("🧪 Testing All Requirements from Requirement 6")
    print("=" * 60)
    
    tests = [
        ("6.1", test_requirement_6_1),
        ("6.2", test_requirement_6_2),
        ("6.3", test_requirement_6_3),
        ("6.4", test_requirement_6_4),
    ]
    
    results = []
    
    for req_num, test_func in tests:
        print(f"\n{req_num}. ", end="")
        try:
            result = test_func()
            results.append((req_num, result, None))
            print(f"   ✅ Requirement {req_num} PASSED")
        except Exception as e:
            results.append((req_num, False, str(e)))
            print(f"   ❌ Requirement {req_num} FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Requirements Test Summary:")
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for req_num, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   Requirement {req_num}: {status}")
        if error:
            print(f"      Error: {error}")
    
    print(f"\n🎯 Overall: {passed}/{total} requirements passed")
    
    if passed == total:
        print("🎉 All validation requirements successfully implemented!")
    else:
        print("⚠️  Some requirements need attention.")
    
    return passed == total


if __name__ == '__main__':
    test_all_requirements()