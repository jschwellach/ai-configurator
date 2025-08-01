"""
Unit tests for template installer functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

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
from src.ai_configurator.core.models import ValidationReport


class TestTemplateInstaller:
    """Test cases for TemplateInstaller class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            examples_dir = temp_path / "examples"
            target_dir = temp_path / "target"
            
            # Create example directory structure
            examples_dir.mkdir()
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (examples_dir / "workflows" / "test-workflow").mkdir(parents=True)
            
            # Create target directory structure
            target_dir.mkdir()
            
            yield {
                "examples": examples_dir,
                "target": target_dir,
                "temp": temp_path
            }
    
    @pytest.fixture
    def installation_config(self, temp_dirs):
        """Create installation configuration for testing."""
        return InstallationConfig(
            target_directory=temp_dirs["target"],
            examples_directory=temp_dirs["examples"],
            conflict_resolution=ConflictResolution(mode=InstallationMode.SKIP),
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
    def sample_profile(self, temp_dirs):
        """Create a sample profile template."""
        profile_file = temp_dirs["examples"] / "profiles" / "basic" / "test-profile.json"
        profile_data = {
            "metadata": {
                "name": "test-profile",
                "description": "Test profile for unit tests",
                "category": "basic",
                "version": "1.0.0",
                "author": "Test Author",
                "created": "2024-01-01",
                "updated": "2024-01-01",
                "tags": ["test", "example"],
                "complexity": "low",
                "prerequisites": [],
                "related_templates": []
            },
            "name": "test-profile",
            "description": "Test profile for unit tests",
            "contexts": ["contexts/test-context.md"],
            "hooks": {},
            "settings": {}
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        return profile_file
    
    @pytest.fixture
    def sample_context(self, temp_dirs):
        """Create a sample context template."""
        context_file = temp_dirs["examples"] / "contexts" / "domains" / "test-context.md"
        context_content = """---
title: Test Context
description: Test context for unit tests
tags: [test, example]
---

# Test Context

This is a test context file for unit testing.
"""
        
        with open(context_file, 'w') as f:
            f.write(context_content)
        
        return context_file
    
    @pytest.fixture
    def sample_hook(self, temp_dirs):
        """Create a sample hook template."""
        hook_file = temp_dirs["examples"] / "hooks" / "automation" / "test-hook.yaml"
        hook_content = """name: test-hook
description: Test hook for unit tests
version: "1.0"
type: context
trigger: on_session_start
timeout: 30
enabled: true
context:
  sources:
    - contexts/test-context.md
  tags: [test]
"""
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        return hook_file
    
    def test_installer_initialization(self, installer, installation_config):
        """Test installer initialization."""
        assert installer.config == installation_config
        assert installer.directory_manager is not None
        assert installer.validator is not None
        assert isinstance(installer.installed_templates, dict)
        assert isinstance(installer.installation_history, list)
    
    def test_discover_templates_empty_directory(self, installer):
        """Test template discovery with empty examples directory."""
        templates = installer.discover_templates()
        assert isinstance(templates, dict)
        assert len(templates) == 0
    
    def test_discover_profile_templates(self, installer, sample_profile):
        """Test discovery of profile templates."""
        templates = installer.discover_templates(TemplateType.PROFILE)
        
        assert len(templates) == 1
        assert "basic/test-profile" in templates
        
        template = templates["basic/test-profile"]
        assert template.name == "basic/test-profile"
        assert template.template_type == TemplateType.PROFILE
        assert template.source_path == sample_profile
        assert template.target_path.name == "test-profile.json"
    
    def test_discover_context_templates(self, installer, sample_context):
        """Test discovery of context templates."""
        templates = installer.discover_templates(TemplateType.CONTEXT)
        
        assert len(templates) == 1
        assert "domains/test-context" in templates
        
        template = templates["domains/test-context"]
        assert template.name == "domains/test-context"
        assert template.template_type == TemplateType.CONTEXT
        assert template.source_path == sample_context
        assert template.target_path.name == "test-context.md"
    
    def test_discover_hook_templates(self, installer, sample_hook):
        """Test discovery of hook templates."""
        templates = installer.discover_templates(TemplateType.HOOK)
        
        assert len(templates) == 1
        assert "automation/test-hook" in templates
        
        template = templates["automation/test-hook"]
        assert template.name == "automation/test-hook"
        assert template.template_type == TemplateType.HOOK
        assert template.source_path == sample_hook
        assert template.target_path.name == "test-hook.yaml"
    
    def test_discover_all_templates(self, installer, sample_profile, sample_context, sample_hook):
        """Test discovery of all template types."""
        templates = installer.discover_templates()
        
        assert len(templates) == 3
        assert "basic/test-profile" in templates
        assert "domains/test-context" in templates
        assert "automation/test-hook" in templates
    
    @patch('src.ai_configurator.core.template_installer.TemplateValidator')
    def test_install_template_not_found(self, mock_validator, installer):
        """Test installation of non-existent template."""
        result = installer.install_template("non-existent")
        
        assert not result.success
        assert result.template_name == "non-existent"
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]
    
    def test_install_template_validation_failure(self, installer, sample_profile):
        """Test installation with validation failure."""
        from src.ai_configurator.core.models import ConfigurationError
        
        # Mock validation failure directly on the installer's validator
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path=str(sample_profile),
                    error_type="validation_error",
                    message="Validation error",
                    severity="error"
                )],
                warnings=[]
            )
            
            result = installer.install_template("basic/test-profile")
            
            assert not result.success
            assert "validation failed" in result.errors[0].lower()
    
    @patch('src.ai_configurator.core.template_installer.TemplateValidator')
    def test_install_template_success(self, mock_validator, installer, sample_profile):
        """Test successful template installation."""
        # Mock successful validation
        mock_validator.return_value.validate_profile_template.return_value = ValidationReport(
            is_valid=True,
            errors=[],
            warnings=[]
        )
        
        result = installer.install_template("basic/test-profile")
        
        assert result.success
        assert result.template_name == "basic/test-profile"
        assert result.template_type == TemplateType.PROFILE
        assert len(result.installed_files) == 1
        assert result.installed_files[0].exists()
        
        # Check that template is tracked
        assert "basic/test-profile" in installer.installed_templates
        assert len(installer.installation_history) == 1
    
    @patch('src.ai_configurator.core.template_installer.TemplateValidator')
    def test_install_template_dry_run(self, mock_validator, installer, sample_profile):
        """Test template installation in dry run mode."""
        installer.config.dry_run = True
        
        # Mock successful validation
        mock_validator.return_value.validate_profile_template.return_value = ValidationReport(
            is_valid=True,
            errors=[],
            warnings=[]
        )
        
        result = installer.install_template("basic/test-profile")
        
        assert result.success
        assert len(result.warnings) == 1
        assert "dry run" in result.warnings[0].lower()
        assert not result.installed_files[0].exists()  # File should not actually exist
    
    def test_install_template_conflict_skip(self, installer, sample_profile, temp_dirs):
        """Test installation with conflict resolution set to skip."""
        # Create conflicting file
        target_file = temp_dirs["target"] / "profiles" / "test-profile.json"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text('{"existing": "config"}')
        
        installer.config.conflict_resolution.mode = InstallationMode.SKIP
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            result = installer.install_template("basic/test-profile")
        
        assert not result.success
        # Original file should remain unchanged
        assert json.loads(target_file.read_text()) == {"existing": "config"}
    
    def test_install_template_conflict_overwrite(self, installer, sample_profile, temp_dirs):
        """Test installation with conflict resolution set to overwrite."""
        # Create conflicting file
        target_file = temp_dirs["target"] / "profiles" / "test-profile.json"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text('{"existing": "config"}')
        
        installer.config.conflict_resolution.mode = InstallationMode.OVERWRITE
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_validate:
            mock_validate.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            result = installer.install_template("basic/test-profile")
        
        assert result.success
        # File should be overwritten
        new_content = json.loads(target_file.read_text())
        assert new_content["name"] == "test-profile"
    
    def test_install_multiple_templates(self, installer, sample_profile, sample_context):
        """Test installation of multiple templates."""
        # Mock successful validation directly on the installer's validator
        with patch.object(installer.validator, 'validate_profile_template') as mock_profile_validate, \
             patch.object(installer.validator, 'validate_context_template') as mock_context_validate:
            
            mock_profile_validate.return_value = ValidationReport(
                is_valid=True, errors=[], warnings=[]
            )
            mock_context_validate.return_value = ValidationReport(
                is_valid=True, errors=[], warnings=[]
            )
            
            results = installer.install_multiple_templates([
                "basic/test-profile",
                "domains/test-context"
            ])
            
            assert len(results) == 2
            assert all(result.success for result in results)
            assert len(installer.installed_templates) == 2
            assert len(installer.installation_history) == 2
    
    def test_list_installed_templates(self, installer):
        """Test listing installed templates."""
        # Add some mock installed templates
        template1 = TemplateMetadata(
            name="test1",
            template_type=TemplateType.PROFILE,
            source_path=Path("source1"),
            target_path=Path("target1")
        )
        template2 = TemplateMetadata(
            name="test2",
            template_type=TemplateType.CONTEXT,
            source_path=Path("source2"),
            target_path=Path("target2")
        )
        
        installer.installed_templates["test1"] = template1
        installer.installed_templates["test2"] = template2
        
        installed = installer.list_installed_templates()
        
        assert len(installed) == 2
        assert "test1" in installed
        assert "test2" in installed
        assert installed["test1"] == template1
        assert installed["test2"] == template2
    
    def test_get_installation_history(self, installer):
        """Test getting installation history."""
        # Add some mock history
        result1 = InstallationResult(
            success=True,
            template_name="test1",
            template_type=TemplateType.PROFILE,
            installed_files=[],
            skipped_files=[],
            errors=[],
            warnings=[]
        )
        result2 = InstallationResult(
            success=False,
            template_name="test2",
            template_type=TemplateType.CONTEXT,
            installed_files=[],
            skipped_files=[],
            errors=["Test error"],
            warnings=[]
        )
        
        installer.installation_history.extend([result1, result2])
        
        history = installer.get_installation_history()
        
        assert len(history) == 2
        assert history[0] == result1
        assert history[1] == result2
    
    @patch('src.ai_configurator.core.template_installer.TemplateValidator')
    def test_uninstall_template(self, mock_validator, installer, sample_profile, temp_dirs):
        """Test template uninstallation."""
        # First install a template
        mock_validator.return_value.validate_profile_template.return_value = ValidationReport(
            is_valid=True, errors=[], warnings=[]
        )
        
        install_result = installer.install_template("basic/test-profile")
        assert install_result.success
        
        # Verify file exists
        target_file = temp_dirs["target"] / "profiles" / "test-profile.json"
        assert target_file.exists()
        
        # Now uninstall
        success = installer.uninstall_template("basic/test-profile")
        
        assert success
        assert not target_file.exists()
        assert "basic/test-profile" not in installer.installed_templates
    
    def test_uninstall_template_not_installed(self, installer):
        """Test uninstalling a template that wasn't installed."""
        success = installer.uninstall_template("non-existent")
        assert not success
    
    def test_template_metadata_creation(self):
        """Test TemplateMetadata creation and defaults."""
        metadata = TemplateMetadata(
            name="test",
            template_type=TemplateType.PROFILE,
            source_path=Path("source"),
            target_path=Path("target")
        )
        
        assert metadata.name == "test"
        assert metadata.template_type == TemplateType.PROFILE
        assert metadata.version == "1.0.0"
        assert metadata.description == ""
        assert metadata.dependencies == []
        assert metadata.tags == []
    
    def test_installation_result_creation(self):
        """Test InstallationResult creation."""
        result = InstallationResult(
            success=True,
            template_name="test",
            template_type=TemplateType.PROFILE,
            installed_files=[Path("file1"), Path("file2")],
            skipped_files=[Path("file3")],
            errors=["error1"],
            warnings=["warning1"]
        )
        
        assert result.success
        assert result.template_name == "test"
        assert result.template_type == TemplateType.PROFILE
        assert len(result.installed_files) == 2
        assert len(result.skipped_files) == 1
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.backup_path is None


class TestConflictResolution:
    """Test cases for conflict resolution functionality."""
    
    def test_conflict_resolution_defaults(self):
        """Test ConflictResolution default values."""
        resolution = ConflictResolution()
        
        assert resolution.mode == InstallationMode.SKIP
        assert resolution.backup_existing is True
        assert resolution.preserve_user_modifications is True
        assert resolution.merge_strategy == "user_priority"
    
    def test_installation_config_defaults(self):
        """Test InstallationConfig default values."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target_dir = temp_path / "target"
            examples_dir = temp_path / "examples"
            target_dir.mkdir()
            examples_dir.mkdir()
            
            config = InstallationConfig(
                target_directory=target_dir,
                examples_directory=examples_dir
            )
            
            assert config.target_directory == target_dir
            assert config.examples_directory == examples_dir
            assert isinstance(config.conflict_resolution, ConflictResolution)
        assert config.validate_before_install is True
        assert config.validate_after_install is True
        assert config.create_backup is True
        assert config.dry_run is False


if __name__ == "__main__":
    pytest.main([__file__])