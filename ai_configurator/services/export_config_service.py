"""
Export configuration service for managing export target preferences.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from ..models.export_targets import AIToolType, ExportTarget, export_target_registry
from .config_service import ConfigService


class ExportConfigService:
    """Service for managing export target configuration."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
        self._config_key = "export_targets"
        self._default_target_key = "default_export_target"
    
    def get_default_export_target(self) -> AIToolType:
        """Get the default export target."""
        config = self.config_service.get_config()
        default_str = config.get(self._default_target_key, AIToolType.KIRO_CLI.value)
        
        try:
            return AIToolType(default_str)
        except ValueError:
            # Fallback to kiro-cli if invalid value
            return AIToolType.KIRO_CLI
    
    def set_default_export_target(self, target_type: AIToolType) -> bool:
        """Set the default export target."""
        try:
            config = self.config_service.get_config()
            config[self._default_target_key] = target_type.value
            return self.config_service.save_config(config)
        except Exception:
            return False
    
    def get_export_target_config(self, target_type: AIToolType) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific export target."""
        config = self.config_service.get_config()
        targets_config = config.get(self._config_key, {})
        return targets_config.get(target_type.value)
    
    def set_export_target_config(self, target_type: AIToolType, target_config: Dict[str, Any]) -> bool:
        """Set configuration for a specific export target."""
        try:
            config = self.config_service.get_config()
            if self._config_key not in config:
                config[self._config_key] = {}
            
            config[self._config_key][target_type.value] = target_config
            return self.config_service.save_config(config)
        except Exception:
            return False
    
    def migrate_from_qcli(self) -> bool:
        """Migrate configuration from qcli to kiro-cli."""
        try:
            current_default = self.get_default_export_target()
            
            # If currently using qcli, migrate to kiro-cli
            if current_default == AIToolType.QCLI:
                self.set_default_export_target(AIToolType.KIRO_CLI)
                
                # Copy qcli config to kiro-cli if exists
                qcli_config = self.get_export_target_config(AIToolType.QCLI)
                if qcli_config:
                    # Adapt qcli config for kiro-cli
                    kiro_config = qcli_config.copy()
                    # Update directory path from .q to .kiro
                    if "export_directory" in kiro_config:
                        old_path = Path(kiro_config["export_directory"])
                        if ".q" in str(old_path):
                            new_path = str(old_path).replace("/.q/", "/.kiro/")
                            kiro_config["export_directory"] = new_path
                    
                    self.set_export_target_config(AIToolType.KIRO_CLI, kiro_config)
                
                return True
            
            return True  # No migration needed
        except Exception:
            return False
    
    def is_migration_needed(self) -> bool:
        """Check if migration from qcli is needed."""
        current_default = self.get_default_export_target()
        return current_default == AIToolType.QCLI
    
    def validate_export_target(self, target_type: AIToolType) -> tuple[bool, Optional[str]]:
        """Validate an export target configuration."""
        target = export_target_registry.get_target(target_type)
        if not target:
            return False, f"Unknown export target: {target_type.value}"
        
        if not target.enabled:
            return False, f"Export target {target.name} is not enabled"
        
        if target.is_deprecated:
            return False, f"Export target {target.name} is deprecated"
        
        # Check if export directory is accessible
        try:
            target.export_directory.mkdir(parents=True, exist_ok=True)
            if not target.export_directory.is_dir():
                return False, f"Export directory is not accessible: {target.export_directory}"
        except Exception as e:
            return False, f"Cannot access export directory: {e}"
        
        return True, None
    
    def get_available_targets(self) -> Dict[AIToolType, ExportTarget]:
        """Get all available (enabled, non-deprecated) export targets."""
        all_targets = export_target_registry.get_enabled_targets()
        return {k: v for k, v in all_targets.items() if not v.is_deprecated}
