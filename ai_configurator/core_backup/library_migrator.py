"""Library migration utilities for moving configurations to library-based structure."""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress

from .models import MigrationResult, ConfigurationError
from .metadata_parser import MetadataParser
from .catalog_generator import CatalogGenerator
from ..utils.logging import LoggerMixin

console = Console()


class LibraryMigrator(LoggerMixin):
    """Handles migration of existing configurations to library-based structure."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.library_dir = workspace_root / "library"
        self.backup_dir = workspace_root / ".migration_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Source directories (old structure)
        self.old_configs_dir = workspace_root / "configs"
        self.old_contexts_dir = workspace_root / "contexts"
        self.old_hooks_dir = workspace_root / "hooks"
        
        # Target directories (new library structure)
        self.library_contexts_dir = self.library_dir / "contexts"
        self.library_profiles_dir = self.library_dir / "profiles"
        self.library_hooks_dir = self.library_dir / "hooks"
        self.library_mcp_dir = self.library_dir / "mcp-servers"
        self.library_personas_dir = self.library_dir / "personas"
        
        self.metadata_parser = MetadataParser()
        self.catalog_generator = CatalogGenerator(self.library_dir)
    
    def create_backup(self, description: str = "Pre-library-migration backup") -> Optional[str]:
        """Create a backup of existing configurations before migration."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"library_migration_{timestamp}"
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create backup metadata
            metadata = {
                "backup_id": backup_id,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "type": "library_migration",
                "source_directories": []
            }
            
            # Backup existing directories
            directories_to_backup = [
                ("configs", self.old_configs_dir),
                ("contexts", self.old_contexts_dir),
                ("hooks", self.old_hooks_dir),
                ("library", self.library_dir)
            ]
            
            for dir_name, source_dir in directories_to_backup:
                if source_dir.exists():
                    target_dir = backup_path / dir_name
                    shutil.copytree(source_dir, target_dir)
                    metadata["source_directories"].append(str(source_dir))
                    self.logger.info(f"Backed up {source_dir} to {target_dir}")
            
            # Save backup metadata
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Created backup: {backup_id}")
            return backup_id
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def discover_existing_configurations(self) -> Dict[str, List[Path]]:
        """Discover existing configurations that need migration."""
        discovered = {
            "contexts": [],
            "profiles": [],
            "hooks": [],
            "mcp_servers": []
        }
        
        # Discover context files
        if self.old_contexts_dir.exists():
            for context_file in self.old_contexts_dir.glob("*.md"):
                discovered["contexts"].append(context_file)
        
        # Discover profile configurations
        if self.old_configs_dir.exists():
            profiles_dir = self.old_configs_dir / "profiles"
            if profiles_dir.exists():
                for profile_dir in profiles_dir.iterdir():
                    if profile_dir.is_dir():
                        context_file = profile_dir / "context.json"
                        if context_file.exists():
                            discovered["profiles"].append(context_file)
        
        # Discover hook configurations
        if self.old_hooks_dir.exists():
            for hook_file in self.old_hooks_dir.glob("*.py"):
                discovered["hooks"].append(hook_file)
            for hook_file in self.old_hooks_dir.glob("*.yaml"):
                discovered["hooks"].append(hook_file)
        
        # Discover MCP server configurations
        if self.old_configs_dir.exists():
            mcp_dir = self.old_configs_dir / "mcp-servers"
            if mcp_dir.exists():
                for mcp_file in mcp_dir.glob("*.json"):
                    discovered["mcp_servers"].append(mcp_file)
        
        return discovered
    
    def add_metadata_to_context(self, context_file: Path) -> Dict[str, Any]:
        """Add metadata frontmatter to a context file."""
        try:
            # Read existing content
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if metadata already exists
            if content.startswith('---'):
                # Parse existing metadata
                try:
                    existing_metadata, _ = self.metadata_parser._extract_markdown_frontmatter(content)
                    if existing_metadata:
                        return existing_metadata
                except Exception:
                    # If parsing fails, treat as content without metadata
                    pass
            
            # Generate metadata based on filename and content
            filename = context_file.stem
            metadata = {
                "id": f"{filename.lower().replace('_', '-').replace(' ', '-')}-v1",
                "name": filename.replace('_', ' ').replace('-', ' ').title(),
                "description": f"Context for {filename.replace('_', ' ').replace('-', ' ').lower()}",
                "version": "1.0.0",
                "author": "migrated-configuration",
                "personas": self._infer_personas_from_filename(filename),
                "domains": self._infer_domains_from_filename(filename),
                "dependencies": [],
                "tags": self._infer_tags_from_content(content),
                "compatibility": {
                    "kiro_version": ">=1.0.0",
                    "platforms": ["linux", "macos", "windows"]
                },
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_date": datetime.now().strftime("%Y-%m-%d"),
                "migration": {
                    "migrated_from": str(context_file),
                    "migration_date": datetime.now().isoformat()
                }
            }
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to add metadata to {context_file}: {e}")
            return {}
    
    def migrate_context_file(self, source_file: Path, dry_run: bool = False) -> bool:
        """Migrate a single context file to the library structure."""
        try:
            # Determine target path based on inferred domain
            filename = source_file.stem
            domain = self._infer_primary_domain(filename)
            
            # Read source content first to check for existing metadata
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If content has existing metadata, use its domain for directory structure
            if content.startswith('---'):
                try:
                    existing_metadata, _ = self.metadata_parser._extract_markdown_frontmatter(content)
                    if existing_metadata and 'domains' in existing_metadata and existing_metadata['domains']:
                        domain = existing_metadata['domains'][0]
                except Exception:
                    # If parsing fails, use inferred domain
                    pass
            
            target_dir = self.library_contexts_dir / domain
            target_file = target_dir / source_file.name
            
            if dry_run:
                console.print(f"[blue]Would migrate:[/blue] {source_file} -> {target_file}")
                return True
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Add metadata if not present
            if not content.startswith('---'):
                metadata = self.add_metadata_to_context(source_file)
                if metadata:
                    # Create frontmatter
                    frontmatter = "---\n" + yaml.dump(metadata, default_flow_style=False, sort_keys=False) + "---\n\n"
                    content = frontmatter + content
            
            # Write to target location
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Migrated context: {source_file} -> {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate context {source_file}: {e}")
            return False
    
    def migrate_profile_config(self, source_file: Path, dry_run: bool = False) -> bool:
        """Migrate a profile configuration to the library structure."""
        try:
            profile_name = source_file.parent.name
            target_file = self.library_profiles_dir / f"{profile_name}.yaml"
            
            if dry_run:
                console.print(f"[blue]Would migrate:[/blue] {source_file} -> {target_file}")
                return True
            
            # Create target directory
            self.library_profiles_dir.mkdir(parents=True, exist_ok=True)
            
            # Read and convert JSON to YAML with metadata
            with open(source_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Create enhanced profile configuration
            profile_config = {
                "id": f"{profile_name.lower().replace('_', '-')}-profile-v1",
                "name": f"{profile_name.replace('_', ' ').replace('-', ' ').title()} Profile",
                "description": f"Migrated profile configuration for {profile_name}",
                "version": "1.0.0",
                "author": "migrated-configuration",
                "personas": self._infer_personas_from_filename(profile_name),
                "domains": self._infer_domains_from_filename(profile_name),
                "dependencies": [],
                "tags": ["profile", "migrated"],
                "compatibility": {
                    "kiro_version": ">=1.0.0",
                    "platforms": ["linux", "macos", "windows"]
                },
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_date": datetime.now().strftime("%Y-%m-%d"),
                "migration": {
                    "migrated_from": str(source_file),
                    "migration_date": datetime.now().isoformat()
                },
                "configuration": json_data
            }
            
            # Write YAML file
            with open(target_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile_config, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Migrated profile: {source_file} -> {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate profile {source_file}: {e}")
            return False
    
    def migrate_hook_file(self, source_file: Path, dry_run: bool = False) -> bool:
        """Migrate a hook file to the library structure."""
        try:
            # Determine target path based on inferred category
            filename = source_file.stem
            category = self._infer_hook_category(filename)
            target_dir = self.library_hooks_dir / category
            target_file = target_dir / source_file.name
            
            if dry_run:
                console.print(f"[blue]Would migrate:[/blue] {source_file} -> {target_file}")
                return True
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            if source_file.suffix == '.py':
                # For Python files, create accompanying YAML metadata
                yaml_file = target_dir / f"{filename}.yaml"
                metadata = {
                    "id": f"{filename.lower().replace('_', '-')}-hook-v1",
                    "name": f"{filename.replace('_', ' ').replace('-', ' ').title()} Hook",
                    "description": f"Migrated hook: {filename}",
                    "version": "1.0.0",
                    "author": "migrated-configuration",
                    "type": "script",
                    "trigger": "manual",  # Default, can be updated
                    "timeout": 30,
                    "enabled": True,
                    "personas": self._infer_personas_from_filename(filename),
                    "domains": [category],
                    "dependencies": [],
                    "tags": ["hook", "migrated"],
                    "compatibility": {
                        "kiro_version": ">=1.0.0",
                        "platforms": ["linux", "macos", "windows"]
                    },
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "updated_date": datetime.now().strftime("%Y-%m-%d"),
                    "migration": {
                        "migrated_from": str(source_file),
                        "migration_date": datetime.now().isoformat()
                    },
                    "script": {
                        "file": source_file.name,
                        "command": "python",
                        "args": [source_file.name],
                        "env": {},
                        "timeout": 30
                    }
                }
                
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
            
            # Copy the actual file
            shutil.copy2(source_file, target_file)
            
            self.logger.info(f"Migrated hook: {source_file} -> {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate hook {source_file}: {e}")
            return False
    
    def migrate_mcp_config(self, source_file: Path, dry_run: bool = False) -> bool:
        """Migrate an MCP server configuration to the library structure."""
        try:
            target_file = self.library_mcp_dir / source_file.name
            
            if dry_run:
                console.print(f"[blue]Would migrate:[/blue] {source_file} -> {target_file}")
                return True
            
            # Create target directory
            self.library_mcp_dir.mkdir(parents=True, exist_ok=True)
            
            # Read and enhance JSON configuration
            with open(source_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Add metadata to the configuration
            enhanced_config = {
                "id": f"{source_file.stem.lower().replace('_', '-')}-mcp-v1",
                "name": f"{source_file.stem.replace('_', ' ').replace('-', ' ').title()} MCP Servers",
                "description": f"Migrated MCP server configuration: {source_file.stem}",
                "version": "1.0.0",
                "author": "migrated-configuration",
                "personas": self._infer_personas_from_filename(source_file.stem),
                "domains": self._infer_domains_from_filename(source_file.stem),
                "dependencies": [],
                "tags": ["mcp-servers", "migrated"],
                "compatibility": {
                    "kiro_version": ">=1.0.0",
                    "platforms": ["linux", "macos", "windows"]
                },
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_date": datetime.now().strftime("%Y-%m-%d"),
                "migration": {
                    "migrated_from": str(source_file),
                    "migration_date": datetime.now().isoformat()
                },
                "mcpServers": json_data.get("mcpServers", json_data)
            }
            
            # Write enhanced configuration
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_config, f, indent=2)
            
            self.logger.info(f"Migrated MCP config: {source_file} -> {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate MCP config {source_file}: {e}")
            return False
    
    def migrate_all_configurations(self, dry_run: bool = False, backup: bool = True) -> MigrationResult:
        """Migrate all existing configurations to library-based structure."""
        result = MigrationResult(
            success=True,
            migrated_files=[],
            failed_files=[],
            backup_path=None,
            errors=[],
            warnings=[]
        )
        
        # Create backup if requested
        if backup and not dry_run:
            backup_id = self.create_backup()
            if backup_id:
                result.backup_path = str(self.backup_dir / backup_id)
                console.print(f"[green]✅ Backup created:[/green] {backup_id}")
            else:
                result.warnings.append(ConfigurationError(
                    file_path="",
                    error_type="backup_warning",
                    message="Failed to create backup before migration",
                    severity="warning"
                ))
        
        # Discover configurations
        discovered = self.discover_existing_configurations()
        
        # Migrate contexts
        for context_file in discovered["contexts"]:
            if self.migrate_context_file(context_file, dry_run):
                result.migrated_files.append(str(context_file))
            else:
                result.failed_files.append(str(context_file))
                result.success = False
        
        # Migrate profiles
        for profile_file in discovered["profiles"]:
            if self.migrate_profile_config(profile_file, dry_run):
                result.migrated_files.append(str(profile_file))
            else:
                result.failed_files.append(str(profile_file))
                result.success = False
        
        # Migrate hooks
        for hook_file in discovered["hooks"]:
            if self.migrate_hook_file(hook_file, dry_run):
                result.migrated_files.append(str(hook_file))
            else:
                result.failed_files.append(str(hook_file))
                result.success = False
        
        # Migrate MCP configurations
        for mcp_file in discovered["mcp_servers"]:
            if self.migrate_mcp_config(mcp_file, dry_run):
                result.migrated_files.append(str(mcp_file))
            else:
                result.failed_files.append(str(mcp_file))
                result.success = False
        
        # Generate catalog if not dry run
        if not dry_run and result.migrated_files:
            try:
                self.catalog_generator.generate_catalog()
                console.print("[green]✅ Generated library catalog[/green]")
            except Exception as e:
                self.logger.warning(f"Failed to generate catalog: {e}")
                result.warnings.append(ConfigurationError(
                    file_path="library/catalog.json",
                    error_type="catalog_generation_warning",
                    message=f"Failed to generate catalog: {e}",
                    severity="warning"
                ))
        
        return result
    
    def validate_migrated_configurations(self) -> List[ConfigurationError]:
        """Validate migrated configurations in the library structure."""
        errors = []
        
        # Validate context files
        contexts_dir = self.library_contexts_dir
        if contexts_dir.exists():
            for context_file in contexts_dir.rglob("*.md"):
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith('---'):
                        metadata, _ = self.metadata_parser._extract_markdown_frontmatter(content)
                        # Validate required metadata fields
                        required_fields = ['id', 'name', 'version', 'author']
                        for field in required_fields:
                            if field not in metadata:
                                errors.append(ConfigurationError(
                                    file_path=str(context_file),
                                    error_type="missing_metadata",
                                    message=f"Missing required metadata field: {field}",
                                    severity="error"
                                ))
                except Exception as e:
                    errors.append(ConfigurationError(
                        file_path=str(context_file),
                        error_type="validation_error",
                        message=str(e),
                        severity="error"
                    ))
        
        # Validate profile files
        profiles_dir = self.library_profiles_dir
        if profiles_dir.exists():
            for profile_file in profiles_dir.glob("*.yaml"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(ConfigurationError(
                        file_path=str(profile_file),
                        error_type="yaml_syntax_error",
                        message=str(e),
                        severity="error"
                    ))
        
        # Validate hook files
        hooks_dir = self.library_hooks_dir
        if hooks_dir.exists():
            for hook_file in hooks_dir.rglob("*.yaml"):
                try:
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(ConfigurationError(
                        file_path=str(hook_file),
                        error_type="yaml_syntax_error",
                        message=str(e),
                        severity="error"
                    ))
        
        # Validate MCP configurations
        mcp_dir = self.library_mcp_dir
        if mcp_dir.exists():
            for mcp_file in mcp_dir.glob("*.json"):
                try:
                    with open(mcp_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(ConfigurationError(
                        file_path=str(mcp_file),
                        error_type="json_syntax_error",
                        message=str(e),
                        severity="error"
                    ))
        
        return errors
    
    def rollback_migration(self, backup_id: str) -> bool:
        """Rollback library migration using backup."""
        try:
            backup_path = self.backup_dir / backup_id
            if not backup_path.exists():
                self.logger.error(f"Backup not found: {backup_id}")
                return False
            
            # Remove current library directory
            if self.library_dir.exists():
                shutil.rmtree(self.library_dir)
            
            # Restore directories from backup
            directories_to_restore = [
                ("configs", self.old_configs_dir),
                ("contexts", self.old_contexts_dir),
                ("hooks", self.old_hooks_dir),
                ("library", self.library_dir)
            ]
            
            for dir_name, target_dir in directories_to_restore:
                backup_source = backup_path / dir_name
                if backup_source.exists():
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(backup_source, target_dir)
                    self.logger.info(f"Restored {dir_name} from backup")
            
            self.logger.info(f"Migration rolled back from backup: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration: {e}")
            return False
    
    def _infer_personas_from_filename(self, filename: str) -> List[str]:
        """Infer personas based on filename patterns."""
        filename_lower = filename.lower()
        personas = []
        
        persona_patterns = {
            "developer": ["dev", "development", "coding", "programming"],
            "network-admin": ["network", "admin", "infrastructure", "networking"],
            "content-creator": ["content", "creator", "writing", "documentation"],
            "researcher": ["research", "academic", "analysis"],
            "devops-engineer": ["devops", "deployment", "ci", "cd", "pipeline"],
            "solutions-architect": ["architect", "solution", "design"],
            "engagement-manager": ["engagement", "manager", "client", "project"]
        }
        
        for persona, patterns in persona_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                personas.append(persona)
        
        return personas if personas else ["general"]
    
    def _infer_domains_from_filename(self, filename: str) -> List[str]:
        """Infer domains based on filename patterns."""
        filename_lower = filename.lower()
        domains = []
        
        domain_patterns = {
            "development": ["dev", "development", "coding", "programming"],
            "networking": ["network", "networking", "infrastructure"],
            "productivity": ["productivity", "task", "management"],
            "engagement": ["engagement", "client", "communication"],
            "aws": ["aws", "cloud", "amazon"],
            "research": ["research", "academic", "analysis"]
        }
        
        for domain, patterns in domain_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                domains.append(domain)
        
        return domains if domains else ["general"]
    
    def _infer_primary_domain(self, filename: str) -> str:
        """Infer the primary domain for directory organization."""
        domains = self._infer_domains_from_filename(filename)
        return domains[0] if domains else "general"
    
    def _infer_hook_category(self, filename: str) -> str:
        """Infer hook category for directory organization."""
        filename_lower = filename.lower()
        
        category_patterns = {
            "development": ["dev", "development", "coding", "test"],
            "productivity": ["productivity", "context", "loader", "task"],
            "engagement": ["engagement", "client", "manager"],
            "maintenance": ["maintenance", "cleanup", "backup"]
        }
        
        for category, patterns in category_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return category
        
        return "general"
    
    def _infer_tags_from_content(self, content: str) -> List[str]:
        """Infer tags based on content analysis."""
        content_lower = content.lower()
        tags = []
        
        tag_patterns = {
            "troubleshooting": ["troubleshoot", "debug", "problem", "issue"],
            "automation": ["automate", "script", "batch", "workflow"],
            "documentation": ["document", "readme", "guide", "manual"],
            "testing": ["test", "testing", "qa", "quality"],
            "security": ["security", "secure", "auth", "permission"],
            "performance": ["performance", "optimize", "speed", "efficiency"]
        }
        
        for tag, patterns in tag_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                tags.append(tag)
        
        return tags if tags else ["general"]