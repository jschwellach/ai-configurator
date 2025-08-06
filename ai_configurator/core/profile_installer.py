"""
Simplified Profile Installer for AI Configurator.
"""

import json
import logging
import shutil
import yaml
from pathlib import Path
from typing import Optional, List

from .library_manager import LibraryManager
from .file_utils import ensure_directory, copy_file


class ProfileInstaller:
    """Simplified profile installer for AI Configurator."""
    
    def __init__(self, library_manager: Optional[LibraryManager] = None):
        """Initialize the profile installer."""
        self.logger = logging.getLogger(__name__)
        self.library_manager = library_manager or LibraryManager()
        
        # Default Amazon Q directories
        self.amazonq_contexts_dir = Path.home() / ".aws" / "amazonq" / "contexts"
        self.amazonq_profiles_dir = Path.home() / ".aws" / "amazonq" / "profiles"
        
    def install_profile(self, profile_id: str) -> bool:
        """Install a profile by copying its contexts and creating Q CLI profile structure."""
        try:
            # Get profile configuration
            config = self.library_manager.get_configuration_by_id(profile_id)
            if not config:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
                
            # Get profile file path
            profile_path = self.library_manager.get_configuration_file_path(profile_id)
            if not profile_path or not profile_path.exists():
                self.logger.error(f"Profile file not found: {profile_path}")
                return False
                
            # Load profile YAML
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = yaml.safe_load(f)
                
            # Ensure Amazon Q directories exist
            ensure_directory(self.amazonq_contexts_dir)
            ensure_directory(self.amazonq_profiles_dir)
            
            # Copy contexts and collect paths
            contexts = profile_data.get('contexts', [])
            profile_dir = profile_path.parent
            context_paths = []
            
            for context_file in contexts:
                source_path = profile_dir / "contexts" / context_file
                if source_path.exists():
                    dest_path = self.amazonq_contexts_dir / context_file
                    copy_file(source_path, dest_path)
                    context_paths.append(str(dest_path))
                    self.logger.info(f"Copied context: {context_file}")
                else:
                    self.logger.warning(f"Context file not found: {source_path}")
            
            # Copy hooks and collect paths
            hooks = profile_data.get('hooks', [])
            hook_paths = []
            amazonq_hooks_dir = Path.home() / ".aws" / "amazonq" / "hooks"
            ensure_directory(amazonq_hooks_dir)
            
            for hook_file in hooks:
                source_path = profile_dir / "hooks" / hook_file
                if source_path.exists():
                    dest_path = amazonq_hooks_dir / hook_file
                    copy_file(source_path, dest_path)
                    # Make hook executable
                    dest_path.chmod(0o755)
                    hook_paths.append(str(dest_path))
                    self.logger.info(f"Copied hook: {hook_file}")
                else:
                    self.logger.warning(f"Hook file not found: {source_path}")
            
            # Create Q CLI profile directory structure
            profile_name = profile_id.replace('-v1', '')  # Remove version suffix for cleaner profile name
            q_profile_dir = self.amazonq_profiles_dir / profile_name
            ensure_directory(q_profile_dir)
            
            # Create context.json file for Q CLI
            hooks_config = {}
            for hook_file in hooks:
                hook_name = hook_file.replace('.py', '')  # Remove .py extension for hook name
                hooks_config[hook_name] = {
                    "trigger": "per_prompt",
                    "type": "inline",
                    "disabled": False,
                    "timeout_ms": 30000,
                    "max_output_size": 10240,
                    "cache_ttl_seconds": 0,
                    "command": str(amazonq_hooks_dir / hook_file)
                }
            
            context_json = {
                "paths": context_paths,
                "hooks": hooks_config
            }
            
            context_json_path = q_profile_dir / "context.json"
            with open(context_json_path, 'w', encoding='utf-8') as f:
                json.dump(context_json, f, indent=2)
            
            self.logger.info(f"Created Q CLI profile: {profile_name}")
            self.logger.info(f"Successfully installed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing profile '{profile_id}': {e}")
            return False
    
    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile by deleting its contexts and Q CLI profile directory."""
        try:
            # Get profile configuration
            config = self.library_manager.get_configuration_by_id(profile_id)
            if not config:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
                
            # Get profile file path
            profile_path = self.library_manager.get_configuration_file_path(profile_id)
            if not profile_path or not profile_path.exists():
                self.logger.error(f"Profile file not found: {profile_path}")
                return False
                
            # Load profile YAML
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = yaml.safe_load(f)
                
            # Remove contexts
            contexts = profile_data.get('contexts', [])
            
            for context_file in contexts:
                context_path = self.amazonq_contexts_dir / context_file
                if context_path.exists():
                    context_path.unlink()
                    self.logger.info(f"Removed context: {context_file}")
            
            # Remove hooks
            hooks = profile_data.get('hooks', [])
            amazonq_hooks_dir = Path.home() / ".aws" / "amazonq" / "hooks"
            
            for hook_file in hooks:
                hook_path = amazonq_hooks_dir / hook_file
                if hook_path.exists():
                    hook_path.unlink()
                    self.logger.info(f"Removed hook: {hook_file}")
            
            # Remove Q CLI profile directory
            profile_name = profile_id.replace('-v1', '')  # Remove version suffix
            q_profile_dir = self.amazonq_profiles_dir / profile_name
            if q_profile_dir.exists():
                shutil.rmtree(q_profile_dir)
                self.logger.info(f"Removed Q CLI profile directory: {profile_name}")
            
            self.logger.info(f"Successfully removed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing profile '{profile_id}': {e}")
            return False
    
    def is_profile_installed(self, profile_id: str) -> bool:
        """Check if a profile is installed by looking for Q CLI profile directory."""
        profile_name = profile_id.replace('-v1', '')  # Remove version suffix
        q_profile_dir = self.amazonq_profiles_dir / profile_name
        context_json_path = q_profile_dir / "context.json"
        return context_json_path.exists()
    
    def list_installed_profiles(self) -> List[str]:
        """List all installed profiles."""
        if not self.amazonq_profiles_dir.exists():
            return []
            
        installed = []
        for marker_file in self.amazonq_profiles_dir.glob("*.installed"):
            profile_id = marker_file.stem
            installed.append(profile_id)
            
        return installed
