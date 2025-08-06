"""
File watching system for hot-reload functionality.

This module provides a FileWatcher class that monitors configuration files
for changes and triggers reload callbacks with debouncing to prevent
excessive reloads during rapid changes.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class DebounceHandler(FileSystemEventHandler):
    """
    File system event handler with debouncing mechanism.
    
    Prevents excessive callback execution during rapid file changes
    by implementing a debounce delay.
    """
    
    def __init__(self, callback: Callable[[Path], None], debounce_delay: float = 1.0):
        """
        Initialize the debounce handler.
        
        Args:
            callback: Function to call when file changes are detected
            debounce_delay: Delay in seconds before triggering callback
        """
        super().__init__()
        self.callback = callback
        self.debounce_delay = debounce_delay
        self.pending_changes: Dict[str, float] = {}
        self.timer: Optional[threading.Timer] = None
        self.lock = threading.Lock()
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self._handle_change(Path(event.src_path))
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self._handle_change(Path(event.src_path))
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self._handle_change(Path(event.src_path))
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events."""
        if not event.is_directory:
            # Handle both source and destination paths
            if hasattr(event, 'src_path'):
                self._handle_change(Path(event.src_path))
            if hasattr(event, 'dest_path'):
                self._handle_change(Path(event.dest_path))
    
    def _handle_change(self, file_path: Path) -> None:
        """
        Handle a file change with debouncing.
        
        Args:
            file_path: Path to the changed file
        """
        # Only watch configuration files
        if not self._is_config_file(file_path):
            return
        
        # Resolve path to handle symlinks consistently
        resolved_path = file_path.resolve()
            
        with self.lock:
            current_time = time.time()
            self.pending_changes[str(resolved_path)] = current_time
            
            # Cancel existing timer if any
            if self.timer:
                self.timer.cancel()
            
            # Start new timer
            self.timer = threading.Timer(self.debounce_delay, self._process_changes)
            self.timer.start()
    
    def _is_config_file(self, file_path: Path) -> bool:
        """
        Check if the file is a configuration file we should watch.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the file should be watched
        """
        suffix = file_path.suffix.lower()
        return suffix in {'.yaml', '.yml', '.md', '.json'}
    
    def _process_changes(self) -> None:
        """Process all pending changes after debounce delay."""
        with self.lock:
            if not self.pending_changes:
                return
                
            # Get all changed files
            changed_files = list(self.pending_changes.keys())
            self.pending_changes.clear()
            
            # Process each changed file
            for file_path_str in changed_files:
                try:
                    file_path = Path(file_path_str)
                    logger.info(f"Processing configuration change: {file_path}")
                    self.callback(file_path)
                except Exception as e:
                    logger.error(f"Error processing file change {file_path_str}: {e}")


class FileWatcher:
    """
    File system watcher for configuration hot-reload.
    
    Monitors specified directories for configuration file changes and
    triggers callbacks with debouncing to prevent excessive reloads.
    """
    
    def __init__(self, debounce_delay: float = 1.0):
        """
        Initialize the file watcher.
        
        Args:
            debounce_delay: Delay in seconds before triggering callbacks
        """
        self.debounce_delay = debounce_delay
        self.observer: Optional[Observer] = None
        self.watched_paths: Set[Path] = set()
        self.callbacks: List[Callable[[Path], None]] = []
        self.is_watching = False
        self.lock = threading.Lock()
    
    def add_callback(self, callback: Callable[[Path], None]) -> None:
        """
        Add a callback to be triggered on file changes.
        
        Args:
            callback: Function that takes a Path argument
        """
        with self.lock:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Path], None]) -> None:
        """
        Remove a callback from the watch list.
        
        Args:
            callback: Function to remove
        """
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
    
    def watch_directory(self, path: Path, callback: Optional[Callable[[Path], None]] = None) -> None:
        """
        Add a directory to watch for changes.
        
        Args:
            path: Directory path to watch
            callback: Optional specific callback for this directory
        """
        if not path.exists():
            logger.warning(f"Cannot watch non-existent directory: {path}")
            return
            
        if not path.is_dir():
            logger.warning(f"Cannot watch non-directory path: {path}")
            return
        
        with self.lock:
            self.watched_paths.add(path)
            if callback:
                self.callbacks.append(callback)
        
        # If already watching, add the new path to the observer
        if self.is_watching and self.observer:
            self._add_watch_path(path)
        
        logger.info(f"Added directory to watch list: {path}")
    
    def unwatch_directory(self, path: Path) -> None:
        """
        Remove a directory from the watch list.
        
        Args:
            path: Directory path to stop watching
        """
        with self.lock:
            self.watched_paths.discard(path)
        
        logger.info(f"Removed directory from watch list: {path}")
    
    def start_watching(self) -> None:
        """Start the file watching system."""
        if self.is_watching:
            logger.warning("File watcher is already running")
            return
        
        if not self.watched_paths:
            logger.warning("No directories to watch")
            return
        
        try:
            self.observer = Observer()
            
            # Add all watched paths
            for path in self.watched_paths:
                self._add_watch_path(path)
            
            self.observer.start()
            self.is_watching = True
            logger.info(f"Started file watcher for {len(self.watched_paths)} directories")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.stop_watching()
            raise
    
    def stop_watching(self) -> None:
        """Stop the file watching system."""
        if not self.is_watching:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)  # Wait up to 5 seconds
                self.observer = None
            
            self.is_watching = False
            logger.info("Stopped file watcher")
            
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
    
    def _add_watch_path(self, path: Path) -> None:
        """
        Add a path to the observer.
        
        Args:
            path: Path to add to the observer
        """
        if not self.observer:
            return
            
        try:
            handler = DebounceHandler(
                callback=self._handle_file_change,
                debounce_delay=self.debounce_delay
            )
            
            self.observer.schedule(handler, str(path), recursive=True)
            logger.debug(f"Added watch for path: {path}")
            
        except Exception as e:
            logger.error(f"Failed to add watch for path {path}: {e}")
    
    def _handle_file_change(self, file_path: Path) -> None:
        """
        Handle a file change by calling all registered callbacks.
        
        Args:
            file_path: Path to the changed file
        """
        with self.lock:
            callbacks_to_call = self.callbacks.copy()
        
        for callback in callbacks_to_call:
            try:
                callback(file_path)
            except Exception as e:
                logger.error(f"Error in file change callback: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.start_watching()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_watching()