"""
Config-based Library Manager for AI Configurator.
Manages library installation in ~/.config/ai-configurator/library
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional, List

from .catalog_schema import LibraryCatalog, ConfigItem, GlobalContext
from .file_utils import ensure_directory, copy_file


class ConfigLibraryManager:
    """Manages library installation in user config directory."""
    
    def __init__(self, source_library_path: Optional[Path] = None):
        """Initialize the config library manager."""
        self.logger = logging.getLogger(__name__)
        
        # Source library (where we read from)
        if source_library_path:
            self.source_library_path = Path(source_library_path)
        else:
            # Default to library directory relative to this file
            self.source_library_path = Path(__file__).parent.parent.parent / "library"
            
        # Config library (where we install to)
        self.config_dir = Path.home() / ".config" / "ai-configurator"
        self.config_library_path = self.config_dir / "library"
        
        self._catalog = None
        
    def ensure_config_library_installed(self) -> bool:
        """Ensure the library is installed in the config directory."""
        try:
            if not self.source_library_path.exists():
                self.logger.error(f"Source library not found: {self.source_library_path}")
                return False
                
            # Create config directory structure
            ensure_directory(self.config_dir)
            ensure_directory(self.config_library_path)
            
            # Copy entire library to config directory
            if self.config_library_path.exists():
                shutil.rmtree(self.config_library_path)
                
            shutil.copytree(self.source_library_path, self.config_library_path)
            self.logger.info(f"Library installed to: {self.config_library_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing library to config directory: {e}")
            return False
    
    def get_catalog(self) -> Optional[LibraryCatalog]:
        """Get the library catalog, ensuring library is installed first."""
        if self._catalog is None:
            if not self.ensure_config_library_installed():
                return None
                
            catalog_path = self.config_library_path / "catalog.json"
            if not catalog_path.exists():
                self.logger.error(f"Catalog not found: {catalog_path}")
                return None
                
            try:
                with open(catalog_path, 'r', encoding='utf-8') as f:
                    catalog_data = json.load(f)
                self._catalog = LibraryCatalog(**catalog_data)
            except Exception as e:
                self.logger.error(f"Error loading catalog: {e}")
                return None
                
        return self._catalog
    
    def get_profiles(self) -> List[ConfigItem]:
        """Get all available profiles."""
        catalog = self.get_catalog()
        return catalog.profiles if catalog else []
    
    def get_global_contexts(self) -> List[GlobalContext]:
        """Get all global contexts sorted by priority (highest first)."""
        catalog = self.get_catalog()
        if not catalog:
            return []
        return sorted(catalog.global_contexts, key=lambda x: x.priority, reverse=True)
    
    def get_profile_by_id(self, profile_id: str) -> Optional[ConfigItem]:
        """Get a specific profile by ID."""
        profiles = self.get_profiles()
        return next((p for p in profiles if p.id == profile_id), None)
    
    def get_profile_file_path(self, profile_id: str) -> Optional[Path]:
        """Get the file path for a profile configuration."""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None
        return self.config_library_path / profile.file_path
    
    def get_global_context_file_path(self, global_context: GlobalContext) -> Path:
        """Get the file path for a global context."""
        return self.config_library_path / global_context.file_path
    
    def refresh_library(self) -> bool:
        """Refresh the library from source (re-install)."""
        self._catalog = None  # Clear cached catalog
        return self.ensure_config_library_installed()
