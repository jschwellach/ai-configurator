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
    EnhancedProfileConfig,
    HookConfig,
    ContextFile,
    ValidationReport,
)
from .platform_utils import PlatformManager
from .yaml_loader import YamlConfigLoader
from .markdown_processor import MarkdownProcessor
from .config_merger import ConfigurationMerger
from .profile_manager import ProfileManager
from .hook_manager import HookManager
from .context_manager import ContextManager
from .file_watcher import FileWatcher


class ConfigurationManager(LoggerMixin):
    """Manages Amazon Q CLI configuration files and operations with YAML/MD support."""
    
    def __init__(self, platform_manager: Optional[PlatformManager] = None):
        self.platform = platform_manager or PlatformManager()
        self.config_dir = self.platform.get_amazonq_config_dir()
        self.app_data_dir = self.platform.get_app_data_dir()
        self.backup_dir = self.app_data_dir / "backups"
        
        # Ensure directories exist
        self.platform.ensure_directories()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize new YAML/MD components
        self.yaml_loader = YamlConfigLoader(self.config_dir)
        self.markdown_processor = MarkdownProcessor(base_path=self.config_dir)
        self.config_merger = ConfigurationMerger()
        self.profile_manager = ProfileManager(self.config_dir, self.yaml_loader)
        self.hook_manager = HookManager(self.config_dir, self.yaml_loader)
        self.context_manager = ContextManager(self.config_dir, self.markdown_processor)
        
        # Initialize file watcher for hot-reload
        self.file_watcher = FileWatcher()
        self._setup_file_watching()
    
    def _setup_file_watching(self):
        """Set up file watching for hot-reload functionality."""
        try:
            # Watch profiles directory
            profiles_dir = self.config_dir / "profiles"
            if profiles_dir.exists():
                self.file_watcher.watch_directory(profiles_dir, self._on_profile_change)
            
            # Watch hooks directory
            hooks_dir = self.config_dir / "hooks"
            if hooks_dir.exists():
                self.file_watcher.watch_directory(hooks_dir, self._on_hook_change)
            
            # Watch contexts directory
            contexts_dir = self.config_dir / "contexts"
            if contexts_dir.exists():
                self.file_watcher.watch_directory(contexts_dir, self._on_context_change)
            
            self.logger.info("File watching enabled for hot-reload")
        except Exception as e:
            self.logger.warning(f"Failed to setup file watching: {e}")
    
    def _on_profile_change(self, file_path: Path):
        """Handle profile file changes."""
        self.logger.info(f"Profile configuration changed: {file_path}")
        # Clear cache if implemented
        if hasattr(self.profile_manager, 'clear_cache'):
            self.profile_manager.clear_cache()
    
    def _on_hook_change(self, file_path: Path):
        """Handle hook file changes."""
        self.logger.info(f"Hook configuration changed: {file_path}")
        # Clear cache if implemented
        if hasattr(self.hook_manager, 'clear_cache'):
            self.hook_manager.clear_cache()
    
    def _on_context_change(self, file_path: Path):
        """Handle context file changes."""
        self.logger.info(f"Context file changed: {file_path}")
        # Clear cache if implemented
        if hasattr(self.context_manager, 'clear_cache'):
            self.context_manager.clear_cache()
    
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
        """List available profiles (legacy JSON only for backward compatibility)."""
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
    
    # Enhanced profile management methods
    def load_enhanced_profile(self, profile_name: str) -> Optional[EnhancedProfileConfig]:
        """Load enhanced profile configuration (YAML or JSON)."""
        return self.profile_manager.load_profile(profile_name)
    
    def list_all_profiles(self) -> List[str]:
        """List all available profiles (both YAML and JSON)."""
        return self.profile_manager.list_profiles()
    
    def validate_profile(self, profile_name: str) -> ValidationReport:
        """Validate a specific profile configuration."""
        return self.profile_manager.validate_profile(profile_name)
    
    def activate_profile(self, profile_name: str) -> bool:
        """Activate a profile and load its configuration."""
        try:
            profile = self.load_enhanced_profile(profile_name)
            if not profile:
                self.logger.error(f"Profile '{profile_name}' not found")
                return False
            
            # Load associated contexts
            contexts = []
            for context_path in profile.contexts:
                full_path = self.config_dir / context_path
                if full_path.exists():
                    context = self.load_context_file(full_path)
                    if context:
                        contexts.append(context)
                else:
                    self.logger.warning(f"Context file not found: {context_path}")
            
            # Load associated hooks
            hooks = []
            for trigger, hook_refs in profile.hooks.items():
                for hook_ref in hook_refs:
                    hook_name = hook_ref.get("name") if isinstance(hook_ref, dict) else hook_ref
                    hook = self.load_hook(hook_name)
                    if hook:
                        hooks.append((trigger, hook))
                    else:
                        self.logger.warning(f"Hook not found: {hook_name}")
            
            self.logger.info(f"Profile '{profile_name}' activated with {len(contexts)} contexts and {len(hooks)} hooks")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate profile '{profile_name}': {e}")
            return False
    
    # Hook management methods
    def load_hook(self, hook_name: str) -> Optional[HookConfig]:
        """Load a specific hook configuration."""
        return self.hook_manager.load_hook_config(hook_name)
    
    def list_hooks(self) -> Dict[str, List[str]]:
        """List all available hooks by category."""
        return self.hook_manager.discover_hooks()
    
    def get_hooks_by_trigger(self, trigger: str) -> List[HookConfig]:
        """Get all hooks for a specific trigger."""
        from .models import HookTrigger
        trigger_enum = HookTrigger(trigger) if isinstance(trigger, str) else trigger
        return self.hook_manager.load_hooks_by_trigger(trigger_enum)
    
    def validate_hook(self, hook_name: str) -> ValidationReport:
        """Validate a specific hook configuration."""
        from .models import ConfigurationError
        
        errors = []
        warnings = []
        hook_file = self.config_dir / "hooks" / f"{hook_name}.yaml"
        
        # Check if hook exists
        hook = self.load_hook(hook_name)
        if not hook:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="missing_file",
                message=f"Hook not found: {hook_name}",
                severity="error"
            ))
            return ValidationReport(is_valid=False, errors=errors, warnings=warnings)
        
        # Basic validation
        if not hook.name:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="missing_field",
                message=f"Hook missing name: {hook_name}",
                severity="error"
            ))
        
        if not hook.trigger:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="missing_field",
                message=f"Hook missing trigger: {hook_name}",
                severity="error"
            ))
        
        if not hook.type:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="missing_field",
                message=f"Hook missing type: {hook_name}",
                severity="error"
            ))
        
        # Validate context sources if it's a context hook
        if hook.type == "context" and hook.context:
            for source in hook.context.sources:
                source_path = self.config_dir / source
                if not source_path.exists():
                    warnings.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="missing_reference",
                        message=f"Hook context source not found: {source}",
                        severity="warning"
                    ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    # Context management methods
    def load_context_file(self, file_path: PathLike) -> Optional[ContextFile]:
        """Load a context file with frontmatter processing."""
        # Convert to relative path from config_dir
        file_path = Path(file_path)
        if file_path.is_absolute():
            try:
                relative_path = file_path.relative_to(self.config_dir)
                path_str = str(relative_path)
            except ValueError:
                path_str = str(file_path)
        else:
            path_str = str(file_path)
        
        context_files = self.context_manager.load_context_files([path_str])
        return context_files[0] if context_files else None
    
    def list_context_files(self) -> Dict[str, List[str]]:
        """List all available context files by category."""
        return self.context_manager.list_available_contexts()
    
    def validate_context_file(self, file_path: PathLike) -> ValidationReport:
        """Validate a specific context file."""
        from .models import ConfigurationError
        
        file_path = Path(file_path)
        errors = []
        warnings = []
        
        # Check if file exists
        if not file_path.exists():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="missing_file",
                message=f"Context file not found: {file_path}",
                severity="error"
            ))
            return ValidationReport(is_valid=False, errors=errors, warnings=warnings)
        
        # Try to load the file
        try:
            context_file = self.load_context_file(file_path)
            if not context_file:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="load_error",
                    message=f"Failed to load context file: {file_path}",
                    severity="error"
                ))
            else:
                # Basic validation
                if not context_file.content.strip():
                    warnings.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="empty_content",
                        message=f"Context file is empty: {file_path}",
                        severity="warning"
                    ))
                
                # Check frontmatter
                if context_file.metadata:
                    if 'title' not in context_file.metadata:
                        warnings.append(ConfigurationError(
                            file_path=str(file_path),
                            error_type="missing_metadata",
                            message=f"Context file missing title in frontmatter: {file_path}",
                            severity="warning"
                        ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="validation_error",
                message=f"Error validating context file {file_path}: {e}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    # Configuration merging and migration
    def merge_configurations(self, yaml_config: Dict[str, Any], json_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge YAML and JSON configurations."""
        return self.config_merger.merge_profile_configs(yaml_config, json_config)
    
    def migrate_json_to_yaml(self, profile_name: str) -> bool:
        """Migrate a JSON profile to YAML format."""
        try:
            yaml_config = self.config_merger.convert_json_to_yaml_profile(profile_name, self.config_dir)
            if not yaml_config:
                return False
            
            # Save the YAML configuration
            yaml_file = self.config_dir / "profiles" / f"{profile_name}.yaml"
            return self.save_yaml_file(yaml_file, yaml_config)
            
        except Exception as e:
            self.logger.error(f"Failed to migrate profile '{profile_name}' to YAML: {e}")
            return False
    
    # Enhanced validation
    def validate_complete_configuration(self) -> ValidationReport:
        """Perform comprehensive validation of all configuration components."""
        from .models import ConfigurationError
        
        errors = []
        warnings = []
        
        # Validate base configuration
        base_validation = self.validate_configuration()
        # Convert string errors/warnings to ConfigurationError objects
        for error in base_validation.errors:
            errors.append(ConfigurationError(
                file_path="configuration",
                error_type="config_error",
                message=error,
                severity="error"
            ))
        for warning in base_validation.warnings:
            warnings.append(ConfigurationError(
                file_path="configuration",
                error_type="config_warning",
                message=warning,
                severity="warning"
            ))
        
        # Validate all profiles
        profiles_dict = self.list_all_profiles()
        for profile_name in profiles_dict.keys():
            profile_validation = self.validate_profile(profile_name)
            if not profile_validation.is_valid:
                errors.extend(profile_validation.errors)
            warnings.extend(profile_validation.warnings)
        
        # Validate all hooks
        hooks_dict = self.list_hooks()
        all_hook_names = []
        for category, hook_list in hooks_dict.items():
            all_hook_names.extend(hook_list)
        
        for hook_name in all_hook_names:
            hook_validation = self.validate_hook(hook_name)
            if not hook_validation.is_valid:
                errors.extend(hook_validation.errors)
            warnings.extend(hook_validation.warnings)
        
        # Validate context files
        context_files_dict = self.list_context_files()
        all_context_files = []
        for category, file_list in context_files_dict.items():
            for file_path in file_list:
                all_context_files.append(self.config_dir / file_path)
        
        for context_file in all_context_files:
            context_validation = self.validate_context_file(context_file)
            if not context_validation.is_valid:
                errors.extend(context_validation.errors)
            warnings.extend(context_validation.warnings)
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    # Workflow execution methods
    def execute_profile_workflow(self, profile_name: str) -> bool:
        """Execute complete profile activation workflow."""
        try:
            # Validate profile first
            validation = self.validate_profile(profile_name)
            if not validation.is_valid:
                self.logger.error(f"Profile validation failed: {validation.errors}")
                return False
            
            # Activate profile
            if not self.activate_profile(profile_name):
                return False
            
            # Execute session start hooks
            session_hooks = self.get_hooks_by_trigger("on_session_start")
            for hook in session_hooks:
                self.logger.info(f"Executing session start hook: {hook.name}")
                # Hook execution would be implemented here
            
            self.logger.info(f"Profile workflow completed for '{profile_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Profile workflow failed for '{profile_name}': {e}")
            return False
    
    def cleanup(self):
        """Clean up resources and stop file watching."""
        try:
            self.file_watcher.stop_watching()
            self.logger.info("Configuration manager cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
