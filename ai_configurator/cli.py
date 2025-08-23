"""Final simplified CLI interface for AI Configurator - Agent-based version."""

import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ai_configurator import __version__
from ai_configurator.core.config_library_manager import ConfigLibraryManager
from ai_configurator.core.agent_installer import AgentInstaller

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
    """AI Configurator - Install profiles as Amazon Q CLI agents."""
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
    library_manager = ConfigLibraryManager()
    installer = AgentInstaller(library_manager)
    
    try:
        profiles = library_manager.get_profiles()
        
        # Apply search filter if provided
        if query:
            query_lower = query.lower()
            profiles = [
                p for p in profiles 
                if query_lower in p.name.lower() or query_lower in p.description.lower() or query_lower in p.id.lower()
            ]
        
        if not profiles:
            console.print("No profiles found matching the criteria.")
            return
        
        if format == "json":
            profiles_data = [
                {
                    "id": profile.id,
                    "name": profile.name,
                    "description": profile.description,
                    "version": profile.version,
                    "installed": installer.is_profile_installed(profile.id)
                }
                for profile in profiles
            ]
            console.print(json.dumps(profiles_data, indent=2))
        else:
            table = Table(title="Available Profiles")
            table.add_column("Name", style="cyan", width=25)
            table.add_column("ID", style="blue", width=30)
            table.add_column("Version", style="green", width=10)
            table.add_column("Status", style="yellow", width=12)
            table.add_column("Description", style="white", width=40)
            
            for profile in profiles:
                status = "✅ Installed" if installer.is_profile_installed(profile.id) else "❌ Not Installed"
                table.add_row(
                    profile.name,
                    profile.id,
                    profile.version,
                    status,
                    profile.description[:37] + "..." if len(profile.description) > 40 else profile.description
                )
            
            console.print(table)
            console.print(f"\nFound {len(profiles)} profiles")
            console.print("[dim]Use 'q chat --agent <ID>' to use an installed agent[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("install")
@click.argument("profile_id")
def install_profile(profile_id: str) -> None:
    """Install a profile as an Amazon Q CLI agent."""
    library_manager = ConfigLibraryManager()
    installer = AgentInstaller(library_manager)
    
    try:
        # Check if profile exists
        profile = library_manager.get_profile_by_id(profile_id)
        if not profile:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            console.print("\nUse 'ai-config list' to see available profiles.")
            return
        
        # Check if already installed
        if installer.is_profile_installed(profile_id):
            console.print(f"[yellow]Agent '{profile.name}' is already installed.[/yellow]")
            console.print(f"[dim]Use: q chat --agent {profile_id}[/dim]")
            return
        
        # Install the profile
        console.print(f"Installing agent: [cyan]{profile.name}[/cyan]")
        
        if installer.install_profile(profile_id):
            console.print(f"[green]✅ Successfully installed agent: {profile.name}[/green]")
            console.print(f"[dim]Use: q chat --agent {profile_id}[/dim]")
        else:
            console.print(f"[red]❌ Failed to install agent: {profile.name}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("remove")
@click.argument("profile_id")
def remove_profile(profile_id: str) -> None:
    """Remove an installed agent."""
    library_manager = ConfigLibraryManager()
    installer = AgentInstaller(library_manager)
    
    try:
        # Check if profile exists
        profile = library_manager.get_profile_by_id(profile_id)
        if not profile:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            return
        
        # Check if installed
        if not installer.is_profile_installed(profile_id):
            console.print(f"[yellow]Agent '{profile.name}' is not installed.[/yellow]")
            return
        
        # Remove the profile
        console.print(f"Removing agent: [cyan]{profile.name}[/cyan]")
        
        if installer.remove_profile(profile_id):
            console.print(f"[green]✅ Successfully removed agent: {profile.name}[/green]")
        else:
            console.print(f"[red]❌ Failed to remove agent: {profile.name}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("info")
@click.argument("profile_id")
@click.option("--format", "-f", type=click.Choice(["panel", "json"]), default="panel", help="Output format")
def show_info(profile_id: str, format: str) -> None:
    """Show detailed information about a profile."""
    library_manager = ConfigLibraryManager()
    installer = AgentInstaller(library_manager)
    
    try:
        profile = library_manager.get_profile_by_id(profile_id)
        
        if not profile:
            console.print(f"[red]Profile '{profile_id}' not found.[/red]")
            return
        
        is_installed = installer.is_profile_installed(profile_id)
        
        if format == "json":
            profile_data = {
                "id": profile.id,
                "name": profile.name,
                "description": profile.description,
                "version": profile.version,
                "installed": is_installed
            }
            console.print(json.dumps(profile_data, indent=2))
        else:
            # Show installation status
            status = "[green]✅ Installed[/green]" if is_installed else "[red]❌ Not Installed[/red]"
            
            console.print(Panel(f"[bold cyan]{profile.name}[/bold cyan] - {status}", title="Agent", border_style="cyan"))
            console.print(f"[bold]ID:[/bold] {profile.id}")
            console.print(f"[bold]Version:[/bold] {profile.version}")
            console.print(Panel(profile.description, title="Description", border_style="green"))
            
            if not is_installed:
                console.print(f"\n[dim]To install: ai-config install {profile.id}[/dim]")
                console.print(f"[dim]Then use: q chat --agent {profile.id}[/dim]")
            else:
                console.print(f"\n[dim]To use: q chat --agent {profile.id}[/dim]")
                console.print(f"[dim]To remove: ai-config remove {profile.id}[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("agents")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_installed_agents(format: str) -> None:
    """List installed Amazon Q CLI agents."""
    library_manager = ConfigLibraryManager()
    installer = AgentInstaller(library_manager)
    
    try:
        installed_agents = installer.list_installed_agents()
        
        if not installed_agents:
            console.print("No agents are currently installed.")
            console.print("[dim]Use 'ai-config install <profile-id>' to install an agent[/dim]")
            return
        
        if format == "json":
            console.print(json.dumps(installed_agents, indent=2))
        else:
            table = Table(title="Installed Amazon Q CLI Agents")
            table.add_column("Agent ID", style="cyan", width=30)
            table.add_column("Usage", style="green", width=50)
            
            for agent_id in installed_agents:
                table.add_row(agent_id, f"q chat --agent {agent_id}")
            
            console.print(table)
            console.print(f"\nFound {len(installed_agents)} installed agents")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command("refresh")
def refresh_library() -> None:
    """Refresh the library from source."""
    library_manager = ConfigLibraryManager()
    
    try:
        console.print("Refreshing library from source...")
        if library_manager.refresh_library():
            console.print("[green]✅ Library refreshed successfully[/green]")
        else:
            console.print("[red]❌ Failed to refresh library[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
