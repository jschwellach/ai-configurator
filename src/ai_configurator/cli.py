"""Main CLI interface for AI Configurator."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .commands.context import context
from .commands.hooks import hooks
from .core import ConfigurationManager, PlatformManager
from .utils.logging import setup_logging

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
@click.option(
    "--quiet", "-q", 
    is_flag=True, 
    help="Suppress non-error output"
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """AI Configurator - Cross-platform configuration manager for Amazon Q CLI."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    
    # Setup logging
    log_level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    setup_logging(log_level)
    
    # Initialize managers
    ctx.obj["platform"] = PlatformManager()
    ctx.obj["config_manager"] = ConfigurationManager(ctx.obj["platform"])


@cli.command()
@click.option(
    "--profile", "-p",
    help="Install with specific profile (e.g., developer, solutions-architect)"
)
@click.option(
    "--mcp-servers",
    help="Comma-separated list of MCP server groups to install"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Force installation even if configuration exists"
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Skip creating backup before installation"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without actually installing"
)
@click.pass_context
def install(
    ctx: click.Context, 
    profile: Optional[str], 
    mcp_servers: Optional[str], 
    force: bool,
    no_backup: bool,
    dry_run: bool
) -> None:
    """Install Amazon Q CLI configuration."""
    from .core import InstallationManager, InstallationConfig
    
    platform = ctx.obj["platform"]
    config_manager = ctx.obj["config_manager"]
    installer = InstallationManager(platform, config_manager)
    
    # Check if Amazon Q CLI is installed
    if not platform.is_amazonq_installed():
        console.print("[red]Error: Amazon Q CLI not found. Please install it first.[/red]")
        console.print("\nTo install Amazon Q CLI:")
        console.print("• Visit: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-getting-started-installing.html")
        sys.exit(1)
    
    # Parse MCP server groups
    mcp_groups = []
    if mcp_servers:
        mcp_groups = [group.strip() for group in mcp_servers.split(",")]
    
    # Create installation configuration
    install_config = InstallationConfig(
        profile=profile,
        mcp_servers=mcp_groups if mcp_groups else None,
        backup_before_install=not no_backup,
        force=force
    )
    
    # Show available options if no profile specified
    if not profile:
        available_profiles = installer.get_available_profiles()
        if available_profiles:
            console.print("[yellow]Available profiles:[/yellow]")
            for p in available_profiles:
                console.print(f"  • {p}")
            console.print("\nUse --profile to specify a profile, or continue with 'default'")
            install_config.profile = "default"
    
    # Show available MCP groups if none specified
    if not mcp_groups:
        available_groups = installer.get_available_mcp_groups()
        if available_groups:
            console.print("[yellow]Available MCP server groups:[/yellow]")
            for group in available_groups:
                console.print(f"  • {group}")
            console.print("\nUse --mcp-servers to specify groups, or continue with 'core'")
            install_config.mcp_servers = ["core"]
    
    # Check if configuration already exists
    if config_manager.config_dir.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_manager.config_dir}[/yellow]")
        console.print("Use --force to overwrite or run 'ai-config update' to update existing configuration.")
        sys.exit(1)
    
    # Show installation summary
    if not ctx.obj["quiet"]:
        console.print(Panel.fit(
            "[bold blue]AI Configurator Installation[/bold blue]\n"
            "Setting up your Amazon Q CLI configuration...",
            border_style="blue"
        ))
    
    summary = installer.get_installation_summary(install_config)
    
    # Create summary table
    table = Table(title="Installation Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="green")
    
    table.add_row("Profile", summary["profile"])
    table.add_row("MCP Groups", ", ".join(summary["mcp_groups"]))
    table.add_row("MCP Servers", f"{len(summary['mcp_servers'])} servers")
    table.add_row("Context Files", f"{len(summary['context_files'])} files")
    table.add_row("Hooks", f"{len(summary['hooks'])} files")
    table.add_row("Backup", "Yes" if summary["backup_before_install"] else "No")
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        
        # Show detailed information
        if summary["mcp_servers"]:
            console.print("\n[bold]MCP Servers to be installed:[/bold]")
            for server in summary["mcp_servers"]:
                console.print(f"  • {server}")
        
        if summary["context_files"]:
            console.print("\n[bold]Context files to be copied:[/bold]")
            for file in summary["context_files"]:
                console.print(f"  • {file}")
        
        return
    
    # Confirm installation
    if not force and not ctx.obj["quiet"]:
        if not click.confirm("\nProceed with installation?"):
            console.print("[yellow]Installation cancelled.[/yellow]")
            return
    
    # Perform installation
    console.print("\n[blue]Installing configuration...[/blue]")
    
    success = installer.install(install_config)
    
    if success:
        console.print("\n[bold green]✅ Installation completed successfully![/bold green]")
        console.print(f"\nConfiguration installed to: {config_manager.config_dir}")
        console.print("\nNext steps:")
        console.print("1. Test your configuration: [cyan]q chat[/cyan]")
        console.print("2. Validate setup: [cyan]ai-config validate[/cyan]")
        console.print("3. View status: [cyan]ai-config status[/cyan]")
    else:
        console.print("\n[bold red]❌ Installation failed![/bold red]")
        console.print("Check the logs above for details.")
        sys.exit(1)


@cli.command()
@click.option(
    "--preserve-personal",
    is_flag=True,
    help="Preserve personal customizations during update"
)
@click.option(
    "--selective",
    help="Update only specific components (comma-separated: mcp,profiles,contexts,hooks)"
)
@click.option(
    "--check-only",
    is_flag=True,
    help="Only check for updates without applying them"
)
@click.pass_context
def update(ctx: click.Context, preserve_personal: bool, selective: str, check_only: bool) -> None:
    """Update existing Amazon Q CLI configuration."""
    from .core import UpdateManager
    
    config_manager = ctx.obj["config_manager"]
    update_manager = UpdateManager(ctx.obj["platform"], config_manager)
    
    if check_only:
        console.print("[blue]Checking for updates...[/blue]")
        
        update_info = update_manager.check_for_updates()
        
        # Create update summary table
        table = Table(title="Available Updates")
        table.add_column("Component", style="cyan")
        table.add_column("Updates", style="green")
        table.add_column("Status", style="yellow")
        
        table.add_row("MCP Servers", str(len(update_info["mcp_updates"])), 
                     "✅ Available" if update_info["mcp_updates"] else "✅ Up to date")
        table.add_row("Profiles", str(len(update_info["profile_updates"])), 
                     "✅ Available" if update_info["profile_updates"] else "✅ Up to date")
        table.add_row("Contexts", str(len(update_info["context_updates"])), 
                     "✅ Available" if update_info["context_updates"] else "✅ Up to date")
        table.add_row("Hooks", str(len(update_info["hook_updates"])), 
                     "✅ Available" if update_info["hook_updates"] else "✅ Up to date")
        
        console.print(table)
        
        # Show recommendations
        if update_info["recommendations"]:
            console.print("\n[bold blue]Recommendations:[/bold blue]")
            for rec in update_info["recommendations"]:
                console.print(f"  💡 {rec}")
        else:
            console.print("\n[bold green]✅ All components are up to date![/bold green]")
        
        return
    
    # Parse selective components
    selective_components = None
    if selective:
        selective_components = [comp.strip() for comp in selective.split(",")]
        valid_components = ["mcp", "profiles", "contexts", "hooks"]
        invalid_components = [comp for comp in selective_components if comp not in valid_components]
        
        if invalid_components:
            console.print(f"[red]Invalid components: {', '.join(invalid_components)}[/red]")
            console.print(f"Valid components: {', '.join(valid_components)}")
            return
    
    # Confirm update
    if not ctx.obj.get("quiet", False):
        update_type = "selective" if selective_components else "full"
        preserve_msg = " (preserving personal configs)" if preserve_personal else ""
        
        console.print(f"[yellow]This will perform a {update_type} update{preserve_msg}[/yellow]")
        
        if not click.confirm("Continue with update?"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return
    
    # Perform update
    console.print("[blue]Updating configuration...[/blue]")
    
    success = update_manager.update_configuration(
        preserve_personal=preserve_personal,
        selective_update=selective_components
    )
    
    if success:
        console.print("[bold green]✅ Configuration updated successfully![/bold green]")
        console.print("\nNext steps:")
        console.print("1. Validate configuration: [cyan]ai-config validate[/cyan]")
        console.print("2. Test your setup: [cyan]q chat[/cyan]")
    else:
        console.print("[bold red]❌ Configuration update failed![/bold red]")
        console.print("Your previous configuration has been restored from backup.")
        sys.exit(1)


@cli.group()
def profile() -> None:
    """Manage configuration profiles."""
    pass


@profile.command("list")
@click.pass_context
def profile_list(ctx: click.Context) -> None:
    """List available profiles."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    active_profile = config_manager.get_active_profile()
    
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return
    
    table = Table(title="Available Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Status", style="green")
    
    for profile_name in profiles:
        status = "Active" if profile_name == active_profile else ""
        table.add_row(profile_name, status)
    
    console.print(table)


@profile.command("switch")
@click.argument("profile_name")
@click.pass_context
def profile_switch(ctx: click.Context, profile_name: str) -> None:
    """Switch to a different profile."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    
    if profile_name not in profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        console.print(f"Available profiles: {', '.join(profiles)}")
        sys.exit(1)
    
    console.print(f"[yellow]Switching to profile '{profile_name}' - functionality coming soon![/yellow]")


@cli.command()
@click.option(
    "--description", "-d",
    help="Description for the backup"
)
@click.pass_context
def backup(ctx: click.Context, description: Optional[str]) -> None:
    """Backup current configuration."""
    config_manager = ctx.obj["config_manager"]
    
    if not config_manager.config_dir.exists():
        console.print("[red]No configuration found to backup.[/red]")
        sys.exit(1)
    
    console.print("[blue]Creating backup...[/blue]")
    backup_id = config_manager.create_backup(description)
    
    if backup_id:
        console.print(f"[green]✅ Backup created successfully: {backup_id}[/green]")
    else:
        console.print("[red]❌ Failed to create backup.[/red]")
        sys.exit(1)


@cli.command()
@click.argument("backup_id")
@click.pass_context
def restore(ctx: click.Context, backup_id: str) -> None:
    """Restore configuration from backup."""
    config_manager = ctx.obj["config_manager"]
    
    # List available backups if backup_id is 'list'
    if backup_id.lower() == "list":
        backups = config_manager.list_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
            return
        
        table = Table(title="Available Backups")
        table.add_column("Backup ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Profile", style="magenta")
        
        for backup in backups:
            table.add_row(
                backup.backup_id,
                backup.timestamp,
                backup.description or "",
                backup.profile or ""
            )
        
        console.print(table)
        return
    
    console.print(f"[blue]Restoring from backup: {backup_id}[/blue]")
    success = config_manager.restore_backup(backup_id)
    
    if success:
        console.print(f"[green]✅ Configuration restored successfully from {backup_id}[/green]")
    else:
        console.print(f"[red]❌ Failed to restore from backup {backup_id}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate current configuration."""
    config_manager = ctx.obj["config_manager"]
    
    console.print("[bold blue]Validating Amazon Q CLI Configuration[/bold blue]\n")
    
    result = config_manager.validate_configuration()
    
    # Show validation results
    for item, status in result.checked_items.items():
        icon = "✅" if status else "❌"
        color = "green" if status else "red"
        item_name = item.replace("_", " ").title()
        console.print(f"{icon} {item_name}: [{color}]{'OK' if status else 'Failed'}[/{color}]")
    
    # Show errors
    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result.errors:
            console.print(f"  • {error}")
    
    # Show warnings
    if result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}")
    
    if result.is_valid:
        console.print("\n[bold green]✅ Configuration is valid![/bold green]")
    else:
        console.print("\n[bold red]❌ Configuration has errors that need to be fixed.[/bold red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current configuration status."""
    config_manager = ctx.obj["config_manager"]
    state = config_manager.get_configuration_state()
    
    # Create status table
    table = Table(title="AI Configurator Status", show_header=False)
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Platform", state.platform)
    table.add_row("AI Configurator Version", state.ai_configurator_version)
    table.add_row("Amazon Q CLI", "✅ Installed" if state.amazonq_installed else "❌ Not Found")
    
    if state.amazonq_version:
        table.add_row("Amazon Q Version", state.amazonq_version)
    
    table.add_row("Config Directory", state.config_dir_path)
    table.add_row("Config Exists", "✅ Yes" if state.config_dir_exists else "❌ No")
    
    if state.active_profile:
        table.add_row("Active Profile", state.active_profile)
    
    if state.installed_mcp_servers:
        table.add_row("MCP Servers", f"{len(state.installed_mcp_servers)} installed")
    
    if state.last_backup:
        table.add_row("Last Backup", state.last_backup)
    
    console.print(table)


@cli.command()
@click.option(
    "--cleanup",
    is_flag=True,
    help="Clean up old files and free disk space"
)
@click.pass_context
def maintenance(ctx: click.Context, cleanup: bool) -> None:
    """Show maintenance status and perform cleanup."""
    from .core import UpdateManager
    
    config_manager = ctx.obj["config_manager"]
    update_manager = UpdateManager(ctx.obj["platform"], config_manager)
    
    if cleanup:
        console.print("[blue]Performing cleanup...[/blue]")
        
        cleanup_result = update_manager.cleanup_old_files()
        
        # Show cleanup results
        table = Table(title="Cleanup Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files Removed", str(len(cleanup_result["removed_files"])))
        table.add_row("Space Freed", f"{cleanup_result['freed_space']:,} bytes")
        table.add_row("Errors", str(len(cleanup_result["errors"])))
        
        console.print(table)
        
        if cleanup_result["removed_files"]:
            console.print("\n[bold blue]Removed Files:[/bold blue]")
            for file_path in cleanup_result["removed_files"][:10]:
                console.print(f"  🗑️ {file_path}")
            
            if len(cleanup_result["removed_files"]) > 10:
                console.print(f"  ... and {len(cleanup_result['removed_files']) - 10} more files")
        
        if cleanup_result["errors"]:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in cleanup_result["errors"]:
                console.print(f"  ❌ {error}")
        
        if cleanup_result["freed_space"] > 0:
            console.print(f"\n[bold green]✅ Cleanup completed! Freed {cleanup_result['freed_space']:,} bytes[/bold green]")
        else:
            console.print("\n[yellow]No cleanup needed[/yellow]")
    else:
        # Show maintenance status
        status = update_manager.get_maintenance_status()
        
        # Create status table
        table = Table(title="Maintenance Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # Health status
        health_color = {"good": "green", "fair": "yellow", "poor": "red"}.get(status["config_health"], "white")
        table.add_row("Configuration Health", status["config_health"].title(), f"[{health_color}]●[/{health_color}]")
        
        # Last update
        last_update = status["last_update"] or "Never"
        table.add_row("Last Update", last_update, "")
        
        # Backup count
        backup_status = "🟢 Good" if status["backup_count"] < 20 else "🟡 Many"
        table.add_row("Backup Count", str(status["backup_count"]), backup_status)
        
        # Disk usage
        disk_mb = status["disk_usage"] / (1024 * 1024)
        disk_status = "🟢 Good" if disk_mb < 100 else "🟡 Large"
        table.add_row("Disk Usage", f"{disk_mb:.1f} MB", disk_status)
        
        console.print(table)
        
        # Show recommendations
        if status["recommendations"]:
            console.print("\n[bold blue]Recommendations:[/bold blue]")
            for rec in status["recommendations"]:
                console.print(f"  💡 {rec}")
        else:
            console.print("\n[bold green]✅ System is well maintained![/bold green]")


# Add command groups
cli.add_command(context)
cli.add_command(hooks)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
