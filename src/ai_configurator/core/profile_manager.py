"""Enhanced profile management system for YAML configurations."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime

from pydantic import ValidationError

from ..utils.logging import LoggerMixin
from .models import (
    EnhancedProfileConfig,
    ValidationReport,
    ConfigurationError,
    PathLike,
)
from .yaml_loader import YamlConfigLoader
from .config_merger import ConfigurationMerger
from .directory_manager import DirectoryManager, ConfigurationType


class ProfileManager(LoggerMixin):
    """
    Enhanced profile management system that handles YAML profile configurations.
    
    This class provides automatic profile discovery, loading, validation, and management
    of YAML-based profile configurations with comprehensive error reporting.
    """
    
    def __init__(self, base_path: Optional[PathLike] = None, yaml_loader: Optional[YamlConfigLoader] = None):
        """
        Initialize the profile manager.
        
        Args:
            base_path: Base directory path for configuration files
            yaml_loader: Optional YamlConfigLoader instance to use
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.yaml_loader = yaml_loader or YamlConfigLoader(self.base_path)
        self.config_merger = ConfigurationMerger()
        
        # Initialize directory manager and create directory structure
        self.directory_manager = DirectoryManager(self.base_path)
        self.directory_manager.create_directory_structure()
        
        # Use directory manager for profiles directory
        self.profiles_dir = self.directory_manager.structure.profiles_dir
        
        # Cache for loaded profiles
        self._profile_cache: Dict[str, EnhancedProfileConfig] = {}
        self._discovery_cache: Optional[List[str]] = None
        self._last_discovery_time: Optional[float] = None
        
    def discover_profiles(self, force_refresh: bool = False) -> List[str]:
        """
        Automatically discover all available YAML profile configurations.
        
        Args:
            force_refresh: Force refresh of discovery cache
            
        Returns:
            List of profile names (without .yaml extension)
        """
        # Check cache first (refresh every 30 seconds)
        current_time = datetime.now().timestamp()
        if (not force_refresh and 
            self._discovery_cache is not None and 
            self._last_discovery_time is not None and 
            current_time - self._last_discovery_time < 30):
            return self._discovery_cache.copy()
        
        profiles = []
        
        if not self.profiles_dir.exists():
            self.logger.warning(f"Profiles directory does not exist: {self.profiles_dir}")
            self._discovery_cache = profiles
            self._last_discovery_time = current_time
            return profiles
        
        # Discover YAML files in profiles directory
        for file_path in self.profiles_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.yaml', '.yml']:
                profile_name = file_path.stem
                profiles.append(profile_name)
                self.logger.debug(f"Discovered profile: {profile_name}")
        
        # Sort profiles alphabetically
        profiles.sort()
        
        # Update cache
        self._discovery_cache = profiles
        self._last_discovery_time = current_time
        
        self.logger.info(f"Discovered {len(profiles)} profiles: {profiles}")
        return profiles.copy()
    
    def validate_profile_name(self, profile_name: str) -> tuple[bool, str]:
        """
        Validate a profile name against naming conventions.
        
        Args:
            profile_name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return self.directory_manager.validate_naming_convention(profile_name, ConfigurationType.PROFILE)
    
    def load_profile(self, profile_name: str, use_cache: bool = True) -> EnhancedProfileConfig:
        """
        Load a profile configuration with comprehensive error handling.
        
        Args:
            profile_name: Name of the profile to load
            use_cache: Whether to use cached profile if available
            
        Returns:
            Loaded and validated profile configuration
            
        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValidationError: If profile configuration is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        # If not using cache, clear any existing cache for this profile
        if not use_cache:
            self._profile_cache.pop(profile_name, None)
            # Also clear yaml_loader cache for this profile
            profile_file = self._get_profile_file_path(profile_name)
            if profile_file:
                self.yaml_loader.clear_cache(profile_file)
        
        # Check cache first
        if use_cache and profile_name in self._profile_cache:
            # Verify file hasn't been modified
            profile_file = self._get_profile_file_path(profile_name)
            if profile_file and profile_file.exists():
                cached_entry = self._profile_cache[profile_name]
                file_mtime = profile_file.stat().st_mtime
                
                # Check if we have cached mtime and if file hasn't changed
                if (hasattr(cached_entry, '_cached_mtime') and 
                    cached_entry._cached_mtime >= file_mtime):
                    self.logger.debug(f"Using cached profile: {profile_name}")
                    return cached_entry
                else:
                    # File has been modified, remove from cache
                    self._profile_cache.pop(profile_name, None)
        
        try:
            # Load profile using yaml_loader
            profile = self.yaml_loader.load_profile(profile_name)
            
            # Add cache metadata
            profile_file = self._get_profile_file_path(profile_name)
            if profile_file and profile_file.exists():
                profile._cached_mtime = profile_file.stat().st_mtime
            
            # Cache the loaded profile only if use_cache is True
            if use_cache:
                self._profile_cache[profile_name] = profile
            
            self.logger.info(f"Successfully loaded profile: {profile_name}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to load profile '{profile_name}': {str(e)}")
            raise
    
    def validate_profile(self, profile_name: str) -> ValidationReport:
        """
        Validate a profile configuration with comprehensive error reporting.
        
        Args:
            profile_name: Name of the profile to validate
            
        Returns:
            Detailed validation report
        """
        profile_file = self._get_profile_file_path(profile_name)
        
        if not profile_file:
            return ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path=f"profiles/{profile_name}.yaml",
                    error_type="FileNotFound",
                    message=f"Profile file not found: {profile_name}",
                    severity="error"
                )],
                files_checked=[f"profiles/{profile_name}.yaml"],
                summary={"errors": 1, "warnings": 0, "info": 0}
            )
        
        # Use yaml_loader's validation
        validation_report = self.yaml_loader.validate_yaml_file(profile_file)
        
        # Add profile-specific validation
        if validation_report.is_valid:
            try:
                profile = self.load_profile(profile_name, use_cache=False)
                additional_errors, additional_warnings = self._validate_profile_references(profile)
                
                validation_report.errors.extend(additional_errors)
                validation_report.warnings.extend(additional_warnings)
                
                # Update validation status
                validation_report.is_valid = len(validation_report.errors) == 0
                validation_report.summary = {
                    "errors": len(validation_report.errors),
                    "warnings": len(validation_report.warnings),
                    "info": len(validation_report.info)
                }
                
            except Exception as e:
                validation_report.errors.append(ConfigurationError(
                    file_path=str(profile_file),
                    error_type="ProfileLoadError",
                    message=f"Failed to load profile for validation: {str(e)}",
                    severity="error"
                ))
                validation_report.is_valid = False
        
        return validation_report
    
    def validate_all_profiles(self) -> ValidationReport:
        """
        Validate all discovered profiles and return a comprehensive report.
        
        Returns:
            Aggregated validation report for all profiles
        """
        profiles = self.discover_profiles()
        
        all_errors = []
        all_warnings = []
        all_info = []
        all_files = []
        
        for profile_name in profiles:
            self.logger.debug(f"Validating profile: {profile_name}")
            report = self.validate_profile(profile_name)
            
            all_errors.extend(report.errors)
            all_warnings.extend(report.warnings)
            all_info.extend(report.info)
            all_files.extend(report.files_checked)
        
        is_valid = len(all_errors) == 0
        
        return ValidationReport(
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            info=all_info,
            files_checked=all_files,
            summary={
                "errors": len(all_errors),
                "warnings": len(all_warnings),
                "info": len(all_info),
                "profiles_checked": len(profiles)
            }
        )
    
    def list_profiles(self, include_descriptions: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        List all available profiles with their metadata.
        
        Args:
            include_descriptions: Whether to include profile descriptions and metadata
            
        Returns:
            Dictionary mapping profile names to their metadata
        """
        profiles = self.discover_profiles()
        profile_info = {}
        
        for profile_name in profiles:
            info = {
                "name": profile_name,
                "file_path": str(self._get_profile_file_path(profile_name)),
                "exists": True
            }
            
            if include_descriptions:
                try:
                    profile = self.load_profile(profile_name)
                    info.update({
                        "description": profile.description,
                        "version": profile.version,
                        "contexts_count": len(profile.contexts),
                        "hooks_count": sum(len(hooks) for hooks in profile.hooks.values()),
                        "mcp_servers_count": len(profile.mcp_servers),
                        "settings": profile.settings.dict() if profile.settings else {}
                    })
                except Exception as e:
                    info.update({
                        "description": None,
                        "version": None,
                        "error": str(e),
                        "valid": False
                    })
            
            profile_info[profile_name] = info
        
        return profile_info
    
    def get_profile_summary(self, profile_name: str) -> Dict[str, Any]:
        """
        Get a detailed summary of a specific profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Dictionary with profile summary information
        """
        try:
            profile = self.load_profile(profile_name)
            profile_file = self._get_profile_file_path(profile_name)
            
            summary = {
                "name": profile.name,
                "description": profile.description,
                "version": profile.version,
                "file_path": str(profile_file) if profile_file else None,
                "contexts": profile.contexts,
                "hooks": {
                    trigger.value: [hook.dict() for hook in hooks] 
                    for trigger, hooks in profile.hooks.items()
                },
                "mcp_servers": profile.mcp_servers,
                "settings": profile.settings.dict(),
                "metadata": profile.metadata,
                "validation": self.validate_profile(profile_name).dict()
            }
            
            # Add file statistics
            if profile_file and profile_file.exists():
                stat = profile_file.stat()
                summary["file_stats"] = {
                    "size_bytes": stat.st_size,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat()
                }
            
            return summary
            
        except Exception as e:
            return {
                "name": profile_name,
                "error": str(e),
                "valid": False,
                "file_path": str(self._get_profile_file_path(profile_name))
            }
    
    def create_profile_template(self, profile_name: str, description: str = None) -> Path:
        """
        Create a new profile template file.
        
        Args:
            profile_name: Name for the new profile
            description: Optional description for the profile
            
        Returns:
            Path to the created profile file
            
        Raises:
            FileExistsError: If profile already exists
        """
        profile_file = self.profiles_dir / f"{profile_name}.yaml"
        
        if profile_file.exists():
            raise FileExistsError(f"Profile already exists: {profile_name}")
        
        template_data = {
            "name": profile_name,
            "description": description or f"Profile configuration for {profile_name}",
            "version": "1.0",
            "contexts": [],
            "hooks": {},
            "mcp_servers": [],
            "settings": {
                "auto_backup": True,
                "validation_level": "normal",
                "hot_reload": True,
                "cache_enabled": True
            },
            "metadata": {
                "created": datetime.now().isoformat(),
                "created_by": "ProfileManager"
            }
        }
        
        # Save template
        import yaml
        with open(profile_file, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"Created profile template: {profile_file}")
        
        # Clear discovery cache to include new profile
        self._discovery_cache = None
        
        return profile_file
    
    def delete_profile(self, profile_name: str, create_backup: bool = True) -> bool:
        """
        Delete a profile configuration file.
        
        Args:
            profile_name: Name of the profile to delete
            create_backup: Whether to create a backup before deletion
            
        Returns:
            True if deletion was successful, False otherwise
        """
        profile_file = self._get_profile_file_path(profile_name)
        
        if not profile_file or not profile_file.exists():
            self.logger.warning(f"Profile file not found for deletion: {profile_name}")
            return False
        
        try:
            # Create backup if requested
            if create_backup:
                backup_dir = self.base_path / "backups" / "profiles"
                backup_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = backup_dir / f"{profile_name}_{timestamp}.yaml"
                
                import shutil
                shutil.copy2(profile_file, backup_file)
                self.logger.info(f"Created backup: {backup_file}")
            
            # Delete the profile file
            profile_file.unlink()
            
            # Clear caches
            self._profile_cache.pop(profile_name, None)
            self._discovery_cache = None
            
            self.logger.info(f"Deleted profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete profile '{profile_name}': {str(e)}")
            return False
    
    def clear_cache(self, profile_name: Optional[str] = None) -> None:
        """
        Clear profile cache.
        
        Args:
            profile_name: Specific profile to clear from cache. If None, clears all.
        """
        if profile_name:
            self._profile_cache.pop(profile_name, None)
            self.yaml_loader.clear_cache(self._get_profile_file_path(profile_name))
        else:
            self._profile_cache.clear()
            self._discovery_cache = None
            self.yaml_loader.clear_cache()
        
        self.logger.debug(f"Cleared profile cache: {profile_name or 'all'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "profile_cache_size": len(self._profile_cache),
            "cached_profiles": list(self._profile_cache.keys()),
            "discovery_cache_valid": self._discovery_cache is not None,
            "yaml_loader_stats": self.yaml_loader.get_cache_stats()
        }
    
    def _get_profile_file_path(self, profile_name: str) -> Optional[Path]:
        """
        Get the file path for a profile configuration.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Path to the profile file, or None if not found
        """
        # Try different possible extensions
        for ext in ['.yaml', '.yml']:
            profile_file = self.profiles_dir / f"{profile_name}{ext}"
            if profile_file.exists():
                return profile_file
        
        # Return the preferred path even if it doesn't exist
        return self.profiles_dir / f"{profile_name}.yaml"
    
    def _validate_profile_references(self, profile: EnhancedProfileConfig) -> tuple[List[ConfigurationError], List[ConfigurationError]]:
        """
        Validate references in a profile configuration.
        
        Args:
            profile: Profile configuration to validate
            
        Returns:
            Tuple of (errors, warnings) lists
        """
        errors = []
        warnings = []
        
        # Validate context file references
        for context_path in profile.contexts:
            if not context_path.startswith('*') and not context_path.endswith('*'):
                # Skip glob patterns
                full_path = self.base_path / context_path
                if not full_path.exists():
                    warnings.append(ConfigurationError(
                        file_path=f"profiles/{profile.name}.yaml",
                        error_type="MissingContextReference",
                        message=f"Referenced context file not found: {context_path}",
                        severity="warning"
                    ))
        
        # Validate hook references
        for trigger, hook_refs in profile.hooks.items():
            for hook_ref in hook_refs:
                hook_file = self.base_path / 'hooks' / f"{hook_ref.name}.yaml"
                if not hook_file.exists():
                    # Try .yml extension
                    hook_file = self.base_path / 'hooks' / f"{hook_ref.name}.yml"
                    if not hook_file.exists():
                        warnings.append(ConfigurationError(
                            file_path=f"profiles/{profile.name}.yaml",
                            error_type="MissingHookReference",
                            message=f"Referenced hook file not found: {hook_ref.name}",
                            severity="warning"
                        ))
        
        # Validate MCP server references (basic check)
        mcp_config_dir = self.base_path / 'configs' / 'mcp-servers'
        if mcp_config_dir.exists():
            available_servers = set()
            for mcp_file in mcp_config_dir.glob('*.json'):
                try:
                    import json
                    with open(mcp_file, 'r') as f:
                        data = json.load(f)
                        if 'mcpServers' in data:
                            available_servers.update(data['mcpServers'].keys())
                except Exception:
                    pass  # Skip invalid MCP config files
            
            for server_name in profile.mcp_servers:
                if server_name not in available_servers:
                    warnings.append(ConfigurationError(
                        file_path=f"profiles/{profile.name}.yaml",
                        error_type="UnknownMCPServer",
                        message=f"MCP server '{server_name}' not found in available configurations",
                        severity="warning"
                    ))
        
        return errors, warnings