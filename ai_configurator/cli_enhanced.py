"""
Enhanced CLI interface with Click and Rich.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .models import ToolType, ResourcePath, LibrarySource
from .services import LibraryService, AgentService, ConfigService

console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """AI Configurator - Enhanced tool-agnostic knowledge library manager."""
    ctx.ensure_object(dict)
    
    # Set up paths
    config_dir = Path.home() / ".config" / "ai-configurator"
    ctx.obj['config_dir'] = config_dir
    ctx.obj['library_service'] = LibraryService(
        config_dir / "library",
        config_dir / "personal"
    )
    ctx.obj['agent_service'] = AgentService(config_dir / "agents")
    ctx.obj['config_service'] = ConfigService(config_dir)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status and configuration."""
    config_dir = ctx.obj['config_dir']
    
    console.print(Panel.fit(
        f"[bold blue]AI Configurator v4.0.0[/bold blue]\n"
        f"Config Directory: {config_dir}",
        title="System Status"
    ))
    
    # Show library status
    library_service = ctx.obj['library_service']
    library = library_service.create_library()
    conflicts = library_service.sync_library(library)
    
    console.print(f"\n📚 [bold]Library Status[/bold]")
    console.print(f"   Base Library: {library.base_path}")
    console.print(f"   Personal Library: {library.personal_path}")
    console.print(f"   Files: {len(library.files)}")
    console.print(f"   Conflicts: {len(conflicts)}")
    
    # Show agents
    agent_service = ctx.obj['agent_service']
    agents = agent_service.list_agents()
    
    console.print(f"\n🤖 [bold]Agents[/bold]")
    if agents:
        table = Table()
        table.add_column("Name")
        table.add_column("Tool")
        table.add_column("Resources")
        table.add_column("Status")
        
        for agent in agents:
            status_color = "green" if agent.health_status.value == "healthy" else "red"
            table.add_row(
                agent.name,
                agent.tool_type.value,
                str(len(agent.config.resources)),
                f"[{status_color}]{agent.health_status.value}[/{status_color}]"
            )
        console.print(table)
    else:
        console.print("   No agents found")


@cli.command()
@click.pass_context
def library(ctx):
    """Manage knowledge library."""
    library_service = ctx.obj['library_service']
    library = library_service.create_library()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Syncing library...", total=None)
        conflicts = library_service.sync_library(library)
        progress.update(task, completed=True)
    
    console.print(f"\n📚 [bold green]Library Synced[/bold green]")
    console.print(f"   Files: {len(library.files)}")
    console.print(f"   Conflicts: {len(conflicts)}")
    
    if conflicts:
        console.print(f"\n⚠️  [bold yellow]Conflicts Found[/bold yellow]")
        for conflict in conflicts:
            console.print(f"   • {conflict.file_path} ({conflict.conflict_type.value})")
    
    # Show discovered files
    files = library_service.discover_files(library)
    if files:
        console.print(f"\n📄 [bold]Available Files[/bold]")
        for i, file_path in enumerate(files, 1):
            console.print(f"   {i:2d}. {file_path}")


@cli.command()
@click.option('--name', prompt='Agent name', help='Name for the new agent')
@click.option('--tool', type=click.Choice(['q-cli', 'claude', 'chatgpt']), 
              default='q-cli', help='Target AI tool')
@click.option('--description', default='', help='Agent description')
@click.pass_context
def create_agent(ctx, name, tool, description):
    """Create a new AI agent."""
    agent_service = ctx.obj['agent_service']
    library_service = ctx.obj['library_service']
    
    tool_type = ToolType(tool)
    
    # Check if agent exists
    if agent_service.agent_exists(name, tool_type):
        console.print(f"[red]Agent '{name}' already exists for {tool}[/red]")
        return
    
    # Create agent
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating agent...", total=None)
        agent = agent_service.create_agent(name, tool_type, description)
        progress.update(task, completed=True)
    
    if not agent:
        console.print("[red]Failed to create agent[/red]")
        return
    
    console.print(f"\n🤖 [bold green]Agent Created[/bold green]")
    console.print(f"   Name: {agent.name}")
    console.print(f"   Tool: {agent.tool_type.value}")
    console.print(f"   Description: {agent.config.description}")
    
    # Ask to add resources
    if Confirm.ask("\nAdd knowledge resources?"):
        _add_resources_interactive(agent, library_service, agent_service)


@cli.command()
@click.pass_context
def list_agents(ctx):
    """List all agents."""
    agent_service = ctx.obj['agent_service']
    agents = agent_service.list_agents()
    
    if not agents:
        console.print("No agents found")
        return
    
    table = Table(title="AI Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Tool", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Resources", justify="right", style="green")
    table.add_column("Status", style="yellow")
    
    for agent in agents:
        status_color = "green" if agent.health_status.value == "healthy" else "red"
        table.add_row(
            agent.name,
            agent.tool_type.value,
            agent.config.description or "No description",
            str(len(agent.config.resources)),
            f"[{status_color}]{agent.health_status.value}[/{status_color}]"
        )
    
    console.print(table)


@cli.command()
@click.argument('name')
@click.option('--tool', type=click.Choice(['q-cli', 'claude', 'chatgpt']), 
              default='q-cli', help='Target AI tool')
@click.pass_context
def show_agent(ctx, name, tool):
    """Show detailed agent information."""
    agent_service = ctx.obj['agent_service']
    tool_type = ToolType(tool)
    
    agent = agent_service.load_agent(name, tool_type)
    if not agent:
        console.print(f"[red]Agent '{name}' not found[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold]{agent.name}[/bold]\n"
        f"Tool: {agent.tool_type.value}\n"
        f"Description: {agent.config.description or 'No description'}\n"
        f"Status: {agent.health_status.value}\n"
        f"Created: {agent.config.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"Updated: {agent.config.updated_at.strftime('%Y-%m-%d %H:%M')}",
        title="Agent Details"
    ))
    
    if agent.config.resources:
        console.print(f"\n📄 [bold]Resources ({len(agent.config.resources)})[/bold]")
        for i, resource in enumerate(agent.config.resources, 1):
            console.print(f"   {i:2d}. {resource.path} ({resource.source.value})")
    
    if agent.config.mcp_servers:
        console.print(f"\n🔧 [bold]MCP Servers ({len(agent.config.mcp_servers)})[/bold]")
        for name, config in agent.config.mcp_servers.items():
            console.print(f"   • {name}: {config.command}")


@cli.command()
@click.argument('name')
@click.option('--tool', type=click.Choice(['q-cli', 'claude', 'chatgpt']), 
              default='q-cli', help='Target AI tool')
@click.option('--save', is_flag=True, help='Save to target tool directory')
@click.pass_context
def export_agent(ctx, name, tool, save):
    """Export agent configuration for target tool."""
    agent_service = ctx.obj['agent_service']
    library_service = ctx.obj['library_service']
    tool_type = ToolType(tool)
    
    agent = agent_service.load_agent(name, tool_type)
    if not agent:
        console.print(f"[red]Agent '{name}' not found[/red]")
        return
    
    config = agent_service.export_for_tool(agent)
    
    # Fix resource paths to be absolute for Q CLI
    if tool == 'q-cli':
        config_dir = ctx.obj['config_dir']
        base_library = config_dir / "library"
        personal_library = config_dir / "personal"
        
        fixed_resources = []
        for resource_uri in config.get("resources", []):
            resource_path = resource_uri.replace("file://", "")
            
            # Check personal library first, then base
            personal_file = personal_library / resource_path
            base_file = base_library / resource_path
            
            if personal_file.exists():
                fixed_resources.append(f"file://{personal_file}")
            elif base_file.exists():
                fixed_resources.append(f"file://{base_file}")
            else:
                fixed_resources.append(resource_uri)
        
        config["resources"] = fixed_resources
        config["description"] = f"{name} created with AI Configurator v4.0"
    
    if save:
        # Save to target tool directory
        if tool == 'q-cli':
            q_cli_dir = Path.home() / ".aws" / "amazonq" / "cli-agents"
            q_cli_dir.mkdir(parents=True, exist_ok=True)
            agent_file = q_cli_dir / f"{name}.json"
            
            try:
                import json
                with open(agent_file, 'w') as f:
                    json.dump(config, f, indent=2)
                console.print(f"\n✅ [bold green]Agent saved to Q CLI[/bold green]")
                console.print(f"   File: {agent_file}")
                console.print(f"   Resources: {len(config.get('resources', []))}")
            except Exception as e:
                console.print(f"[red]Failed to save: {e}[/red]")
        else:
            console.print(f"[yellow]Save not implemented for {tool} yet[/yellow]")
    else:
        console.print(f"\n🔧 [bold]Exported Configuration for {tool}[/bold]")
        console.print(Panel(
            str(config).replace("'", '"'),
            title=f"{name} - {tool} Configuration",
            expand=False
        ))
        console.print(f"\n[dim]Use --save flag to save to {tool} directory[/dim]")


@cli.command()
@click.argument('name')
@click.option('--tool', type=click.Choice(['q-cli', 'claude', 'chatgpt']), 
              default='q-cli', help='Target AI tool')
@click.pass_context
def manage_agent(ctx, name, tool):
    """Interactively manage agent resources and MCP servers."""
    agent_service = ctx.obj['agent_service']
    library_service = ctx.obj['library_service']
    tool_type = ToolType(tool)
    
    agent = agent_service.load_agent(name, tool_type)
    if not agent:
        console.print(f"[red]Agent '{name}' not found[/red]")
        return
    
    while True:
        # Show current agent status
        console.print(f"\n🤖 [bold]Managing Agent: {agent.name}[/bold]")
        console.print(f"   Resources: {len(agent.config.resources)}")
        console.print(f"   MCP Servers: {len(agent.config.mcp_servers)}")
        
        # Show menu
        console.print(f"\n[bold]What would you like to do?[/bold]")
        console.print("1. Add/Remove Resources")
        console.print("2. Add MCP Server")
        console.print("3. Remove MCP Server")
        console.print("4. View Agent Details")
        console.print("5. Export to Q CLI")
        console.print("6. Save and Exit")
        
        choice = Prompt.ask("\nSelect option", choices=['1', '2', '3', '4', '5', '6'], default='6')
        
        if choice == '1':
            _manage_resources_interactive(agent, library_service, agent_service)
        elif choice == '2':
            _add_mcp_interactive(agent, agent_service)
        elif choice == '3':
            _remove_mcp_interactive(agent, agent_service)
        elif choice == '4':
            _show_agent_details(agent)
        elif choice == '5':
            _export_agent_interactive(agent, ctx)
        elif choice == '6':
            if agent_service.update_agent(agent):
                console.print(f"\n✅ [green]Agent '{agent.name}' saved successfully[/green]")
            else:
                console.print(f"\n❌ [red]Failed to save agent[/red]")
            break


def _manage_resources_interactive(agent, library_service, agent_service):
    """Interactive resource management."""
    while True:
        console.print(f"\n📄 [bold]Current Resources ({len(agent.config.resources)})[/bold]")
        for i, resource in enumerate(agent.config.resources, 1):
            console.print(f"   {i:2d}. {resource.path} ({resource.source.value})")
        
        console.print(f"\n[bold]Resource Management[/bold]")
        console.print("1. Add Resource")
        console.print("2. Remove Resource")
        console.print("3. Back to Main Menu")
        
        choice = Prompt.ask("Select option", choices=['1', '2', '3'], default='3')
        
        if choice == '1':
            _add_resources_interactive(agent, library_service, agent_service)
        elif choice == '2':
            if agent.config.resources:
                try:
                    index = int(Prompt.ask("Enter resource number to remove")) - 1
                    if 0 <= index < len(agent.config.resources):
                        removed = agent.config.resources.pop(index)
                        console.print(f"[green]Removed: {removed.path}[/green]")
                    else:
                        console.print("[red]Invalid resource number[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
            else:
                console.print("[yellow]No resources to remove[/yellow]")
        elif choice == '3':
            break


def _add_mcp_interactive(agent, agent_service):
    """Interactive MCP server addition."""
    console.print(f"\n🔧 [bold]Add MCP Server[/bold]")
    
    # Show common MCP servers
    console.print("\n[bold]Common MCP Servers:[/bold]")
    console.print("1. fetch (mcp-server-fetch)")
    console.print("2. awslabs.core-mcp-server")
    console.print("3. aws-documentation-mcp-server")
    console.print("4. cdk-mcp-server")
    console.print("5. Custom server")
    
    choice = Prompt.ask("Select server", choices=['1', '2', '3', '4', '5'], default='5')
    
    if choice == '1':
        server_name = "fetch"
        command = "uvx"
        args = ["mcp-server-fetch"]
    elif choice == '2':
        server_name = "awslabs.core-mcp-server"
        command = "uvx"
        args = ["awslabs.core-mcp-server@latest"]
    elif choice == '3':
        server_name = "aws-documentation-mcp-server"
        command = "uvx"
        args = ["aws-documentation-mcp-server"]
    elif choice == '4':
        server_name = "cdk-mcp-server"
        command = "uvx"
        args = ["cdk-mcp-server"]
    else:
        server_name = Prompt.ask("Server name")
        command = Prompt.ask("Command")
        args_input = Prompt.ask("Arguments (comma-separated)", default="")
        args = [arg.strip() for arg in args_input.split(',')] if args_input else []
    
    # Create MCP server config
    from .models import MCPServerConfig
    mcp_config = MCPServerConfig(
        command=command,
        args=args,
        env={},
        disabled=False
    )
    
    # Add to agent
    agent.configure_mcp_server(server_name, mcp_config)
    console.print(f"[green]Added MCP server: {server_name}[/green]")


def _remove_mcp_interactive(agent, agent_service):
    """Interactive MCP server removal."""
    if not agent.config.mcp_servers:
        console.print("[yellow]No MCP servers to remove[/yellow]")
        return
    
    console.print(f"\n🔧 [bold]Current MCP Servers[/bold]")
    servers = list(agent.config.mcp_servers.keys())
    for i, server_name in enumerate(servers, 1):
        server_config = agent.config.mcp_servers[server_name]
        console.print(f"   {i:2d}. {server_name}: {server_config.command}")
    
    try:
        index = int(Prompt.ask("Enter server number to remove")) - 1
        if 0 <= index < len(servers):
            server_name = servers[index]
            del agent.config.mcp_servers[server_name]
            console.print(f"[green]Removed MCP server: {server_name}[/green]")
        else:
            console.print("[red]Invalid server number[/red]")
    except ValueError:
        console.print("[red]Please enter a valid number[/red]")


def _show_agent_details(agent):
    """Show detailed agent information."""
    console.print(f"\n🤖 [bold]Agent Details: {agent.name}[/bold]")
    console.print(f"   Tool: {agent.tool_type.value}")
    console.print(f"   Description: {agent.config.description or 'No description'}")
    console.print(f"   Status: {agent.health_status.value}")
    console.print(f"   Created: {agent.config.created_at.strftime('%Y-%m-%d %H:%M')}")
    console.print(f"   Updated: {agent.config.updated_at.strftime('%Y-%m-%d %H:%M')}")
    
    if agent.config.resources:
        console.print(f"\n📄 [bold]Resources ({len(agent.config.resources)})[/bold]")
        for i, resource in enumerate(agent.config.resources, 1):
            console.print(f"   {i:2d}. {resource.path} ({resource.source.value})")
    
    if agent.config.mcp_servers:
        console.print(f"\n🔧 [bold]MCP Servers ({len(agent.config.mcp_servers)})[/bold]")
        for name, config in agent.config.mcp_servers.items():
            console.print(f"   • {name}: {config.command}")


def _export_agent_interactive(agent, ctx):
    """Interactive agent export."""
    console.print(f"\n🔧 [bold]Export Agent: {agent.name}[/bold]")
    
    if Confirm.ask("Export and save to Q CLI directory?"):
        # Use the existing export logic
        agent_service = ctx.obj['agent_service']
        config_dir = ctx.obj['config_dir']
        
        config = agent_service.export_for_tool(agent)
        
        # Fix resource paths
        base_library = config_dir / "library"
        personal_library = config_dir / "personal"
        
        fixed_resources = []
        for resource_uri in config.get("resources", []):
            resource_path = resource_uri.replace("file://", "")
            personal_file = personal_library / resource_path
            base_file = base_library / resource_path
            
            if personal_file.exists():
                fixed_resources.append(f"file://{personal_file}")
            elif base_file.exists():
                fixed_resources.append(f"file://{base_file}")
            else:
                fixed_resources.append(resource_uri)
        
        config["resources"] = fixed_resources
        config["description"] = f"{agent.name} created with AI Configurator v4.0"
        
        # Save to Q CLI
        q_cli_dir = Path.home() / ".aws" / "amazonq" / "cli-agents"
        q_cli_dir.mkdir(parents=True, exist_ok=True)
        agent_file = q_cli_dir / f"{agent.name}.json"
        
        try:
            import json
            with open(agent_file, 'w') as f:
                json.dump(config, f, indent=2)
            console.print(f"✅ [green]Agent exported to Q CLI: {agent_file}[/green]")
        except Exception as e:
            console.print(f"[red]Export failed: {e}[/red]")


@cli.command()
@click.argument('agent_name')
@click.argument('server_name')
@click.argument('command')
@click.option('--args', default='', help='Command arguments (comma-separated)')
@click.option('--tool', type=click.Choice(['q-cli', 'claude', 'chatgpt']), 
              default='q-cli', help='Target AI tool')
@click.pass_context
def add_mcp(ctx, agent_name, server_name, command, args, tool):
    """Add MCP server to an agent."""
    agent_service = ctx.obj['agent_service']
    tool_type = ToolType(tool)
    
    agent = agent_service.load_agent(agent_name, tool_type)
    if not agent:
        console.print(f"[red]Agent '{agent_name}' not found[/red]")
        return
    
    # Parse args
    server_args = [arg.strip() for arg in args.split(',')] if args else []
    
    # Create MCP server config
    from .models import MCPServerConfig
    mcp_config = MCPServerConfig(
        command=command,
        args=server_args,
        env={},
        disabled=False
    )
    
    # Add to agent
    agent.configure_mcp_server(server_name, mcp_config)
    
    # Save agent
    if agent_service.update_agent(agent):
        console.print(f"✅ [green]Added MCP server '{server_name}' to agent '{agent_name}'[/green]")
        console.print(f"   Command: {command}")
        if server_args:
            console.print(f"   Args: {server_args}")
    else:
        console.print("[red]Failed to update agent[/red]")


def _add_resources_interactive(agent, library_service, agent_service):
    """Interactive resource addition."""
    library = library_service.create_library()
    library_service.sync_library(library)
    files = library_service.discover_files(library)
    
    if not files:
        console.print("No library files found")
        return
    
    console.print(f"\n📄 [bold]Available Files[/bold]")
    for i, file_path in enumerate(files, 1):
        console.print(f"   {i:2d}. {file_path}")
    
    while True:
        choice = Prompt.ask(
            "\nEnter file number to add (or 'done' to finish)",
            default="done"
        )
        
        if choice.lower() == 'done':
            break
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(files):
                file_path = files[index]
                
                # Determine source (simplified - assume base for now)
                resource = ResourcePath(path=file_path, source=LibrarySource.BASE)
                agent.add_resource(resource)
                
                console.print(f"[green]Added: {file_path}[/green]")
            else:
                console.print("[red]Invalid file number[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number or 'done'[/red]")
    
    # Save updated agent
    if agent_service.update_agent(agent):
        console.print(f"\n[green]Agent updated with {len(agent.config.resources)} resources[/green]")
    else:
        console.print("[red]Failed to save agent[/red]")


if __name__ == '__main__':
    cli()
