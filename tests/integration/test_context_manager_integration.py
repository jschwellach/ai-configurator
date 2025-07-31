#!/usr/bin/env python3
"""Integration test for ContextManager backward compatibility."""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock

from src.ai_configurator.core.context_manager import ContextManager
from src.ai_configurator.core.models import GlobalContext, ProfileContext


class TestContextManagerIntegration:
    """Test ContextManager backward compatibility and integration."""
    
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
    
    def test_legacy_load_context_content_still_works(self):
        """Test that the legacy load_context_content method still works."""
        # Create a simple markdown file
        test_file = self.contexts_dir / "legacy.md"
        test_file.write_text("# Legacy Content\n\nThis is legacy content.", encoding='utf-8')
        
        # Test legacy method
        content = self.context_manager.load_context_content([test_file])
        
        assert "Legacy Content" in content
        assert "This is legacy content" in content
        assert "--- legacy.md ---" in content
    
    def test_resolve_context_paths_still_works(self):
        """Test that resolve_context_paths method still works."""
        # Create test files
        (self.contexts_dir / "test1.md").write_text("Test 1", encoding='utf-8')
        (self.contexts_dir / "test2.md").write_text("Test 2", encoding='utf-8')
        
        # Test path resolution
        paths = ["contexts/test1.md", "contexts/*.md"]
        resolved = self.context_manager.resolve_context_paths(paths)
        
        assert len(resolved) >= 2
        assert any("test1.md" in str(p) for p in resolved)
        assert any("test2.md" in str(p) for p in resolved)
    
    def test_get_combined_context_content_with_mocked_config(self):
        """Test combined context loading with mocked configuration."""
        # Create test files
        global_file = self.contexts_dir / "global.md"
        global_file.write_text("---\ntitle: Global Context\npriority: 10\n---\n# Global\nGlobal content", encoding='utf-8')
        
        profile_file = self.contexts_dir / "profile.md"
        profile_file.write_text("---\ntitle: Profile Context\npriority: 5\n---\n# Profile\nProfile content", encoding='utf-8')
        
        # Mock config manager responses
        global_context = GlobalContext(paths=["contexts/global.md"])
        profile_context = ProfileContext(paths=["contexts/profile.md"])
        
        self.mock_config_manager.load_global_context.return_value = global_context
        self.mock_config_manager.load_profile_context.return_value = profile_context
        
        # Test combined context loading
        combined_content = self.context_manager.get_combined_context_content("test_profile")
        
        assert "=== GLOBAL CONTEXT ===" in combined_content
        assert "=== PROFILE CONTEXT: TEST_PROFILE ===" in combined_content
        assert "Global content" in combined_content
        assert "Profile content" in combined_content
        
        # Global should come before profile due to priority
        global_pos = combined_content.find("Global content")
        profile_pos = combined_content.find("Profile content")
        assert global_pos < profile_pos
    
    def test_validate_context_paths_still_works(self):
        """Test that validate_context_paths method still works."""
        # Create test files
        (self.contexts_dir / "valid.md").write_text("Valid content", encoding='utf-8')
        
        # Test validation
        paths = ["contexts/valid.md", "contexts/nonexistent.md", "contexts/*.md"]
        validation = self.context_manager.validate_context_paths(paths)
        
        assert "contexts/valid.md" in validation["valid_paths"]
        assert "contexts/nonexistent.md" in validation["invalid_paths"]
        assert "contexts/*.md" in validation["glob_patterns"]
        assert validation["total_files"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])