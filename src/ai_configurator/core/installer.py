"""Installation system for Amazon Q CLI configurations."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..utils.logging import LoggerMixin
from .config_manager import ConfigurationManager
from .models import (
    GlobalContext,
    InstallationConfig,
    MCPConfiguration,
    MCPServerConfig,
    ProfileContext,
)
from .platform import PlatformManager


class InstallationManager(LoggerMixin):
    """Manages installation of Amazon Q CLI configurations."""
    
    def __init__(
        self, 
        platform_manager: Optional[PlatformManager] = None,
        config_manager: Optional[ConfigurationManager] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_manager = config_manager or ConfigurationManager(self.platform)
        
        # Get paths to template directories
        self.package_root = Path(__file__).parent.parent.parent.parent
        self.configs_dir = self.package_root / "configs"
        self.contexts_dir = self.package_root / "contexts"
        self.templates_dir = self.package_root / "templates"
        self.hooks_dir = self.package_root / "hooks"
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available installation profiles."""
        profiles_dir = self.configs_dir / "profiles"
        if not profiles_dir.exists():
            return []
        
        profiles = []
        for item in profiles_dir.iterdir():
            if item.is_dir() and (item / "context.json").exists():
                profiles.append(item.name)
        
        return sorted(profiles)
    
    def get_available_mcp_groups(self) -> List[str]:
        """Get list of available MCP server groups."""
        mcp_dir = self.configs_dir / "mcp-servers"
        if not mcp_dir.exists():
            return []
        
        groups = []
        for item in mcp_dir.iterdir():
            if item.is_file() and item.suffix == ".json":
                groups.append(item.stem)
        
        return sorted(groups)
    
    def load_mcp_group(self, group_name: str) -> Optional[Dict[str, MCPServerConfig]]:
        """Load MCP servers from a group configuration file."""
        mcp_file = self.configs_dir / "mcp-servers" / f"{group_name}.json"
        
        if not mcp_file.exists():
            self.logger.error(f"MCP group file not found: {mcp_file}")
            return None
        
        try:
            with open(mcp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse the MCP servers
            mcp_servers = {}
            for name, config in data.get("mcpServers", {}).items():
                mcp_servers[name] = MCPServerConfig(**config)
            
            return mcp_servers
        except Exception as e:
            self.logger.error(f"Failed to load MCP group {group_name}: {e}")
            return None
    
    def merge_mcp_configurations(self, groups: List[str]) -> MCPConfiguration:
        """Merge multiple MCP server groups into a single configuration."""
        merged_servers = {}
        
        for group in groups:
            servers = self.load_mcp_group(group)
            if servers:
                merged_servers.update(servers)
                self.logger.info(f"Loaded {len(servers)} MCP servers from group '{group}'")
        
        return MCPConfiguration(mcp_servers=merged_servers)
    
    def load_profile_template(self, profile_name: str) -> Optional[ProfileContext]:
        """Load a profile template."""
        profile_file = self.configs_dir / "profiles" / profile_name / "context.json"
        
        if not profile_file.exists():
            self.logger.error(f"Profile template not found: {profile_file}")
            return None
        
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProfileContext(**data)
        except Exception as e:
            self.logger.error(f"Failed to load profile template {profile_name}: {e}")
            return None
    
    def load_global_context_template(self) -> GlobalContext:
        """Load the global context template."""
        template_file = self.templates_dir / "global_context.json"
        
        if not template_file.exists():
            # Return default if template doesn't exist
            return GlobalContext()
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return GlobalContext(**data)
        except Exception as e:
            self.logger.warning(f"Failed to load global context template: {e}")
            return GlobalContext()
    
    def copy_context_files(self) -> bool:
        """Copy context files to the Amazon Q configuration directory."""
        if not self.contexts_dir.exists():
            self.logger.warning("No context files to copy")
            return True
        
        target_contexts_dir = self.config_manager.config_dir / "contexts"
        
        try:
            if target_contexts_dir.exists():
                shutil.rmtree(target_contexts_dir)
            
            shutil.copytree(self.contexts_dir, target_contexts_dir)
            self.logger.info(f"Context files copied to {target_contexts_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy context files: {e}")
            return False
    
    def copy_hooks(self) -> bool:
        """Copy hook files to the Amazon Q configuration directory."""
        if not self.hooks_dir.exists():
            self.logger.warning("No hook files to copy")
            return True
        
        target_hooks_dir = self.config_manager.config_dir / "hooks"
        
        try:
            if target_hooks_dir.exists():
                shutil.rmtree(target_hooks_dir)
            
            shutil.copytree(self.hooks_dir, target_hooks_dir)
            
            # Make hook scripts executable on Unix systems
            if not self.platform.is_windows():
                for hook_file in target_hooks_dir.rglob("*.sh"):
                    hook_file.chmod(0o755)
                for hook_file in target_hooks_dir.rglob("*.py"):
                    hook_file.chmod(0o755)
            
            self.logger.info(f"Hook files copied to {target_hooks_dir}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy hook files: {e}")
            return False
    
    def customize_configuration(self, config: InstallationConfig) -> bool:
        """Customize the configuration based on user environment."""
        # This method can be extended to customize configurations
        # based on the user's environment, detected tools, etc.
        
        # For now, we'll just log what we would customize
        self.logger.info("Customizing configuration for user environment...")
        
        # Example customizations:
        # - Detect user's email for Outlook MCP server
        # - Find local tool paths
        # - Set appropriate log levels
        # - Configure environment-specific settings
        
        return True
    
    def install(self, config: InstallationConfig) -> bool:
        """Install Amazon Q CLI configuration."""
        self.logger.info("Starting Amazon Q CLI configuration installation...")
        
        # Create backup if configuration exists and backup is requested
        if config.backup_before_install and self.config_manager.config_dir.exists():
            backup_id = self.config_manager.create_backup("Pre-installation backup")
            if backup_id:
                self.logger.info(f"Created backup: {backup_id}")
            else:
                self.logger.warning("Failed to create backup, continuing anyway...")
        
        try:
            # Ensure configuration directory exists
            self.config_manager.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Install MCP configuration
            mcp_groups = config.mcp_servers or ["core"]
            mcp_config = self.merge_mcp_configurations(mcp_groups)
            
            if not self.config_manager.save_mcp_config(mcp_config):
                self.logger.error("Failed to save MCP configuration")
                return False
            
            # Install global context
            global_context = self.load_global_context_template()
            if not self.config_manager.save_global_context(global_context):
                self.logger.error("Failed to save global context")
                return False
            
            # Install profile
            profile_name = config.profile or "default"
            profile_context = self.load_profile_template(profile_name)
            
            if profile_context:
                if not self.config_manager.save_profile_context(profile_name, profile_context):
                    self.logger.error(f"Failed to save profile context for {profile_name}")
                    return False
            else:
                # Create default profile if template not found
                default_context = ProfileContext()
                if not self.config_manager.save_profile_context(profile_name, default_context):
                    self.logger.error(f"Failed to create default profile {profile_name}")
                    return False
            
            # Copy context files
            if not self.copy_context_files():
                self.logger.warning("Failed to copy context files, continuing...")
            
            # Copy hooks
            if not self.copy_hooks():
                self.logger.warning("Failed to copy hook files, continuing...")
            
            # Customize configuration
            if not self.customize_configuration(config):
                self.logger.warning("Configuration customization failed, continuing...")
            
            self.logger.info("Amazon Q CLI configuration installation completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return False
    
    def get_installation_summary(self, config: InstallationConfig) -> Dict[str, any]:
        """Get a summary of what would be installed."""
        summary = {
            "profile": config.profile or "default",
            "mcp_groups": config.mcp_servers or ["core"],
            "mcp_servers": [],
            "context_files": [],
            "hooks": [],
            "backup_before_install": config.backup_before_install,
            "force": config.force
        }
        
        # Get MCP servers that would be installed
        for group in summary["mcp_groups"]:
            servers = self.load_mcp_group(group)
            if servers:
                summary["mcp_servers"].extend(servers.keys())
        
        # Get context files
        if self.contexts_dir.exists():
            for context_file in self.contexts_dir.rglob("*.md"):
                summary["context_files"].append(str(context_file.relative_to(self.contexts_dir)))
        
        # Get hooks
        if self.hooks_dir.exists():
            for hook_file in self.hooks_dir.iterdir():
                if hook_file.is_file():
                    summary["hooks"].append(hook_file.name)
        
        return summary
