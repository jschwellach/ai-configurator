"""
Simplified Library Manager for AI Configurator.
"""

import json
import logging
import time
from pathlib import Path
from typing import List, Optional

from .catalog_schema import LibraryCatalog, ConfigItem


class LibraryManager:
    """Simplified library manager for AI Configurator."""
    
    def __init__(self, library_path: Optional[Path] = None):
        """Initialize the library manager."""
        self.logger = logging.getLogger(__name__)
        self.library_path = library_path or self._get_default_library_path()
        self._catalog_cache = None
        
    def _get_default_library_path(self) -> Path:
        """Get the default library path - always use project root library."""
        # Always use project root library directory
        # This works for both development and installed packages
        package_root = Path(__file__).parent.parent.parent.parent
        library_path = package_root / "library"
        
        if library_path.exists():
            return library_path
            
        # Fallback: current directory
        return Path("library")
    
    def load_catalog(self, force_refresh: bool = False) -> Optional[LibraryCatalog]:
        """Load the library catalog."""
        if self._catalog_cache and not force_refresh:
            return self._catalog_cache
            
        catalog_path = self.library_path / "catalog.json"
        
        if not catalog_path.exists():
            self.logger.error(f"Catalog file not found: {catalog_path}")
            return None
            
        try:
            start_time = time.time()
            
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
                
            catalog = LibraryCatalog(**catalog_data)
            self._catalog_cache = catalog
            
            load_time = time.time() - start_time
            self.logger.info(f"Loaded catalog with {len(catalog.profiles)} configurations in {load_time:.2f}s")
            
            return catalog
            
        except Exception as e:
            self.logger.error(f"Error loading catalog: {e}")
            return None
    
    def search_configurations(self, query: Optional[str] = None) -> List[ConfigItem]:
        """Search configurations based on query."""
        start_time = time.time()
        
        catalog = self.load_catalog()
        if not catalog:
            return []
        
        results = []
        
        # Search through all profiles
        for profile in catalog.profiles:
            # If no query, return all profiles
            if not query:
                results.append(profile)
                continue
                
            # Search in name and description
            query_lower = query.lower()
            if (query_lower in profile.name.lower() or 
                query_lower in profile.description.lower()):
                results.append(profile)
        
        search_time = time.time() - start_time
        self.logger.info(f"Search returned {len(results)} configurations in {search_time:.2f}s")
        
        return results
    
    def get_configuration_by_id(self, config_id: str) -> Optional[ConfigItem]:
        """Get a configuration by its ID."""
        catalog = self.load_catalog()
        if not catalog:
            return None
            
        for profile in catalog.profiles:
            if profile.id == config_id:
                return profile
                
        return None
    
    def get_configuration_file_path(self, config_id: str) -> Optional[Path]:
        """Get the file path for a configuration."""
        config = self.get_configuration_by_id(config_id)
        if not config:
            return None
            
        return self.library_path / config.file_path
    
    def get_stats(self) -> dict:
        """Get library statistics."""
        catalog = self.load_catalog()
        if not catalog:
            return {"error": "Could not load catalog"}
            
        return {
            "total_configs": len(catalog.profiles),
            "version": catalog.version,
            "profiles": len(catalog.profiles)
        }
    
    def shutdown(self):
        """Shutdown the library manager."""
        self.logger.info("LibraryManager shutdown completed")
