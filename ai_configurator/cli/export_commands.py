"""
CLI commands for multi-AI tool export functionality.
"""

import click
from pathlib import Path
from typing import Optional
from ..models.export_targets import AIToolType
from ..models.value_objects import ToolType
from ..services.agent_service import AgentService
from ..services.multi_export_service import MultiExportService
from ..core.config import get_config


@click.group()
def export():
    """Export management commands."""
    pass


@export.command()
@click.argument('agent_name')
@click.option('--target', '-t', 
              type=click.Choice([t.value for t in AIToolType]), 
              help='Export target (default: kiro-cli)')
@click.option('--validate-only', '-v', is_flag=True, 
              help='Only validate, do not export')
def agent(agent_name: str, target: Optional[str], validate_only: bool):
    """Export agent to AI tool."""
    try:
        # Initialize services
        config = get_config()
        agents_dir = Path(config.get('agents_dir', '~/.ai-configurator/agents')).expanduser()
        agent_service = AgentService(agents_dir)
        
        # Load agent (try kiro-cli tool type first)
        agent = agent_service.load_agent(agent_name, ToolType.QCLI)  # Using existing ToolType
        if not agent:
            click.echo(f"❌ Agent '{agent_name}' not found", err=True)
            return
        
        # Determine target
        target_type = AIToolType(target) if target else AIToolType.KIRO_CLI
        
        if validate_only:
            # Basic validation
            if agent.validate():
                click.echo(f"✅ Agent '{agent_name}' is valid for {target_type.value}")
            else:
                click.echo(f"❌ Validation failed: {', '.join(agent.validation_errors)}", err=True)
        else:
            # Export agent
            success, error_msg = agent_service.export_agent(agent, target_type)
            if success:
                click.echo(f"✅ Agent '{agent_name}' exported to {target_type.value}")
            else:
                click.echo(f"❌ Export failed: {error_msg}", err=True)
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@export.command()
def targets():
    """List available export targets."""
    try:
        multi_export_service = MultiExportService()
        available_targets = multi_export_service.get_available_targets()
        
        click.echo("Available export targets:")
        for target_type, target_config in available_targets.items():
            click.echo(f"  • {target_config.name} ({target_type.value})")
            click.echo(f"    Directory: {target_config.export_directory}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@export.command()
@click.argument('target_type', type=click.Choice([t.value for t in AIToolType]))
def set_default(target_type: str):
    """Set default export target."""
    try:
        multi_export_service = MultiExportService()
        target = AIToolType(target_type)
        
        # Validate target is available
        available_targets = multi_export_service.get_available_targets()
        if target not in available_targets:
            click.echo(f"❌ Target '{target_type}' is not available", err=True)
            return
        
        # Set default
        success = multi_export_service.set_default_target(target)
        if success:
            click.echo(f"✅ Default export target set to {target_type}")
        else:
            click.echo("❌ Failed to set default export target", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
