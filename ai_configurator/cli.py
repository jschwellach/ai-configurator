"""Final simplified CLI interface for AI Configurator."""

import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ai_configurator import __version__
from ai_configurator.core.library_manager import LibraryManager
from ai_configurator.core.profile_installer import ProfileInstaller

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
def cli(verbose: bool, quiet: bool) -> None:
    """AI Configurator - Simple tool to install profiles and configurations."""
    # Set up logging based on verbosity
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        import logging
        logging.basicConfig(level=logging.ERROR)


@cli.command("list")
@click.option("--query", "-q", help="Search query")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_profiles(query: str, format: str) -> None:
    """List available profiles."""
    library_manager = LibraryManager()
    
    try:
        configs = library_manager.search_configurations(query=query)
        
        if not configs:
            console.print("No profiles found matching the criteria.")
            return
        
        if format == "json":
            configs_data = [
                {
                    "id": config.id,
                    "name": config.name,
                    "description": config.description,
                    "version": config.version
                }
                for config in configs
            ]
            console.print(json.dumps(configs_data, indent=2))
        else:
            table = Table(title="Available Profiles")
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
            console.print(f"\nFound {len(configs)} profiles")
    
    finally:
        library_manager.shutdown()


@cli.command("install")
@click.argument("profile_id")
def install_profile(profile_id: str) -> None:
    """Install a profile."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        # Check if profile exists
        config = library_manager.get_configuration_by_id(profile_id)
        if not config:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            console.print("\nUse 'ai-config list' to see available profiles.")
            return
        
        # Check if already installed
        if installer.is_profile_installed(profile_id):
            console.print(f"[yellow]Profile '{config.name}' is already installed.[/yellow]")
            return
        
        # Install the profile
        console.print(f"Installing profile: [cyan]{config.name}[/cyan]")
        
        if installer.install_profile(profile_id):
            console.print(f"[green]✅ Successfully installed profile: {config.name}[/green]")
        else:
            console.print(f"[red]❌ Failed to install profile: {config.name}[/red]")
    
    finally:
        library_manager.shutdown()


@cli.command("remove")
@click.argument("profile_id")
def remove_profile(profile_id: str) -> None:
    """Remove an installed profile."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        # Check if profile exists
        config = library_manager.get_configuration_by_id(profile_id)
        if not config:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            return
        
        # Check if installed
        if not installer.is_profile_installed(profile_id):
            console.print(f"[yellow]Profile '{config.name}' is not installed.[/yellow]")
            return
        
        # Remove the profile
        console.print(f"Removing profile: [cyan]{config.name}[/cyan]")
        
        if installer.remove_profile(profile_id):
            console.print(f"[green]✅ Successfully removed profile: {config.name}[/green]")
        else:
            console.print(f"[red]❌ Failed to remove profile: {config.name}[/red]")
    
    finally:
        library_manager.shutdown()


@cli.command("info")
@click.argument("profile_id")
@click.option("--format", "-f", type=click.Choice(["panel", "json"]), default="panel", help="Output format")
def show_info(profile_id: str, format: str) -> None:
    """Show detailed information about a profile."""
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        config = library_manager.get_configuration_by_id(profile_id)
        
        if not config:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            return
        
        is_installed = installer.is_profile_installed(profile_id)
        
        if format == "json":
            config_data = {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "version": config.version,
                "installed": is_installed
            }
            console.print(json.dumps(config_data, indent=2))
        else:
            # Show installation status
            status = "[green]✅ Installed[/green]" if is_installed else "[red]❌ Not Installed[/red]"
            
            console.print(Panel(f"[bold cyan]{config.name}[/bold cyan] - {status}", title="Profile", border_style="cyan"))
            console.print(f"[bold]ID:[/bold] {config.id}")
            console.print(f"[bold]Version:[/bold] {config.version}")
            console.print(Panel(config.description, title="Description", border_style="green"))
            
            if not is_installed:
                console.print(f"\n[dim]To install: ai-config install {config.id}[/dim]")
            else:
                console.print(f"\n[dim]To remove: ai-config remove {config.id}[/dim]")
    
    finally:
        library_manager.shutdown()


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
