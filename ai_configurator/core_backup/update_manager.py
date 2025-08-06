"""Update and maintenance system for Amazon Q CLI configurations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..utils.logging import LoggerMixin
from .config_manager import ConfigurationManager
from .installer import InstallationManager
from .models import InstallationConfig, MCPConfiguration, MCPServerConfig
from .platform_utils import PlatformManager


class UpdateManager(LoggerMixin):
    """Manages configuration updates and maintenance."""
    
    def __init__(
        self,
        platform_manager: Optional[PlatformManager] = None,
        config_manager: Optional[ConfigurationManager] = None,
        installer: Optional[InstallationManager] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_manager = config_manager or ConfigurationManager(self.platform)
        self.installer = installer or InstallationManager(self.platform, self.config_manager)
    
    def check_for_updates(self) -> Dict[str, any]:
        """Check for available updates to configurations and templates."""
        update_info = {
            "templates_available": False,
            "mcp_updates": [],
            "profile_updates": [],
            "context_updates": [],
            "hook_updates": [],
            "recommendations": []
        }
        
        # Check if template directory exists (indicates updates available)
        if self.installer.configs_dir.exists():
            update_info["templates_available"] = True
        
        # Check for MCP server updates
        current_mcp = self.config_manager.load_mcp_config()
        if current_mcp:
            update_info["mcp_updates"] = self._check_mcp_updates(current_mcp)
        
        # Check for profile updates
        current_profiles = self.config_manager.list_profiles()
        available_profiles = self.installer.get_available_profiles()
        
        for profile in available_profiles:
            if profile not in current_profiles:
                update_info["profile_updates"].append({
                    "profile": profile,
                    "status": "new",
                    "action": "install"
                })
            else:
                # Check if profile template is newer
                template_context = self.installer.load_profile_template(profile)
                current_context = self.config_manager.load_profile_context(profile)
                
                if template_context and current_context:
                    if template_context.paths != current_context.paths:
                        update_info["profile_updates"].append({
                            "profile": profile,
                            "status": "modified",
                            "action": "update",
                            "changes": self._compare_profile_contexts(current_context, template_context)
                        })
        
        # Check for context file updates
        update_info["context_updates"] = self._check_context_updates()
        
        # Check for hook updates
        update_info["hook_updates"] = self._check_hook_updates()
        
        # Generate recommendations
        if update_info["mcp_updates"]:
            update_info["recommendations"].append(
                f"Update {len(update_info['mcp_updates'])} MCP server configurations"
            )
        
        if update_info["profile_updates"]:
            update_info["recommendations"].append(
                f"Update {len(update_info['profile_updates'])} profile configurations"
            )
        
        if update_info["context_updates"]:
            update_info["recommendations"].append(
                f"Update {len(update_info['context_updates'])} context files"
            )
        
        return update_info
    
    def _check_mcp_updates(self, current_mcp: MCPConfiguration) -> List[Dict[str, any]]:
        """Check for MCP server configuration updates."""
        updates = []
        
        # Get available MCP groups
        available_groups = self.installer.get_available_mcp_groups()
        
        for group in available_groups:
            template_servers = self.installer.load_mcp_group(group)
            if not template_servers:
                continue
            
            for server_name, template_config in template_servers.items():
                if server_name in current_mcp.mcp_servers:
                    current_config = current_mcp.mcp_servers[server_name]
                    
                    # Compare configurations
                    changes = self._compare_mcp_configs(current_config, template_config)
                    if changes:
                        updates.append({
                            "server": server_name,
                            "group": group,
                            "status": "modified",
                            "changes": changes
                        })
                else:
                    updates.append({
                        "server": server_name,
                        "group": group,
                        "status": "new",
                        "changes": ["Server not installed"]
                    })
        
        return updates
    
    def _compare_mcp_configs(self, current: MCPServerConfig, template: MCPServerConfig) -> List[str]:
        """Compare MCP server configurations and return list of changes."""
        changes = []
        
        if current.command != template.command:
            changes.append(f"Command: '{current.command}' → '{template.command}'")
        
        if current.args != template.args:
            changes.append(f"Args: {current.args} → {template.args}")
        
        if current.env != template.env:
            changes.append(f"Environment variables changed")
        
        if current.disabled != template.disabled:
            status = "disabled" if template.disabled else "enabled"
            changes.append(f"Status changed to {status}")
        
        return changes
    
    def _compare_profile_contexts(self, current, template) -> List[str]:
        """Compare profile contexts and return list of changes."""
        changes = []
        
        current_paths = set(current.paths)
        template_paths = set(template.paths)
        
        added = template_paths - current_paths
        removed = current_paths - template_paths
        
        if added:
            changes.append(f"Added paths: {list(added)}")
        
        if removed:
            changes.append(f"Removed paths: {list(removed)}")
        
        return changes
    
    def _check_context_updates(self) -> List[Dict[str, any]]:
        """Check for context file updates."""
        updates = []
        
        if not self.installer.contexts_dir.exists():
            return updates
        
        current_contexts_dir = self.config_manager.config_dir / "contexts"
        
        # Compare context files
        for template_file in self.installer.contexts_dir.rglob("*.md"):
            relative_path = template_file.relative_to(self.installer.contexts_dir)
            current_file = current_contexts_dir / relative_path
            
            if not current_file.exists():
                updates.append({
                    "file": str(relative_path),
                    "status": "new",
                    "action": "install"
                })
            else:
                # Compare file contents
                try:
                    template_content = template_file.read_text(encoding='utf-8')
                    current_content = current_file.read_text(encoding='utf-8')
                    
                    if template_content != current_content:
                        updates.append({
                            "file": str(relative_path),
                            "status": "modified",
                            "action": "update"
                        })
                except Exception as e:
                    self.logger.warning(f"Failed to compare context file {relative_path}: {e}")
        
        return updates
    
    def _check_hook_updates(self) -> List[Dict[str, any]]:
        """Check for hook file updates."""
        updates = []
        
        if not self.installer.hooks_dir.exists():
            return updates
        
        current_hooks_dir = self.config_manager.config_dir / "hooks"
        
        # Compare hook files
        for template_file in self.installer.hooks_dir.iterdir():
            if template_file.is_file():
                current_file = current_hooks_dir / template_file.name
                
                if not current_file.exists():
                    updates.append({
                        "file": template_file.name,
                        "status": "new",
                        "action": "install"
                    })
                else:
                    # Compare file contents
                    try:
                        template_content = template_file.read_text(encoding='utf-8')
                        current_content = current_file.read_text(encoding='utf-8')
                        
                        if template_content != current_content:
                            updates.append({
                                "file": template_file.name,
                                "status": "modified",
                                "action": "update"
                            })
                    except Exception as e:
                        self.logger.warning(f"Failed to compare hook file {template_file.name}: {e}")
        
        return updates
    
    def update_configuration(
        self, 
        preserve_personal: bool = True,
        selective_update: Optional[List[str]] = None
    ) -> bool:
        """Update configuration with preservation options."""
        self.logger.info("Starting configuration update...")
        
        # Create backup before update
        backup_id = self.config_manager.create_backup("Pre-update backup")
        if not backup_id:
            self.logger.error("Failed to create backup - aborting update")
            return False
        
        try:
            # Get current state
            current_profiles = self.config_manager.list_profiles()
            current_mcp = self.config_manager.load_mcp_config()
            
            # Preserve personal configurations if requested
            preserved_data = {}
            if preserve_personal:
                preserved_data = self._preserve_personal_configs()
            
            # Perform selective or full update
            if selective_update:
                success = self._perform_selective_update(selective_update)
            else:
                success = self._perform_full_update()
            
            if not success:
                self.logger.error("Update failed - restoring from backup")
                self.config_manager.restore_backup(backup_id)
                return False
            
            # Restore personal configurations
            if preserve_personal and preserved_data:
                self._restore_personal_configs(preserved_data)
            
            self.logger.info("Configuration update completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Update failed with error: {e}")
            self.logger.info("Restoring from backup...")
            self.config_manager.restore_backup(backup_id)
            return False
    
    def _preserve_personal_configs(self) -> Dict[str, any]:
        """Preserve personal configurations before update."""
        preserved = {
            "all_mcp_servers": {},  # Changed: preserve ALL MCP servers
            "custom_profiles": {},
            "personal_contexts": [],
            "custom_hooks": []
        }
        
        # Preserve ALL MCP servers (not just custom ones)
        # This fixes the bug where personal MCP servers were being lost
        current_mcp = self.config_manager.load_mcp_config()
        if current_mcp:
            # Store ALL current MCP servers to prevent data loss
            for server_name, config in current_mcp.mcp_servers.items():
                preserved["all_mcp_servers"][server_name] = config
                self.logger.debug(f"Preserving MCP server: {server_name}")
        
        # Preserve custom profiles
        current_profiles = self.config_manager.list_profiles()
        available_profiles = self.installer.get_available_profiles()
        
        for profile in current_profiles:
            if profile not in available_profiles:
                context = self.config_manager.load_profile_context(profile)
                if context:
                    preserved["custom_profiles"][profile] = context
        
        # Preserve personal context files (not in templates)
        current_contexts_dir = self.config_manager.config_dir / "contexts"
        if current_contexts_dir.exists() and self.installer.contexts_dir.exists():
            template_files = set()
            for template_file in self.installer.contexts_dir.rglob("*.md"):
                template_files.add(template_file.relative_to(self.installer.contexts_dir))
            
            for context_file in current_contexts_dir.rglob("*.md"):
                relative_path = context_file.relative_to(current_contexts_dir)
                if relative_path not in template_files:
                    preserved["personal_contexts"].append({
                        "path": str(relative_path),
                        "content": context_file.read_text(encoding='utf-8')
                    })
        
        return preserved
    
    def _restore_personal_configs(self, preserved_data: Dict[str, any]) -> None:
        """Restore personal configurations after update."""
        # Restore ALL MCP servers (fixes the preservation bug)
        if preserved_data.get("all_mcp_servers"):
            current_mcp = self.config_manager.load_mcp_config()
            if current_mcp:
                # Merge preserved servers with any new template servers
                # This ensures we keep all existing servers while adding new ones
                for server_name, config in preserved_data["all_mcp_servers"].items():
                    current_mcp.mcp_servers[server_name] = config
                    self.logger.debug(f"Restored MCP server: {server_name}")
                self.config_manager.save_mcp_config(current_mcp)
        
        # Fallback for old preservation format (backward compatibility)
        elif preserved_data.get("custom_mcp_servers"):
            current_mcp = self.config_manager.load_mcp_config()
            if current_mcp:
                current_mcp.mcp_servers.update(preserved_data["custom_mcp_servers"])
                self.config_manager.save_mcp_config(current_mcp)
        
        # Restore custom profiles
        for profile_name, context in preserved_data["custom_profiles"].items():
            self.config_manager.save_profile_context(profile_name, context)
        
        # Restore personal context files
        contexts_dir = self.config_manager.config_dir / "contexts"
        for context_info in preserved_data["personal_contexts"]:
            context_file = contexts_dir / context_info["path"]
            context_file.parent.mkdir(parents=True, exist_ok=True)
            context_file.write_text(context_info["content"], encoding='utf-8')
    
    def _perform_full_update(self) -> bool:
        """Perform a full configuration update."""
        try:
            # Get current active profile to maintain it
            current_profile = self.config_manager.get_active_profile() or "default"
            
            # Update components individually to avoid destructive overwrite
            success = True
            
            # Update MCP servers (merge with existing)
            if not self._update_mcp_servers():
                success = False
                
            # Update profiles (preserve existing)
            if not self._update_profiles():
                success = False
                
            # Update contexts (preserve personal ones)
            if not self._update_contexts():
                success = False
                
            # Update hooks (preserve custom ones)
            if not self._update_hooks():
                success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Full update failed: {e}")
            return False
    
    def _perform_selective_update(self, components: List[str]) -> bool:
        """Perform selective update of specific components."""
        success = True
        
        for component in components:
            if component == "mcp":
                if not self._update_mcp_servers():
                    success = False
            elif component == "profiles":
                if not self._update_profiles():
                    success = False
            elif component == "contexts":
                if not self._update_contexts():
                    success = False
            elif component == "hooks":
                if not self._update_hooks():
                    success = False
            else:
                self.logger.warning(f"Unknown component for selective update: {component}")
        
        return success
    
    def _update_mcp_servers(self) -> bool:
        """Update MCP server configurations by merging with existing."""
        try:
            # Load current MCP configuration
            current_mcp = self.config_manager.load_mcp_config()
            if not current_mcp:
                # If no current config, create new one with core servers
                mcp_groups = ["core"]
                mcp_config = self.installer.merge_mcp_configurations(mcp_groups)
                return self.config_manager.save_mcp_config(mcp_config)
            
            # Get template servers from core group
            core_servers = self.installer.load_mcp_group("core")
            if core_servers:
                # Merge template servers with existing ones
                # Template servers will update existing ones, but won't remove custom ones
                for server_name, server_config in core_servers.items():
                    current_mcp.mcp_servers[server_name] = server_config
                    self.logger.debug(f"Updated template MCP server: {server_name}")
            
            return self.config_manager.save_mcp_config(current_mcp)
            
        except Exception as e:
            self.logger.error(f"Failed to update MCP servers: {e}")
            return False
    
    def _update_profiles(self) -> bool:
        """Update profile configurations."""
        try:
            available_profiles = self.installer.get_available_profiles()
            current_profiles = self.config_manager.list_profiles()
            
            for profile in available_profiles:
                if profile in current_profiles:
                    # Update existing profile
                    template_context = self.installer.load_profile_template(profile)
                    if template_context:
                        self.config_manager.save_profile_context(profile, template_context)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update profiles: {e}")
            return False
    
    def _update_contexts(self) -> bool:
        """Update context files."""
        try:
            return self.installer.copy_context_files()
        except Exception as e:
            self.logger.error(f"Failed to update contexts: {e}")
            return False
    
    def _update_hooks(self) -> bool:
        """Update hook files."""
        try:
            return self.installer.copy_hooks()
        except Exception as e:
            self.logger.error(f"Failed to update hooks: {e}")
            return False
    
    def cleanup_old_files(self) -> Dict[str, any]:
        """Clean up old and unused configuration files."""
        cleanup_result = {
            "removed_files": [],
            "freed_space": 0,
            "errors": []
        }
        
        # Clean up old backup files (keep only last 10)
        try:
            backups = self.config_manager.list_backups()
            if len(backups) > 10:
                old_backups = backups[10:]  # Keep first 10 (most recent)
                
                for backup in old_backups:
                    backup_path = self.config_manager.backup_dir / backup.backup_id
                    if backup_path.exists():
                        size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
                        shutil.rmtree(backup_path)
                        cleanup_result["removed_files"].append(f"backup/{backup.backup_id}")
                        cleanup_result["freed_space"] += size
        except Exception as e:
            cleanup_result["errors"].append(f"Failed to clean up old backups: {e}")
        
        # Clean up cache files
        cache_dir = self.config_manager.config_dir / "cache"
        if cache_dir.exists():
            try:
                for cache_file in cache_dir.rglob("*.tmp"):
                    if cache_file.is_file():
                        size = cache_file.stat().st_size
                        cache_file.unlink()
                        cleanup_result["removed_files"].append(f"cache/{cache_file.name}")
                        cleanup_result["freed_space"] += size
            except Exception as e:
                cleanup_result["errors"].append(f"Failed to clean up cache files: {e}")
        
        return cleanup_result
    
    def get_maintenance_status(self) -> Dict[str, any]:
        """Get overall maintenance status and recommendations."""
        status = {
            "last_update": None,
            "backup_count": 0,
            "config_health": "unknown",
            "disk_usage": 0,
            "recommendations": []
        }
        
        # Check last update (from backup timestamps)
        backups = self.config_manager.list_backups()
        if backups:
            status["backup_count"] = len(backups)
            # Find most recent non-automatic backup
            for backup in backups:
                if "update" not in backup.description.lower():
                    status["last_update"] = backup.timestamp
                    break
        
        # Check configuration health
        validation = self.config_manager.validate_configuration()
        if validation.is_valid:
            status["config_health"] = "good"
        elif validation.errors:
            status["config_health"] = "poor"
        else:
            status["config_health"] = "fair"
        
        # Calculate disk usage
        if self.config_manager.config_dir.exists():
            try:
                status["disk_usage"] = sum(
                    f.stat().st_size for f in self.config_manager.config_dir.rglob('*') 
                    if f.is_file()
                )
            except Exception:
                pass
        
        # Generate recommendations
        if status["backup_count"] > 20:
            status["recommendations"].append("Consider cleaning up old backups")
        
        if status["config_health"] != "good":
            status["recommendations"].append("Run configuration validation and fix issues")
        
        if status["disk_usage"] > 100 * 1024 * 1024:  # 100MB
            status["recommendations"].append("Configuration directory is large - consider cleanup")
        
        if not status["last_update"]:
            status["recommendations"].append("No recent updates found - consider checking for updates")
        
        return status
