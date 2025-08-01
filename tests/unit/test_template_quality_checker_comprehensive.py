"""Comprehensive unit tests for template quality checker system."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.ai_configurator.core.template_quality_checker import (
    TemplateQualityChecker,
    QualityLevel,
    QualityMetric,
    QualityReport
)


class TestTemplateQualityCheckerComprehensive:
    """Comprehensive tests for template quality checker functionality."""
    
    @pytest.fixture
    def temp_examples_dir(self):
        """Create a comprehensive temporary examples directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create comprehensive directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "profiles" / "advanced").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "hooks" / "enhancement").mkdir(parents=True)
            
            yield examples_dir
    
    @pytest.fixture
    def quality_checker(self, temp_examples_dir):
        """Create a quality checker with comprehensive test directory."""
        return TemplateQualityChecker(temp_examples_dir)
    
    def test_comprehensive_quality_assessment_profiles(self, quality_checker, temp_examples_dir):
        """Test comprehensive quality assessment for various profile templates."""
        test_profiles = [
            # Excellent quality profile
            {
                "filename": "excellent-profile.json",
                "content": '''
                {
                    // ============================================================================
                    // EXCELLENT PROFILE TEMPLATE
                    // ============================================================================
                    // This profile demonstrates exceptional documentation practices with
                    // comprehensive comments, clear structure, and detailed explanations.
                    // 
                    // Use this template as a reference for creating high-quality profiles
                    // that provide clear guidance to users.
                    // ============================================================================
                    
                    // METADATA SECTION
                    // ============================================================================
                    // Complete metadata with all recommended fields
                    // ============================================================================
                    "metadata": {
                        "name": "excellent-profile",
                        "description": "An exceptionally well-documented profile template that demonstrates best practices for structure, documentation, and user guidance. This comprehensive example includes detailed comments, clear organization, and practical examples.",
                        "category": "professional",
                        "version": "2.1.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "updated": "2024-02-15",
                        "tags": ["best-practices", "comprehensive", "example", "professional"],
                        "complexity": "medium",
                        "prerequisites": ["basic-understanding", "tool-familiarity"],
                        "related_templates": ["advanced-profile", "specialized-profile"]
                    },
                    
                    // CONTEXT PATHS SECTION
                    // ============================================================================
                    // Carefully curated context paths for comprehensive guidance
                    // ============================================================================
                    "paths": [
                        "contexts/domains/development-best-practices.md",
                        "contexts/workflows/code-review-process.md",
                        "contexts/integrations/ci-cd-patterns.md"
                    ],
                    
                    // HOOKS CONFIGURATION
                    // ============================================================================
                    // Optional automation hooks for enhanced functionality
                    // Uncomment and configure as needed for your specific use case
                    // ============================================================================
                    "hooks": {
                        // "auto-documentation": {
                        //     "enabled": false,
                        //     "description": "Automatically generate documentation from code"
                        // },
                        // "quality-check": {
                        //     "enabled": true,
                        //     "description": "Run quality checks on code changes"
                        // }
                    },
                    
                    // PROFILE SETTINGS
                    // ============================================================================
                    // Configuration options for profile behavior
                    // Customize these settings based on your workflow requirements
                    // ============================================================================
                    "settings": {
                        "auto_reload": true,           // Automatically reload contexts on change
                        "max_contexts": 50,            // Maximum number of contexts to load
                        "validation_level": "strict",  // Validation strictness level
                        "cache_enabled": true,         // Enable context caching for performance
                        "debug_mode": false           // Enable debug logging
                    }
                }
                ''',
                "expected_score_range": (0.85, 1.0),
                "expected_level": QualityLevel.EXCELLENT
            },
            
            # Good quality profile
            {
                "filename": "good-profile.json",
                "content": '''
                {
                    // Good Profile Template
                    // This profile shows good practices with adequate documentation
                    
                    "metadata": {
                        "name": "good-profile",
                        "description": "A well-structured profile template with good documentation and clear organization",
                        "category": "basic",
                        "version": "1.2.0",
                        "created": "2024-01-01",
                        "tags": ["example", "good-practices"],
                        "complexity": "low"
                    },
                    
                    // Context paths for this profile
                    "paths": [
                        "contexts/basic-guidelines.md",
                        "contexts/getting-started.md"
                    ],
                    
                    // Basic settings
                    "settings": {
                        "auto_reload": true,
                        "max_contexts": 25
                    }
                }
                ''',
                "expected_score_range": (0.65, 0.84),
                "expected_level": QualityLevel.GOOD
            },
            
            # Fair quality profile
            {
                "filename": "fair-profile.json",
                "content": '''
                {
                    // Basic profile with minimal documentation
                    "metadata": {
                        "name": "fair-profile",
                        "description": "Basic profile template",
                        "category": "basic",
                        "complexity": "low",
                        "created": "2024-01-01"
                    },
                    "paths": ["contexts/basic.md"]
                }
                ''',
                "expected_score_range": (0.4, 0.64),
                "expected_level": QualityLevel.FAIR
            },
            
            # Poor quality profile
            {
                "filename": "poor-profile.json",
                "content": '''
                {
                    "metadata": {
                        "name": "poor",
                        "description": "Bad",
                        "category": "basic",
                        "complexity": "low",
                        "created": "2024-01-01"
                    },
                    "paths": []
                }
                ''',
                "expected_score_range": (0.0, 0.39),
                "expected_level": QualityLevel.POOR
            }
        ]
        
        for profile_test in test_profiles:
            # Create the profile file
            profile_file = temp_examples_dir / "profiles" / "basic" / profile_test["filename"]
            with open(profile_file, 'w') as f:
                f.write(profile_test["content"])
            
            # Assess quality
            report = quality_checker.assess_template_quality(profile_file)
            
            # Verify quality assessment
            assert report.template_type == "profile"
            assert profile_test["expected_score_range"][0] <= report.overall_score <= profile_test["expected_score_range"][1], \
                f"Score {report.overall_score} not in expected range {profile_test['expected_score_range']} for {profile_test['filename']}"
            assert report.overall_level == profile_test["expected_level"], \
                f"Expected level {profile_test['expected_level']}, got {report.overall_level} for {profile_test['filename']}"
            
            # Verify metrics are present
            assert len(report.metrics) > 0, f"Should have quality metrics for {profile_test['filename']}"
            
            # Verify suggestions for lower quality templates
            if report.overall_level in [QualityLevel.POOR, QualityLevel.FAIR]:
                assert len(report.suggestions) > 0, f"Should have suggestions for improvement for {profile_test['filename']}"
    
    def test_comprehensive_quality_assessment_contexts(self, quality_checker, temp_examples_dir):
        """Test comprehensive quality assessment for various context templates."""
        test_contexts = [
            # Excellent quality context
            {
                "filename": "excellent-context.md",
                "content": '''---
name: excellent-context
description: Comprehensive development best practices guide
tags: [development, best-practices, comprehensive, guide]
categories: [development, documentation]
version: "2.0.0"
author: "AI Configurator Team"
created: "2024-01-01"
updated: "2024-02-15"
---

# Comprehensive Development Best Practices Guide

## Overview

This comprehensive guide provides detailed information about modern software development practices, covering everything from initial project setup to advanced deployment strategies. It serves as a complete reference for developers at all levels, offering practical examples, code snippets, and real-world scenarios that can be immediately applied to your projects.

The guide emphasizes industry-standard practices, proven methodologies, and emerging trends that will help you build robust, maintainable, and scalable software solutions.

## Getting Started

### Prerequisites

Before diving into the development practices outlined in this guide, ensure you have the following foundational knowledge and tools:

- **Programming Fundamentals**: Understanding of at least one programming language
- **Version Control**: Familiarity with Git and version control concepts
- **Development Environment**: Properly configured IDE or text editor
- **Command Line**: Basic command line navigation and operations

### Essential Tools

```bash
# Install essential development tools
npm install -g @commitlint/cli @commitlint/config-conventional
pip install pre-commit black flake8 pytest
```

## Code Quality Standards

### Writing Clean Code

Clean code is the foundation of maintainable software. Follow these principles:

1. **Meaningful Names**: Use descriptive variable and function names
2. **Single Responsibility**: Each function should do one thing well
3. **DRY Principle**: Don't Repeat Yourself - extract common functionality
4. **SOLID Principles**: Follow object-oriented design principles

```python
# Good example: Clear, descriptive function
def calculate_user_engagement_score(user_actions: List[UserAction]) -> float:
    """Calculate engagement score based on user actions.
    
    Args:
        user_actions: List of user action objects
        
    Returns:
        Engagement score between 0.0 and 1.0
    """
    if not user_actions:
        return 0.0
    
    weighted_score = sum(action.weight * action.value for action in user_actions)
    return min(weighted_score / len(user_actions), 1.0)
```

### Code Documentation

Comprehensive documentation is crucial for team collaboration:

```python
class DataProcessor:
    """Processes and validates incoming data streams.
    
    This class handles various data formats and provides validation,
    transformation, and error handling capabilities.
    
    Attributes:
        config: Configuration object for processing parameters
        validators: List of validation functions to apply
    """
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.validators = self._load_validators()
    
    def process_batch(self, data_batch: List[Dict]) -> ProcessedBatch:
        """Process a batch of data items.
        
        Args:
            data_batch: List of raw data dictionaries
            
        Returns:
            ProcessedBatch object containing results and metadata
            
        Raises:
            ValidationError: If data fails validation
            ProcessingError: If processing fails
        """
        # Implementation details...
        pass
```

## Testing Strategies

### Unit Testing Best Practices

For instance, when writing unit tests, consider these essential practices:

- **Test Isolation**: Each test should be independent
- **Clear Assertions**: Use descriptive assertion messages
- **Edge Cases**: Test boundary conditions and error scenarios
- **Mock External Dependencies**: Isolate the code under test

```python
import pytest
from unittest.mock import Mock, patch

class TestDataProcessor:
    
    def test_process_batch_with_valid_data(self):
        """Test processing with valid data returns expected results."""
        processor = DataProcessor(config=Mock())
        valid_data = [{"id": 1, "value": "test"}]
        
        result = processor.process_batch(valid_data)
        
        assert result.success is True
        assert len(result.processed_items) == 1
        assert result.error_count == 0
    
    def test_process_batch_handles_validation_errors(self):
        """Test that validation errors are properly handled."""
        processor = DataProcessor(config=Mock())
        invalid_data = [{"id": None, "value": ""}]
        
        with pytest.raises(ValidationError) as exc_info:
            processor.process_batch(invalid_data)
        
        assert "Invalid data format" in str(exc_info.value)
```

### Integration Testing

Such as in scenarios where you need to test complete workflows:

```python
def test_complete_data_pipeline():
    """Test the entire data processing pipeline."""
    # Setup test data
    test_data = create_test_dataset()
    
    # Run pipeline
    pipeline = DataPipeline(config=test_config)
    result = pipeline.run(test_data)
    
    # Verify results
    assert result.status == "completed"
    assert result.processed_count == len(test_data)
```

## Performance Optimization

### Database Optimization

When you encounter performance issues with database queries:

```sql
-- Optimize queries with proper indexing
CREATE INDEX idx_user_actions_timestamp 
ON user_actions(user_id, timestamp DESC);

-- Use efficient query patterns
SELECT u.id, u.name, COUNT(a.id) as action_count
FROM users u
LEFT JOIN user_actions a ON u.id = a.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(a.id) > 10;
```

### Caching Strategies

In real-world applications, implement strategic caching:

```python
from functools import lru_cache
import redis

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    @lru_cache(maxsize=1000)
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences with memory caching."""
        cache_key = f"user_prefs:{user_id}"
        
        # Try Redis cache first
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # Fetch from database and cache
        preferences = self._fetch_from_database(user_id)
        self.redis_client.setex(cache_key, 3600, json.dumps(preferences))
        
        return preferences
```

## Security Best Practices

### Input Validation

Always validate and sanitize user input:

```python
from typing import Optional
import re

def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    return sanitized.strip()
```

### Authentication and Authorization

```python
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def hash_password(self, password: str) -> str:
        """Hash password securely."""
        return generate_password_hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return check_password_hash(password_hash, password)
    
    def generate_token(self, user_id: int) -> str:
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
```

## Deployment and DevOps

### Containerization

Use Docker for consistent deployments:

```dockerfile
# Multi-stage build for optimized images
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim as runtime

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:application"]
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Monitoring and Observability

### Logging Best Practices

```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def process_user_request(user_id: int, request_data: Dict):
    """Process user request with comprehensive logging."""
    logger.info(
        "Processing user request",
        user_id=user_id,
        request_type=request_data.get('type'),
        timestamp=datetime.utcnow().isoformat()
    )
    
    try:
        result = perform_processing(request_data)
        logger.info(
            "Request processed successfully",
            user_id=user_id,
            processing_time=result.processing_time,
            result_count=len(result.items)
        )
        return result
    except Exception as e:
        logger.error(
            "Request processing failed",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

## Conclusion

This comprehensive guide provides a solid foundation for modern software development practices. By following these guidelines and continuously learning from the community, you'll be well-equipped to build high-quality, maintainable software that meets both current needs and future requirements.

Remember that software development is an iterative process. Start with these fundamentals, apply them consistently, and gradually incorporate more advanced techniques as your projects and team grow.

### Additional Resources

- [Clean Code by Robert C. Martin](https://example.com/clean-code)
- [The Pragmatic Programmer](https://example.com/pragmatic-programmer)
- [Effective Python by Brett Slatkin](https://example.com/effective-python)
- [Building Microservices by Sam Newman](https://example.com/microservices)

### Contributing

If you have suggestions for improving this guide or want to contribute additional examples, please follow our [contribution guidelines](CONTRIBUTING.md) and submit a pull request.
''',
                "expected_score_range": (0.85, 1.0),
                "expected_level": QualityLevel.EXCELLENT
            },
            
            # Poor quality context
            {
                "filename": "poor-context.md",
                "content": '''Basic tips:
- Do stuff
- Test stuff
- Deploy stuff

That's it.''',
                "expected_score_range": (0.0, 0.39),
                "expected_level": QualityLevel.POOR
            }
        ]
        
        for context_test in test_contexts:
            # Create the context file
            context_file = temp_examples_dir / "contexts" / "domains" / context_test["filename"]
            with open(context_file, 'w') as f:
                f.write(context_test["content"])
            
            # Assess quality
            report = quality_checker.assess_template_quality(context_file)
            
            # Verify quality assessment
            assert report.template_type == "context"
            assert context_test["expected_score_range"][0] <= report.overall_score <= context_test["expected_score_range"][1], \
                f"Score {report.overall_score} not in expected range {context_test['expected_score_range']} for {context_test['filename']}"
            assert report.overall_level == context_test["expected_level"], \
                f"Expected level {context_test['expected_level']}, got {report.overall_level} for {context_test['filename']}"
    
    def test_comprehensive_quality_assessment_hooks(self, quality_checker, temp_examples_dir):
        """Test comprehensive quality assessment for various hook templates."""
        test_hooks = [
            # Excellent quality hook
            {
                "filename": "excellent-hook.yaml",
                "content": '''# Comprehensive Hook Template
# This hook demonstrates best practices for hook configuration
# with detailed documentation and proper structure

name: comprehensive-automation-hook
description: |
  A comprehensive automation hook that demonstrates best practices for
  hook configuration, documentation, and functionality. This hook provides
  intelligent context switching based on project type and user preferences,
  with robust error handling and performance optimization.

version: "2.1.0"
type: context
trigger: on_session_start
timeout: 45
enabled: true

# Metadata section with comprehensive information
metadata:
  name: comprehensive-automation-hook
  description: Comprehensive automation hook with intelligent context switching
  category: automation
  version: "2.1.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-15"
  tags: [automation, context-switching, intelligent, comprehensive]
  complexity: medium
  prerequisites: [basic-configuration, profile-setup]
  related_hooks: [context-enhancer, smart-suggestions]

# Hook configuration with detailed options
config:
  # Context switching configuration
  context_switching:
    enabled: true
    strategy: intelligent
    fallback_contexts: [general-guidance, basic-help]
  
  # Performance optimization settings
  performance:
    cache_enabled: true
    max_cache_size: 100
    cache_ttl: 3600
  
  # Error handling configuration
  error_handling:
    retry_attempts: 3
    retry_delay: 1000
    fallback_behavior: graceful_degradation
  
  # Logging and monitoring
  monitoring:
    log_level: info
    metrics_enabled: true
    performance_tracking: true

# Context sources and configuration
context:
  sources:
    - contexts/domains/development-guidelines.md
    - contexts/workflows/automation-patterns.md
    - contexts/integrations/tool-configurations.md
  
  tags: [development, automation, productivity]
  priority: 1
  
  # Dynamic context loading rules
  rules:
    - condition: "project_type == 'machine-learning'"
      additional_contexts:
        - contexts/domains/ml-best-practices.md
        - contexts/workflows/data-pipeline.md
    
    - condition: "user_role == 'data-scientist'"
      additional_contexts:
        - contexts/domains/data-analysis.md
        - contexts/tools/jupyter-notebooks.md

# Conditional execution rules
conditions:
  - profile: [data-scientist, ml-engineer, developer]
    project_type: [machine-learning, data-analysis, web-development]
  
  - user_preferences:
      automation_level: [medium, high]
      context_switching: enabled

# Hook execution script (optional)
script:
  language: python
  inline: |
    import logging
    from typing import Dict, List, Any
    
    def execute_hook(context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the comprehensive automation hook.
        
        Args:
            context: Hook execution context
            
        Returns:
            Execution result with status and data
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Intelligent context selection
            selected_contexts = select_contexts(context)
            
            # Load and process contexts
            processed_contexts = process_contexts(selected_contexts)
            
            # Apply optimizations
            optimized_result = optimize_contexts(processed_contexts)
            
            logger.info(f"Hook executed successfully, loaded {len(optimized_result)} contexts")
            
            return {
                "status": "success",
                "contexts_loaded": len(optimized_result),
                "execution_time": context.get("execution_time", 0),
                "cache_hits": context.get("cache_hits", 0)
            }
            
        except Exception as e:
            logger.error(f"Hook execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_applied": True
            }
    
    def select_contexts(context: Dict[str, Any]) -> List[str]:
        """Intelligently select contexts based on current situation."""
        # Implementation would go here
        return []
    
    def process_contexts(contexts: List[str]) -> List[Dict]:
        """Process and validate selected contexts."""
        # Implementation would go here
        return []
    
    def optimize_contexts(contexts: List[Dict]) -> List[Dict]:
        """Apply performance optimizations to contexts."""
        # Implementation would go here
        return contexts
''',
                "expected_score_range": (0.85, 1.0),
                "expected_level": QualityLevel.EXCELLENT
            },
            
            # Poor quality hook
            {
                "filename": "poor-hook.yaml",
                "content": '''name: bad
trigger: invalid_trigger
timeout: 500''',
                "expected_score_range": (0.0, 0.39),
                "expected_level": QualityLevel.POOR
            }
        ]
        
        for hook_test in test_hooks:
            # Create the hook file
            hook_file = temp_examples_dir / "hooks" / "automation" / hook_test["filename"]
            with open(hook_file, 'w') as f:
                f.write(hook_test["content"])
            
            # Assess quality
            report = quality_checker.assess_template_quality(hook_file)
            
            # Verify quality assessment
            assert report.template_type == "hook"
            assert hook_test["expected_score_range"][0] <= report.overall_score <= hook_test["expected_score_range"][1], \
                f"Score {report.overall_score} not in expected range {hook_test['expected_score_range']} for {hook_test['filename']}"
            assert report.overall_level == hook_test["expected_level"], \
                f"Expected level {hook_test['expected_level']}, got {report.overall_level} for {hook_test['filename']}"
    
    def test_quality_metric_edge_cases(self, quality_checker):
        """Test quality metric calculations with edge cases."""
        # Test score to level conversion edge cases
        edge_cases = [
            (0.0, QualityLevel.POOR),
            (0.59, QualityLevel.POOR),
            (0.6, QualityLevel.FAIR),
            (0.74, QualityLevel.FAIR),
            (0.75, QualityLevel.GOOD),
            (0.89, QualityLevel.GOOD),
            (0.9, QualityLevel.EXCELLENT),
            (1.0, QualityLevel.EXCELLENT),
        ]
        
        for score, expected_level in edge_cases:
            result_level = quality_checker._score_to_level(score)
            assert result_level == expected_level, f"Score {score} should map to {expected_level}, got {result_level}"
    
    def test_metadata_completeness_comprehensive(self, quality_checker):
        """Test metadata completeness assessment with various scenarios."""
        test_cases = [
            # Perfect metadata
            {
                "metadata": {
                    "name": "perfect-template",
                    "description": "A comprehensive template with all metadata fields properly filled",
                    "category": "professional",
                    "complexity": "medium",
                    "created": "2024-01-01",
                    "version": "2.1.0",
                    "author": "AI Configurator Team",
                    "updated": "2024-02-15",
                    "tags": ["comprehensive", "example", "best-practices"],
                    "prerequisites": ["basic-knowledge", "tool-setup"],
                    "related_templates": ["related-template-1", "related-template-2"]
                },
                "expected_score": 1.0
            },
            # Minimal required metadata
            {
                "metadata": {
                    "name": "minimal-template",
                    "description": "Minimal template with only required fields",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01"
                },
                "expected_score": 0.7  # Only required fields
            },
            # Empty metadata
            {
                "metadata": {},
                "expected_score": 0.0
            },
            # Partial metadata with some optional fields
            {
                "metadata": {
                    "name": "partial-template",
                    "description": "Template with some fields missing",
                    "category": "basic",
                    "complexity": "low",
                    "created": "2024-01-01",
                    "tags": ["partial", "example"],
                    "version": "1.0.0"
                },
                "expected_score_range": (0.7, 0.85)  # Required + some optional
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            json_data = {"metadata": test_case["metadata"]}
            metric = quality_checker._assess_metadata_completeness(json_data)
            
            if "expected_score" in test_case:
                assert abs(metric.score - test_case["expected_score"]) < 0.01, \
                    f"Test case {i}: expected score {test_case['expected_score']}, got {metric.score}"
            elif "expected_score_range" in test_case:
                min_score, max_score = test_case["expected_score_range"]
                assert min_score <= metric.score <= max_score, \
                    f"Test case {i}: score {metric.score} not in range {test_case['expected_score_range']}"
            
            # Verify suggestions are provided for incomplete metadata
            if metric.score < 1.0:
                assert len(metric.suggestions) > 0, f"Test case {i}: should have suggestions for incomplete metadata"
    
    def test_quality_summary_generation(self, quality_checker):
        """Test comprehensive quality summary generation."""
        # Create mock quality reports with various quality levels
        mock_reports = [
            QualityReport(
                file_path="excellent1.json",
                template_type="profile",
                overall_score=0.95,
                overall_level=QualityLevel.EXCELLENT,
                metrics=[],
                documentation_completeness=0.9,
                example_accuracy=0.95,
                best_practices_compliance=1.0,
                suggestions=["Minor improvement suggestion"]
            ),
            QualityReport(
                file_path="excellent2.md",
                template_type="context",
                overall_score=0.92,
                overall_level=QualityLevel.EXCELLENT,
                metrics=[],
                documentation_completeness=0.95,
                example_accuracy=0.9,
                best_practices_compliance=0.9,
                suggestions=[]
            ),
            QualityReport(
                file_path="good1.yaml",
                template_type="hook",
                overall_score=0.8,
                overall_level=QualityLevel.GOOD,
                metrics=[],
                documentation_completeness=0.75,
                example_accuracy=0.8,
                best_practices_compliance=0.85,
                suggestions=["Add more documentation", "Include examples"]
            ),
            QualityReport(
                file_path="fair1.json",
                template_type="profile",
                overall_score=0.65,
                overall_level=QualityLevel.FAIR,
                metrics=[],
                documentation_completeness=0.6,
                example_accuracy=0.7,
                best_practices_compliance=0.65,
                suggestions=["Improve documentation", "Add examples", "Follow naming conventions"]
            ),
            QualityReport(
                file_path="poor1.md",
                template_type="context",
                overall_score=0.3,
                overall_level=QualityLevel.POOR,
                metrics=[],
                documentation_completeness=0.2,
                example_accuracy=0.3,
                best_practices_compliance=0.4,
                suggestions=["Major improvements needed", "Add comprehensive content", "Include code examples", "Improve structure"]
            )
        ]
        
        summary = quality_checker.generate_quality_summary(mock_reports)
        
        # Verify summary structure
        assert "total_templates" in summary
        assert "average_score" in summary
        assert "quality_distribution" in summary
        assert "template_types" in summary
        assert "common_issues" in summary
        assert "best_template" in summary
        assert "worst_template" in summary
        assert "recommendations" in summary
        
        # Verify calculations
        assert summary["total_templates"] == 5
        expected_avg = sum(r.overall_score for r in mock_reports) / len(mock_reports)
        assert abs(summary["average_score"] - expected_avg) < 0.01
        
        # Verify quality distribution
        distribution = summary["quality_distribution"]
        assert distribution[QualityLevel.EXCELLENT.value] == 2
        assert distribution[QualityLevel.GOOD.value] == 1
        assert distribution[QualityLevel.FAIR.value] == 1
        assert distribution[QualityLevel.POOR.value] == 1
        
        # Verify template type distribution
        type_dist = summary["template_types"]
        assert type_dist["profile"] == 2
        assert type_dist["context"] == 2
        assert type_dist["hook"] == 1
        
        # Verify best and worst templates
        assert summary["best_template"]["file_path"] == "excellent1.json"
        assert summary["worst_template"]["file_path"] == "poor1.md"
        
        # Verify common issues identification
        assert len(summary["common_issues"]) > 0
        
        # Verify recommendations
        assert len(summary["recommendations"]) > 0
    
    def test_quality_assessment_error_handling(self, quality_checker, temp_examples_dir):
        """Test quality assessment error handling for problematic files."""
        problematic_files = [
            # Binary file with template extension
            ("binary.json", b"\x00\x01\x02\x03"),
            # File with encoding issues
            ("encoding.md", "# Test\n\xff\xfe Invalid UTF-8"),
            # Empty file
            ("empty.yaml", ""),
            # File with null bytes
            ("null.json", '{"name": "test\x00null"}'),
        ]
        
        for filename, content in problematic_files:
            file_path = temp_examples_dir / "profiles" / "basic" / filename
            
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                try:
                    file_path.write_text(content, encoding='utf-8')
                except UnicodeEncodeError:
                    file_path.write_bytes(content.encode('utf-8', errors='ignore'))
            
            # Quality checker should handle these gracefully
            try:
                report = quality_checker.assess_template_quality(file_path)
                # Should return a report, possibly with poor quality
                assert isinstance(report, QualityReport)
                # Problematic files should typically get poor scores
                assert report.overall_level in [QualityLevel.POOR, QualityLevel.FAIR]
            except Exception as e:
                pytest.fail(f"Quality checker should handle {filename} gracefully, but raised: {e}")
    
    def test_performance_with_large_templates(self, quality_checker, temp_examples_dir):
        """Test quality assessment performance with large templates."""
        # Create a very large context template
        large_content = """# Large Context Template

## Overview

This is a very large context template designed to test performance.
""" + "\n\n".join([f"""
## Section {i}

This is section {i} with substantial content to make the template large.
It includes multiple paragraphs, code examples, and detailed explanations.

### Subsection {i}.1

More content for subsection {i}.1 with detailed information.

```python
def function_{i}():
    \"\"\"Function {i} documentation.\"\"\"
    return f"Result from function {i}"
```

### Subsection {i}.2

Additional content for subsection {i}.2 with examples and explanations.

For instance, when you need to implement feature {i}, consider these approaches:
- Approach 1 for feature {i}
- Approach 2 for feature {i}
- Approach 3 for feature {i}

Such as in scenarios where feature {i} is critical for performance.
""" for i in range(100)])  # Create 100 sections
        
        large_file = temp_examples_dir / "contexts" / "domains" / "large-context.md"
        large_file.write_text(large_content)
        
        # Measure assessment time
        import time
        start_time = time.time()
        
        report = quality_checker.assess_template_quality(large_file)
        
        end_time = time.time()
        assessment_time = end_time - start_time
        
        # Assessment should complete within reasonable time
        assert assessment_time < 10, f"Quality assessment took too long: {assessment_time} seconds"
        
        # Large, well-structured template should get good quality score
        assert report.overall_score > 0.7, f"Large template should get good score, got {report.overall_score}"
        assert report.template_type == "context"
    
    def test_quality_trends_analysis(self, quality_checker):
        """Test quality trends analysis across multiple assessments."""
        # Simulate multiple assessment runs with improving quality
        assessment_runs = [
            # Run 1: Initial poor quality
            [
                QualityReport("template1.json", "profile", 0.3, QualityLevel.POOR, [], 0.2, 0.3, 0.4, ["Many issues"]),
                QualityReport("template2.md", "context", 0.4, QualityLevel.POOR, [], 0.3, 0.4, 0.5, ["Several issues"]),
            ],
            # Run 2: Some improvements
            [
                QualityReport("template1.json", "profile", 0.6, QualityLevel.FAIR, [], 0.5, 0.6, 0.7, ["Some issues"]),
                QualityReport("template2.md", "context", 0.7, QualityLevel.GOOD, [], 0.6, 0.7, 0.8, ["Minor issues"]),
            ],
            # Run 3: Good quality achieved
            [
                QualityReport("template1.json", "profile", 0.85, QualityLevel.GOOD, [], 0.8, 0.85, 0.9, ["Few issues"]),
                QualityReport("template2.md", "context", 0.92, QualityLevel.EXCELLENT, [], 0.9, 0.92, 0.94, []),
            ]
        ]
        
        # Analyze trends
        trends = []
        for run in assessment_runs:
            summary = quality_checker.generate_quality_summary(run)
            trends.append({
                "average_score": summary["average_score"],
                "excellent_count": summary["quality_distribution"].get(QualityLevel.EXCELLENT.value, 0),
                "poor_count": summary["quality_distribution"].get(QualityLevel.POOR.value, 0)
            })
        
        # Verify improving trends
        assert trends[0]["average_score"] < trends[1]["average_score"] < trends[2]["average_score"]
        assert trends[0]["poor_count"] > trends[1]["poor_count"] > trends[2]["poor_count"]
        assert trends[0]["excellent_count"] < trends[2]["excellent_count"]