"""Configuration migration CLI commands."""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, TaskID

from ..core import ConfigurationManager
from ..core.models import (
    MigrationResult,
    ConfigurationError,
    EnhancedProfileConfig,
    HookConfig,
    ContextConfig,
    ProfileSettings,
    HookReference,
    HookTrigger,
    HookType,
    ValidationLevel
)
from ..utils.logging import LoggerMixin

console = Console()


class ConfigurationMigrator(LoggerMixin):
    """Handles migration from JSON to YAML configurations."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.config_dir = config_manager.config_dir
        self.app_data_dir = config_manager.app_data_dir
        self.migration_backup_dir = self.app_data_dir / "migration_backups"
        self.migration_backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_migration_backup(self, description: str = "Pre-migration backup") -> Optional[str]:
        """Create a backup before migration."""
        return self.config_manager.create_backup(description)
    
    def discover_json_configurations(self) -> Dict[str, List[Path]]:
        """Discover existing JSON configuration files."""
        discovered = {
            "profiles": [],
            "mcp_servers": [],
            "global_context": [],
            "hooks": []
        }
        
        # Find profile configurations
        profiles_dir = self.config_dir / "profiles"
        if profiles_dir.exists():
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir():
                    context_file = profile_dir / "context.json"
                    hooks_file = profile_dir / "hooks.json"
                    
                    if context_file.exists():
                        discovered["profiles"].append(context_file)
                    if hooks_file.exists():
                        discovered["hooks"].append(hooks_file)
        
        # Find MCP server configurations
        mcp_file = self.config_dir / "mcp.json"
        if mcp_file.exists():
            discovered["mcp_servers"].append(mcp_file)
        
        # Find global context
        global_context_file = self.config_dir / "global_context.json"
        if global_context_file.exists():
            discovered["global_context"].append(global_context_file)
        
        return discovered
    
    def convert_profile_context_to_yaml(self, json_path: Path) -> Optional[Dict[str, Any]]:
        """Convert a profile context JSON file to YAML format."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            profile_name = json_path.parent.name
            
            # Convert to enhanced profile config format
            yaml_config = {
                "name": profile_name,
                "description": f"Migrated profile: {profile_name}",
                "version": "1.0",
                "contexts": json_data.get("paths", []),
                "hooks": {},
                "mcp_servers": [],
                "settings": {
                    "auto_backup": True,
                    "validation_level": "normal",
                    "hot_reload": True,
                    "cache_enabled": True
                },
                "metadata": {
                    "migrated_from": str(json_path),
                    "migration_date": self._get_current_timestamp()
                }
            }
            
            # Convert hooks if they exist
            if "hooks" in json_data:
                for trigger, commands in json_data["hooks"].items():
                    # Map old trigger names to new enum values
                    trigger_mapping = {
                        "conversation_start": "on_session_start",
                        "per_message": "per_user_message",
                        "file_change": "on_file_change"
                    }
                    
                    new_trigger = trigger_mapping.get(trigger, trigger)
                    
                    hook_refs = []
                    for i, command in enumerate(commands):
                        hook_name = f"{profile_name}_{trigger}_{i}"
                        hook_refs.append({
                            "name": hook_name,
                            "enabled": True,
                            "config": {
                                "command": command,
                                "migrated": True
                            }
                        })
                    
                    yaml_config["hooks"][new_trigger] = hook_refs
            
            return yaml_config
            
        except Exception as e:
            self.logger.error(f"Failed to convert profile context {json_path}: {e}")
            return None
    
    def convert_mcp_config_to_yaml(self, json_path: Path) -> Optional[Dict[str, Any]]:
        """Convert MCP configuration from JSON to YAML format."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # MCP config structure remains the same, just convert to YAML
            return json_data
            
        except Exception as e:
            self.logger.error(f"Failed to convert MCP config {json_path}: {e}")
            return None
    
    def create_hook_yaml_from_command(self, hook_name: str, command: str, trigger: str) -> Dict[str, Any]:
        """Create a hook YAML configuration from a command string."""
        # Parse command to extract executable and args
        parts = command.split()
        executable = parts[0] if parts else "python"
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            "name": hook_name,
            "description": f"Migrated hook: {hook_name}",
            "version": "1.0",
            "type": "script",
            "trigger": trigger,
            "timeout": 30,
            "enabled": True,
            "script": {
                "command": executable,
                "args": args,
                "env": {},
                "timeout": 30
            },
            "conditions": [],
            "metadata": {
                "migrated": True,
                "original_command": command,
                "migration_date": self._get_current_timestamp()
            }
        }
    
    def migrate_profile(self, json_path: Path, dry_run: bool = False) -> bool:
        """Migrate a single profile from JSON to YAML."""
        try:
            yaml_config = self.convert_profile_context_to_yaml(json_path)
            if not yaml_config:
                return False
            
            profile_name = json_path.parent.name
            yaml_path = self.config_dir / "profiles" / f"{profile_name}.yaml"
            
            if dry_run:
                console.print(f"[blue]Would create:[/blue] {yaml_path}")
                return True
            
            # Create profiles directory if it doesn't exist
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save YAML file
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"Migrated profile {profile_name} to {yaml_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate profile {json_path}: {e}")
            return False
    
    def migrate_mcp_config(self, json_path: Path, dry_run: bool = False) -> bool:
        """Migrate MCP configuration from JSON to YAML."""
        try:
            yaml_config = self.convert_mcp_config_to_yaml(json_path)
            if not yaml_config:
                return False
            
            yaml_path = self.config_dir / "mcp.yaml"
            
            if dry_run:
                console.print(f"[blue]Would create:[/blue] {yaml_path}")
                return True
            
            # Save YAML file
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            self.logger.info(f"Migrated MCP config to {yaml_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate MCP config {json_path}: {e}")
            return False
    
    def migrate_all_configurations(self, dry_run: bool = False, backup: bool = True) -> MigrationResult:
        """Migrate all JSON configurations to YAML format."""
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
            backup_id = self.create_migration_backup()
            if backup_id:
                result.backup_path = str(self.config_manager.backup_dir / backup_id)
                console.print(f"[green]✅ Backup created:[/green] {backup_id}")
            else:
                result.warnings.append(ConfigurationError(
                    file_path="",
                    error_type="backup_warning",
                    message="Failed to create backup before migration",
                    severity="warning"
                ))
        
        # Discover configurations
        discovered = self.discover_json_configurations()
        
        # Migrate profiles
        for profile_json in discovered["profiles"]:
            if self.migrate_profile(profile_json, dry_run):
                result.migrated_files.append(str(profile_json))
            else:
                result.failed_files.append(str(profile_json))
                result.success = False
        
        # Migrate MCP configurations
        for mcp_json in discovered["mcp_servers"]:
            if self.migrate_mcp_config(mcp_json, dry_run):
                result.migrated_files.append(str(mcp_json))
            else:
                result.failed_files.append(str(mcp_json))
                result.success = False
        
        return result
    
    def rollback_migration(self, backup_path: str) -> bool:
        """Rollback migration using backup."""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                self.logger.error(f"Backup directory not found: {backup_path}")
                return False
            
            # Remove current configuration
            if self.config_dir.exists():
                shutil.rmtree(self.config_dir)
            
            # Restore from backup
            shutil.copytree(backup_dir, self.config_dir)
            
            # Remove backup metadata from restored config
            metadata_file = self.config_dir / "backup_metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            self.logger.info(f"Migration rolled back from backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback migration: {e}")
            return False
    
    def validate_migrated_configurations(self) -> List[ConfigurationError]:
        """Validate migrated YAML configurations."""
        errors = []
        
        # Check for YAML syntax errors
        profiles_dir = self.config_dir / "profiles"
        if profiles_dir.exists():
            for yaml_file in profiles_dir.glob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    errors.append(ConfigurationError(
                        file_path=str(yaml_file),
                        line_number=getattr(e, 'problem_mark', {}).get('line'),
                        error_type="yaml_syntax_error",
                        message=str(e),
                        severity="error"
                    ))
        
        # Check MCP YAML
        mcp_yaml = self.config_dir / "mcp.yaml"
        if mcp_yaml.exists():
            try:
                with open(mcp_yaml, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(ConfigurationError(
                    file_path=str(mcp_yaml),
                    line_number=getattr(e, 'problem_mark', {}).get('line'),
                    error_type="yaml_syntax_error",
                    message=str(e),
                    severity="error"
                ))
        
        return errors
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


@click.group()
def migrate():
    """Migrate configurations from JSON to YAML format."""
    pass


@migrate.command("discover")
@click.pass_context
def migrate_discover(ctx: click.Context):
    """Discover existing JSON configurations that can be migrated."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    discovered = migrator.discover_json_configurations()
    
    # Create discovery table
    table = Table(title="Discoverable JSON Configurations")
    table.add_column("Type", style="cyan")
    table.add_column("Files", style="green")
    table.add_column("Status", style="yellow")
    
    total_files = 0
    for config_type, files in discovered.items():
        count = len(files)
        total_files += count
        status = "✅ Ready" if count > 0 else "⚪ None"
        table.add_row(config_type.replace("_", " ").title(), str(count), status)
    
    console.print(table)
    
    if total_files == 0:
        console.print("\n[yellow]No JSON configurations found to migrate.[/yellow]")
        console.print("This could mean:")
        console.print("• Configurations are already in YAML format")
        console.print("• No configurations exist yet")
        console.print("• Configurations are in a different location")
        return
    
    # Show detailed file list
    console.print(f"\n[bold blue]Detailed File List ({total_files} files):[/bold blue]")
    for config_type, files in discovered.items():
        if files:
            console.print(f"\n[bold]{config_type.replace('_', ' ').title()}:[/bold]")
            for file_path in files:
                console.print(f"  📄 {file_path}")


@migrate.command("preview")
@click.option(
    "--profile", "-p",
    help="Preview migration for specific profile only"
)
@click.pass_context
def migrate_preview(ctx: click.Context, profile: Optional[str]):
    """Preview what would be migrated without making changes."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    console.print("[blue]Migration Preview (Dry Run)[/blue]\n")
    
    if profile:
        # Preview specific profile
        profile_json = config_manager.config_dir / "profiles" / profile / "context.json"
        if not profile_json.exists():
            console.print(f"[red]Profile '{profile}' not found at {profile_json}[/red]")
            return
        
        yaml_config = migrator.convert_profile_context_to_yaml(profile_json)
        if yaml_config:
            console.print(f"[bold green]Profile: {profile}[/bold green]")
            yaml_content = yaml.dump(yaml_config, default_flow_style=False, allow_unicode=True, sort_keys=False)
            console.print(Panel(yaml_content, title=f"Converted YAML for {profile}", border_style="green"))
        else:
            console.print(f"[red]Failed to convert profile: {profile}[/red]")
    else:
        # Preview all configurations
        result = migrator.migrate_all_configurations(dry_run=True, backup=False)
        
        if result.migrated_files:
            console.print("[bold green]Files that would be migrated:[/bold green]")
            for file_path in result.migrated_files:
                console.print(f"  ✅ {file_path}")
        
        if result.failed_files:
            console.print("\n[bold red]Files that would fail:[/bold red]")
            for file_path in result.failed_files:
                console.print(f"  ❌ {file_path}")
        
        console.print(f"\n[bold blue]Summary:[/bold blue]")
        console.print(f"• Would migrate: {len(result.migrated_files)} files")
        console.print(f"• Would fail: {len(result.failed_files)} files")
        console.print(f"• Overall success: {'✅ Yes' if result.success else '❌ No'}")


@migrate.command("run")
@click.option(
    "--profile", "-p",
    help="Migrate specific profile only"
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Skip creating backup before migration"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Force migration even if YAML files already exist"
)
@click.pass_context
def migrate_run(ctx: click.Context, profile: Optional[str], no_backup: bool, force: bool):
    """Run the migration from JSON to YAML configurations."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    # Check if YAML files already exist
    if not force:
        yaml_files_exist = []
        profiles_dir = config_manager.config_dir / "profiles"
        if profiles_dir.exists():
            yaml_files_exist.extend(list(profiles_dir.glob("*.yaml")))
        
        mcp_yaml = config_manager.config_dir / "mcp.yaml"
        if mcp_yaml.exists():
            yaml_files_exist.append(mcp_yaml)
        
        if yaml_files_exist:
            console.print("[yellow]YAML configuration files already exist:[/yellow]")
            for yaml_file in yaml_files_exist:
                console.print(f"  📄 {yaml_file}")
            console.print("\nUse --force to overwrite existing YAML files")
            return
    
    # Confirm migration
    if not ctx.obj.get("quiet", False):
        backup_msg = " (with backup)" if not no_backup else " (without backup)"
        scope_msg = f" for profile '{profile}'" if profile else ""
        
        console.print(f"[yellow]This will migrate JSON configurations to YAML{scope_msg}{backup_msg}[/yellow]")
        
        if not click.confirm("Continue with migration?"):
            console.print("[yellow]Migration cancelled.[/yellow]")
            return
    
    # Run migration
    console.print("[blue]Running migration...[/blue]")
    
    with Progress() as progress:
        task = progress.add_task("Migrating configurations...", total=100)
        
        if profile:
            # Migrate specific profile
            profile_json = config_manager.config_dir / "profiles" / profile / "context.json"
            if not profile_json.exists():
                console.print(f"[red]Profile '{profile}' not found at {profile_json}[/red]")
                return
            
            progress.update(task, advance=50)
            success = migrator.migrate_profile(profile_json, dry_run=False)
            progress.update(task, advance=50)
            
            if success:
                console.print(f"[bold green]✅ Profile '{profile}' migrated successfully![/bold green]")
            else:
                console.print(f"[bold red]❌ Failed to migrate profile '{profile}'[/bold red]")
        else:
            # Migrate all configurations
            progress.update(task, advance=20)
            result = migrator.migrate_all_configurations(dry_run=False, backup=not no_backup)
            progress.update(task, advance=80)
            
            # Show results
            if result.success:
                console.print("[bold green]✅ Migration completed successfully![/bold green]")
            else:
                console.print("[bold red]❌ Migration completed with errors![/bold red]")
            
            # Create results table
            table = Table(title="Migration Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", style="green")
            
            table.add_row("Migrated Files", str(len(result.migrated_files)))
            table.add_row("Failed Files", str(len(result.failed_files)))
            table.add_row("Errors", str(len(result.errors)))
            table.add_row("Warnings", str(len(result.warnings)))
            
            console.print(table)
            
            # Show backup info
            if result.backup_path:
                console.print(f"\n[blue]Backup created at:[/blue] {result.backup_path}")
            
            # Show migrated files
            if result.migrated_files:
                console.print("\n[bold green]Migrated Files:[/bold green]")
                for file_path in result.migrated_files:
                    console.print(f"  ✅ {file_path}")
            
            # Show failed files
            if result.failed_files:
                console.print("\n[bold red]Failed Files:[/bold red]")
                for file_path in result.failed_files:
                    console.print(f"  ❌ {file_path}")
            
            # Show errors
            if result.errors:
                console.print("\n[bold red]Errors:[/bold red]")
                for error in result.errors:
                    console.print(f"  ❌ {error.message}")
    
    # Validate migrated configurations
    console.print("\n[blue]Validating migrated configurations...[/blue]")
    validation_errors = migrator.validate_migrated_configurations()
    
    if validation_errors:
        console.print("[bold red]Validation errors found:[/bold red]")
        for error in validation_errors:
            line_info = f" (line {error.line_number})" if error.line_number else ""
            console.print(f"  ❌ {error.file_path}{line_info}: {error.message}")
    else:
        console.print("[bold green]✅ All migrated configurations are valid![/bold green]")
    
    # Show next steps
    console.print("\n[bold blue]Next steps:[/bold blue]")
    console.print("1. Review the migrated YAML files")
    console.print("2. Test your configuration: [cyan]ai-config validate[/cyan]")
    console.print("3. Remove old JSON files if migration was successful")
    if result.backup_path:
        console.print(f"4. Keep backup safe: [cyan]{result.backup_path}[/cyan]")


@migrate.command("rollback")
@click.argument("backup_id")
@click.pass_context
def migrate_rollback(ctx: click.Context, backup_id: str):
    """Rollback migration using a backup."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    # List available backups if backup_id is 'list'
    if backup_id.lower() == "list":
        backups = config_manager.list_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
            return
        
        table = Table(title="Available Migration Backups")
        table.add_column("Backup ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Description", style="yellow")
        
        for backup in backups:
            if "migration" in backup.description.lower():
                table.add_row(backup.backup_id, backup.timestamp, backup.description or "")
        
        console.print(table)
        return
    
    # Confirm rollback
    if not ctx.obj.get("quiet", False):
        console.print(f"[yellow]This will rollback the migration using backup: {backup_id}[/yellow]")
        console.print("[red]This will replace all current configurations![/red]")
        
        if not click.confirm("Continue with rollback?"):
            console.print("[yellow]Rollback cancelled.[/yellow]")
            return
    
    # Perform rollback
    console.print(f"[blue]Rolling back migration using backup: {backup_id}[/blue]")
    
    backup_path = str(config_manager.backup_dir / backup_id)
    success = migrator.rollback_migration(backup_path)
    
    if success:
        console.print(f"[bold green]✅ Migration rolled back successfully![/bold green]")
        console.print("Your configuration has been restored to the pre-migration state.")
    else:
        console.print(f"[bold red]❌ Failed to rollback migration![/bold red]")
        console.print("Check the logs for details.")


@migrate.command("validate")
@click.pass_context
def migrate_validate(ctx: click.Context):
    """Validate migrated YAML configurations."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    console.print("[blue]Validating migrated YAML configurations...[/blue]")
    
    errors = migrator.validate_migrated_configurations()
    
    if not errors:
        console.print("[bold green]✅ All YAML configurations are valid![/bold green]")
        return
    
    # Show validation errors
    table = Table(title="Validation Errors")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="yellow")
    table.add_column("Error", style="red")
    
    for error in errors:
        line_str = str(error.line_number) if error.line_number else "N/A"
        table.add_row(
            Path(error.file_path).name,
            line_str,
            error.message
        )
    
    console.print(table)
    
    console.print(f"\n[bold red]Found {len(errors)} validation errors.[/bold red]")
    console.print("Please fix these errors before using the migrated configurations.")


@migrate.command("cleanup")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be cleaned up without making changes"
)
@click.pass_context
def migrate_cleanup(ctx: click.Context, dry_run: bool):
    """Clean up old JSON files after successful migration."""
    config_manager = ctx.obj["config_manager"]
    migrator = ConfigurationMigrator(config_manager)
    
    # Discover JSON files
    discovered = migrator.discover_json_configurations()
    
    all_json_files = []
    for file_list in discovered.values():
        all_json_files.extend(file_list)
    
    if not all_json_files:
        console.print("[yellow]No JSON configuration files found to clean up.[/yellow]")
        return
    
    if dry_run:
        console.print("[blue]Cleanup Preview (Dry Run)[/blue]\n")
        console.print("Files that would be removed:")
        for json_file in all_json_files:
            console.print(f"  🗑️ {json_file}")
        console.print(f"\nTotal: {len(all_json_files)} files")
        return
    
    # Confirm cleanup
    if not ctx.obj.get("quiet", False):
        console.print(f"[yellow]This will permanently delete {len(all_json_files)} JSON configuration files.[/yellow]")
        console.print("[red]Make sure you have backups and the migration was successful![/red]")
        
        if not click.confirm("Continue with cleanup?"):
            console.print("[yellow]Cleanup cancelled.[/yellow]")
            return
    
    # Perform cleanup
    console.print("[blue]Cleaning up JSON configuration files...[/blue]")
    
    removed_files = []
    failed_files = []
    
    for json_file in all_json_files:
        try:
            json_file.unlink()
            removed_files.append(json_file)
            console.print(f"  🗑️ Removed: {json_file}")
        except Exception as e:
            failed_files.append((json_file, str(e)))
            console.print(f"  ❌ Failed to remove: {json_file} ({e})")
    
    # Show results
    console.print(f"\n[bold green]✅ Cleanup completed![/bold green]")
    console.print(f"• Removed: {len(removed_files)} files")
    console.print(f"• Failed: {len(failed_files)} files")
    
    if failed_files:
        console.print("\n[bold red]Failed to remove:[/bold red]")
        for file_path, error in failed_files:
            console.print(f"  ❌ {file_path}: {error}")