"""Performance integration tests for template management system."""

import json
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest

from src.ai_configurator.core.template_validator import TemplateValidator
from src.ai_configurator.core.template_quality_checker import TemplateQualityChecker
from src.ai_configurator.core.template_installer import TemplateInstaller, InstallationConfig
from src.ai_configurator.core.template_catalog_generator import TemplateCatalogGenerator
from src.ai_configurator.core.models import ValidationReport


class TestTemplatePerformanceIntegration:
    """Performance integration tests for template management workflows."""
    
    @pytest.fixture
    def large_template_set(self):
        """Create a large set of templates for performance testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            
            # Create large number of templates
            num_templates = 100
            
            for i in range(num_templates):
                # Create profile template
                profile_data = {
                    "metadata": {
                        "name": f"perf-profile-{i}",
                        "description": f"Performance test profile {i} with comprehensive metadata and configuration options",
                        "category": "basic" if i % 2 == 0 else "professional",
                        "version": f"1.{i % 10}.0",
                        "author": "Performance Test Suite",
                        "created": "2024-01-01",
                        "tags": [f"perf-{i}", "performance", "test", f"category-{i % 5}"],
                        "complexity": ["low", "medium", "high"][i % 3],
                        "prerequisites": [f"prereq-{j}" for j in range(i % 3)],
                        "related_templates": [f"related-{j}" for j in range(i % 4)]
                    },
                    "paths": [f"contexts/domains/perf-context-{i}.md"],
                    "hooks": {f"perf-hook-{i}": {"enabled": True}},
                    "settings": {"auto_reload": True, "max_contexts": 50 + i}
                }
                
                category = "basic" if i % 2 == 0 else "professional"
                profile_file = examples_dir / "profiles" / category / f"perf-profile-{i}.json"
                with open(profile_file, 'w') as f:
                    json.dump(profile_data, f, indent=2)
                
                # Create context template
                context_content = f"""---
name: perf-context-{i}
description: Performance test context {i} for scalability testing
tags: [performance, test, context-{i}, category-{i % 5}]
categories: [performance, testing]
version: "1.{i % 10}.0"
---

# Performance Context {i}

## Overview

This is performance test context {i} designed to test the scalability and performance
of the template management system with large numbers of templates.

## Section 1: Basic Information

Context {i} provides comprehensive guidance for performance testing scenario {i}.
It includes multiple sections, code examples, and detailed explanations to simulate
real-world template complexity.

### Subsection 1.1: Configuration

```python
def performance_config_{i}():
    \"\"\"Configuration for performance test {i}.\"\"\"
    return {{
        "test_id": {i},
        "complexity": "{["low", "medium", "high"][i % 3]}",
        "category": "{category}",
        "features": [f"feature_{{j}}" for j in range({i % 5 + 1})]
    }}
```

### Subsection 1.2: Implementation

For instance, when implementing feature {i}:

```python
class PerformanceTest{i}:
    def __init__(self, config):
        self.config = config
        self.test_id = {i}
    
    def run_test(self):
        \"\"\"Run performance test {i}.\"\"\"
        start_time = time.time()
        
        # Simulate processing
        result = self.process_data()
        
        end_time = time.time()
        return {{
            "test_id": self.test_id,
            "duration": end_time - start_time,
            "result": result
        }}
    
    def process_data(self):
        \"\"\"Process test data for scenario {i}.\"\"\"
        return f"Processed data for test {i}"
```

## Section 2: Advanced Features

Such as in scenarios where you need advanced functionality:

- Feature A: Advanced processing capabilities
- Feature B: Enhanced performance monitoring
- Feature C: Scalable architecture patterns

### Code Examples

```bash
# Performance test script for scenario {i}
#!/bin/bash
echo "Running performance test {i}"

# Setup test environment
export TEST_ID={i}
export TEST_CATEGORY={category}

# Run test
python performance_test_{i}.py --config test_config_{i}.json

echo "Performance test {i} completed"
```

## Section 3: Best Practices

In real-world applications, consider these practices for scenario {i}:

1. **Performance Monitoring**: Track key metrics
2. **Resource Management**: Optimize memory usage
3. **Scalability**: Design for growth
4. **Error Handling**: Implement robust error recovery

## Conclusion

Performance context {i} demonstrates scalable template processing and provides
comprehensive guidance for performance testing scenarios.
"""
                
                context_file = examples_dir / "contexts" / "domains" / f"perf-context-{i}.md"
                with open(context_file, 'w') as f:
                    f.write(context_content)
                
                # Create hook template (every 3rd iteration)
                if i % 3 == 0:
                    hook_content = f"""name: perf-hook-{i}
description: Performance test hook {i} for automation and enhancement testing
version: "1.{i % 10}.0"
type: {"context" if i % 2 == 0 else "script"}
trigger: {"on_session_start" if i % 2 == 0 else "per_user_message"}
timeout: {30 + (i % 60)}
enabled: true

metadata:
  name: perf-hook-{i}
  description: Comprehensive performance test hook {i} with full configuration
  category: automation
  version: "1.{i % 10}.0"
  author: Performance Test Suite
  created: "2024-01-01"
  tags: [performance, test, hook-{i}, automation]
  complexity: {["low", "medium", "high"][i % 3]}
  prerequisites: [prereq-{j} for j in range({i % 2})]
  related_hooks: [related-hook-{j} for j in range({i % 3})]

config:
  performance_settings:
    max_iterations: {100 + i}
    timeout_multiplier: {1.0 + (i % 10) * 0.1}
    cache_enabled: {str(i % 2 == 0).lower()}
  
  test_parameters:
    test_id: {i}
    complexity_level: {i % 3 + 1}
    feature_flags: [flag-{j} for j in range({i % 4})]

context:
  sources:
    - contexts/domains/perf-context-{i}.md
  tags: [performance, test-{i}]
  priority: {i % 3 + 1}

conditions:
  - performance_test: true
    test_scenario: {i}
  - complexity_level: 
      above: {i % 3}
"""
                    
                    hook_file = examples_dir / "hooks" / "automation" / f"perf-hook-{i}.yaml"
                    with open(hook_file, 'w') as f:
                        f.write(hook_content)
            
            yield {
                "examples_dir": examples_dir,
                "num_profiles": num_templates,
                "num_contexts": num_templates,
                "num_hooks": num_templates // 3,
                "total_templates": num_templates * 2 + (num_templates // 3)
            }
    
    def test_validation_performance_large_scale(self, large_template_set):
        """Test validation performance with large template sets."""
        examples_dir = large_template_set["examples_dir"]
        expected_total = large_template_set["total_templates"]
        
        # Initialize validator
        validator = TemplateValidator(examples_dir)
        
        # Measure validation time
        start_time = time.time()
        validation_report = validator.validate_all_templates()
        validation_time = time.time() - start_time
        
        # Performance assertions
        assert validation_time < 60, f"Validation took too long: {validation_time:.2f} seconds"
        assert validation_report.is_valid, "Large scale validation should succeed"
        assert len(validation_report.files_checked) >= expected_total
        
        # Verify performance metrics
        files_per_second = len(validation_report.files_checked) / validation_time
        assert files_per_second > 2, f"Validation too slow: {files_per_second:.2f} files/second"
        
        print(f"Validation Performance: {files_per_second:.2f} files/second, {validation_time:.2f}s total")
    
    def test_quality_assessment_performance_large_scale(self, large_template_set):
        """Test quality assessment performance with large template sets."""
        examples_dir = large_template_set["examples_dir"]
        expected_total = large_template_set["total_templates"]
        
        # Initialize quality checker
        quality_checker = TemplateQualityChecker(examples_dir)
        
        # Measure quality assessment time
        start_time = time.time()
        quality_reports = quality_checker.assess_all_templates()
        assessment_time = time.time() - start_time
        
        # Performance assertions
        assert assessment_time < 120, f"Quality assessment took too long: {assessment_time:.2f} seconds"
        assert len(quality_reports) >= expected_total
        
        # Verify performance metrics
        templates_per_second = len(quality_reports) / assessment_time
        assert templates_per_second > 1, f"Quality assessment too slow: {templates_per_second:.2f} templates/second"
        
        # Verify quality distribution
        quality_levels = [report.overall_level for report in quality_reports]
        assert len(set(quality_levels)) > 1, "Should have varied quality levels"
        
        print(f"Quality Assessment Performance: {templates_per_second:.2f} templates/second, {assessment_time:.2f}s total")
    
    def test_catalog_generation_performance_large_scale(self, large_template_set):
        """Test catalog generation performance with large template sets."""
        examples_dir = large_template_set["examples_dir"]
        expected_total = large_template_set["total_templates"]
        
        # Initialize catalog generator
        generator = TemplateCatalogGenerator(str(examples_dir))
        
        # Measure catalog generation time
        start_time = time.time()
        catalog = generator.generate_catalog()
        generation_time = time.time() - start_time
        
        # Performance assertions
        assert generation_time < 30, f"Catalog generation took too long: {generation_time:.2f} seconds"
        assert catalog.total_count >= expected_total
        
        # Verify performance metrics
        templates_per_second = catalog.total_count / generation_time
        assert templates_per_second > 5, f"Catalog generation too slow: {templates_per_second:.2f} templates/second"
        
        print(f"Catalog Generation Performance: {templates_per_second:.2f} templates/second, {generation_time:.2f}s total")
    
    def test_concurrent_operations_performance(self, large_template_set):
        """Test performance of concurrent template operations."""
        examples_dir = large_template_set["examples_dir"]
        
        def run_validation():
            validator = TemplateValidator(examples_dir)
            start_time = time.time()
            report = validator.validate_all_templates()
            return ("validation", time.time() - start_time, len(report.files_checked))
        
        def run_quality_assessment():
            quality_checker = TemplateQualityChecker(examples_dir)
            start_time = time.time()
            reports = quality_checker.assess_all_templates()
            return ("quality", time.time() - start_time, len(reports))
        
        def run_catalog_generation():
            generator = TemplateCatalogGenerator(str(examples_dir))
            start_time = time.time()
            catalog = generator.generate_catalog()
            return ("catalog", time.time() - start_time, catalog.total_count)
        
        # Run operations concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(run_validation),
                executor.submit(run_quality_assessment),
                executor.submit(run_catalog_generation)
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        # Verify all operations completed
        assert len(results) == 3
        
        # Verify performance
        for operation, duration, count in results:
            assert duration < 120, f"{operation} took too long: {duration:.2f} seconds"
            assert count > 0, f"{operation} processed no templates"
            
            throughput = count / duration
            print(f"{operation.title()} Performance: {throughput:.2f} items/second, {duration:.2f}s total")
    
    def test_memory_usage_large_scale(self, large_template_set):
        """Test memory usage with large template sets."""
        import psutil
        import os
        
        examples_dir = large_template_set["examples_dir"]
        process = psutil.Process(os.getpid())
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run memory-intensive operations
        validator = TemplateValidator(examples_dir)
        validation_report = validator.validate_all_templates()
        
        quality_checker = TemplateQualityChecker(examples_dir)
        quality_reports = quality_checker.assess_all_templates()
        
        generator = TemplateCatalogGenerator(str(examples_dir))
        catalog = generator.generate_catalog()
        
        # Measure peak memory
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory usage assertions
        assert memory_increase < 500, f"Memory usage too high: {memory_increase:.2f} MB increase"
        
        # Memory efficiency metrics
        templates_per_mb = large_template_set["total_templates"] / max(memory_increase, 1)
        assert templates_per_mb > 1, f"Memory efficiency too low: {templates_per_mb:.2f} templates/MB"
        
        print(f"Memory Usage: {memory_increase:.2f} MB increase, {templates_per_mb:.2f} templates/MB")
    
    def test_installation_performance_large_scale(self, large_template_set):
        """Test installation performance with large template sets."""
        examples_dir = large_template_set["examples_dir"]
        
        with tempfile.TemporaryDirectory() as temp_target:
            target_dir = Path(temp_target)
            
            # Setup installer
            config = InstallationConfig(
                target_directory=target_dir,
                examples_directory=examples_dir,
                validate_before_install=False,  # Skip validation for performance
                validate_after_install=False
            )
            installer = TemplateInstaller(config)
            
            # Discover templates
            start_time = time.time()
            templates = installer.discover_templates()
            discovery_time = time.time() - start_time
            
            # Performance assertions for discovery
            assert discovery_time < 10, f"Template discovery took too long: {discovery_time:.2f} seconds"
            assert len(templates) >= large_template_set["total_templates"]
            
            # Install subset of templates for performance testing
            template_names = list(templates.keys())[:50]  # Install first 50 templates
            
            start_time = time.time()
            results = installer.install_multiple_templates(template_names)
            installation_time = time.time() - start_time
            
            # Performance assertions for installation
            assert installation_time < 30, f"Installation took too long: {installation_time:.2f} seconds"
            
            successful_installs = [r for r in results if r.success]
            assert len(successful_installs) == len(template_names)
            
            # Installation performance metrics
            installs_per_second = len(successful_installs) / installation_time
            assert installs_per_second > 1, f"Installation too slow: {installs_per_second:.2f} installs/second"
            
            print(f"Installation Performance: {installs_per_second:.2f} installs/second, {installation_time:.2f}s total")
    
    def test_scalability_stress_test(self, large_template_set):
        """Stress test system scalability with maximum load."""
        examples_dir = large_template_set["examples_dir"]
        
        # Run all operations simultaneously with maximum load
        operations = []
        
        def stress_validation():
            validator = TemplateValidator(examples_dir)
            for _ in range(3):  # Multiple validation runs
                report = validator.validate_all_templates()
                assert report is not None
        
        def stress_quality_assessment():
            quality_checker = TemplateQualityChecker(examples_dir)
            for _ in range(2):  # Multiple quality runs
                reports = quality_checker.assess_all_templates()
                assert len(reports) > 0
        
        def stress_catalog_generation():
            generator = TemplateCatalogGenerator(str(examples_dir))
            for _ in range(3):  # Multiple catalog generations
                catalog = generator.generate_catalog()
                assert catalog.total_count > 0
        
        # Run stress test
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(stress_validation),
                executor.submit(stress_validation),  # Duplicate for stress
                executor.submit(stress_quality_assessment),
                executor.submit(stress_quality_assessment),  # Duplicate for stress
                executor.submit(stress_catalog_generation),
                executor.submit(stress_catalog_generation)  # Duplicate for stress
            ]
            
            # Wait for all operations to complete
            for future in as_completed(futures):
                future.result()  # Will raise exception if operation failed
        
        total_time = time.time() - start_time
        
        # Stress test assertions
        assert total_time < 300, f"Stress test took too long: {total_time:.2f} seconds"
        
        print(f"Stress Test Performance: {total_time:.2f}s total for 8 concurrent operations")
    
    def test_performance_regression_detection(self, large_template_set):
        """Test for performance regression detection."""
        examples_dir = large_template_set["examples_dir"]
        
        # Baseline performance measurements
        baseline_times = {}
        
        # Measure validation baseline
        validator = TemplateValidator(examples_dir)
        start_time = time.time()
        validator.validate_all_templates()
        baseline_times["validation"] = time.time() - start_time
        
        # Measure quality assessment baseline
        quality_checker = TemplateQualityChecker(examples_dir)
        start_time = time.time()
        quality_checker.assess_all_templates()
        baseline_times["quality"] = time.time() - start_time
        
        # Measure catalog generation baseline
        generator = TemplateCatalogGenerator(str(examples_dir))
        start_time = time.time()
        generator.generate_catalog()
        baseline_times["catalog"] = time.time() - start_time
        
        # Run operations again and compare
        regression_threshold = 1.5  # 50% slower is considered regression
        
        # Re-measure validation
        start_time = time.time()
        validator.validate_all_templates()
        validation_time = time.time() - start_time
        
        assert validation_time < baseline_times["validation"] * regression_threshold, \
            f"Validation regression detected: {validation_time:.2f}s vs baseline {baseline_times['validation']:.2f}s"
        
        # Re-measure quality assessment
        start_time = time.time()
        quality_checker.assess_all_templates()
        quality_time = time.time() - start_time
        
        assert quality_time < baseline_times["quality"] * regression_threshold, \
            f"Quality assessment regression detected: {quality_time:.2f}s vs baseline {baseline_times['quality']:.2f}s"
        
        # Re-measure catalog generation
        start_time = time.time()
        generator.generate_catalog()
        catalog_time = time.time() - start_time
        
        assert catalog_time < baseline_times["catalog"] * regression_threshold, \
            f"Catalog generation regression detected: {catalog_time:.2f}s vs baseline {baseline_times['catalog']:.2f}s"
        
        print("Performance Regression Test: PASSED - No significant regressions detected")
        for operation, baseline_time in baseline_times.items():
            print(f"  {operation}: {baseline_time:.2f}s baseline")