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
from .catalog_schema import AgentConfig
from .file_utils import ensure_directory, copy_file


class ProfileInstaller:
    """Simplified profile installer for AI Configurator."""
    
    def __init__(self, library_manager: Optional[LibraryManager] = None):
        """Initialize the profile installer."""
        self.logger = logging.getLogger(__name__)
        self.library_manager = library_manager or LibraryManager()
        
        # Default Amazon Q directories
        self.amazonq_contexts_dir = Path.home() / ".aws" / "amazonq" / "contexts"
        self.amazonq_agents_dir = Path.home() / ".aws" / "amazonq" / "cli-agents"
        
    def install_global_contexts(self) -> bool:
        """Install global contexts and create/update global_context.json."""
        try:
            # Ensure Amazon Q directories exist
            amazonq_dir = Path.home() / ".aws" / "amazonq"
            global_contexts_dir = amazonq_dir / "global-contexts"
            ensure_directory(amazonq_dir)
            ensure_directory(global_contexts_dir)
            
            # Get global contexts sorted by priority (highest first)
            global_contexts = self.library_manager.get_global_contexts()
            global_context_paths = []
            
            for global_context in global_contexts:
                global_context_path = self.library_manager.library_path / global_context.file_path
                if global_context_path.exists():
                    # Copy to ~/.aws/amazonq/global-contexts/ with original filename
                    dest_filename = Path(global_context.file_path).name
                    dest_path = global_contexts_dir / dest_filename
                    copy_file(global_context_path, dest_path)
                    global_context_paths.append(str(dest_path))
                    self.logger.info(f"Copied global context: {global_context.name}")
                else:
                    self.logger.warning(f"Global context file not found: {global_context_path}")
            
            # Create/update global_context.json
            global_context_json_path = amazonq_dir / "global_context.json"
            
            # Load existing global_context.json if it exists
            existing_global_context = {"paths": [], "hooks": {}}
            if global_context_json_path.exists():
                try:
                    with open(global_context_json_path, 'r', encoding='utf-8') as f:
                        existing_global_context = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Failed to load existing global_context.json: {e}")
            
            # Keep existing non-global-context paths and add global context paths
            existing_paths = existing_global_context.get("paths", [])
            # Filter out any existing global context paths (in case of reinstall)
            global_filenames = {Path(gc.file_path).name for gc in global_contexts}
            non_global_paths = [p for p in existing_paths 
                              if not (Path(p).parent.name == "global-contexts" and Path(p).name in global_filenames)]
            
            # Combine non-global paths with new global context paths
            all_paths = non_global_paths + global_context_paths
            
            global_context_config = {
                "paths": all_paths,
                "hooks": existing_global_context.get("hooks", {})
            }
            
            with open(global_context_json_path, 'w', encoding='utf-8') as f:
                json.dump(global_context_config, f, indent=2)
            
            self.logger.info(f"Updated global_context.json with {len(global_context_paths)} global contexts")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing global contexts: {e}")
            return False

    def install_profile(self, profile_id: str) -> bool:
        """Install a profile by copying its contexts and creating Q CLI agent configuration."""
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
            ensure_directory(self.amazonq_agents_dir)
            
            # Install global contexts first
            if not self.install_global_contexts():
                self.logger.warning("Failed to install global contexts, continuing with profile installation")
            
            # Copy profile-specific contexts
            context_resources = []
            contexts = profile_data.get('contexts', [])
            profile_dir = profile_path.parent
            
            for context_file in contexts:
                source_path = profile_dir / "contexts" / context_file
                if source_path.exists():
                    dest_path = self.amazonq_contexts_dir / f"{profile_id}_{context_file}"
                    copy_file(source_path, dest_path)
                    context_resources.append(f"file://{dest_path}")
                    self.logger.info(f"Copied context: {context_file}")
                else:
                    self.logger.warning(f"Context file not found: {source_path}")
            
            # Add global contexts to resources
            global_contexts = self.library_manager.get_global_contexts()
            global_contexts_dir = Path.home() / ".aws" / "amazonq" / "global-contexts"
            for global_context in global_contexts:
                dest_filename = Path(global_context.file_path).name
                dest_path = global_contexts_dir / dest_filename
                if dest_path.exists():
                    context_resources.append(f"file://{dest_path}")
            
            # Create agent configuration
            agent_config = AgentConfig(
                name=profile_id,
                description=config.description,
                resources=context_resources
            )
            
            # Save agent JSON
            agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
            with open(agent_json_path, 'w', encoding='utf-8') as f:
                json.dump(agent_config.dict(by_alias=True), f, indent=2)
            
            self.logger.info(f"Created Q CLI agent: {profile_id}")
            self.logger.info(f"Successfully installed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing profile '{profile_id}': {e}")
            return False
    
    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile by deleting its contexts and Q CLI agent configuration."""
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
                
            # Remove profile-specific contexts
            contexts = profile_data.get('contexts', [])
            
            for context_file in contexts:
                context_path = self.amazonq_contexts_dir / f"{profile_id}_{context_file}"
                if context_path.exists():
                    context_path.unlink()
                    self.logger.info(f"Removed context: {context_file}")
            
            # Remove agent JSON
            agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
            if agent_json_path.exists():
                agent_json_path.unlink()
                self.logger.info(f"Removed Q CLI agent: {profile_id}")
            
            self.logger.info(f"Successfully removed profile: {config.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing profile '{profile_id}': {e}")
            return False
    
    def remove_global_contexts(self) -> bool:
        """Remove global contexts and clean up global_context.json."""
        try:
            amazonq_dir = Path.home() / ".aws" / "amazonq"
            global_contexts_dir = amazonq_dir / "global-contexts"
            global_context_json_path = amazonq_dir / "global_context.json"
            
            # Get global contexts to remove
            global_contexts = self.library_manager.get_global_contexts()
            
            # Remove global context files from global-contexts folder
            for global_context in global_contexts:
                dest_filename = Path(global_context.file_path).name
                dest_path = global_contexts_dir / dest_filename
                if dest_path.exists():
                    dest_path.unlink()
                    self.logger.info(f"Removed global context: {global_context.name}")
            
            # Remove the global-contexts directory if it's empty
            if global_contexts_dir.exists() and not any(global_contexts_dir.iterdir()):
                global_contexts_dir.rmdir()
                self.logger.info("Removed empty global-contexts directory")
            
            # Update global_context.json to remove global context paths
            if global_context_json_path.exists():
                try:
                    with open(global_context_json_path, 'r', encoding='utf-8') as f:
                        existing_global_context = json.load(f)
                    
                    # Keep only non-global-context paths
                    existing_paths = existing_global_context.get("paths", [])
                    global_filenames = {Path(gc.file_path).name for gc in global_contexts}
                    non_global_paths = [p for p in existing_paths 
                                      if not (Path(p).parent.name == "global-contexts" and Path(p).name in global_filenames)]
                    
                    updated_config = {
                        "paths": non_global_paths,
                        "hooks": existing_global_context.get("hooks", {})
                    }
                    
                    with open(global_context_json_path, 'w', encoding='utf-8') as f:
                        json.dump(updated_config, f, indent=2)
                    
                    self.logger.info("Updated global_context.json to remove global context paths")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to update global_context.json: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing global contexts: {e}")
            return False

    def is_profile_installed(self, profile_id: str) -> bool:
        """Check if a profile is installed by looking for Q CLI agent JSON."""
        agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
        return agent_json_path.exists()
    
    def list_installed_profiles(self) -> List[str]:
        """List all installed profiles."""
        if not self.amazonq_agents_dir.exists():
            return []
            
        installed = []
        for agent_file in self.amazonq_agents_dir.glob("*.json"):
            if agent_file.name != "agent_config.json.example":  # Skip example file
                profile_id = agent_file.stem
                installed.append(profile_id)
            
        return installed
