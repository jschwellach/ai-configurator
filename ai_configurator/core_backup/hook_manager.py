"""Advanced hook management and execution system."""

import json
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from ..utils.logging import LoggerMixin
# Removed circular import - ConfigurationManager will be passed as parameter
from .platform_utils import PlatformManager
from .models import (
    HookConfig, HookType, HookTrigger, ConditionConfig, 
    ScriptConfig, ContextConfig, ConfigurationError, ValidationReport
)
from .yaml_loader import YamlConfigLoader
from .markdown_processor import MarkdownProcessor
# Removed directory_manager import to avoid circular dependencies


class HookManager(LoggerMixin):
    """Enhanced hook management system supporting YAML hook definitions."""
    
    def __init__(
        self,
        config_dir: Path,
        yaml_loader: YamlConfigLoader,
        platform_manager: Optional[PlatformManager] = None,
        markdown_processor: Optional[MarkdownProcessor] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_dir = config_dir
        self.yaml_loader = yaml_loader
        self.markdown_processor = markdown_processor or MarkdownProcessor()
        
        # Initialize hooks directory
        self.hooks_dir = self.config_dir / "hooks"
        self.hooks_dir.mkdir(parents=True, exist_ok=True)
        # hooks_dir already set above
        
        # Cache for loaded hook configurations
        self._hook_cache: Dict[str, HookConfig] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
        # Registry of hooks by trigger type
        self._hooks_by_trigger: Dict[HookTrigger, List[HookConfig]] = {
            trigger: [] for trigger in HookTrigger
        }
    
    def discover_hooks(self) -> Dict[str, List[str]]:
        """Discover all available hooks organized by type."""
        hooks = {
            "yaml": [],
            "scripts": [],
            "python": [],
            "shell": [],
            "markdown": [],
            "legacy": []
        }
        
        if not self.hooks_dir.exists():
            return hooks
        
        for hook_file in self.hooks_dir.iterdir():
            if hook_file.is_file():
                if hook_file.suffix in [".yaml", ".yml"]:
                    hooks["yaml"].append(hook_file.stem)
                elif hook_file.suffix == ".py":
                    hooks["python"].append(hook_file.stem)
                    hooks["scripts"].append(hook_file.stem)
                elif hook_file.suffix in [".sh", ".bash"]:
                    hooks["shell"].append(hook_file.stem)
                    hooks["scripts"].append(hook_file.stem)
                elif hook_file.suffix == ".md":
                    hooks["markdown"].append(hook_file.stem)
                elif hook_file.suffix == ".json":
                    hooks["legacy"].append(hook_file.stem)
        
        return hooks
    
    def validate_hook_name(self, hook_name: str) -> tuple[bool, str]:
        """
        Validate a hook name against naming conventions.
        
        Args:
            hook_name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Simple naming validation
        if not hook_name or not hook_name.replace('-', '').replace('_', '').isalnum():
            return False, "Hook name must contain only alphanumeric characters, hyphens, and underscores"
        return True, ""
    
    def load_hook_config(self, hook_name: str) -> Optional[HookConfig]:
        """Load hook configuration from YAML file with caching."""
        hook_file = self.hooks_dir / f"{hook_name}.yaml"
        
        if not hook_file.exists():
            # Try .yml extension
            hook_file = self.hooks_dir / f"{hook_name}.yml"
            if not hook_file.exists():
                self.logger.warning(f"Hook configuration file not found: {hook_name}")
                return None
        
        # Check cache
        file_mtime = hook_file.stat().st_mtime
        if (hook_name in self._hook_cache and 
            hook_name in self._cache_timestamps and
            self._cache_timestamps[hook_name] >= file_mtime):
            return self._hook_cache[hook_name]
        
        try:
            hook_config = self.yaml_loader.load_hook_config(hook_file)
            if hook_config:
                # Cache the configuration
                self._hook_cache[hook_name] = hook_config
                self._cache_timestamps[hook_name] = file_mtime
                self.logger.debug(f"Loaded hook configuration: {hook_name}")
                return hook_config
        except Exception as e:
            self.logger.error(f"Failed to load hook configuration '{hook_name}': {e}")
        
        return None
    
    def load_hooks_by_trigger(self, trigger: HookTrigger) -> List[HookConfig]:
        """Load all hooks for a specific trigger, sorted by execution order."""
        if trigger in self._hooks_by_trigger and self._hooks_by_trigger[trigger]:
            return self._hooks_by_trigger[trigger]
        
        hooks = []
        discovered = self.discover_hooks()
        
        for hook_name in discovered["yaml"]:
            hook_config = self.load_hook_config(hook_name)
            if hook_config and hook_config.trigger == trigger and hook_config.enabled:
                # Check conditions
                if self._check_hook_conditions(hook_config):
                    hooks.append(hook_config)
        
        # Sort hooks by name to ensure consistent execution order
        hooks.sort(key=lambda h: h.name)
        
        # Cache the result
        self._hooks_by_trigger[trigger] = hooks
        
        return hooks
    
    def _check_hook_conditions(self, hook_config: HookConfig) -> bool:
        """Check if hook conditions are met for execution."""
        if not hook_config.conditions:
            return True
        
        for condition in hook_config.conditions:
            # Check platform condition
            if condition.platform:
                current_platform = self.platform.get_platform_name().lower()
                if current_platform not in condition.platform:
                    return False
            
            # Check environment variables
            if condition.environment:
                for env_var, expected_value in condition.environment.items():
                    if os.environ.get(env_var) != expected_value:
                        return False
        
        return True
    
    def execute_hook(self, hook_config: HookConfig, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
        """Execute a hook based on its configuration."""
        try:
            if hook_config.type == HookType.CONTEXT:
                return self._execute_context_hook(hook_config, context)
            elif hook_config.type == HookType.SCRIPT:
                return self._execute_script_hook(hook_config, context)
            elif hook_config.type == HookType.HYBRID:
                return self._execute_hybrid_hook(hook_config, context)
            else:
                return False, "", f"Unsupported hook type: {hook_config.type}"
        except Exception as e:
            self.logger.error(f"Failed to execute hook '{hook_config.name}': {e}")
            return False, "", str(e)
    
    def _execute_context_hook(self, hook_config: HookConfig, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
        """Execute a context-type hook."""
        if not hook_config.context or not hook_config.context.sources:
            return False, "", "Context hook has no context sources defined"
        
        try:
            context_content = []
            
            for source_path in hook_config.context.sources:
                # Resolve relative paths
                if not Path(source_path).is_absolute():
                    source_file = self.config_manager.config_dir / source_path
                else:
                    source_file = Path(source_path)
                
                if source_file.exists():
                    if source_file.suffix == ".md":
                        # Load Markdown with frontmatter
                        context_file = self.markdown_processor.load_context_file(source_file)
                        context_content.append(context_file.content)
                    else:
                        # Load plain text
                        with open(source_file, 'r', encoding='utf-8') as f:
                            context_content.append(f.read())
                else:
                    self.logger.warning(f"Context source not found: {source_path}")
            
            combined_content = "\n\n".join(context_content)
            self.logger.info(f"Context hook '{hook_config.name}' loaded {len(context_content)} sources")
            
            return True, combined_content, ""
            
        except Exception as e:
            return False, "", f"Failed to load context: {e}"
    
    def _execute_script_hook(self, hook_config: HookConfig, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
        """Execute a script-type hook."""
        if not hook_config.script:
            return False, "", "Script hook has no script configuration"
        
        script_config = hook_config.script
        
        # Prepare command
        cmd = [script_config.command]
        if script_config.args:
            cmd.extend(script_config.args)
        
        # Prepare environment
        env = dict(os.environ)
        env.update(script_config.env)
        
        # Add standard environment variables
        env["AMAZONQ_CONFIG_DIR"] = str(self.config_manager.config_dir)
        env["AI_CONFIGURATOR_HOOKS_DIR"] = str(self.hooks_dir)
        env["HOOK_NAME"] = hook_config.name
        
        # Add context as environment variable if provided
        if context:
            env["HOOK_CONTEXT"] = json.dumps(context)
        
        # Determine working directory
        working_dir = self.hooks_dir
        if script_config.working_dir:
            if Path(script_config.working_dir).is_absolute():
                working_dir = Path(script_config.working_dir)
            else:
                working_dir = self.config_manager.config_dir / script_config.working_dir
        
        try:
            self.logger.debug(f"Executing script hook: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=script_config.timeout,
                env=env,
                cwd=working_dir
            )
            
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            if success:
                self.logger.info(f"Script hook '{hook_config.name}' executed successfully")
            else:
                self.logger.warning(f"Script hook '{hook_config.name}' failed with return code {result.returncode}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Script hook '{hook_config.name}' timed out after {script_config.timeout} seconds")
            return False, "", f"Hook execution timed out after {script_config.timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    def _execute_hybrid_hook(self, hook_config: HookConfig, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
        """Execute a hybrid-type hook (both context and script)."""
        # First execute context part
        context_success, context_content, context_error = self._execute_context_hook(hook_config, context)
        
        if not context_success:
            return False, "", f"Context execution failed: {context_error}"
        
        # Then execute script part with context as additional input
        enhanced_context = context or {}
        enhanced_context["loaded_context"] = context_content
        
        script_success, script_output, script_error = self._execute_script_hook(hook_config, enhanced_context)
        
        # Combine results
        combined_output = f"Context Content:\n{context_content}\n\nScript Output:\n{script_output}"
        
        return script_success, combined_output, script_error
    
    def execute_hooks_for_trigger(self, trigger: HookTrigger, context: Optional[Dict[str, Any]] = None) -> List[Tuple[str, bool, str, str]]:
        """Execute all hooks for a specific trigger in order."""
        hooks = self.load_hooks_by_trigger(trigger)
        results = []
        
        self.logger.info(f"Executing {len(hooks)} hooks for trigger: {trigger.value}")
        
        for hook_config in hooks:
            try:
                success, stdout, stderr = self.execute_hook(hook_config, context)
                results.append((hook_config.name, success, stdout, stderr))
                
                if not success:
                    self.logger.error(f"Hook '{hook_config.name}' failed: {stderr}")
                    # Continue with other hooks as per requirement 2.4
                    
            except Exception as e:
                self.logger.error(f"Exception executing hook '{hook_config.name}': {e}")
                results.append((hook_config.name, False, "", str(e)))
                # Continue with other hooks
        
        return results
    
    def execute_hook_by_name(self, hook_name: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, str]:
        """Execute a specific hook by name."""
        hook_config = self.load_hook_config(hook_name)
        if not hook_config:
            return False, "", f"Hook configuration not found: {hook_name}"
        
        if not hook_config.enabled:
            return False, "", f"Hook is disabled: {hook_name}"
        
        if not self._check_hook_conditions(hook_config):
            return False, "", f"Hook conditions not met: {hook_name}"
        
        return self.execute_hook(hook_config, context)
    
    def validate_hooks(self) -> ValidationReport:
        """Validate all hooks and return detailed validation report."""
        errors = []
        warnings = []
        info = []
        files_checked = []
        
        discovered = self.discover_hooks()
        
        # Validate YAML hook configurations
        for hook_name in discovered["yaml"]:
            hook_file = self.hooks_dir / f"{hook_name}.yaml"
            if not hook_file.exists():
                hook_file = self.hooks_dir / f"{hook_name}.yml"
            
            files_checked.append(str(hook_file))
            
            try:
                hook_config = self.load_hook_config(hook_name)
                if hook_config:
                    # Validate hook configuration
                    validation_errors = self._validate_hook_config(hook_config, hook_file)
                    errors.extend(validation_errors)
                    
                    info.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="info",
                        message=f"Hook '{hook_name}' loaded successfully",
                        severity="info"
                    ))
                else:
                    errors.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="load_error",
                        message=f"Failed to load hook configuration",
                        severity="error"
                    ))
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(hook_file),
                    error_type="exception",
                    message=f"Exception loading hook: {e}",
                    severity="error"
                ))
        
        # Check for orphaned Markdown files
        for md_name in discovered["markdown"]:
            yaml_exists = (md_name in discovered["yaml"] or 
                          any(hook_config and hook_config.context and 
                              any(f"{md_name}.md" in source for source in hook_config.context.sources)
                              for hook_config in self._hook_cache.values()))
            
            if not yaml_exists:
                warnings.append(ConfigurationError(
                    file_path=str(self.hooks_dir / f"{md_name}.md"),
                    error_type="orphaned_file",
                    message=f"Markdown file has no corresponding YAML hook configuration",
                    severity="warning"
                ))
        
        is_valid = len(errors) == 0
        summary = {
            "total_hooks": len(discovered["yaml"]),
            "valid_hooks": len(discovered["yaml"]) - len([e for e in errors if e.error_type != "info"]),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info)
        }
        
        return ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=files_checked,
            summary=summary
        )
    
    def _validate_hook_config(self, hook_config: HookConfig, hook_file: Path) -> List[ConfigurationError]:
        """Validate a single hook configuration."""
        errors = []
        
        # Validate context sources exist
        if hook_config.context and hook_config.context.sources:
            for source_path in hook_config.context.sources:
                if not Path(source_path).is_absolute():
                    source_file = self.config_manager.config_dir / source_path
                else:
                    source_file = Path(source_path)
                
                if not source_file.exists():
                    errors.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="missing_file",
                        message=f"Context source file not found: {source_path}",
                        severity="error"
                    ))
        
        # Validate script configuration
        if hook_config.script:
            # Check if command exists (basic check)
            try:
                import shutil
                if not shutil.which(hook_config.script.command):
                    errors.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="missing_command",
                        message=f"Script command not found: {hook_config.script.command}",
                        severity="warning"
                    ))
            except Exception:
                pass  # Skip if we can't check
        
        # Validate hook type consistency
        if hook_config.type == HookType.CONTEXT and not hook_config.context:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="config_mismatch",
                message="Context hook type specified but no context configuration provided",
                severity="error"
            ))
        
        if hook_config.type == HookType.SCRIPT and not hook_config.script:
            errors.append(ConfigurationError(
                file_path=str(hook_file),
                error_type="config_mismatch",
                message="Script hook type specified but no script configuration provided",
                severity="error"
            ))
        
        return errors
    
    def create_script_hook_template(self, hook_name: str, script_type: str = "python") -> bool:
        """Create a simple script hook template (Python or shell)."""
        try:
            # Ensure hooks directory exists
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            
            if script_type == "python":
                extension = "py"
                content = self._generate_python_script_template(hook_name)
            elif script_type == "shell":
                extension = "sh"
                content = self._generate_shell_script_template(hook_name)
            else:
                raise ValueError(f"Unsupported script type: {script_type}")
            
            # Create script file
            script_file = self.hooks_dir / f"{hook_name}.{extension}"
            
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make shell scripts executable
            if script_type == "shell":
                import stat
                script_file.chmod(script_file.stat().st_mode | stat.S_IEXEC)
            
            self.logger.info(f"Created {script_type} script hook: {hook_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create script hook template: {e}")
            return False
    
    def _generate_python_script_template(self, hook_name: str) -> str:
        """Generate Python script template content."""
        return f'''#!/usr/bin/env python3
"""
{hook_name} Hook Script

This is an auto-generated hook template.
Customize this script to perform your desired actions.
"""

import sys
import os
from pathlib import Path

def main():
    """Main hook function."""
    print(f"Executing {hook_name} hook...")
    
    # Access environment variables
    config_dir = os.getenv("AMAZONQ_CONFIG_DIR", "")
    hooks_dir = os.getenv("AI_CONFIGURATOR_HOOKS_DIR", "")
    hook_name = os.getenv("HOOK_NAME", "{hook_name}")
    
    print(f"Config directory: {{config_dir}}")
    print(f"Hooks directory: {{hooks_dir}}")
    print(f"Hook name: {{hook_name}}")
    
    # Add your custom logic here
    # Example: Read configuration files, process data, etc.
    
    # Return success
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _generate_shell_script_template(self, hook_name: str) -> str:
        """Generate shell script template content."""
        return f'''#!/bin/bash
#
# {hook_name} Hook Script
#
# This is an auto-generated hook template.
# Customize this script to perform your desired actions.
#

set -e  # Exit on error

echo "Executing {hook_name} hook..."

# Access environment variables
echo "Config directory: $AMAZONQ_CONFIG_DIR"
echo "Hooks directory: $AI_CONFIGURATOR_HOOKS_DIR"
echo "Hook name: $HOOK_NAME"

# Add your custom logic here
# Example: Process files, run commands, etc.

echo "{hook_name} hook completed successfully"
exit 0
'''

    def create_hook_template(self, hook_name: str, hook_type: HookType = HookType.CONTEXT, 
                           trigger: HookTrigger = HookTrigger.ON_SESSION_START) -> bool:
        """Create a new YAML hook template."""
        try:
            # Ensure hooks directory exists
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            
            # Create YAML configuration
            yaml_content = self._generate_hook_template(hook_name, hook_type, trigger)
            yaml_file = self.hooks_dir / f"{hook_name}.yaml"
            
            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Create companion Markdown file if it's a context hook
            if hook_type in [HookType.CONTEXT, HookType.HYBRID]:
                md_content = self._generate_markdown_template(hook_name)
                md_file = self.hooks_dir / f"{hook_name}.md"
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            
            self.logger.info(f"Created hook template: {hook_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create hook template: {e}")
            return False
    
    def _generate_hook_template(self, hook_name: str, hook_type: HookType, trigger: HookTrigger) -> str:
        """Generate YAML hook template content."""
        template = f"""# {hook_name} Hook Configuration
name: "{hook_name}"
description: "Auto-generated hook template"
version: "1.0"
type: "{hook_type.value}"
trigger: "{trigger.value}"
timeout: 30
enabled: true

"""
        
        if hook_type in [HookType.CONTEXT, HookType.HYBRID]:
            template += f"""context:
  sources:
    - "hooks/{hook_name}.md"
  tags: []
  categories: []
  priority: 0

"""
        
        if hook_type in [HookType.SCRIPT, HookType.HYBRID]:
            template += f"""script:
  command: "python"
  args: ["scripts/{hook_name}.py"]
  env: {{}}
  working_dir: "."
  timeout: 30

"""
        
        template += """conditions: []

metadata:
  created_by: "ai-configurator"
  template_version: "1.0"
"""
        
        return template
    
    def _generate_markdown_template(self, hook_name: str) -> str:
        """Generate Markdown template content."""
        return f"""---
title: "{hook_name} Hook Context"
tags: ["hook", "context"]
categories: ["automation"]
priority: 0
---

# {hook_name} Hook Context

This file provides context for the {hook_name} hook.

## Purpose

Describe what this hook does and when it should be executed.

## Context Information

Add relevant context information that will be provided to the AI system when this hook is executed.

## Examples

Provide examples of how this hook should behave or what output is expected.
"""
    
    def test_hook(self, hook_name: str) -> Dict[str, Any]:
        """Test a hook and return detailed results."""
        test_result = {
            "hook": hook_name,
            "exists": False,
            "valid_config": False,
            "conditions_met": False,
            "execution_time": 0,
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": None,
            "hook_type": None
        }
        
        # Check if hook configuration exists
        hook_config = self.load_hook_config(hook_name)
        test_result["exists"] = hook_config is not None
        
        if not test_result["exists"]:
            test_result["error"] = "Hook configuration not found"
            return test_result
        
        test_result["valid_config"] = True
        test_result["hook_type"] = hook_config.type.value
        
        # Check conditions
        test_result["conditions_met"] = self._check_hook_conditions(hook_config)
        
        if not test_result["conditions_met"]:
            test_result["error"] = "Hook conditions not met"
            return test_result
        
        # Execute hook
        start_time = time.time()
        
        success, stdout, stderr = self.execute_hook(hook_config, {"test_mode": True})
        
        test_result["execution_time"] = round(time.time() - start_time, 3)
        test_result["success"] = success
        test_result["stdout"] = stdout
        test_result["stderr"] = stderr
        
        if not success and not stderr:
            test_result["error"] = "Hook execution failed"
        
        return test_result
    
    def reload_hooks(self) -> None:
        """Reload all hook configurations, clearing cache."""
        self._hook_cache.clear()
        self._cache_timestamps.clear()
        self._hooks_by_trigger = {trigger: [] for trigger in HookTrigger}
        self.logger.info("Hook configurations reloaded")
    
    def get_hook_info(self, hook_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a hook."""
        hook_config = self.load_hook_config(hook_name)
        if not hook_config:
            return None
        
        return {
            "name": hook_config.name,
            "description": hook_config.description,
            "version": hook_config.version,
            "type": hook_config.type.value,
            "trigger": hook_config.trigger.value,
            "enabled": hook_config.enabled,
            "timeout": hook_config.timeout,
            "has_context": hook_config.context is not None,
            "has_script": hook_config.script is not None,
            "conditions": len(hook_config.conditions),
            "context_sources": len(hook_config.context.sources) if hook_config.context else 0,
            "metadata": hook_config.metadata
        }
    
    def list_hooks_by_trigger(self) -> Dict[str, List[str]]:
        """List all hooks organized by trigger type."""
        hooks_by_trigger = {}
        discovered = self.discover_hooks()
        
        for hook_name in discovered["yaml"]:
            hook_config = self.load_hook_config(hook_name)
            if hook_config and hook_config.enabled:
                trigger_name = hook_config.trigger.value
                if trigger_name not in hooks_by_trigger:
                    hooks_by_trigger[trigger_name] = []
                hooks_by_trigger[trigger_name].append(hook_name)
        
        return hooks_by_trigger
    
    # Legacy compatibility methods
    def list_available_hooks(self) -> Dict[str, List[str]]:
        """Legacy method for backward compatibility."""
        return self.discover_hooks()
    
    def load_hook_config_legacy(self) -> Optional[Dict[str, Any]]:
        """Legacy method for loading old-style hook configuration."""
        config_file = self.hooks_dir / "config.yaml"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load legacy hook configuration: {e}")
            return None
