"""
Unit tests for template updater functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from packaging import version

from src.ai_configurator.core.template_updater import (
    TemplateUpdater,
    UpdateStrategy,
    UpdateConfig,
    VersionInfo,
    UpdateResult
)
from src.ai_configurator.core.template_installer import (
    TemplateInstaller,
    TemplateType,
    TemplateMetadata,
    InstallationConfig,
    InstallationResult
)


class TestTemplateUpdater:
    """Test cases for TemplateUpdater class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            examples_dir = temp_path / "examples"
            target_dir = temp_path / "target"
            
            # Create directory structure
            examples_dir.mkdir()
            target_dir.mkdir()
            (target_dir / "profiles").mkdir()
            (target_dir / "contexts").mkdir()
            (target_dir / "hooks").mkdir()
            
            yield {
                "examples": examples_dir,
                "target": target_dir,
                "temp": temp_path
            }
    
    @pytest.fixture
    def mock_installer(self, temp_dirs):
        """Create mock installer for testing."""
        config = InstallationConfig(
            target_directory=temp_dirs["target"],
            examples_directory=temp_dirs["examples"]
        )
        installer = Mock(spec=TemplateInstaller)
        installer.config = config
        return installer
    
    @pytest.fixture
    def update_config(self):
        """Create update configuration for testing."""
        return UpdateConfig(
            strategy=UpdateStrategy.CONSERVATIVE,
            backup_before_update=True,
            validate_after_update=True,
            max_backup_count=5
        )
    
    @pytest.fixture
    def updater(self, mock_installer, update_config):
        """Create template updater instance."""
        return TemplateUpdater(mock_installer, update_config)
    
    @pytest.fixture
    def sample_template_metadata(self, temp_dirs):
        """Create sample template metadata."""
        return TemplateMetadata(
            name="test-template",
            template_type=TemplateType.PROFILE,
            source_path=temp_dirs["examples"] / "test-template.json",
            target_path=temp_dirs["target"] / "profiles" / "test-template.json",
            version="1.0.0"
        )
    
    def test_updater_initialization(self, updater, mock_installer, update_config):
        """Test updater initialization."""
        assert updater.installer == mock_installer
        assert updater.config == update_config
        assert isinstance(updater.update_history, list)
        assert isinstance(updater.version_cache, dict)
        assert updater.backup_dir.exists()
    
    def test_version_info_creation(self):
        """Test VersionInfo dataclass creation."""
        version_info = VersionInfo(
            current="1.0.0",
            available="1.1.0",
            is_newer=True,
            is_compatible=True,
            changelog="Bug fixes and improvements"
        )
        
        assert version_info.current == "1.0.0"
        assert version_info.available == "1.1.0"
        assert version_info.is_newer is True
        assert version_info.is_compatible is True
        assert version_info.changelog == "Bug fixes and improvements"
        assert version_info.breaking_changes == []
    
    def test_update_result_creation(self, temp_dirs):
        """Test UpdateResult dataclass creation."""
        result = UpdateResult(
            success=True,
            template_name="test-template",
            old_version="1.0.0",
            new_version="1.1.0",
            updated_files=[temp_dirs["target"] / "test.json"],
            backup_path=temp_dirs["temp"] / "backup",
            errors=[],
            warnings=["Minor warning"]
        )
        
        assert result.success is True
        assert result.template_name == "test-template"
        assert result.old_version == "1.0.0"
        assert result.new_version == "1.1.0"
        assert len(result.updated_files) == 1
        assert len(result.warnings) == 1
        assert result.rollback_available is True
    
    def test_get_profile_version(self, updater, temp_dirs):
        """Test extracting version from profile JSON."""
        profile_file = temp_dirs["examples"] / "test-profile.json"
        profile_data = {
            "metadata": {
                "version": "2.1.0"
            },
            "name": "test-profile"
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        version_str = updater._get_profile_version(profile_file)
        assert version_str == "2.1.0"
    
    def test_get_profile_version_fallback(self, updater, temp_dirs):
        """Test profile version fallback to root level."""
        profile_file = temp_dirs["examples"] / "test-profile.json"
        profile_data = {
            "name": "test-profile",
            "version": "1.5.0"
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        version_str = updater._get_profile_version(profile_file)
        assert version_str == "1.5.0"
    
    def test_get_profile_version_default(self, updater, temp_dirs):
        """Test profile version default when not found."""
        profile_file = temp_dirs["examples"] / "test-profile.json"
        profile_data = {
            "name": "test-profile"
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f)
        
        version_str = updater._get_profile_version(profile_file)
        assert version_str == "1.0.0"
    
    def test_get_context_version(self, updater, temp_dirs):
        """Test extracting version from context markdown frontmatter."""
        context_file = temp_dirs["examples"] / "test-context.md"
        context_content = """---
title: Test Context
version: "1.2.0"
description: Test context
---

# Test Context

This is a test context.
"""
        
        with open(context_file, 'w') as f:
            f.write(context_content)
        
        version_str = updater._get_context_version(context_file)
        assert version_str == "1.2.0"
    
    def test_get_context_version_no_frontmatter(self, updater, temp_dirs):
        """Test context version when no frontmatter exists."""
        context_file = temp_dirs["examples"] / "test-context.md"
        context_content = """# Test Context

This is a test context without frontmatter.
"""
        
        with open(context_file, 'w') as f:
            f.write(context_content)
        
        version_str = updater._get_context_version(context_file)
        assert version_str == "1.0.0"
    
    def test_get_hook_version(self, updater, temp_dirs):
        """Test extracting version from hook YAML."""
        hook_file = temp_dirs["examples"] / "test-hook.yaml"
        hook_content = """name: test-hook
description: Test hook
version: "1.3.0"
type: context
trigger: on_session_start
"""
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        version_str = updater._get_hook_version(hook_file)
        assert version_str == "1.3.0"
    
    def test_check_compatibility(self, updater):
        """Test version compatibility checking."""
        # Same major version - compatible
        current = version.parse("1.2.0")
        available = version.parse("1.3.0")
        assert updater._check_compatibility(current, available) is True
        
        # Different major version - incompatible
        current = version.parse("1.2.0")
        available = version.parse("2.0.0")
        assert updater._check_compatibility(current, available) is False
    
    def test_compare_versions(self, updater, sample_template_metadata, temp_dirs):
        """Test version comparison between templates."""
        # Create installed template with version 1.0.0
        installed_template = sample_template_metadata
        
        # Create available template with version 1.1.0
        available_template = TemplateMetadata(
            name="test-template",
            template_type=TemplateType.PROFILE,
            source_path=temp_dirs["examples"] / "test-template-new.json",
            target_path=temp_dirs["target"] / "profiles" / "test-template.json",
            version="1.1.0"
        )
        
        # Mock version extraction
        with patch.object(updater, '_get_template_version') as mock_get_version:
            mock_get_version.side_effect = lambda t: t.version
            
            version_info = updater._compare_versions(installed_template, available_template)
            
            assert version_info.current == "1.0.0"
            assert version_info.available == "1.1.0"
            assert version_info.is_newer is True
            assert version_info.is_compatible is True
    
    def test_check_for_updates_no_updates(self, updater):
        """Test checking for updates when none are available."""
        # Mock installer methods
        updater.installer.list_installed_templates.return_value = {
            "test-template": TemplateMetadata(
                name="test-template",
                template_type=TemplateType.PROFILE,
                source_path=Path("source"),
                target_path=Path("target"),
                version="1.0.0"
            )
        }
        
        updater.installer.discover_templates.return_value = {
            "test-template": TemplateMetadata(
                name="test-template",
                template_type=TemplateType.PROFILE,
                source_path=Path("source"),
                target_path=Path("target"),
                version="1.0.0"  # Same version
            )
        }
        
        with patch.object(updater, '_get_template_version', return_value="1.0.0"):
            updates = updater.check_for_updates()
            
            assert len(updates) == 0
    
    def test_check_for_updates_with_updates(self, updater):
        """Test checking for updates when updates are available."""
        # Mock installer methods
        updater.installer.list_installed_templates.return_value = {
            "test-template": TemplateMetadata(
                name="test-template",
                template_type=TemplateType.PROFILE,
                source_path=Path("source"),
                target_path=Path("target"),
                version="1.0.0"
            )
        }
        
        updater.installer.discover_templates.return_value = {
            "test-template": TemplateMetadata(
                name="test-template",
                template_type=TemplateType.PROFILE,
                source_path=Path("source"),
                target_path=Path("target"),
                version="1.1.0"  # Newer version
            )
        }
        
        with patch.object(updater, '_get_template_version') as mock_get_version:
            mock_get_version.side_effect = lambda t: t.version
            
            updates = updater.check_for_updates()
            
            assert len(updates) == 1
            assert "test-template" in updates
            assert updates["test-template"].is_newer is True
    
    def test_create_update_backup(self, updater, temp_dirs):
        """Test creating backup before update."""
        # Create a test template file
        template_file = temp_dirs["target"] / "profiles" / "test-template.json"
        template_file.parent.mkdir(parents=True, exist_ok=True)
        template_data = {"name": "test-template", "version": "1.0.0"}
        
        with open(template_file, 'w') as f:
            json.dump(template_data, f)
        
        # Mock installed templates
        template_meta = TemplateMetadata(
            name="test-template",
            template_type=TemplateType.PROFILE,
            source_path=Path("source"),
            target_path=template_file,
            version="1.0.0"
        )
        
        updater.installer.list_installed_templates.return_value = {
            "test-template": template_meta
        }
        
        with patch.object(updater, '_get_template_version', return_value="1.0.0"):
            backup_path = updater._create_update_backup("test-template")
            
            assert backup_path is not None
            assert backup_path.exists()
            assert (backup_path / "backup_metadata.json").exists()
            assert (backup_path / "test-template.json").exists()
    
    def test_update_template_no_update_available(self, updater):
        """Test updating template when no update is available."""
        with patch.object(updater, 'check_for_updates', return_value={}):
            result = updater.update_template("test-template")
            
            assert result.success is False
            assert "No update available" in result.errors[0]
    
    def test_update_template_incompatible_version(self, updater):
        """Test updating template with incompatible version."""
        version_info = VersionInfo(
            current="1.0.0",
            available="2.0.0",
            is_newer=True,
            is_compatible=False
        )
        
        with patch.object(updater, 'check_for_updates', return_value={"test-template": version_info}):
            result = updater.update_template("test-template")
            
            assert result.success is False
            assert "Incompatible version" in result.errors[0]
    
    def test_update_template_success(self, updater, temp_dirs):
        """Test successful template update."""
        version_info = VersionInfo(
            current="1.0.0",
            available="1.1.0",
            is_newer=True,
            is_compatible=True
        )
        
        backup_path = temp_dirs["temp"] / "backup"
        backup_path.mkdir()
        
        install_result = InstallationResult(
            success=True,
            template_name="test-template",
            template_type=TemplateType.PROFILE,
            installed_files=[temp_dirs["target"] / "test.json"],
            skipped_files=[],
            errors=[],
            warnings=[]
        )
        
        with patch.object(updater, 'check_for_updates', return_value={"test-template": version_info}), \
             patch.object(updater, '_create_update_backup', return_value=backup_path), \
             patch.object(updater.installer, 'uninstall_template', return_value=True), \
             patch.object(updater.installer, 'install_template', return_value=install_result):
            
            result = updater.update_template("test-template")
            
            assert result.success is True
            assert result.old_version == "1.0.0"
            assert result.new_version == "1.1.0"
            assert len(result.updated_files) == 1
    
    def test_update_template_with_rollback(self, updater, temp_dirs):
        """Test template update with rollback on failure."""
        version_info = VersionInfo(
            current="1.0.0",
            available="1.1.0",
            is_newer=True,
            is_compatible=True
        )
        
        backup_path = temp_dirs["temp"] / "backup"
        backup_path.mkdir()
        
        failed_install_result = InstallationResult(
            success=False,
            template_name="test-template",
            template_type=TemplateType.PROFILE,
            installed_files=[],
            skipped_files=[],
            errors=["Installation failed"],
            warnings=[]
        )
        
        with patch.object(updater, 'check_for_updates', return_value={"test-template": version_info}), \
             patch.object(updater, '_create_update_backup', return_value=backup_path), \
             patch.object(updater.installer, 'uninstall_template', return_value=True), \
             patch.object(updater.installer, 'install_template', return_value=failed_install_result), \
             patch.object(updater, '_rollback_from_backup', return_value=True):
            
            result = updater.update_template("test-template")
            
            assert result.success is False
            assert "rolled back" in result.errors[1]
    
    def test_update_multiple_templates(self, updater):
        """Test updating multiple templates."""
        with patch.object(updater, 'update_template') as mock_update:
            mock_update.side_effect = [
                UpdateResult(True, "template1", "1.0.0", "1.1.0", [], None, [], []),
                UpdateResult(True, "template2", "1.0.0", "1.1.0", [], None, [], [])
            ]
            
            results = updater.update_multiple_templates(["template1", "template2"])
            
            assert len(results) == 2
            assert all(result.success for result in results)
            assert mock_update.call_count == 2
    
    def test_find_backup(self, updater, temp_dirs):
        """Test finding backup by template name."""
        # Create a mock backup directory
        backup_name = "test-template_20240101_120000"
        backup_dir = updater.backup_dir / backup_name
        backup_dir.mkdir(parents=True)
        
        metadata = {
            "template_name": "test-template",
            "backup_timestamp": "20240101_120000",
            "original_version": "1.0.0"
        }
        
        with open(backup_dir / "backup_metadata.json", 'w') as f:
            json.dump(metadata, f)
        
        found_backup = updater._find_backup("test-template")
        
        assert found_backup == backup_dir
    
    def test_find_backup_specific_timestamp(self, updater, temp_dirs):
        """Test finding backup by specific timestamp."""
        # Create multiple backup directories
        timestamps = ["20240101_120000", "20240102_120000"]
        
        for ts in timestamps:
            backup_name = f"test-template_{ts}"
            backup_dir = updater.backup_dir / backup_name
            backup_dir.mkdir(parents=True)
            
            metadata = {
                "template_name": "test-template",
                "backup_timestamp": ts,
                "original_version": "1.0.0"
            }
            
            with open(backup_dir / "backup_metadata.json", 'w') as f:
                json.dump(metadata, f)
        
        # Find specific backup
        found_backup = updater._find_backup("test-template", "20240101_120000")
        
        assert found_backup.name == "test-template_20240101_120000"
    
    def test_list_backups(self, updater, temp_dirs):
        """Test listing available backups."""
        # Create mock backup directories
        backup_data = [
            ("test-template_20240101_120000", "test-template", "20240101_120000", "1.0.0"),
            ("other-template_20240102_120000", "other-template", "20240102_120000", "2.0.0")
        ]
        
        for backup_name, template_name, timestamp, version in backup_data:
            backup_dir = updater.backup_dir / backup_name
            backup_dir.mkdir(parents=True)
            
            metadata = {
                "template_name": template_name,
                "backup_timestamp": timestamp,
                "original_version": version,
                "backup_type": "pre_update"
            }
            
            with open(backup_dir / "backup_metadata.json", 'w') as f:
                json.dump(metadata, f)
        
        # List all backups
        backups = updater.list_backups()
        
        assert len(backups) == 2
        assert backups[0]['template_name'] in ['test-template', 'other-template']
        
        # List backups for specific template
        template_backups = updater.list_backups("test-template")
        
        assert len(template_backups) == 1
        assert template_backups[0]['template_name'] == "test-template"
    
    def test_get_update_history(self, updater):
        """Test getting update history."""
        # Add some mock history
        result1 = UpdateResult(True, "template1", "1.0.0", "1.1.0", [], None, [], [])
        result2 = UpdateResult(False, "template2", "1.0.0", "1.1.0", [], None, ["Error"], [])
        
        updater.update_history.extend([result1, result2])
        
        history = updater.get_update_history()
        
        assert len(history) == 2
        assert history[0] == result1
        assert history[1] == result2
    
    def test_cleanup_old_backups(self, updater, temp_dirs):
        """Test cleanup of old backups."""
        # Set max backup count to 2
        updater.config.max_backup_count = 2
        
        # Create 4 backup directories
        timestamps = ["20240101_120000", "20240102_120000", "20240103_120000", "20240104_120000"]
        
        for ts in timestamps:
            backup_name = f"test-template_{ts}"
            backup_dir = updater.backup_dir / backup_name
            backup_dir.mkdir(parents=True)
            
            metadata = {
                "template_name": "test-template",
                "backup_timestamp": ts,
                "original_version": "1.0.0"
            }
            
            with open(backup_dir / "backup_metadata.json", 'w') as f:
                json.dump(metadata, f)
        
        # Run cleanup
        updater._cleanup_old_backups("test-template")
        
        # Check that only 2 newest backups remain
        remaining_backups = [d for d in updater.backup_dir.iterdir() 
                           if d.is_dir() and d.name.startswith("test-template_")]
        
        assert len(remaining_backups) == 2
        
        # Check that the newest ones are kept
        backup_names = [d.name for d in remaining_backups]
        assert "test-template_20240104_120000" in backup_names
        assert "test-template_20240103_120000" in backup_names


class TestUpdateConfig:
    """Test cases for UpdateConfig class."""
    
    def test_update_config_defaults(self):
        """Test UpdateConfig default values."""
        config = UpdateConfig()
        
        assert config.strategy == UpdateStrategy.CONSERVATIVE
        assert config.backup_before_update is True
        assert config.validate_after_update is True
        assert config.preserve_user_modifications is True
        assert config.auto_resolve_conflicts is False
        assert config.max_backup_count == 10
        assert config.check_compatibility is True
    
    def test_update_config_custom_values(self):
        """Test UpdateConfig with custom values."""
        config = UpdateConfig(
            strategy=UpdateStrategy.AUTOMATIC,
            backup_before_update=False,
            max_backup_count=5
        )
        
        assert config.strategy == UpdateStrategy.AUTOMATIC
        assert config.backup_before_update is False
        assert config.max_backup_count == 5


if __name__ == "__main__":
    pytest.main([__file__])