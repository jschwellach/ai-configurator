"""
Simplified library command for AI Configurator.
"""

import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.library_manager import LibraryManager
from ..core.profile_installer import ProfileInstaller
from ..core.catalog_schema import ConfigItem

console = Console()


@click.group()
def library():
    """Manage configuration library."""
    pass


@library.command("browse")
@click.option("--query", "-q", help="Search query")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.pass_context
def browse(ctx: click.Context, query: str, format: str) -> None:
    """Browse available configurations."""
    library_manager = LibraryManager()
    
    try:
        configs = library_manager.search_configurations(query=query)
        
        if not configs:
            console.print("No configurations found matching the criteria.")
            return
        
        if format == "json":
            configs_data = [
                {
                    "id": config.id,
                    "name": config.name,
                    "description": config.description,
                    "version": config.version,
                    "file_path": config.file_path
                }
                for config in configs
            ]
            console.print(json.dumps(configs_data, indent=2))
        else:
            table = Table(title="Available Configurations")
            table.add_column("Name", style="cyan", width=25)
            table.add_column("ID", style="blue", width=30)
            table.add_column("Version", style="green", width=10)
            table.add_column("Description", style="white", width=50)
            
            for config in configs:
                table.add_row(
                    config.name,
                    config.id,
                    config.version,
                    config.description[:47] + "..." if len(config.description) > 50 else config.description
                )
            
            console.print(table)
            console.print(f"\nFound {len(configs)} configurations")
    
    finally:
        library_manager.shutdown()


@library.command("info")
@click.argument("config_id")
@click.option("--format", "-f", type=click.Choice(["panel", "json"]), default="panel", help="Output format")
@click.pass_context
def info(ctx: click.Context, config_id: str, format: str) -> None:
    """Show detailed information about a configuration."""
    library_manager = LibraryManager()
    
    try:
        config = library_manager.get_configuration_by_id(config_id)
        
        if not config:
            console.print(f"[red]Configuration '{config_id}' not found.[/red]")
            return
        
        if format == "json":
            config_data = {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "version": config.version,
                "file_path": config.file_path
            }
            console.print(json.dumps(config_data, indent=2))
        else:
            console.print(Panel(f"[bold cyan]{config.name}[/bold cyan]", title="Configuration", border_style="cyan"))
            console.print(f"[bold]ID:[/bold] {config.id}")
            console.print(f"[bold]Version:[/bold] {config.version}")
            console.print(f"[bold]File Path:[/bold] {config.file_path}")
            console.print(Panel(config.description, title="Description", border_style="green"))
    
    finally:
        library_manager.shutdown()


@library.command("install")
@click.argument("config_id")
@click.pass_context
def install(ctx: click.Context, config_id: str) -> None:
    """Install a configuration profile."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        # Check if profile exists
        config = library_manager.get_configuration_by_id(config_id)
        if not config:
            console.print(f"[red]Configuration '{config_id}' not found.[/red]")
            return
        
        # Check if already installed
        if installer.is_profile_installed(config_id):
            console.print(f"[yellow]Profile '{config.name}' is already installed.[/yellow]")
            return
        
        # Install the profile
        console.print(f"Installing profile: [cyan]{config.name}[/cyan]")
        
        if installer.install_profile(config_id):
            console.print(f"[green]✅ Successfully installed profile: {config.name}[/green]")
        else:
            console.print(f"[red]❌ Failed to install profile: {config.name}[/red]")
    
    finally:
        library_manager.shutdown()


@library.command("remove")
@click.argument("config_id")
@click.pass_context
def remove(ctx: click.Context, config_id: str) -> None:
    """Remove an installed configuration profile."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        # Check if profile exists
        config = library_manager.get_configuration_by_id(config_id)
        if not config:
            console.print(f"[red]Configuration '{config_id}' not found.[/red]")
            return
        
        # Check if installed
        if not installer.is_profile_installed(config_id):
            console.print(f"[yellow]Profile '{config.name}' is not installed.[/yellow]")
            return
        
        # Remove the profile
        console.print(f"Removing profile: [cyan]{config.name}[/cyan]")
        
        if installer.remove_profile(config_id):
            console.print(f"[green]✅ Successfully removed profile: {config.name}[/green]")
        else:
            console.print(f"[red]❌ Failed to remove profile: {config.name}[/red]")
    
    finally:
        library_manager.shutdown()


@library.command("list")
@click.pass_context
def list_installed(ctx: click.Context) -> None:
    """List installed configuration profiles."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        installed_ids = installer.list_installed_profiles()
        
        if not installed_ids:
            console.print("[yellow]No profiles are currently installed.[/yellow]")
            return
        
        table = Table(title="Installed Profiles")
        table.add_column("Name", style="cyan", width=25)
        table.add_column("ID", style="blue", width=30)
        table.add_column("Version", style="green", width=10)
        
        for profile_id in installed_ids:
            config = library_manager.get_configuration_by_id(profile_id)
            if config:
                table.add_row(config.name, config.id, config.version)
            else:
                table.add_row("Unknown", profile_id, "Unknown")
        
        console.print(table)
        console.print(f"\nFound {len(installed_ids)} installed profiles")
    
    finally:
        library_manager.shutdown()


@library.command("stats")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.pass_context
def stats(ctx: click.Context, format: str) -> None:
    """Show library statistics."""
    library_manager = LibraryManager()
    
    try:
        stats_data = library_manager.get_stats()
        
        if format == "json":
            console.print(json.dumps(stats_data, indent=2))
        else:
            table = Table(title="Library Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Configurations", str(stats_data.get("total_configs", 0)))
            table.add_row("Profiles", str(stats_data.get("profiles", 0)))
            table.add_row("Catalog Version", stats_data.get("version", "Unknown"))
            
            console.print(table)
    
    finally:
        library_manager.shutdown()
