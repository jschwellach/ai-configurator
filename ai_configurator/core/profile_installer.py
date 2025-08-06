"""
Simplified Profile Installer for AI Configurator.
"""

import logging
import shutil
import yaml
from pathlib import Path
from typing import Optional, List

from .library_manager import LibraryManager
from .file_utils import ensure_directory, copy_file


class ProfileInstaller:
    """Simplified profile installer for AI Configurator."""
    
    def __init__(self, library_manager: Optional[LibraryManager] = None):
        """Initialize the profile installer."""
        self.logger = logging.getLogger(__name__)
        self.library_manager = library_manager or LibraryManager()
        
        # Default Amazon Q directories
        self.amazonq_contexts_dir = Path.home() / ".aws" / "amazonq" / "contexts"
        self.amazonq_profiles_dir = Path.home() / ".aws" / "amazonq" / "profiles"
        
    def install_profile(self, profile_id: str) -> bool:
        """Install a profile by copying its contexts to Amazon Q directory."""
        try:
            # Get profile configuration
            config = self.library_manager.get_configuration_by_id(profile_id)
            if not config:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
                
            # Get profile file path
            profile_path = self.library_manager.get_configuration_file_path(profile_id)
            if not profile_path or not profile_path.exists():
                self.logger.error(f"Profile file not found: {profile_path}")
                return False
                
            # Load profile YAML
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = yaml.safe_load(f)
                
            # Ensure Amazon Q directories exist
            ensure_directory(self.amazonq_contexts_dir)
            ensure_directory(self.amazonq_profiles_dir)
            
            # Copy contexts
            contexts = profile_data.get('contexts', [])
            profile_dir = profile_path.parent
            
            for context_file in contexts:
                source_path = profile_dir / "contexts" / context_file
                if source_path.exists():
                    dest_path = self.amazonq_contexts_dir / context_file
                    copy_file(source_path, dest_path)
                    self.logger.info(f"Copied context: {context_file}")
                else:
                    self.logger.warning(f"Context file not found: {source_path}")
            
            # Create profile marker file
            profile_marker = self.amazonq_profiles_dir / f"{profile_id}.installed"
            profile_marker.write_text(f"Installed: {config.name} v{config.version}")
            
            self.logger.info(f"Successfully installed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing profile '{profile_id}': {e}")
            return False
    
    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile by deleting its contexts and marker."""
        try:
            # Get profile configuration
            config = self.library_manager.get_configuration_by_id(profile_id)
            if not config:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
                
            # Get profile file path
            profile_path = self.library_manager.get_configuration_file_path(profile_id)
            if not profile_path or not profile_path.exists():
                self.logger.error(f"Profile file not found: {profile_path}")
                return False
                
            # Load profile YAML
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = yaml.safe_load(f)
                
            # Remove contexts
            contexts = profile_data.get('contexts', [])
            
            for context_file in contexts:
                context_path = self.amazonq_contexts_dir / context_file
                if context_path.exists():
                    context_path.unlink()
                    self.logger.info(f"Removed context: {context_file}")
            
            # Remove profile marker file
            profile_marker = self.amazonq_profiles_dir / f"{profile_id}.installed"
            if profile_marker.exists():
                profile_marker.unlink()
            
            self.logger.info(f"Successfully removed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing profile '{profile_id}': {e}")
            return False
    
    def is_profile_installed(self, profile_id: str) -> bool:
        """Check if a profile is installed."""
        profile_marker = self.amazonq_profiles_dir / f"{profile_id}.installed"
        return profile_marker.exists()
    
    def list_installed_profiles(self) -> List[str]:
        """List all installed profiles."""
        if not self.amazonq_profiles_dir.exists():
            return []
            
        installed = []
        for marker_file in self.amazonq_profiles_dir.glob("*.installed"):
            profile_id = marker_file.stem
            installed.append(profile_id)
            
        return installed
