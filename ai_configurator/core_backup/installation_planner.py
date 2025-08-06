"""
Installation planning and validation for configuration management.

This module provides installation planning, compatibility validation,
and dry-run functionality for configuration installations.
"""

import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..utils.logging import LoggerMixin
from .catalog_schema import ConfigItem, LibraryCatalog, ConfigMetadata, CompatibilityInfo
from .dependency_resolver import DependencyResolver, ResolutionResult, ConflictInfo, ConflictType


class InstallationAction(Enum):
    """Types of installation actions."""
    INSTALL = "install"
    UPDATE = "update"
    SKIP = "skip"
    REMOVE = "remove"


class ValidationLevel(Enum):
    """Validation levels for installation planning."""
    BASIC = "basic"
    STRICT = "strict"
    PERMISSIVE = "permissive"


@dataclass
class InstallationStep:
    """A single step in the installation plan."""
    config_id: str
    config_name: str
    action: InstallationAction
    source_path: Path
    target_path: Path
    file_size: int = 0
    dependencies: List[str] = None
    conflicts: List[ConflictInfo] = None
    is_optional: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class InstallationPlan:
    """Complete installation plan with all steps and metadata."""
    steps: List[InstallationStep]
    total_configs: int
    total_size: int
    estimated_time_seconds: int
    conflicts: List[ConflictInfo]
    platform_info: Dict[str, str]
    validation_level: ValidationLevel
    dry_run: bool = False
    
    @property
    def has_conflicts(self) -> bool:
        """Check if the plan has any conflicts."""
        return len(self.conflicts) > 0 or any(step.conflicts for step in self.steps)
    
    @property
    def required_steps(self) -> List[InstallationStep]:
        """Get only required installation steps."""
        return [step for step in self.steps if not step.is_optional]
    
    @property
    def optional_steps(self) -> List[InstallationStep]:
        """Get only optional installation steps."""
        return [step for step in self.steps if step.is_optional]
    
    @property
    def install_steps(self) -> List[InstallationStep]:
        """Get steps that involve installing new configurations."""
        return [step for step in self.steps if step.action == InstallationAction.INSTALL]
    
    @property
    def update_steps(self) -> List[InstallationStep]:
        """Get steps that involve updating existing configurations."""
        return [step for step in self.steps if step.action == InstallationAction.UPDATE]


@dataclass
class PlatformInfo:
    """Information about the target platform."""
    os_name: str
    os_version: str
    architecture: str
    python_version: str
    kiro_version: Optional[str] = None
    
    @classmethod
    def detect_current(cls) -> 'PlatformInfo':
        """Detect current platform information."""
        import sys
        return cls(
            os_name=platform.system().lower(),
            os_version=platform.release(),
            architecture=platform.machine(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "os_name": self.os_name,
            "os_version": self.os_version,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "kiro_version": self.kiro_version or "unknown"
        }


class InstallationPlanner(LoggerMixin):
    """
    Creates installation plans with validation and conflict resolution.
    """
    
    def __init__(
        self, 
        catalog: LibraryCatalog,
        library_path: Path,
        target_path: Path,
        platform_info: Optional[PlatformInfo] = None
    ):
        """
        Initialize the installation planner.
        
        Args:
            catalog: Library catalog
            library_path: Path to the library directory
            target_path: Target installation directory (e.g., ~/.kiro/)
            platform_info: Platform information for compatibility checking
        """
        self.catalog = catalog
        self.library_path = library_path
        self.target_path = target_path
        self.platform_info = platform_info or PlatformInfo.detect_current()
        self.dependency_resolver = DependencyResolver(catalog)
        
        # Build config map for fast lookup
        self._config_map = self._build_config_map()
    
    def _build_config_map(self) -> Dict[str, ConfigItem]:
        """Build a map of config_id to ConfigItem for fast lookup."""
        config_map = {}
        
        for category_name, category_data in self.catalog.categories.dict().items():
            if not isinstance(category_data, dict):
                continue
            for subcategory_name, configs in category_data.items():
                if not isinstance(configs, list):
                    continue
                for config_data in configs:
                    if isinstance(config_data, dict):
                        config = ConfigItem(**config_data)
                    else:
                        config = config_data
                    config_map[config.id] = config
        
        return config_map
    
    def create_installation_plan(
        self,
        config_ids: List[str],
        validation_level: ValidationLevel = ValidationLevel.BASIC,
        dry_run: bool = False,
        force_reinstall: bool = False
    ) -> InstallationPlan:
        """
        Create a complete installation plan for the given configurations.
        
        Args:
            config_ids: List of configuration IDs to install
            validation_level: Level of validation to perform
            dry_run: If True, create plan without actually installing
            force_reinstall: If True, reinstall even if already installed
            
        Returns:
            InstallationPlan with all steps and validation results
        """
        self.logger.info(f"Creating installation plan for {len(config_ids)} configurations")
        
        # Resolve dependencies
        resolution_result = self.dependency_resolver.resolve_dependencies(
            config_ids,
            platform=self.platform_info.os_name,
            kiro_version=self.platform_info.kiro_version
        )
        
        # Get installation order
        all_configs = resolution_result.resolved_configs + resolution_result.optional_configs
        ordered_configs = self.dependency_resolver.suggest_resolution_order(all_configs)
        
        # Create installation steps
        steps = []
        total_size = 0
        
        for config_id in ordered_configs:
            config = self._config_map.get(config_id)
            if not config:
                continue
            
            # Determine action
            action = self._determine_action(config_id, force_reinstall)
            
            # Create step
            source_path = self.library_path / config.file_path
            target_path = self._get_target_path(config)
            file_size = self._get_file_size(source_path)
            
            step = InstallationStep(
                config_id=config_id,
                config_name=config.name,
                action=action,
                source_path=source_path,
                target_path=target_path,
                file_size=file_size,
                dependencies=config.dependencies,
                is_optional=config_id in resolution_result.optional_configs
            )
            
            # Add step-specific conflicts
            step_conflicts = self._validate_step(step, validation_level)
            step.conflicts = step_conflicts
            
            steps.append(step)
            total_size += file_size
        
        # Estimate installation time (rough estimate: 1MB per second + overhead)
        estimated_time = max(10, total_size // (1024 * 1024) + len(steps) * 2)
        
        plan = InstallationPlan(
            steps=steps,
            total_configs=len(all_configs),
            total_size=total_size,
            estimated_time_seconds=estimated_time,
            conflicts=resolution_result.conflicts,
            platform_info=self.platform_info.to_dict(),
            validation_level=validation_level,
            dry_run=dry_run
        )
        
        self.logger.info(
            f"Installation plan created: {len(steps)} steps, "
            f"{total_size // 1024}KB total, ~{estimated_time}s estimated"
        )
        
        return plan
    
    def _determine_action(self, config_id: str, force_reinstall: bool) -> InstallationAction:
        """Determine what action to take for a configuration."""
        config = self._config_map.get(config_id)
        if not config:
            return InstallationAction.SKIP
        
        target_path = self._get_target_path(config)
        
        if not target_path.exists():
            return InstallationAction.INSTALL
        elif force_reinstall:
            return InstallationAction.INSTALL
        else:
            # Check if update is needed (simplified version check)
            installed_version = self._get_installed_version(config_id)
            if installed_version and installed_version != config.version:
                return InstallationAction.UPDATE
            else:
                return InstallationAction.SKIP
    
    def _get_target_path(self, config: ConfigItem) -> Path:
        """Get the target installation path for a configuration."""
        # Map library paths to target paths
        relative_path = Path(config.file_path)
        
        # Remove 'library/' prefix if present and map to appropriate target directory
        if relative_path.parts[0] == "library":
            relative_path = Path(*relative_path.parts[1:])
        
        # Map to appropriate target directories
        if relative_path.parts[0] == "contexts":
            return self.target_path / "contexts" / Path(*relative_path.parts[1:])
        elif relative_path.parts[0] == "profiles":
            return self.target_path / "profiles" / Path(*relative_path.parts[1:])
        elif relative_path.parts[0] == "hooks":
            return self.target_path / "hooks" / Path(*relative_path.parts[1:])
        elif relative_path.parts[0] == "mcp-servers":
            return self.target_path / "settings" / Path(*relative_path.parts[1:])
        else:
            return self.target_path / relative_path
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get the size of a file in bytes."""
        try:
            return file_path.stat().st_size if file_path.exists() else 0
        except OSError:
            return 0
    
    def _get_installed_version(self, config_id: str) -> Optional[str]:
        """Get the version of an installed configuration."""
        # This would typically read from an installation manifest
        # For now, return None (not implemented)
        return None
    
    def _validate_step(self, step: InstallationStep, validation_level: ValidationLevel) -> List[ConflictInfo]:
        """Validate a single installation step."""
        conflicts = []
        config = self._config_map.get(step.config_id)
        
        if not config:
            conflicts.append(ConflictInfo(
                conflict_type=ConflictType.MISSING_DEPENDENCY,
                config_id=step.config_id,
                message=f"Configuration not found: {step.config_id}"
            ))
            return conflicts
        
        # Check source file exists
        if not step.source_path.exists():
            conflicts.append(ConflictInfo(
                conflict_type=ConflictType.MISSING_DEPENDENCY,
                config_id=step.config_id,
                message=f"Source file not found: {step.source_path}"
            ))
        
        # Check target directory permissions
        target_dir = step.target_path.parent
        if not self._check_write_permissions(target_dir):
            conflicts.append(ConflictInfo(
                conflict_type=ConflictType.INCOMPATIBLE_PLATFORM,
                config_id=step.config_id,
                message=f"No write permission to target directory: {target_dir}",
                suggested_resolution="Run with appropriate permissions or change target directory"
            ))
        
        # Platform compatibility (if strict validation)
        if validation_level == ValidationLevel.STRICT and config.compatibility:
            if self.platform_info.os_name not in config.compatibility.platforms:
                conflicts.append(ConflictInfo(
                    conflict_type=ConflictType.INCOMPATIBLE_PLATFORM,
                    config_id=step.config_id,
                    message=f"Configuration not compatible with {self.platform_info.os_name}",
                    suggested_resolution=f"Use a configuration compatible with: {', '.join(config.compatibility.platforms)}"
                ))
        
        # Disk space check (basic validation)
        if validation_level in [ValidationLevel.BASIC, ValidationLevel.STRICT]:
            available_space = self._get_available_disk_space(step.target_path.parent)
            if available_space is not None and step.file_size > available_space:
                conflicts.append(ConflictInfo(
                    conflict_type=ConflictType.INCOMPATIBLE_PLATFORM,
                    config_id=step.config_id,
                    message=f"Insufficient disk space: need {step.file_size} bytes, have {available_space} bytes",
                    suggested_resolution="Free up disk space or choose a different target directory"
                ))
        
        return conflicts
    
    def _check_write_permissions(self, directory: Path) -> bool:
        """Check if we have write permissions to a directory."""
        try:
            # Create directory if it doesn't exist
            directory.mkdir(parents=True, exist_ok=True)
            
            # Try to create a temporary file
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False
    
    def _get_available_disk_space(self, path: Path) -> Optional[int]:
        """Get available disk space in bytes."""
        try:
            stat = os.statvfs(str(path))
            return stat.f_bavail * stat.f_frsize
        except (OSError, AttributeError):
            # statvfs not available on Windows
            try:
                import shutil
                return shutil.disk_usage(str(path)).free
            except (OSError, AttributeError):
                return None
    
    def validate_plan(self, plan: InstallationPlan) -> Tuple[bool, List[str]]:
        """
        Validate an installation plan and return validation results.
        
        Args:
            plan: Installation plan to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Check for blocking conflicts
        blocking_conflicts = [
            c for c in plan.conflicts 
            if c.conflict_type in [ConflictType.MISSING_DEPENDENCY, ConflictType.CIRCULAR_DEPENDENCY]
        ]
        
        if blocking_conflicts:
            for conflict in blocking_conflicts:
                errors.append(f"{conflict.conflict_type.value}: {conflict.message}")
        
        # Check step-level conflicts
        for step in plan.steps:
            step_blocking_conflicts = [
                c for c in step.conflicts
                if c.conflict_type in [ConflictType.MISSING_DEPENDENCY]
            ]
            for conflict in step_blocking_conflicts:
                errors.append(f"Step {step.config_id}: {conflict.message}")
        
        # Check total disk space
        total_required = sum(step.file_size for step in plan.steps)
        if plan.platform_info.get("available_space"):
            available = int(plan.platform_info["available_space"])
            if total_required > available:
                errors.append(f"Insufficient disk space: need {total_required} bytes, have {available} bytes")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def preview_plan(self, plan: InstallationPlan) -> str:
        """
        Generate a human-readable preview of the installation plan.
        
        Args:
            plan: Installation plan to preview
            
        Returns:
            Formatted string describing the plan
        """
        lines = []
        lines.append("=" * 60)
        lines.append("INSTALLATION PLAN PREVIEW")
        lines.append("=" * 60)
        lines.append("")
        
        # Summary
        lines.append(f"Total configurations: {plan.total_configs}")
        lines.append(f"Required steps: {len(plan.required_steps)}")
        lines.append(f"Optional steps: {len(plan.optional_steps)}")
        lines.append(f"Total size: {plan.total_size // 1024:.1f} KB")
        lines.append(f"Estimated time: {plan.estimated_time_seconds} seconds")
        lines.append(f"Validation level: {plan.validation_level.value}")
        lines.append(f"Dry run: {'Yes' if plan.dry_run else 'No'}")
        lines.append("")
        
        # Platform info
        lines.append("Platform Information:")
        for key, value in plan.platform_info.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
        
        # Conflicts
        if plan.has_conflicts:
            lines.append("CONFLICTS DETECTED:")
            for conflict in plan.conflicts:
                lines.append(f"  ⚠️  {conflict.conflict_type.value}: {conflict.message}")
                if conflict.suggested_resolution:
                    lines.append(f"      Resolution: {conflict.suggested_resolution}")
            lines.append("")
        
        # Installation steps
        lines.append("Installation Steps:")
        for i, step in enumerate(plan.steps, 1):
            status_icon = "📦" if step.action == InstallationAction.INSTALL else "🔄" if step.action == InstallationAction.UPDATE else "⏭️"
            optional_marker = " (optional)" if step.is_optional else ""
            lines.append(f"  {i:2d}. {status_icon} {step.config_name}{optional_marker}")
            lines.append(f"      ID: {step.config_id}")
            lines.append(f"      Action: {step.action.value}")
            lines.append(f"      Size: {step.file_size // 1024:.1f} KB")
            lines.append(f"      Target: {step.target_path}")
            
            if step.dependencies:
                lines.append(f"      Dependencies: {', '.join(step.dependencies)}")
            
            if step.conflicts:
                for conflict in step.conflicts:
                    lines.append(f"      ⚠️  {conflict.message}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_rollback_plan(self, installed_configs: List[str]) -> InstallationPlan:
        """
        Create a rollback plan to remove installed configurations.
        
        Args:
            installed_configs: List of configuration IDs to remove
            
        Returns:
            InstallationPlan for removal
        """
        steps = []
        total_size = 0
        
        # Reverse dependency order for removal
        ordered_configs = self.dependency_resolver.suggest_resolution_order(installed_configs)
        ordered_configs.reverse()
        
        for config_id in ordered_configs:
            config = self._config_map.get(config_id)
            if not config:
                continue
            
            target_path = self._get_target_path(config)
            file_size = self._get_file_size(target_path)
            
            step = InstallationStep(
                config_id=config_id,
                config_name=config.name,
                action=InstallationAction.REMOVE,
                source_path=target_path,  # Source is the installed file
                target_path=target_path,
                file_size=file_size
            )
            
            steps.append(step)
            total_size += file_size
        
        return InstallationPlan(
            steps=steps,
            total_configs=len(installed_configs),
            total_size=total_size,
            estimated_time_seconds=max(5, len(steps) * 1),
            conflicts=[],
            platform_info=self.platform_info.to_dict(),
            validation_level=ValidationLevel.BASIC,
            dry_run=False
        )