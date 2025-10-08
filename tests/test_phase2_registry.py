"""
Tests for Phase 2 MCP registry features.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from ai_configurator.models.registry_models import (
    MCPServerRegistry, MCPServerMetadata, InstallationManager, InstallationStatus
)
from ai_configurator.models.value_objects import HealthStatus
from ai_configurator.services.registry_service import RegistryService


class TestMCPServerMetadata:
    """Test suite for MCPServerMetadata model."""
    
    def test_server_metadata_creation(self):
        """Test MCPServerMetadata creation."""
        server = MCPServerMetadata(
            name="test-server",
            display_name="Test Server",
            description="A test server",
            version="1.0.0",
            install_command="npm install test-server",
            install_type="npm",
            category="test",
            tags=["test", "example"],
            platforms=["linux", "macos"]
        )
        
        assert server.name == "test-server"
        assert server.display_name == "Test Server"
        assert server.version == "1.0.0"
        assert "test" in server.tags
        assert "linux" in server.platforms
    
    def test_is_compatible(self):
        """Test platform compatibility check."""
        server = MCPServerMetadata(
            name="test-server",
            display_name="Test Server",
            description="A test server",
            version="1.0.0",
            install_command="npm install test-server",
            install_type="npm",
            platforms=["linux", "macos"]
        )
        
        assert server.is_compatible("linux")
        assert server.is_compatible("Linux")  # Case insensitive
        assert server.is_compatible("macos")
        assert not server.is_compatible("windows")
    
    def test_matches_search(self):
        """Test search matching."""
        server = MCPServerMetadata(
            name="git-server",
            display_name="Git Server",
            description="Git repository operations",
            version="1.0.0",
            install_command="npm install git-server",
            install_type="npm",
            category="development",
            tags=["git", "version-control"]
        )
        
        assert server.matches_search("git")
        assert server.matches_search("Git")  # Case insensitive
        assert server.matches_search("repository")
        assert server.matches_search("development")
        assert server.matches_search("version-control")
        assert not server.matches_search("database")


class TestMCPServerRegistry:
    """Test suite for MCPServerRegistry model."""
    
    def test_registry_creation(self):
        """Test MCPServerRegistry creation."""
        registry = MCPServerRegistry()
        
        assert len(registry.servers) == 0
        assert len(registry.categories) == 0
        assert registry.registry_version == "1.0.0"
    
    def test_add_server(self):
        """Test adding server to registry."""
        registry = MCPServerRegistry()
        
        server = MCPServerMetadata(
            name="test-server",
            display_name="Test Server",
            description="A test server",
            version="1.0.0",
            install_command="npm install test-server",
            install_type="npm",
            category="test"
        )
        
        registry.add_server(server)
        
        assert len(registry.servers) == 1
        assert "test-server" in registry.servers
        assert "test" in registry.categories
        assert "test-server" in registry.categories["test"]
    
    def test_search_servers(self):
        """Test server search functionality."""
        registry = MCPServerRegistry()
        
        # Add test servers
        git_server = MCPServerMetadata(
            name="git-server",
            display_name="Git Server",
            description="Git operations",
            version="1.0.0",
            install_command="npm install git-server",
            install_type="npm",
            category="development",
            tags=["git"]
        )
        
        db_server = MCPServerMetadata(
            name="db-server",
            display_name="Database Server",
            description="Database operations",
            version="1.0.0",
            install_command="npm install db-server",
            install_type="npm",
            category="data",
            tags=["database"]
        )
        
        registry.add_server(git_server)
        registry.add_server(db_server)
        
        # Test search
        results = registry.search_servers("git")
        assert len(results) == 1
        assert results[0].name == "git-server"
        
        # Test category filter
        results = registry.search_servers("", category="data")
        assert len(results) == 1
        assert results[0].name == "db-server"
    
    def test_get_categories(self):
        """Test category retrieval."""
        registry = MCPServerRegistry()
        
        server1 = MCPServerMetadata(
            name="server1", display_name="Server 1", description="Test",
            version="1.0.0", install_command="test", install_type="npm",
            category="cat1"
        )
        
        server2 = MCPServerMetadata(
            name="server2", display_name="Server 2", description="Test",
            version="1.0.0", install_command="test", install_type="npm",
            category="cat2"
        )
        
        registry.add_server(server1)
        registry.add_server(server2)
        
        categories = registry.get_categories()
        assert "cat1" in categories
        assert "cat2" in categories
        assert len(categories) == 2


class TestInstallationStatus:
    """Test suite for InstallationStatus model."""
    
    def test_installation_status_creation(self):
        """Test InstallationStatus creation."""
        status = InstallationStatus(
            server_name="test-server",
            installed=True,
            install_path=Path("/test/path"),
            installed_version="1.0.0"
        )
        
        assert status.server_name == "test-server"
        assert status.installed
        assert status.install_path == Path("/test/path")
        assert status.installed_version == "1.0.0"
    
    def test_needs_update(self):
        """Test update detection."""
        status = InstallationStatus(
            server_name="test-server",
            installed=True,
            installed_version="1.0.0"
        )
        
        # Should need update for newer version
        assert status.needs_update("1.1.0")
        assert status.needs_update("2.0.0")
        
        # Should not need update for same or older version
        assert not status.needs_update("1.0.0")
        assert not status.needs_update("0.9.0")


class TestInstallationManager:
    """Test suite for InstallationManager model."""
    
    def test_installation_manager_creation(self):
        """Test InstallationManager creation."""
        manager = InstallationManager(
            install_directory=Path("/test/install")
        )
        
        assert manager.install_directory == Path("/test/install")
        assert len(manager.installations) == 0
    
    def test_get_installation_status(self):
        """Test getting installation status."""
        manager = InstallationManager(
            install_directory=Path("/test/install")
        )
        
        # Should return default status for unknown server
        status = manager.get_installation_status("unknown-server")
        assert status.server_name == "unknown-server"
        assert not status.installed
    
    def test_update_installation_status(self):
        """Test updating installation status."""
        manager = InstallationManager(
            install_directory=Path("/test/install")
        )
        
        status = InstallationStatus(
            server_name="test-server",
            installed=True,
            installed_version="1.0.0"
        )
        
        manager.update_installation_status(status)
        
        retrieved = manager.get_installation_status("test-server")
        assert retrieved.installed
        assert retrieved.installed_version == "1.0.0"
    
    def test_get_installed_servers(self):
        """Test getting list of installed servers."""
        manager = InstallationManager(
            install_directory=Path("/test/install")
        )
        
        # Add installed server
        status1 = InstallationStatus(
            server_name="server1",
            installed=True
        )
        
        # Add uninstalled server
        status2 = InstallationStatus(
            server_name="server2",
            installed=False
        )
        
        manager.update_installation_status(status1)
        manager.update_installation_status(status2)
        
        installed = manager.get_installed_servers()
        assert len(installed) == 1
        assert installed[0].server_name == "server1"


class TestRegistryService:
    """Test suite for RegistryService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path("/tmp/test_registry")
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.console = Mock()
        self.registry_service = RegistryService(self.test_dir, self.console)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_load_empty_registry(self):
        """Test loading empty registry."""
        registry = self.registry_service.load_registry()
        
        assert isinstance(registry, MCPServerRegistry)
        assert len(registry.servers) == 0
    
    def test_save_and_load_registry(self):
        """Test saving and loading registry."""
        registry = MCPServerRegistry()
        
        server = MCPServerMetadata(
            name="test-server",
            display_name="Test Server",
            description="A test server",
            version="1.0.0",
            install_command="npm install test-server",
            install_type="npm"
        )
        
        registry.add_server(server)
        
        # Save registry
        success = self.registry_service.save_registry(registry)
        assert success
        
        # Load registry
        loaded_registry = self.registry_service.load_registry()
        assert len(loaded_registry.servers) == 1
        assert "test-server" in loaded_registry.servers
    
    def test_create_sample_registry(self):
        """Test sample registry creation."""
        self.registry_service.create_sample_registry()
        
        registry = self.registry_service.load_registry()
        assert len(registry.servers) > 0
        
        # Check that sample servers exist
        server_names = list(registry.servers.keys())
        assert "filesystem" in server_names
        assert "git" in server_names
        assert "database" in server_names


if __name__ == "__main__":
    pytest.main([__file__])
