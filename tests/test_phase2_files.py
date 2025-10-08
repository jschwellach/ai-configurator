"""
Tests for Phase 2 file management features.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ai_configurator.models.file_models import (
    FilePattern, LocalResource, FileWatcher, FileDiscoveryResult
)
from ai_configurator.models.value_objects import LibrarySource
from ai_configurator.services.file_service import FileService


class TestFilePattern:
    """Test suite for FilePattern model."""
    
    def test_file_pattern_creation(self):
        """Test FilePattern creation."""
        pattern = FilePattern(
            pattern="**/*.md",
            base_path=Path("/test"),
            recursive=True,
            file_extensions={".md", ".txt"}
        )
        
        assert pattern.pattern == "**/*.md"
        assert pattern.base_path == Path("/test")
        assert pattern.recursive
        assert ".md" in pattern.file_extensions
    
    def test_resolve_pattern(self):
        """Test pattern resolution."""
        pattern = FilePattern(
            pattern="./docs/**/*.md",
            base_path=Path("/project")
        )
        
        resolved = pattern.resolve_pattern()
        assert resolved == "/project/docs/**/*.md"
    
    def test_matches_extension(self):
        """Test file extension matching."""
        pattern = FilePattern(
            pattern="**/*.md",
            base_path=Path("/test"),
            file_extensions={".md", ".txt"}
        )
        
        assert pattern.matches_extension(Path("test.md"))
        assert pattern.matches_extension(Path("test.txt"))
        assert not pattern.matches_extension(Path("test.py"))
    
    def test_is_excluded(self):
        """Test file exclusion."""
        pattern = FilePattern(
            pattern="**/*.md",
            base_path=Path("/test"),
            exclude_patterns=["**/temp/*", "**/*.tmp"]
        )
        
        assert pattern.is_excluded(Path("/test/temp/file.md"))
        assert pattern.is_excluded(Path("/test/file.tmp"))
        assert not pattern.is_excluded(Path("/test/docs/file.md"))


class TestLocalResource:
    """Test suite for LocalResource model."""
    
    def test_local_resource_creation(self):
        """Test LocalResource creation."""
        from datetime import datetime
        
        resource = LocalResource(
            file_path=Path("/test/file.md"),
            relative_path="file.md",
            content_hash="abc123",
            last_modified=datetime.now(),
            size_bytes=1024,
            source=LibrarySource.LOCAL
        )
        
        assert resource.file_path == Path("/test/file.md")
        assert resource.relative_path == "file.md"
        assert resource.source == LibrarySource.LOCAL
    
    def test_needs_update(self):
        """Test update detection."""
        from datetime import datetime, timedelta
        
        old_time = datetime.now() - timedelta(hours=1)
        new_time = datetime.now()
        
        resource = LocalResource(
            file_path=Path("/test/file.md"),
            relative_path="file.md",
            content_hash="old_hash",
            last_modified=old_time,
            size_bytes=1024
        )
        
        # Should need update if time is newer
        assert resource.needs_update(new_time, "old_hash")
        
        # Should need update if hash is different
        assert resource.needs_update(old_time, "new_hash")
        
        # Should not need update if both are same
        assert not resource.needs_update(old_time, "old_hash")


class TestFileService:
    """Test suite for FileService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.console = Mock()
        self.file_service = FileService(self.console)
        
        # Create temporary directory for testing
        self.test_dir = Path("/tmp/test_files")
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        test_file = self.test_dir / "test.md"
        test_file.write_text("# Test Content")
        
        hash1 = self.file_service.calculate_file_hash(test_file)
        hash2 = self.file_service.calculate_file_hash(test_file)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
    
    def test_discover_files(self):
        """Test file discovery."""
        # Create test files
        (self.test_dir / "doc1.md").write_text("Content 1")
        (self.test_dir / "doc2.md").write_text("Content 2")
        (self.test_dir / "script.py").write_text("print('hello')")
        
        # Create subdirectory
        subdir = self.test_dir / "subdir"
        subdir.mkdir()
        (subdir / "doc3.md").write_text("Content 3")
        
        # Test pattern matching
        pattern = FilePattern(
            pattern="**/*.md",
            base_path=self.test_dir,
            recursive=True
        )
        
        result = self.file_service.discover_files([pattern])
        
        assert result.total_files == 3  # Should find 3 .md files
        assert len(result.discovered_files) == 3
        assert not result.errors
        
        # Check that all found files are .md files
        for file_path in result.discovered_files:
            assert file_path.suffix == ".md"
    
    def test_create_local_resource(self):
        """Test local resource creation."""
        test_file = self.test_dir / "test.md"
        test_file.write_text("# Test Content")
        
        resource = self.file_service.create_local_resource(test_file, self.test_dir)
        
        assert resource is not None
        assert resource.file_path == test_file
        assert resource.relative_path == "test.md"
        assert resource.source == LibrarySource.LOCAL
        assert resource.size_bytes > 0
    
    def test_get_watch_status(self):
        """Test watch status retrieval."""
        agent_id = "test_agent"
        
        status = self.file_service.get_watch_status(agent_id)
        
        assert status["agent_id"] == agent_id
        assert not status["is_watching"]
        assert not status["is_active"]
        assert status["watched_files_count"] == 0


class TestFileDiscoveryResult:
    """Test suite for FileDiscoveryResult model."""
    
    def test_file_discovery_result_creation(self):
        """Test FileDiscoveryResult creation."""
        result = FileDiscoveryResult()
        
        assert result.total_files == 0
        assert len(result.discovered_files) == 0
        assert len(result.matched_patterns) == 0
        assert len(result.errors) == 0
    
    def test_add_file(self):
        """Test adding files to discovery result."""
        result = FileDiscoveryResult()
        
        result.add_file(Path("/test/file1.md"), "**/*.md")
        result.add_file(Path("/test/file2.md"), "**/*.md")
        
        assert result.total_files == 2
        assert len(result.discovered_files) == 2
        assert result.matched_patterns["**/*.md"] == 2
    
    def test_add_excluded(self):
        """Test adding excluded files."""
        result = FileDiscoveryResult()
        
        result.add_excluded(Path("/test/temp.md"))
        
        assert len(result.excluded_files) == 1
        assert result.excluded_files[0] == Path("/test/temp.md")
    
    def test_add_error(self):
        """Test adding errors."""
        result = FileDiscoveryResult()
        
        result.add_error("Test error message")
        
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error message"


if __name__ == "__main__":
    pytest.main([__file__])
