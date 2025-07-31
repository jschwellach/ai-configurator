#!/usr/bin/env python3
"""
Simple test script to verify AI Configurator installation.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_cli_import():
    """Test that the CLI can be imported."""
    try:
        import ai_configurator.cli
        print("✅ CLI module import successful")
        return True
    except ImportError as e:
        print(f"❌ CLI module import failed: {e}")
        return False


def test_cli_command():
    """Test that the CLI command works."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ai_configurator.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ CLI command works: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ CLI command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ CLI command error: {e}")
        return False


def test_entry_point():
    """Test that the entry point works."""
    try:
        result = subprocess.run(
            ["ai-config", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Entry point works: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Entry point failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Entry point not found (ai-config command not in PATH)")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Entry point timed out")
        return False
    except Exception as e:
        print(f"❌ Entry point error: {e}")
        return False


def main():
    """Run installation tests."""
    print("🧪 Testing AI Configurator installation...\n")
    
    tests = [
        ("Import test", test_cli_import),
        ("CLI module test", test_cli_command),
        ("Entry point test", test_entry_point),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Configurator is properly installed.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)