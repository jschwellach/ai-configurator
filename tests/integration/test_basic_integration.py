#!/usr/bin/env python3
"""
Basic integration test to verify components work together.
"""

import tempfile
import shutil
from pathlib import Path

from src.ai_configurator.core import (
    ConfigurationManager,
    PlatformManager
)


def test_basic_integration():
    """Test basic integration of components."""
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Initialize platform manager with test directory
        platform = PlatformManager()
        platform._config_dir = temp_dir / "config"
        
        # Initialize configuration manager
        config_manager = ConfigurationManager(platform)
        
        # Test that all components are initialized
        assert config_manager.yaml_loader is not None
        assert config_manager.markdown_processor is not None
        assert config_manager.config_merger is not None
        assert config_manager.profile_manager is not None
        assert config_manager.hook_manager is not None
        assert config_manager.context_manager is not None
        assert config_manager.file_watcher is not None
        
        # Test directory creation
        assert config_manager.config_dir.exists()
        
        # Test enhanced methods exist
        assert hasattr(config_manager, 'load_enhanced_profile')
        assert hasattr(config_manager, 'list_all_profiles')
        assert hasattr(config_manager, 'validate_complete_configuration')
        assert hasattr(config_manager, 'execute_profile_workflow')
        
        print("✅ Basic integration test passed!")
        
    finally:
        # Cleanup
        config_manager.cleanup()
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_basic_integration()