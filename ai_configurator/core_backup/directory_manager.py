"""
Directory structure management for AI Configurator.

This module handles the creation and organization of the new YAML/Markdown
configuration directory structure, including automatic directory creation
and naming convention validation.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from ..utils.logging import LoggerMixin


class ConfigurationType(Enum):
    """Types of configuration files."""
    PROFILE = "profile"
    HOOK = "hook"
    CONTEXT = "context"


@dataclass
class DirectoryStructure:
    """Represents the expected directory structure."""
    profiles_dir: Path
    hooks_dir: Path
    contexts_dir: Path
    contexts_shared_dir: Path


@dataclass
class NamingConvention:
    """Naming convention rules for configuration files."""
    pattern: str
    description: str
    examples: List[str]


class DirectoryManager(LoggerMixin):
    """
    Manages the directory structure for YAML/Markdown configurations.
    
    Handles:
    - Creating the new directory layout
    - Automatic directory creation and organization
    - Naming convention validation
    """
    
    # Naming convention patterns
    NAMING_CONVENTIONS = {
        ConfigurationType.PROFILE: NamingConvention(
            pattern=r'^[a-z][a-z0-9-]*[a-z0-9]$',
            description="Profile names must start with lowercase letter, contain only lowercase letters, numbers, and hyphens, and end with alphanumeric character",
            examples=["developer", "solutions-architect", "team-lead"]
        ),
        ConfigurationType.HOOK: NamingConvention(
            pattern=r'^[a-z][a-z0-9-]*[a-z0-9]$',
            description="Hook names must start with lowercase letter, contain only lowercase letters, numbers, and hyphens, and end with alphanumeric character",
            examples=["setup-dev-env", "context-enhancer", "auto-backup"]
        ),
        ConfigurationType.CONTEXT: NamingConvention(
            pattern=r'^[a-z][a-z0-9-]*[a-z0-9]$',
            description="Context names must start with lowercase letter, contain only lowercase letters, numbers, and hyphens, and end with alphanumeric character",
            examples=["aws-best-practices", "development-guidelines", "project-delivery"]
        )
    }
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize directory manager.
        
        Args:
            base_path: Base path for configuration directories. Defaults to current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
        # Define directory structure
        self.structure = DirectoryStructure(
            profiles_dir=self.base_path / 'profiles',
            hooks_dir=self.base_path / 'hooks',
            contexts_dir=self.base_path / 'contexts',
            contexts_shared_dir=self.base_path / 'contexts' / 'shared'
        )
    
    def create_directory_structure(self) -> bool:
        """
        Create the new directory layout for profiles, hooks, and contexts.
        
        Returns:
            True if all directories were created successfully, False otherwise.
        """
        try:
            directories_to_create = [
                self.structure.profiles_dir,
                self.structure.hooks_dir,
                self.structure.contexts_dir,
                self.structure.contexts_shared_dir
            ]
            
            created_dirs = []
            for directory in directories_to_create:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(directory)
                    self.logger.info(f"Created directory: {directory}")
                else:
                    self.logger.debug(f"Directory already exists: {directory}")
            
            if created_dirs:
                self.logger.info(f"Successfully created {len(created_dirs)} directories")
            else:
                self.logger.info("All required directories already exist")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create directory structure: {e}")
            return False
    
    def validate_naming_convention(self, name: str, config_type: ConfigurationType) -> Tuple[bool, str]:
        """
        Validate that a configuration file name follows naming conventions.
        
        Args:
            name: The name to validate (without extension)
            config_type: The type of configuration
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Name cannot be empty"
        
        convention = self.NAMING_CONVENTIONS[config_type]
        
        if not re.match(convention.pattern, name):
            return False, f"Invalid {config_type.value} name '{name}'. {convention.description}. Examples: {', '.join(convention.examples)}"
        
        # Additional length check
        if len(name) > 50:
            return False, f"Name '{name}' is too long (maximum 50 characters)"
        
        if len(name) < 2:
            return False, f"Name '{name}' is too short (minimum 2 characters)"
        
        return True, ""
    
    def organize_configuration_files(self) -> Dict[str, List[Path]]:
        """
        Organize existing configuration files according to the new structure.
        
        Returns:
            Dictionary mapping configuration types to lists of organized files.
        """
        organized = {
            "profiles": [],
            "hooks": [],
            "contexts": [],
            "errors": []
        }
        
        try:
            # Organize profiles
            if self.structure.profiles_dir.exists():
                for file_path in self.structure.profiles_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.yaml', '.yml', '.md']:
                        name = file_path.stem
                        is_valid, error = self.validate_naming_convention(name, ConfigurationType.PROFILE)
                        if is_valid:
                            organized["profiles"].append(file_path)
                        else:
                            organized["errors"].append(f"Profile file {file_path.name}: {error}")
            
            # Organize hooks
            if self.structure.hooks_dir.exists():
                for file_path in self.structure.hooks_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.yaml', '.yml', '.md']:
                        name = file_path.stem
                        is_valid, error = self.validate_naming_convention(name, ConfigurationType.HOOK)
                        if is_valid:
                            organized["hooks"].append(file_path)
                        else:
                            organized["errors"].append(f"Hook file {file_path.name}: {error}")
            
            # Organize contexts
            if self.structure.contexts_dir.exists():
                for file_path in self.structure.contexts_dir.rglob("*.md"):
                    if file_path.is_file():
                        name = file_path.stem
                        is_valid, error = self.validate_naming_convention(name, ConfigurationType.CONTEXT)
                        if is_valid:
                            organized["contexts"].append(file_path)
                        else:
                            organized["errors"].append(f"Context file {file_path.name}: {error}")
            
            self.logger.info(f"Organized {len(organized['profiles'])} profiles, {len(organized['hooks'])} hooks, {len(organized['contexts'])} contexts")
            
            if organized["errors"]:
                self.logger.warning(f"Found {len(organized['errors'])} naming convention violations")
                for error in organized["errors"]:
                    self.logger.warning(error)
            
        except Exception as e:
            self.logger.error(f"Failed to organize configuration files: {e}")
            organized["errors"].append(f"Organization failed: {e}")
        
        return organized
    
    def get_directory_structure(self) -> DirectoryStructure:
        """
        Get the current directory structure configuration.
        
        Returns:
            DirectoryStructure object with all directory paths.
        """
        return self.structure
    
    def validate_directory_structure(self) -> Dict[str, bool]:
        """
        Validate that all required directories exist and are accessible.
        
        Returns:
            Dictionary mapping directory names to their existence status.
        """
        validation_results = {}
        
        directories = {
            "profiles": self.structure.profiles_dir,
            "hooks": self.structure.hooks_dir,
            "contexts": self.structure.contexts_dir,
            "contexts_shared": self.structure.contexts_shared_dir
        }
        
        for name, directory in directories.items():
            try:
                exists = directory.exists()
                is_dir = directory.is_dir() if exists else False
                is_writable = directory.is_dir() and directory.stat().st_mode & 0o200 if exists else False
                
                validation_results[name] = exists and is_dir and is_writable
                
                if not exists:
                    self.logger.warning(f"Directory does not exist: {directory}")
                elif not is_dir:
                    self.logger.error(f"Path exists but is not a directory: {directory}")
                elif not is_writable:
                    self.logger.error(f"Directory is not writable: {directory}")
                    
            except Exception as e:
                self.logger.error(f"Failed to validate directory {directory}: {e}")
                validation_results[name] = False
        
        return validation_results
    
    def get_configuration_files(self, config_type: ConfigurationType) -> List[Path]:
        """
        Get all configuration files of a specific type.
        
        Args:
            config_type: Type of configuration files to retrieve
            
        Returns:
            List of Path objects for configuration files of the specified type.
        """
        files = []
        
        try:
            if config_type == ConfigurationType.PROFILE:
                directory = self.structure.profiles_dir
                extensions = ['.yaml', '.yml']
            elif config_type == ConfigurationType.HOOK:
                directory = self.structure.hooks_dir
                extensions = ['.yaml', '.yml']
            elif config_type == ConfigurationType.CONTEXT:
                directory = self.structure.contexts_dir
                extensions = ['.md']
            else:
                return files
            
            if directory.exists():
                for file_path in directory.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in extensions:
                        files.append(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to get {config_type.value} files: {e}")
        
        return files
    
    def suggest_valid_name(self, invalid_name: str, config_type: ConfigurationType) -> str:
        """
        Suggest a valid name based on an invalid one.
        
        Args:
            invalid_name: The invalid name to fix
            config_type: Type of configuration
            
        Returns:
            A suggested valid name.
        """
        # Convert to lowercase
        suggested = invalid_name.lower()
        
        # Replace invalid characters with hyphens
        suggested = re.sub(r'[^a-z0-9-]', '-', suggested)
        
        # Remove multiple consecutive hyphens
        suggested = re.sub(r'-+', '-', suggested)
        
        # Remove leading/trailing hyphens
        suggested = suggested.strip('-')
        
        # Ensure it starts with a letter
        if suggested and not suggested[0].isalpha():
            suggested = 'config-' + suggested
        
        # Ensure it's not empty
        if not suggested:
            suggested = f"default-{config_type.value}"
        
        # Ensure it ends with alphanumeric
        if suggested and not suggested[-1].isalnum():
            suggested = suggested.rstrip('-') + '-config'
        
        # Validate the suggestion
        is_valid, _ = self.validate_naming_convention(suggested, config_type)
        if not is_valid:
            # Fallback to a simple valid name
            suggested = f"default-{config_type.value}"
        
        return suggested