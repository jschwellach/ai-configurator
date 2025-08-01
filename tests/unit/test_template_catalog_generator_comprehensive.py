"""Comprehensive unit tests for template catalog generator functionality."""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from src.ai_configurator.core.template_catalog_generator import (
    TemplateCatalogGenerator,
    TemplateMetadata,
    TemplateCatalog
)


class TestTemplateCatalogGeneratorComprehensive:
    """Comprehensive tests for template catalog generator functionality."""
    
    @pytest.fixture
    def temp_examples_dir(self):
        """Create comprehensive temporary examples directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            examples_dir = Path(temp_dir) / "examples"
            
            # Create comprehensive directory structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "profiles" / "advanced").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "contexts" / "integrations").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "hooks" / "enhancement").mkdir(parents=True)
            (examples_dir / "hooks" / "integration").mkdir(parents=True)
            (examples_dir / "workflows" / "complete-setup").mkdir(parents=True)
            (examples_dir / "workflows" / "content-creation").mkdir(parents=True)
            
            yield examples_dir
    
    @pytest.fixture
    def catalog_generator(self, temp_examples_dir):
        """Create catalog generator with test directory."""
        return TemplateCatalogGenerator(str(temp_examples_dir))
    
    @pytest.fixture
    def comprehensive_templates(self, temp_examples_dir):
        """Create comprehensive set of test templates."""
        # Create profile templates
        profiles = [
            {
                "path": "profiles/basic/minimal.json",
                "content": '''
                {
                    // Minimal Profile Example
                    "metadata": {
                        "name": "minimal-profile",
                        "description": "A minimal profile template for basic usage scenarios. Perfect for getting started with the AI Configurator system.",
                        "category": "basic",
                        "version": "1.0.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "updated": "2024-01-15",
                        "tags": ["basic", "minimal", "starter"],
                        "complexity": "low",
                        "prerequisites": [],
                        "related_templates": ["basic-context", "getting-started"]
                    },
                    "paths": ["contexts/domains/basic-guidelines.md"],
                    "hooks": {},
                    "settings": {"auto_reload": true}
                }
                '''
            },
            {
                "path": "profiles/professional/data-scientist.json",
                "content": '''
                {
                    // Data Scientist Profile
                    "metadata": {
                        "name": "data-scientist-profile",
                        "description": "Comprehensive profile for data science workflows including ML pipelines, data analysis, and model deployment best practices.",
                        "category": "professional",
                        "version": "2.1.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "updated": "2024-02-15",
                        "tags": ["data-science", "machine-learning", "analytics", "python"],
                        "complexity": "high",
                        "prerequisites": ["python-knowledge", "statistics-background"],
                        "related_templates": ["ml-engineer", "data-analyst", "python-developer"]
                    },
                    "paths": [
                        "contexts/domains/data-science-best-practices.md",
                        "contexts/workflows/ml-pipeline.md",
                        "contexts/integrations/jupyter-notebooks.md"
                    ],
                    "hooks": {
                        "auto-documentation": {"enabled": true},
                        "data-validation": {"enabled": true}
                    },
                    "settings": {
                        "auto_reload": true,
                        "max_contexts": 100,
                        "validation_level": "strict"
                    }
                }
                '''
            },
            {
                "path": "profiles/advanced/architect.json",
                "content": '''
                {
                    // Solutions Architect Profile
                    "metadata": {
                        "name": "solutions-architect-profile",
                        "description": "Advanced profile for solutions architects managing complex system designs, cloud architectures, and enterprise integrations.",
                        "category": "advanced",
                        "version": "3.0.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "updated": "2024-03-01",
                        "tags": ["architecture", "cloud", "enterprise", "design-patterns"],
                        "complexity": "high",
                        "prerequisites": ["system-design-knowledge", "cloud-experience", "enterprise-patterns"],
                        "related_templates": ["cloud-architect", "enterprise-developer", "devops-engineer"]
                    },
                    "paths": [
                        "contexts/domains/system-architecture.md",
                        "contexts/workflows/design-review-process.md",
                        "contexts/integrations/cloud-patterns.md"
                    ],
                    "hooks": {
                        "architecture-review": {"enabled": true},
                        "compliance-check": {"enabled": true},
                        "documentation-generator": {"enabled": true}
                    },
                    "settings": {
                        "auto_reload": true,
                        "max_contexts": 200,
                        "validation_level": "enterprise",
                        "security_mode": "strict"
                    }
                }
                '''
            }
        ]
        
        # Create context templates
        contexts = [
            {
                "path": "contexts/domains/data-science-best-practices.md",
                "content": '''---
name: data-science-best-practices
description: Comprehensive data science best practices and methodologies
tags: [data-science, machine-learning, best-practices, python]
categories: [data-science, development]
version: "2.0.0"
author: "AI Configurator Team"
created: "2024-01-01"
updated: "2024-02-15"
---

# Data Science Best Practices

## Overview

This comprehensive guide covers essential best practices for data science projects, from initial data exploration to model deployment and monitoring. It provides practical guidance for data scientists, ML engineers, and analysts working on machine learning projects.

## Data Management

### Data Collection and Validation

Ensure data quality through systematic validation:

```python
import pandas as pd
from typing import Dict, Any, List

def validate_data_schema(df: pd.DataFrame, schema: Dict[str, Any]) -> bool:
    """Validate dataframe against expected schema."""
    for column, expected_type in schema.items():
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")
        if not df[column].dtype == expected_type:
            raise ValueError(f"Column {column} has wrong type: {df[column].dtype}")
    return True

def detect_data_drift(current_data: pd.DataFrame, reference_data: pd.DataFrame) -> Dict[str, float]:
    """Detect statistical drift between datasets."""
    drift_scores = {}
    for column in current_data.select_dtypes(include=[np.number]).columns:
        # Calculate KS statistic for numerical columns
        ks_stat, p_value = stats.ks_2samp(reference_data[column], current_data[column])
        drift_scores[column] = ks_stat
    return drift_scores
```

## Model Development

### Feature Engineering

For instance, when creating features for time series data:

```python
def create_time_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """Create time-based features from datetime column."""
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Extract time components
    df['year'] = df[date_column].dt.year
    df['month'] = df[date_column].dt.month
    df['day_of_week'] = df[date_column].dt.dayofweek
    df['hour'] = df[date_column].dt.hour
    
    # Create cyclical features
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df
```

### Model Validation

Such as in cross-validation scenarios with time series data:

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error

def time_series_cv_score(model, X, y, n_splits=5):
    """Perform time series cross-validation."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []
    
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        
        score = mean_squared_error(y_val, y_pred)
        scores.append(score)
    
    return np.array(scores)
```

## Deployment and Monitoring

In real-world applications, implement comprehensive monitoring:

```python
import mlflow
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

class ModelMonitor:
    def __init__(self, model_name: str, reference_data: pd.DataFrame):
        self.model_name = model_name
        self.reference_data = reference_data
        
    def log_prediction(self, features: Dict, prediction: float, actual: float = None):
        """Log prediction for monitoring."""
        with mlflow.start_run():
            mlflow.log_params(features)
            mlflow.log_metric("prediction", prediction)
            if actual is not None:
                mlflow.log_metric("actual", actual)
                mlflow.log_metric("error", abs(prediction - actual))
    
    def generate_drift_report(self, current_data: pd.DataFrame) -> str:
        """Generate data drift report."""
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=self.reference_data, current_data=current_data)
        return report.json()
```

## Conclusion

Following these data science best practices ensures robust, reliable, and maintainable machine learning systems that can adapt to changing data and business requirements.
'''
            },
            {
                "path": "contexts/workflows/code-review-process.md",
                "content": '''# Code Review Process

## Overview

This context defines a comprehensive code review process that ensures code quality, knowledge sharing, and team collaboration. It covers review guidelines, checklists, and best practices for both reviewers and authors.

## Review Guidelines

### For Authors

1. **Self-Review First**: Review your own code before submitting
2. **Clear Description**: Provide context and reasoning for changes
3. **Small Changes**: Keep pull requests focused and manageable
4. **Tests Included**: Ensure adequate test coverage

### For Reviewers

1. **Timely Reviews**: Respond within 24 hours
2. **Constructive Feedback**: Focus on code, not the person
3. **Ask Questions**: Seek to understand the reasoning
4. **Suggest Improvements**: Provide actionable feedback

## Review Checklist

- [ ] Code follows style guidelines
- [ ] Logic is clear and well-documented
- [ ] Error handling is appropriate
- [ ] Tests cover new functionality
- [ ] Performance considerations addressed
- [ ] Security implications reviewed

## Best Practices

For instance, when reviewing complex algorithms:
- Verify edge cases are handled
- Check for potential performance bottlenecks
- Ensure algorithm correctness

Such as in scenarios involving database queries:
- Review for SQL injection vulnerabilities
- Check query performance and indexing
- Verify transaction handling
'''
            },
            {
                "path": "contexts/integrations/cloud-patterns.md",
                "content": '''# Cloud Architecture Patterns

## Overview

This context provides guidance on common cloud architecture patterns, best practices for cloud-native applications, and integration strategies for multi-cloud environments.

## Common Patterns

### Microservices Architecture

```yaml
# docker-compose.yml example
version: '3.8'
services:
  api-gateway:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - user-service
      - order-service
  
  user-service:
    build: ./user-service
    environment:
      - DATABASE_URL=postgresql://user:pass@user-db:5432/users
    depends_on:
      - user-db
  
  order-service:
    build: ./order-service
    environment:
      - DATABASE_URL=postgresql://user:pass@order-db:5432/orders
    depends_on:
      - order-db
```

### Event-Driven Architecture

For instance, when implementing event sourcing:

```python
from dataclasses import dataclass
from typing import List, Any
import json

@dataclass
class Event:
    event_type: str
    aggregate_id: str
    data: dict
    timestamp: str
    version: int

class EventStore:
    def __init__(self):
        self.events: List[Event] = []
    
    def append_event(self, event: Event):
        """Append event to the event store."""
        self.events.append(event)
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for an aggregate."""
        return [e for e in self.events if e.aggregate_id == aggregate_id]
```

## Best Practices

Such as in multi-cloud scenarios:
- Use cloud-agnostic services where possible
- Implement proper data replication strategies
- Design for failure and recovery
'''
            }
        ]
        
        # Create hook templates
        hooks = [
            {
                "path": "hooks/automation/auto-documentation.yaml",
                "content": '''name: auto-documentation
description: Automatically generate comprehensive documentation from code comments, docstrings, and type hints
version: "2.0.0"
type: script
trigger: on_file_save
timeout: 120
enabled: true

metadata:
  name: auto-documentation
  description: Intelligent documentation generation with support for multiple programming languages and formats
  category: automation
  version: "2.0.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-20"
  tags: [automation, documentation, code-analysis, multi-language]
  complexity: medium
  prerequisites: [python-environment, documentation-tools]
  related_hooks: [code-quality-check, api-documentation]

config:
  # Documentation formats to generate
  output_formats: [markdown, html, pdf, rst]
  
  # Language-specific settings
  languages:
    python:
      docstring_style: google
      include_private: false
      type_hints: true
    javascript:
      jsdoc_style: true
      include_examples: true
    typescript:
      generate_interfaces: true
      include_generics: true
  
  # Content configuration
  content:
    include_examples: true
    generate_api_docs: true
    create_tutorials: true
    update_readme: true
    include_changelog: true
  
  # Quality settings
  quality:
    min_docstring_coverage: 80
    require_examples: true
    validate_links: true

# Script configuration
script:
  language: python
  file: auto_documentation.py
  
# Execution conditions
conditions:
  - file_types: [".py", ".js", ".ts", ".java", ".cpp", ".h"]
    project_types: [library, application, framework]
    min_file_size: 100  # bytes
  
  - documentation_coverage: 
      below: 90  # Trigger when coverage drops below 90%
'''
            },
            {
                "path": "hooks/enhancement/smart-suggestions.yaml",
                "content": '''name: smart-suggestions
description: Provide AI-powered code suggestions, improvements, and best practice recommendations based on context analysis
version: "3.0.0"
type: context
trigger: per_user_message
timeout: 45
enabled: true

metadata:
  name: smart-suggestions
  description: Advanced AI-powered code analysis and suggestion system with context-aware recommendations
  category: enhancement
  version: "3.0.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-03-01"
  tags: [ai, suggestions, code-improvement, context-aware, machine-learning]
  complexity: high
  prerequisites: [ai-model-access, code-analysis-tools]
  related_hooks: [context-switcher, code-quality-check]

config:
  # AI model configuration
  ai_model:
    provider: openai
    model: gpt-4
    temperature: 0.3
    max_tokens: 1000
  
  # Suggestion types and priorities
  suggestion_types:
    code_improvement:
      enabled: true
      priority: high
      categories: [performance, readability, maintainability]
    
    best_practices:
      enabled: true
      priority: medium
      categories: [security, testing, documentation]
    
    refactoring:
      enabled: true
      priority: low
      categories: [design-patterns, code-smells, architecture]
  
  # Quality thresholds
  thresholds:
    confidence_minimum: 0.8
    relevance_score: 0.7
    max_suggestions_per_request: 5
  
  # Context analysis
  context_analysis:
    code_complexity: true
    dependency_analysis: true
    pattern_recognition: true
    historical_changes: true

# Context sources for intelligent suggestions
context:
  sources:
    - contexts/domains/data-science-best-practices.md
    - contexts/workflows/code-review-process.md
    - contexts/integrations/testing-strategies.md
  
  dynamic_loading:
    enabled: true
    based_on: [file_type, project_structure, user_history]
  
  tags: [suggestions, improvement, ai-powered]
  priority: 2

# Advanced conditions for suggestion triggering
conditions:
  - user_preferences:
      suggestions_enabled: true
      ai_assistance: [medium, high]
      suggestion_frequency: [real-time, on-demand]
  
  - code_context:
      complexity_score: 
        above: 5  # Trigger for complex code
      test_coverage:
        below: 80  # Suggest when coverage is low
      code_smells:
        detected: true
  
  - project_context:
      project_size: [medium, large]
      team_size: 
        above: 2  # Multi-developer projects
      development_stage: [active, maintenance]
'''
            },
            {
                "path": "hooks/integration/git-workflow.yaml",
                "content": '''name: git-workflow-integration
description: Integrate with Git workflows to provide context-aware assistance during development lifecycle
version: "1.8.0"
type: hybrid
trigger: on_file_change
timeout: 30
enabled: true

metadata:
  name: git-workflow-integration
  description: Comprehensive Git workflow integration with branch management, commit analysis, and merge assistance
  category: integration
  version: "1.8.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-10"
  tags: [git, workflow, integration, version-control]
  complexity: medium
  prerequisites: [git-repository, branch-permissions]
  related_hooks: [code-quality-check, auto-documentation]

config:
  # Git integration settings
  git:
    auto_fetch: true
    branch_protection: true
    commit_message_validation: true
    merge_conflict_assistance: true
  
  # Workflow stages
  workflows:
    feature_development:
      branch_pattern: "feature/*"
      required_checks: [tests, linting, documentation]
      auto_rebase: false
    
    hotfix:
      branch_pattern: "hotfix/*"
      fast_track: true
      required_approvals: 2
    
    release:
      branch_pattern: "release/*"
      changelog_generation: true
      version_tagging: true

# Context and script combination
context:
  sources:
    - contexts/workflows/git-best-practices.md
    - contexts/integrations/ci-cd-patterns.md
  tags: [git, workflow]

script:
  language: python
  inline: |
    import subprocess
    import re
    from typing import Dict, List

    def analyze_git_status() -> Dict[str, any]:
        """Analyze current Git repository status."""
        try:
            # Get current branch
            branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
            
            # Get uncommitted changes
            status = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
            
            # Get recent commits
            log = subprocess.check_output(['git', 'log', '--oneline', '-10'], text=True)
            
            return {
                'current_branch': branch,
                'uncommitted_changes': len(status.strip().split('\n')) if status.strip() else 0,
                'recent_commits': log.strip().split('\n'),
                'workflow_stage': determine_workflow_stage(branch)
            }
        except subprocess.CalledProcessError:
            return {'error': 'Not a Git repository or Git not available'}

    def determine_workflow_stage(branch: str) -> str:
        """Determine workflow stage based on branch name."""
        if branch.startswith('feature/'):
            return 'feature_development'
        elif branch.startswith('hotfix/'):
            return 'hotfix'
        elif branch.startswith('release/'):
            return 'release'
        elif branch in ['main', 'master', 'develop']:
            return 'main_branch'
        else:
            return 'unknown'

conditions:
  - git_repository: true
    file_types: [".py", ".js", ".ts", ".java", ".cpp", ".md"]
  
  - branch_patterns: ["feature/*", "hotfix/*", "release/*"]
    has_uncommitted_changes: true
'''
            }
        ]
        
        # Create workflow templates
        workflows = [
            {
                "path": "workflows/complete-setup",
                "files": {
                    "README.md": '''# Complete Development Setup Workflow

This workflow provides a comprehensive development environment setup that includes:

- Development tools and dependencies
- Code quality and testing frameworks  
- Documentation generation
- CI/CD pipeline configuration
- Monitoring and logging setup

## Features

- **Automated Environment Setup**: One-command setup for all development tools
- **Quality Assurance**: Integrated linting, testing, and code quality checks
- **Documentation**: Automatic API documentation and README generation
- **CI/CD Integration**: Pre-configured pipelines for popular CI/CD platforms
- **Monitoring**: Built-in logging and performance monitoring

## Usage

1. Install the workflow profile
2. Run the environment setup hook
3. Configure your project-specific settings
4. Start developing with full toolchain support

## Customization

The workflow can be customized for different technology stacks:
- Python/Django projects
- Node.js/React applications  
- Java/Spring Boot services
- Go microservices
- Docker containerized applications
''',
                    "profile.json": {
                        "metadata": {
                            "name": "complete-development-setup",
                            "description": "Comprehensive development environment setup workflow with automated tooling, quality checks, and CI/CD integration",
                            "category": "workflow",
                            "version": "2.5.0",
                            "author": "AI Configurator Team",
                            "created": "2024-01-01",
                            "updated": "2024-03-01",
                            "tags": ["workflow", "setup", "development", "automation", "ci-cd"],
                            "complexity": "high",
                            "prerequisites": ["docker", "git", "package-manager"],
                            "related_templates": ["devops-engineer", "full-stack-developer"]
                        },
                        "paths": [
                            "contexts/workflows/development-setup.md",
                            "contexts/integrations/ci-cd-patterns.md",
                            "contexts/domains/testing-strategies.md"
                        ],
                        "hooks": {
                            "environment-setup": {"enabled": True, "priority": 1},
                            "dependency-installer": {"enabled": True, "priority": 2},
                            "quality-tools-setup": {"enabled": True, "priority": 3},
                            "ci-cd-generator": {"enabled": True, "priority": 4}
                        },
                        "settings": {
                            "auto_reload": True,
                            "setup_mode": "comprehensive",
                            "validation_level": "strict",
                            "backup_configs": True
                        }
                    },
                    "contexts/development-setup.md": '''# Development Environment Setup

## Overview

Comprehensive guide for setting up a complete development environment with all necessary tools, configurations, and best practices.

## Prerequisites

- Git version control system
- Docker and Docker Compose
- Package manager (npm, pip, maven, etc.)
- Code editor or IDE

## Setup Steps

1. **Environment Validation**
2. **Tool Installation** 
3. **Configuration Setup**
4. **Quality Tools Integration**
5. **CI/CD Pipeline Setup**

## Supported Stacks

- **Frontend**: React, Vue, Angular
- **Backend**: Node.js, Python, Java, Go
- **Database**: PostgreSQL, MongoDB, Redis
- **Infrastructure**: Docker, Kubernetes, AWS
''',
                    "hooks/environment-setup.yaml": '''name: environment-setup
description: Automated development environment setup and configuration
version: "2.0.0"
type: script
trigger: manual
timeout: 300
enabled: true

config:
  setup_stages:
    - validate_prerequisites
    - install_dependencies  
    - configure_tools
    - setup_quality_checks
    - initialize_ci_cd

script:
  language: python
  file: environment_setup.py
'''
                }
            },
            {
                "path": "workflows/content-creation",
                "files": {
                    "README.md": '''# Content Creation Suite Workflow

A comprehensive workflow for content creators, technical writers, and documentation teams. Includes tools for writing, editing, publishing, and maintaining high-quality content.

## Features

- **Writing Tools**: Integrated editors with spell-check, grammar, and style assistance
- **Content Management**: Version control and collaboration tools for content
- **Publishing Pipeline**: Automated publishing to multiple platforms
- **SEO Optimization**: Built-in SEO analysis and optimization suggestions
- **Analytics Integration**: Content performance tracking and analytics

## Supported Content Types

- Technical documentation
- Blog posts and articles
- API documentation
- User guides and tutorials
- Marketing content
- Social media content

## Workflow Stages

1. **Content Planning**: Topic research and content strategy
2. **Writing**: Assisted writing with AI suggestions
3. **Review**: Collaborative editing and review process
4. **Publishing**: Multi-platform content distribution
5. **Analytics**: Performance monitoring and optimization
''',
                    "profile.json": {
                        "metadata": {
                            "name": "content-creation-suite",
                            "description": "Complete content creation workflow with writing assistance, collaboration tools, and multi-platform publishing capabilities",
                            "category": "workflow", 
                            "version": "1.8.0",
                            "author": "AI Configurator Team",
                            "created": "2024-01-01",
                            "updated": "2024-02-20",
                            "tags": ["content", "writing", "publishing", "collaboration", "seo"],
                            "complexity": "medium",
                            "prerequisites": ["writing-tools", "content-platforms"],
                            "related_templates": ["technical-writer", "content-manager"]
                        },
                        "paths": [
                            "contexts/domains/content-creation-guidelines.md",
                            "contexts/workflows/editorial-process.md",
                            "contexts/integrations/publishing-platforms.md"
                        ],
                        "hooks": {
                            "writing-assistant": {"enabled": True},
                            "grammar-checker": {"enabled": True},
                            "seo-optimizer": {"enabled": True},
                            "publishing-automation": {"enabled": True}
                        },
                        "settings": {
                            "auto_save": True,
                            "collaboration_mode": "real-time",
                            "ai_assistance": "enhanced",
                            "publishing_schedule": "automated"
                        }
                    }
                }
            }
        ]
        
        # Write all template files
        for profile in profiles:
            file_path = temp_examples_dir / profile["path"]
            with open(file_path, 'w') as f:
                f.write(profile["content"])
        
        for context in contexts:
            file_path = temp_examples_dir / context["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(context["content"])
        
        for hook in hooks:
            file_path = temp_examples_dir / hook["path"]
            with open(file_path, 'w') as f:
                f.write(hook["content"])
        
        for workflow in workflows:
            workflow_dir = temp_examples_dir / workflow["path"]
            for file_name, content in workflow["files"].items():
                file_path = workflow_dir / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                if isinstance(content, dict):
                    with open(file_path, 'w') as f:
                        json.dump(content, f, indent=2)
                else:
                    with open(file_path, 'w') as f:
                        f.write(content)
        
        return {
            "profiles": len(profiles),
            "contexts": len(contexts), 
            "hooks": len(hooks),
            "workflows": len(workflows)
        }
    
    def test_comprehensive_template_scanning(self, catalog_generator, comprehensive_templates):
        """Test comprehensive template scanning across all categories."""
        catalog = catalog_generator.generate_catalog()
        
        # Verify catalog structure
        assert isinstance(catalog, TemplateCatalog)
        assert len(catalog.profiles) == comprehensive_templates["profiles"]
        assert len(catalog.contexts) == comprehensive_templates["contexts"]
        assert len(catalog.hooks) == comprehensive_templates["hooks"]
        assert len(catalog.workflows) == comprehensive_templates["workflows"]
        
        # Verify total count
        expected_total = sum(comprehensive_templates.values())
        assert catalog.total_count == expected_total
        
        # Verify generated timestamp
        assert catalog.generated_at
        
        # Verify all templates have required metadata
        all_templates = catalog.profiles + catalog.contexts + catalog.hooks + catalog.workflows
        for template in all_templates:
            assert isinstance(template, TemplateMetadata)
            assert template.name
            assert template.description
            assert template.template_type
            assert template.file_path
    
    def test_profile_metadata_extraction(self, catalog_generator, comprehensive_templates):
        """Test comprehensive profile metadata extraction."""
        catalog = catalog_generator.generate_catalog()
        profiles = catalog.profiles
        
        # Find specific profiles to test
        minimal_profile = next((p for p in profiles if "minimal" in p.name.lower()), None)
        data_scientist_profile = next((p for p in profiles if "data-scientist" in p.name.lower()), None)
        architect_profile = next((p for p in profiles if "architect" in p.name.lower()), None)
        
        assert minimal_profile is not None
        assert data_scientist_profile is not None
        assert architect_profile is not None
        
        # Test minimal profile
        assert minimal_profile.category == "basic"
        assert minimal_profile.complexity == "low"
        assert minimal_profile.version == "1.0.0"
        assert "basic" in minimal_profile.tags
        assert "minimal" in minimal_profile.tags
        
        # Test data scientist profile
        assert data_scientist_profile.category == "professional"
        assert data_scientist_profile.complexity == "high"
        assert data_scientist_profile.version == "2.1.0"
        assert "data-science" in data_scientist_profile.tags
        assert "machine-learning" in data_scientist_profile.tags
        assert len(data_scientist_profile.prerequisites) > 0
        assert len(data_scientist_profile.related_templates) > 0
        
        # Test architect profile
        assert architect_profile.category == "advanced"
        assert architect_profile.complexity == "high"
        assert architect_profile.version == "3.0.0"
        assert "architecture" in architect_profile.tags
        assert "cloud" in architect_profile.tags
    
    def test_context_metadata_extraction(self, catalog_generator, comprehensive_templates):
        """Test comprehensive context metadata extraction."""
        catalog = catalog_generator.generate_catalog()
        contexts = catalog.contexts
        
        # Find specific contexts to test
        data_science_context = next((c for c in contexts if "data-science" in c.name.lower()), None)
        code_review_context = next((c for c in contexts if "code-review" in c.name.lower()), None)
        cloud_patterns_context = next((c for c in contexts if "cloud" in c.name.lower()), None)
        
        assert data_science_context is not None
        assert code_review_context is not None
        assert cloud_patterns_context is not None
        
        # Test data science context
        assert data_science_context.template_type == "context"
        assert "data-science" in data_science_context.tags
        assert "machine-learning" in data_science_context.tags
        assert data_science_context.complexity in ["medium", "high"]
        
        # Test code review context
        assert code_review_context.template_type == "context"
        assert len(code_review_context.description) > 50
        
        # Test cloud patterns context
        assert cloud_patterns_context.template_type == "context"
        assert "cloud" in cloud_patterns_context.name.lower()
    
    def test_hook_metadata_extraction(self, catalog_generator, comprehensive_templates):
        """Test comprehensive hook metadata extraction."""
        catalog = catalog_generator.generate_catalog()
        hooks = catalog.hooks
        
        # Find specific hooks to test
        auto_doc_hook = next((h for h in hooks if "auto-documentation" in h.name.lower()), None)
        smart_suggestions_hook = next((h for h in hooks if "smart-suggestions" in h.name.lower()), None)
        git_workflow_hook = next((h for h in hooks if "git-workflow" in h.name.lower()), None)
        
        assert auto_doc_hook is not None
        assert smart_suggestions_hook is not None
        assert git_workflow_hook is not None
        
        # Test auto-documentation hook
        assert auto_doc_hook.template_type == "hook"
        assert auto_doc_hook.version == "2.0.0"
        assert "automation" in auto_doc_hook.tags
        assert "documentation" in auto_doc_hook.tags
        assert auto_doc_hook.complexity == "medium"
        
        # Test smart suggestions hook
        assert smart_suggestions_hook.template_type == "hook"
        assert smart_suggestions_hook.version == "3.0.0"
        assert "ai" in smart_suggestions_hook.tags
        assert "suggestions" in smart_suggestions_hook.tags
        assert smart_suggestions_hook.complexity == "high"
        
        # Test git workflow hook
        assert git_workflow_hook.template_type == "hook"
        assert git_workflow_hook.version == "1.8.0"
        assert "git" in git_workflow_hook.tags
        assert "workflow" in git_workflow_hook.tags
    
    def test_workflow_metadata_extraction(self, catalog_generator, comprehensive_templates):
        """Test comprehensive workflow metadata extraction."""
        catalog = catalog_generator.generate_catalog()
        workflows = catalog.workflows
        
        # Find specific workflows to test
        complete_setup_workflow = next((w for w in workflows if "complete" in w.name.lower()), None)
        content_creation_workflow = next((w for w in workflows if "content" in w.name.lower()), None)
        
        assert complete_setup_workflow is not None
        assert content_creation_workflow is not None
        
        # Test complete setup workflow
        assert complete_setup_workflow.template_type == "workflow"
        assert complete_setup_workflow.category == "workflow"
        assert "workflow" in complete_setup_workflow.tags
        assert "setup" in complete_setup_workflow.tags
        assert complete_setup_workflow.complexity == "high"
        
        # Test content creation workflow
        assert content_creation_workflow.template_type == "workflow"
        assert content_creation_workflow.category == "workflow"
        assert "content" in content_creation_workflow.tags
        assert "writing" in content_creation_workflow.tags
    
    def test_category_determination(self, catalog_generator):
        """Test category determination from file paths."""
        test_cases = [
            (Path("examples/profiles/basic/test.json"), "basic"),
            (Path("examples/profiles/professional/test.json"), "professional"),
            (Path("examples/profiles/advanced/test.json"), "advanced"),
            (Path("examples/contexts/domains/test.md"), "domain"),
            (Path("examples/contexts/workflows/test.md"), "workflow"),
            (Path("examples/hooks/automation/test.yaml"), "automation"),
            (Path("examples/hooks/enhancement/test.yaml"), "enhancement"),
            (Path("examples/workflows/test/profile.json"), "workflow"),
            (Path("examples/other/test.json"), "general"),
        ]
        
        for file_path, expected_category in test_cases:
            result = catalog_generator._determine_category_from_path(file_path)
            assert result == expected_category, f"Path {file_path} should map to {expected_category}, got {result}"
    
    def test_tag_extraction_from_content(self, catalog_generator):
        """Test tag extraction from content analysis."""
        test_cases = [
            ("Python code with pandas and numpy", ["python", "data-science"]),
            ("JavaScript Node.js application", ["javascript"]),
            ("Docker containerization guide", ["devops"]),
            ("Security authentication patterns", ["security"]),
            ("Testing strategies with pytest", ["testing", "python"]),
            ("Documentation with markdown", ["documentation"]),
            ("Machine learning model deployment", ["data-science"]),
            ("CI/CD pipeline automation", ["devops", "automation"]),
        ]
        
        for content, expected_tags in test_cases:
            result = catalog_generator._extract_tags_from_content(content)
            
            # Check that at least some expected tags are found
            found_tags = set(result) & set(expected_tags)
            assert len(found_tags) > 0, f"Content '{content}' should contain tags {expected_tags}, got {result}"
    
    def test_complexity_determination(self, catalog_generator):
        """Test complexity determination from content analysis."""
        test_cases = [
            ("# Short Guide\n\nBrief content.", "low"),
            ("# Medium Guide\n\n" + "Content section. " * 100, "medium"),
            ("# Comprehensive Guide\n\n" + "## Section\n\nDetailed content. " * 200, "high"),
        ]
        
        for content, expected_complexity in test_cases:
            result = catalog_generator._determine_complexity_from_content(content)
            assert result == expected_complexity, f"Content should be {expected_complexity} complexity, got {result}"
    
    def test_markdown_catalog_generation(self, catalog_generator, comprehensive_templates, temp_examples_dir):
        """Test comprehensive markdown catalog generation."""
        output_file = temp_examples_dir / "test_catalog.md"
        
        result_path = catalog_generator.generate_markdown_catalog(str(output_file))
        
        assert Path(result_path).exists()
        
        # Read and verify content
        with open(result_path, 'r') as f:
            content = f.read()
        
        # Verify structure
        assert "# AI Configurator Template Catalog" in content
        assert "## Summary" in content
        assert "## Table of Contents" in content
        assert "## Profiles" in content
        assert "## Contexts" in content
        assert "## Hooks" in content
        assert "## Workflows" in content
        assert "## Quick Reference" in content
        
        # Verify content includes templates
        assert "minimal-profile" in content.lower()
        assert "data-scientist" in content.lower()
        assert "auto-documentation" in content.lower()
        assert "smart-suggestions" in content.lower()
        
        # Verify metadata is included
        assert "**Description**:" in content
        assert "**File**:" in content
        assert "**Tags**:" in content
        assert "**Complexity**:" in content
    
    def test_json_catalog_generation(self, catalog_generator, comprehensive_templates, temp_examples_dir):
        """Test comprehensive JSON catalog generation."""
        output_file = temp_examples_dir / "test_catalog.json"
        
        result_path = catalog_generator.generate_json_catalog(str(output_file))
        
        assert Path(result_path).exists()
        
        # Read and verify content
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        # Verify structure
        assert "profiles" in data
        assert "contexts" in data
        assert "hooks" in data
        assert "workflows" in data
        assert "generated_at" in data
        assert "total_count" in data
        
        # Verify counts
        assert len(data["profiles"]) == comprehensive_templates["profiles"]
        assert len(data["contexts"]) == comprehensive_templates["contexts"]
        assert len(data["hooks"]) == comprehensive_templates["hooks"]
        assert len(data["workflows"]) == comprehensive_templates["workflows"]
        
        # Verify template structure
        for template in data["profiles"]:
            assert "name" in template
            assert "description" in template
            assert "template_type" in template
            assert "file_path" in template
            assert template["template_type"] == "profile"
    
    def test_html_catalog_generation(self, catalog_generator, comprehensive_templates, temp_examples_dir):
        """Test comprehensive HTML catalog generation."""
        output_file = temp_examples_dir / "test_catalog.html"
        
        result_path = catalog_generator.generate_html_catalog(str(output_file))
        
        assert Path(result_path).exists()
        
        # Read and verify content
        with open(result_path, 'r') as f:
            content = f.read()
        
        # Verify HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html lang=\"en\">" in content
        assert "<title>AI Configurator Template Catalog</title>" in content
        assert "<h1>AI Configurator Template Catalog</h1>" in content
        
        # Verify CSS styling
        assert "<style>" in content
        assert "font-family:" in content
        assert ".template {" in content
        
        # Verify content sections
        assert "<h2>Profiles</h2>" in content
        assert "<h2>Contexts</h2>" in content
        assert "<h2>Hooks</h2>" in content
        assert "<h2>Workflows</h2>" in content
        
        # Verify template information
        assert "minimal-profile" in content.lower()
        assert "data-scientist" in content.lower()
        assert "auto-documentation" in content.lower()
        
        # Verify metadata display
        assert "<strong>Description:</strong>" in content
        assert "<strong>File:</strong>" in content
        assert "<strong>Category:</strong>" in content
        assert "<strong>Complexity:</strong>" in content
        assert 'class="tag"' in content
    
    def test_error_handling_with_malformed_templates(self, catalog_generator, temp_examples_dir):
        """Test error handling with malformed template files."""
        # Create malformed templates
        malformed_files = [
            # Invalid JSON
            ("profiles/basic/invalid.json", '{"name": "test", invalid json}'),
            # Invalid YAML
            ("hooks/automation/invalid.yaml", 'name: test\ninvalid: [unclosed'),
            # Binary file with template extension
            ("contexts/domains/binary.md", b"\x00\x01\x02\x03"),
            # Empty file
            ("profiles/basic/empty.json", ""),
        ]
        
        for file_path, content in malformed_files:
            full_path = temp_examples_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, bytes):
                full_path.write_bytes(content)
            else:
                full_path.write_text(content)
        
        # Generator should handle malformed files gracefully
        catalog = catalog_generator.generate_catalog()
        
        # Should still generate a catalog (may have fewer templates)
        assert isinstance(catalog, TemplateCatalog)
        assert catalog.total_count >= 0
    
    def test_performance_with_large_template_set(self, temp_examples_dir):
        """Test catalog generation performance with large template sets."""
        import time
        
        # Create a large number of templates
        num_templates = 50
        
        for i in range(num_templates):
            # Create profile
            profile_data = {
                "metadata": {
                    "name": f"profile-{i}",
                    "description": f"Test profile number {i}",
                    "category": "basic",
                    "version": "1.0.0",
                    "created": "2024-01-01",
                    "tags": [f"test-{i}", "generated"],
                    "complexity": "low"
                },
                "paths": [f"contexts/context-{i}.md"]
            }
            
            profile_file = temp_examples_dir / "profiles" / "basic" / f"profile-{i}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f)
            
            # Create context
            context_content = f"""# Context {i}

## Overview

This is test context number {i} for performance testing.

## Details

Context {i} provides guidance for scenario {i}.
"""
            
            context_file = temp_examples_dir / "contexts" / "domains" / f"context-{i}.md"
            context_file.parent.mkdir(parents=True, exist_ok=True)
            context_file.write_text(context_content)
        
        # Measure generation time
        generator = TemplateCatalogGenerator(str(temp_examples_dir))
        
        start_time = time.time()
        catalog = generator.generate_catalog()
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should complete within reasonable time
        assert generation_time < 30, f"Catalog generation took too long: {generation_time} seconds"
        
        # Verify all templates were processed
        assert catalog.total_count == num_templates * 2  # profiles + contexts
    
    def test_template_relationship_analysis(self, catalog_generator, comprehensive_templates):
        """Test analysis of template relationships and dependencies."""
        catalog = catalog_generator.generate_catalog()
        
        # Find templates with relationships
        data_scientist_profile = next((p for p in catalog.profiles if "data-scientist" in p.name.lower()), None)
        
        assert data_scientist_profile is not None
        assert len(data_scientist_profile.related_templates) > 0
        
        # Verify related templates are mentioned
        related_templates = data_scientist_profile.related_templates
        assert any("ml-engineer" in template.lower() for template in related_templates)
        assert any("data-analyst" in template.lower() for template in related_templates)
    
    def test_catalog_consistency_validation(self, catalog_generator, comprehensive_templates):
        """Test catalog consistency and data integrity validation."""
        catalog = catalog_generator.generate_catalog()
        
        # Verify no duplicate names within each category
        profile_names = [p.name for p in catalog.profiles]
        assert len(profile_names) == len(set(profile_names)), "Duplicate profile names found"
        
        context_names = [c.name for c in catalog.contexts]
        assert len(context_names) == len(set(context_names)), "Duplicate context names found"
        
        hook_names = [h.name for h in catalog.hooks]
        assert len(hook_names) == len(set(hook_names)), "Duplicate hook names found"
        
        workflow_names = [w.name for w in catalog.workflows]
        assert len(workflow_names) == len(set(workflow_names)), "Duplicate workflow names found"
        
        # Verify all file paths are unique
        all_templates = catalog.profiles + catalog.contexts + catalog.hooks + catalog.workflows
        file_paths = [t.file_path for t in all_templates]
        assert len(file_paths) == len(set(file_paths)), "Duplicate file paths found"
        
        # Verify all templates have required fields
        for template in all_templates:
            assert template.name, f"Template missing name: {template.file_path}"
            assert template.description, f"Template missing description: {template.file_path}"
            assert template.template_type, f"Template missing type: {template.file_path}"
            assert template.file_path, f"Template missing file path: {template.name}"
    
    def test_catalog_update_detection(self, catalog_generator, temp_examples_dir):
        """Test detection of template changes for incremental updates."""
        # Generate initial catalog
        initial_catalog = catalog_generator.generate_catalog()
        initial_count = initial_catalog.total_count
        
        # Add a new template
        new_profile = {
            "metadata": {
                "name": "new-profile",
                "description": "Newly added profile",
                "category": "basic",
                "version": "1.0.0",
                "created": "2024-01-01",
                "complexity": "low"
            },
            "paths": []
        }
        
        new_profile_file = temp_examples_dir / "profiles" / "basic" / "new-profile.json"
        with open(new_profile_file, 'w') as f:
            json.dump(new_profile, f)
        
        # Generate updated catalog
        updated_catalog = catalog_generator.generate_catalog()
        
        # Verify the new template was detected
        assert updated_catalog.total_count == initial_count + 1
        
        # Find the new profile
        new_profile_found = any(p.name == "new-profile" for p in updated_catalog.profiles)
        assert new_profile_found, "New profile should be detected in updated catalog"