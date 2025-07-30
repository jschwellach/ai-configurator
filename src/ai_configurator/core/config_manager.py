"""Configuration file management and operations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import ValidationError

from ..utils.logging import LoggerMixin
from .models import (
    BackupMetadata,
    ConfigDict,
    ConfigurationState,
    GlobalContext,
    MCPConfiguration,
    PathLike,
    ProfileConfig,
    ProfileContext,
    ValidationResult,
)
from .platform import PlatformManager


class ConfigurationManager(LoggerMixin):
    """Manages Amazon Q CLI configuration files and operations."""
    
    def __init__(self, platform_manager: Optional[PlatformManager] = None):
        self.platform = platform_manager or PlatformManager()
        self.config_dir = self.platform.get_amazonq_config_dir()
        self.app_data_dir = self.platform.get_app_data_dir()
        self.backup_dir = self.app_data_dir / "backups"
        
        # Ensure directories exist
        self.platform.ensure_directories()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def load_mcp_config(self) -> Optional[MCPConfiguration]:
        """Load MCP server configuration."""
        mcp_file = self.config_dir / "mcp.json"
        
        if not mcp_file.exists():
            self.logger.warning(f"MCP configuration file not found: {mcp_file}")
            return None
        
        try:
            with open(mcp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return MCPConfiguration(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Failed to load MCP configuration: {e}")
            return None
    
    def save_mcp_config(self, config: MCPConfiguration) -> bool:
        """Save MCP server configuration."""
        mcp_file = self.config_dir / "mcp.json"
        
        try:
            # Ensure directory exists
            mcp_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict and save
            data = config.dict(by_alias=True)
            with open(mcp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Set appropriate permissions
            if not self.platform.is_windows():
                mcp_file.chmod(0o600)
            
            self.logger.info(f"MCP configuration saved to {mcp_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save MCP configuration: {e}")
            return False
    
    def load_global_context(self) -> Optional[GlobalContext]:
        """Load global context configuration."""
        context_file = self.config_dir / "global_context.json"
        
        if not context_file.exists():
            self.logger.warning(f"Global context file not found: {context_file}")
            return None
        
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return GlobalContext(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Failed to load global context: {e}")
            return None
    
    def save_global_context(self, context: GlobalContext) -> bool:
        """Save global context configuration."""
        context_file = self.config_dir / "global_context.json"
        
        try:
            context_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = context.dict()
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Global context saved to {context_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save global context: {e}")
            return False
    
    def load_profile_context(self, profile_name: str) -> Optional[ProfileContext]:
        """Load context configuration for a specific profile."""
        profile_dir = self.config_dir / "profiles" / profile_name
        context_file = profile_dir / "context.json"
        
        if not context_file.exists():
            self.logger.warning(f"Profile context file not found: {context_file}")
            return None
        
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProfileContext(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Failed to load profile context for {profile_name}: {e}")
            return None
    
    def save_profile_context(self, profile_name: str, context: ProfileContext) -> bool:
        """Save context configuration for a specific profile."""
        profile_dir = self.config_dir / "profiles" / profile_name
        context_file = profile_dir / "context.json"
        
        try:
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            data = context.dict()
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Profile context saved for {profile_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save profile context for {profile_name}: {e}")
            return False
    
    def list_profiles(self) -> List[str]:
        """List available profiles."""
        profiles_dir = self.config_dir / "profiles"
        
        if not profiles_dir.exists():
            return []
        
        profiles = []
        for item in profiles_dir.iterdir():
            if item.is_dir() and (item / "context.json").exists():
                profiles.append(item.name)
        
        return sorted(profiles)
    
    def get_active_profile(self) -> Optional[str]:
        """Get the currently active profile."""
        # This could be stored in a separate file or determined by other means
        # For now, we'll check if there's a default profile
        profiles = self.list_profiles()
        if "default" in profiles:
            return "default"
        elif profiles:
            return profiles[0]
        return None
    
    def create_backup(self, description: Optional[str] = None) -> Optional[str]:
        """Create a backup of the current configuration."""
        if not self.config_dir.exists():
            self.logger.warning("No configuration directory to backup")
            return None
        
        timestamp = datetime.now().isoformat()
        backup_id = f"backup_{timestamp.replace(':', '-').replace('.', '-')}"
        backup_path = self.backup_dir / backup_id
        
        try:
            # Copy entire configuration directory
            shutil.copytree(self.config_dir, backup_path)
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=timestamp,
                description=description,
                profile=self.get_active_profile(),
                version="0.1.0",  # TODO: Get from package
                platform=self.platform.get_platform_name()
            )
            
            # Save metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata.dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Backup created: {backup_id}")
            return backup_id
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def list_backups(self) -> List[BackupMetadata]:
        """List available backups."""
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_path in self.backup_dir.iterdir():
            if not backup_path.is_dir():
                continue
            
            metadata_file = backup_path / "backup_metadata.json"
            if not metadata_file.exists():
                continue
            
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                backups.append(BackupMetadata(**data))
            except Exception as e:
                self.logger.warning(f"Failed to load backup metadata for {backup_path.name}: {e}")
        
        return sorted(backups, key=lambda x: x.timestamp, reverse=True)
    
    def restore_backup(self, backup_id: str) -> bool:
        """Restore configuration from a backup."""
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            self.logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            # Create a backup of current state before restoring
            current_backup = self.create_backup("Pre-restore backup")
            if current_backup:
                self.logger.info(f"Created pre-restore backup: {current_backup}")
            
            # Remove current configuration
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)
            
            # Copy backup to configuration directory
            shutil.copytree(backup_path, self.config_dir)
            
            # Remove the backup metadata from the restored config
            metadata_file = self.config_dir / "backup_metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            self.logger.info(f"Configuration restored from backup: {backup_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_id}: {e}")
            return False
    
    def validate_configuration(self) -> ValidationResult:
        """Validate the current configuration."""
        errors = []
        warnings = []
        checked_items = {}
        
        # Check if config directory exists
        checked_items["config_directory"] = self.config_dir.exists()
        if not checked_items["config_directory"]:
            errors.append(f"Configuration directory not found: {self.config_dir}")
        
        # Check MCP configuration
        mcp_config = self.load_mcp_config()
        checked_items["mcp_config"] = mcp_config is not None
        if not checked_items["mcp_config"]:
            warnings.append("MCP configuration not found or invalid")
        
        # Check global context
        global_context = self.load_global_context()
        checked_items["global_context"] = global_context is not None
        if not checked_items["global_context"]:
            warnings.append("Global context configuration not found or invalid")
        
        # Check profiles
        profiles = self.list_profiles()
        checked_items["profiles"] = len(profiles) > 0
        if not checked_items["profiles"]:
            warnings.append("No profiles found")
        
        # Check Amazon Q CLI installation
        checked_items["amazonq_cli"] = self.platform.is_amazonq_installed()
        if not checked_items["amazonq_cli"]:
            errors.append("Amazon Q CLI not installed or not accessible")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            checked_items=checked_items
        )
    
    def get_configuration_state(self) -> ConfigurationState:
        """Get the current state of the configuration."""
        return ConfigurationState(
            amazonq_installed=self.platform.is_amazonq_installed(),
            amazonq_version=self.platform.get_amazonq_version(),
            config_dir_exists=self.config_dir.exists(),
            config_dir_path=str(self.config_dir),
            active_profile=self.get_active_profile(),
            installed_mcp_servers=list(self.load_mcp_config().mcp_servers.keys()) if self.load_mcp_config() else [],
            last_backup=self.list_backups()[0].timestamp if self.list_backups() else None,
            ai_configurator_version="0.1.0",  # TODO: Get from package
            platform=self.platform.get_platform_name()
        )
    
    def load_yaml_file(self, file_path: PathLike) -> Optional[Dict[str, Any]]:
        """Load a YAML file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.warning(f"YAML file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to load YAML file {file_path}: {e}")
            return None
    
    def save_yaml_file(self, file_path: PathLike, data: Dict[str, Any]) -> bool:
        """Save data to a YAML file."""
        file_path = Path(file_path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"YAML file saved: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save YAML file {file_path}: {e}")
            return False
