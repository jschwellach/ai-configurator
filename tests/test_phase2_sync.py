"""
Tests for Phase 2 library synchronization features.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from ai_configurator.models.sync_models import (
    LibrarySync, ConflictReport, SyncHistory, FileDiff
)
from ai_configurator.models.value_objects import ConflictType, Resolution
from ai_configurator.services.sync_service import SyncService


class TestSyncService:
    """Test suite for SyncService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock()
        self.sync_service = SyncService(self.console)
        
        # Create temporary directories for testing
        self.base_path = Path("/tmp/test_base")
        self.personal_path = Path("/tmp/test_personal")
        self.backup_path = Path("/tmp/test_backup")
        
        # Clean up and create directories
        import shutil
        for path in [self.base_path, self.personal_path, self.backup_path]:
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        for path in [self.base_path, self.personal_path, self.backup_path]:
            if path.exists():
                shutil.rmtree(path)
    
    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        # Create test file
        test_file = self.base_path / "test.md"
        test_file.write_text("# Test Content")
        
        # Calculate hash
        hash1 = self.sync_service.calculate_file_hash(test_file)
        hash2 = self.sync_service.calculate_file_hash(test_file)
        
        # Hash should be consistent
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
        
        # Different content should produce different hash
        test_file.write_text("# Different Content")
        hash3 = self.sync_service.calculate_file_hash(test_file)
        assert hash1 != hash3
    
    def test_generate_diff(self):
        """Test diff generation."""
        base_content = "Line 1\nLine 2\nLine 3"
        personal_content = "Line 1\nModified Line 2\nLine 3\nNew Line 4"
        
        diff = self.sync_service.generate_diff(base_content, personal_content, "test.md")
        
        assert diff.file_path == "test.md"
        assert diff.base_content == base_content
        assert diff.personal_content == personal_content
        assert len(diff.diff_lines) > 0
    
    def test_detect_conflicts_no_conflicts(self):
        """Test conflict detection with no conflicts."""
        # Create identical files
        (self.base_path / "same.md").write_text("Same content")
        (self.personal_path / "same.md").write_text("Same content")
        
        library_sync = LibrarySync(
            base_path=self.base_path,
            personal_path=self.personal_path,
            backup_path=self.backup_path
        )
        
        conflicts = self.sync_service.detect_conflicts(library_sync)
        assert len(conflicts) == 0
    
    def test_detect_conflicts_with_modifications(self):
        """Test conflict detection with file modifications."""
        # Create different files
        (self.base_path / "modified.md").write_text("Base content")
        (self.personal_path / "modified.md").write_text("Personal content")
        
        library_sync = LibrarySync(
            base_path=self.base_path,
            personal_path=self.personal_path,
            backup_path=self.backup_path
        )
        
        conflicts = self.sync_service.detect_conflicts(library_sync)
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.MODIFIED
        assert conflicts[0].file_path == "modified.md"
    
    def test_create_backup(self):
        """Test backup creation."""
        # Create test files
        (self.personal_path / "file1.md").write_text("Content 1")
        (self.personal_path / "file2.md").write_text("Content 2")
        
        library_sync = LibrarySync(
            base_path=self.base_path,
            personal_path=self.personal_path,
            backup_path=self.backup_path
        )
        
        backup_dir = self.sync_service.create_backup(library_sync)
        
        # Verify backup was created
        assert backup_dir.exists()
        assert (backup_dir / "file1.md").exists()
        assert (backup_dir / "file2.md").exists()
        assert (backup_dir / "file1.md").read_text() == "Content 1"


class TestLibrarySync:
    """Test suite for LibrarySync model."""
    
    def test_library_sync_creation(self):
        """Test LibrarySync model creation."""
        sync = LibrarySync(
            base_path=Path("/base"),
            personal_path=Path("/personal"),
            backup_path=Path("/backup")
        )
        
        assert sync.base_path == Path("/base")
        assert sync.personal_path == Path("/personal")
        assert sync.backup_path == Path("/backup")
        assert len(sync.current_conflicts) == 0
    
    def test_add_conflict(self):
        """Test adding conflicts to LibrarySync."""
        sync = LibrarySync(
            base_path=Path("/base"),
            personal_path=Path("/personal"),
            backup_path=Path("/backup")
        )
        
        conflict = ConflictReport(
            file_path="test.md",
            conflict_type=ConflictType.MODIFIED,
            base_exists=True,
            personal_exists=True,
            suggested_resolution=Resolution.KEEP_LOCAL
        )
        
        sync.add_conflict(conflict)
        assert len(sync.current_conflicts) == 1
        assert sync.has_conflicts()
    
    def test_resolve_conflict(self):
        """Test conflict resolution."""
        sync = LibrarySync(
            base_path=Path("/base"),
            personal_path=Path("/personal"),
            backup_path=Path("/backup")
        )
        
        conflict = ConflictReport(
            file_path="test.md",
            conflict_type=ConflictType.MODIFIED,
            base_exists=True,
            personal_exists=True,
            suggested_resolution=Resolution.KEEP_LOCAL
        )
        
        sync.add_conflict(conflict)
        assert sync.has_conflicts()
        
        # Resolve conflict
        resolved = sync.resolve_conflict("test.md", Resolution.KEEP_LOCAL)
        assert resolved
        assert not sync.has_conflicts()


class TestConflictReport:
    """Test suite for ConflictReport model."""
    
    def test_conflict_report_creation(self):
        """Test ConflictReport creation."""
        conflict = ConflictReport(
            file_path="test.md",
            conflict_type=ConflictType.MODIFIED,
            base_exists=True,
            personal_exists=True,
            base_hash="hash1",
            personal_hash="hash2",
            suggested_resolution=Resolution.KEEP_LOCAL
        )
        
        assert conflict.file_path == "test.md"
        assert conflict.conflict_type == ConflictType.MODIFIED
        assert conflict.base_exists
        assert conflict.personal_exists
    
    def test_is_safe_merge(self):
        """Test safe merge detection."""
        # Safe merge scenario
        safe_conflict = ConflictReport(
            file_path="test.md",
            conflict_type=ConflictType.MODIFIED,
            base_exists=True,
            personal_exists=True,
            suggested_resolution=Resolution.MERGE
        )
        
        assert safe_conflict.is_safe_merge()
        
        # Unsafe merge scenario
        unsafe_conflict = ConflictReport(
            file_path="test.md",
            conflict_type=ConflictType.DELETED,
            base_exists=False,
            personal_exists=True,
            suggested_resolution=Resolution.KEEP_LOCAL
        )
        
        assert not unsafe_conflict.is_safe_merge()


if __name__ == "__main__":
    pytest.main([__file__])
