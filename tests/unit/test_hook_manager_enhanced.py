#!/usr/bin/env python3
"""
Test suite for the enhanced HookManager with YAML support.
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from src.ai_configurator.core.hook_manager import HookManager
from src.ai_configurator.core.models import HookType, HookTrigger
from src.ai_configurator.core.platform import PlatformManager
from src.ai_configurator.core.config_manager import ConfigurationManager
from src.ai_configurator.core.yaml_loader import YamlConfigLoader
from src.ai_configurator.core.markdown_processor import MarkdownProcessor


class TestEnhancedHookManager:
    """Test cases for enhanced HookManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.hooks_dir = self.temp_dir / "hooks"
        self.hooks_dir.mkdir(parents=True)
        
        # Mock dependencies
        self.platform_manager = Mock(spec=PlatformManager)
        self.platform_manager.get_platform_name.return_value = "Darwin"
        self.platform_manager.is_windows.return_value = False
        
        self.config_manager = Mock(spec=ConfigurationManager)
        self.config_manager.config_dir = self.temp_dir
        
        self.yaml_loader = YamlConfigLoader(self.temp_dir)
        self.markdown_processor = MarkdownProcessor()
        
        # Create HookManager instance
        self.hook_manager = HookManager(
            platform_manager=self.platform_manager,
            config_manager=self.config_manager,
            yaml_loader=self.yaml_loader,
            markdown_processor=self.markdown_processor
        )
        
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_hook_yaml(self, hook_name: str, hook_type: HookType = HookType.CONTEXT, 
                            trigger: HookTrigger = HookTrigger.ON_SESSION_START) -> Path:
        """Create a test hook YAML file."""
        hook_config = {
            "name": hook_name,
            "description": f"Test hook {hook_name}",
            "version": "1.0",
            "type": hook_type.value,
            "trigger": trigger.value,
            "timeout": 30,
            "enabled": True
        }
        
        if hook_type in [HookType.CONTEXT, HookType.HYBRID]:
            hook_config["context"] = {
                "sources": [f"hooks/{hook_name}.md"],
                "tags": ["test"],
                "categories": ["testing"],
                "priority": 0
            }
        
        if hook_type in [HookType.SCRIPT, HookType.HYBRID]:
            hook_config["script"] = {
                "command": "echo",
                "args": [f"Hook {hook_name} executed"],
                "env": {"TEST_MODE": "true"},
                "timeout": 10
            }
        
        hook_file = self.hooks_dir / f"{hook_name}.yaml"
        with open(hook_file, 'w') as f:
            yaml.dump(hook_config, f)
        
        return hook_file
    
    def create_test_markdown(self, hook_name: str) -> Path:
        """Create a test Markdown file for context."""
        content = f"""---
title: "{hook_name} Context"
tags: ["test", "context"]
categories: ["testing"]
priority: 0
---

# {hook_name} Test Context

This is test context for the {hook_name} hook.

## Test Information

This hook is used for testing the enhanced hook management system.
"""
        
        md_file = self.hooks_dir / f"{hook_name}.md"
        with open(md_file, 'w') as f:
            f.write(content)
        
        return md_file
    
    def test_discover_hooks(self):
        """Test hook discovery functionality."""
        # Create test hooks
        self.create_test_hook_yaml("test_context", HookType.CONTEXT)
        self.create_test_hook_yaml("test_script", HookType.SCRIPT)
        self.create_test_markdown("test_context")
        
        discovered = self.hook_manager.discover_hooks()
        
        assert "test_context" in discovered["yaml"]
        assert "test_script" in discovered["yaml"]
        assert "test_context" in discovered["markdown"]
        assert len(discovered["yaml"]) == 2
        assert len(discovered["markdown"]) == 1
    
    def test_load_hook_config(self):
        """Test loading hook configuration."""
        # Create test hook
        self.create_test_hook_yaml("test_hook", HookType.CONTEXT, HookTrigger.PER_USER_MESSAGE)
        
        hook_config = self.hook_manager.load_hook_config("test_hook")
        
        assert hook_config is not None
        assert hook_config.name == "test_hook"
        assert hook_config.type == HookType.CONTEXT
        assert hook_config.trigger == HookTrigger.PER_USER_MESSAGE
        assert hook_config.enabled is True
    
    def test_load_hooks_by_trigger(self):
        """Test loading hooks by trigger type."""
        # Clear any existing hooks and cache
        for hook_file in self.hooks_dir.glob("*.yaml"):
            hook_file.unlink()
        for md_file in self.hooks_dir.glob("*.md"):
            md_file.unlink()
        self.hook_manager.reload_hooks()
        
        # Create hooks with different triggers
        self.create_test_hook_yaml("session_hook", HookType.CONTEXT, HookTrigger.ON_SESSION_START)
        self.create_test_hook_yaml("message_hook", HookType.SCRIPT, HookTrigger.PER_USER_MESSAGE)
        self.create_test_hook_yaml("file_hook", HookType.HYBRID, HookTrigger.ON_FILE_CHANGE)
        
        session_hooks = self.hook_manager.load_hooks_by_trigger(HookTrigger.ON_SESSION_START)
        message_hooks = self.hook_manager.load_hooks_by_trigger(HookTrigger.PER_USER_MESSAGE)
        file_hooks = self.hook_manager.load_hooks_by_trigger(HookTrigger.ON_FILE_CHANGE)
        

        assert len(session_hooks) == 1
        assert len(message_hooks) == 1
        assert len(file_hooks) == 1
        assert session_hooks[0].name == "session_hook"
        assert message_hooks[0].name == "message_hook"
        assert file_hooks[0].name == "file_hook"
    
    def test_execute_context_hook(self):
        """Test executing a context-type hook."""
        # Create test hook and markdown
        self.create_test_hook_yaml("context_test", HookType.CONTEXT)
        self.create_test_markdown("context_test")
        
        hook_config = self.hook_manager.load_hook_config("context_test")
        success, output, error = self.hook_manager.execute_hook(hook_config)
        
        assert success is True
        assert "This is test context for the context_test hook" in output
        assert error == ""
    
    @patch('subprocess.run')
    def test_execute_script_hook(self, mock_run):
        """Test executing a script-type hook."""
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Hook test_script executed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create test hook
        self.create_test_hook_yaml("test_script", HookType.SCRIPT)
        
        hook_config = self.hook_manager.load_hook_config("test_script")
        success, output, error = self.hook_manager.execute_hook(hook_config)
        
        assert success is True
        assert output == "Hook test_script executed"
        assert error == ""
        
        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "echo"
        assert "Hook test_script executed" in call_args[0][0]
    
    @patch('subprocess.run')
    def test_execute_hybrid_hook(self, mock_run):
        """Test executing a hybrid-type hook."""
        # Mock subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Script executed with context"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # Create test hook and markdown
        self.create_test_hook_yaml("hybrid_test", HookType.HYBRID)
        self.create_test_markdown("hybrid_test")
        
        hook_config = self.hook_manager.load_hook_config("hybrid_test")
        success, output, error = self.hook_manager.execute_hook(hook_config)
        
        assert success is True
        assert "This is test context for the hybrid_test hook" in output
        assert "Script executed with context" in output
        assert error == ""
    
    def test_execute_hooks_for_trigger(self):
        """Test executing multiple hooks for a trigger."""
        # Create multiple hooks for the same trigger
        self.create_test_hook_yaml("hook1", HookType.CONTEXT, HookTrigger.ON_SESSION_START)
        self.create_test_hook_yaml("hook2", HookType.CONTEXT, HookTrigger.ON_SESSION_START)
        self.create_test_markdown("hook1")
        self.create_test_markdown("hook2")
        
        results = self.hook_manager.execute_hooks_for_trigger(HookTrigger.ON_SESSION_START)
        
        assert len(results) == 2
        # Results should be sorted by hook name
        assert results[0][0] == "hook1"  # hook name
        assert results[1][0] == "hook2"  # hook name
        assert results[0][1] is True     # success
        assert results[1][1] is True     # success
    
    def test_hook_conditions_platform(self):
        """Test hook condition checking for platform."""
        # Create hook with platform condition
        hook_config = {
            "name": "platform_test",
            "type": "context",
            "trigger": "on_session_start",
            "enabled": True,
            "context": {"sources": []},
            "conditions": [
                {"platform": ["linux", "darwin"]}
            ]
        }
        
        hook_file = self.hooks_dir / "platform_test.yaml"
        with open(hook_file, 'w') as f:
            yaml.dump(hook_config, f)
        
        loaded_config = self.hook_manager.load_hook_config("platform_test")
        assert self.hook_manager._check_hook_conditions(loaded_config) is True
        
        # Test with non-matching platform
        hook_config["conditions"][0]["platform"] = ["windows"]
        with open(hook_file, 'w') as f:
            yaml.dump(hook_config, f)
        
        # Clear cache and reload
        self.hook_manager._hook_cache.clear()
        loaded_config = self.hook_manager.load_hook_config("platform_test")
        assert self.hook_manager._check_hook_conditions(loaded_config) is False
    
    def test_validate_hooks(self):
        """Test hook validation functionality."""
        # Clear any existing hooks and cache
        for hook_file in self.hooks_dir.glob("*.yaml"):
            hook_file.unlink()
        for md_file in self.hooks_dir.glob("*.md"):
            md_file.unlink()
        self.hook_manager.reload_hooks()
        
        # Create valid hook
        self.create_test_hook_yaml("valid_hook", HookType.CONTEXT)
        self.create_test_markdown("valid_hook")
        
        # Create invalid hook (missing context sources)
        invalid_config = {
            "name": "invalid_hook",
            "type": "context",
            "trigger": "on_session_start",
            "enabled": True,
            "context": {"sources": ["nonexistent.md"]}
        }
        
        invalid_file = self.hooks_dir / "invalid_hook.yaml"
        with open(invalid_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        validation_report = self.hook_manager.validate_hooks()
        
        assert validation_report.summary["total_hooks"] == 2
        assert len(validation_report.errors) > 0  # Should have error for missing file
        assert any("nonexistent.md" in error.message for error in validation_report.errors)
    
    def test_create_hook_template(self):
        """Test creating hook templates."""
        success = self.hook_manager.create_hook_template(
            "new_hook", 
            HookType.CONTEXT, 
            HookTrigger.ON_SESSION_START
        )
        
        assert success is True
        
        # Check YAML file was created
        yaml_file = self.hooks_dir / "new_hook.yaml"
        assert yaml_file.exists()
        
        # Check Markdown file was created
        md_file = self.hooks_dir / "new_hook.md"
        assert md_file.exists()
        
        # Verify content
        with open(yaml_file) as f:
            config = yaml.safe_load(f)
        
        assert config["name"] == "new_hook"
        assert config["type"] == "context"
        assert config["trigger"] == "on_session_start"
    
    def test_get_hook_info(self):
        """Test getting hook information."""
        self.create_test_hook_yaml("info_test", HookType.HYBRID, HookTrigger.PER_USER_MESSAGE)
        
        info = self.hook_manager.get_hook_info("info_test")
        
        assert info is not None
        assert info["name"] == "info_test"
        assert info["type"] == "hybrid"
        assert info["trigger"] == "per_user_message"
        assert info["has_context"] is True
        assert info["has_script"] is True
    
    def test_list_hooks_by_trigger(self):
        """Test listing hooks organized by trigger."""
        self.create_test_hook_yaml("session1", HookType.CONTEXT, HookTrigger.ON_SESSION_START)
        self.create_test_hook_yaml("session2", HookType.SCRIPT, HookTrigger.ON_SESSION_START)
        self.create_test_hook_yaml("message1", HookType.CONTEXT, HookTrigger.PER_USER_MESSAGE)
        
        hooks_by_trigger = self.hook_manager.list_hooks_by_trigger()
        
        assert "on_session_start" in hooks_by_trigger
        assert "per_user_message" in hooks_by_trigger
        assert len(hooks_by_trigger["on_session_start"]) == 2
        assert len(hooks_by_trigger["per_user_message"]) == 1
        assert "session1" in hooks_by_trigger["on_session_start"]
        assert "session2" in hooks_by_trigger["on_session_start"]
        assert "message1" in hooks_by_trigger["per_user_message"]


if __name__ == "__main__":
    # Run basic tests
    test_instance = TestEnhancedHookManager()
    test_instance.setup_method()
    
    try:
        print("Testing hook discovery...")
        test_instance.test_discover_hooks()
        print("✓ Hook discovery test passed")
        
        print("Testing hook config loading...")
        test_instance.test_load_hook_config()
        print("✓ Hook config loading test passed")
        
        print("Testing hooks by trigger...")
        test_instance.test_load_hooks_by_trigger()
        print("✓ Hooks by trigger test passed")
        
        print("Testing context hook execution...")
        test_instance.test_execute_context_hook()
        print("✓ Context hook execution test passed")
        
        print("Testing hook template creation...")
        test_instance.test_create_hook_template()
        print("✓ Hook template creation test passed")
        
        print("Testing hook validation...")
        test_instance.test_validate_hooks()
        print("✓ Hook validation test passed")
        
        print("\n✅ All enhanced HookManager tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        test_instance.teardown_method()