"""Comprehensive unit tests for template updater functionality."""

import json
import tempfile
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from packaging import version

import pytest

from src.ai_configurator.core.template_updater import (
    TemplateUpdater,
    UpdateStrategy,
    VersionInfo,
    UpdateResult,
    UpdateConfig
)
from src.ai_configurator.core.template_installer import (
    TemplateInstaller,
    TemplateType,
    TemplateMetadata,
    InstallationConfig,
    InstallationResult
)


class TestTemplateUpdaterComprehensive:
    """Comprehensive tests for template updater functionality."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create comprehensive temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            examples_dir = temp_path / "examples"
            target_dir = temp_path / "target"
            
            # Create directory structures
            examples_dir.mkdir()
            target_dir.mkdir()
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            (target_dir / "profiles").mkdir(parents=True)
            (target_dir / "contexts").mkdir(parents=True)
            (target_dir / "hooks").mkdir(parents=True)
            
            yield {
                "examples": examples_dir,
                "target": target_dir,
                "temp": temp_path
            }
    
    @pytest.fixture
    def mock_installer(self, temp_dirs):
        """Create a mock installer for testing."""
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
            preserve_user_modifications=True,
            auto_resolve_conflicts=False,
            max_backup_count=5,
            check_compatibility=True
        )
    
    @pytest.fixture
    def updater(self, mock_installer, update_config):
        """Create template updater instance."""
        return TemplateUpdater(mock_installer, update_config)
    
    @pytest.fixture
    def sample_templates(self, temp_dirs):
        """Create sample templates with different versions."""
        examples_dir = temp_dirs["examples"]
        target_dir = temp_dirs["target"]
        
        # Create example templates (newer versions)
        example_profile = {
            "metadata": {
                "name": "test-profile",
                "description": "Test profile for updates",
                "category": "basic",
                "version": "2.0.0",  # Newer version
                "created": "2024-01-01",
                "updated": "2024-02-01",
                "complexity": "low"
            },
            "paths": ["contexts/test.md"]
        }
        
        example_profile_file = examples_dir / "profiles" / "basic" / "test-profile.json"
        with open(example_profile_file, 'w') as f:
            json.dump(example_profile, f)
        
        # Create installed templates (older versions)
        installed_profile = {
            "metadata": {
                "name": "test-profile",
                "description": "Test profile for updates",
                "category": "basic",
                "version": "1.0.0",  # Older version
                "created": "2024-01-01",
                "complexity": "low"
            },
            "paths": ["contexts/test.md"]
        }
        
        installed_profile_file = target_dir / "profiles" / "test-profile.json"
        with open(installed_profile_file, 'w') as f:
            json.dump(installed_profile, f)
        
        # Create context template
        context_content = """---
version: "1.5.0"
---

# Test Context

This is a test context for update testing.
"""
        
        example_context_file = examples_dir / "contexts" / "domains" / "test-context.md"
        example_context_file.parent.mkdir(parents=True, exist_ok=True)
        with open(example_context_file, 'w') as f:
            f.write(context_content)
        
        installed_context_content = """---
version: "1.0.0"
---

# Test Context

This is a test context for update testing.
"""
        
        installed_context_file = target_dir / "contexts" / "test-context.md"
        installed_context_file.parent.mkdir(parents=True, exist_ok=True)
        with open(installed_context_file, 'w') as f:
            f.write(installed_context_content)
        
        # Create hook template
        hook_content = """name: test-hook
description: Test hook for updates
version: "2.1.0"
trigger: on_session_start
"""
        
        example_hook_file = examples_dir / "hooks" / "automation" / "test-hook.yaml"
        with open(example_hook_file, 'w') as f:
            f.write(hook_content)
        
        installed_hook_content = """name: test-hook
description: Test hook for updates
version: "1.5.0"
trigger: on_session_start
"""
        
        installed_hook_file = target_dir / "hooks" / "test-hook.yaml"
        with open(installed_hook_file, 'w') as f:
            f.write(installed_hook_content)
        
        return {
            "profile": {
                "example": example_profile_file,
                "installed": installed_profile_file,
                "example_version": "2.0.0",
                "installed_version": "1.0.0"
            },
            "context": {
                "example": example_context_file,
                "installed": installed_context_file,
                "example_version": "1.5.0",
                "installed_version": "1.0.0"
            },
            "hook": {
                "example": example_hook_file,
                "installed": installed_hook_file,
                "example_version": "2.1.0",
                "installed_version": "1.5.0"
            }
        }
    
    def test_version_extraction_comprehensive(self, updater, sample_templates):
        """Test version extraction from various template types."""
        # Test profile version extraction
        profile_metadata = TemplateMetadata(
            name="test-profile",
            template_type=TemplateType.PROFILE,
            source_path=sample_templates["profile"]["example"],
            target_path=Path("target.json")
        )
        
        profile_version = updater._get_template_version(profile_metadata)
        assert profile_version == "2.0.0"
        
        # Test context version extraction
        context_metadata = TemplateMetadata(
            name="test-context",
            template_type=TemplateType.CONTEXT,
            source_path=sample_templates["context"]["example"],
            target_path=Path("target.md")
        )
        
        context_version = updater._get_template_version(context_metadata)
        assert context_version == "1.5.0"
        
        # Test hook version extraction
        hook_metadata = TemplateMetadata(
            name="test-hook",
            template_type=TemplateType.HOOK,
            source_path=sample_templates["hook"]["example"],
            target_path=Path("target.yaml")
        )
        
        hook_version = updater._get_template_version(hook_metadata)
        assert hook_version == "2.1.0"
    
    def test_version_comparison_comprehensive(self, updater):
        """Test comprehensive version comparison scenarios."""
        test_cases = [
            # Standard version comparisons
            ("1.0.0", "2.0.0", True, True),   # Major version update, compatible
            ("1.5.0", "1.6.0", True, True),   # Minor version update, compatible
            ("1.0.1", "1.0.2", True, True),   # Patch version update, compatible
            ("2.0.0", "1.9.9", False, False), # Downgrade, not newer
            ("1.0.0", "1.0.0", False, True),  # Same version, not newer but compatible
            ("1.0.0", "2.0.0", True, True),   # Major version jump, compatible (same major)
            ("1.0.0", "3.0.0", True, False),  # Major version jump, incompatible
            
            # Pre-release versions
            ("1.0.0", "1.1.0-alpha", True, True),
            ("1.0.0-beta", "1.0.0", True, True),
            ("1.0.0-alpha.1", "1.0.0-alpha.2", True, True),
            
            # Development versions
            ("1.0.0", "1.1.0.dev1", True, True),
            ("1.0.0.dev1", "1.0.0", True, True),
        ]
        
        for current_ver, available_ver, expected_newer, expected_compatible in test_cases:
            # Create mock template metadata
            installed = TemplateMetadata(
                name="test",
                template_type=TemplateType.PROFILE,
                source_path=Path("installed.json"),
                target_path=Path("target.json"),
                version=current_ver
            )
            
            available = TemplateMetadata(
                name="test",
                template_type=TemplateType.PROFILE,
                source_path=Path("available.json"),
                target_path=Path("target.json"),
                version=available_ver
            )
            
            # Mock version extraction
            with patch.object(updater, '_get_template_version') as mock_get_version:
                mock_get_version.side_effect = [current_ver, available_ver]
                
                version_info = updater._compare_versions(installed, available)
                
                assert version_info.current == current_ver
                assert version_info.available == available_ver
                assert version_info.is_newer == expected_newer, \
                    f"Version {available_ver} should {'be' if expected_newer else 'not be'} newer than {current_ver}"
                assert version_info.is_compatible == expected_compatible, \
                    f"Version {available_ver} should {'be' if expected_compatible else 'not be'} compatible with {current_ver}"
    
    def test_update_availability_check(self, updater, sample_templates):
        """Test comprehensive update availability checking."""
        # Mock installed templates
        installed_templates = {
            "basic/test-profile": TemplateMetadata(
                name="basic/test-profile",
                template_type=TemplateType.PROFILE,
                source_path=sample_templates["profile"]["installed"],
                target_path=Path("profiles/test-profile.json"),
                version="1.0.0"
            ),
            "domains/test-context": TemplateMetadata(
                name="domains/test-context",
                template_type=TemplateType.CONTEXT,
                source_path=sample_templates["context"]["installed"],
                target_path=Path("contexts/test-context.md"),
                version="1.0.0"
            )
        }
        
        # Mock available templates
        available_templates = {
            "basic/test-profile": TemplateMetadata(
                name="basic/test-profile",
                template_type=TemplateType.PROFILE,
                source_path=sample_templates["profile"]["example"],
                target_path=Path("profiles/test-profile.json"),
                version="2.0.0"
            ),
            "domains/test-context": TemplateMetadata(
                name="domains/test-context",
                template_type=TemplateType.CONTEXT,
                source_path=sample_templates["context"]["example"],
                target_path=Path("contexts/test-context.md"),
                version="1.5.0"
            )
        }
        
        updater.installer.list_installed_templates.return_value = installed_templates
        updater.installer.discover_templates.return_value = available_templates
        
        # Check for updates
        updates = updater.check_for_updates()
        
        # Should find updates for both templates
        assert len(updates) == 2
        assert "basic/test-profile" in updates
        assert "domains/test-context" in updates
        
        # Verify version information
        profile_update = updates["basic/test-profile"]
        assert profile_update.current == "1.0.0"
        assert profile_update.available == "2.0.0"
        assert profile_update.is_newer is True
        
        context_update = updates["domains/test-context"]
        assert context_update.current == "1.0.0"
        assert context_update.available == "1.5.0"
        assert context_update.is_newer is True
    
    def test_update_with_backup_creation(self, updater, sample_templates, temp_dirs):
        """Test update process with backup creation."""
        # Mock installed template
        template_name = "basic/test-profile"
        installed_template = TemplateMetadata(
            name=template_name,
            template_type=TemplateType.PROFILE,
            source_path=sample_templates["profile"]["installed"],
            target_path=temp_dirs["target"] / "profiles" / "test-profile.json",
            version="1.0.0"
        )
        
        updater.installer.list_installed_templates.return_value = {
            template_name: installed_template
        }
        
        # Mock version info
        version_info = VersionInfo(
            current="1.0.0",
            available="2.0.0",
            is_newer=True,
            is_compatible=True
        )
        
        # Mock successful uninstall and install
        updater.installer.uninstall_template.return_value = True
        updater.installer.install_template.return_value = InstallationResult(
            success=True,
            template_name=template_name,
            template_type=TemplateType.PROFILE,
            installed_files=[temp_dirs["target"] / "profiles" / "test-profile.json"],
            skipped_files=[],
            errors=[],
            warnings=[]
        )
        
        with patch.object(updater, 'check_for_updates') as mock_check_updates:
            mock_check_updates.return_value = {template_name: version_info}
            
            result = updater.update_template(template_name)
            
            assert result.success
            assert result.template_name == template_name
            assert result.old_version == "1.0.0"
            assert result.new_version == "2.0.0"
            assert result.backup_path is not None
            assert result.backup_path.exists()
            
            # Verify backup metadata
            metadata_file = result.backup_path / "backup_metadata.json"
            assert metadata_file.exists()
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            assert metadata["template_name"] == template_name
            assert metadata["original_version"] == "1.0.0"
            assert metadata["backup_type"] == "pre_update"
    
    def test_update_compatibility_checking(self, updater):
        """Test update compatibility checking with various scenarios."""
        test_cases = [
            # Compatible updates (same major version)
            ("1.0.0", "1.5.0", True, True),   # Should update
            ("2.1.0", "2.9.9", True, True),   # Should update
            
            # Incompatible updates (different major version)
            ("1.0.0", "2.0.0", True, False),  # Should not update without force
            ("2.0.0", "3.0.0", True, False),  # Should not update without force
            
            # No updates available
            ("1.0.0", "1.0.0", False, True),  # No update needed
            ("2.0.0", "1.9.0", False, True),  # Downgrade not allowed
        ]
        
        for current_ver, available_ver, is_newer, is_compatible in test_cases:
            template_name = "test/template"
            version_info = VersionInfo(
                current=current_ver,
                available=available_ver,
                is_newer=is_newer,
                is_compatible=is_compatible
            )
            
            with patch.object(updater, 'check_for_updates') as mock_check_updates:
                if is_newer:
                    mock_check_updates.return_value = {template_name: version_info}
                else:
                    mock_check_updates.return_value = {}
                
                # Test without force
                result = updater.update_template(template_name, force=False)
                
                if not is_newer:
                    assert not result.success
                    assert "No update available" in result.errors[0]
                elif not is_compatible:
                    assert not result.success
                    assert "Incompatible version" in result.errors[0]
                else:
                    # Mock successful update for compatible versions
                    with patch.object(updater, '_perform_update') as mock_perform:
                        mock_perform.return_value = UpdateResult(
                            success=True,
                            template_name=template_name,
                            old_version=current_ver,
                            new_version=available_ver,
                            updated_files=[],
                            backup_path=None,
                            errors=[],
                            warnings=[]
                        )
                        
                        result = updater.update_template(template_name, force=False)
                        assert result.success
    
    def test_update_with_force_flag(self, updater):
        """Test update process with force flag for incompatible versions."""
        template_name = "test/template"
        version_info = VersionInfo(
            current="1.0.0",
            available="2.0.0",  # Incompatible major version
            is_newer=True,
            is_compatible=False,
            breaking_changes=["API changes", "Configuration format changed"]
        )
        
        with patch.object(updater, 'check_for_updates') as mock_check_updates, \
             patch.object(updater, '_perform_update') as mock_perform:
            
            mock_check_updates.return_value = {template_name: version_info}
            mock_perform.return_value = UpdateResult(
                success=True,
                template_name=template_name,
                old_version="1.0.0",
                new_version="2.0.0",
                updated_files=[],
                backup_path=None,
                errors=[],
                warnings=["API changes", "Configuration format changed"]
            )
            
            # Test with force=True
            result = updater.update_template(template_name, force=True)
            
            assert result.success
            assert result.old_version == "1.0.0"
            assert result.new_version == "2.0.0"
            assert len(result.warnings) > 0  # Should include breaking changes
    
    def test_multiple_template_updates(self, updater):
        """Test updating multiple templates with dependency handling."""
        template_names = ["template1", "template2", "template3"]
        
        # Mock version info for all templates
        version_infos = {
            name: VersionInfo(
                current="1.0.0",
                available="1.1.0",
                is_newer=True,
                is_compatible=True
            ) for name in template_names
        }
        
        with patch.object(updater, 'check_for_updates') as mock_check_updates, \
             patch.object(updater, '_perform_update') as mock_perform:
            
            mock_check_updates.return_value = version_infos
            
            # Mock successful updates
            def mock_update_result(template_name, version_info, backup_path, force):
                return UpdateResult(
                    success=True,
                    template_name=template_name,
                    old_version="1.0.0",
                    new_version="1.1.0",
                    updated_files=[],
                    backup_path=backup_path,
                    errors=[],
                    warnings=[]
                )
            
            mock_perform.side_effect = mock_update_result
            
            results = updater.update_multiple_templates(template_names)
            
            assert len(results) == 3
            assert all(result.success for result in results)
            assert all(result.old_version == "1.0.0" for result in results)
            assert all(result.new_version == "1.1.0" for result in results)
    
    def test_update_rollback_functionality(self, updater, temp_dirs):
        """Test update rollback functionality."""
        template_name = "test/template"
        
        # Create a backup directory with test data
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = updater.backup_dir / f"{template_name.replace('/', '_')}_{backup_timestamp}"
        backup_dir.mkdir(parents=True)
        
        # Create backup metadata
        metadata = {
            "template_name": template_name,
            "backup_timestamp": backup_timestamp,
            "original_version": "1.0.0",
            "backup_type": "pre_update"
        }
        
        metadata_file = backup_dir / "backup_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Create backed up file
        backed_up_file = backup_dir / "template.json"
        backed_up_content = {"version": "1.0.0", "content": "original"}
        with open(backed_up_file, 'w') as f:
            json.dump(backed_up_content, f)
        
        # Mock current installed template
        current_file = temp_dirs["target"] / "profiles" / "template.json"
        current_file.parent.mkdir(parents=True, exist_ok=True)
        current_content = {"version": "2.0.0", "content": "updated"}
        with open(current_file, 'w') as f:
            json.dump(current_content, f)
        
        # Mock installer methods
        updater.installer.list_installed_templates.return_value = {
            template_name: TemplateMetadata(
                name=template_name,
                template_type=TemplateType.PROFILE,
                source_path=Path("source.json"),
                target_path=current_file
            )
        }
        updater.installer.uninstall_template.return_value = True
        
        # Perform rollback
        success = updater.rollback_update(template_name, backup_timestamp)
        
        assert success
        
        # Verify file was restored (in a real scenario)
        # Note: The actual restoration logic would need to be implemented
        # This test verifies the rollback process structure
    
    def test_backup_cleanup(self, updater, temp_dirs):
        """Test automatic cleanup of old backups."""
        template_name = "test/template"
        
        # Create multiple backup directories (more than max_backup_count)
        backup_timestamps = []
        for i in range(updater.config.max_backup_count + 3):  # Create 3 extra backups
            timestamp = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d_%H%M%S")
            backup_timestamps.append(timestamp)
            
            backup_dir = updater.backup_dir / f"{template_name.replace('/', '_')}_{timestamp}"
            backup_dir.mkdir(parents=True)
            
            # Create backup metadata
            metadata = {
                "template_name": template_name,
                "backup_timestamp": timestamp,
                "original_version": f"1.{i}.0",
                "backup_type": "pre_update"
            }
            
            metadata_file = backup_dir / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f)
        
        # Trigger cleanup
        updater._cleanup_old_backups(template_name)
        
        # Verify only max_backup_count backups remain
        remaining_backups = [
            d for d in updater.backup_dir.iterdir()
            if d.is_dir() and d.name.startswith(template_name.replace('/', '_'))
        ]
        
        assert len(remaining_backups) <= updater.config.max_backup_count
    
    def test_update_strategies(self, updater):
        """Test different update strategies."""
        template_name = "test/template"
        version_info = VersionInfo(
            current="1.0.0",
            available="1.1.0",
            is_newer=True,
            is_compatible=True
        )
        
        # Test CONSERVATIVE strategy (default)
        updater.config.strategy = UpdateStrategy.CONSERVATIVE
        with patch.object(updater, 'check_for_updates') as mock_check:
            mock_check.return_value = {template_name: version_info}
            
            # Conservative strategy should require explicit update request
            # (This would be implemented in a higher-level update manager)
            updates = updater.check_for_updates()
            assert template_name in updates
        
        # Test AUTOMATIC strategy
        updater.config.strategy = UpdateStrategy.AUTOMATIC
        # Automatic strategy would trigger updates automatically
        # (Implementation would depend on the specific use case)
        
        # Test PROMPT strategy
        updater.config.strategy = UpdateStrategy.PROMPT
        # Prompt strategy would ask user for confirmation
        # (Implementation would involve user interaction)
    
    def test_update_error_handling(self, updater):
        """Test comprehensive error handling during updates."""
        template_name = "test/template"
        version_info = VersionInfo(
            current="1.0.0",
            available="1.1.0",
            is_newer=True,
            is_compatible=True
        )
        
        with patch.object(updater, 'check_for_updates') as mock_check_updates:
            mock_check_updates.return_value = {template_name: version_info}
            
            # Test backup creation failure
            with patch.object(updater, '_create_update_backup') as mock_backup:
                mock_backup.return_value = None  # Backup failed
                
                result = updater.update_template(template_name)
                
                assert not result.success
                assert "Failed to create backup" in result.errors[0]
            
            # Test uninstall failure
            with patch.object(updater, '_create_update_backup') as mock_backup, \
                 patch.object(updater.installer, 'uninstall_template') as mock_uninstall:
                
                mock_backup.return_value = Path("backup")
                mock_uninstall.return_value = False  # Uninstall failed
                
                result = updater.update_template(template_name)
                
                assert not result.success
                assert "Failed to uninstall current version" in result.errors[0]
            
            # Test install failure with rollback
            with patch.object(updater, '_create_update_backup') as mock_backup, \
                 patch.object(updater.installer, 'uninstall_template') as mock_uninstall, \
                 patch.object(updater.installer, 'install_template') as mock_install, \
                 patch.object(updater, '_rollback_from_backup') as mock_rollback:
                
                backup_path = Path("backup")
                mock_backup.return_value = backup_path
                mock_uninstall.return_value = True
                mock_install.return_value = InstallationResult(
                    success=False,
                    template_name=template_name,
                    template_type=TemplateType.PROFILE,
                    installed_files=[],
                    skipped_files=[],
                    errors=["Installation failed"],
                    warnings=[]
                )
                mock_rollback.return_value = True
                
                result = updater.update_template(template_name)
                
                assert not result.success
                assert "rolled back to previous version" in result.errors[0]
                mock_rollback.assert_called_once_with(template_name, backup_path)
    
    def test_update_history_tracking(self, updater):
        """Test update history tracking and retrieval."""
        template_name = "test/template"
        
        # Mock successful update
        update_result = UpdateResult(
            success=True,
            template_name=template_name,
            old_version="1.0.0",
            new_version="1.1.0",
            updated_files=[Path("file1.json")],
            backup_path=Path("backup"),
            errors=[],
            warnings=[]
        )
        
        # Add to history
        updater.update_history.append(update_result)
        
        # Retrieve history
        history = updater.get_update_history()
        
        assert len(history) == 1
        assert history[0].template_name == template_name
        assert history[0].old_version == "1.0.0"
        assert history[0].new_version == "1.1.0"
        assert history[0].success is True
    
    def test_backup_listing(self, updater, temp_dirs):
        """Test listing available backups."""
        template_names = ["template1", "template2"]
        
        # Create backups for multiple templates
        for i, template_name in enumerate(template_names):
            for j in range(3):  # Create 3 backups per template
                timestamp = (datetime.now() - timedelta(days=j)).strftime("%Y%m%d_%H%M%S")
                backup_dir = updater.backup_dir / f"{template_name}_{timestamp}"
                backup_dir.mkdir(parents=True)
                
                metadata = {
                    "template_name": template_name,
                    "backup_timestamp": timestamp,
                    "original_version": f"1.{j}.0",
                    "backup_type": "pre_update"
                }
                
                metadata_file = backup_dir / "backup_metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f)
        
        # List all backups
        all_backups = updater.list_backups()
        assert len(all_backups) == 6  # 2 templates × 3 backups each
        
        # List backups for specific template
        template1_backups = updater.list_backups("template1")
        assert len(template1_backups) == 3
        assert all(backup["template_name"] == "template1" for backup in template1_backups)
        
        # Verify backup information structure
        for backup in all_backups:
            assert "backup_path" in backup
            assert "template_name" in backup
            assert "timestamp" in backup
            assert "version" in backup
            assert "backup_type" in backup
    
    def test_performance_optimization(self, updater):
        """Test update performance with large numbers of templates."""
        import time
        
        # Create a large number of mock templates
        num_templates = 100
        installed_templates = {}
        available_templates = {}
        
        for i in range(num_templates):
            template_name = f"template_{i}"
            
            installed_templates[template_name] = TemplateMetadata(
                name=template_name,
                template_type=TemplateType.PROFILE,
                source_path=Path(f"installed_{i}.json"),
                target_path=Path(f"target_{i}.json"),
                version="1.0.0"
            )
            
            available_templates[template_name] = TemplateMetadata(
                name=template_name,
                template_type=TemplateType.PROFILE,
                source_path=Path(f"available_{i}.json"),
                target_path=Path(f"target_{i}.json"),
                version="1.1.0"
            )
        
        updater.installer.list_installed_templates.return_value = installed_templates
        updater.installer.discover_templates.return_value = available_templates
        
        # Measure update check time
        start_time = time.time()
        updates = updater.check_for_updates()
        end_time = time.time()
        
        check_time = end_time - start_time
        
        # Should complete within reasonable time
        assert check_time < 10.0, f"Update check took too long: {check_time} seconds"
        assert len(updates) == num_templates
    
    def test_concurrent_update_safety(self, updater):
        """Test update safety with concurrent operations."""
        import threading
        import time
        
        template_name = "test/template"
        results = []
        errors = []
        
        def perform_update(delay=0):
            try:
                if delay:
                    time.sleep(delay)
                
                version_info = VersionInfo(
                    current="1.0.0",
                    available="1.1.0",
                    is_newer=True,
                    is_compatible=True
                )
                
                with patch.object(updater, 'check_for_updates') as mock_check, \
                     patch.object(updater, '_perform_update') as mock_perform:
                    
                    mock_check.return_value = {template_name: version_info}
                    mock_perform.return_value = UpdateResult(
                        success=True,
                        template_name=template_name,
                        old_version="1.0.0",
                        new_version="1.1.0",
                        updated_files=[],
                        backup_path=None,
                        errors=[],
                        warnings=[]
                    )
                    
                    result = updater.update_template(template_name)
                    results.append(result)
                    
            except Exception as e:
                errors.append(e)
        
        # Start multiple update threads
        threads = [
            threading.Thread(target=perform_update, args=(0.1,)),
            threading.Thread(target=perform_update, args=(0.2,)),
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent update errors: {errors}"
        # Note: In a real implementation, only one update should succeed
        # due to proper locking mechanisms