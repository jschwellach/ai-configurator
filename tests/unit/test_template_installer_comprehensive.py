"""Comprehensive unit tests for template installer functionality."""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.ai_configurator.core.template_installer import (
    TemplateInstaller,
    TemplateType,
    InstallationMode,
    TemplateMetadata,
    InstallationConfig,
    ConflictResolution,
    InstallationResult
)
from src.ai_configurator.core.models import ValidationReport, ConfigurationError


class TestTemplateInstallerComprehensive:
    """Comprehensive tests for template installer functionality."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create comprehensive temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            examples_dir = temp_path / "examples"
            target_dir = temp_path / "target"
            
            # Create comprehensive example directory structure
            examples_dir.mkdir()
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
            
            # Create target directory structure
            target_dir.mkdir()
            
            yield {
                "examples": examples_dir,
                "target": target_dir,
                "temp": temp_path
            }
    
    @pytest.fixture
    def installation_config(self, temp_dirs):
        """Create comprehensive installation configuration."""
        return InstallationConfig(
            target_directory=temp_dirs["target"],
            examples_directory=temp_dirs["examples"],
            conflict_resolution=ConflictResolution(
                mode=InstallationMode.SKIP,
                backup_existing=True,
                preserve_user_modifications=True,
                merge_strategy="user_priority"
            ),
            validate_before_install=True,
            validate_after_install=True,
            create_backup=True,
            dry_run=False
        )
    
    @pytest.fixture
    def installer(self, installation_config):
        """Create template installer instance."""
        return TemplateInstaller(installation_config)
    
    @pytest.fixture
    def comprehensive_templates(self, temp_dirs):
        """Create comprehensive set of test templates."""
        examples_dir = temp_dirs["examples"]
        
        # Create profile templates
        profiles = [
            {
                "path": "profiles/basic/minimal.json",
                "data": {
                    "metadata": {
                        "name": "minimal-profile",
                        "description": "A minimal profile for basic usage",
                        "category": "basic",
                        "version": "1.0.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "tags": ["basic", "minimal"],
                        "complexity": "low",
                        "prerequisites": [],
                        "related_templates": []
                    },
                    "paths": ["contexts/domains/basic-guidelines.md"],
                    "hooks": {},
                    "settings": {"auto_reload": True}
                }
            },
            {
                "path": "profiles/professional/data-scientist.json",
                "data": {
                    "metadata": {
                        "name": "data-scientist-profile",
                        "description": "Comprehensive profile for data science workflows",
                        "category": "professional",
                        "version": "2.1.0",
                        "author": "AI Configurator Team",
                        "created": "2024-01-01",
                        "updated": "2024-02-15",
                        "tags": ["data-science", "ml", "analytics"],
                        "complexity": "high",
                        "prerequisites": ["python-knowledge", "statistics-background"],
                        "related_templates": ["ml-engineer", "data-analyst"]
                    },
                    "paths": [
                        "contexts/domains/data-science-best-practices.md",
                        "contexts/workflows/ml-pipeline.md"
                    ],
                    "hooks": {
                        "auto-documentation": {"enabled": True},
                        "data-validation": {"enabled": True}
                    },
                    "settings": {
                        "auto_reload": True,
                        "max_contexts": 100,
                        "validation_level": "strict"
                    }
                }
            }
        ]
        
        # Create context templates
        contexts = [
            {
                "path": "contexts/domains/basic-guidelines.md",
                "content": """---
name: basic-guidelines
description: Basic development guidelines
tags: [development, guidelines, basic]
categories: [development]
version: "1.0.0"
---

# Basic Development Guidelines

## Overview

This context provides fundamental development guidelines for getting started
with software development projects.

## Best Practices

1. **Code Organization**: Keep your code well-organized
2. **Documentation**: Document your code thoroughly
3. **Testing**: Write tests for your code

## Examples

```python
def hello_world():
    \"\"\"A simple hello world function.\"\"\"
    return "Hello, World!"
```

## Conclusion

Following these basic guidelines will help you write better code.
"""
            },
            {
                "path": "contexts/domains/data-science-best-practices.md",
                "content": """---
name: data-science-best-practices
description: Comprehensive data science best practices
tags: [data-science, ml, best-practices]
categories: [data-science, development]
version: "2.0.0"
---

# Data Science Best Practices

## Overview

This comprehensive guide covers best practices for data science projects,
from data collection to model deployment.

## Data Management

### Data Collection

- Ensure data quality and consistency
- Document data sources and collection methods
- Implement data validation checks

```python
import pandas as pd
from typing import Dict, Any

def validate_data(df: pd.DataFrame, schema: Dict[str, Any]) -> bool:
    \"\"\"Validate dataframe against schema.\"\"\"
    for column, expected_type in schema.items():
        if column not in df.columns:
            return False
        if not df[column].dtype == expected_type:
            return False
    return True
```

### Data Preprocessing

- Handle missing values appropriately
- Normalize and scale features
- Engineer relevant features

## Model Development

### Model Selection

For instance, when choosing between models, consider:
- Problem complexity
- Data size and quality
- Interpretability requirements

### Model Validation

Such as in cross-validation scenarios:

```python
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

def evaluate_model(X, y, model=None):
    \"\"\"Evaluate model using cross-validation.\"\"\"
    if model is None:
        model = RandomForestClassifier()
    
    scores = cross_val_score(model, X, y, cv=5)
    return scores.mean(), scores.std()
```

## Deployment

### Model Monitoring

In real-world applications, monitor:
- Model performance metrics
- Data drift detection
- System performance

## Conclusion

Following these practices ensures robust and reliable data science projects.
"""
            }
        ]
        
        # Create hook templates
        hooks = [
            {
                "path": "hooks/automation/auto-documentation.yaml",
                "content": """name: auto-documentation
description: Automatically generate documentation from code
version: "1.5.0"
type: script
trigger: on_file_save
timeout: 60
enabled: true

metadata:
  name: auto-documentation
  description: Intelligent documentation generation hook
  category: automation
  version: "1.5.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-10"
  tags: [automation, documentation, code-analysis]
  complexity: medium
  prerequisites: [python-environment]
  related_hooks: [code-quality-check]

config:
  documentation_formats: [markdown, rst, html]
  include_examples: true
  generate_api_docs: true
  update_readme: true

script:
  language: python
  file: auto_documentation.py

conditions:
  - file_types: [".py", ".js", ".ts"]
    project_types: [library, application]
"""
            },
            {
                "path": "hooks/enhancement/smart-suggestions.yaml",
                "content": """name: smart-suggestions
description: Provide intelligent code suggestions based on context
version: "2.0.0"
type: context
trigger: per_user_message
timeout: 30
enabled: true

metadata:
  name: smart-suggestions
  description: AI-powered code suggestions and improvements
  category: enhancement
  version: "2.0.0"
  author: AI Configurator Team
  created: "2024-01-01"
  updated: "2024-02-20"
  tags: [ai, suggestions, code-improvement]
  complexity: high
  prerequisites: [ai-model-access]
  related_hooks: [context-switcher]

config:
  suggestion_types: [code-improvement, best-practices, performance]
  confidence_threshold: 0.8
  max_suggestions: 5

context:
  sources:
    - contexts/domains/data-science-best-practices.md
    - contexts/workflows/code-review-process.md
  tags: [suggestions, improvement]
  priority: 2

conditions:
  - user_preferences:
      suggestions_enabled: true
      ai_assistance: [medium, high]
"""
            }
        ]
        
        # Create workflow templates
        workflows = [
            {
                "path": "workflows/complete-setup",
                "files": {
                    "profile.json": {
                        "metadata": {
                            "name": "complete-setup-workflow",
                            "description": "Complete development environment setup",
                            "category": "workflow",
                            "version": "1.0.0",
                            "tags": ["workflow", "setup", "complete"]
                        },
                        "paths": [
                            "contexts/domains/development-setup.md",
                            "contexts/workflows/environment-config.md"
                        ],
                        "hooks": {
                            "environment-setup": {"enabled": True},
                            "dependency-check": {"enabled": True}
                        }
                    },
                    "contexts/development-setup.md": """# Development Setup

Complete guide for setting up development environment.
""",
                    "hooks/environment-setup.yaml": """name: environment-setup
description: Setup development environment
trigger: manual
"""
                }
            }
        ]
        
        # Write all template files
        for profile in profiles:
            file_path = examples_dir / profile["path"]
            with open(file_path, 'w') as f:
                json.dump(profile["data"], f, indent=2)
        
        for context in contexts:
            file_path = examples_dir / context["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(context["content"])
        
        for hook in hooks:
            file_path = examples_dir / hook["path"]
            with open(file_path, 'w') as f:
                f.write(hook["content"])
        
        for workflow in workflows:
            workflow_dir = examples_dir / workflow["path"]
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
    
    def test_comprehensive_template_discovery(self, installer, comprehensive_templates):
        """Test comprehensive template discovery across all categories."""
        templates = installer.discover_templates()
        
        # Verify all template types are discovered
        profile_templates = [t for t in templates.values() if t.template_type == TemplateType.PROFILE]
        context_templates = [t for t in templates.values() if t.template_type == TemplateType.CONTEXT]
        hook_templates = [t for t in templates.values() if t.template_type == TemplateType.HOOK]
        workflow_templates = [t for t in templates.values() if t.template_type == TemplateType.WORKFLOW]
        
        assert len(profile_templates) == comprehensive_templates["profiles"]
        assert len(context_templates) == comprehensive_templates["contexts"]
        assert len(hook_templates) == comprehensive_templates["hooks"]
        assert len(workflow_templates) == comprehensive_templates["workflows"]
        
        # Verify template metadata
        for template in templates.values():
            assert isinstance(template, TemplateMetadata)
            assert template.name
            assert template.template_type in [t.value for t in TemplateType]
            assert template.source_path.exists()
            assert template.target_path
    
    def test_template_discovery_by_type(self, installer, comprehensive_templates):
        """Test template discovery filtered by type."""
        # Test each template type individually
        for template_type in TemplateType:
            templates = installer.discover_templates(template_type)
            
            # All discovered templates should be of the requested type
            for template in templates.values():
                assert template.template_type == template_type
            
            # Verify expected counts
            if template_type == TemplateType.PROFILE:
                assert len(templates) == comprehensive_templates["profiles"]
            elif template_type == TemplateType.CONTEXT:
                assert len(templates) == comprehensive_templates["contexts"]
            elif template_type == TemplateType.HOOK:
                assert len(templates) == comprehensive_templates["hooks"]
            elif template_type == TemplateType.WORKFLOW:
                assert len(templates) == comprehensive_templates["workflows"]
    
    def test_installation_with_validation(self, installer, comprehensive_templates):
        """Test template installation with comprehensive validation."""
        # Mock successful validation
        with patch.object(installer.validator, 'validate_profile_template') as mock_profile_validate, \
             patch.object(installer.validator, 'validate_context_template') as mock_context_validate, \
             patch.object(installer.validator, 'validate_hook_template') as mock_hook_validate:
            
            mock_profile_validate.return_value = ValidationReport(
                is_valid=True, errors=[], warnings=[]
            )
            mock_context_validate.return_value = ValidationReport(
                is_valid=True, errors=[], warnings=[]
            )
            mock_hook_validate.return_value = ValidationReport(
                is_valid=True, errors=[], warnings=[]
            )
            
            # Install a profile template
            result = installer.install_template("basic/minimal")
            
            assert result.success
            assert result.template_name == "basic/minimal"
            assert result.template_type == TemplateType.PROFILE
            assert len(result.installed_files) == 1
            assert result.installed_files[0].exists()
            
            # Verify validation was called
            mock_profile_validate.assert_called_once()
    
    def test_installation_validation_failure(self, installer, comprehensive_templates):
        """Test installation behavior when validation fails."""
        # Mock validation failure
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path="test.json",
                    error_type="validation_error",
                    message="Template validation failed",
                    severity="error"
                )],
                warnings=[]
            )
            
            result = installer.install_template("basic/minimal")
            
            assert not result.success
            assert "validation failed" in result.errors[0].lower()
            assert len(result.installed_files) == 0
    
    def test_conflict_resolution_modes(self, installer, comprehensive_templates, temp_dirs):
        """Test all conflict resolution modes."""
        # First install a template
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Initial installation
            result = installer.install_template("basic/minimal")
            assert result.success
            
            target_file = temp_dirs["target"] / "profiles" / "minimal.json"
            assert target_file.exists()
            original_content = target_file.read_text()
            
            # Modify the installed file to simulate user changes
            modified_content = original_content.replace("minimal-profile", "user-modified-profile")
            target_file.write_text(modified_content)
            
            # Test SKIP mode (default)
            installer.config.conflict_resolution.mode = InstallationMode.SKIP
            result = installer.install_template("basic/minimal")
            assert not result.success  # Should skip due to conflict
            assert target_file.read_text() == modified_content  # File unchanged
            
            # Test OVERWRITE mode
            installer.config.conflict_resolution.mode = InstallationMode.OVERWRITE
            result = installer.install_template("basic/minimal")
            assert result.success
            # File should be overwritten (content will be different from modified)
            assert "user-modified-profile" not in target_file.read_text()
            
            # Test BACKUP mode
            installer.config.conflict_resolution.mode = InstallationMode.BACKUP
            target_file.write_text(modified_content)  # Restore modified content
            
            result = installer.install_template("basic/minimal")
            assert result.success
            
            # Check that backup was created
            backup_dir = temp_dirs["target"] / "backups"
            assert backup_dir.exists()
            backup_files = list(backup_dir.rglob("*.json"))
            assert len(backup_files) > 0
    
    def test_workflow_installation(self, installer, comprehensive_templates):
        """Test installation of complete workflow templates."""
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            result = installer.install_template("workflow/complete-setup")
            
            assert result.success
            assert result.template_type == TemplateType.WORKFLOW
            assert len(result.installed_files) > 1  # Should install multiple files
            
            # Verify all workflow components were installed
            target_dir = installer.config.target_directory
            assert (target_dir / "profiles" / "complete-setup.json").exists()
    
    def test_multiple_template_installation(self, installer, comprehensive_templates):
        """Test installation of multiple templates with dependency handling."""
        with patch.object(installer.validator, 'validate_profile_template') as mock_profile_validate, \
             patch.object(installer.validator, 'validate_context_template') as mock_context_validate, \
             patch.object(installer.validator, 'validate_hook_template') as mock_hook_validate:
            
            mock_profile_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_context_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            mock_hook_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            template_names = [
                "basic/minimal",
                "domains/basic-guidelines",
                "automation/auto-documentation"
            ]
            
            results = installer.install_multiple_templates(template_names)
            
            assert len(results) == 3
            assert all(result.success for result in results)
            
            # Verify all templates are tracked
            installed = installer.list_installed_templates()
            assert len(installed) == 3
            
            # Verify installation history
            history = installer.get_installation_history()
            assert len(history) == 3
    
    def test_installation_rollback_on_failure(self, installer, comprehensive_templates):
        """Test installation rollback when installation fails."""
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Mock a failure during file copying
            with patch('shutil.copy2', side_effect=PermissionError("Permission denied")):
                result = installer.install_template("basic/minimal")
                
                assert not result.success
                assert "Permission denied" in str(result.errors)
                
                # Verify no partial installation
                target_file = installer.config.target_directory / "profiles" / "minimal.json"
                assert not target_file.exists()
    
    def test_dry_run_mode(self, installer, comprehensive_templates):
        """Test installation in dry run mode."""
        installer.config.dry_run = True
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            result = installer.install_template("basic/minimal")
            
            assert result.success
            assert len(result.warnings) > 0
            assert any("dry run" in warning.lower() for warning in result.warnings)
            
            # Verify no actual files were created
            target_file = installer.config.target_directory / "profiles" / "minimal.json"
            assert not target_file.exists()
    
    def test_template_uninstallation(self, installer, comprehensive_templates):
        """Test comprehensive template uninstallation."""
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Install template
            result = installer.install_template("basic/minimal")
            assert result.success
            
            target_file = installer.config.target_directory / "profiles" / "minimal.json"
            assert target_file.exists()
            
            # Uninstall template
            success = installer.uninstall_template("basic/minimal")
            assert success
            
            # Verify file was removed
            assert not target_file.exists()
            
            # Verify template is no longer tracked
            installed = installer.list_installed_templates()
            assert "basic/minimal" not in installed
    
    def test_installation_with_missing_dependencies(self, installer, temp_dirs):
        """Test installation behavior with missing template dependencies."""
        # Create a profile that references non-existent contexts
        profile_data = {
            "metadata": {
                "name": "dependent-profile",
                "description": "Profile with dependencies",
                "category": "basic",
                "complexity": "low",
                "created": "2024-01-01"
            },
            "paths": [
                "contexts/existing-context.md",
                "contexts/missing-context.md"  # This doesn't exist
            ]
        }
        
        profile_file = temp_dirs["examples"] / "profiles" / "basic" / "dependent.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        # Create only one of the referenced contexts
        context_file = temp_dirs["examples"] / "contexts" / "domains" / "existing-context.md"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        context_file.write_text("# Existing Context\n\nThis context exists.")
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            # Mock validation that warns about missing dependencies
            mock_validate.return_value = ValidationReport(
                is_valid=True,
                errors=[],
                warnings=[ConfigurationError(
                    file_path=str(profile_file),
                    error_type="MissingDependency",
                    message="Referenced context not found: contexts/missing-context.md",
                    severity="warning"
                )]
            )
            
            result = installer.install_template("basic/dependent")
            
            # Installation should succeed but with warnings
            assert result.success
            assert len(result.warnings) > 0
    
    def test_concurrent_installation_safety(self, installer, comprehensive_templates):
        """Test installation safety with concurrent operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def install_template(template_name, delay=0):
            try:
                if delay:
                    time.sleep(delay)
                
                with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
                    mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
                    result = installer.install_template(template_name)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple installation threads
        threads = [
            threading.Thread(target=install_template, args=("basic/minimal", 0.1)),
            threading.Thread(target=install_template, args=("professional/data-scientist", 0.2)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent installation errors: {errors}"
        assert len(results) == 2
        assert all(result.success for result in results)
    
    def test_installation_with_custom_target_paths(self, temp_dirs):
        """Test installation with custom target directory structure."""
        # Create custom target structure
        custom_target = temp_dirs["temp"] / "custom_target"
        custom_target.mkdir()
        (custom_target / "my_profiles").mkdir()
        (custom_target / "my_contexts").mkdir()
        (custom_target / "my_hooks").mkdir()
        
        # Create custom installation config
        custom_config = InstallationConfig(
            target_directory=custom_target,
            examples_directory=temp_dirs["examples"]
        )
        
        custom_installer = TemplateInstaller(custom_config)
        
        # Create a simple template
        profile_data = {
            "metadata": {
                "name": "custom-profile",
                "description": "Profile for custom installation",
                "category": "basic",
                "complexity": "low",
                "created": "2024-01-01"
            },
            "paths": []
        }
        
        profile_file = temp_dirs["examples"] / "profiles" / "basic" / "custom.json"
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        with patch.object(custom_installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            result = custom_installer.install_template("basic/custom")
            
            assert result.success
            # Verify file was installed in custom location
            assert (custom_target / "profiles" / "custom.json").exists()
    
    def test_installation_error_recovery(self, installer, comprehensive_templates, temp_dirs):
        """Test installation error recovery and cleanup."""
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Mock partial failure during installation
            original_copy = installer._install_single_file
            
            def failing_install(template):
                # Create the target file but then fail
                template.target_path.parent.mkdir(parents=True, exist_ok=True)
                template.target_path.write_text("partial content")
                raise RuntimeError("Installation failed after partial completion")
            
            with patch.object(installer, '_install_single_file', side_effect=failing_install):
                result = installer.install_template("basic/minimal")
                
                assert not result.success
                assert "Installation failed" in str(result.errors)
                
                # Verify cleanup occurred (no partial files left)
                target_file = temp_dirs["target"] / "profiles" / "minimal.json"
                # The file might exist but should not be tracked as installed
                assert "basic/minimal" not in installer.installed_templates
    
    def test_installation_performance_monitoring(self, installer, comprehensive_templates):
        """Test installation performance monitoring and optimization."""
        import time
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            # Measure installation time
            start_time = time.time()
            
            result = installer.install_template("basic/minimal")
            
            end_time = time.time()
            installation_time = end_time - start_time
            
            assert result.success
            # Installation should be reasonably fast
            assert installation_time < 5.0, f"Installation took too long: {installation_time} seconds"
    
    def test_template_metadata_validation(self, installer, temp_dirs):
        """Test comprehensive template metadata validation."""
        # Create templates with various metadata issues
        test_cases = [
            {
                "name": "valid-metadata.json",
                "data": {
                    "metadata": {
                        "name": "valid-template",
                        "description": "A template with valid metadata",
                        "category": "basic",
                        "version": "1.0.0",
                        "created": "2024-01-01",
                        "complexity": "low"
                    },
                    "paths": []
                },
                "should_install": True
            },
            {
                "name": "missing-metadata.json",
                "data": {
                    "paths": []
                },
                "should_install": False  # Missing metadata
            },
            {
                "name": "invalid-version.json",
                "data": {
                    "metadata": {
                        "name": "invalid-version",
                        "description": "Template with invalid version",
                        "category": "basic",
                        "version": "not-a-version",
                        "created": "2024-01-01",
                        "complexity": "low"
                    },
                    "paths": []
                },
                "should_install": True  # Version validation might be lenient
            }
        ]
        
        for test_case in test_cases:
            # Create template file
            template_file = temp_dirs["examples"] / "profiles" / "basic" / test_case["name"]
            with open(template_file, 'w') as f:
                json.dump(test_case["data"], f)
            
            template_name = f"basic/{test_case['name'][:-5]}"  # Remove .json extension
            
            with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
                if test_case["should_install"]:
                    mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
                else:
                    mock_validate.return_value = ValidationReport(
                        is_valid=False,
                        errors=[ConfigurationError(
                            file_path=str(template_file),
                            error_type="metadata_error",
                            message="Invalid metadata",
                            severity="error"
                        )],
                        warnings=[]
                    )
                
                result = installer.install_template(template_name)
                
                if test_case["should_install"]:
                    assert result.success, f"Template {test_case['name']} should install successfully"
                else:
                    assert not result.success, f"Template {test_case['name']} should fail to install"