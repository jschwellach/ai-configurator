"""
Agent-based Profile Installer for AI Configurator.
Creates Amazon Q CLI agents instead of copying contexts.
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Optional, List

from .config_library_manager import ConfigLibraryManager
from .catalog_schema import AgentConfig
from .file_utils import ensure_directory


class AgentInstaller:
    """Agent-based profile installer for AI Configurator."""
    
    def __init__(self, library_manager: Optional[ConfigLibraryManager] = None):
        """Initialize the agent installer."""
        self.logger = logging.getLogger(__name__)
        self.library_manager = library_manager or ConfigLibraryManager()
        
        # Amazon Q CLI agent directory
        self.amazonq_agents_dir = Path.home() / ".aws" / "amazonq" / "cli-agents"
        
    def install_profile(self, profile_id: str) -> bool:
        """Install a profile by creating an Amazon Q CLI agent configuration."""
        try:
            # Get profile configuration
            profile = self.library_manager.get_profile_by_id(profile_id)
            if not profile:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
                
            # Get profile file path
            profile_path = self.library_manager.get_profile_file_path(profile_id)
            if not profile_path or not profile_path.exists():
                self.logger.error(f"Profile file not found: {profile_path}")
                return False
                
            # Load profile YAML
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = yaml.safe_load(f)
                
            # Ensure Amazon Q agents directory exists
            ensure_directory(self.amazonq_agents_dir)
            
            # Build resource list
            resources = []
            
            # Add base contexts first (our "organizational contexts")
            base_contexts = self.library_manager.get_base_contexts()
            for base_context in base_contexts:
                base_context_path = self.library_manager.get_base_context_file_path(base_context)
                if base_context_path.exists():
                    resources.append(f"file://{base_context_path.absolute()}")
                    self.logger.info(f"Added base context: {base_context.name}")
                else:
                    self.logger.warning(f"Base context file not found: {base_context_path}")
            
            # Add profile-specific contexts
            contexts = profile_data.get('contexts', [])
            profile_dir = profile_path.parent
            
            for context_file in contexts:
                context_path = profile_dir / "contexts" / context_file
                if context_path.exists():
                    resources.append(f"file://{context_path.absolute()}")
                    self.logger.info(f"Added profile context: {context_file}")
                else:
                    self.logger.warning(f"Profile context file not found: {context_path}")
            
            # Create agent configuration
            agent_config = AgentConfig(
                name=profile_id,
                description=profile.description,
                resources=resources,
                tools=["*"],  # Allow all tools as per user preference
                allowedTools=["fs_read"],  # Pre-approve read operations for better UX
            )
            
            # Save agent JSON
            agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
            with open(agent_json_path, 'w', encoding='utf-8') as f:
                json.dump(agent_config.dict(by_alias=True), f, indent=2)
            
            self.logger.info(f"Created Amazon Q CLI agent: {profile_id}")
            self.logger.info(f"Agent file: {agent_json_path}")
            self.logger.info(f"To use: q chat --agent {profile_id}")
            self.logger.info(f"Successfully installed profile: {profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing profile '{profile_id}': {e}")
            return False
    
    def remove_profile(self, profile_id: str) -> bool:
        """Remove a profile by deleting its Amazon Q CLI agent configuration."""
        try:
            # Get profile configuration for logging
            profile = self.library_manager.get_profile_by_id(profile_id)
            if not profile:
                self.logger.error(f"Profile '{profile_id}' not found")
                return False
            
            # Remove agent JSON
            agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
            if agent_json_path.exists():
                agent_json_path.unlink()
                self.logger.info(f"Removed Amazon Q CLI agent: {profile_id}")
            else:
                self.logger.warning(f"Agent file not found: {agent_json_path}")
            
            self.logger.info(f"Successfully removed profile: {profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing profile '{profile_id}': {e}")
            return False
    
    def list_installed_agents(self) -> List[str]:
        """List all installed Amazon Q CLI agents."""
        try:
            if not self.amazonq_agents_dir.exists():
                return []
                
            agent_files = list(self.amazonq_agents_dir.glob("*.json"))
            return [f.stem for f in agent_files]
            
        except Exception as e:
            self.logger.error(f"Error listing installed agents: {e}")
            return []
    
    def is_profile_installed(self, profile_id: str) -> bool:
        """Check if a profile is installed as an agent."""
        agent_json_path = self.amazonq_agents_dir / f"{profile_id}.json"
        return agent_json_path.exists()
    
    def validate_agent_config(self, agent_config: AgentConfig) -> bool:
        """Validate an agent configuration (basic validation for now)."""
        try:
            # Check required fields
            if not agent_config.name:
                self.logger.error("Agent name is required")
                return False
                
            # Validate resource paths
            for resource in agent_config.resources:
                if not resource.startswith("file://"):
                    self.logger.error(f"Resource must start with 'file://': {resource}")
                    return False
                    
                # Check if file exists
                file_path = Path(resource[7:])  # Remove 'file://' prefix
                if not file_path.exists():
                    self.logger.warning(f"Resource file not found: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating agent config: {e}")
            return False
