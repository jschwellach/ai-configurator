#!/usr/bin/env python3
"""Test script to verify template infrastructure implementation."""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_configurator.core.template_models import (
    TemplateMetadata, TemplateCategory, TemplateComplexity, TemplateType,
    ProfileTemplate, ContextTemplate, HookTemplate, TemplateRegistry, TemplateInfo
)
from ai_configurator.core.template_validator import TemplateValidator, ValidationResult


def test_directory_structure():
    """Test that directory structure was created correctly."""
    print("Testing directory structure...")
    
    required_dirs = [
        "examples/profiles/basic",
        "examples/profiles/professional", 
        "examples/contexts/domains",
        "examples/contexts/workflows",
        "examples/hooks/automation",
        "examples/workflows"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Directory exists: {dir_path}")
    
    return True


def test_template_metadata():
    """Test template metadata creation and validation."""
    print("\nTesting template metadata...")
    
    # Create sample metadata
    metadata = TemplateMetadata(
        name="test-template",
        description="A test template for validation",
        category=TemplateCategory.BASIC,
        version="1.0.0",
        author="Test Author",
        tags=["test", "example"],
        complexity=TemplateComplexity.LOW
    )
    
    # Test conversion to dict
    metadata_dict = metadata.to_dict()
    expected_keys = ["name", "description", "category", "version", "author", "tags", "complexity"]
    
    for key in expected_keys:
        if key not in metadata_dict:
            print(f"❌ Missing key in metadata dict: {key}")
            return False
    
    # Test conversion from dict
    metadata_from_dict = TemplateMetadata.from_dict(metadata_dict)
    if metadata_from_dict.name != metadata.name:
        print("❌ Metadata from_dict conversion failed")
        return False
        
    print("✅ Template metadata working correctly")
    return True


def test_template_validator():
    """Test template validator functionality."""
    print("\nTesting template validator...")
    
    validator = TemplateValidator()
    
    # Test valid metadata
    valid_metadata = {
        "name": "test-template",
        "description": "A test template for validation purposes",
        "category": "basic",
        "version": "1.0.0"
    }
    
    result = validator.validate_metadata(valid_metadata)
    if not result.is_valid:
        print(f"❌ Valid metadata failed validation: {result.errors}")
        return False
    
    # Test invalid metadata
    invalid_metadata = {
        "name": "Test Template!",  # Invalid characters
        "description": "Short",    # Too short
        "category": "invalid",     # Invalid category
        "version": "1.0"          # Invalid version format
    }
    
    result = validator.validate_metadata(invalid_metadata)
    if result.is_valid:
        print("❌ Invalid metadata passed validation")
        return False
        
    print("✅ Template validator working correctly")
    return True


def test_profile_template():
    """Test profile template functionality."""
    print("\nTesting profile template...")
    
    metadata = TemplateMetadata(
        name="test-profile",
        description="A test profile template",
        category=TemplateCategory.BASIC,
        version="1.0.0"
    )
    
    profile = ProfileTemplate(
        metadata=metadata,
        paths=["contexts/test-context.md"],
        hooks={"test_hook": {"enabled": True}},
        settings={"theme": "dark"}
    )
    
    # Test template type
    if profile.template_type != TemplateType.PROFILE:
        print("❌ Profile template type incorrect")
        return False
    
    # Test dictionary conversion
    profile_dict = profile.to_dict()
    required_keys = ["metadata", "paths", "hooks", "settings"]
    
    for key in required_keys:
        if key not in profile_dict:
            print(f"❌ Missing key in profile dict: {key}")
            return False
    
    print("✅ Profile template working correctly")
    return True


def test_template_registry():
    """Test template registry functionality."""
    print("\nTesting template registry...")
    
    registry = TemplateRegistry()
    
    # Create test template info
    metadata = TemplateMetadata(
        name="test-template",
        description="A test template",
        category=TemplateCategory.BASIC,
        version="1.0.0"
    )
    
    # Create dummy file first
    dummy_file = Path("examples/profiles/basic/test.json")
    dummy_file.write_text('{"test": true}')
    
    try:
        template_info = TemplateInfo(
            name="test-template",
            path=dummy_file,
            template_type=TemplateType.PROFILE,
            metadata=metadata
        )
        
        registry.register_template(template_info)
        
        # Test retrieval
        retrieved = registry.get_template("test-template")
        if not retrieved or retrieved.name != "test-template":
            print("❌ Template registry retrieval failed")
            return False
        
        # Test category retrieval
        basic_templates = registry.get_templates_by_category(TemplateCategory.BASIC)
        if len(basic_templates) != 1 or basic_templates[0].name != "test-template":
            print("❌ Template registry category retrieval failed")
            return False
            
        print("✅ Template registry working correctly")
        return True
        
    finally:
        # Clean up dummy file
        if dummy_file.exists():
            dummy_file.unlink()


def main():
    """Run all tests."""
    print("Testing Template Infrastructure Implementation")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_template_metadata,
        test_template_validator,
        test_profile_template,
        test_template_registry
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Template infrastructure is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)