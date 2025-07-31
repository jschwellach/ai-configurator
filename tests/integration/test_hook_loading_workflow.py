#!/usr/bin/env python3
"""Integration tests for hook loading workflows."""

import pytest
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.validator import ConfigurationValidator
from ai_configurator.core.hook_manager import HookManager


class TestHookLoadingWorkflow:
    """Integration tests for complete hook loading workflow."""
    
    def setup_method(self):
        """Set up test environment with realistic hook configurations."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
        # Create directory structure
        (self.test_dir / 'profiles').mkdir(exist_ok=True)
        (self.test_dir / 'hooks').mkdir(exist_ok=True)
        (self.test_dir / 'contexts').mkdir(exist_ok=True)
        
        # Initialize components
        self.loader = YamlConfigLoader(self.test_dir)
        self.validator = ConfigurationValidator(self.test_dir)
        self.hook_manager = HookManager(self.test_dir)
        
        self._create_test_hooks()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_hooks(self):
        """Create realistic test hook configurations."""
        # Create context files for hooks
        setup_context = self.test_dir / 'contexts' / 'setup-context.md'
        setup_context.write_text("""---
tags: [setup, initialization]
priority: 1
---

# Setup Context

Context for environment setup hooks.
""")
        
        enhancement_context = self.test_dir / 'contexts' / 'enhancement-context.md'
        enhancement_context.write_text("""---
tags: [enhancement, context]
priority: 2
---

# Enhancement Context

Context for message enhancement hooks.
""")
        
        # Create various types of hooks
        
        # 1. Context hook for session start
        session_hook = {
            'name': 'session-initializer',
            'description': 'Initialize session with development context',
            'version': '1.0',
            'type': 'context',
            'trigger': 'on_session_start',
            'timeout': 30,
            'enabled': True,
            'context': {
                'sources': ['contexts/setup-context.md'],
                'tags': ['setup', 'session'],
                'priority': 1
            },
            'conditions': [
                {
                    'profile': ['developer', 'solutions-architect'],
                    'platform': ['darwin', 'linux']
                }
            ]
        }
        
        with open(self.test_dir / 'hooks' / 'session-initializer.yaml', 'w') as f:
            yaml.dump(session_hook, f)
        
        # 2. Context hook for per-message enhancement
        message_hook = {
            'name': 'message-enhancer',
            'description': 'Enhance user messages with context',
            'version': '1.0',
            'type': 'context',
            'trigger': 'per_user_message',
            'timeout': 15,
            'enabled': True,
            'context': {
                'sources': ['contexts/enhancement-context.md'],
                'tags': ['enhancement', 'message'],
                'priority': 2
            }
        }
        
        with open(self.test_dir / 'hooks' / 'message-enhancer.yaml', 'w') as f:
            yaml.dump(message_hook, f)
        
        # 3. Script hook for file changes
        file_watcher_hook = {
            'name': 'file-watcher',
            'description': 'React to file changes',
            'version': '1.0',
            'type': 'script',
            'trigger': 'on_file_change',
            'timeout': 10,
            'enabled': True,
            'script': {
                'command': 'python',
                'args': ['scripts/file_handler.py'],
                'working_directory': '.',
                'environment': {
                    'HOOK_NAME': 'file-watcher'
                }
            }
        }
        
        with open(self.test_dir / 'hooks' / 'file-watcher.yaml', 'w') as f:
            yaml.dump(file_watcher_hook, f)
        
        # 4. Hybrid hook
        hybrid_hook = {
            'name': 'hybrid-processor',
            'description': 'Hybrid hook with both context and script',
            'version': '1.0',
            'type': 'hybrid',
            'trigger': 'per_user_message',
            'timeout': 25,
            'enabled': True,
            'context': {
                'sources': ['contexts/enhancement-context.md'],
                'tags': ['hybrid', 'processing'],
                'priority': 3
            },
            'script': {
                'command': 'python',
                'args': ['scripts/hybrid_processor.py'],
                'working_directory': '.'
            }
        }
        
        with open(self.test_dir / 'hooks' / 'hybrid-processor.yaml', 'w') as f:
            yaml.dump(hybrid_hook, f)
        
        # 5. Disabled hook
        disabled_hook = {
            'name': 'disabled-hook',
            'description': 'Hook that is disabled',
            'type': 'context',
            'trigger': 'on_session_start',
            'enabled': False,
            'context': {
                'sources': ['contexts/setup-context.md']
            }
        }
        
        with open(self.test_dir / 'hooks' / 'disabled-hook.yaml', 'w') as f:
            yaml.dump(disabled_hook, f)
    
    def test_complete_hook_discovery_workflow(self):
        """Test complete hook discovery workflow."""
        # Step 1: Discover all hooks
        discovered = self.loader.discover_configurations()
        
        assert 'hooks' in discovered
        assert len(discovered['hooks']) >= 5
        
        # Verify specific hooks are discovered
        hook_names = [Path(h).stem for h in discovered['hooks']]
        expected_hooks = [
            'session-initializer',
            'message-enhancer', 
            'file-watcher',
            'hybrid-processor',
            'disabled-hook'
        ]
        
        for expected in expected_hooks:
            assert expected in hook_names, f"Hook {expected} should be discovered"
    
    def test_hook_validation_workflow(self):
        """Test hook validation workflow."""
        # Validate all hook configurations
        validation_report = self.validator.validate_all_configurations()
        
        # All hooks should be valid
        assert validation_report.is_valid is True
        assert len(validation_report.errors) == 0
        
        # Test individual hook validation
        hook_files = [
            'session-initializer.yaml',
            'message-enhancer.yaml',
            'file-watcher.yaml',
            'hybrid-processor.yaml',
            'disabled-hook.yaml'
        ]
        
        for hook_file in hook_files:
            hook_path = self.test_dir / 'hooks' / hook_file
            result = self.validator.validate_configuration_file(hook_path)
            
            assert result.is_valid is True, f"Hook {hook_file} should be valid"
            assert len(result.errors) == 0
    
    def test_hook_loading_by_type(self):
        """Test loading hooks by type."""
        # Load context hooks
        context_hooks = ['session-initializer', 'message-enhancer', 'disabled-hook']
        
        for hook_name in context_hooks:
            hook = self.loader.load_hook(hook_name)
            
            assert hook.name == hook_name
            assert hook.type == 'context'
            assert hasattr(hook, 'context')
            assert 'sources' in hook.context
        
        # Load script hook
        script_hook = self.loader.load_hook('file-watcher')
        
        assert script_hook.name == 'file-watcher'
        assert script_hook.type == 'script'
        assert hasattr(script_hook, 'script')
        assert 'command' in script_hook.script
        
        # Load hybrid hook
        hybrid_hook = self.loader.load_hook('hybrid-processor')
        
        assert hybrid_hook.name == 'hybrid-processor'
        assert hybrid_hook.type == 'hybrid'
        assert hasattr(hybrid_hook, 'context')
        assert hasattr(hybrid_hook, 'script')
    
    def test_hook_loading_by_trigger(self):
        """Test loading hooks by trigger type."""
        # Group hooks by trigger
        expected_triggers = {
            'on_session_start': ['session-initializer', 'disabled-hook'],
            'per_user_message': ['message-enhancer', 'hybrid-processor'],
            'on_file_change': ['file-watcher']
        }
        
        for trigger, expected_hooks in expected_triggers.items():
            for hook_name in expected_hooks:
                hook = self.loader.load_hook(hook_name)
                
                assert hook.trigger == trigger, f"Hook {hook_name} should have trigger {trigger}"
    
    def test_hook_manager_integration(self):
        """Test integration with HookManager."""
        # Discover hooks through HookManager
        discovered_hooks = self.hook_manager.discover_hooks()
        
        assert 'yaml' in discovered_hooks
        assert len(discovered_hooks['yaml']) >= 5
        
        # Load hooks by trigger
        session_hooks = self.hook_manager.load_hooks_by_trigger('on_session_start')
        message_hooks = self.hook_manager.load_hooks_by_trigger('per_user_message')
        file_hooks = self.hook_manager.load_hooks_by_trigger('on_file_change')
        
        assert len(session_hooks) >= 2  # session-initializer, disabled-hook
        assert len(message_hooks) >= 2  # message-enhancer, hybrid-processor
        assert len(file_hooks) >= 1     # file-watcher
        
        # Verify enabled/disabled status is respected
        enabled_session_hooks = [h for h in session_hooks if h.enabled]
        disabled_session_hooks = [h for h in session_hooks if not h.enabled]
        
        assert len(enabled_session_hooks) >= 1   # session-initializer
        assert len(disabled_session_hooks) >= 1  # disabled-hook
    
    def test_hook_execution_workflow(self):
        """Test hook execution workflow (mock execution)."""
        # Load and prepare hooks for execution
        session_hook = self.loader.load_hook('session-initializer')
        message_hook = self.loader.load_hook('message-enhancer')
        
        # Verify hooks have required execution information
        assert session_hook.enabled is True
        assert session_hook.timeout == 30
        assert session_hook.type == 'context'
        
        assert message_hook.enabled is True
        assert message_hook.timeout == 15
        assert message_hook.type == 'context'
        
        # Test context hook execution preparation
        assert 'sources' in session_hook.context
        assert len(session_hook.context['sources']) > 0
        
        # Verify context files exist for execution
        for source in session_hook.context['sources']:
            context_path = self.test_dir / source
            assert context_path.exists(), f"Context file should exist: {source}"
    
    def test_hook_condition_evaluation(self):
        """Test hook condition evaluation."""
        # Load hook with conditions
        session_hook = self.loader.load_hook('session-initializer')
        
        assert hasattr(session_hook, 'conditions')
        assert len(session_hook.conditions) > 0
        
        condition = session_hook.conditions[0]
        assert 'profile' in condition
        assert 'platform' in condition
        
        # Verify condition structure
        assert isinstance(condition['profile'], list)
        assert isinstance(condition['platform'], list)
        assert 'developer' in condition['profile']
        assert 'solutions-architect' in condition['profile']
    
    def test_hook_error_handling_workflow(self):
        """Test error handling in hook loading workflow."""
        # Create hook with invalid configuration
        invalid_hook = {
            'name': 'invalid-hook',
            'description': 'Hook with invalid trigger',
            'type': 'context',
            'trigger': 'invalid_trigger_name',  # Invalid trigger
            'context': {
                'sources': ['contexts/nonexistent.md']  # Missing file
            }
        }
        
        invalid_file = self.test_dir / 'hooks' / 'invalid-hook.yaml'
        with open(invalid_file, 'w') as f:
            yaml.dump(invalid_hook, f)
        
        # Validation should catch errors
        result = self.validator.validate_configuration_file(invalid_file)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Should have schema validation error for invalid trigger
        schema_errors = [e for e in result.errors if e.error_type == "SchemaValidationError"]
        trigger_errors = [e for e in schema_errors if "trigger" in e.message.lower()]
        assert len(trigger_errors) > 0
        
        # Should have file reference error for missing context
        ref_errors = [e for e in result.errors if e.error_type == "MissingFileReference"]
        assert len(ref_errors) > 0
    
    def test_hook_caching_workflow(self):
        """Test hook caching across loading workflow."""
        # Load same hook multiple times
        hook1 = self.loader.load_hook('session-initializer')
        hook2 = self.loader.load_hook('session-initializer')
        
        # Verify caching is working
        cache_stats = self.loader.get_cache_stats()
        assert cache_stats['config_cache_size'] > 0
        
        # Hooks should be identical (cached)
        assert hook1.name == hook2.name
        assert hook1.description == hook2.description
        assert hook1.type == hook2.type
        
        # Clear cache and reload
        self.loader.clear_cache()
        hook3 = self.loader.load_hook('session-initializer')
        
        # Should still work after cache clear
        assert hook3.name == 'session-initializer'
    
    def test_comprehensive_hook_workflow(self):
        """Test comprehensive hook workflow from discovery to execution prep."""
        # Step 1: Discover all hooks
        discovered = self.loader.discover_configurations()
        hook_files = discovered['hooks']
        
        # Step 2: Validate all hooks
        validation_report = self.validator.validate_all_configurations()
        assert validation_report.is_valid is True
        
        # Step 3: Load all hooks and group by trigger
        hooks_by_trigger = {}
        
        for hook_file in hook_files:
            hook_name = Path(hook_file).stem
            hook = self.loader.load_hook(hook_name)
            
            if hook.trigger not in hooks_by_trigger:
                hooks_by_trigger[hook.trigger] = []
            hooks_by_trigger[hook.trigger].append(hook)
        
        # Step 4: Verify hook organization
        assert 'on_session_start' in hooks_by_trigger
        assert 'per_user_message' in hooks_by_trigger
        assert 'on_file_change' in hooks_by_trigger
        
        # Step 5: Prepare hooks for execution (verify all required data is present)
        for trigger, hooks in hooks_by_trigger.items():
            for hook in hooks:
                # All hooks should have basic required fields
                assert hook.name is not None
                assert hook.type in ['context', 'script', 'hybrid']
                assert hook.trigger == trigger
                assert isinstance(hook.enabled, bool)
                
                # Context hooks should have context configuration
                if hook.type in ['context', 'hybrid']:
                    assert hasattr(hook, 'context')
                    assert 'sources' in hook.context
                
                # Script hooks should have script configuration
                if hook.type in ['script', 'hybrid']:
                    assert hasattr(hook, 'script')
                    assert 'command' in hook.script
        
        print(f"✅ Successfully processed {len(hook_files)} hooks across {len(hooks_by_trigger)} triggers")


if __name__ == '__main__':
    pytest.main([__file__])