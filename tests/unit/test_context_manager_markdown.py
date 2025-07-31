#!/usr/bin/env python3
"""Test the enhanced ContextManager with Markdown support."""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.ai_configurator.core.context_manager import ContextManager
from src.ai_configurator.core.models import GlobalContext, ProfileContext, ContextFile


class TestContextManagerMarkdown:
    """Test ContextManager with Markdown frontmatter support."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.contexts_dir = self.config_dir / "contexts"
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock platform and config managers
        self.mock_platform = Mock()
        self.mock_config_manager = Mock()
        self.mock_config_manager.config_dir = self.config_dir
        
        # Create ContextManager instance
        self.context_manager = ContextManager(
            platform_manager=self.mock_platform,
            config_manager=self.mock_config_manager
        )
    
    def create_test_markdown_file(self, filename: str, content: str, frontmatter: dict = None):
        """Create a test Markdown file with optional frontmatter."""
        file_path = self.contexts_dir / filename
        
        if frontmatter:
            import yaml
            frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
            full_content = f"---\n{frontmatter_yaml}---\n{content}"
        else:
            full_content = content
        
        file_path.write_text(full_content, encoding='utf-8')
        return file_path
    
    def test_load_context_files_with_frontmatter(self):
        """Test loading context files with YAML frontmatter."""
        # Create test files
        self.create_test_markdown_file(
            "test1.md",
            "This is test content 1",
            {"title": "Test 1", "tags": ["dev", "test"], "priority": 5}
        )
        
        self.create_test_markdown_file(
            "test2.md",
            "This is test content 2",
            {"title": "Test 2", "categories": ["docs"], "priority": 3}
        )
        
        # Load context files
        paths = ["contexts/test1.md", "contexts/test2.md"]
        context_files = self.context_manager.load_context_files(paths)
        
        assert len(context_files) == 2
        
        # Check first file
        assert context_files[0].content == "This is test content 1"
        assert context_files[0].tags == ["dev", "test"]
        assert context_files[0].priority == 5
        
        # Check second file
        assert context_files[1].content == "This is test content 2"
        assert context_files[1].categories == ["docs"]
        assert context_files[1].priority == 3
    
    def test_organize_contexts_by_tags(self):
        """Test organizing contexts by tags."""
        # Create context files with different tags
        context_files = [
            ContextFile(
                file_path="test1.md",
                content="Content 1",
                tags=["dev", "api"],
                priority=1
            ),
            ContextFile(
                file_path="test2.md",
                content="Content 2",
                tags=["dev", "ui"],
                priority=2
            ),
            ContextFile(
                file_path="test3.md",
                content="Content 3",
                tags=["docs"],
                priority=3
            )
        ]
        
        organized = self.context_manager.organize_contexts_by_tags(context_files)
        
        assert "dev" in organized
        assert len(organized["dev"]) == 2
        assert "api" in organized
        assert len(organized["api"]) == 1
        assert "docs" in organized
        assert len(organized["docs"]) == 1
    
    def test_organize_contexts_by_categories(self):
        """Test organizing contexts by categories."""
        context_files = [
            ContextFile(
                file_path="test1.md",
                content="Content 1",
                categories=["development", "backend"],
                priority=1
            ),
            ContextFile(
                file_path="test2.md",
                content="Content 2",
                categories=["development", "frontend"],
                priority=2
            ),
            ContextFile(
                file_path="test3.md",
                content="Content 3",
                categories=["documentation"],
                priority=3
            )
        ]
        
        organized = self.context_manager.organize_contexts_by_categories(context_files)
        
        assert "development" in organized
        assert len(organized["development"]) == 2
        assert "backend" in organized
        assert len(organized["backend"]) == 1
        assert "documentation" in organized
        assert len(organized["documentation"]) == 1
    
    def test_sort_contexts_by_priority(self):
        """Test sorting contexts by priority."""
        context_files = [
            ContextFile(file_path="test1.md", content="Content 1", priority=1),
            ContextFile(file_path="test2.md", content="Content 2", priority=5),
            ContextFile(file_path="test3.md", content="Content 3", priority=3),
        ]
        
        sorted_files = self.context_manager.sort_contexts_by_priority(context_files)
        
        assert sorted_files[0].priority == 5
        assert sorted_files[1].priority == 3
        assert sorted_files[2].priority == 1
    
    def test_get_context_by_tags(self):
        """Test filtering contexts by tags."""
        # Create test files
        self.create_test_markdown_file(
            "dev1.md",
            "Development content 1",
            {"tags": ["dev", "api"], "priority": 5}
        )
        
        self.create_test_markdown_file(
            "dev2.md",
            "Development content 2",
            {"tags": ["dev", "ui"], "priority": 3}
        )
        
        self.create_test_markdown_file(
            "docs.md",
            "Documentation content",
            {"tags": ["docs"], "priority": 1}
        )
        
        # Mock config manager to return test paths
        global_context = GlobalContext(paths=["contexts/dev1.md", "contexts/dev2.md", "contexts/docs.md"])
        self.mock_config_manager.load_global_context.return_value = global_context
        self.mock_config_manager.load_profile_context.return_value = None
        
        # Get contexts by tags
        dev_contexts = self.context_manager.get_context_by_tags(["dev"])
        
        assert len(dev_contexts) == 2
        assert all("dev" in cf.tags for cf in dev_contexts)
        # Should be sorted by priority (highest first)
        assert dev_contexts[0].priority == 5
        assert dev_contexts[1].priority == 3
    
    def test_get_high_priority_contexts(self):
        """Test filtering contexts by priority threshold."""
        # Create test files with different priorities
        self.create_test_markdown_file(
            "high1.md",
            "High priority content 1",
            {"priority": 10}
        )
        
        self.create_test_markdown_file(
            "high2.md",
            "High priority content 2",
            {"priority": 5}
        )
        
        self.create_test_markdown_file(
            "low.md",
            "Low priority content",
            {"priority": 1}
        )
        
        # Mock config manager
        global_context = GlobalContext(paths=["contexts/high1.md", "contexts/high2.md", "contexts/low.md"])
        self.mock_config_manager.load_global_context.return_value = global_context
        self.mock_config_manager.load_profile_context.return_value = None
        
        # Get high priority contexts
        high_priority = self.context_manager.get_high_priority_contexts(min_priority=5)
        
        assert len(high_priority) == 2
        assert all(cf.priority >= 5 for cf in high_priority)
        # Should be sorted by priority (highest first)
        assert high_priority[0].priority == 10
        assert high_priority[1].priority == 5
    
    def test_context_caching(self):
        """Test that context files are cached to prevent duplication."""
        # Create test file
        self.create_test_markdown_file(
            "cached.md",
            "Cached content",
            {"title": "Cached", "priority": 1}
        )
        
        # Load the same file multiple times
        paths = ["contexts/cached.md"]
        context_files1 = self.context_manager.load_context_files(paths)
        context_files2 = self.context_manager.load_context_files(paths)
        
        # Should return the same cached instance
        assert len(context_files1) == 1
        assert len(context_files2) == 1
        assert context_files1[0] is context_files2[0]  # Same object reference
        
        # Check cache size
        assert len(self.context_manager._context_cache) == 1
    
    def test_clear_context_cache(self):
        """Test clearing the context cache."""
        # Create and load test file
        self.create_test_markdown_file("test.md", "Test content")
        paths = ["contexts/test.md"]
        self.context_manager.load_context_files(paths)
        
        # Verify cache has content
        assert len(self.context_manager._context_cache) == 1
        
        # Clear cache
        self.context_manager.clear_context_cache()
        
        # Verify cache is empty
        assert len(self.context_manager._context_cache) == 0
    
    def test_get_context_metadata_summary(self):
        """Test getting context metadata summary."""
        # Create test files with various metadata
        self.create_test_markdown_file(
            "file1.md",
            "Content 1",
            {"tags": ["dev", "api"], "categories": ["backend"], "priority": 5}
        )
        
        self.create_test_markdown_file(
            "file2.md",
            "Content 2",
            {"tags": ["dev"], "categories": ["frontend"], "priority": 3}
        )
        
        self.create_test_markdown_file(
            "file3.md",
            "Content 3"  # No frontmatter
        )
        
        # Mock config manager
        global_context = GlobalContext(paths=["contexts/file1.md", "contexts/file2.md", "contexts/file3.md"])
        self.mock_config_manager.load_global_context.return_value = global_context
        self.mock_config_manager.load_profile_context.return_value = None
        
        # Get metadata summary
        summary = self.context_manager.get_context_metadata_summary()
        
        assert summary['total_files'] == 3
        assert summary['files_with_frontmatter'] == 2
        assert set(summary['unique_tags']) == {"dev", "api"}
        assert set(summary['unique_categories']) == {"backend", "frontend"}
        assert 5 in summary['priority_distribution']
        assert 3 in summary['priority_distribution']
        assert 0 in summary['priority_distribution']  # Default priority for file without frontmatter
    
    def test_load_organized_context_content(self):
        """Test loading organized context content."""
        # Create test files
        self.create_test_markdown_file(
            "high.md",
            "High priority content",
            {"priority": 10, "tags": ["important"]}
        )
        
        self.create_test_markdown_file(
            "low.md",
            "Low priority content",
            {"priority": 1, "tags": ["basic"]}
        )
        
        # Test priority organization
        paths = ["contexts/high.md", "contexts/low.md"]
        content = self.context_manager.load_organized_context_content(paths, organize_by="priority")
        
        # High priority should come first
        assert "High priority content" in content
        assert "Low priority content" in content
        assert content.index("High priority content") < content.index("Low priority content")
        
        # Test tag organization
        content_by_tags = self.context_manager.load_organized_context_content(paths, organize_by="tags")
        
        assert "TAGS: IMPORTANT" in content_by_tags
        assert "TAGS: BASIC" in content_by_tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])