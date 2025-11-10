"""Agent management CLI commands."""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ai_configurator.services.agent_service import AgentService
from ai_configurator.services.wizard_service import WizardService
from ai_configurator.models.value_objects import ToolType

console = Console()


def get_agent_service():
    """Get configured agent service."""
    agents_dir = Path.home() / ".config" / "ai-configurator" / "agents"
    return AgentService(agents_dir)


@click.group()
def agent():
    """Agent management commands."""
    pass


@agent.command()
def list():
    """List all agents."""
    service = get_agent_service()
    agents = service.list_agents()
    
    if not agents:
        console.print("[yellow]No agents found.[/yellow]")
        return
    
    table = Table(title="Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Resources", style="blue")
    table.add_column("Status", style="magenta")
    
    for agent in agents:
        table.add_row(
            agent.name,
            agent.tool_type.value,
            str(len(agent.config.resources)),
            agent.health_status.value
        )
    
    console.print(table)


@agent.command()
@click.argument('name')
def show(name: str):
    """Show agent details."""
    service = get_agent_service()
    agent = service.get_agent(name)
    
    if not agent:
        console.print(f"[red]Agent '{name}' not found.[/red]")
        raise click.Abort()
    
    console.print(f"\n[bold cyan]Agent: {agent.name}[/bold cyan]")
    console.print(f"Tool: {agent.tool_type.value}")
    console.print(f"Resources: {len(agent.config.resources)}")
    console.print(f"Status: {agent.health_status.value}")


@agent.command()
@click.argument('name')
@click.option('--tool', type=click.Choice(['q-cli', 'cursor', 'windsurf']), help='Tool type')
@click.option('--interactive', is_flag=True, help='Interactive creation wizard')
def create(name: str, tool: str, interactive: bool):
    """Create new agent."""
    if interactive:
        wizard = WizardService()
        result = wizard.create_agent_wizard(name)
        console.print(f"[green]✓[/green] Created agent: {result.agent_name}")
    else:
        service = get_agent_service()
        agent = service.create_agent(name, tool or 'q-cli')
        console.print(f"[green]✓[/green] Created agent: {agent.name}")


@agent.command()
@click.argument('name')
def edit(name: str):
    """Edit agent configuration."""
    console.print(f"[yellow]Opening editor for agent: {name}[/yellow]")
    console.print("[dim]Use TUI mode for interactive editing: ai-config[/dim]")


@agent.command()
@click.argument('name')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
def delete(name: str, force: bool):
    """Delete agent."""
    if not force:
        if not click.confirm(f"Delete agent '{name}'?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    service = get_agent_service()
    service.delete_agent(name)
    console.print(f"[green]✓[/green] Deleted agent: {name}")


@agent.command()
@click.argument('name')
def export(name: str):
    """Export agent to target tool."""
    service = get_agent_service()
    
    # Find the agent (we need to know its tool type)
    agents = service.list_agents()
    agent = None
    for a in agents:
        if a.name == name:
            agent = a
            break
    
    if not agent:
        console.print(f"[red]Agent '{name}' not found.[/red]")
        raise click.Abort()
    
    if agent.tool_type == ToolType.Q_CLI:
        result = service.export_to_q_cli(agent)
        if result:
            console.print(f"[green]✓[/green] Exported agent: {name}")
            console.print(f"Location: ~/.aws/amazonq/cli-agents/{name}.json")
        else:
            console.print(f"[red]✗[/red] Failed to export agent: {name}")
    else:
        console.print(f"[yellow]Export not implemented for tool type: {agent.tool_type.value}[/yellow]")


@agent.command()
@click.argument('name')
@click.argument('output_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def export_package(name: str, output_path: str):
    """Export agent as a shareable package.
    
    NAME: Name of the agent to export
    OUTPUT_PATH: Directory where the package should be created
    """
    from ai_configurator.services.import_export_service import ImportExportService
    
    service = get_agent_service()
    import_export_service = ImportExportService(service)
    
    # Find the agent (we need to know its tool type)
    agents = service.list_agents()
    agent = None
    tool_type = None
    for a in agents:
        if a.name == name:
            agent = a
            tool_type = a.tool_type
            break
    
    if not agent:
        console.print(f"[red]Agent '{name}' not found.[/red]")
        raise click.Abort()
    
    output_path_obj = Path(output_path)
    result = import_export_service.export_agent(name, tool_type, output_path_obj)
    
    if result:
        console.print(f"[green]✓[/green] Exported agent package: {name}")
        console.print(f"Location: {output_path_obj / f'{name}_package'}")
    else:
        console.print(f"[red]✗[/red] Failed to export agent package: {name}")


@agent.command()
@click.argument('package_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--name', help='New name for the imported agent')
def import_package(package_path: str, name: str):
    """Import agent from a package.
    
    PACKAGE_PATH: Path to the agent package directory
    """
    from ai_configurator.services.import_export_service import ImportExportService
    
    service = get_agent_service()
    import_export_service = ImportExportService(service)
    
    package_path_obj = Path(package_path)
    result = import_export_service.import_agent(package_path_obj, name)
    
    if result:
        agent_name, tool_type = result
        console.print(f"[green]✓[/green] Imported agent: {agent_name}")
        console.print(f"Tool type: {tool_type.value}")
    else:
        console.print(f"[red]✗[/red] Failed to import agent from package")
