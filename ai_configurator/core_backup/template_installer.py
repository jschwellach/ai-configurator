"""
Template installation and management system.

This module provides functionality to install, manage, and validate template
configurations including profiles, contexts, and hooks from the examples directory
to user configuration directories.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import yaml
from pydantic import BaseModel, Field

from ..utils.logging import LoggerMixin
from .models import (
    ConfigurationError,
    ValidationReport,
    EnhancedProfileConfig,
    HookConfig,
    ContextFile,
    PathLike
)
from .directory_manager import DirectoryManager, ConfigurationType
from .template_validator import TemplateValidator


class TemplateType(str, Enum):
    """Types of templates that can be installed."""
    PROFILE = "profile"
    CONTEXT = "context"
    HOOK = "hook"
    WORKFLOW = "workflow"


class InstallationMode(str, Enum):
    """Installation modes for handling conflicts."""
    SKIP = "skip"          # Skip if target exists
    OVERWRITE = "overwrite"  # Overwrite existing files
    MERGE = "merge"        # Merge configurations where possible
    BACKUP = "backup"      # Backup existing and install new


@dataclass
class TemplateMetadata:
    """Metadata for a template."""
    name: str
    template_type: TemplateType
    source_path: Path
    target_path: Path
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


@dataclass
class InstallationResult:
    """Result of a template installation operation."""
    success: bool
    template_name: str
    template_type: TemplateType
    installed_files: List[Path]
    skipped_files: List[Path]
    errors: List[str]
    warnings: List[str]
    backup_path: Optional[Path] = None


class ConflictResolution(BaseModel):
    """Configuration for resolving installation conflicts."""
    mode: InstallationMode = InstallationMode.SKIP
    backup_existing: bool = True
    preserve_user_modifications: bool = True
    merge_strategy: str = "user_priority"  # user_priority, template_priority, interactive


class InstallationConfig(BaseModel):
    """Configuration for template installation."""
    target_directory: Path
    examples_directory: Path
    conflict_resolution: ConflictResolution = Field(default_factory=ConflictResolution)
    validate_before_install: bool = True
    validate_after_install: bool = True
    create_backup: bool = True
    dry_run: bool = False


class TemplateInstaller(LoggerMixin):
    """
    Manages installation of template configurations from examples to user directories.
    
    Handles:
    - Template discovery and validation
    - Conflict resolution during installation
    - Dependency management
    - Backup and rollback functionality
    """
    
    def __init__(self, config: InstallationConfig):
        """
        Initialize the template installer.
        
        Args:
            config: Installation configuration
        """
        self.config = config
        self.directory_manager = DirectoryManager(config.target_directory)
        self.validator = TemplateValidator()
        
        # Ensure target directories exist
        self.directory_manager.create_directory_structure()
        
        # Track installed templates
        self.installed_templates: Dict[str, TemplateMetadata] = {}
        self.installation_history: List[InstallationResult] = []
    
    def discover_templates(self, template_type: Optional[TemplateType] = None) -> Dict[str, TemplateMetadata]:
        """
        Discover available templates in the examples directory.
        
        Args:
            template_type: Optional filter by template type
            
        Returns:
            Dictionary mapping template names to their metadata
        """
        templates = {}
        
        try:
            examples_dir = self.config.examples_directory
            if not examples_dir.exists():
                self.logger.warning(f"Examples directory not found: {examples_dir}")
                return templates
            
            # Discover profiles
            if not template_type or template_type == TemplateType.PROFILE:
                profiles_dir = examples_dir / "profiles"
                if profiles_dir.exists():
                    templates.update(self._discover_profiles(profiles_dir))
            
            # Discover contexts
            if not template_type or template_type == TemplateType.CONTEXT:
                contexts_dir = examples_dir / "contexts"
                if contexts_dir.exists():
                    templates.update(self._discover_contexts(contexts_dir))
            
            # Discover hooks
            if not template_type or template_type == TemplateType.HOOK:
                hooks_dir = examples_dir / "hooks"
                if hooks_dir.exists():
                    templates.update(self._discover_hooks(hooks_dir))
            
            # Discover workflows
            if not template_type or template_type == TemplateType.WORKFLOW:
                workflows_dir = examples_dir / "workflows"
                if workflows_dir.exists():
                    templates.update(self._discover_workflows(workflows_dir))
            
            self.logger.info(f"Discovered {len(templates)} templates")
            
        except Exception as e:
            self.logger.error(f"Failed to discover templates: {e}")
        
        return templates
    
    def _discover_profiles(self, profiles_dir: Path) -> Dict[str, TemplateMetadata]:
        """Discover profile templates."""
        templates = {}
        
        for category_dir in profiles_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            for profile_file in category_dir.glob("*.json"):
                name = f"{category_dir.name}/{profile_file.stem}"
                target_path = self.config.target_directory / "profiles" / f"{profile_file.stem}.json"
                
                templates[name] = TemplateMetadata(
                    name=name,
                    template_type=TemplateType.PROFILE,
                    source_path=profile_file,
                    target_path=target_path,
                    description=f"Profile template from {category_dir.name} category"
                )
        
        return templates
    
    def _discover_contexts(self, contexts_dir: Path) -> Dict[str, TemplateMetadata]:
        """Discover context templates."""
        templates = {}
        
        for context_file in contexts_dir.rglob("*.md"):
            # Calculate relative path from contexts directory
            rel_path = context_file.relative_to(contexts_dir)
            name = str(rel_path.with_suffix(''))
            target_path = self.config.target_directory / "contexts" / rel_path
            
            templates[name] = TemplateMetadata(
                name=name,
                template_type=TemplateType.CONTEXT,
                source_path=context_file,
                target_path=target_path,
                description=f"Context template: {name}"
            )
        
        return templates
    
    def _discover_hooks(self, hooks_dir: Path) -> Dict[str, TemplateMetadata]:
        """Discover hook templates."""
        templates = {}
        
        for category_dir in hooks_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            for hook_file in category_dir.glob("*.yaml"):
                name = f"{category_dir.name}/{hook_file.stem}"
                target_path = self.config.target_directory / "hooks" / f"{hook_file.stem}.yaml"
                
                # Check for associated Python script
                script_file = hook_file.with_suffix('.py')
                
                templates[name] = TemplateMetadata(
                    name=name,
                    template_type=TemplateType.HOOK,
                    source_path=hook_file,
                    target_path=target_path,
                    description=f"Hook template from {category_dir.name} category"
                )
        
        return templates
    
    def _discover_workflows(self, workflows_dir: Path) -> Dict[str, TemplateMetadata]:
        """Discover workflow templates."""
        templates = {}
        
        for workflow_dir in workflows_dir.iterdir():
            if not workflow_dir.is_dir() or workflow_dir.name.startswith('.'):
                continue
                
            profile_file = workflow_dir / "profile.json"
            if profile_file.exists():
                name = f"workflow/{workflow_dir.name}"
                target_path = self.config.target_directory / "profiles" / f"{workflow_dir.name}.json"
                
                templates[name] = TemplateMetadata(
                    name=name,
                    template_type=TemplateType.WORKFLOW,
                    source_path=workflow_dir,
                    target_path=target_path,
                    description=f"Complete workflow: {workflow_dir.name}"
                )
        
        return templates
    
    def install_template(self, template_name: str, templates: Optional[Dict[str, TemplateMetadata]] = None) -> InstallationResult:
        """
        Install a specific template.
        
        Args:
            template_name: Name of the template to install
            templates: Optional pre-discovered templates dict
            
        Returns:
            InstallationResult with installation details
        """
        if templates is None:
            templates = self.discover_templates()
        
        if template_name not in templates:
            return InstallationResult(
                success=False,
                template_name=template_name,
                template_type=TemplateType.PROFILE,  # Default
                installed_files=[],
                skipped_files=[],
                errors=[f"Template '{template_name}' not found"],
                warnings=[]
            )
        
        template = templates[template_name]
        
        try:
            # Validate template before installation
            if self.config.validate_before_install:
                validation = self._validate_template(template)
                if not validation.is_valid:
                    return InstallationResult(
                        success=False,
                        template_name=template_name,
                        template_type=template.template_type,
                        installed_files=[],
                        skipped_files=[],
                        errors=[f"Template validation failed: {validation.errors}"],
                        warnings=[]
                    )
            
            # Check for conflicts and resolve them
            conflicts = self._check_conflicts(template)
            if conflicts and not self._resolve_conflicts(template, conflicts):
                return InstallationResult(
                    success=False,
                    template_name=template_name,
                    template_type=template.template_type,
                    installed_files=[],
                    skipped_files=[],
                    errors=["Failed to resolve installation conflicts"],
                    warnings=[]
                )
            
            # Perform the installation
            result = self._perform_installation(template)
            
            # Validate after installation
            if result.success and self.config.validate_after_install:
                post_validation = self._validate_installed_template(template)
                if not post_validation.is_valid:
                    result.warnings.extend([f"Post-installation validation warning: {w}" for w in post_validation.warnings])
            
            # Track successful installation
            if result.success:
                self.installed_templates[template_name] = template
                self.installation_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to install template '{template_name}': {e}")
            return InstallationResult(
                success=False,
                template_name=template_name,
                template_type=template.template_type,
                installed_files=[],
                skipped_files=[],
                errors=[f"Installation failed: {e}"],
                warnings=[]
            )
    
    def install_multiple_templates(self, template_names: List[str]) -> List[InstallationResult]:
        """
        Install multiple templates in dependency order.
        
        Args:
            template_names: List of template names to install
            
        Returns:
            List of InstallationResult objects
        """
        templates = self.discover_templates()
        results = []
        
        # Sort templates by dependencies
        sorted_names = self._sort_by_dependencies(template_names, templates)
        
        for template_name in sorted_names:
            result = self.install_template(template_name, templates)
            results.append(result)
            
            # Stop on first failure if not in permissive mode
            if not result.success and self.config.conflict_resolution.mode != InstallationMode.SKIP:
                self.logger.error(f"Stopping installation due to failure: {template_name}")
                break
        
        return results
    
    def _validate_template(self, template: TemplateMetadata) -> ValidationReport:
        """Validate a template before installation."""
        try:
            if template.template_type == TemplateType.PROFILE:
                return self.validator.validate_profile_template(template.source_path)
            elif template.template_type == TemplateType.CONTEXT:
                return self.validator.validate_context_template(template.source_path)
            elif template.template_type == TemplateType.HOOK:
                return self.validator.validate_hook_template(template.source_path)
            elif template.template_type == TemplateType.WORKFLOW:
                return self.validator.validate_workflow_template(template.source_path)
            else:
                return ValidationReport(
                    is_valid=False,
                    errors=[ConfigurationError(
                        file_path=str(template.source_path),
                        error_type="unknown_type",
                        message=f"Unknown template type: {template.template_type}",
                        severity="error"
                    )]
                )
        except Exception as e:
            return ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path=str(template.source_path),
                    error_type="validation_error",
                    message=f"Validation failed: {e}",
                    severity="error"
                )]
            )
    
    def _check_conflicts(self, template: TemplateMetadata) -> List[Path]:
        """Check for installation conflicts."""
        conflicts = []
        
        if template.template_type == TemplateType.WORKFLOW:
            # Workflows may install multiple files
            workflow_conflicts = self._check_workflow_conflicts(template)
            conflicts.extend(workflow_conflicts)
        else:
            # Single file installation
            if template.target_path.exists():
                conflicts.append(template.target_path)
        
        return conflicts
    
    def _check_workflow_conflicts(self, template: TemplateMetadata) -> List[Path]:
        """Check conflicts for workflow templates."""
        conflicts = []
        workflow_dir = template.source_path
        
        # Check profile file
        profile_file = workflow_dir / "profile.json"
        if profile_file.exists():
            target_profile = self.config.target_directory / "profiles" / f"{workflow_dir.name}.json"
            if target_profile.exists():
                conflicts.append(target_profile)
        
        # Check context files
        contexts_dir = workflow_dir / "contexts"
        if contexts_dir.exists():
            for context_file in contexts_dir.rglob("*.md"):
                rel_path = context_file.relative_to(contexts_dir)
                target_context = self.config.target_directory / "contexts" / rel_path
                if target_context.exists():
                    conflicts.append(target_context)
        
        # Check hook files
        hooks_dir = workflow_dir / "hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.rglob("*.yaml"):
                target_hook = self.config.target_directory / "hooks" / hook_file.name
                if target_hook.exists():
                    conflicts.append(target_hook)
        
        return conflicts
    
    def _resolve_conflicts(self, template: TemplateMetadata, conflicts: List[Path]) -> bool:
        """Resolve installation conflicts based on configuration."""
        mode = self.config.conflict_resolution.mode
        
        if mode == InstallationMode.SKIP:
            self.logger.info(f"Skipping template '{template.name}' due to conflicts")
            return False
        
        elif mode == InstallationMode.OVERWRITE:
            self.logger.info(f"Will overwrite existing files for template '{template.name}'")
            return True
        
        elif mode == InstallationMode.BACKUP:
            return self._backup_conflicting_files(conflicts)
        
        elif mode == InstallationMode.MERGE:
            return self._can_merge_conflicts(template, conflicts)
        
        return False
    
    def _backup_conflicting_files(self, conflicts: List[Path]) -> bool:
        """Create backups of conflicting files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.config.target_directory / f"backups/template_install_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for conflict_file in conflicts:
                if conflict_file.exists():
                    # Preserve directory structure in backup
                    rel_path = conflict_file.relative_to(self.config.target_directory)
                    backup_file = backup_dir / rel_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(conflict_file, backup_file)
                    self.logger.info(f"Backed up {conflict_file} to {backup_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup conflicting files: {e}")
            return False
    
    def _can_merge_conflicts(self, template: TemplateMetadata, conflicts: List[Path]) -> bool:
        """Check if conflicts can be merged."""
        # For now, only support merging for JSON profile files
        if template.template_type == TemplateType.PROFILE:
            return all(f.suffix.lower() == '.json' for f in conflicts)
        return False
    
    def _perform_installation(self, template: TemplateMetadata) -> InstallationResult:
        """Perform the actual template installation."""
        installed_files = []
        skipped_files = []
        errors = []
        warnings = []
        
        try:
            if self.config.dry_run:
                self.logger.info(f"DRY RUN: Would install template '{template.name}'")
                return InstallationResult(
                    success=True,
                    template_name=template.name,
                    template_type=template.template_type,
                    installed_files=[template.target_path],
                    skipped_files=[],
                    errors=[],
                    warnings=["Dry run mode - no files actually installed"]
                )
            
            if template.template_type == TemplateType.WORKFLOW:
                return self._install_workflow(template)
            else:
                return self._install_single_file(template)
                
        except Exception as e:
            errors.append(f"Installation failed: {e}")
            return InstallationResult(
                success=False,
                template_name=template.name,
                template_type=template.template_type,
                installed_files=installed_files,
                skipped_files=skipped_files,
                errors=errors,
                warnings=warnings
            )
    
    def _install_single_file(self, template: TemplateMetadata) -> InstallationResult:
        """Install a single template file."""
        installed_files = []
        errors = []
        warnings = []
        
        try:
            # Ensure target directory exists
            template.target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(template.source_path, template.target_path)
            installed_files.append(template.target_path)
            
            # For hooks, also copy associated Python script if it exists
            if template.template_type == TemplateType.HOOK:
                script_source = template.source_path.with_suffix('.py')
                if script_source.exists():
                    script_target = template.target_path.with_suffix('.py')
                    shutil.copy2(script_source, script_target)
                    installed_files.append(script_target)
            
            self.logger.info(f"Installed template '{template.name}' to {template.target_path}")
            
            return InstallationResult(
                success=True,
                template_name=template.name,
                template_type=template.template_type,
                installed_files=installed_files,
                skipped_files=[],
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"Failed to install file: {e}")
            return InstallationResult(
                success=False,
                template_name=template.name,
                template_type=template.template_type,
                installed_files=installed_files,
                skipped_files=[],
                errors=errors,
                warnings=warnings
            )
    
    def _install_workflow(self, template: TemplateMetadata) -> InstallationResult:
        """Install a complete workflow template."""
        installed_files = []
        skipped_files = []
        errors = []
        warnings = []
        
        try:
            workflow_dir = template.source_path
            
            # Install profile file
            profile_file = workflow_dir / "profile.json"
            if profile_file.exists():
                target_profile = self.config.target_directory / "profiles" / f"{workflow_dir.name}.json"
                target_profile.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(profile_file, target_profile)
                installed_files.append(target_profile)
            
            # Install context files
            contexts_dir = workflow_dir / "contexts"
            if contexts_dir.exists():
                for context_file in contexts_dir.rglob("*.md"):
                    rel_path = context_file.relative_to(contexts_dir)
                    target_context = self.config.target_directory / "contexts" / rel_path
                    target_context.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(context_file, target_context)
                    installed_files.append(target_context)
            
            # Install hook files
            hooks_dir = workflow_dir / "hooks"
            if hooks_dir.exists():
                for hook_file in hooks_dir.rglob("*.yaml"):
                    target_hook = self.config.target_directory / "hooks" / hook_file.name
                    target_hook.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(hook_file, target_hook)
                    installed_files.append(target_hook)
                    
                    # Copy associated Python scripts
                    script_file = hook_file.with_suffix('.py')
                    if script_file.exists():
                        target_script = target_hook.with_suffix('.py')
                        shutil.copy2(script_file, target_script)
                        installed_files.append(target_script)
            
            self.logger.info(f"Installed workflow '{template.name}' with {len(installed_files)} files")
            
            return InstallationResult(
                success=True,
                template_name=template.name,
                template_type=template.template_type,
                installed_files=installed_files,
                skipped_files=skipped_files,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"Failed to install workflow: {e}")
            return InstallationResult(
                success=False,
                template_name=template.name,
                template_type=template.template_type,
                installed_files=installed_files,
                skipped_files=skipped_files,
                errors=errors,
                warnings=warnings
            )
    
    def _validate_installed_template(self, template: TemplateMetadata) -> ValidationReport:
        """Validate template after installation."""
        try:
            if template.template_type == TemplateType.PROFILE:
                return self.validator.validate_profile_template(template.target_path)
            elif template.template_type == TemplateType.CONTEXT:
                return self.validator.validate_context_template(template.target_path)
            elif template.template_type == TemplateType.HOOK:
                return self.validator.validate_hook_template(template.target_path)
            else:
                return ValidationReport(is_valid=True, errors=[], warnings=[])
        except Exception as e:
            return ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path=str(template.target_path),
                    error_type="post_install_validation",
                    message=f"Post-installation validation failed: {e}",
                    severity="error"
                )]
            )
    
    def _sort_by_dependencies(self, template_names: List[str], templates: Dict[str, TemplateMetadata]) -> List[str]:
        """Sort templates by their dependencies."""
        # Simple topological sort - for now just return as-is
        # TODO: Implement proper dependency resolution
        return template_names
    
    def list_installed_templates(self) -> Dict[str, TemplateMetadata]:
        """Get list of currently installed templates."""
        return self.installed_templates.copy()
    
    def get_installation_history(self) -> List[InstallationResult]:
        """Get history of template installations."""
        return self.installation_history.copy()
    
    def uninstall_template(self, template_name: str) -> bool:
        """
        Uninstall a previously installed template.
        
        Args:
            template_name: Name of template to uninstall
            
        Returns:
            True if uninstallation was successful
        """
        if template_name not in self.installed_templates:
            self.logger.warning(f"Template '{template_name}' is not installed")
            return False
        
        template = self.installed_templates[template_name]
        
        try:
            # Find installation result for this template
            install_result = None
            for result in self.installation_history:
                if result.template_name == template_name and result.success:
                    install_result = result
                    break
            
            if not install_result:
                self.logger.warning(f"No installation record found for '{template_name}'")
                return False
            
            # Remove installed files
            for file_path in install_result.installed_files:
                if file_path.exists():
                    file_path.unlink()
                    self.logger.info(f"Removed {file_path}")
            
            # Remove from tracking
            del self.installed_templates[template_name]
            
            self.logger.info(f"Successfully uninstalled template '{template_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall template '{template_name}': {e}")
            return False