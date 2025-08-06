"""Backward compatibility support for existing configurations during library migration."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import yaml
from rich.console import Console

from .models import ConfigurationError
from ..utils.logging import LoggerMixin

console = Console()


class BackwardCompatibilityManager(LoggerMixin):
    """Manages backward compatibility during transition to library-based architecture."""
    
    def __init__(self, workspace_root: Path, user_config_dir: Optional[Path] = None):
        self.workspace_root = workspace_root
        self.user_config_dir = user_config_dir or Path.home() / ".kiro"
        
        # Old structure paths
        self.old_configs_dir = workspace_root / "configs"
        self.old_contexts_dir = workspace_root / "contexts"
        self.old_hooks_dir = workspace_root / "hooks"
        
        # New library structure
        self.library_dir = workspace_root / "library"
        
        # User configuration directory
        self.user_contexts_dir = self.user_config_dir / "contexts"
        self.user_profiles_dir = self.user_config_dir / "profiles"
        self.user_hooks_dir = self.user_config_dir / "hooks"
        self.user_mcp_dir = self.user_config_dir / "mcp-servers"
    
    def check_migration_status(self) -> Dict[str, Any]:
        """Check the current migration status and what needs to be done."""
        status = {
            "has_old_structure": False,
            "has_library_structure": False,
            "has_user_configs": False,
            "migration_needed": False,
            "old_config_count": 0,
            "library_config_count": 0,
            "user_config_count": 0,
            "recommendations": []
        }
        
        # Check for old structure
        old_configs = self._count_old_configurations()
        if old_configs > 0:
            status["has_old_structure"] = True
            status["old_config_count"] = old_configs
        
        # Check for library structure
        library_configs = self._count_library_configurations()
        if library_configs > 0:
            status["has_library_structure"] = True
            status["library_config_count"] = library_configs
        
        # Check for user configurations
        user_configs = self._count_user_configurations()
        if user_configs > 0:
            status["has_user_configs"] = True
            status["user_config_count"] = user_configs
        
        # Determine if migration is needed
        if status["has_old_structure"] and not status["has_library_structure"]:
            status["migration_needed"] = True
            status["recommendations"].append(
                "Run 'ai-config migrate to-library' to migrate old configurations to library structure"
            )
        
        if status["has_old_structure"] and status["has_library_structure"]:
            status["recommendations"].append(
                "Both old and new structures exist. Consider cleaning up old structure after verifying migration"
            )
        
        if not status["has_library_structure"] and not status["has_old_structure"]:
            status["recommendations"].append(
                "No configurations found. Start by browsing the library: 'ai-config browse'"
            )
        
        return status
    
    def ensure_user_config_directories(self):
        """Ensure user configuration directories exist."""
        directories = [
            self.user_config_dir,
            self.user_contexts_dir,
            self.user_profiles_dir,
            self.user_hooks_dir,
            self.user_mcp_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    def get_configuration_sources(self, config_type: str) -> List[Path]:
        """Get all possible sources for a configuration type in priority order."""
        sources = []
        
        if config_type == "contexts":
            # Priority: user configs -> library -> old structure
            if self.user_contexts_dir.exists():
                sources.append(self.user_contexts_dir)
            if self.library_dir.exists():
                sources.extend([
                    self.library_dir / "contexts" / subdir
                    for subdir in ["development", "networking", "productivity", "engagement", "aws", "research", "general"]
                    if (self.library_dir / "contexts" / subdir).exists()
                ])
            if self.old_contexts_dir.exists():
                sources.append(self.old_contexts_dir)
        
        elif config_type == "profiles":
            if self.user_profiles_dir.exists():
                sources.append(self.user_profiles_dir)
            if (self.library_dir / "profiles").exists():
                sources.append(self.library_dir / "profiles")
            if (self.old_configs_dir / "profiles").exists():
                sources.append(self.old_configs_dir / "profiles")
        
        elif config_type == "hooks":
            if self.user_hooks_dir.exists():
                sources.append(self.user_hooks_dir)
            if self.library_dir.exists():
                sources.extend([
                    self.library_dir / "hooks" / subdir
                    for subdir in ["development", "productivity", "engagement", "maintenance", "general"]
                    if (self.library_dir / "hooks" / subdir).exists()
                ])
            if self.old_hooks_dir.exists():
                sources.append(self.old_hooks_dir)
        
        elif config_type == "mcp-servers":
            if self.user_mcp_dir.exists():
                sources.append(self.user_mcp_dir)
            if (self.library_dir / "mcp-servers").exists():
                sources.append(self.library_dir / "mcp-servers")
            if (self.old_configs_dir / "mcp-servers").exists():
                sources.append(self.old_configs_dir / "mcp-servers")
        
        return [source for source in sources if source.exists()]
    
    def find_configuration_file(self, config_name: str, config_type: str) -> Optional[Path]:
        """Find a configuration file by name, checking all possible sources."""
        sources = self.get_configuration_sources(config_type)
        
        # Common file extensions by type
        extensions = {
            "contexts": [".md"],
            "profiles": [".yaml", ".yml", ".json"],
            "hooks": [".yaml", ".yml", ".py"],
            "mcp-servers": [".json", ".yaml", ".yml"]
        }
        
        for source in sources:
            if config_type == "profiles" and source.name == "profiles" and (self.old_configs_dir / "profiles") in sources:
                # Handle old profile structure (directories with context.json)
                profile_dir = source / config_name
                if profile_dir.is_dir():
                    context_file = profile_dir / "context.json"
                    if context_file.exists():
                        return context_file
            else:
                # Handle file-based configurations
                for ext in extensions.get(config_type, [""]):
                    config_file = source / f"{config_name}{ext}"
                    if config_file.exists():
                        return config_file
                    
                    # Also check in subdirectories for library structure
                    if source.is_dir():
                        for subdir in source.iterdir():
                            if subdir.is_dir():
                                config_file = subdir / f"{config_name}{ext}"
                                if config_file.exists():
                                    return config_file
        
        return None
    
    def list_available_configurations(self, config_type: str) -> Dict[str, Dict[str, Any]]:
        """List all available configurations of a given type from all sources."""
        configurations = {}
        sources = self.get_configuration_sources(config_type)
        
        for source in sources:
            source_name = self._get_source_name(source)
            
            if config_type == "contexts":
                configs = self._list_context_files(source)
            elif config_type == "profiles":
                configs = self._list_profile_files(source)
            elif config_type == "hooks":
                configs = self._list_hook_files(source)
            elif config_type == "mcp-servers":
                configs = self._list_mcp_files(source)
            else:
                configs = {}
            
            for config_name, config_info in configs.items():
                if config_name not in configurations:
                    configurations[config_name] = config_info
                    configurations[config_name]["source"] = source_name
                    configurations[config_name]["path"] = str(config_info["path"])
                else:
                    # Configuration exists in multiple sources, note the conflict
                    if "conflicts" not in configurations[config_name]:
                        configurations[config_name]["conflicts"] = [configurations[config_name]["source"]]
                    configurations[config_name]["conflicts"].append(source_name)
        
        return configurations
    
    def create_migration_guide(self) -> str:
        """Create a migration guide for users."""
        status = self.check_migration_status()
        
        guide = """# AI Configurator Migration Guide

## Current Status
"""
        
        if status["has_old_structure"]:
            guide += f"- ✅ Old configuration structure found ({status['old_config_count']} configurations)\n"
        else:
            guide += "- ⚪ No old configuration structure found\n"
        
        if status["has_library_structure"]:
            guide += f"- ✅ Library structure found ({status['library_config_count']} configurations)\n"
        else:
            guide += "- ⚪ No library structure found\n"
        
        if status["has_user_configs"]:
            guide += f"- ✅ User configurations found ({status['user_config_count']} configurations)\n"
        else:
            guide += "- ⚪ No user configurations found\n"
        
        guide += "\n## Recommendations\n\n"
        
        for i, recommendation in enumerate(status["recommendations"], 1):
            guide += f"{i}. {recommendation}\n"
        
        guide += """
## Migration Steps

### Step 1: Backup Your Configurations
```bash
# Create a backup before migration
ai-config migrate to-library --dry-run  # Preview what will be migrated
ai-config migrate to-library            # Perform migration with automatic backup
```

### Step 2: Verify Migration
```bash
# Check library structure
ai-config library refresh
ai-config browse

# Validate migrated configurations
ai-config migrate library-validate
```

### Step 3: Test Your Setup
```bash
# Test installing configurations from library
ai-config install <configuration-name>

# List installed configurations
ai-config list
```

### Step 4: Clean Up (Optional)
```bash
# After verifying everything works, clean up old structure
ai-config migrate cleanup --dry-run  # Preview cleanup
ai-config migrate cleanup            # Remove old files
```

## Backward Compatibility

During the transition period:
- Existing configurations will continue to work
- The system will check multiple locations for configurations
- Priority order: User configs → Library → Old structure
- You can gradually migrate configurations at your own pace

## Getting Help

If you encounter issues:
1. Check migration status: `ai-config migrate library-discover`
2. Validate configurations: `ai-config migrate library-validate`
3. Rollback if needed: `ai-config migrate library-rollback <backup-id>`

For more help, see the documentation or create an issue on GitHub.
"""
        
        return guide
    
    def _count_old_configurations(self) -> int:
        """Count configurations in old structure."""
        count = 0
        
        # Count contexts
        if self.old_contexts_dir.exists():
            count += len(list(self.old_contexts_dir.glob("*.md")))
        
        # Count profiles
        if (self.old_configs_dir / "profiles").exists():
            profiles_dir = self.old_configs_dir / "profiles"
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir() and (profile_dir / "context.json").exists():
                    count += 1
        
        # Count hooks
        if self.old_hooks_dir.exists():
            count += len(list(self.old_hooks_dir.glob("*.py")))
            count += len(list(self.old_hooks_dir.glob("*.yaml")))
        
        # Count MCP servers
        if (self.old_configs_dir / "mcp-servers").exists():
            count += len(list((self.old_configs_dir / "mcp-servers").glob("*.json")))
        
        return count
    
    def _count_library_configurations(self) -> int:
        """Count configurations in library structure."""
        count = 0
        
        if not self.library_dir.exists():
            return 0
        
        # Count contexts
        contexts_dir = self.library_dir / "contexts"
        if contexts_dir.exists():
            count += len(list(contexts_dir.rglob("*.md")))
        
        # Count profiles
        profiles_dir = self.library_dir / "profiles"
        if profiles_dir.exists():
            count += len(list(profiles_dir.glob("*.yaml")))
            count += len(list(profiles_dir.glob("*.yml")))
        
        # Count hooks
        hooks_dir = self.library_dir / "hooks"
        if hooks_dir.exists():
            count += len(list(hooks_dir.rglob("*.yaml")))
            count += len(list(hooks_dir.rglob("*.yml")))
            count += len(list(hooks_dir.rglob("*.py")))
        
        # Count MCP servers
        mcp_dir = self.library_dir / "mcp-servers"
        if mcp_dir.exists():
            count += len(list(mcp_dir.glob("*.json")))
        
        return count
    
    def _count_user_configurations(self) -> int:
        """Count configurations in user directory."""
        count = 0
        
        # Count contexts
        if self.user_contexts_dir.exists():
            count += len(list(self.user_contexts_dir.glob("*.md")))
        
        # Count profiles
        if self.user_profiles_dir.exists():
            count += len(list(self.user_profiles_dir.glob("*.yaml")))
            count += len(list(self.user_profiles_dir.glob("*.yml")))
        
        # Count hooks
        if self.user_hooks_dir.exists():
            count += len(list(self.user_hooks_dir.glob("*.yaml")))
            count += len(list(self.user_hooks_dir.glob("*.yml")))
            count += len(list(self.user_hooks_dir.glob("*.py")))
        
        # Count MCP servers
        if self.user_mcp_dir.exists():
            count += len(list(self.user_mcp_dir.glob("*.json")))
        
        return count
    
    def _get_source_name(self, source: Path) -> str:
        """Get a human-readable name for a configuration source."""
        if self.user_config_dir in source.parents or source == self.user_config_dir:
            return "user"
        elif self.library_dir in source.parents or source == self.library_dir:
            return "library"
        elif self.workspace_root in source.parents:
            return "old-structure"
        else:
            return "unknown"
    
    def _list_context_files(self, source: Path) -> Dict[str, Dict[str, Any]]:
        """List context files in a source directory."""
        contexts = {}
        
        if source.is_dir():
            for md_file in source.rglob("*.md"):
                name = md_file.stem
                contexts[name] = {
                    "name": name,
                    "path": md_file,
                    "type": "context",
                    "format": "markdown"
                }
        
        return contexts
    
    def _list_profile_files(self, source: Path) -> Dict[str, Dict[str, Any]]:
        """List profile files in a source directory."""
        profiles = {}
        
        if source.is_dir():
            # Handle YAML/JSON files
            for ext in ["*.yaml", "*.yml", "*.json"]:
                for profile_file in source.glob(ext):
                    name = profile_file.stem
                    profiles[name] = {
                        "name": name,
                        "path": profile_file,
                        "type": "profile",
                        "format": profile_file.suffix[1:]
                    }
            
            # Handle old directory structure
            for profile_dir in source.iterdir():
                if profile_dir.is_dir():
                    context_file = profile_dir / "context.json"
                    if context_file.exists():
                        name = profile_dir.name
                        profiles[name] = {
                            "name": name,
                            "path": context_file,
                            "type": "profile",
                            "format": "json-legacy"
                        }
        
        return profiles
    
    def _list_hook_files(self, source: Path) -> Dict[str, Dict[str, Any]]:
        """List hook files in a source directory."""
        hooks = {}
        
        if source.is_dir():
            for ext, format_name in [("*.yaml", "yaml"), ("*.yml", "yaml"), ("*.py", "python")]:
                for hook_file in source.rglob(ext):
                    name = hook_file.stem
                    hooks[name] = {
                        "name": name,
                        "path": hook_file,
                        "type": "hook",
                        "format": format_name
                    }
        
        return hooks
    
    def _list_mcp_files(self, source: Path) -> Dict[str, Dict[str, Any]]:
        """List MCP server files in a source directory."""
        mcp_configs = {}
        
        if source.is_dir():
            for mcp_file in source.glob("*.json"):
                name = mcp_file.stem
                mcp_configs[name] = {
                    "name": name,
                    "path": mcp_file,
                    "type": "mcp-servers",
                    "format": "json"
                }
        
        return mcp_configs