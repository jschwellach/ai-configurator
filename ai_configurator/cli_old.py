"""Main CLI interface for AI Configurator - Library-focused."""

import click
from rich.console import Console

from . import __version__
from .commands.context import context
from .commands.hooks import hooks
from .commands.library import library
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
    """AI Configurator - Library-based configuration manager.
    
    🚀 Get started with: ai-config library browse
    
    Browse, search, and install community-driven configurations for your AI development workflow.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    
    # Setup logging
    log_level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    setup_logging(log_level)


# Add command groups - Library-focused CLI
cli.add_command(library)
cli.add_command(context)
cli.add_command(hooks)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()