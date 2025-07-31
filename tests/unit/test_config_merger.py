"""Tests for the ConfigurationMerger class."""

import pytest
from pathlib import Path
from typing import Dict, Any

from src.ai_configurator.core.config_merger import ConfigurationMerger, ConflictReport
from src.ai_configurator.core.models import (
    EnhancedProfileConfig, ValidationLevel, HookTrigger
)


class TestConfigurationMerger:
    """Test cases for ConfigurationMerger."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.merger = ConfigurationMerger()
    
    def test_merge_yaml_only_config(self):
        """Test merging with only YAML configuration."""
        yaml_config = {
            "name": "test-profile",
            "description": "Test profile",
            "version": "1.0",
            "contexts": ["context1.md", "context2.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "hook1", "enabled": True}
                ]
            },
            "mcp_servers": ["server1", "server2"]
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            profile_name="test-profile"
        )
        
        assert result.name == "test-profile"
        assert result.description == "Test profile"
        assert result.contexts == ["context1.md", "context2.md"]
        assert len(result.hooks) == 1
        assert HookTrigger.ON_SESSION_START in result.hooks
        assert result.mcp_servers == ["server1", "server2"]
    
    def test_merge_json_only_config(self):
        """Test merging with only JSON configuration."""
        json_config = {
            "paths": ["context1.md", "context2.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "hook1", "enabled": True, "description": "Test hook"}
                ]
            }
        }
        
        result = self.merger.merge_profile_configs(
            json_config=json_config,
            profile_name="test-profile"
        )
        
        assert result.name == "test-profile"
        assert result.contexts == ["context1.md", "context2.md"]
        assert len(result.hooks) == 1
        assert result.metadata.get("migrated_from_json") is True
    
    def test_merge_yaml_overrides_json(self):
        """Test that YAML configuration overrides JSON configuration."""
        json_config = {
            "paths": ["json_context.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "json_hook", "enabled": True}
                ]
            }
        }
        
        yaml_config = {
            "name": "test-profile",
            "description": "YAML description",
            "contexts": ["yaml_context.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "yaml_hook", "enabled": True}
                ]
            }
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="test-profile"
        )
        
        assert result.name == "test-profile"
        assert result.description == "YAML description"
        assert result.contexts == ["yaml_context.md"]  # YAML overrides JSON
        
        # Check that conflicts were detected
        conflicts = self.merger.get_conflicts()
        assert len(conflicts) > 0
        
        # Find the contexts conflict
        context_conflict = next(
            (c for c in conflicts if "contexts" in c.field_path), None
        )
        assert context_conflict is not None
        assert context_conflict.resolution == "YAML value used"
    
    def test_convert_json_hooks_format(self):
        """Test conversion of JSON hook format to YAML format."""
        json_config = {
            "hooks": {
                "on_session_start": [
                    {
                        "name": "complex_hook",
                        "enabled": True,
                        "timeout": 60,
                        "description": "A complex hook",
                        "custom_param": "value"
                    },
                    "simple_hook"  # String format
                ]
            }
        }
        
        result = self.merger.merge_profile_configs(
            json_config=json_config,
            profile_name="test-profile"
        )
        
        hooks = result.hooks.get(HookTrigger.ON_SESSION_START, [])
        assert len(hooks) == 2
        
        # Check complex hook conversion
        complex_hook = hooks[0]
        assert complex_hook.name == "complex_hook"
        assert complex_hook.enabled is True
        assert complex_hook.timeout == 60
        assert complex_hook.config.get("description") == "A complex hook"
        assert complex_hook.config.get("custom_param") == "value"
        
        # Check simple hook conversion
        simple_hook = hooks[1]
        assert simple_hook.name == "simple_hook"
        assert simple_hook.enabled is True
    
    def test_detect_conflicts_between_configs(self):
        """Test conflict detection between multiple configurations."""
        config1 = {
            "name": "profile1",
            "contexts": ["context1.md"],
            "settings": {"auto_backup": True}
        }
        
        config2 = {
            "name": "profile2",  # Conflict
            "contexts": ["context2.md"],  # Conflict
            "settings": {"auto_backup": True}  # No conflict
        }
        
        conflicts = self.merger.detect_conflicts([config1, config2])
        
        assert len(conflicts) >= 2  # At least name and contexts conflicts
        
        # Check for name conflict
        name_conflict = next(
            (c for c in conflicts if c.field_path == "name"), None
        )
        assert name_conflict is not None
        assert name_conflict.json_value == "profile1"
        assert name_conflict.yaml_value == "profile2"
    
    def test_apply_precedence_rules(self):
        """Test application of precedence rules."""
        json_config = {
            "name": "json_profile",
            "contexts": ["json_context.md"],
            "shared_field": "json_value"
        }
        
        yaml_config = {
            "name": "yaml_profile",
            "description": "YAML only field",
            "shared_field": "yaml_value"
        }
        
        configs = [
            (json_config, "json"),
            (yaml_config, "yaml")
        ]
        
        result = self.merger.apply_precedence_rules(configs)
        
        # YAML should override JSON
        assert result["name"] == "yaml_profile"
        assert result["shared_field"] == "yaml_value"
        
        # JSON-only fields should be preserved
        assert result["contexts"] == ["json_context.md"]
        
        # YAML-only fields should be included
        assert result["description"] == "YAML only field"
    
    def test_validation_of_merged_config(self):
        """Test validation of merged configuration."""
        yaml_config = {
            "name": "valid-profile",
            "contexts": ["context1.md", "context2.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "valid_hook", "enabled": True}
                ]
            }
        }
        
        merged_config = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            profile_name="valid-profile"
        )
        
        validation_report = self.merger.validate_merged_config(merged_config)
        
        assert validation_report.is_valid
        assert len(validation_report.errors) == 0
    
    def test_validation_with_invalid_config(self):
        """Test validation with invalid configuration."""
        invalid_config = {
            "name": "",  # Invalid: empty name
            "contexts": [123, "valid_context.md"],  # Invalid: non-string context
            "hooks": {
                "on_session_start": "not_a_list"  # Invalid: should be list
            }
        }
        
        validation_report = self.merger.validate_raw_config(invalid_config)
        
        assert not validation_report.is_valid
        assert len(validation_report.errors) > 0
        
        # Check for specific error types
        error_types = [error.error_type for error in validation_report.errors]
        assert "InvalidType" in error_types
        assert "MissingField" in error_types
    
    def test_merge_with_nested_dictionaries(self):
        """Test merging configurations with nested dictionary structures."""
        json_config = {
            "settings": {
                "auto_backup": True,
                "validation_level": "normal",
                "cache": {
                    "enabled": True,
                    "ttl": 300
                }
            }
        }
        
        yaml_config = {
            "name": "test-profile",
            "settings": {
                "validation_level": "strict",  # Override
                "hot_reload": True,  # New field
                "cache": {
                    "ttl": 600  # Override nested field
                    # enabled should be preserved from JSON
                }
            }
        }
        
        result = self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="test-profile"
        )
        
        # Check that nested merging worked correctly
        assert result.settings.auto_backup is True  # From JSON
        assert result.settings.validation_level == ValidationLevel.STRICT  # YAML override
        assert result.settings.hot_reload is True  # YAML only
        assert result.settings.cache_enabled is True  # From JSON nested
    
    def test_clear_conflicts(self):
        """Test clearing of conflicts and errors."""
        yaml_config = {"name": "test", "contexts": ["yaml.md"]}
        json_config = {"paths": ["json.md"]}
        
        # This should generate conflicts
        self.merger.merge_profile_configs(
            yaml_config=yaml_config,
            json_config=json_config,
            profile_name="test"
        )
        
        assert len(self.merger.get_conflicts()) > 0
        
        self.merger.clear_conflicts()
        
        assert len(self.merger.get_conflicts()) == 0
    
    def test_conflict_report_string_representation(self):
        """Test string representation of ConflictReport."""
        conflict = ConflictReport(
            field_path="test.field",
            json_value="json_val",
            yaml_value="yaml_val",
            resolution="YAML used",
            severity="info"
        )
        
        conflict_str = str(conflict)
        assert "test.field" in conflict_str
        assert "json_val" in conflict_str
        assert "yaml_val" in conflict_str
        assert "YAML used" in conflict_str
    
    def test_convert_json_to_yaml_config(self):
        """Test the public conversion utility interface."""
        json_config = {
            "paths": ["context1.md", "context2.md"],
            "hooks": {
                "on_session_start": [
                    {"name": "hook1", "enabled": True, "timeout": 45}
                ]
            }
        }
        
        result = self.merger.convert_json_to_yaml_config(json_config, "test-profile")
        
        assert result["name"] == "test-profile"
        assert result["contexts"] == ["context1.md", "context2.md"]
        assert result["metadata"]["migrated_from_json"] is True
        assert "hooks" in result
        assert "on_session_start" in result["hooks"]
    
    def test_create_migration_report(self):
        """Test migration report generation."""
        original_json = {
            "paths": ["old_context.md"],
            "hooks": {
                "on_session_start": ["simple_hook"]
            }
        }
        
        converted_yaml = self.merger.convert_json_to_yaml_config(original_json, "test-profile")
        
        report = self.merger.create_migration_report(
            original_json, converted_yaml, "test-profile"
        )
        
        assert report["profile_name"] == "test-profile"
        assert "original_structure" in report
        assert "converted_structure" in report
        assert len(report["changes_made"]) > 0
        
        # Check for paths -> contexts change
        paths_change = next(
            (change for change in report["changes_made"] 
             if "paths -> contexts" in change["field"]), None
        )
        assert paths_change is not None
        assert paths_change["original_value"] == ["old_context.md"]
        assert paths_change["new_value"] == ["old_context.md"]
    
    def test_validate_conversion(self):
        """Test conversion validation."""
        original_json = {
            "paths": ["context.md"],
            "hooks": {
                "on_session_start": [{"name": "test_hook", "enabled": True}]
            }
        }
        
        converted_yaml = self.merger.convert_json_to_yaml_config(original_json, "test-profile")
        
        validation_report = self.merger.validate_conversion(
            original_json, converted_yaml, "test-profile"
        )
        
        assert validation_report.is_valid
        assert validation_report.summary["conversion_successful"] == 1
        
        # Should have info about successful validation
        validation_success = next(
            (info for info in validation_report.info 
             if info.error_type == "ValidationSuccess"), None
        )
        assert validation_success is not None
    
    def test_validate_conversion_with_missing_data(self):
        """Test conversion validation when data is missing."""
        original_json = {
            "paths": ["context.md"],
            "hooks": {"on_session_start": ["hook1"]}
        }
        
        # Simulate a bad conversion that loses data
        bad_converted_yaml = {
            "name": "test-profile",
            "version": "1.0"
            # Missing contexts and hooks
        }
        
        validation_report = self.merger.validate_conversion(
            original_json, bad_converted_yaml, "test-profile"
        )
        
        assert not validation_report.is_valid
        assert len(validation_report.errors) > 0
        
        # Should have error about missing contexts
        missing_contexts_error = next(
            (error for error in validation_report.errors 
             if "contexts" in error.message), None
        )
        assert missing_contexts_error is not None


if __name__ == "__main__":
    pytest.main([__file__])