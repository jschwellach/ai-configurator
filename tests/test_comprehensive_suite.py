#!/usr/bin/env python3
"""Comprehensive test suite runner for AI Configurator."""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def run_comprehensive_tests():
    """Run the complete comprehensive test suite."""
    
    print("🧪 Running Comprehensive Test Suite for AI Configurator")
    print("=" * 70)
    
    # Test configuration
    test_args = [
        # Test directories
        'tests/unit/',
        'tests/integration/',
        
        # Output options
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        
        # Coverage options (if coverage is installed)
        '--cov=src/ai_configurator',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        
        # Test discovery
        '--collect-only',  # First, just collect tests to verify structure
    ]
    
    print("\n📋 Test Discovery Phase")
    print("-" * 30)
    
    # First run: collect tests only
    collection_result = pytest.main([
        'tests/',
        '--collect-only',
        '-q'
    ])
    
    if collection_result != 0:
        print("❌ Test collection failed!")
        return False
    
    print("✅ Test collection successful")
    
    print("\n🏃 Test Execution Phase")
    print("-" * 30)
    
    # Second run: execute tests
    execution_args = [
        'tests/',
        '-v',
        '--tb=short',
        '--strict-markers'
    ]
    
    # Add coverage if available
    try:
        import coverage
        execution_args.extend([
            '--cov=src/ai_configurator',
            '--cov-report=term-missing'
        ])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("⚠️  Coverage not available, skipping coverage report")
    
    execution_result = pytest.main(execution_args)
    
    print("\n" + "=" * 70)
    
    if execution_result == 0:
        print("🎉 All tests passed successfully!")
        print("\n📊 Test Summary:")
        print("   ✅ Unit tests: PASSED")
        print("   ✅ Integration tests: PASSED") 
        print("   ✅ YAML loading tests: PASSED")
        print("   ✅ Validation tests: PASSED")
        print("   ✅ Error handling tests: PASSED")
        return True
    else:
        print("❌ Some tests failed!")
        print(f"   Exit code: {execution_result}")
        return False


def run_specific_test_category(category):
    """Run tests for a specific category."""
    
    category_map = {
        'unit': 'tests/unit/',
        'integration': 'tests/integration/',
        'yaml': 'tests/unit/test_yaml_loader.py',
        'validation': 'tests/unit/test_validator.py',
        'profile': 'tests/integration/test_profile_loading_workflow.py',
        'hook': 'tests/integration/test_hook_loading_workflow.py'
    }
    
    if category not in category_map:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(category_map.keys())}")
        return False
    
    test_path = category_map[category]
    
    print(f"🧪 Running {category.upper()} tests")
    print("=" * 50)
    
    result = pytest.main([
        test_path,
        '-v',
        '--tb=short'
    ])
    
    if result == 0:
        print(f"✅ {category.upper()} tests passed!")
    else:
        print(f"❌ {category.upper()} tests failed!")
    
    return result == 0


def validate_test_environment():
    """Validate that the test environment is properly set up."""
    
    print("🔍 Validating Test Environment")
    print("-" * 40)
    
    # Check required directories
    required_dirs = [
        'src/ai_configurator',
        'tests/unit',
        'tests/integration',
        'tests/fixtures'
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Found directory: {dir_path}")
    
    # Check required modules
    required_modules = [
        'ai_configurator.core.yaml_loader',
        'ai_configurator.core.validator',
        'ai_configurator.core.models'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ Module importable: {module}")
        except ImportError as e:
            print(f"❌ Cannot import module {module}: {e}")
            return False
    
    # Check test fixtures
    fixture_files = [
        'tests/fixtures/profiles/valid/developer.yaml',
        'tests/fixtures/hooks/valid/setup-dev-env.yaml',
        'tests/fixtures/contexts/development-guidelines.md'
    ]
    
    for fixture in fixture_files:
        if not Path(fixture).exists():
            print(f"❌ Missing test fixture: {fixture}")
            return False
        print(f"✅ Found test fixture: {fixture}")
    
    print("\n✅ Test environment validation passed!")
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AI Configurator test suite')
    parser.add_argument(
        '--category', 
        choices=['unit', 'integration', 'yaml', 'validation', 'profile', 'hook'],
        help='Run specific test category'
    )
    parser.add_argument(
        '--validate-env',
        action='store_true',
        help='Validate test environment setup'
    )
    
    args = parser.parse_args()
    
    if args.validate_env:
        success = validate_test_environment()
        sys.exit(0 if success else 1)
    
    if args.category:
        success = run_specific_test_category(args.category)
        sys.exit(0 if success else 1)
    
    # Run comprehensive tests
    if not validate_test_environment():
        print("❌ Test environment validation failed!")
        sys.exit(1)
    
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)