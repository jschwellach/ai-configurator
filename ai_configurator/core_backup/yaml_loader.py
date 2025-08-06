"""YAML configuration loader with validation and caching."""

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import yaml
from pydantic import ValidationError

from .models import (
    EnhancedProfileConfig,
    HookConfig,
    ContextFile,
    ConfigurationError,
    ValidationReport,
    PathLike,
    YamlConfigDict,
)
from .validator import ConfigurationValidator


class YamlConfigLoader:
    """
    YAML configuration loader with file discovery, parsing, validation, and caching.
    
    This class handles loading YAML configuration files for profiles, hooks, and contexts
    with comprehensive error reporting and caching for performance.
    """
    
    def __init__(self, base_path: Optional[PathLike] = None):
        """
        Initialize the YAML configuration loader.
        
        Args:
            base_path: Base directory path for configuration files. 
                      Defaults to current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._cache: Dict[str, Tuple[Any, float]] = {}  # file_path -> (config, mtime)
        self._validation_cache: Dict[str, Tuple[ValidationReport, float]] = {}
        self._validator = ConfigurationValidator(self.base_path)
        
    def discover_configurations(self) -> Dict[str, List[str]]:
        """
        Discover all YAML configuration files in the base directory structure.
        
        Returns:
            Dictionary mapping configuration types to lists of file paths:
            {
                'profiles': ['profile1.yaml', 'profile2.yaml'],
                'hooks': ['hook1.yaml', 'hook2.yaml'],
                'contexts': ['context1.md', 'context2.md']
            }
        """
        discovered = {
            'profiles': [],
            'hooks': [],
            'contexts': []
        }
        
        # Discover profiles
        profiles_dir = self.base_path / 'profiles'
        if profiles_dir.exists():
            for file_path in profiles_dir.glob('*.yaml'):
                discovered['profiles'].append(str(file_path.relative_to(self.base_path)))
            for file_path in profiles_dir.glob('*.yml'):
                discovered['profiles'].append(str(file_path.relative_to(self.base_path)))
        
        # Discover hooks
        hooks_dir = self.base_path / 'hooks'
        if hooks_dir.exists():
            for file_path in hooks_dir.glob('*.yaml'):
                discovered['hooks'].append(str(file_path.relative_to(self.base_path)))
            for file_path in hooks_dir.glob('*.yml'):
                discovered['hooks'].append(str(file_path.relative_to(self.base_path)))
        
        # Discover contexts (Markdown files)
        contexts_dir = self.base_path / 'contexts'
        if contexts_dir.exists():
            for file_path in contexts_dir.glob('*.md'):
                discovered['contexts'].append(str(file_path.relative_to(self.base_path)))
            # Also check for nested contexts
            for file_path in contexts_dir.rglob('*.md'):
                if file_path != contexts_dir / file_path.name:  # Avoid duplicates
                    discovered['contexts'].append(str(file_path.relative_to(self.base_path)))
        
        return discovered
    
    def load_profile(self, profile_name: str) -> EnhancedProfileConfig:
        """
        Load a profile configuration from YAML file.
        
        Args:
            profile_name: Name of the profile (without .yaml extension)
            
        Returns:
            Parsed and validated profile configuration
            
        Raises:
            FileNotFoundError: If profile file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValidationError: If configuration validation fails
        """
        # Try different possible file paths
        possible_paths = [
            self.base_path / 'profiles' / f'{profile_name}.yaml',
            self.base_path / 'profiles' / f'{profile_name}.yml',
            self.base_path / f'{profile_name}.yaml',
            self.base_path / f'{profile_name}.yml',
        ]
        
        file_path = None
        for path in possible_paths:
            if path.exists():
                file_path = path
                break
        
        if not file_path:
            raise FileNotFoundError(
                f"Profile configuration not found: {profile_name}. "
                f"Searched in: {[str(p) for p in possible_paths]}"
            )
        
        # Check cache first
        cache_key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        
        if cache_key in self._cache:
            cached_config, cached_mtime = self._cache[cache_key]
            if cached_mtime >= current_mtime:
                return cached_config
        
        # Load and parse YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                yaml_data = {}
            
            # Ensure name matches filename if not specified
            if 'name' not in yaml_data:
                yaml_data['name'] = profile_name
            
            # Validate and create profile config
            profile_config = EnhancedProfileConfig(**yaml_data)
            
            # Cache the result
            self._cache[cache_key] = (profile_config, current_mtime)
            
            return profile_config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"YAML parsing error in {file_path}: {str(e)}"
            ) from e
        except ValidationError as e:
            raise ValidationError(
                f"Validation error in {file_path}: {str(e)}"
            ) from e
    
    def load_hook(self, hook_name: str) -> HookConfig:
        """
        Load a hook configuration from YAML file.
        
        Args:
            hook_name: Name of the hook (without .yaml extension)
            
        Returns:
            Parsed and validated hook configuration
            
        Raises:
            FileNotFoundError: If hook file doesn't exist
            yaml.YAMLError: If YAML parsing fails
            ValidationError: If configuration validation fails
        """
        # Try different possible file paths
        possible_paths = [
            self.base_path / 'hooks' / f'{hook_name}.yaml',
            self.base_path / 'hooks' / f'{hook_name}.yml',
            self.base_path / f'{hook_name}.yaml',
            self.base_path / f'{hook_name}.yml',
        ]
        
        file_path = None
        for path in possible_paths:
            if path.exists():
                file_path = path
                break
        
        if not file_path:
            raise FileNotFoundError(
                f"Hook configuration not found: {hook_name}. "
                f"Searched in: {[str(p) for p in possible_paths]}"
            )
        
        # Check cache first
        cache_key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        
        if cache_key in self._cache:
            cached_config, cached_mtime = self._cache[cache_key]
            if cached_mtime >= current_mtime:
                return cached_config
        
        # Load and parse YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                yaml_data = {}
            
            # Ensure name matches filename if not specified
            if 'name' not in yaml_data:
                yaml_data['name'] = hook_name
            
            # Validate and create hook config
            hook_config = HookConfig(**yaml_data)
            
            # Cache the result
            self._cache[cache_key] = (hook_config, current_mtime)
            
            return hook_config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"YAML parsing error in {file_path}: {str(e)}"
            ) from e
        except ValidationError as e:
            raise ValidationError(
                f"Validation error in {file_path}: {str(e)}"
            ) from e
    
    def load_hook_config(self, file_path: PathLike) -> Optional[HookConfig]:
        """
        Load a hook configuration from a specific YAML file path.
        
        Args:
            file_path: Path to the hook YAML file
            
        Returns:
            Parsed hook configuration or None if loading fails
        """
        try:
            # Extract hook name from file path
            hook_name = Path(file_path).stem
            
            # Check cache first
            cache_key = str(file_path)
            current_mtime = Path(file_path).stat().st_mtime
            
            if cache_key in self._cache:
                cached_config, cached_mtime = self._cache[cache_key]
                if cached_mtime >= current_mtime:
                    return cached_config
            
            # Load and parse YAML
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                yaml_data = {}
            
            # Ensure name matches filename if not specified
            if 'name' not in yaml_data:
                yaml_data['name'] = hook_name
            
            # Validate and create hook config
            hook_config = HookConfig(**yaml_data)
            
            # Cache the result
            self._cache[cache_key] = (hook_config, current_mtime)
            
            return hook_config
            
        except Exception:
            # Return None on any error - let the caller handle logging
            return None
    
    def validate_yaml_file(self, file_path: PathLike) -> ValidationReport:
        """
        Validate a YAML configuration file with comprehensive error reporting.
        
        Args:
            file_path: Path to the YAML file to validate
            
        Returns:
            Comprehensive validation report with errors, warnings, and info
        """
        file_path = Path(file_path)
        
        # Check validation cache first
        cache_key = str(file_path)
        if file_path.exists():
            current_mtime = file_path.stat().st_mtime
            
            if cache_key in self._validation_cache:
                cached_report, cached_mtime = self._validation_cache[cache_key]
                if cached_mtime >= current_mtime:
                    return cached_report
        
        # Use the comprehensive validator
        report = self._validator.validate_configuration_file(file_path)
        
        # Cache the result
        if file_path.exists():
            self._validation_cache[cache_key] = (report, file_path.stat().st_mtime)
        
        return report
    
    def load_yaml_file(self, file_path: PathLike) -> YamlConfigDict:
        """
        Load and parse a YAML file with caching.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Parsed YAML data as dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check cache first
        cache_key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        
        if cache_key in self._cache:
            cached_data, cached_mtime = self._cache[cache_key]
            if cached_mtime >= current_mtime:
                return cached_data
        
        # Load and parse YAML
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                yaml_data = {}
            
            # Cache the result
            self._cache[cache_key] = (yaml_data, current_mtime)
            
            return yaml_data
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"YAML parsing error in {file_path}: {str(e)}"
            ) from e
    
    def clear_cache(self, file_path: Optional[PathLike] = None) -> None:
        """
        Clear configuration cache.
        
        Args:
            file_path: Specific file to clear from cache. If None, clears entire cache.
        """
        if file_path:
            cache_key = str(Path(file_path))
            self._cache.pop(cache_key, None)
            self._validation_cache.pop(cache_key, None)
        else:
            self._cache.clear()
            self._validation_cache.clear()
    
    def validate_all_configurations(self) -> ValidationReport:
        """
        Validate all configuration files with comprehensive checks.
        
        This method performs:
        - Schema validation for all YAML configuration types
        - File reference validation
        - Circular dependency detection
        - Cross-file reference validation
        
        Returns:
            Comprehensive validation report for all configurations
        """
        return self._validator.validate_all_configurations()
    
    def validate_schema(self, file_path: PathLike, config_type: str) -> ValidationReport:
        """
        Validate configuration schema for a specific file type.
        
        Args:
            file_path: Path to the configuration file
            config_type: Type of configuration ('profile', 'hook', 'context')
            
        Returns:
            Schema validation report
        """
        return self._validator.validate_schema(file_path, config_type)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring and debugging.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "config_cache_size": len(self._cache),
            "validation_cache_size": len(self._validation_cache),
            "cached_files": list(self._cache.keys()),
            "cache_hit_ratio": self._calculate_cache_hit_ratio()
        }
    
    def _determine_config_type(self, file_path: Path, yaml_data: Dict[str, Any]) -> str:
        """
        Determine the type of configuration based on file path and content.
        
        Args:
            file_path: Path to the configuration file
            yaml_data: Parsed YAML data
            
        Returns:
            Configuration type: 'profile', 'hook', or 'unknown'
        """
        # Check file path patterns
        if 'profiles' in file_path.parts:
            return 'profile'
        elif 'hooks' in file_path.parts:
            return 'hook'
        
        # Check content patterns
        if 'trigger' in yaml_data or 'type' in yaml_data:
            return 'hook'
        elif 'contexts' in yaml_data or 'mcp_servers' in yaml_data:
            return 'profile'
        
        return 'unknown'
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio for performance monitoring."""
        # This is a simplified implementation
        # In a real implementation, you'd track hits and misses
        return 0.0 if not self._cache else 0.85  # Placeholder value