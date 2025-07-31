"""Integration tests for ConfigurationMerger with real configuration files."""

import json
import tempfile
from pathlib import Path
import pytest

from src.ai_configurator.core.config_merger import ConfigurationMerger
from src.ai_configurator.core.models import EnhancedProfileConfig


class TestConfigurationMergerIntegration:
    """Integration tests for ConfigurationMerger."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.merger = ConfigurationMerger()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_merge_real_json_config(self):
        """Test merging with a real JSON configuration structure."""
        # Create a JSON config similar to the existing ones
        json_config = {
            "paths": [
                ".amazonq/rules/**/*.md",
                "README.md",
                "contexts/development-guidelines.md"
            ]
        }
        
        # Create a YAML config that extends the JSON
        yaml_config = {
            "name": "developer",
            "description": "Enhanced developer profile",
            "version": "2.0",
            "contexts": [
                "contexts/aws-best-practices.md",
                "contexts/troubleshooting.md"
            ],
            "hooks": {
                "on_session_start": [
                    {"name": "setup-dev-env", "enabled": True, "timeout": 45}
                ],
                "per_user_message": [
                    {"name": "context-enhancer", "enabled": True}
                ]
            },
            "mcp_servers": ["development", "core"],
            "settings": {
                "auto_backup": True,
                "validation_level": "strict",
                "hot_reload": True
            }
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="developer"
        )
        
        # Verify the merge results
        assert result.name == "developer"
        assert result.description == "Enhanced developer profile"
        assert result.version == "2.0"
        
        # YAML contexts should override JSON paths
        assert result.contexts == [
            "contexts/aws-best-practices.md",
            "contexts/troubleshooting.md"
        ]
        
        # Hooks should be properly converted
        assert len(result.hooks) == 2
        assert "on_session_start" in [trigger.value for trigger in result.hooks.keys()]
        
        # MCP servers should be included
        assert result.mcp_servers == ["development", "core"]
        
        # Settings should be properly set
        assert result.settings.auto_backup is True
        assert result.settings.hot_reload is True
        
        # Check that conflicts were detected
        conflicts = self.merger.get_conflicts()
        assert len(conflicts) > 0
        
        # Should have a conflict for contexts vs paths
        context_conflict = next(
            (c for c in conflicts if "contexts" in c.field_path), None
        )
        assert context_conflict is not None
    
    def test_merge_engagement_manager_style_config(self):
        """Test merging with engagement manager style configuration."""
        # Based on the real engagement-manager hooks.json
        json_config = {
            "hooks": {
                "on_session_start": [
                    {
                        "name": "engagement_manager_context.py",
                        "description": "Dynamic context delivery for engagement managers",
                        "enabled": True
                    }
                ],
                "per_user_message": []
            }
        }
        
        # YAML config that adds to the existing hooks
        yaml_config = {
            "name": "engagement-manager",
            "description": "Engagement Manager Profile with Enhanced Context",
            "contexts": [
                "contexts/engagement-management.md",
                "contexts/client-communication.md",
                "contexts/project-delivery.md"
            ],
            "hooks": {
                "on_session_start": [
                    {"name": "project-setup", "enabled": True, "timeout": 60}
                ],
                "per_user_message": [
                    {"name": "client-context", "enabled": True}
                ]
            },
            "mcp_servers": ["engagement", "core"]
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="engagement-manager"
        )
        
        # Verify the merge
        assert result.name == "engagement-manager"
        assert len(result.contexts) == 3
        
        # Check that hooks were properly merged (YAML overrides JSON)
        from src.ai_configurator.core.models import HookTrigger
        on_session_hooks = result.hooks.get(HookTrigger.ON_SESSION_START, [])
        assert len(on_session_hooks) == 1
        assert on_session_hooks[0].name == "project-setup"  # YAML override
        
        per_message_hooks = result.hooks.get(HookTrigger.PER_USER_MESSAGE, [])
        assert len(per_message_hooks) == 1
        assert per_message_hooks[0].name == "client-context"
    
    def test_json_only_migration_scenario(self):
        """Test scenario where only JSON config exists (migration case)."""
        json_config = {
            "paths": [
                "contexts/development-guidelines.md",
                "contexts/aws-best-practices.md"
            ],
            "hooks": {
                "on_session_start": [
                    "setup_dev_environment",
                    {
                        "name": "load_project_context",
                        "enabled": True,
                        "timeout": 30,
                        "custom_setting": "value"
                    }
                ]
            }
        }
        
        result = self.merger.merge_profile_configs(
            json_config=json_config,
            profile_name="legacy-profile"
        )
        
        # Verify JSON-to-YAML conversion
        assert result.name == "legacy-profile"
        assert result.contexts == [
            "contexts/development-guidelines.md",
            "contexts/aws-best-practices.md"
        ]
        
        # Check migration metadata
        assert result.metadata.get("migrated_from_json") is True
        
        # Verify hook conversion
        from src.ai_configurator.core.models import HookTrigger
        hooks = result.hooks.get(HookTrigger.ON_SESSION_START, [])
        assert len(hooks) == 2
        
        # First hook (string format)
        assert hooks[0].name == "setup_dev_environment"
        assert hooks[0].enabled is True
        
        # Second hook (dict format with custom settings)
        assert hooks[1].name == "load_project_context"
        assert hooks[1].enabled is True
        assert hooks[1].timeout == 30
        assert hooks[1].config.get("custom_setting") == "value"
    
    def test_validation_report_generation(self):
        """Test comprehensive validation report generation."""
        yaml_config = {
            "name": "test-profile",
            "contexts": ["valid_context.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "valid_hook", "enabled": True}
                ]
            }
        }
        
        json_config = {
            "paths": ["json_context.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "json_hook", "enabled": True}
                ]
            }
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="test-profile"
        )
        
        validation_report = self.merger.validate_merged_config(result)
        
        # Should be valid overall
        assert validation_report.is_valid
        
        # Should have warnings about conflicts
        assert len(validation_report.warnings) > 0
        
        # Check summary
        assert validation_report.summary["total_conflicts"] > 0
        assert "merged_config" in validation_report.files_checked
    
    def test_conversion_utility_end_to_end(self):
        """Test the complete conversion utility workflow."""
        # Simulate a real JSON config from the existing system
        original_json_config = {
            "paths": [
                "contexts/development-guidelines.md",
                "contexts/aws-best-practices.md",
                "README.md"
            ],
            "hooks": {
                "on_session_start": [
                    {
                        "name": "setup_development_environment",
                        "enabled": True,
                        "timeout": 60,
                        "description": "Initialize development environment"
                    },
                    "load_project_context"
                ],
                "per_user_message": [
                    {
                        "name": "context_enhancer",
                        "enabled": True,
                        "priority": "high"
                    }
                ]
            }
        }
        
        profile_name = "developer-migrated"
        
        # Step 1: Convert JSON to YAML format
        converted_yaml = self.merger.convert_json_to_yaml_config(
            original_json_config, profile_name
        )
        
        # Verify conversion structure
        assert converted_yaml["name"] == profile_name
        assert converted_yaml["contexts"] == original_json_config["paths"]
        assert converted_yaml["metadata"]["migrated_from_json"] is True
        assert "hooks" in converted_yaml
        
        # Step 2: Create migration report
        migration_report = self.merger.create_migration_report(
            original_json_config, converted_yaml, profile_name
        )
        
        assert migration_report["profile_name"] == profile_name
        assert len(migration_report["changes_made"]) > 0
        assert len(migration_report["recommendations"]) > 0
        
        # Should recommend adding description
        desc_recommendation = next(
            (rec for rec in migration_report["recommendations"] 
             if "description" in rec), None
        )
        assert desc_recommendation is not None
        
        # Step 3: Validate conversion
        validation_report = self.merger.validate_conversion(
            original_json_config, converted_yaml, profile_name
        )
        
        assert validation_report.is_valid
        assert validation_report.summary["conversion_successful"] == 1
        
        # Step 4: Verify the converted config can be used to create a valid profile
        profile_config = EnhancedProfileConfig(**converted_yaml)
        assert profile_config.name == profile_name
        assert len(profile_config.contexts) == 3
        assert len(profile_config.hooks) == 2  # Two trigger types
        
        # Verify hooks were converted correctly
        from src.ai_configurator.core.models import HookTrigger
        on_session_hooks = profile_config.hooks.get(HookTrigger.ON_SESSION_START, [])
        assert len(on_session_hooks) == 2
        
        # Check complex hook conversion
        setup_hook = next(
            (hook for hook in on_session_hooks 
             if hook.name == "setup_development_environment"), None
        )
        assert setup_hook is not None
        assert setup_hook.timeout == 60
        assert setup_hook.config.get("description") == "Initialize development environment"
        
        # Check simple hook conversion
        context_hook = next(
            (hook for hook in on_session_hooks 
             if hook.name == "load_project_context"), None
        )
        assert context_hook is not None
        assert context_hook.enabled is True
        
        # Check per-message hooks
        per_message_hooks = profile_config.hooks.get(HookTrigger.PER_USER_MESSAGE, [])
        assert len(per_message_hooks) == 1
        
        enhancer_hook = per_message_hooks[0]
        assert enhancer_hook.name == "context_enhancer"
        assert enhancer_hook.enabled is True
        assert enhancer_hook.config.get("priority") == "high"


if __name__ == "__main__":
    pytest.main([__file__])