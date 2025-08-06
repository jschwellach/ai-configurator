"""
Installation Tracker for managing installed configuration metadata.

This module provides the InstallationTracker class that handles tracking
of installed configurations, their metadata, versions, and status.
"""

import json
import hashlib
import platform
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime
import uuid

from ..utils.logging import LoggerMixin
from .models import (
    InstallationManifest,
    InstalledConfigMetadata,
    InstallationOperation,
    ConfigurationStatus,
    InstallationStatus
)
from .catalog_schema import ConfigMetadata


class InstallationTracker(LoggerMixin):
    """
    Manages tracking of installed configurations including metadata,
    versions, dependencies, and status information.
    """
    
    def __init__(self, target_path: Optional[Path] = None):
        """
        Initialize InstallationTracker.
        
        Args:
            target_path: Target installation directory. Defaults to ~/.kiro/
        """
        self.target_path = target_path or Path.home() / ".kiro"
        self.manifest_file = self.target_path / "installation_manifest.json"
        
        # Ensure target directory exists
        self.target_path.mkdir(parents=True, exist_ok=True)
        
        # Load or create manifest
        self._manifest: Optional[InstallationManifest] = None
        self._load_manifest()
    
    def _load_manifest(self) -> None:
        """Load the installation manifest from disk."""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._manifest = InstallationManifest(**data)
                self.logger.debug(f"Loaded installation manifest with {len(self._manifest.configurations)} configurations")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.error(f"Failed to load installation manifest: {e}")
                self._create_new_manifest()
        else:
            self._create_new_manifest()
    
    def _create_new_manifest(self) -> None:
        """Create a new installation manifest."""
        now = datetime.now().isoformat()
        self._manifest = InstallationManifest(
            created_date=now,
            last_updated=now,
            ai_configurator_version="0.1.0",  # TODO: Get from package
            platform=platform.system(),
            target_directory=str(self.target_path)
        )
        self._save_manifest()
        self.logger.info("Created new installation manifest")
    
    def _save_manifest(self) -> bool:
        """Save the installation manifest to disk."""
        if not self._manifest:
            return False
        
        try:
            # Update last_updated timestamp
            self._manifest.last_updated = datetime.now().isoformat()
            
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(self._manifest.dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Saved installation manifest")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save installation manifest: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> Optional[str]:
        """Calculate SHA256 checksum of a file."""
        if not file_path.exists():
            return None
        
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return None
    
    def record_installation(
        self,
        config_metadata: ConfigMetadata,
        source_path: str,
        target_path: str,
        dependencies: Optional[List[str]] = None,
        installed_by: str = "manual"
    ) -> bool:
        """
        Record the installation of a configuration.
        
        Args:
            config_metadata: Metadata of the installed configuration
            source_path: Original source path in library
            target_path: Installation target path
            dependencies: List of dependency config IDs
            installed_by: How it was installed (manual, dependency, bundle)
            
        Returns:
            True if recording was successful, False otherwise
        """
        if not self._manifest:
            return False
        
        # Calculate checksum of installed file
        target_file = Path(target_path)
        checksum = self._calculate_file_checksum(target_file)
        
        # Create installed config metadata
        installed_config = InstalledConfigMetadata(
            config_id=config_metadata.id,
            name=config_metadata.name,
            version=config_metadata.version,
            config_type=self._determine_config_type(source_path),
            installation_date=datetime.now().isoformat(),
            source_path=source_path,
            target_path=target_path,
            dependencies=dependencies or [],
            installed_by=installed_by,
            status=InstallationStatus.INSTALLED,
            checksum=checksum,
            metadata={
                "author": config_metadata.author,
                "description": config_metadata.description,
                "personas": config_metadata.personas,
                "domains": config_metadata.domains,
                "tags": config_metadata.tags
            }
        )
        
        # Add to manifest
        self._manifest.configurations[config_metadata.id] = installed_config
        
        # Record installation operation
        operation = InstallationOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="install",
            timestamp=datetime.now().isoformat(),
            config_ids=[config_metadata.id],
            success=True,
            metadata={
                "installed_by": installed_by,
                "source_path": source_path,
                "target_path": target_path
            }
        )
        self._manifest.installation_history.append(operation.dict())
        
        # Save manifest
        success = self._save_manifest()
        if success:
            self.logger.info(f"Recorded installation of {config_metadata.id}")
        
        return success
    
    def record_removal(self, config_id: str) -> bool:
        """
        Record the removal of a configuration.
        
        Args:
            config_id: Configuration ID to remove
            
        Returns:
            True if recording was successful, False otherwise
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return False
        
        # Remove from manifest
        removed_config = self._manifest.configurations.pop(config_id)
        
        # Record removal operation
        operation = InstallationOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="remove",
            timestamp=datetime.now().isoformat(),
            config_ids=[config_id],
            success=True,
            metadata={
                "removed_config": removed_config.dict()
            }
        )
        self._manifest.installation_history.append(operation.dict())
        
        # Save manifest
        success = self._save_manifest()
        if success:
            self.logger.info(f"Recorded removal of {config_id}")
        
        return success
    
    def record_update(
        self,
        config_id: str,
        new_version: str,
        new_checksum: Optional[str] = None
    ) -> bool:
        """
        Record the update of a configuration.
        
        Args:
            config_id: Configuration ID to update
            new_version: New version after update
            new_checksum: New file checksum after update
            
        Returns:
            True if recording was successful, False otherwise
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return False
        
        # Update configuration metadata
        config = self._manifest.configurations[config_id]
        old_version = config.version
        config.version = new_version
        config.status = InstallationStatus.INSTALLED
        
        if new_checksum:
            config.checksum = new_checksum
        
        # Record update operation
        operation = InstallationOperation(
            operation_id=str(uuid.uuid4()),
            operation_type="update",
            timestamp=datetime.now().isoformat(),
            config_ids=[config_id],
            success=True,
            metadata={
                "old_version": old_version,
                "new_version": new_version
            }
        )
        self._manifest.installation_history.append(operation.dict())
        
        # Save manifest
        success = self._save_manifest()
        if success:
            self.logger.info(f"Recorded update of {config_id} from {old_version} to {new_version}")
        
        return success
    
    def is_installed(self, config_id: str) -> bool:
        """
        Check if a configuration is installed.
        
        Args:
            config_id: Configuration ID to check
            
        Returns:
            True if installed, False otherwise
        """
        if not self._manifest:
            return False
        
        return config_id in self._manifest.configurations
    
    def get_installed_version(self, config_id: str) -> Optional[str]:
        """
        Get the installed version of a configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Installed version or None if not installed
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return None
        
        return self._manifest.configurations[config_id].version
    
    def get_installed_config(self, config_id: str) -> Optional[InstalledConfigMetadata]:
        """
        Get installed configuration metadata.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            InstalledConfigMetadata or None if not installed
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return None
        
        return self._manifest.configurations[config_id]
    
    def list_installed_configurations(self) -> List[InstalledConfigMetadata]:
        """
        Get list of all installed configurations.
        
        Returns:
            List of InstalledConfigMetadata objects
        """
        if not self._manifest:
            return []
        
        return list(self._manifest.configurations.values())
    
    def list_installed_by_type(self, config_type: str) -> List[InstalledConfigMetadata]:
        """
        Get list of installed configurations by type.
        
        Args:
            config_type: Type of configuration (context, profile, hook, mcp-server)
            
        Returns:
            List of InstalledConfigMetadata objects
        """
        if not self._manifest:
            return []
        
        return [
            config for config in self._manifest.configurations.values()
            if config.config_type == config_type
        ]
    
    def list_installed_by_persona(self, persona: str) -> List[InstalledConfigMetadata]:
        """
        Get list of installed configurations for a specific persona.
        
        Args:
            persona: Target persona
            
        Returns:
            List of InstalledConfigMetadata objects
        """
        if not self._manifest:
            return []
        
        return [
            config for config in self._manifest.configurations.values()
            if persona in config.metadata.get("personas", [])
        ]
    
    def get_dependencies(self, config_id: str) -> List[str]:
        """
        Get dependencies of an installed configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            List of dependency config IDs
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return []
        
        return self._manifest.configurations[config_id].dependencies
    
    def get_dependents(self, config_id: str) -> List[str]:
        """
        Get configurations that depend on the given configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            List of dependent config IDs
        """
        if not self._manifest:
            return []
        
        dependents = []
        for other_id, config in self._manifest.configurations.items():
            if config_id in config.dependencies:
                dependents.append(other_id)
        
        return dependents
    
    def check_integrity(self, config_id: str) -> bool:
        """
        Check integrity of an installed configuration by verifying checksum.
        
        Args:
            config_id: Configuration ID to check
            
        Returns:
            True if integrity is valid, False otherwise
        """
        config = self.get_installed_config(config_id)
        if not config or not config.checksum:
            return False
        
        target_file = Path(config.target_path)
        current_checksum = self._calculate_file_checksum(target_file)
        
        return current_checksum == config.checksum
    
    def update_status(self, config_id: str, status: InstallationStatus) -> bool:
        """
        Update the status of an installed configuration.
        
        Args:
            config_id: Configuration ID
            status: New status
            
        Returns:
            True if update was successful, False otherwise
        """
        if not self._manifest or config_id not in self._manifest.configurations:
            return False
        
        self._manifest.configurations[config_id].status = status
        return self._save_manifest()
    
    def get_installation_history(self, limit: Optional[int] = None) -> List[InstallationOperation]:
        """
        Get installation history.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of InstallationOperation objects
        """
        if not self._manifest:
            return []
        
        operations = [
            InstallationOperation(**op) for op in self._manifest.installation_history
        ]
        
        # Sort by timestamp (newest first)
        operations.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            operations = operations[:limit]
        
        return operations
    
    def get_installation_stats(self) -> Dict[str, Any]:
        """
        Get installation statistics.
        
        Returns:
            Dictionary with installation statistics
        """
        if not self._manifest:
            return {}
        
        configs = list(self._manifest.configurations.values())
        
        # Count by type
        type_counts = {}
        for config in configs:
            type_counts[config.config_type] = type_counts.get(config.config_type, 0) + 1
        
        # Count by status
        status_counts = {}
        for config in configs:
            status_counts[config.status.value] = status_counts.get(config.status.value, 0) + 1
        
        # Count by installed_by
        source_counts = {}
        for config in configs:
            source_counts[config.installed_by] = source_counts.get(config.installed_by, 0) + 1
        
        return {
            "total_installed": len(configs),
            "by_type": type_counts,
            "by_status": status_counts,
            "by_source": source_counts,
            "manifest_created": self._manifest.created_date,
            "last_updated": self._manifest.last_updated,
            "platform": self._manifest.platform
        }
    
    def _determine_config_type(self, source_path: str) -> str:
        """
        Determine configuration type from source path.
        
        Args:
            source_path: Source path in library
            
        Returns:
            Configuration type string
        """
        path_parts = Path(source_path).parts
        
        if "contexts" in path_parts:
            return "context"
        elif "profiles" in path_parts:
            return "profile"
        elif "hooks" in path_parts:
            return "hook"
        elif "mcp-servers" in path_parts:
            return "mcp-server"
        else:
            return "unknown"
    
    def cleanup_broken_installations(self) -> List[str]:
        """
        Clean up broken installations (files that no longer exist).
        
        Returns:
            List of config IDs that were cleaned up
        """
        if not self._manifest:
            return []
        
        cleaned_up = []
        
        for config_id, config in list(self._manifest.configurations.items()):
            target_file = Path(config.target_path)
            if not target_file.exists():
                self.logger.warning(f"Cleaning up broken installation: {config_id}")
                self._manifest.configurations.pop(config_id)
                cleaned_up.append(config_id)
        
        if cleaned_up:
            self._save_manifest()
        
        return cleaned_up
    
    def export_manifest(self, export_path: Path) -> bool:
        """
        Export installation manifest to a file.
        
        Args:
            export_path: Path to export the manifest
            
        Returns:
            True if export was successful, False otherwise
        """
        if not self._manifest:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._manifest.dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported installation manifest to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export manifest: {e}")
            return False
    
    def import_manifest(self, import_path: Path) -> bool:
        """
        Import installation manifest from a file.
        
        Args:
            import_path: Path to import the manifest from
            
        Returns:
            True if import was successful, False otherwise
        """
        if not import_path.exists():
            return False
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._manifest = InstallationManifest(**data)
            success = self._save_manifest()
            
            if success:
                self.logger.info(f"Imported installation manifest from {import_path}")
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to import manifest: {e}")
            return False