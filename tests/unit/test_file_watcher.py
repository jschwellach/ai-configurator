"""
Tests for the FileWatcher class.

Tests cover file watching functionality, debouncing mechanism,
callback system, and platform compatibility.
"""

import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.ai_configurator.core.file_watcher import FileWatcher, DebounceHandler


class TestDebounceHandler(unittest.TestCase):
    """Test the DebounceHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.callback = Mock()
        self.handler = DebounceHandler(self.callback, debounce_delay=0.1)
    
    def test_is_config_file(self):
        """Test configuration file detection."""
        # Test YAML files
        self.assertTrue(self.handler._is_config_file(Path("test.yaml")))
        self.assertTrue(self.handler._is_config_file(Path("test.yml")))
        
        # Test Markdown files
        self.assertTrue(self.handler._is_config_file(Path("test.md")))
        
        # Test JSON files
        self.assertTrue(self.handler._is_config_file(Path("test.json")))
        
        # Test non-config files
        self.assertFalse(self.handler._is_config_file(Path("test.txt")))
        self.assertFalse(self.handler._is_config_file(Path("test.py")))
        self.assertFalse(self.handler._is_config_file(Path("test")))
    
    def test_debouncing_mechanism(self):
        """Test that rapid changes are debounced."""
        test_file = Path("test.yaml")
        
        # Create mock event
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = str(test_file)
        
        # Trigger multiple rapid changes
        self.handler.on_modified(mock_event)
        self.handler.on_modified(mock_event)
        self.handler.on_modified(mock_event)
        
        # Callback should not be called immediately
        self.callback.assert_not_called()
        
        # Wait for debounce delay
        time.sleep(0.15)
        
        # Callback should be called only once with resolved path
        self.callback.assert_called_once_with(test_file.resolve())
    
    def test_different_event_types(self):
        """Test handling of different file system events."""
        test_file = Path("test.yaml")
        
        # Test modification event
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = str(test_file)
        
        self.handler.on_modified(mock_event)
        time.sleep(0.15)
        self.callback.assert_called_with(test_file.resolve())
        
        self.callback.reset_mock()
        
        # Test creation event
        self.handler.on_created(mock_event)
        time.sleep(0.15)
        self.callback.assert_called_with(test_file.resolve())
        
        self.callback.reset_mock()
        
        # Test deletion event
        self.handler.on_deleted(mock_event)
        time.sleep(0.15)
        self.callback.assert_called_with(test_file.resolve())
    
    def test_directory_events_ignored(self):
        """Test that directory events are ignored."""
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = "/some/directory"
        
        self.handler.on_modified(mock_event)
        time.sleep(0.15)
        
        self.callback.assert_not_called()


class TestFileWatcher(unittest.TestCase):
    """Test the FileWatcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.watcher = FileWatcher(debounce_delay=0.1)
        self.callback = Mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.watcher.stop_watching()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_remove_callback(self):
        """Test adding and removing callbacks."""
        # Add callback
        self.watcher.add_callback(self.callback)
        self.assertIn(self.callback, self.watcher.callbacks)
        
        # Remove callback
        self.watcher.remove_callback(self.callback)
        self.assertNotIn(self.callback, self.watcher.callbacks)
    
    def test_watch_directory_validation(self):
        """Test directory watching validation."""
        # Test non-existent directory
        non_existent = Path("/non/existent/path")
        self.watcher.watch_directory(non_existent)
        self.assertNotIn(non_existent, self.watcher.watched_paths)
        
        # Test file instead of directory
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test")
        self.watcher.watch_directory(test_file)
        self.assertNotIn(test_file, self.watcher.watched_paths)
        
        # Test valid directory
        self.watcher.watch_directory(self.temp_path)
        self.assertIn(self.temp_path, self.watcher.watched_paths)
    
    def test_unwatch_directory(self):
        """Test removing directories from watch list."""
        self.watcher.watch_directory(self.temp_path)
        self.assertIn(self.temp_path, self.watcher.watched_paths)
        
        self.watcher.unwatch_directory(self.temp_path)
        self.assertNotIn(self.temp_path, self.watcher.watched_paths)
    
    def test_start_stop_watching(self):
        """Test starting and stopping the file watcher."""
        self.watcher.watch_directory(self.temp_path)
        
        # Test starting
        self.watcher.start_watching()
        self.assertTrue(self.watcher.is_watching)
        self.assertIsNotNone(self.watcher.observer)
        
        # Test stopping
        self.watcher.stop_watching()
        self.assertFalse(self.watcher.is_watching)
    
    def test_start_without_directories(self):
        """Test starting watcher without any directories to watch."""
        # Should not start if no directories are being watched
        self.watcher.start_watching()
        self.assertFalse(self.watcher.is_watching)
    
    def test_context_manager(self):
        """Test using FileWatcher as a context manager."""
        self.watcher.watch_directory(self.temp_path)
        
        with self.watcher:
            self.assertTrue(self.watcher.is_watching)
        
        self.assertFalse(self.watcher.is_watching)
    
    def test_file_change_detection(self):
        """Test actual file change detection."""
        self.watcher.add_callback(self.callback)
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        # Give the watcher time to start
        time.sleep(0.1)
        
        # Create a YAML file
        test_file = self.temp_path / "test.yaml"
        test_file.write_text("test: value")
        
        # Wait for file system event and debounce
        time.sleep(0.3)
        
        # Callback should have been called
        self.callback.assert_called()
        
        # Check that the callback was called with the correct file path
        call_args = self.callback.call_args[0]
        # Resolve both paths to handle symlinks consistently
        self.assertEqual(call_args[0].resolve(), test_file.resolve())
    
    def test_multiple_callbacks(self):
        """Test that multiple callbacks are triggered."""
        callback1 = Mock()
        callback2 = Mock()
        
        self.watcher.add_callback(callback1)
        self.watcher.add_callback(callback2)
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create a file
        test_file = self.temp_path / "test.yaml"
        test_file.write_text("test: value")
        
        time.sleep(0.3)
        
        # Both callbacks should be called
        callback1.assert_called()
        callback2.assert_called()
    
    def test_callback_error_handling(self):
        """Test that callback errors don't crash the watcher."""
        def failing_callback(path):
            raise Exception("Test error")
        
        working_callback = Mock()
        
        self.watcher.add_callback(failing_callback)
        self.watcher.add_callback(working_callback)
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create a file
        test_file = self.temp_path / "test.yaml"
        test_file.write_text("test: value")
        
        time.sleep(0.3)
        
        # Working callback should still be called despite the failing one
        working_callback.assert_called()
    
    def test_rapid_file_changes_debounced(self):
        """Test that rapid file changes are properly debounced."""
        self.watcher.add_callback(self.callback)
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create and modify file rapidly
        test_file = self.temp_path / "test.yaml"
        test_file.write_text("test: value1")
        time.sleep(0.05)  # Less than debounce delay
        test_file.write_text("test: value2")
        time.sleep(0.05)  # Less than debounce delay
        test_file.write_text("test: value3")
        
        # Wait for debounce
        time.sleep(0.3)
        
        # Should be called only once due to debouncing
        # Note: The exact number might vary due to file system behavior,
        # but it should be significantly less than 3
        self.assertTrue(self.callback.call_count <= 2)
    
    def test_non_config_files_ignored(self):
        """Test that non-configuration files are ignored."""
        self.watcher.add_callback(self.callback)
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create a non-config file
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test content")
        
        time.sleep(0.3)
        
        # Callback should not be called for non-config files
        self.callback.assert_not_called()


class TestFileWatcherIntegration(unittest.TestCase):
    """Integration tests for FileWatcher with real file operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.watcher = FileWatcher(debounce_delay=0.1)
        self.changes_detected = []
        
        def change_callback(path):
            self.changes_detected.append(path.resolve())
        
        self.watcher.add_callback(change_callback)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.watcher.stop_watching()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_yaml_file_changes(self):
        """Test detection of YAML file changes."""
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create YAML file
        yaml_file = self.temp_path / "config.yaml"
        yaml_file.write_text("key: value")
        
        time.sleep(0.3)
        
        self.assertIn(yaml_file.resolve(), self.changes_detected)
    
    def test_markdown_file_changes(self):
        """Test detection of Markdown file changes."""
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create Markdown file
        md_file = self.temp_path / "context.md"
        md_file.write_text("# Context\nSome content")
        
        time.sleep(0.3)
        
        self.assertIn(md_file.resolve(), self.changes_detected)
    
    def test_subdirectory_changes(self):
        """Test detection of changes in subdirectories."""
        # Create subdirectory
        sub_dir = self.temp_path / "profiles"
        sub_dir.mkdir()
        
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        
        # Create file in subdirectory
        sub_file = sub_dir / "profile.yaml"
        sub_file.write_text("name: test")
        
        time.sleep(0.3)
        
        self.assertIn(sub_file.resolve(), self.changes_detected)
    
    def test_file_deletion(self):
        """Test detection of file deletion."""
        # Create file first
        test_file = self.temp_path / "temp.yaml"
        test_file.write_text("temp: content")
        
        self.watcher.watch_directory(self.temp_path)
        self.watcher.start_watching()
        
        time.sleep(0.1)
        self.changes_detected.clear()  # Clear any creation events
        
        # Delete file
        test_file.unlink()
        
        time.sleep(0.3)
        
        self.assertIn(test_file.resolve(), self.changes_detected)


if __name__ == '__main__':
    unittest.main()