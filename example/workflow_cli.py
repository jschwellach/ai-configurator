"""CLI interface for workflow management."""

import click
import json
from .workflow import Workflow


@click.group()
def workflow():
    """Workflow state management commands."""
    pass


@workflow.command()
@click.argument('name')
@click.option('--data', help='JSON data for the step')
def add(name, data):
    """Add a step to the workflow."""
    wf = Workflow()
    step_data = json.loads(data) if data else None
    wf.add_step(name, step_data)
    click.echo(f"Added step: {name}")


@workflow.command()
@click.option('--step', type=int, help='Step index to complete (default: current)')
def complete(step):
    """Complete a workflow step."""
    wf = Workflow()
    if wf.complete_step(step):
        click.echo(f"Completed step {step if step is not None else 'current'}")
    else:
        click.echo("Failed to complete step")


@workflow.command()
def status():
    """Show workflow status."""
    wf = Workflow()
    status = wf.get_status()
    current = wf.get_current_step()
    
    click.echo(f"Status: {status['status']}")
    click.echo(f"Progress: {status['completed_steps']}/{status['total_steps']}")
    
    if current:
        click.echo(f"Current step: {current['name']}")


@workflow.command()
def reset():
    """Reset workflow state."""
    wf = Workflow()
    wf.reset()
    click.echo("Workflow reset")


if __name__ == '__main__':
    workflow()