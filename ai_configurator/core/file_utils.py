"""
Simplified file utilities for AI Configurator.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


def ensure_directory(path: Path) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def copy_file(source: Path, destination: Path) -> bool:
    """Copy a file from source to destination."""
    try:
        # Ensure destination directory exists
        ensure_directory(destination.parent)
        
        # Copy the file
        shutil.copy2(source, destination)
        logger.debug(f"Copied {source} to {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying {source} to {destination}: {e}")
        return False


def delete_file(path: Path) -> bool:
    """Delete a file if it exists."""
    try:
        if path.exists():
            path.unlink()
            logger.debug(f"Deleted {path}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting {path}: {e}")
        return False


def read_text_file(path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Read a text file and return its contents."""
    try:
        return path.read_text(encoding=encoding)
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None


def write_text_file(path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """Write content to a text file."""
    try:
        # Ensure directory exists
        ensure_directory(path.parent)
        
        path.write_text(content, encoding=encoding)
        logger.debug(f"Wrote content to {path}")
        return True
        
    except Exception as e:
        logger.error(f"Error writing to {path}: {e}")
        return False
