"""Simplified CLI interface for AI Configurator."""

import click
from rich.console import Console

from . import __version__
from .commands.library import library

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
    """AI Configurator - Simplified configuration manager for Amazon Q CLI."""
    # Set up logging based on verbosity
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    elif quiet:
        import logging
        logging.basicConfig(level=logging.ERROR)


# Add the library command group
cli.add_command(library)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
