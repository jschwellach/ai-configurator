"""Configuration merger for backward compatibility between JSON and YAML formats."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .models import (
    ProfileConfig, EnhancedProfileConfig, HookConfig, HookReference,
    ConfigurationError, ValidationReport, HookTrigger, HookType,
    ProfileSettings, ContextConfig, ValidationLevel
)

logger = logging.getLogger(__name__)


class ConflictReport:
    """Represents a configuration conflict between JSON and YAML."""
    
    def __init__(
        self,
        field_path: str,
        json_value: Any,
        yaml_value: Any,
        resolution: str,
        severity: str = "info"
    ):
        self.field_path = field_path
        self.json_value = json_value
        self.yaml_value = yaml_value
        self.resolution = resolution
        self.severity = severity
    
    def __str__(self) -> str:
        return (
            f"Conflict at '{self.field_path}': "
            f"JSON={self.json_value}, YAML={self.yaml_value} "
            f"-> {self.resolution}"
        )


class ConfigurationMerger:
    """Handles merging of JSON and YAML configurations with precedence rules."""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.NORMAL):
        self.validation_level = validation_level
        self.conflicts: List[ConflictReport] = []
        self.errors: List[ConfigurationError] = []
        self.warnings: List[ConfigurationError] = []
    
    def merge_profile_configs(
        self,
        yaml_config: Optional[Dict[str, Any]] = None,
        json_config: Optional[Dict[str, Any]] = None,
        profile_name: str = "unknown"
    ) -> EnhancedProfileConfig:
        """
        Merge JSON and YAML profile configurations with YAML taking precedence.
        
        Args:
            yaml_config: YAML configuration dictionary
            json_config: JSON configuration dictionary  
            profile_name: Name of the profile being merged
            
        Returns:
            EnhancedProfileConfig: Merged configuration
        """
        self.conflicts.clear()
        merged_config = {}
        
        # Start with JSON config as base if it exists
        if json_config:
            merged_config = self._convert_json_to_yaml_format(json_config, profile_name)
        
        # Override with YAML config if it exists
        if yaml_config:
            merged_config = self._merge_dictionaries(
                merged_config, 
                yaml_config, 
                f"profile.{profile_name}"
            )
        
        # Ensure required fields are present
        merged_config.setdefault("name", profile_name)
        merged_config.setdefault("version", "1.0")
        merged_config.setdefault("contexts", [])
        merged_config.setdefault("hooks", {})
        merged_config.setdefault("mcp_servers", [])
        merged_config.setdefault("settings", {})
        merged_config.setdefault("metadata", {})
        
        try:
            return EnhancedProfileConfig(**merged_config)
        except Exception as e:
            error = ConfigurationError(
                file_path=f"profile.{profile_name}",
                error_type="ValidationError",
                message=f"Failed to create profile config: {str(e)}",
                severity="error"
            )
            self.errors.append(error)
            # Return a minimal valid config
            return EnhancedProfileConfig(name=profile_name)
    
    def _convert_json_to_yaml_format(
        self, 
        json_config: Dict[str, Any], 
        profile_name: str
    ) -> Dict[str, Any]:
        """Convert legacy JSON format to new YAML format structure."""
        yaml_format = {
            "name": profile_name,
            "version": "1.0",
            "contexts": [],
            "hooks": {},
            "mcp_servers": [],
            "settings": {},
            "metadata": {"migrated_from_json": True}
        }
        
        # Convert context paths
        if "paths" in json_config:
            yaml_format["contexts"] = json_config["paths"]
        elif "context" in json_config and "paths" in json_config["context"]:
            yaml_format["contexts"] = json_config["context"]["paths"]
        
        # Convert hooks
        if "hooks" in json_config:
            yaml_format["hooks"] = self._convert_json_hooks(json_config["hooks"])
        elif "context" in json_config and "hooks" in json_config["context"]:
            yaml_format["hooks"] = self._convert_json_hooks(json_config["context"]["hooks"])
        
        # Convert MCP servers
        if "mcp_servers" in json_config:
            yaml_format["mcp_servers"] = json_config["mcp_servers"]
        
        # Convert other fields
        if "description" in json_config:
            yaml_format["description"] = json_config["description"]
        
        return yaml_format
    
    def _convert_json_hooks(self, json_hooks: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Convert JSON hook format to YAML hook format."""
        yaml_hooks = {}
        
        for trigger, hook_list in json_hooks.items():
            if not isinstance(hook_list, list):
                continue
                
            converted_hooks = []
            for hook in hook_list:
                if isinstance(hook, dict):
                    converted_hook = {
                        "name": hook.get("name", "unknown"),
                        "enabled": hook.get("enabled", True)
                    }
                    
                    # Add timeout if specified
                    if "timeout" in hook:
                        converted_hook["timeout"] = hook["timeout"]
                    
                    # Add any additional config
                    config = {k: v for k, v in hook.items() 
                             if k not in ["name", "enabled", "timeout"]}
                    if config:
                        converted_hook["config"] = config
                    
                    converted_hooks.append(converted_hook)
                elif isinstance(hook, str):
                    # Simple string hook reference
                    converted_hooks.append({
                        "name": hook,
                        "enabled": True
                    })
            
            if converted_hooks:
                yaml_hooks[trigger] = converted_hooks
        
        return yaml_hooks
    
    def _merge_dictionaries(
        self, 
        base: Dict[str, Any], 
        override: Dict[str, Any], 
        path: str = ""
    ) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries with conflict detection.
        
        Args:
            base: Base dictionary (lower precedence)
            override: Override dictionary (higher precedence)
            path: Current path for conflict reporting
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            current_path = f"{path}.{key}" if path else key
            
            if key not in result:
                # No conflict, just add the value
                result[key] = value
            elif isinstance(result[key], dict) and isinstance(value, dict):
                # Both are dictionaries, merge recursively
                result[key] = self._merge_dictionaries(
                    result[key], value, current_path
                )
            elif result[key] != value:
                # Conflict detected
                conflict = ConflictReport(
                    field_path=current_path,
                    json_value=result[key],
                    yaml_value=value,
                    resolution="YAML value used",
                    severity="info"
                )
                self.conflicts.append(conflict)
                result[key] = value
            # If values are equal, no conflict
        
        return result
    
    def detect_conflicts(self, configs: List[Dict[str, Any]]) -> List[ConflictReport]:
        """
        Detect conflicts between multiple configuration dictionaries.
        
        Args:
            configs: List of configuration dictionaries to compare
            
        Returns:
            List[ConflictReport]: List of detected conflicts
        """
        if len(configs) < 2:
            return []
        
        conflicts = []
        base_config = configs[0]
        
        for i, config in enumerate(configs[1:], 1):
            config_conflicts = self._find_conflicts_between_configs(
                base_config, config, f"config_{i}"
            )
            conflicts.extend(config_conflicts)
        
        return conflicts
    
    def _find_conflicts_between_configs(
        self,
        config1: Dict[str, Any],
        config2: Dict[str, Any],
        config2_name: str,
        path: str = ""
    ) -> List[ConflictReport]:
        """Find conflicts between two configuration dictionaries."""
        conflicts = []
        
        # Check all keys in both configs
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key in config1 and key in config2:
                value1, value2 = config1[key], config2[key]
                
                if isinstance(value1, dict) and isinstance(value2, dict):
                    # Recursively check nested dictionaries
                    nested_conflicts = self._find_conflicts_between_configs(
                        value1, value2, config2_name, current_path
                    )
                    conflicts.extend(nested_conflicts)
                elif value1 != value2:
                    # Values differ
                    conflict = ConflictReport(
                        field_path=current_path,
                        json_value=value1,
                        yaml_value=value2,
                        resolution=f"{config2_name} value would override",
                        severity="warning"
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def apply_precedence_rules(
        self, 
        configs: List[Tuple[Dict[str, Any], str]]
    ) -> Dict[str, Any]:
        """
        Apply precedence rules to merge multiple configurations.
        
        Args:
            configs: List of (config_dict, source_type) tuples
                    source_type should be 'json' or 'yaml'
            
        Returns:
            Dict[str, Any]: Merged configuration with precedence applied
        """
        if not configs:
            return {}
        
        # Sort by precedence: JSON first (lower), then YAML (higher)
        sorted_configs = sorted(configs, key=lambda x: x[1] == 'yaml')
        
        result = {}
        for config, source_type in sorted_configs:
            result = self._merge_dictionaries(result, config, f"merge_{source_type}")
        
        return result
    
    def validate_merged_config(
        self, 
        config: EnhancedProfileConfig
    ) -> ValidationReport:
        """
        Validate a merged configuration and return a comprehensive report.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationReport: Validation results
        """
        errors = []
        warnings = []
        info = []
        
        # Check required fields
        if not config.name:
            errors.append(ConfigurationError(
                file_path="merged_config",
                error_type="MissingField",
                message="Profile name is required",
                severity="error"
            ))
        
        # Validate context paths
        for i, context_path in enumerate(config.contexts):
            if not isinstance(context_path, str):
                errors.append(ConfigurationError(
                    file_path="merged_config",
                    error_type="InvalidType",
                    message=f"Context path at index {i} must be a string",
                    severity="error"
                ))
        
        # Validate hooks
        for trigger, hook_list in config.hooks.items():
            if not isinstance(hook_list, list):
                errors.append(ConfigurationError(
                    file_path="merged_config",
                    error_type="InvalidType",
                    message=f"Hook list for trigger '{trigger}' must be a list",
                    severity="error"
                ))
                continue
            
            for i, hook in enumerate(hook_list):
                if not isinstance(hook, HookReference):
                    try:
                        # Try to convert to HookReference
                        if isinstance(hook, dict):
                            HookReference(**hook)
                    except Exception as e:
                        errors.append(ConfigurationError(
                            file_path="merged_config",
                            error_type="InvalidHook",
                            message=f"Invalid hook at {trigger}[{i}]: {str(e)}",
                            severity="error"
                        ))
        
        # Add conflict information as warnings
        for conflict in self.conflicts:
            warnings.append(ConfigurationError(
                file_path="merged_config",
                error_type="ConfigConflict",
                message=str(conflict),
                severity="warning"
            ))
        
        # Add any existing errors and warnings
        errors.extend(self.errors)
        warnings.extend(self.warnings)
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=["merged_config"],
            summary={
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "total_conflicts": len(self.conflicts)
            }
        )
    
    def validate_raw_config(
        self, 
        config_dict: Dict[str, Any]
    ) -> ValidationReport:
        """
        Validate a raw configuration dictionary before model creation.
        
        Args:
            config_dict: Raw configuration dictionary to validate
            
        Returns:
            ValidationReport: Validation results
        """
        errors = []
        warnings = []
        info = []
        
        # Check required fields
        if not config_dict.get("name"):
            errors.append(ConfigurationError(
                file_path="raw_config",
                error_type="MissingField",
                message="Profile name is required",
                severity="error"
            ))
        
        # Validate context paths
        contexts = config_dict.get("contexts", [])
        if not isinstance(contexts, list):
            errors.append(ConfigurationError(
                file_path="raw_config",
                error_type="InvalidType",
                message="Contexts must be a list",
                severity="error"
            ))
        else:
            for i, context_path in enumerate(contexts):
                if not isinstance(context_path, str):
                    errors.append(ConfigurationError(
                        file_path="raw_config",
                        error_type="InvalidType",
                        message=f"Context path at index {i} must be a string",
                        severity="error"
                    ))
        
        # Validate hooks
        hooks = config_dict.get("hooks", {})
        if not isinstance(hooks, dict):
            errors.append(ConfigurationError(
                file_path="raw_config",
                error_type="InvalidType",
                message="Hooks must be a dictionary",
                severity="error"
            ))
        else:
            for trigger, hook_list in hooks.items():
                if not isinstance(hook_list, list):
                    errors.append(ConfigurationError(
                        file_path="raw_config",
                        error_type="InvalidType",
                        message=f"Hook list for trigger '{trigger}' must be a list",
                        severity="error"
                    ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=["raw_config"],
            summary={
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "total_conflicts": 0
            }
        )
    
    def get_conflicts(self) -> List[ConflictReport]:
        """Get list of conflicts detected during merging."""
        return self.conflicts.copy()
    
    def clear_conflicts(self) -> None:
        """Clear the list of detected conflicts."""
        self.conflicts.clear()
        self.errors.clear()
        self.warnings.clear()
    
    def convert_json_to_yaml_config(
        self, 
        json_config: Dict[str, Any], 
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Convert a JSON configuration to YAML format for migration purposes.
        
        This is a public interface for the conversion utility functionality
        required by requirement 4.3.
        
        Args:
            json_config: JSON configuration dictionary to convert
            profile_name: Name of the profile being converted
            
        Returns:
            Dict[str, Any]: YAML-formatted configuration dictionary
        """
        return self._convert_json_to_yaml_format(json_config, profile_name)
    
    def create_migration_report(
        self,
        original_json: Dict[str, Any],
        converted_yaml: Dict[str, Any],
        profile_name: str
    ) -> Dict[str, Any]:
        """
        Create a detailed migration report for JSON to YAML conversion.
        
        Args:
            original_json: Original JSON configuration
            converted_yaml: Converted YAML configuration
            profile_name: Name of the profile being migrated
            
        Returns:
            Dict[str, Any]: Migration report with details and recommendations
        """
        report = {
            "profile_name": profile_name,
            "migration_timestamp": "",  # Would be set by caller
            "original_structure": self._analyze_config_structure(original_json),
            "converted_structure": self._analyze_config_structure(converted_yaml),
            "changes_made": [],
            "recommendations": [],
            "warnings": []
        }
        
        # Analyze changes made during conversion
        if "paths" in original_json and "contexts" in converted_yaml:
            report["changes_made"].append({
                "field": "paths -> contexts",
                "description": "Renamed 'paths' field to 'contexts' for YAML format",
                "original_value": original_json["paths"],
                "new_value": converted_yaml["contexts"]
            })
        
        # Check for hook conversions
        if "hooks" in original_json and "hooks" in converted_yaml:
            original_hooks = original_json["hooks"]
            converted_hooks = converted_yaml["hooks"]
            
            for trigger in original_hooks:
                if trigger in converted_hooks:
                    orig_count = len(original_hooks[trigger]) if isinstance(original_hooks[trigger], list) else 1
                    conv_count = len(converted_hooks[trigger]) if isinstance(converted_hooks[trigger], list) else 1
                    
                    if orig_count != conv_count:
                        report["warnings"].append(
                            f"Hook count changed for trigger '{trigger}': {orig_count} -> {conv_count}"
                        )
        
        # Add recommendations
        if not converted_yaml.get("description"):
            report["recommendations"].append(
                "Consider adding a 'description' field to document the profile's purpose"
            )
        
        if not converted_yaml.get("version") or converted_yaml["version"] == "1.0":
            report["recommendations"].append(
                "Consider updating the 'version' field to reflect the migration"
            )
        
        # Check for metadata
        if converted_yaml.get("metadata", {}).get("migrated_from_json"):
            report["changes_made"].append({
                "field": "metadata.migrated_from_json",
                "description": "Added migration metadata flag",
                "original_value": None,
                "new_value": True
            })
        
        return report
    
    def _analyze_config_structure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of a configuration for reporting purposes."""
        structure = {
            "total_fields": len(config),
            "field_types": {},
            "nested_objects": 0,
            "arrays": 0
        }
        
        for key, value in config.items():
            value_type = type(value).__name__
            structure["field_types"][key] = value_type
            
            if isinstance(value, dict):
                structure["nested_objects"] += 1
            elif isinstance(value, list):
                structure["arrays"] += 1
        
        return structure
    
    def validate_conversion(
        self,
        original_json: Dict[str, Any],
        converted_yaml: Dict[str, Any],
        profile_name: str
    ) -> ValidationReport:
        """
        Validate that a JSON to YAML conversion preserved essential data.
        
        Args:
            original_json: Original JSON configuration
            converted_yaml: Converted YAML configuration  
            profile_name: Name of the profile being validated
            
        Returns:
            ValidationReport: Validation results for the conversion
        """
        errors = []
        warnings = []
        info = []
        
        # Check that essential data was preserved
        if "paths" in original_json:
            if "contexts" not in converted_yaml:
                errors.append(ConfigurationError(
                    file_path=f"conversion.{profile_name}",
                    error_type="MissingField",
                    message="Original 'paths' field was not converted to 'contexts'",
                    severity="error"
                ))
            elif original_json["paths"] != converted_yaml["contexts"]:
                info.append(ConfigurationError(
                    file_path=f"conversion.{profile_name}",
                    error_type="FieldRenamed",
                    message="'paths' field renamed to 'contexts'",
                    severity="info"
                ))
        
        # Check hooks conversion
        if "hooks" in original_json and "hooks" in converted_yaml:
            for trigger in original_json["hooks"]:
                if trigger not in converted_yaml["hooks"]:
                    warnings.append(ConfigurationError(
                        file_path=f"conversion.{profile_name}",
                        error_type="MissingHook",
                        message=f"Hook trigger '{trigger}' was not preserved in conversion",
                        severity="warning"
                    ))
        
        # Validate the converted config can be loaded as EnhancedProfileConfig
        try:
            EnhancedProfileConfig(**converted_yaml)
            info.append(ConfigurationError(
                file_path=f"conversion.{profile_name}",
                error_type="ValidationSuccess",
                message="Converted configuration is valid",
                severity="info"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=f"conversion.{profile_name}",
                error_type="ValidationError",
                message=f"Converted configuration is invalid: {str(e)}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[f"conversion.{profile_name}"],
            summary={
                "total_errors": len(errors),
                "total_warnings": len(warnings),
                "conversion_successful": 1 if len(errors) == 0 else 0
            }
        )