"""Directory structure management commands."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.directory_manager import DirectoryManager, ConfigurationType
import logging

console = Console()
logger = logging.getLogger(__name__)


@click.group()
def structure():
    """Manage configuration directory structure."""
    pass


@structure.command()
@click.option(
    "--base-path", "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Base path for configuration directories (defaults to current directory)"
)
def create(base_path: Path):
    """Create the new directory structure for YAML/Markdown configurations."""
    try:
        directory_manager = DirectoryManager(base_path)
        
        console.print("[bold blue]Creating directory structure...[/bold blue]")
        
        success = directory_manager.create_directory_structure()
        
        if success:
            structure_info = directory_manager.get_directory_structure()
            
            # Display created directories
            table = Table(title="Directory Structure Created")
            table.add_column("Directory Type", style="cyan")
            table.add_column("Path", style="green")
            table.add_column("Status", style="yellow")
            
            directories = {
                "Profiles": structure_info.profiles_dir,
                "Hooks": structure_info.hooks_dir,
                "Contexts": structure_info.contexts_dir,
                "Shared Contexts": structure_info.contexts_shared_dir
            }
            
            for dir_type, dir_path in directories.items():
                status = "✓ Created" if dir_path.exists() else "✗ Failed"
                table.add_row(dir_type, str(dir_path), status)
            
            console.print(table)
            console.print("[bold green]Directory structure created successfully![/bold green]")
        else:
            console.print("[bold red]Failed to create directory structure. Check logs for details.[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]Error creating directory structure: {e}[/bold red]")
        logger.error(f"Failed to create directory structure: {e}")


@structure.command()
@click.option(
    "--base-path", "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Base path for configuration directories (defaults to current directory)"
)
def validate(base_path: Path):
    """Validate the current directory structure and naming conventions."""
    try:
        directory_manager = DirectoryManager(base_path)
        
        console.print("[bold blue]Validating directory structure...[/bold blue]")
        
        # Validate directory structure
        validation_results = directory_manager.validate_directory_structure()
        
        # Display directory validation results
        dir_table = Table(title="Directory Structure Validation")
        dir_table.add_column("Directory", style="cyan")
        dir_table.add_column("Status", style="yellow")
        
        all_dirs_valid = True
        for dir_name, is_valid in validation_results.items():
            status = "✓ Valid" if is_valid else "✗ Invalid"
            style = "green" if is_valid else "red"
            dir_table.add_row(dir_name.replace("_", " ").title(), f"[{style}]{status}[/{style}]")
            if not is_valid:
                all_dirs_valid = False
        
        console.print(dir_table)
        
        # Organize and validate configuration files
        organized_files = directory_manager.organize_configuration_files()
        
        # Display file organization results
        file_table = Table(title="Configuration Files")
        file_table.add_column("Type", style="cyan")
        file_table.add_column("Count", style="yellow")
        file_table.add_column("Files", style="green")
        
        for config_type in ["profiles", "hooks", "contexts"]:
            files = organized_files[config_type]
            file_names = [f.name for f in files] if files else ["None"]
            file_table.add_row(
                config_type.title(),
                str(len(files)),
                ", ".join(file_names[:5]) + ("..." if len(file_names) > 5 else "")
            )
        
        console.print(file_table)
        
        # Display errors if any
        if organized_files["errors"]:
            error_panel = Panel(
                "\n".join(organized_files["errors"]),
                title="[red]Naming Convention Violations[/red]",
                border_style="red"
            )
            console.print(error_panel)
        
        # Summary
        if all_dirs_valid and not organized_files["errors"]:
            console.print("[bold green]✓ Directory structure and naming conventions are valid![/bold green]")
        else:
            console.print("[bold yellow]⚠ Issues found in directory structure or naming conventions.[/bold yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Error validating directory structure: {e}[/bold red]")
        logger.error(f"Failed to validate directory structure: {e}")


@structure.command()
@click.argument("name")
@click.argument("config_type", type=click.Choice(["profile", "hook", "context"]))
def validate_name(name: str, config_type: str):
    """Validate a configuration name against naming conventions."""
    try:
        directory_manager = DirectoryManager()
        
        # Map string to enum
        type_mapping = {
            "profile": ConfigurationType.PROFILE,
            "hook": ConfigurationType.HOOK,
            "context": ConfigurationType.CONTEXT
        }
        
        config_enum = type_mapping[config_type]
        is_valid, error_message = directory_manager.validate_naming_convention(name, config_enum)
        
        if is_valid:
            console.print(f"[bold green]✓ '{name}' is a valid {config_type} name[/bold green]")
        else:
            console.print(f"[bold red]✗ '{name}' is not a valid {config_type} name[/bold red]")
            console.print(f"[yellow]{error_message}[/yellow]")
            
            # Suggest a valid name
            suggested = directory_manager.suggest_valid_name(name, config_enum)
            console.print(f"[cyan]Suggested name: '{suggested}'[/cyan]")
            
    except Exception as e:
        console.print(f"[bold red]Error validating name: {e}[/bold red]")
        logger.error(f"Failed to validate name: {e}")


@structure.command()
@click.option(
    "--base-path", "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Base path for configuration directories (defaults to current directory)"
)
def info(base_path: Path):
    """Display information about the directory structure."""
    try:
        directory_manager = DirectoryManager(base_path)
        structure_info = directory_manager.get_directory_structure()
        
        # Display directory structure information
        info_table = Table(title="Directory Structure Information")
        info_table.add_column("Directory Type", style="cyan")
        info_table.add_column("Path", style="green")
        info_table.add_column("Exists", style="yellow")
        info_table.add_column("File Count", style="blue")
        
        directories = {
            "Profiles": (structure_info.profiles_dir, ['.yaml', '.yml']),
            "Hooks": (structure_info.hooks_dir, ['.yaml', '.yml']),
            "Contexts": (structure_info.contexts_dir, ['.md']),
            "Shared Contexts": (structure_info.contexts_shared_dir, ['.md'])
        }
        
        for dir_type, (dir_path, extensions) in directories.items():
            exists = "✓" if dir_path.exists() else "✗"
            
            # Count files with appropriate extensions
            file_count = 0
            if dir_path.exists():
                for ext in extensions:
                    file_count += len(list(dir_path.rglob(f"*{ext}")))
            
            info_table.add_row(dir_type, str(dir_path), exists, str(file_count))
        
        console.print(info_table)
        
        # Display naming conventions
        conventions_panel = Panel(
            "\n".join([
                f"[cyan]{config_type.value.title()}:[/cyan] {conv.description}"
                for config_type, conv in DirectoryManager.NAMING_CONVENTIONS.items()
            ]),
            title="Naming Conventions",
            border_style="blue"
        )
        console.print(conventions_panel)
        
    except Exception as e:
        console.print(f"[bold red]Error getting directory structure info: {e}[/bold red]")
        logger.error(f"Failed to get directory structure info: {e}")