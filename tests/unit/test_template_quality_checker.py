"""Unit tests for template quality checker system."""

import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.ai_configurator.core.template_quality_checker import (
    TemplateQualityChecker,
    QualityLevel,
    QualityMetric,
    QualityReport
)


class TestQualityMetric:
    """Test quality metric data structure."""
    
    def test_quality_metric_creation(self):
        """Test quality metric creation."""
        metric = QualityMetric(
            name="Test Metric",
            score=0.8,
            level=QualityLevel.GOOD,
            message="Test message",
            suggestions=["Suggestion 1", "Suggestion 2"]
        )
        
        assert metric.name == "Test Metric"
        assert metric.score == 0.8
        assert metric.level == QualityLevel.GOOD
        assert len(metric.suggestions) == 2


class TestQualityReport:
    """Test quality report data structure."""
    
    def test_quality_report_creation(self):
        """Test quality report creation."""
        metrics = [
            QualityMetric("Metric 1", 0.8, QualityLevel.GOOD, "Good", []),
            QualityMetric("Metric 2", 0.9, QualityLevel.EXCELLENT, "Excellent", [])
        ]
        
        report = QualityReport(
            file_path="test.json",
            template_type="profile",
            overall_score=0.85,
            overall_level=QualityLevel.GOOD,
            metrics=metrics,
            documentation_completeness=0.8,
            example_accuracy=0.9,
            best_practices_compliance=0.85,
            suggestions=["Test suggestion"]
        )
        
        assert report.file_path == "test.json"
        assert report.template_type == "profile"
        assert report.overall_score == 0.85
        assert len(report.metrics) == 2


class TestTemplateQualityChecker:
    """Test template quality checker functionality."""
    
    @pytest.fixture
    def temp_examples_dir(self):
        """Create a temporary examples directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            
            yield examples_dir
    
    @pytest.fixture
    def quality_checker(self, temp_examples_dir):
        """Create a quality checker with temporary directory."""
        return TemplateQualityChecker(temp_examples_dir)
    
    def test_quality_checker_initialization(self, temp_examples_dir):
        """Test quality checker initialization."""
        checker = TemplateQualityChecker(temp_examples_dir)
        assert checker.base_path == temp_examples_dir
        assert hasattr(checker, 'validator')
        assert hasattr(checker, 'quality_thresholds')
    
    def test_score_to_level_conversion(self, quality_checker):
        """Test score to quality level conversion."""
        assert quality_checker._score_to_level(0.95) == QualityLevel.EXCELLENT
        assert quality_checker._score_to_level(0.8) == QualityLevel.GOOD
        assert quality_checker._score_to_level(0.65) == QualityLevel.FAIR
        assert quality_checker._score_to_level(0.4) == QualityLevel.POOR
    
    def test_assess_metadata_completeness(self, quality_checker):
        """Test metadata completeness assessment."""
        # Complete metadata
        complete_metadata = {
            'metadata': {
                'name': 'test-template',
                'description': 'A comprehensive test template',
                'category': 'basic',
                'complexity': 'low',
                'created': '2024-01-01',
                'version': '1.0.0',
                'author': 'Test Author',
                'tags': ['test', 'example']
            }
        }
        
        metric = quality_checker._assess_metadata_completeness(complete_metadata)
        assert metric.score > 0.8
        assert metric.level in [QualityLevel.GOOD, QualityLevel.EXCELLENT]
        
        # Incomplete metadata
        incomplete_metadata = {
            'metadata': {
                'name': 'test-template'
            }
        }
        
        metric = quality_checker._assess_metadata_completeness(incomplete_metadata)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_profile_documentation(self, quality_checker):
        """Test profile documentation assessment."""
        # Well-documented profile
        good_content = '''
        {
            // ============================================================================
            // COMPREHENSIVE PROFILE EXAMPLE
            // ============================================================================
            // This profile demonstrates excellent documentation practices
            // with detailed comments explaining each configuration option.
            // ============================================================================
            // METADATA SECTION
            // ============================================================================
            "metadata": {
                "name": "test-profile",
                "description": "A comprehensive test profile with excellent documentation and examples"
            },
            // PATHS SECTION
            // ============================================================================
            "paths": ["contexts/test.md"]
        }
        '''
        
        json_data = {'metadata': {'description': 'A comprehensive test profile with excellent documentation and examples'}}
        metric = quality_checker._assess_profile_documentation(json_data, good_content)
        assert metric.score > 0.7
        
        # Poorly documented profile
        poor_content = '''
        {
            "metadata": {"name": "test", "description": "Short"},
            "paths": []
        }
        '''
        
        json_data = {'metadata': {'description': 'Short'}}
        metric = quality_checker._assess_profile_documentation(json_data, poor_content)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_context_structure(self, quality_checker):
        """Test context structure assessment."""
        # Well-structured context
        good_content = '''# Main Title

## Overview

This is a comprehensive overview of the context.

## Section 1

Content for section 1.

### Subsection 1.1

More detailed content.

## Section 2

Content for section 2.

## Conclusion

Summary of the context.
'''
        
        metric = quality_checker._assess_context_structure(good_content)
        assert metric.score > 0.8
        
        # Poorly structured context
        poor_content = '''Some content without proper headers or structure.
This lacks organization and clear sections.'''
        
        metric = quality_checker._assess_context_structure(poor_content)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_context_depth(self, quality_checker):
        """Test context depth assessment."""
        # Comprehensive content
        comprehensive_content = '''# Comprehensive Guide

## Overview
''' + ' '.join(['This is comprehensive content with many words.'] * 100) + '''

## Section 1
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

## Section 2
- Another point 1
- Another point 2
- Another point 3
- Another point 4
- Another point 5

## Section 3
More detailed content here.

## Section 4
Even more content.

## Section 5
Final section with content.
'''
        
        metric = quality_checker._assess_context_depth(comprehensive_content)
        assert metric.score > 0.7
        
        # Shallow content
        shallow_content = '''# Short Guide

Brief content.'''
        
        metric = quality_checker._assess_context_depth(shallow_content)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_context_examples(self, quality_checker):
        """Test context examples assessment."""
        # Content with good examples
        good_examples_content = '''# Guide with Examples

## Overview

This guide provides many practical examples.

```python
# Example 1: Basic usage
def example_function():
    return "This is an example"
```

For instance, when you need to implement authentication, you can use this approach.

```javascript
// Example 2: JavaScript implementation
function authenticate(user) {
    return user.isValid();
}
```

Such as in scenarios where you need to validate user input.

```bash
# Example 3: Command line usage
./script.sh --option value
```

In real-world situations, you might encounter various use cases like this.
'''
        
        metric = quality_checker._assess_context_examples(good_examples_content)
        assert metric.score > 0.8
        
        # Content without examples
        no_examples_content = '''# Guide Without Examples

This guide lacks practical examples and code snippets.
It's mostly theoretical without showing how to implement concepts.
'''
        
        metric = quality_checker._assess_context_examples(no_examples_content)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_hook_configuration(self, quality_checker):
        """Test hook configuration assessment."""
        # Complete hook configuration
        complete_hook = {
            'name': 'test-hook',
            'description': 'A comprehensive test hook',
            'trigger': 'on_session_start',
            'type': 'context',
            'timeout': 30,
            'config': {
                'option1': 'value1',
                'option2': 'value2'
            }
        }
        
        metric = quality_checker._assess_hook_configuration(complete_hook)
        assert metric.score > 0.8
        
        # Minimal hook configuration
        minimal_hook = {
            'name': 'minimal-hook'
        }
        
        metric = quality_checker._assess_hook_configuration(minimal_hook)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_hook_documentation(self, quality_checker):
        """Test hook documentation assessment."""
        # Well-documented hook
        documented_hook = {
            'name': 'test-hook',
            'description': 'This is a comprehensive description of the hook that explains its purpose and functionality',
            'metadata': {
                'author': 'Test Author',
                'category': 'automation',
                'complexity': 'medium'
            }
        }
        
        metric = quality_checker._assess_hook_documentation(documented_hook)
        assert metric.score > 0.6
        
        # Poorly documented hook
        undocumented_hook = {
            'name': 'test-hook'
        }
        
        metric = quality_checker._assess_hook_documentation(undocumented_hook)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_template_quality_profile(self, quality_checker, temp_examples_dir):
        """Test complete profile template quality assessment."""
        # Create a test profile file
        profile_content = '''
        {
            // ============================================================================
            // TEST PROFILE EXAMPLE
            // ============================================================================
            "metadata": {
                "name": "test-profile",
                "description": "A comprehensive test profile for quality assessment",
                "category": "basic",
                "complexity": "low",
                "created": "2024-01-01",
                "tags": ["test", "example"]
            },
            // PATHS SECTION
            // ============================================================================
            "paths": ["contexts/test.md"],
            "hooks": {},
            "settings": {"auto_reload": true}
        }
        '''
        
        profile_file = temp_examples_dir / "profiles" / "basic" / "test-profile.json"
        with open(profile_file, 'w') as f:
            f.write(profile_content)
        
        report = quality_checker.assess_template_quality(profile_file)
        
        assert report.template_type == "profile"
        assert report.overall_score > 0.0
        assert len(report.metrics) > 0
        assert report.overall_level in QualityLevel
    
    def test_assess_template_quality_context(self, quality_checker, temp_examples_dir):
        """Test complete context template quality assessment."""
        # Create a test context file
        context_content = '''---
name: test-context
description: A test context for quality assessment
tags: [test, example]
---

# Test Context

## Overview

This is a comprehensive test context that provides substantial guidance for testing purposes.

## Best Practices

- Follow established patterns
- Include comprehensive documentation
- Provide practical examples

```python
# Example code snippet
def example_function():
    return "This demonstrates code examples in contexts"
```

For instance, when implementing this pattern, you should consider the following scenarios.

## Use Cases

Such as in situations where you need to:
- Handle user input
- Process data
- Generate reports

## Conclusion

This context provides sufficient content and structure for quality assessment testing.
'''
        
        context_file = temp_examples_dir / "contexts" / "domains" / "test-context.md"
        with open(context_file, 'w') as f:
            f.write(context_content)
        
        report = quality_checker.assess_template_quality(context_file)
        
        assert report.template_type == "context"
        assert report.overall_score > 0.0
        assert len(report.metrics) > 0
        assert report.overall_level in QualityLevel
    
    def test_assess_template_quality_hook(self, quality_checker, temp_examples_dir):
        """Test complete hook template quality assessment."""
        # Create a test hook file
        hook_content = '''name: test-hook
description: A comprehensive test hook for quality assessment
version: "1.0"
type: context
trigger: on_session_start
timeout: 30
enabled: true

config:
  option1: value1
  option2: value2
  option3: value3

metadata:
  author: Test Author
  category: automation
  complexity: medium
  related_hooks: [other-hook]

context:
  sources: [contexts/test.md]
  tags: [test]
  priority: 1
'''
        
        hook_file = temp_examples_dir / "hooks" / "automation" / "test-hook.yaml"
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        report = quality_checker.assess_template_quality(hook_file)
        
        assert report.template_type == "hook"
        assert report.overall_score > 0.0
        assert len(report.metrics) > 0
        assert report.overall_level in QualityLevel
    
    def test_assess_all_templates(self, quality_checker, temp_examples_dir):
        """Test assessment of all templates."""
        # Create test files
        profile_file = temp_examples_dir / "profiles" / "basic" / "test.json"
        with open(profile_file, 'w') as f:
            f.write('{"metadata": {"name": "test", "description": "test", "category": "basic", "complexity": "low", "created": "2024-01-01"}}')
        
        context_file = temp_examples_dir / "contexts" / "domains" / "test.md"
        with open(context_file, 'w') as f:
            f.write('# Test\n\nThis is a test context with sufficient content for assessment.')
        
        reports = quality_checker.assess_all_templates()
        
        assert len(reports) == 2
        assert all(isinstance(report, QualityReport) for report in reports)
    
    def test_generate_quality_summary(self, quality_checker):
        """Test quality summary generation."""
        # Create mock reports
        reports = [
            QualityReport(
                file_path="test1.json",
                template_type="profile",
                overall_score=0.9,
                overall_level=QualityLevel.EXCELLENT,
                metrics=[],
                documentation_completeness=0.8,
                example_accuracy=0.9,
                best_practices_compliance=0.95,
                suggestions=["Suggestion 1"]
            ),
            QualityReport(
                file_path="test2.md",
                template_type="context",
                overall_score=0.6,
                overall_level=QualityLevel.FAIR,
                metrics=[],
                documentation_completeness=0.5,
                example_accuracy=0.7,
                best_practices_compliance=0.6,
                suggestions=["Suggestion 2", "Suggestion 1"]
            )
        ]
        
        summary = quality_checker.generate_quality_summary(reports)
        
        assert summary["total_templates"] == 2
        assert "average_score" in summary
        assert "quality_distribution" in summary
        assert "template_types" in summary
        assert "common_issues" in summary
        assert "best_template" in summary
        assert "worst_template" in summary
        assert "recommendations" in summary
    
    def test_generate_quality_summary_empty(self, quality_checker):
        """Test quality summary generation with empty reports."""
        summary = quality_checker.generate_quality_summary([])
        assert "error" in summary
    
    def test_assess_profile_best_practices(self, quality_checker, temp_examples_dir):
        """Test profile best practices assessment."""
        # Good practices
        good_data = {
            'metadata': {
                'category': 'basic',
                'complexity': 'low'
            },
            'paths': ['contexts/relative/path.md']
        }
        
        good_file = temp_examples_dir / "profiles" / "basic" / "good-profile.json"
        metric = quality_checker._assess_profile_best_practices(good_data, good_file)
        assert metric.score > 0.7
        
        # Poor practices
        poor_data = {
            'metadata': {
                'category': 'wrong',
                'complexity': ''
            },
            'paths': ['/absolute/path/to/context.md']
        }
        
        poor_file = temp_examples_dir / "profiles" / "basic" / "BadProfileName.json"
        metric = quality_checker._assess_profile_best_practices(poor_data, poor_file)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0
    
    def test_assess_hook_best_practices(self, quality_checker, temp_examples_dir):
        """Test hook best practices assessment."""
        # Good practices
        good_data = {
            'trigger': 'on_session_start',
            'timeout': 30,
            'conditions': [{'profile': ['test']}]
        }
        
        good_file = temp_examples_dir / "hooks" / "automation" / "good-hook.yaml"
        metric = quality_checker._assess_hook_best_practices(good_data, good_file)
        assert metric.score > 0.8
        
        # Poor practices
        poor_data = {
            'trigger': '',
            'timeout': 200
        }
        
        poor_file = temp_examples_dir / "hooks" / "automation" / "BadHookName.yaml"
        metric = quality_checker._assess_hook_best_practices(poor_data, poor_file)
        assert metric.score < 0.5
        assert len(metric.suggestions) > 0


class TestQualityCheckerIntegration:
    """Integration tests for quality checker."""
    
    @pytest.fixture
    def temp_examples_with_quality_files(self):
        """Create temporary examples directory with files of varying quality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            
            # Create high-quality profile
            high_quality_profile = '''
            {
                // ============================================================================
                // EXCELLENT PROFILE EXAMPLE
                // ============================================================================
                // This profile demonstrates excellent documentation practices with detailed
                // comments explaining each configuration option and providing examples.
                // ============================================================================
                // METADATA SECTION
                // ============================================================================
                "metadata": {
                    "name": "excellent-profile",
                    "description": "A comprehensive profile template demonstrating best practices with excellent documentation and examples",
                    "category": "basic",
                    "version": "1.0.0",
                    "author": "AI Configurator Team",
                    "created": "2024-01-01",
                    "updated": "2024-01-01",
                    "tags": ["example", "best-practices", "comprehensive"],
                    "complexity": "low",
                    "prerequisites": [],
                    "related_templates": ["good-profile"]
                },
                // PATHS SECTION
                // ============================================================================
                // Define context paths that provide domain-specific guidance
                // ============================================================================
                "paths": [
                    "contexts/domains/development-guidelines.md",
                    "contexts/workflows/best-practices.md"
                ],
                // HOOKS SECTION
                // ============================================================================
                // Optional automation hooks for enhanced functionality
                // ============================================================================
                "hooks": {
                    // "auto-documentation": {
                    //   "enabled": false,
                    //   "description": "Automatically generate documentation"
                    // }
                },
                // SETTINGS SECTION
                // ============================================================================
                // Configuration options for profile behavior
                // ============================================================================
                "settings": {
                    "auto_reload": true,
                    "max_contexts": 50,
                    "validate_contexts": true
                }
            }
            '''
            
            excellent_profile_file = examples_dir / "profiles" / "basic" / "excellent-profile.json"
            with open(excellent_profile_file, 'w') as f:
                f.write(high_quality_profile)
            
            # Create low-quality profile
            low_quality_profile = '''
            {
                "metadata": {"name": "bad", "description": "bad", "category": "basic", "complexity": "low", "created": "2024-01-01"},
                "paths": []
            }
            '''
            
            poor_profile_file = examples_dir / "profiles" / "basic" / "BadProfile.json"
            with open(poor_profile_file, 'w') as f:
                f.write(low_quality_profile)
            
            yield examples_dir
    
    def test_comprehensive_quality_assessment(self, temp_examples_with_quality_files):
        """Test comprehensive quality assessment of templates with varying quality."""
        checker = TemplateQualityChecker(temp_examples_with_quality_files)
        reports = checker.assess_all_templates()
        
        assert len(reports) == 2
        
        # Find the excellent and poor quality reports
        excellent_report = next((r for r in reports if "excellent" in r.file_path), None)
        poor_report = next((r for r in reports if "BadProfile" in r.file_path), None)
        
        assert excellent_report is not None
        assert poor_report is not None
        
        # Excellent template should have higher score
        assert excellent_report.overall_score > poor_report.overall_score
        assert excellent_report.overall_level.value != QualityLevel.POOR.value
        
        # Generate summary
        summary = checker.generate_quality_summary(reports)
        assert summary["total_templates"] == 2
        assert "recommendations" in summary