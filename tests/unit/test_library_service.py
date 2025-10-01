"""
Unit tests for LibraryService.
"""

import tempfile
from pathlib import Path
from datetime import datetime

from ai_configurator.services import LibraryService
from ai_configurator.models import LibrarySource, ConflictType, Resolution


class TestLibraryService:
    """Test cases for LibraryService."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.base_path = self.temp_dir / "base"
        self.personal_path = self.temp_dir / "personal"
        
        # Create base library structure
        self.base_path.mkdir(parents=True)
        (self.base_path / "roles").mkdir()
        (self.base_path / "common").mkdir()
        (self.base_path / "roles" / "engineer.md").write_text("# Software Engineer\nBase content")
        (self.base_path / "common" / "policies.md").write_text("# Policies\nBase policies")
        
        self.service = LibraryService(self.base_path, self.personal_path)
    
    def test_create_library(self):
        """Test creating a new library instance."""
        library = self.service.create_library()
        
        assert library.base_path == self.base_path
        assert library.personal_path == self.personal_path
        assert library.metadata.version == "4.0.0"
        assert len(library.files) == 0
    
    def test_sync_library_no_conflicts(self):
        """Test library sync with no conflicts."""
        library = self.service.create_library()
        conflicts = self.service.sync_library(library)
        
        assert len(conflicts) == 0
        assert len(library.files) == 2  # engineer.md and policies.md
        assert library.metadata.sync_status.value == "synced"
        assert library.metadata.base_hash != ""
    
    def test_sync_library_with_conflicts(self):
        """Test library sync detecting conflicts."""
        # Create personal file with different content
        (self.personal_path / "roles").mkdir(parents=True, exist_ok=True)
        (self.personal_path / "roles" / "engineer.md").write_text("# Software Engineer\nPersonal content")
        
        library = self.service.create_library()
        conflicts = self.service.sync_library(library)
        
        assert len(conflicts) == 1
        assert conflicts[0].file_path == "roles/engineer.md"
        assert conflicts[0].conflict_type == ConflictType.MODIFIED
        assert library.metadata.sync_status.value == "conflicts"
    
    def test_resolve_conflict_accept_remote(self):
        """Test resolving conflict by accepting remote (base) version."""
        # Set up conflict
        self.personal_path.mkdir(parents=True)
        (self.personal_path / "roles").mkdir()
        (self.personal_path / "roles" / "engineer.md").write_text("Personal content")
        
        library = self.service.create_library()
        self.service.sync_library(library)
        
        # Resolve conflict
        success = self.service.resolve_conflict(library, "roles/engineer.md", Resolution.ACCEPT_REMOTE)
        
        assert success is True
        personal_file = self.personal_path / "roles" / "engineer.md"
        assert personal_file.exists()
        assert "Base content" in personal_file.read_text()
    
    def test_resolve_conflict_keep_local(self):
        """Test resolving conflict by keeping local version."""
        # Set up conflict
        self.personal_path.mkdir(parents=True)
        (self.personal_path / "roles").mkdir()
        personal_file = self.personal_path / "roles" / "engineer.md"
        personal_file.write_text("Personal content")
        
        library = self.service.create_library()
        self.service.sync_library(library)
        
        # Resolve conflict
        success = self.service.resolve_conflict(library, "roles/engineer.md", Resolution.KEEP_LOCAL)
        
        assert success is True
        assert "Personal content" in personal_file.read_text()
    
    def test_discover_files(self):
        """Test file discovery functionality."""
        library = self.service.create_library()
        self.service.sync_library(library)
        
        files = self.service.discover_files(library)
        
        assert "roles/engineer.md" in files
        assert "common/policies.md" in files
        assert len(files) == 2
    
    def test_get_file_content_base(self):
        """Test getting content from base library."""
        library = self.service.create_library()
        self.service.sync_library(library)
        
        content = self.service.get_file_content(library, "roles/engineer.md")
        
        assert content is not None
        assert "Base content" in content
    
    def test_get_file_content_personal_override(self):
        """Test personal library overriding base content."""
        # Create personal override
        self.personal_path.mkdir(parents=True)
        (self.personal_path / "roles").mkdir()
        (self.personal_path / "roles" / "engineer.md").write_text("Personal override")
        
        library = self.service.create_library()
        self.service.sync_library(library)
        
        content = self.service.get_file_content(library, "roles/engineer.md")
        
        assert content is not None
        assert "Personal override" in content
    
    def test_save_personal_file(self):
        """Test saving content to personal library."""
        library = self.service.create_library()
        
        success = self.service.save_personal_file(library, "custom/my-role.md", "# My Custom Role")
        
        assert success is True
        personal_file = self.personal_path / "custom" / "my-role.md"
        assert personal_file.exists()
        assert "# My Custom Role" in personal_file.read_text()
        assert "personal/custom/my-role.md" in library.files
