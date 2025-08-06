"""
Simplified AI Configurator core module.
"""

from .library_manager import LibraryManager
from .profile_installer import ProfileInstaller
from .catalog_schema import LibraryCatalog, ConfigItem
from . import file_utils

__all__ = [
    'LibraryManager',
    'ProfileInstaller', 
    'LibraryCatalog',
    'ConfigItem',
    'file_utils'
]
