"""Advanced hook management and execution system."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..utils.logging import LoggerMixin
from .config_manager import ConfigurationManager
from .platform import PlatformManager


class HookManager(LoggerMixin):
    """Manages hook execution and lifecycle."""
    
    def __init__(
        self,
        platform_manager: Optional[PlatformManager] = None,
        config_manager: Optional[ConfigurationManager] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_manager = config_manager or ConfigurationManager(self.platform)
        self.hooks_dir = self.config_manager.config_dir / "hooks"
    
    def list_available_hooks(self) -> Dict[str, List[str]]:
        """List all available hooks organized by type."""
        hooks = {
            "scripts": [],
            "python": [],
            "shell": [],
            "config": []
        }
        
        if not self.hooks_dir.exists():
            return hooks
        
        for hook_file in self.hooks_dir.iterdir():
            if hook_file.is_file():
                if hook_file.suffix == ".py":
                    hooks["python"].append(hook_file.name)
                    hooks["scripts"].append(hook_file.name)
                elif hook_file.suffix in [".sh", ".bash"]:
                    hooks["shell"].append(hook_file.name)
                    hooks["scripts"].append(hook_file.name)
                elif hook_file.suffix in [".yaml", ".yml", ".json"]:
                    hooks["config"].append(hook_file.name)
        
        return hooks
    
    def load_hook_config(self) -> Optional[Dict[str, Any]]:
        """Load hook configuration from config.yaml."""
        config_file = self.hooks_dir / "config.yaml"
        
        if not config_file.exists():
            self.logger.warning("Hook configuration file not found")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load hook configuration: {e}")
            return None
    
    def execute_hook(
        self, 
        hook_name: str, 
        args: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """Execute a hook script and return success status, stdout, stderr."""
        hook_file = self.hooks_dir / hook_name
        
        if not hook_file.exists():
            return False, "", f"Hook file not found: {hook_name}"
        
        # Prepare command
        if hook_file.suffix == ".py":
            cmd = [sys.executable, str(hook_file)]
        elif hook_file.suffix in [".sh", ".bash"]:
            if self.platform.is_windows():
                # On Windows, try to use bash if available, otherwise skip
                bash_path = self.platform._find_bash()
                if bash_path:
                    cmd = [bash_path, str(hook_file)]
                else:
                    return False, "", "Bash not available on Windows"
            else:
                cmd = ["bash", str(hook_file)]
        else:
            return False, "", f"Unsupported hook file type: {hook_file.suffix}"
        
        # Add arguments
        if args:
            cmd.extend(args)
        
        # Prepare environment
        env = dict(os.environ) if 'os' in globals() else {}
        if env_vars:
            env.update(env_vars)
        
        # Add Amazon Q config directory to environment
        env["AMAZONQ_CONFIG_DIR"] = str(self.config_manager.config_dir)
        env["AI_CONFIGURATOR_HOOKS_DIR"] = str(self.hooks_dir)
        
        try:
            self.logger.debug(f"Executing hook: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=self.hooks_dir
            )
            
            success = result.returncode == 0
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            
            if success:
                self.logger.info(f"Hook '{hook_name}' executed successfully")
            else:
                self.logger.warning(f"Hook '{hook_name}' failed with return code {result.returncode}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Hook '{hook_name}' timed out after {timeout} seconds")
            return False, "", f"Hook execution timed out after {timeout} seconds"
        except Exception as e:
            self.logger.error(f"Failed to execute hook '{hook_name}': {e}")
            return False, "", str(e)
    
    def execute_context_hook(self, context_name: str) -> Tuple[bool, str]:
        """Execute context loading hook and return success status and content."""
        hook_config = self.load_hook_config()
        if not hook_config:
            return False, "Hook configuration not available"
        
        # Check if context is defined in hook config
        contexts = hook_config.get("contexts", {})
        if context_name not in contexts:
            return False, f"Context '{context_name}' not defined in hook configuration"
        
        # Execute context loader hook
        success, stdout, stderr = self.execute_hook(
            "context_loader.py",
            args=[context_name],
            timeout=60
        )
        
        if success:
            return True, stdout
        else:
            error_msg = stderr or "Unknown error"
            return False, f"Context loading failed: {error_msg}"
    
    def validate_hooks(self) -> Dict[str, Any]:
        """Validate all hooks and return detailed status."""
        validation_result = {
            "valid_hooks": [],
            "invalid_hooks": [],
            "executable_hooks": [],
            "config_issues": [],
            "recommendations": []
        }
        
        hooks = self.list_available_hooks()
        
        # Validate script hooks
        for script in hooks["scripts"]:
            hook_file = self.hooks_dir / script
            
            # Check if file exists and is readable
            if not hook_file.exists():
                validation_result["invalid_hooks"].append({
                    "hook": script,
                    "issue": "File not found"
                })
                continue
            
            if not hook_file.is_file():
                validation_result["invalid_hooks"].append({
                    "hook": script,
                    "issue": "Not a regular file"
                })
                continue
            
            # Check if file is executable (on Unix systems)
            if not self.platform.is_windows():
                if not hook_file.stat().st_mode & 0o111:
                    validation_result["invalid_hooks"].append({
                        "hook": script,
                        "issue": "File is not executable"
                    })
                    continue
            
            # Basic syntax validation for Python files
            if hook_file.suffix == ".py":
                try:
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to compile the Python code
                    compile(content, str(hook_file), 'exec')
                    validation_result["valid_hooks"].append(script)
                    validation_result["executable_hooks"].append(script)
                    
                except SyntaxError as e:
                    validation_result["invalid_hooks"].append({
                        "hook": script,
                        "issue": f"Python syntax error: {e}"
                    })
                except Exception as e:
                    validation_result["invalid_hooks"].append({
                        "hook": script,
                        "issue": f"Failed to validate: {e}"
                    })
            else:
                # For shell scripts, just check if they're readable
                validation_result["valid_hooks"].append(script)
                validation_result["executable_hooks"].append(script)
        
        # Validate hook configuration
        hook_config = self.load_hook_config()
        if hook_config:
            # Check if context loader exists for defined contexts
            contexts = hook_config.get("contexts", {})
            if contexts and "context_loader.py" not in hooks["python"]:
                validation_result["config_issues"].append(
                    "Contexts defined but context_loader.py not found"
                )
            
            # Check if defined context files exist
            for context_name, files in contexts.items():
                for file_path in files:
                    full_path = self.config_manager.config_dir / file_path
                    if not full_path.exists():
                        validation_result["config_issues"].append(
                            f"Context file not found for '{context_name}': {file_path}"
                        )
        else:
            validation_result["config_issues"].append("Hook configuration file not found")
        
        # Generate recommendations
        if validation_result["invalid_hooks"]:
            validation_result["recommendations"].append(
                f"Fix {len(validation_result['invalid_hooks'])} invalid hooks"
            )
        
        if validation_result["config_issues"]:
            validation_result["recommendations"].append(
                "Resolve hook configuration issues"
            )
        
        if not validation_result["executable_hooks"]:
            validation_result["recommendations"].append(
                "No executable hooks found - consider adding automation scripts"
            )
        
        return validation_result
    
    def create_hook_template(self, hook_name: str, hook_type: str = "python") -> bool:
        """Create a new hook from template."""
        if hook_type == "python":
            template_content = '''#!/usr/bin/env python3
"""
{hook_name} - Amazon Q CLI Hook

This hook is executed by AI Configurator.
Environment variables available:
- AMAZONQ_CONFIG_DIR: Path to Amazon Q configuration directory
- AI_CONFIGURATOR_HOOKS_DIR: Path to hooks directory
"""

import os
import sys
from pathlib import Path

def main():
    """Main hook function."""
    # Get environment variables
    config_dir = Path(os.environ.get("AMAZONQ_CONFIG_DIR", ""))
    hooks_dir = Path(os.environ.get("AI_CONFIGURATOR_HOOKS_DIR", ""))
    
    print(f"Hook '{hook_name}' executed successfully!")
    print(f"Config directory: {{config_dir}}")
    print(f"Hooks directory: {{hooks_dir}}")
    
    # Add your hook logic here
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''.format(hook_name=hook_name)
            
            hook_file = self.hooks_dir / f"{hook_name}.py"
            
        elif hook_type == "shell":
            template_content = '''#!/bin/bash
#
# {hook_name} - Amazon Q CLI Hook
#
# This hook is executed by AI Configurator.
# Environment variables available:
# - AMAZONQ_CONFIG_DIR: Path to Amazon Q configuration directory
# - AI_CONFIGURATOR_HOOKS_DIR: Path to hooks directory
#

set -e

echo "Hook '{hook_name}' executed successfully!"
echo "Config directory: $AMAZONQ_CONFIG_DIR"
echo "Hooks directory: $AI_CONFIGURATOR_HOOKS_DIR"

# Add your hook logic here

exit 0
'''.format(hook_name=hook_name)
            
            hook_file = self.hooks_dir / f"{hook_name}.sh"
        else:
            self.logger.error(f"Unsupported hook type: {hook_type}")
            return False
        
        try:
            # Ensure hooks directory exists
            self.hooks_dir.mkdir(parents=True, exist_ok=True)
            
            # Write hook file
            with open(hook_file, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Make executable on Unix systems
            if not self.platform.is_windows():
                hook_file.chmod(0o755)
            
            self.logger.info(f"Created hook template: {hook_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create hook template: {e}")
            return False
    
    def test_hook(self, hook_name: str) -> Dict[str, Any]:
        """Test a hook and return detailed results."""
        test_result = {
            "hook": hook_name,
            "exists": False,
            "executable": False,
            "execution_time": 0,
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": None
        }
        
        hook_file = self.hooks_dir / hook_name
        test_result["exists"] = hook_file.exists()
        
        if not test_result["exists"]:
            test_result["error"] = "Hook file not found"
            return test_result
        
        # Check if executable
        if self.platform.is_windows() or hook_file.stat().st_mode & 0o111:
            test_result["executable"] = True
        
        if not test_result["executable"]:
            test_result["error"] = "Hook file is not executable"
            return test_result
        
        # Execute hook with test arguments
        import time
        start_time = time.time()
        
        success, stdout, stderr = self.execute_hook(
            hook_name,
            args=["--test"] if hook_name.endswith(".py") else [],
            timeout=10
        )
        
        test_result["execution_time"] = round(time.time() - start_time, 3)
        test_result["success"] = success
        test_result["stdout"] = stdout
        test_result["stderr"] = stderr
        
        if not success and not test_result["stderr"]:
            test_result["error"] = "Hook execution failed"
        
        return test_result
