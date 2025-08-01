"""Integration tests for complete template workflows."""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.ai_configurator.core.template_validator import TemplateValidator
from src.ai_configurator.core.template_quality_checker import TemplateQualityChecker, QualityLevel
from src.ai_configurator.core.template_installer import (
    TemplateInstaller,
    InstallationConfig,
    ConflictResolution,
    InstallationMode
)
from src.ai_configurator.core.template_updater import TemplateUpdater, UpdateConfig
from src.ai_configurator.core.template_catalog_generator import TemplateCatalogGenerator
from src.ai_configurator.core.models import ValidationReport


class TestTemplateWorkflowIntegration:
    """Integration tests for complete template management workflows."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a comprehensive temporary workspace for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            examples_dir = workspace / "examples"
            target_dir = workspace / "target"
            docs_dir = workspace / "docs"
            
            # Create examples structure
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "profiles" / "professional").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "contexts" / "workflows").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "hooks" / "enhancement").mkdir(parents=True)
            (examples_dir / "workflows" / "complete-setup").mkdir(parents=True)
            
            # Create target structure
            target_dir.mkdir()
            (target_dir / "profiles").mkdir()
            (target_dir / "contexts").mkdir()
            (target_dir / "hooks").mkdir()
            
            # Create docs structure
            docs_dir.mkdir()
            
            yield {
                "workspace": workspace,
                "examples": examples_dir,
                "target": target_dir,
                "docs": docs_dir
            }
    
    @pytest.fixture
    def sample_templates(self, temp_workspace):
        """Create a comprehensive set of sample templates for testing."""
        examples_dir = temp_workspace["examples"]
        
        # Create profile templates
        basic_profile = {
            "metadata": {
                "name": "basic-developer",
                "description": "Basic developer profile for general programming tasks",
                "category": "basic",
                "version": "1.0.0",
                "author": "AI Configurator Team",
                "created": "2024-01-01",
                "tags": ["basic", "developer", "general"],
                "complexity": "low",
                "prerequisites": [],
                "related_templates": ["advanced-developer"]
            },
            "paths": [
                "contexts/domains/development-basics.md",
                "contexts/workflows/basic-workflow.md"
            ],
            "hooks": {
                "basic-helper": {"enabled": True}
            },
            "settings": {
                "auto_reload": True,
                "max_contexts": 25
            }
        }
        
        professional_profile = {
            "metadata": {
                "name": "data-scientist",
                "description": "Professional data scientist profile with ML and analytics capabilities",
                "category": "professional",
                "version": "2.0.0",
                "author": "AI Configurator Team",
                "created": "2024-01-01",
                "updated": "2024-02-01",
                "tags": ["data-science", "ml", "analytics", "python"],
                "complexity": "high",
                "prerequisites": ["python-knowledge", "statistics"],
                "related_templates": ["ml-engineer", "data-analyst"]
            },
            "paths": [
                "contexts/domains/data-science.md",
                "contexts/workflows/ml-pipeline.md"
            ],
            "hooks": {
                "data-validator": {"enabled": True},
                "model-tracker": {"enabled": True}
            },
            "settings": {
                "auto_reload": True,
                "max_contexts": 100,
                "validation_level": "strict"
            }
        }
        
        # Write profile files
        basic_profile_file = examples_dir / "profiles" / "basic" / "basic-developer.json"
        with open(basic_profile_file, 'w') as f:
            json.dump(basic_profile, f, indent=2)
        
        professional_profile_file = examples_dir / "profiles" / "professional" / "data-scientist.json"
        with open(professional_profile_file, 'w') as f:
            json.dump(professional_profile, f, indent=2)
        
        # Create context templates
        basic_context = '''---
name: development-basics
description: Basic development guidelines and best practices
tags: [development, basics, guidelines]
categories: [development]
version: "1.0.0"
---

# Development Basics

## Overview

This context provides fundamental development guidelines for software projects.
It covers essential practices that every developer should follow.

## Best Practices

### Code Organization

1. **Use meaningful names** for variables, functions, and classes
2. **Keep functions small** and focused on a single responsibility
3. **Write self-documenting code** with clear logic flow

```python
def calculate_user_score(user_actions: list) -> float:
    """Calculate user engagement score based on actions.
    
    Args:
        user_actions: List of user action dictionaries
        
    Returns:
        Engagement score between 0.0 and 1.0
    """
    if not user_actions:
        return 0.0
    
    total_weight = sum(action.get('weight', 1) for action in user_actions)
    return min(total_weight / len(user_actions), 1.0)
```

### Testing

For instance, when writing unit tests:
- Test the happy path
- Test edge cases
- Test error conditions

```python
def test_calculate_user_score():
    # Happy path
    actions = [{'weight': 1}, {'weight': 2}]
    assert calculate_user_score(actions) == 1.5 / 2
    
    # Edge case: empty list
    assert calculate_user_score([]) == 0.0
    
    # Edge case: high weights
    high_weight_actions = [{'weight': 10}] * 5
    assert calculate_user_score(high_weight_actions) == 1.0
```

## Documentation

Such as in scenarios where you need to document APIs:
- Use clear, descriptive docstrings
- Include examples in documentation
- Keep documentation up to date

## Conclusion

Following these basic practices will help you write better, more maintainable code.
'''
        
        data_science_context = '''---
name: data-science
description: Comprehensive data science best practices and methodologies
tags: [data-science, ml, python, analytics]
categories: [data-science, development]
version: "2.0.0"
---

# Data Science Best Practices

## Overview

This comprehensive guide covers advanced data science practices, from data preprocessing
to model deployment and monitoring in production environments.

## Data Pipeline Development

### Data Validation

```python
import pandas as pd
from typing import Dict, List, Any
import numpy as np

class DataValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Validate dataframe against schema."""
        errors = {}
        
        # Check required columns
        missing_cols = set(self.schema.keys()) - set(df.columns)
        if missing_cols:
            errors['missing_columns'] = list(missing_cols)
        
        # Check data types
        type_errors = []
        for col, expected_type in self.schema.items():
            if col in df.columns and df[col].dtype != expected_type:
                type_errors.append(f"{col}: expected {expected_type}, got {df[col].dtype}")
        
        if type_errors:
            errors['type_errors'] = type_errors
        
        return errors
```

### Feature Engineering

For instance, when creating features for time series:

```python
def create_lag_features(df: pd.DataFrame, target_col: str, lags: List[int]) -> pd.DataFrame:
    """Create lag features for time series data."""
    df_with_lags = df.copy()
    
    for lag in lags:
        df_with_lags[f'{target_col}_lag_{lag}'] = df_with_lags[target_col].shift(lag)
    
    return df_with_lags

def create_rolling_features(df: pd.DataFrame, col: str, windows: List[int]) -> pd.DataFrame:
    """Create rolling window features."""
    df_with_rolling = df.copy()
    
    for window in windows:
        df_with_rolling[f'{col}_rolling_mean_{window}'] = df_with_rolling[col].rolling(window).mean()
        df_with_rolling[f'{col}_rolling_std_{window}'] = df_with_rolling[col].rolling(window).std()
    
    return df_with_rolling
```

## Model Development

### Cross-Validation

Such as in time series cross-validation scenarios:

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

def time_series_cross_validate(model, X, y, n_splits=5):
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

## Model Deployment

In real-world applications, implement proper monitoring:

```python
import mlflow
from datetime import datetime

class ModelMonitor:
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def log_prediction(self, features: Dict, prediction: float, actual: float = None):
        """Log prediction for monitoring."""
        with mlflow.start_run():
            mlflow.log_params(features)
            mlflow.log_metric("prediction", prediction)
            mlflow.log_metric("timestamp", datetime.now().timestamp())
            
            if actual is not None:
                mlflow.log_metric("actual", actual)
                mlflow.log_metric("error", abs(prediction - actual))
```

## Conclusion

These advanced practices ensure robust, scalable data science solutions that can
handle real-world complexity and changing requirements.
'''
        
        # Write context files
        basic_context_file = examples_dir / "contexts" / "domains" / "development-basics.md"
        with open(basic_context_file, 'w') as f:
            f.write(basic_context)
        
        data_science_context_file = examples_dir / "contexts" / "domains" / "data-science.md"
        with open(data_science_context_file, 'w') as f:
            f.write(data_science_context)
        
        # Create workflow context
        ml_pipeline_context = '''# ML Pipeline Workflow

## Overview

This workflow defines the complete machine learning pipeline from data ingestion
to model deployment and monitoring.

## Pipeline Stages

1. **Data Ingestion**: Collect and validate raw data
2. **Data Preprocessing**: Clean and transform data
3. **Feature Engineering**: Create and select features
4. **Model Training**: Train and validate models
5. **Model Evaluation**: Assess model performance
6. **Model Deployment**: Deploy to production
7. **Monitoring**: Track model performance

## Implementation

```python
class MLPipeline:
    def __init__(self, config):
        self.config = config
        self.model = None
    
    def run_pipeline(self, data_path: str):
        # Load and validate data
        data = self.load_data(data_path)
        validated_data = self.validate_data(data)
        
        # Preprocess and engineer features
        processed_data = self.preprocess_data(validated_data)
        features = self.engineer_features(processed_data)
        
        # Train and evaluate model
        self.model = self.train_model(features)
        metrics = self.evaluate_model(self.model, features)
        
        # Deploy if metrics are acceptable
        if metrics['accuracy'] > self.config.min_accuracy:
            self.deploy_model(self.model)
        
        return metrics
```

## Best Practices

For instance, when implementing pipeline stages:
- Use consistent data formats between stages
- Implement proper error handling and logging
- Create checkpoints for long-running processes

Such as in production deployment scenarios:
- Implement A/B testing for model comparison
- Set up automated retraining triggers
- Monitor data drift and model performance
'''
        
        ml_pipeline_file = examples_dir / "contexts" / "workflows" / "ml-pipeline.md"
        with open(ml_pipeline_file, 'w') as f:
            f.write(ml_pipeline_context)
        
        # Create hook templates
        basic_helper_hook = '''name: basic-helper
description: Basic development helper with code suggestions and best practices
version: "1.0.0"
type: context
trigger: per_user_message
timeout: 30
enabled: true

metadata:
  name: basic-helper
  description: Provides basic development assistance and code suggestions
  category: enhancement
  version: "1.0.0"
  author: AI Configurator Team
  created: "2024-01-01"
  tags: [helper, basic, development]
  complexity: low
  prerequisites: []
  related_hooks: [advanced-helper]

config:
  suggestion_types: [syntax, best-practices, documentation]
  max_suggestions: 3
  confidence_threshold: 0.7

context:
  sources:
    - contexts/domains/development-basics.md
  tags: [development, helper]
  priority: 1

conditions:
  - user_preferences:
      assistance_level: [basic, medium]
  - project_complexity: [low, medium]
'''
        
        data_validator_hook = '''name: data-validator
description: Advanced data validation and quality checking for data science projects
version: "2.0.0"
type: script
trigger: on_file_save
timeout: 60
enabled: true

metadata:
  name: data-validator
  description: Comprehensive data validation with schema checking and quality metrics
  category: automation
  version: "2.0.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-01"
  tags: [data-validation, quality, automation, data-science]
  complexity: high
  prerequisites: [python-environment, data-tools]
  related_hooks: [model-tracker, data-profiler]

config:
  validation_rules:
    - check_missing_values: true
    - validate_data_types: true
    - detect_outliers: true
    - check_duplicates: true
  
  quality_thresholds:
    missing_data_threshold: 0.05
    outlier_threshold: 0.02
    duplicate_threshold: 0.01
  
  output_formats: [json, html, csv]

script:
  language: python
  inline: |
    import pandas as pd
    import numpy as np
    from typing import Dict, Any
    
    def validate_data(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dataframe according to configuration."""
        results = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'validation_results': {}
        }
        
        # Check missing values
        if config.get('check_missing_values', True):
            missing_pct = df.isnull().sum() / len(df)
            results['validation_results']['missing_values'] = {
                'columns_with_missing': missing_pct[missing_pct > 0].to_dict(),
                'threshold_violations': missing_pct[missing_pct > config.get('missing_data_threshold', 0.05)].to_dict()
            }
        
        # Check data types
        if config.get('validate_data_types', True):
            results['validation_results']['data_types'] = df.dtypes.astype(str).to_dict()
        
        # Detect outliers (for numeric columns)
        if config.get('detect_outliers', True):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outliers = {}
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_mask = (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
                outlier_count = outlier_mask.sum()
                outliers[col] = {
                    'count': int(outlier_count),
                    'percentage': float(outlier_count / len(df))
                }
            results['validation_results']['outliers'] = outliers
        
        return results

conditions:
  - file_types: [".csv", ".parquet", ".json"]
    project_types: [data-science, analytics]
  - data_files_modified: true
'''
        
        # Write hook files
        basic_helper_file = examples_dir / "hooks" / "enhancement" / "basic-helper.yaml"
        with open(basic_helper_file, 'w') as f:
            f.write(basic_helper_hook)
        
        data_validator_file = examples_dir / "hooks" / "automation" / "data-validator.yaml"
        with open(data_validator_file, 'w') as f:
            f.write(data_validator_hook)
        
        # Create workflow template
        complete_setup_workflow = {
            "profile.json": {
                "metadata": {
                    "name": "complete-development-setup",
                    "description": "Complete development environment setup with tools and automation",
                    "category": "workflow",
                    "version": "1.0.0",
                    "author": "AI Configurator Team",
                    "created": "2024-01-01",
                    "tags": ["workflow", "setup", "development"],
                    "complexity": "medium",
                    "prerequisites": ["development-tools"],
                    "related_templates": ["basic-developer", "advanced-developer"]
                },
                "paths": [
                    "contexts/domains/development-basics.md",
                    "contexts/workflows/setup-process.md"
                ],
                "hooks": {
                    "environment-setup": {"enabled": True, "priority": 1},
                    "tool-installer": {"enabled": True, "priority": 2}
                },
                "settings": {
                    "auto_reload": True,
                    "setup_mode": "comprehensive"
                }
            },
            "contexts/setup-process.md": '''# Development Setup Process

## Overview

Complete guide for setting up a development environment with all necessary tools and configurations.

## Setup Steps

1. **Environment Validation**
2. **Tool Installation**
3. **Configuration Setup**
4. **Verification**

## Tools

- Git version control
- Code editor/IDE
- Package managers
- Testing frameworks
- Linting tools

## Configuration

```bash
# Example setup script
#!/bin/bash
set -e

echo "Setting up development environment..."

# Install Git hooks
git config core.hooksPath .githooks

# Install dependencies
npm install
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install

echo "Setup complete!"
```
''',
            "hooks/environment-setup.yaml": '''name: environment-setup
description: Automated development environment setup
version: "1.0.0"
type: script
trigger: manual
timeout: 300
enabled: true

config:
  setup_stages:
    - validate_system
    - install_tools
    - configure_environment
    - verify_setup

script:
  language: bash
  inline: |
    #!/bin/bash
    echo "Starting environment setup..."
    
    # Validate system requirements
    echo "Validating system..."
    
    # Install development tools
    echo "Installing tools..."
    
    # Configure environment
    echo "Configuring environment..."
    
    # Verify setup
    echo "Verifying setup..."
    
    echo "Environment setup complete!"
'''
        }
        
        # Write workflow files
        workflow_dir = examples_dir / "workflows" / "complete-setup"
        for file_name, content in complete_setup_workflow.items():
            file_path = workflow_dir / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, dict):
                with open(file_path, 'w') as f:
                    json.dump(content, f, indent=2)
            else:
                with open(file_path, 'w') as f:
                    f.write(content)
        
        return {
            "profiles": 2,
            "contexts": 3,
            "hooks": 2,
            "workflows": 1
        }
    
    def test_complete_validation_workflow(self, temp_workspace, sample_templates):
        """Test complete template validation workflow."""
        examples_dir = temp_workspace["examples"]
        
        # Initialize validator
        validator = TemplateValidator(examples_dir)
        
        # Run comprehensive validation
        validation_report = validator.validate_all_templates()
        
        # Verify validation results
        assert isinstance(validation_report, ValidationReport)
        assert validation_report.is_valid, f"Validation failed with errors: {validation_report.errors}"
        
        # Verify all templates were checked
        expected_files = sample_templates["profiles"] + sample_templates["contexts"] + sample_templates["hooks"] + 1  # +1 for workflow profile
        assert len(validation_report.files_checked) >= expected_files
        
        # Verify summary information
        assert validation_report.summary["total_files"] >= expected_files
        assert validation_report.summary["valid_files"] >= expected_files
        assert validation_report.summary["invalid_files"] == 0
        
        # Verify specific template validations
        profile_files = [f for f in validation_report.files_checked if "profiles" in f and f.endswith(".json")]
        context_files = [f for f in validation_report.files_checked if "contexts" in f and f.endswith(".md")]
        hook_files = [f for f in validation_report.files_checked if "hooks" in f and f.endswith(".yaml")]
        
        assert len(profile_files) >= sample_templates["profiles"]
        assert len(context_files) >= sample_templates["contexts"]
        assert len(hook_files) >= sample_templates["hooks"]
    
    def test_complete_quality_assessment_workflow(self, temp_workspace, sample_templates):
        """Test complete template quality assessment workflow."""
        examples_dir = temp_workspace["examples"]
        
        # Initialize quality checker
        quality_checker = TemplateQualityChecker(examples_dir)
        
        # Assess all templates
        quality_reports = quality_checker.assess_all_templates()
        
        # Verify quality reports
        assert len(quality_reports) >= sum(sample_templates.values())
        
        # Verify all reports have required structure
        for report in quality_reports:
            assert report.file_path
            assert report.template_type in ["profile", "context", "hook", "workflow"]
            assert 0.0 <= report.overall_score <= 1.0
            assert report.overall_level in [level.value for level in QualityLevel]
            assert len(report.metrics) > 0
            assert 0.0 <= report.documentation_completeness <= 1.0
            assert 0.0 <= report.example_accuracy <= 1.0
            assert 0.0 <= report.best_practices_compliance <= 1.0
        
        # Generate quality summary
        summary = quality_checker.generate_quality_summary(quality_reports)
        
        # Verify summary structure
        assert "total_templates" in summary
        assert "average_score" in summary
        assert "quality_distribution" in summary
        assert "template_types" in summary
        assert "best_template" in summary
        assert "worst_template" in summary
        assert "recommendations" in summary
        
        # Verify quality distribution
        distribution = summary["quality_distribution"]
        total_in_distribution = sum(distribution.values())
        assert total_in_distribution == len(quality_reports)
        
        # Verify template type distribution
        type_distribution = summary["template_types"]
        assert "profile" in type_distribution
        assert "context" in type_distribution
        assert "hook" in type_distribution
    
    def test_complete_installation_workflow(self, temp_workspace, sample_templates):
        """Test complete template installation workflow."""
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        
        # Initialize installer
        config = InstallationConfig(
            target_directory=target_dir,
            examples_directory=examples_dir,
            conflict_resolution=ConflictResolution(mode=InstallationMode.OVERWRITE),
            validate_before_install=True,
            validate_after_install=True
        )
        installer = TemplateInstaller(config)
        
        # Mock validation to always pass
        with patch.object(installer.validator, 'validate_profile_template') as mock_profile_val, \
             patch.object(installer.validator, 'validate_context_template') as mock_context_val, \
             patch.object(installer.validator, 'validate_hook_template') as mock_hook_val:
            
            mock_profile_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_context_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_hook_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Discover templates
            templates = installer.discover_templates()
            
            # Verify template discovery
            assert len(templates) >= sum(sample_templates.values())
            
            # Install all templates
            template_names = list(templates.keys())
            installation_results = installer.install_multiple_templates(template_names)
            
            # Verify installations
            assert len(installation_results) == len(template_names)
            successful_installations = [r for r in installation_results if r.success]
            assert len(successful_installations) == len(template_names)
            
            # Verify files were created
            for result in successful_installations:
                for installed_file in result.installed_files:
                    assert installed_file.exists(), f"Installed file should exist: {installed_file}"
            
            # Verify tracking
            installed_templates = installer.list_installed_templates()
            assert len(installed_templates) == len(template_names)
            
            # Verify installation history
            history = installer.get_installation_history()
            assert len(history) == len(template_names)
    
    def test_complete_update_workflow(self, temp_workspace, sample_templates):
        """Test complete template update workflow."""
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        
        # Setup installer
        config = InstallationConfig(
            target_directory=target_dir,
            examples_directory=examples_dir
        )
        installer = TemplateInstaller(config)
        
        # Setup updater
        update_config = UpdateConfig(
            backup_before_update=True,
            validate_after_update=True,
            max_backup_count=3
        )
        updater = TemplateUpdater(installer, update_config)
        
        # Mock installed templates (older versions)
        installed_templates = {
            "basic/basic-developer": MagicMock(
                name="basic/basic-developer",
                template_type="profile",
                source_path=target_dir / "profiles" / "basic-developer.json",
                version="0.9.0"
            ),
            "professional/data-scientist": MagicMock(
                name="professional/data-scientist", 
                template_type="profile",
                source_path=target_dir / "profiles" / "data-scientist.json",
                version="1.5.0"
            )
        }
        
        # Mock available templates (newer versions)
        available_templates = {
            "basic/basic-developer": MagicMock(
                name="basic/basic-developer",
                template_type="profile",
                source_path=examples_dir / "profiles" / "basic" / "basic-developer.json",
                version="1.0.0"
            ),
            "professional/data-scientist": MagicMock(
                name="professional/data-scientist",
                template_type="profile", 
                source_path=examples_dir / "profiles" / "professional" / "data-scientist.json",
                version="2.0.0"
            )
        }
        
        installer.list_installed_templates.return_value = installed_templates
        installer.discover_templates.return_value = available_templates
        
        # Mock version extraction
        with patch.object(updater, '_get_template_version') as mock_get_version:
            mock_get_version.side_effect = lambda t: t.version
            
            # Check for updates
            updates = updater.check_for_updates()
            
            # Verify updates were found
            assert len(updates) == 2
            assert "basic/basic-developer" in updates
            assert "professional/data-scientist" in updates
            
            # Verify version information
            basic_update = updates["basic/basic-developer"]
            assert basic_update.current == "0.9.0"
            assert basic_update.available == "1.0.0"
            assert basic_update.is_newer is True
            
            data_scientist_update = updates["professional/data-scientist"]
            assert data_scientist_update.current == "1.5.0"
            assert data_scientist_update.available == "2.0.0"
            assert data_scientist_update.is_newer is True
    
    def test_complete_catalog_generation_workflow(self, temp_workspace, sample_templates):
        """Test complete catalog generation workflow."""
        examples_dir = temp_workspace["examples"]
        docs_dir = temp_workspace["docs"]
        
        # Initialize catalog generator
        generator = TemplateCatalogGenerator(str(examples_dir))
        
        # Generate catalog
        catalog = generator.generate_catalog()
        
        # Verify catalog structure
        assert catalog.total_count >= sum(sample_templates.values())
        assert len(catalog.profiles) >= sample_templates["profiles"]
        assert len(catalog.contexts) >= sample_templates["contexts"]
        assert len(catalog.hooks) >= sample_templates["hooks"]
        assert len(catalog.workflows) >= sample_templates["workflows"]
        
        # Generate markdown catalog
        markdown_file = docs_dir / "catalog.md"
        generator.generate_markdown_catalog(str(markdown_file))
        
        assert markdown_file.exists()
        
        # Verify markdown content
        with open(markdown_file, 'r') as f:
            markdown_content = f.read()
        
        assert "# AI Configurator Template Catalog" in markdown_content
        assert "## Profiles" in markdown_content
        assert "## Contexts" in markdown_content
        assert "## Hooks" in markdown_content
        assert "## Workflows" in markdown_content
        assert "basic-developer" in markdown_content
        assert "data-scientist" in markdown_content
        
        # Generate JSON catalog
        json_file = docs_dir / "catalog.json"
        generator.generate_json_catalog(str(json_file))
        
        assert json_file.exists()
        
        # Verify JSON content
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        assert "profiles" in json_data
        assert "contexts" in json_data
        assert "hooks" in json_data
        assert "workflows" in json_data
        assert json_data["total_count"] >= sum(sample_templates.values())
        
        # Generate HTML catalog
        html_file = docs_dir / "catalog.html"
        generator.generate_html_catalog(str(html_file))
        
        assert html_file.exists()
        
        # Verify HTML content
        with open(html_file, 'r') as f:
            html_content = f.read()
        
        assert "<!DOCTYPE html>" in html_content
        assert "<title>AI Configurator Template Catalog</title>" in html_content
        assert "basic-developer" in html_content
        assert "data-scientist" in html_content
    
    def test_end_to_end_template_lifecycle(self, temp_workspace, sample_templates):
        """Test complete end-to-end template lifecycle."""
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        docs_dir = temp_workspace["docs"]
        
        # Phase 1: Validation
        validator = TemplateValidator(examples_dir)
        validation_report = validator.validate_all_templates()
        assert validation_report.is_valid
        
        # Phase 2: Quality Assessment
        quality_checker = TemplateQualityChecker(examples_dir)
        quality_reports = quality_checker.assess_all_templates()
        
        # Filter for high-quality templates
        high_quality_templates = [
            r for r in quality_reports 
            if r.overall_level in [QualityLevel.GOOD, QualityLevel.EXCELLENT]
        ]
        assert len(high_quality_templates) > 0
        
        # Phase 3: Installation
        config = InstallationConfig(
            target_directory=target_dir,
            examples_directory=examples_dir,
            validate_before_install=True,
            validate_after_install=True
        )
        installer = TemplateInstaller(config)
        
        # Mock validation for installation
        with patch.object(installer.validator, 'validate_profile_template') as mock_profile_val, \
             patch.object(installer.validator, 'validate_context_template') as mock_context_val, \
             patch.object(installer.validator, 'validate_hook_template') as mock_hook_val:
            
            mock_profile_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_context_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_hook_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Install high-quality templates
            templates = installer.discover_templates()
            template_names = list(templates.keys())[:3]  # Install first 3 templates
            
            installation_results = installer.install_multiple_templates(template_names)
            successful_installations = [r for r in installation_results if r.success]
            assert len(successful_installations) == len(template_names)
        
        # Phase 4: Update Management
        update_config = UpdateConfig(backup_before_update=True)
        updater = TemplateUpdater(installer, update_config)
        
        # Simulate checking for updates
        installed_templates = installer.list_installed_templates()
        assert len(installed_templates) == len(template_names)
        
        # Phase 5: Documentation Generation
        generator = TemplateCatalogGenerator(str(examples_dir))
        catalog = generator.generate_catalog()
        
        # Generate all documentation formats
        markdown_file = docs_dir / "final_catalog.md"
        json_file = docs_dir / "final_catalog.json"
        html_file = docs_dir / "final_catalog.html"
        
        generator.generate_markdown_catalog(str(markdown_file))
        generator.generate_json_catalog(str(json_file))
        generator.generate_html_catalog(str(html_file))
        
        # Verify all documentation was generated
        assert markdown_file.exists()
        assert json_file.exists()
        assert html_file.exists()
        
        # Phase 6: Verification
        # Verify installed templates are functional
        for template_name, template_metadata in installed_templates.items():
            assert template_metadata.target_path.exists()
            
            # Verify template content is valid
            if template_metadata.template_type.value == "profile":
                with open(template_metadata.target_path, 'r') as f:
                    profile_data = json.load(f)
                assert "metadata" in profile_data
                assert "name" in profile_data["metadata"]
        
        # Verify documentation contains installed templates
        with open(json_file, 'r') as f:
            catalog_data = json.load(f)
        
        catalog_template_names = []
        for template_list in [catalog_data["profiles"], catalog_data["contexts"], catalog_data["hooks"], catalog_data["workflows"]]:
            catalog_template_names.extend([t["name"] for t in template_list])
        
        # At least some installed templates should be in the catalog
        installed_names = [name.split('/')[-1] for name in installed_templates.keys()]
        common_names = set(installed_names) & set(catalog_template_names)
        assert len(common_names) > 0
    
    def test_error_handling_and_recovery(self, temp_workspace, sample_templates):
        """Test error handling and recovery in integrated workflows."""
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        
        # Create a malformed template to test error handling
        malformed_profile = '{"name": "malformed", invalid json}'
        malformed_file = examples_dir / "profiles" / "basic" / "malformed.json"
        with open(malformed_file, 'w') as f:
            f.write(malformed_profile)
        
        # Test validation with malformed template
        validator = TemplateValidator(examples_dir)
        validation_report = validator.validate_all_templates()
        
        # Should have errors but not crash
        assert len(validation_report.errors) > 0
        assert not validation_report.is_valid
        
        # Find the malformed template error
        malformed_errors = [e for e in validation_report.errors if "malformed" in e.file_path]
        assert len(malformed_errors) > 0
        
        # Test quality assessment with malformed template
        quality_checker = TemplateQualityChecker(examples_dir)
        quality_reports = quality_checker.assess_all_templates()
        
        # Should handle malformed templates gracefully
        malformed_reports = [r for r in quality_reports if "malformed" in r.file_path]
        if malformed_reports:
            # If it creates a report, it should be poor quality
            assert malformed_reports[0].overall_level == QualityLevel.POOR
        
        # Test installation with validation failure
        config = InstallationConfig(
            target_directory=target_dir,
            examples_directory=examples_dir,
            validate_before_install=True
        )
        installer = TemplateInstaller(config)
        
        # Mock validation failure for malformed template
        def mock_validation(file_path):
            if "malformed" in str(file_path):
                return ValidationReport(
                    is_valid=False,
                    errors=[MagicMock(file_path=str(file_path), error_type="syntax_error")],
                    warnings=[]
                )
            return ValidationReport(is_valid=True, errors=[], warnings=[])
        
        with patch.object(installer.validator, 'validate_profile_template', side_effect=mock_validation):
            # Try to install malformed template
            result = installer.install_template("basic/malformed")
            
            # Should fail gracefully
            assert not result.success
            assert len(result.errors) > 0
            assert "validation failed" in result.errors[0].lower()
        
        # Test catalog generation with malformed templates
        generator = TemplateCatalogGenerator(str(examples_dir))
        catalog = generator.generate_catalog()
        
        # Should complete despite malformed templates
        assert isinstance(catalog, type(generator.catalog))
        assert catalog.total_count >= 0
    
    def test_performance_with_large_template_set(self, temp_workspace):
        """Test workflow performance with large template sets."""
        import time
        
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        
        # Create a large number of templates
        num_templates = 25
        
        for i in range(num_templates):
            # Create profile
            profile_data = {
                "metadata": {
                    "name": f"performance-profile-{i}",
                    "description": f"Performance test profile {i}",
                    "category": "basic",
                    "version": "1.0.0",
                    "created": "2024-01-01",
                    "complexity": "low"
                },
                "paths": [f"contexts/performance-context-{i}.md"]
            }
            
            profile_file = examples_dir / "profiles" / "basic" / f"performance-profile-{i}.json"
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f)
            
            # Create context
            context_content = f"""# Performance Context {i}

## Overview

This is performance test context {i} for testing workflow scalability.

## Content

Context {i} provides guidance for performance testing scenario {i}.
It includes sufficient content to test processing performance.

```python
def performance_function_{i}():
    return f"Performance test {i}"
```

## Conclusion

Context {i} demonstrates scalable template processing.
"""
            
            context_file = examples_dir / "contexts" / "domains" / f"performance-context-{i}.md"
            context_file.parent.mkdir(parents=True, exist_ok=True)
            context_file.write_text(context_content)
        
        # Test validation performance
        start_time = time.time()
        validator = TemplateValidator(examples_dir)
        validation_report = validator.validate_all_templates()
        validation_time = time.time() - start_time
        
        assert validation_time < 30, f"Validation took too long: {validation_time} seconds"
        assert validation_report.is_valid
        
        # Test quality assessment performance
        start_time = time.time()
        quality_checker = TemplateQualityChecker(examples_dir)
        quality_reports = quality_checker.assess_all_templates()
        quality_time = time.time() - start_time
        
        assert quality_time < 60, f"Quality assessment took too long: {quality_time} seconds"
        assert len(quality_reports) >= num_templates * 2  # profiles + contexts
        
        # Test catalog generation performance
        start_time = time.time()
        generator = TemplateCatalogGenerator(str(examples_dir))
        catalog = generator.generate_catalog()
        catalog_time = time.time() - start_time
        
        assert catalog_time < 20, f"Catalog generation took too long: {catalog_time} seconds"
        assert catalog.total_count >= num_templates * 2
    
    def test_concurrent_workflow_operations(self, temp_workspace, sample_templates):
        """Test concurrent workflow operations for thread safety."""
        import threading
        import time
        
        examples_dir = temp_workspace["examples"]
        target_dir = temp_workspace["target"]
        
        results = []
        errors = []
        
        def run_validation():
            try:
                validator = TemplateValidator(examples_dir)
                report = validator.validate_all_templates()
                results.append(("validation", report.is_valid))
            except Exception as e:
                errors.append(("validation", e))
        
        def run_quality_assessment():
            try:
                quality_checker = TemplateQualityChecker(examples_dir)
                reports = quality_checker.assess_all_templates()
                results.append(("quality", len(reports)))
            except Exception as e:
                errors.append(("quality", e))
        
        def run_catalog_generation():
            try:
                generator = TemplateCatalogGenerator(str(examples_dir))
                catalog = generator.generate_catalog()
                results.append(("catalog", catalog.total_count))
            except Exception as e:
                errors.append(("catalog", e))
        
        # Start concurrent operations
        threads = [
            threading.Thread(target=run_validation),
            threading.Thread(target=run_quality_assessment),
            threading.Thread(target=run_catalog_generation),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent operation errors: {errors}"
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # Verify all operations completed successfully
        operation_types = [result[0] for result in results]
        assert "validation" in operation_types
        assert "quality" in operation_types
        assert "catalog" in operation_types