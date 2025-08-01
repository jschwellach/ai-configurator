#!/usr/bin/env python3
"""
Comprehensive test runner for template management system.

This script runs all unit and integration tests for the template components,
providing detailed reporting and performance metrics.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def run_test_suite(test_path: str, description: str) -> Tuple[bool, float, str]:
    """Run a test suite and return results."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path, 
            "-v", 
            "--tb=short",
            "--durations=10"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        duration = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        return success, duration, result.stdout
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to run {description}: {e}"
        print(error_msg)
        return False, duration, error_msg


def main():
    """Run comprehensive test suite."""
    print("🧪 AI Configurator Template System - Comprehensive Test Suite")
    print("=" * 70)
    
    # Define test suites
    test_suites = [
        # Unit Tests
        ("tests/unit/test_template_validator_comprehensive.py", "Template Validator Unit Tests"),
        ("tests/unit/test_template_quality_checker_comprehensive.py", "Quality Checker Unit Tests"),
        ("tests/unit/test_template_installer_comprehensive.py", "Template Installer Unit Tests"),
        ("tests/unit/test_template_updater_comprehensive.py", "Template Updater Unit Tests"),
        ("tests/unit/test_template_catalog_generator_comprehensive.py", "Catalog Generator Unit Tests"),
        
        # Integration Tests
        ("tests/integration/test_template_workflow_integration.py", "Workflow Integration Tests"),
        ("tests/integration/test_template_performance_integration.py", "Performance Integration Tests"),
        ("tests/integration/test_template_system_integration.py", "System Integration Tests"),
        
        # Existing Tests (for regression)
        ("tests/unit/test_template_validator.py", "Template Validator (Existing)"),
        ("tests/unit/test_template_quality_checker.py", "Quality Checker (Existing)"),
        ("tests/unit/test_template_installer.py", "Template Installer (Existing)"),
    ]
    
    # Run all test suites
    results = []
    total_start_time = time.time()
    
    for test_path, description in test_suites:
        success, duration, output = run_test_suite(test_path, description)
        results.append((test_path, description, success, duration, output))
    
    total_duration = time.time() - total_start_time
    
    # Generate summary report
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    
    successful_tests = [r for r in results if r[2]]
    failed_tests = [r for r in results if not r[2]]
    
    print(f"✅ Successful Test Suites: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed Test Suites: {len(failed_tests)}/{len(results)}")
    print(f"⏱️  Total Execution Time: {total_duration:.2f} seconds")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    print("-" * 70)
    
    for test_path, description, success, duration, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {description:<40} | {duration:>6.2f}s")
    
    # Performance metrics
    print(f"\n⚡ Performance Metrics:")
    print("-" * 70)
    
    unit_tests = [r for r in results if "unit" in r[0]]
    integration_tests = [r for r in results if "integration" in r[0]]
    
    if unit_tests:
        unit_duration = sum(r[3] for r in unit_tests)
        print(f"Unit Tests Total Time: {unit_duration:.2f}s")
        print(f"Average Unit Test Time: {unit_duration/len(unit_tests):.2f}s")
    
    if integration_tests:
        integration_duration = sum(r[3] for r in integration_tests)
        print(f"Integration Tests Total Time: {integration_duration:.2f}s")
        print(f"Average Integration Test Time: {integration_duration/len(integration_tests):.2f}s")
    
    # Failed test details
    if failed_tests:
        print(f"\n🔍 Failed Test Details:")
        print("-" * 70)
        
        for test_path, description, success, duration, output in failed_tests:
            print(f"\n❌ {description}")
            print(f"   Path: {test_path}")
            print(f"   Duration: {duration:.2f}s")
            
            # Extract key error information
            lines = output.split('\n')
            error_lines = [line for line in lines if 'FAILED' in line or 'ERROR' in line]
            if error_lines:
                print("   Key Errors:")
                for error_line in error_lines[:5]:  # Show first 5 errors
                    print(f"     {error_line.strip()}")
    
    # Coverage and quality metrics
    print(f"\n📈 Test Coverage Summary:")
    print("-" * 70)
    
    comprehensive_tests = [r for r in results if "comprehensive" in r[0]]
    existing_tests = [r for r in results if "comprehensive" not in r[0] and "integration" not in r[0]]
    
    print(f"Comprehensive Unit Tests: {len(comprehensive_tests)} suites")
    print(f"Integration Tests: {len(integration_tests)} suites")
    print(f"Existing/Regression Tests: {len(existing_tests)} suites")
    
    # Final status
    print(f"\n🎯 Final Status:")
    print("-" * 70)
    
    if len(failed_tests) == 0:
        print("🎉 ALL TESTS PASSED! Template system is ready for production.")
        exit_code = 0
    else:
        print(f"⚠️  {len(failed_tests)} test suite(s) failed. Review and fix issues before deployment.")
        exit_code = 1
    
    print(f"\nTotal test execution time: {total_duration:.2f} seconds")
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)