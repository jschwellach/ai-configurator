"""
Template update and version management system.

This module provides functionality to check for template updates, manage versions,
and safely apply updates with backup and rollback capabilities.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from packaging import version

import yaml
from pydantic import BaseModel, Field

from ..utils.logging import LoggerMixin
from .models import (
    ConfigurationError,
    ValidationReport,
    PathLike
)
from .template_installer import (
    TemplateInstaller,
    TemplateType,
    TemplateMetadata,
    InstallationConfig,
    InstallationResult
)


class UpdateStrategy(str, Enum):
    """Strategies for handling template updates."""
    CONSERVATIVE = "conservative"  # Only update if explicitly requested
    AUTOMATIC = "automatic"       # Auto-update compatible versions
    PROMPT = "prompt"            # Ask user for each update
    FORCE = "force"              # Force update regardless of conflicts


@dataclass
class VersionInfo:
    """Version information for a template."""
    current: str
    available: str
    is_newer: bool
    is_compatible: bool
    changelog: Optional[str] = None
    breaking_changes: List[str] = None
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []


@dataclass
class UpdateResult:
    """Result of a template update operation."""
    success: bool
    template_name: str
    old_version: str
    new_version: str
    updated_files: List[Path]
    backup_path: Optional[Path]
    errors: List[str]
    warnings: List[str]
    rollback_available: bool = True


class UpdateConfig(BaseModel):
    """Configuration for template updates."""
    strategy: UpdateStrategy = UpdateStrategy.CONSERVATIVE
    backup_before_update: bool = True
    validate_after_update: bool = True
    preserve_user_modifications: bool = True
    auto_resolve_conflicts: bool = False
    max_backup_count: int = 10
    check_compatibility: bool = True


class TemplateUpdater(LoggerMixin):
    """
    Manages template updates and version control.
    
    Handles:
    - Version checking and comparison
    - Safe updates with backup/rollback
    - Conflict resolution during updates
    - Update history tracking
    """
    
    def __init__(self, installer: TemplateInstaller, config: UpdateConfig = None):
        """
        Initialize the template updater.
        
        Args:
            installer: TemplateInstaller instance for performing installations
            config: Update configuration
        """
        self.installer = installer
        self.config = config or UpdateConfig()
        
        # Track update history
        self.update_history: List[UpdateResult] = []
        self.version_cache: Dict[str, VersionInfo] = {}
        
        # Backup management
        self.backup_dir = self.installer.config.target_directory / "backups" / "updates"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self, template_names: Optional[List[str]] = None) -> Dict[str, VersionInfo]:
        """
        Check for available updates for installed templates.
        
        Args:
            template_names: Optional list of specific templates to check
            
        Returns:
            Dictionary mapping template names to their version information
        """
        updates_available = {}
        
        try:
            # Get installed templates
            installed_templates = self.installer.list_installed_templates()
            
            # Filter by requested templates if specified
            if template_names:
                installed_templates = {
                    name: meta for name, meta in installed_templates.items()
                    if name in template_names
                }
            
            # Discover available templates from examples
            available_templates = self.installer.discover_templates()
            
            for template_name, installed_meta in installed_templates.items():
                if template_name in available_templates:
                    available_meta = available_templates[template_name]
                    version_info = self._compare_versions(installed_meta, available_meta)
                    
                    if version_info.is_newer:
                        updates_available[template_name] = version_info
                        self.logger.info(f"Update available for '{template_name}': {version_info.current} -> {version_info.available}")
            
            # Cache the results
            self.version_cache.update(updates_available)
            
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
        
        return updates_available
    
    def _compare_versions(self, installed: TemplateMetadata, available: TemplateMetadata) -> VersionInfo:
        """Compare versions between installed and available templates."""
        try:
            current_version = self._get_template_version(installed)
            available_version = self._get_template_version(available)
            
            # Parse versions
            current_ver = version.parse(current_version)
            available_ver = version.parse(available_version)
            
            is_newer = available_ver > current_ver
            is_compatible = self._check_compatibility(current_ver, available_ver)
            
            # Get changelog if available
            changelog = self._get_changelog(available, current_version, available_version)
            breaking_changes = self._get_breaking_changes(available, current_version, available_version)
            
            return VersionInfo(
                current=current_version,
                available=available_version,
                is_newer=is_newer,
                is_compatible=is_compatible,
                changelog=changelog,
                breaking_changes=breaking_changes
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to compare versions for template: {e}")
            return VersionInfo(
                current="unknown",
                available="unknown",
                is_newer=False,
                is_compatible=False
            )
    
    def _get_template_version(self, template: TemplateMetadata) -> str:
        """Extract version from template metadata."""
        try:
            if template.template_type == TemplateType.PROFILE:
                return self._get_profile_version(template.source_path)
            elif template.template_type == TemplateType.CONTEXT:
                return self._get_context_version(template.source_path)
            elif template.template_type == TemplateType.HOOK:
                return self._get_hook_version(template.source_path)
            else:
                return template.version
        except Exception:
            return "1.0.0"  # Default version
    
    def _get_profile_version(self, profile_path: Path) -> str:
        """Get version from profile JSON file."""
        try:
            with open(profile_path, 'r') as f:
                data = json.load(f)
            
            # Check metadata first
            if 'metadata' in data and 'version' in data['metadata']:
                return data['metadata']['version']
            
            # Fallback to root level version
            return data.get('version', '1.0.0')
            
        except Exception:
            return "1.0.0"
    
    def _get_context_version(self, context_path: Path) -> str:
        """Get version from context markdown frontmatter."""
        try:
            content = context_path.read_text()
            
            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        return frontmatter.get('version', '1.0.0')
            
            return "1.0.0"
            
        except Exception:
            return "1.0.0"
    
    def _get_hook_version(self, hook_path: Path) -> str:
        """Get version from hook YAML file."""
        try:
            with open(hook_path, 'r') as f:
                data = yaml.safe_load(f)
            
            return data.get('version', '1.0.0')
            
        except Exception:
            return "1.0.0"
    
    def _check_compatibility(self, current: version.Version, available: version.Version) -> bool:
        """Check if the available version is compatible with current."""
        # Simple compatibility check: same major version
        return current.major == available.major
    
    def _get_changelog(self, template: TemplateMetadata, from_version: str, to_version: str) -> Optional[str]:
        """Get changelog for version update."""
        try:
            # Look for CHANGELOG.md in template directory
            changelog_path = template.source_path.parent / "CHANGELOG.md"
            if changelog_path.exists():
                content = changelog_path.read_text()
                # Extract relevant section (simplified)
                return f"Changelog available at {changelog_path}"
            
            return None
            
        except Exception:
            return None
    
    def _get_breaking_changes(self, template: TemplateMetadata, from_version: str, to_version: str) -> List[str]:
        """Get list of breaking changes between versions."""
        try:
            # This would typically parse changelog or metadata
            # For now, return empty list
            return []
            
        except Exception:
            return []
    
    def update_template(self, template_name: str, force: bool = False) -> UpdateResult:
        """
        Update a specific template to the latest version.
        
        Args:
            template_name: Name of template to update
            force: Force update even if there are conflicts
            
        Returns:
            UpdateResult with update details
        """
        try:
            # Check if update is available
            updates = self.check_for_updates([template_name])
            if template_name not in updates:
                return UpdateResult(
                    success=False,
                    template_name=template_name,
                    old_version="unknown",
                    new_version="unknown",
                    updated_files=[],
                    backup_path=None,
                    errors=["No update available or template not found"],
                    warnings=[]
                )
            
            version_info = updates[template_name]
            
            # Check compatibility if required
            if self.config.check_compatibility and not version_info.is_compatible and not force:
                return UpdateResult(
                    success=False,
                    template_name=template_name,
                    old_version=version_info.current,
                    new_version=version_info.available,
                    updated_files=[],
                    backup_path=None,
                    errors=["Incompatible version - use force=True to override"],
                    warnings=version_info.breaking_changes
                )
            
            # Create backup if configured
            backup_path = None
            if self.config.backup_before_update:
                backup_path = self._create_update_backup(template_name)
                if not backup_path:
                    return UpdateResult(
                        success=False,
                        template_name=template_name,
                        old_version=version_info.current,
                        new_version=version_info.available,
                        updated_files=[],
                        backup_path=None,
                        errors=["Failed to create backup"],
                        warnings=[]
                    )
            
            # Perform the update
            result = self._perform_update(template_name, version_info, backup_path, force)
            
            # Track the update
            if result.success:
                self.update_history.append(result)
                self.logger.info(f"Successfully updated '{template_name}' from {version_info.current} to {version_info.available}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update template '{template_name}': {e}")
            return UpdateResult(
                success=False,
                template_name=template_name,
                old_version="unknown",
                new_version="unknown",
                updated_files=[],
                backup_path=None,
                errors=[f"Update failed: {e}"],
                warnings=[]
            )
    
    def _create_update_backup(self, template_name: str) -> Optional[Path]:
        """Create backup before updating template."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{template_name}_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Get installed template info
            installed_templates = self.installer.list_installed_templates()
            if template_name not in installed_templates:
                return None
            
            template = installed_templates[template_name]
            
            # Backup the current template files
            if template.target_path.exists():
                if template.target_path.is_file():
                    # Single file template
                    backup_file = backup_path / template.target_path.name
                    shutil.copy2(template.target_path, backup_file)
                else:
                    # Directory template (workflow)
                    shutil.copytree(template.target_path, backup_path / template.target_path.name)
            
            # Create backup metadata
            metadata = {
                "template_name": template_name,
                "backup_timestamp": timestamp,
                "original_version": self._get_template_version(template),
                "backup_type": "pre_update"
            }
            
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Created backup for '{template_name}' at {backup_path}")
            
            # Clean up old backups if needed
            self._cleanup_old_backups(template_name)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for '{template_name}': {e}")
            return None
    
    def _cleanup_old_backups(self, template_name: str):
        """Remove old backups beyond the configured limit."""
        try:
            # Find all backups for this template
            backups = []
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith(f"{template_name}_"):
                    metadata_file = backup_dir / "backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            backups.append((backup_dir, metadata.get('backup_timestamp', '')))
                        except Exception:
                            continue
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remove excess backups
            if len(backups) > self.config.max_backup_count:
                for backup_dir, _ in backups[self.config.max_backup_count:]:
                    shutil.rmtree(backup_dir)
                    self.logger.info(f"Removed old backup: {backup_dir}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old backups: {e}")
    
    def _perform_update(self, template_name: str, version_info: VersionInfo, backup_path: Optional[Path], force: bool) -> UpdateResult:
        """Perform the actual template update."""
        try:
            # Uninstall current version
            uninstall_success = self.installer.uninstall_template(template_name)
            if not uninstall_success:
                return UpdateResult(
                    success=False,
                    template_name=template_name,
                    old_version=version_info.current,
                    new_version=version_info.available,
                    updated_files=[],
                    backup_path=backup_path,
                    errors=["Failed to uninstall current version"],
                    warnings=[]
                )
            
            # Install new version
            install_result = self.installer.install_template(template_name)
            
            if install_result.success:
                return UpdateResult(
                    success=True,
                    template_name=template_name,
                    old_version=version_info.current,
                    new_version=version_info.available,
                    updated_files=install_result.installed_files,
                    backup_path=backup_path,
                    errors=[],
                    warnings=install_result.warnings
                )
            else:
                # Installation failed, try to rollback
                if backup_path:
                    rollback_success = self._rollback_from_backup(template_name, backup_path)
                    if rollback_success:
                        return UpdateResult(
                            success=False,
                            template_name=template_name,
                            old_version=version_info.current,
                            new_version=version_info.available,
                            updated_files=[],
                            backup_path=backup_path,
                            errors=install_result.errors + ["Update failed, rolled back to previous version"],
                            warnings=[]
                        )
                
                return UpdateResult(
                    success=False,
                    template_name=template_name,
                    old_version=version_info.current,
                    new_version=version_info.available,
                    updated_files=[],
                    backup_path=backup_path,
                    errors=install_result.errors,
                    warnings=[]
                )
                
        except Exception as e:
            return UpdateResult(
                success=False,
                template_name=template_name,
                old_version=version_info.current,
                new_version=version_info.available,
                updated_files=[],
                backup_path=backup_path,
                errors=[f"Update failed: {e}"],
                warnings=[]
            )
    
    def update_multiple_templates(self, template_names: List[str], force: bool = False) -> List[UpdateResult]:
        """
        Update multiple templates.
        
        Args:
            template_names: List of template names to update
            force: Force updates even if there are conflicts
            
        Returns:
            List of UpdateResult objects
        """
        results = []
        
        for template_name in template_names:
            result = self.update_template(template_name, force)
            results.append(result)
            
            # Stop on first failure if not forcing
            if not result.success and not force:
                self.logger.error(f"Stopping updates due to failure: {template_name}")
                break
        
        return results
    
    def rollback_update(self, template_name: str, backup_timestamp: Optional[str] = None) -> bool:
        """
        Rollback a template to a previous version from backup.
        
        Args:
            template_name: Name of template to rollback
            backup_timestamp: Specific backup to rollback to (latest if None)
            
        Returns:
            True if rollback was successful
        """
        try:
            # Find the backup to rollback to
            backup_path = self._find_backup(template_name, backup_timestamp)
            if not backup_path:
                self.logger.error(f"No backup found for template '{template_name}'")
                return False
            
            return self._rollback_from_backup(template_name, backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to rollback template '{template_name}': {e}")
            return False
    
    def _find_backup(self, template_name: str, timestamp: Optional[str] = None) -> Optional[Path]:
        """Find backup directory for template."""
        try:
            backups = []
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith(f"{template_name}_"):
                    metadata_file = backup_dir / "backup_metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            backup_ts = metadata.get('backup_timestamp', '')
                            if timestamp is None or backup_ts == timestamp:
                                backups.append((backup_dir, backup_ts))
                        except Exception:
                            continue
            
            if not backups:
                return None
            
            # Sort by timestamp (newest first) and return the first match
            backups.sort(key=lambda x: x[1], reverse=True)
            return backups[0][0]
            
        except Exception:
            return None
    
    def _rollback_from_backup(self, template_name: str, backup_path: Path) -> bool:
        """Restore template from backup."""
        try:
            # Get current installed template info
            installed_templates = self.installer.list_installed_templates()
            if template_name in installed_templates:
                # Uninstall current version
                self.installer.uninstall_template(template_name)
            
            # Restore from backup
            metadata_file = backup_path / "backup_metadata.json"
            if not metadata_file.exists():
                self.logger.error(f"Backup metadata not found: {metadata_file}")
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Find the backed up files and restore them
            for item in backup_path.iterdir():
                if item.name == "backup_metadata.json":
                    continue
                
                # Determine target path based on template type
                if template_name in installed_templates:
                    template = installed_templates[template_name]
                    target_path = template.target_path
                else:
                    # Guess target path based on backup structure
                    if item.suffix == '.json':
                        target_path = self.installer.config.target_directory / "profiles" / item.name
                    elif item.suffix == '.md':
                        target_path = self.installer.config.target_directory / "contexts" / item.name
                    elif item.suffix == '.yaml':
                        target_path = self.installer.config.target_directory / "hooks" / item.name
                    else:
                        continue
                
                # Restore the file/directory
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                if item.is_file():
                    shutil.copy2(item, target_path)
                else:
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
            
            self.logger.info(f"Successfully rolled back '{template_name}' from backup {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback from backup: {e}")
            return False
    
    def list_available_updates(self) -> Dict[str, VersionInfo]:
        """Get list of all available updates."""
        return self.check_for_updates()
    
    def get_update_history(self) -> List[UpdateResult]:
        """Get history of template updates."""
        return self.update_history.copy()
    
    def list_backups(self, template_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            template_name: Optional filter by template name
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        try:
            for backup_dir in self.backup_dir.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                metadata_file = backup_dir / "backup_metadata.json"
                if not metadata_file.exists():
                    continue
                
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Filter by template name if specified
                    if template_name and metadata.get('template_name') != template_name:
                        continue
                    
                    backup_info = {
                        'backup_path': str(backup_dir),
                        'template_name': metadata.get('template_name'),
                        'timestamp': metadata.get('backup_timestamp'),
                        'version': metadata.get('original_version'),
                        'backup_type': metadata.get('backup_type', 'unknown')
                    }
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to read backup metadata from {backup_dir}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
        
        return backups