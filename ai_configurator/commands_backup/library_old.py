"""Library management commands for browsing and searching configurations."""

import json
from pathlib import Path
from typing import List, Optional, Dict

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..core.library_manager import LibraryManager
from ..core.catalog_schema import ConfigItem
from ..core.library_installer import LibraryInstallationManager
from ..core.models import InstalledProfile
from ..core.profile_validator import ProfileValidator

console = Console()


@click.group()
def library() -> None:
    """Manage configuration library operations."""
    pass


@library.command("browse")
@click.option(
    "--persona", "-p",
    help="Filter by persona (e.g., developer, network-admin, content-creator)"
)
@click.option(
    "--category", "-c",
    type=click.Choice(["contexts", "profiles", "hooks", "mcp_servers"]),
    help="Filter by category"
)
@click.option(
    "--subcategory", "-s",
    help="Filter by subcategory within a category"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format"
)
@click.pass_context
def browse(
    ctx: click.Context,
    persona: Optional[str],
    category: Optional[str],
    subcategory: Optional[str],
    format: str
) -> None:
    """Browse available configurations in the library."""
    library_manager = LibraryManager()
    
    # Load configurations based on filters
    if persona:
        configs = library_manager.get_configurations_by_persona(persona)
        title = f"Configurations for {persona}"
    else:
        configs = library_manager.search_configurations(
            category=category,
            subcategory=subcategory
        )
        title = "Available Configurations"
        if category:
            title += f" - {category}"
            if subcategory:
                title += f" / {subcategory}"
    
    if not configs:
        console.print("[yellow]No configurations found matching the criteria.[/yellow]")
        return
    
    if format == "json":
        # JSON output
        config_data = [
            {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "version": config.version,
                "personas": config.personas,
                "domains": config.domains,
                "tags": config.tags,
                "dependencies": config.dependencies,
                "downloads": config.downloads,
                "rating": config.rating
            }
            for config in configs
        ]
        console.print(json.dumps(config_data, indent=2))
        
    elif format == "detailed":
        # Detailed output with descriptions
        console.print(Panel.fit(f"[bold blue]{title}[/bold blue]", border_style="blue"))
        
        for config in configs:
            # Create a panel for each configuration
            content = []
            content.append(f"[bold cyan]ID:[/bold cyan] {config.id}")
            content.append(f"[bold cyan]Version:[/bold cyan] {config.version}")
            content.append(f"[bold cyan]Description:[/bold cyan] {config.description}")
            content.append(f"[bold cyan]Personas:[/bold cyan] {', '.join(config.personas)}")
            content.append(f"[bold cyan]Domains:[/bold cyan] {', '.join(config.domains)}")
            content.append(f"[bold cyan]Tags:[/bold cyan] {', '.join(config.tags)}")
            
            if config.dependencies:
                content.append(f"[bold cyan]Dependencies:[/bold cyan] {', '.join(config.dependencies)}")
            
            content.append(f"[bold cyan]Downloads:[/bold cyan] {config.downloads}")
            content.append(f"[bold cyan]Rating:[/bold cyan] {config.rating}/5.0")
            
            panel_content = "\n".join(content)
            console.print(Panel(panel_content, title=config.name, border_style="green"))
            console.print()
    
    else:
        # Table output (default)
        table = Table(title=title)
        table.add_column("Name", style="cyan", width=25)
        table.add_column("ID", style="blue", width=30)
        table.add_column("Version", style="green", width=8)
        table.add_column("Personas", style="yellow", width=20)
        table.add_column("Downloads", style="magenta", width=10)
        table.add_column("Rating", style="red", width=8)
        
        for config in configs:
            personas_text = ", ".join(config.personas[:2])  # Show first 2 personas
            if len(config.personas) > 2:
                personas_text += f" +{len(config.personas) - 2}"
            
            table.add_row(
                config.name,
                config.id,
                config.version,
                personas_text,
                str(config.downloads),
                f"{config.rating:.1f}/5"
            )
        
        console.print(table)
        
        # Show summary
        console.print(f"\n[dim]Found {len(configs)} configurations[/dim]")


@library.command("search")
@click.argument("query", required=False)
@click.option(
    "--persona", "-p",
    help="Filter by persona"
)
@click.option(
    "--domain", "-d",
    help="Filter by domain"
)
@click.option(
    "--tag", "-t",
    help="Filter by tag"
)
@click.option(
    "--category", "-c",
    type=click.Choice(["contexts", "profiles", "hooks", "mcp_servers"]),
    help="Filter by category"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format"
)
@click.pass_context
def search(
    ctx: click.Context,
    query: Optional[str],
    persona: Optional[str],
    domain: Optional[str],
    tag: Optional[str],
    category: Optional[str],
    format: str
) -> None:
    """Search configurations with keyword and tag filtering."""
    library_manager = LibraryManager()
    
    # Build filter lists
    personas = [persona] if persona else None
    domains = [domain] if domain else None
    tags = [tag] if tag else None
    
    # Search configurations
    configs = library_manager.search_configurations(
        query=query,
        personas=personas,
        domains=domains,
        tags=tags,
        category=category
    )
    
    if not configs:
        search_terms = []
        if query:
            search_terms.append(f"query: '{query}'")
        if persona:
            search_terms.append(f"persona: {persona}")
        if domain:
            search_terms.append(f"domain: {domain}")
        if tag:
            search_terms.append(f"tag: {tag}")
        if category:
            search_terms.append(f"category: {category}")
        
        search_desc = ", ".join(search_terms) if search_terms else "no filters"
        console.print(f"[yellow]No configurations found for {search_desc}.[/yellow]")
        return
    
    # Display results using the same logic as browse command
    title = f"Search Results"
    if query:
        title += f" for '{query}'"
    
    if format == "json":
        config_data = [
            {
                "id": config.id,
                "name": config.name,
                "description": config.description,
                "version": config.version,
                "personas": config.personas,
                "domains": config.domains,
                "tags": config.tags,
                "dependencies": config.dependencies,
                "downloads": config.downloads,
                "rating": config.rating
            }
            for config in configs
        ]
        console.print(json.dumps(config_data, indent=2))
        
    elif format == "detailed":
        console.print(Panel.fit(f"[bold blue]{title}[/bold blue]", border_style="blue"))
        
        for config in configs:
            content = []
            content.append(f"[bold cyan]ID:[/bold cyan] {config.id}")
            content.append(f"[bold cyan]Version:[/bold cyan] {config.version}")
            content.append(f"[bold cyan]Description:[/bold cyan] {config.description}")
            content.append(f"[bold cyan]Personas:[/bold cyan] {', '.join(config.personas)}")
            content.append(f"[bold cyan]Domains:[/bold cyan] {', '.join(config.domains)}")
            content.append(f"[bold cyan]Tags:[/bold cyan] {', '.join(config.tags)}")
            
            if config.dependencies:
                content.append(f"[bold cyan]Dependencies:[/bold cyan] {', '.join(config.dependencies)}")
            
            content.append(f"[bold cyan]Downloads:[/bold cyan] {config.downloads}")
            content.append(f"[bold cyan]Rating:[/bold cyan] {config.rating}/5.0")
            
            panel_content = "\n".join(content)
            console.print(Panel(panel_content, title=config.name, border_style="green"))
            console.print()
    
    else:
        table = Table(title=title)
        table.add_column("Name", style="cyan", width=25)
        table.add_column("ID", style="blue", width=30)
        table.add_column("Version", style="green", width=8)
        table.add_column("Personas", style="yellow", width=20)
        table.add_column("Downloads", style="magenta", width=10)
        table.add_column("Rating", style="red", width=8)
        
        for config in configs:
            personas_text = ", ".join(config.personas[:2])
            if len(config.personas) > 2:
                personas_text += f" +{len(config.personas) - 2}"
            
            table.add_row(
                config.name,
                config.id,
                config.version,
                personas_text,
                str(config.downloads),
                f"{config.rating:.1f}/5"
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(configs)} configurations[/dim]")


@library.command("info")
@click.argument("config_id")
@click.option(
    "--format", "-f",
    type=click.Choice(["detailed", "json"]),
    default="detailed",
    help="Output format"
)
@click.pass_context
def info(ctx: click.Context, config_id: str, format: str) -> None:
    """Show detailed information about a specific configuration."""
    library_manager = LibraryManager()
    
    # Get configuration metadata
    metadata = library_manager.get_configuration_metadata(config_id)
    if not metadata:
        console.print(f"[red]Configuration not found: {config_id}[/red]")
        return
    
    if format == "json":
        # JSON output
        metadata_dict = {
            "id": metadata.id,
            "name": metadata.name,
            "description": metadata.description,
            "version": metadata.version,
            "author": metadata.author,
            "personas": metadata.personas,
            "domains": metadata.domains,
            "dependencies": metadata.dependencies,
            "tags": metadata.tags,
            "compatibility": {
                "kiro_version": metadata.compatibility.kiro_version,
                "platforms": metadata.compatibility.platforms
            },
            "created_date": metadata.created_date,
            "updated_date": metadata.updated_date,
            "usage_stats": {
                "downloads": metadata.usage_stats.downloads,
                "rating": metadata.usage_stats.rating
            }
        }
        console.print(json.dumps(metadata_dict, indent=2))
    
    else:
        # Detailed output
        console.print(Panel.fit(f"[bold blue]Configuration Details[/bold blue]", border_style="blue"))
        
        # Basic information
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="bold cyan", width=20)
        info_table.add_column("Value", style="white")
        
        info_table.add_row("ID", metadata.id)
        info_table.add_row("Name", metadata.name)
        info_table.add_row("Version", metadata.version)
        info_table.add_row("Author", metadata.author)
        info_table.add_row("Created", metadata.created_date)
        info_table.add_row("Updated", metadata.updated_date)
        
        console.print(info_table)
        console.print()
        
        # Description
        console.print(Panel(metadata.description, title="Description", border_style="green"))
        
        # Personas and domains
        personas_text = Text()
        for i, persona in enumerate(metadata.personas):
            if i > 0:
                personas_text.append(", ")
            personas_text.append(persona, style="yellow")
        
        domains_text = Text()
        for i, domain in enumerate(metadata.domains):
            if i > 0:
                domains_text.append(", ")
            domains_text.append(domain, style="blue")
        
        console.print(Panel(personas_text, title="Target Personas", border_style="yellow"))
        console.print(Panel(domains_text, title="Domains", border_style="blue"))
        
        # Tags
        if metadata.tags:
            tags_text = Text()
            for i, tag in enumerate(metadata.tags):
                if i > 0:
                    tags_text.append(", ")
                tags_text.append(f"#{tag}", style="magenta")
            console.print(Panel(tags_text, title="Tags", border_style="magenta"))
        
        # Dependencies
        if metadata.dependencies:
            deps_text = Text()
            for i, dep in enumerate(metadata.dependencies):
                if i > 0:
                    deps_text.append(", ")
                deps_text.append(dep, style="red")
            console.print(Panel(deps_text, title="Dependencies", border_style="red"))
        
        # Compatibility and usage stats
        compat_table = Table(title="Compatibility & Usage")
        compat_table.add_column("Field", style="cyan")
        compat_table.add_column("Value", style="white")
        
        compat_table.add_row("Kiro Version", metadata.compatibility.kiro_version)
        compat_table.add_row("Platforms", ", ".join(metadata.compatibility.platforms))
        compat_table.add_row("Downloads", str(metadata.usage_stats.downloads))
        compat_table.add_row("Rating", f"{metadata.usage_stats.rating}/5.0")
        
        console.print(compat_table)


@library.command("personas")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
@click.pass_context
def personas(ctx: click.Context, format: str) -> None:
    """List all available personas."""
    library_manager = LibraryManager()
    
    personas_dict = library_manager.list_personas()
    
    if not personas_dict:
        console.print("[yellow]No personas found in the library.[/yellow]")
        return
    
    if format == "json":
        personas_data = {
            persona_id: {
                "name": info.name,
                "description": info.description,
                "recommended_configs": info.recommended_configs
            }
            for persona_id, info in personas_dict.items()
        }
        console.print(json.dumps(personas_data, indent=2))
    
    else:
        table = Table(title="Available Personas")
        table.add_column("ID", style="cyan", width=20)
        table.add_column("Name", style="blue", width=25)
        table.add_column("Description", style="white", width=40)
        table.add_column("Configs", style="green", width=10)
        
        for persona_id, info in personas_dict.items():
            table.add_row(
                persona_id,
                info.name,
                info.description,
                str(len(info.recommended_configs))
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(personas_dict)} personas[/dim]")


@library.command("categories")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
@click.pass_context
def categories(ctx: click.Context, format: str) -> None:
    """List all available categories and subcategories."""
    library_manager = LibraryManager()
    
    categories_dict = library_manager.list_categories()
    
    if not categories_dict:
        console.print("[yellow]No categories found in the library.[/yellow]")
        return
    
    if format == "json":
        console.print(json.dumps(categories_dict, indent=2))
    
    else:
        table = Table(title="Available Categories")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Subcategories", style="blue", width=50)
        table.add_column("Count", style="green", width=10)
        
        for category, subcategories in categories_dict.items():
            subcategories_text = ", ".join(subcategories) if subcategories else "None"
            table.add_row(
                category,
                subcategories_text,
                str(len(subcategories))
            )
        
        console.print(table)


@library.command("refresh")
@click.pass_context
def refresh(ctx: click.Context) -> None:
    """Refresh the library catalog from disk."""
    library_manager = LibraryManager()
    
    console.print("[blue]Refreshing library catalog...[/blue]")
    
    success = library_manager.refresh_catalog()
    
    if success:
        stats = library_manager.get_library_stats()
        console.print("[green]✅ Library catalog refreshed successfully![/green]")
        console.print(f"Total configurations: {stats.get('total_configs', 0)}")
        console.print(f"Last updated: {stats.get('last_updated', 'Unknown')}")
    else:
        console.print("[red]❌ Failed to refresh library catalog.[/red]")


@library.command("stats")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
@click.pass_context
def stats(ctx: click.Context, format: str) -> None:
    """Show library statistics."""
    library_manager = LibraryManager()
    
    stats_data = library_manager.get_library_stats()
    
    if not stats_data:
        console.print("[yellow]No statistics available.[/yellow]")
        return
    
    if format == "json":
        console.print(json.dumps(stats_data, indent=2))
    
    else:
        console.print(Panel.fit("[bold blue]Library Statistics[/bold blue]", border_style="blue"))
        
        # General stats
        general_table = Table(title="General Statistics")
        general_table.add_column("Metric", style="cyan")
        general_table.add_column("Value", style="white")
        
        general_table.add_row("Total Configurations", str(stats_data.get("total_configs", 0)))
        general_table.add_row("Total Personas", str(stats_data.get("personas_count", 0)))
        general_table.add_row("Last Updated", stats_data.get("last_updated", "Unknown"))
        
        console.print(general_table)
        
        # Category breakdown
        if "categories" in stats_data:
            category_table = Table(title="Configurations by Category")
            category_table.add_column("Category", style="cyan")
            category_table.add_column("Count", style="green")
            
            for category, count in stats_data["categories"].items():
                category_table.add_row(category, str(count))
            
            console.print(category_table)


@library.command("install")
@click.argument("profile_names", nargs=-1, required=True)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without actually installing"
)
@click.option(
    "--force",
    is_flag=True,
    help="Force installation even if profiles already exist"
)
@click.option(
    "--target", "-t",
    type=click.Choice(["auto", "kiro", "amazonq", "both"]),
    default="auto",
    help="Installation target (auto-detects by default)"
)
@click.option(
    "--concurrent",
    is_flag=True,
    help="Install profiles concurrently for better performance"
)
@click.option(
    "--progress",
    is_flag=True,
    help="Show detailed progress indicators"
)
@click.pass_context
def install(
    ctx: click.Context,
    profile_names: tuple,
    dry_run: bool,
    force: bool,
    target: str,
    concurrent: bool,
    progress: bool
) -> None:
    """Install profiles from the library by name with performance optimizations."""
    if not profile_names:
        console.print("[red]No profile names provided.[/red]")
        return
    
    # Initialize the new installation manager
    installer = LibraryInstallationManager()
    
    # Check target availability
    if target != "both":
        target_paths = installer.detect_target_paths(target)
        if not target_paths:
            console.print(f"[red]Target '{target}' not available or not detected.[/red]")
            if target == "auto":
                console.print("Neither Kiro nor Amazon Q CLI installation detected.")
                console.print("Make sure you're in a directory with .kiro/ or have Amazon Q CLI installed.")
            return
    
    if dry_run:
        console.print("[blue]Dry run - showing what would be installed:[/blue]")
        
        # Load catalog to check if profiles exist
        from ..core.library_manager import LibraryManager
        library_manager = LibraryManager(library_path=installer.library_path)
        catalog = library_manager.load_catalog()
        
        if not catalog:
            console.print("  ❌ Failed to load library catalog")
            return
        
        for profile_name in profile_names:
            # Find the profile in the catalog
            profile_config = None
            for category_name, category_profiles in catalog.categories.profiles.items():
                for config in category_profiles:
                    if config.id == profile_name:
                        profile_config = config
                        break
                if profile_config:
                    break
            
            if profile_config:
                # Check if the directory exists
                profile_dir = installer.library_path / profile_config.file_path.split('/')[0]
                if profile_dir.exists():
                    console.print(f"  ✅ Would install profile: {profile_name}")
                    if target == "both":
                        console.print(f"    → Target: Kiro and Amazon Q CLI")
                    else:
                        detected_target = installer.detect_target_paths(target)
                        if detected_target:
                            console.print(f"    → Target: {detected_target['target_type']}")
                else:
                    console.print(f"  ❌ Profile directory not found: {profile_dir}")
            else:
                console.print(f"  ❌ Profile not found: {profile_name}")
        
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return
    
    # Confirm installation
    if not force:
        console.print(f"[blue]Installing {len(profile_names)} profile(s) to target '{target}':[/blue]")
        for profile_name in profile_names:
            console.print(f"  • {profile_name}")
        
        if concurrent and len(profile_names) > 1:
            console.print(f"\n[dim]Using concurrent installation with up to {installer.max_workers} workers[/dim]")
        
        if not click.confirm("\nProceed with installation?"):
            console.print("[yellow]Installation cancelled.[/yellow]")
            return
    
    # Perform installation
    console.print("\n[blue]Installing profiles...[/blue]")
    
    # Use concurrent installation if requested and multiple profiles
    if concurrent and len(profile_names) > 1:
        def progress_callback(message: str, current: int, total: int):
            if progress:
                console.print(f"  [{current}/{total}] {message}")
        
        results = installer.install_multiple_profiles(
            list(profile_names), 
            target, 
            force,
            progress_callback if progress else None
        )
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(profile_names)
        
        # Show detailed results
        console.print("\n[blue]Installation Results:[/blue]")
        for profile_name, success in results.items():
            status = "✅" if success else "❌"
            console.print(f"  {status} {profile_name}")
    
    else:
        # Sequential installation with progress indicators
        success_count = 0
        total_count = len(profile_names)
        
        for i, profile_name in enumerate(profile_names, 1):
            console.print(f"\n[{i}/{total_count}] Installing {profile_name}...")
            
            def progress_callback(message: str):
                if progress:
                    console.print(f"  → {message}")
            
            if installer.install_profile(profile_name, target, force, progress_callback if progress else None):
                console.print(f"  ✅ Successfully installed {profile_name}")
                success_count += 1
            else:
                console.print(f"  ❌ Failed to install {profile_name}")
    
    # Show final results with performance stats
    if success_count == total_count:
        console.print(f"\n[bold green]✅ All {total_count} profiles installed successfully![/bold green]")
    elif success_count > 0:
        console.print(f"\n[bold yellow]⚠️ {success_count}/{total_count} profiles installed successfully.[/bold yellow]")
    else:
        console.print(f"\n[bold red]❌ All profile installations failed![/bold red]")
    
    # Show performance statistics if requested
    if progress:
        stats = installer.get_performance_stats()
        if stats.get('avg_installation_time'):
            console.print(f"\n[dim]Average installation time: {stats['avg_installation_time']:.2f}s[/dim]")
        if stats.get('cache_hit_ratio'):
            console.print(f"[dim]Cache hit ratio: {stats['cache_hit_ratio']:.1%}[/dim]")


@library.command("list")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format"
)
def list_installed(format: str) -> None:
    """List installed profiles."""
    try:
        installer = LibraryInstallationManager()
        manifest = installer.load_installation_manifest()
        
        if not manifest:
            console.print("[yellow]No profiles are currently installed.[/yellow]")
            return
        
        # Display results
        if format == "json":
            import json
            data = {name: profile.to_dict() for name, profile in manifest.items()}
            console.print(json.dumps(data, indent=2, ensure_ascii=False))
        elif format == "detailed":
            _display_detailed_installed_profiles(manifest)
        else:
            _display_installed_profiles_table(manifest)
        
        # Show summary
        console.print(f"\n[dim]Total: {len(manifest)} profiles installed[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error listing installed profiles: {e}[/red]")


@library.command("remove")
@click.argument("profile_names", nargs=-1, required=True)
@click.option(
    "--force",
    is_flag=True,
    help="Force removal without confirmation"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be removed without actually removing"
)
def remove(profile_names: tuple, force: bool, dry_run: bool) -> None:
    """Remove installed profiles."""
    try:
        installer = LibraryInstallationManager()
        manifest = installer.load_installation_manifest()
        
        # Validate that all profiles are installed
        to_remove = []
        for profile_name in profile_names:
            if profile_name not in manifest:
                console.print(f"[yellow]Profile not installed: {profile_name}[/yellow]")
                continue
            to_remove.append(manifest[profile_name])
        
        if not to_remove:
            console.print("[yellow]No profiles to remove.[/yellow]")
            return
        
        # Display removal plan
        table = Table(title="Removal Plan")
        table.add_column("Profile", style="cyan")
        table.add_column("Version", style="yellow")
        table.add_column("Target", style="magenta")
        table.add_column("Files", style="green")
        
        for profile in to_remove:
            table.add_row(
                profile.name,
                profile.version,
                profile.target,
                str(len(profile.files))
            )
        
        console.print(table)
        
        if dry_run:
            console.print(f"\n[yellow]Dry run - would remove {len(to_remove)} profiles.[/yellow]")
            return
        
        # Confirm removal
        if not force and not click.confirm(f"\nRemove {len(to_remove)} profiles?"):
            console.print("[yellow]Removal cancelled.[/yellow]")
            return
        
        # Perform removal
        console.print("\n[blue]Removing profiles...[/blue]")
        success_count = 0
        
        for profile in to_remove:
            console.print(f"  Removing {profile.name}...")
            
            try:
                # Remove files
                for file_path in profile.files:
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        file_path_obj.unlink()
                        console.print(f"    Removed: {file_path}")
                
                # Remove from manifest
                del manifest[profile.name]
                success_count += 1
                console.print(f"    ✅ Removed {profile.name}")
                
            except Exception as e:
                console.print(f"    ❌ Failed to remove {profile.name}: {e}")
        
        # Save updated manifest
        if success_count > 0:
            installer.save_installation_manifest(manifest)
        
        console.print(f"\n[bold green]✅ Successfully removed {success_count}/{len(to_remove)} profiles.[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error removing profiles: {e}[/red]")


def _display_installed_profiles_table(manifest: Dict[str, InstalledProfile]) -> None:
    """Display installed profiles in table format."""
    table = Table(title="Installed Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="yellow")
    table.add_column("Target", style="magenta")
    table.add_column("Installed", style="dim")
    table.add_column("Files", style="green")
    
    for profile_name, profile in manifest.items():
        # Format installation date
        try:
            date_str = profile.installed_date.strftime("%Y-%m-%d")
        except:
            date_str = str(profile.installed_date)[:10]
        
        table.add_row(
            profile.name,
            profile.version,
            profile.target,
            date_str,
            str(len(profile.files))
        )
    
    console.print(table)


def _display_detailed_installed_profiles(manifest: Dict[str, InstalledProfile]) -> None:
    """Display installed profiles in detailed format."""
    for i, (profile_name, profile) in enumerate(manifest.items()):
        if i > 0:
            console.print()
        
        # Create panel content
        content = []
        content.append(f"[bold]Name:[/bold] {profile.name}")
        content.append(f"[bold]Version:[/bold] {profile.version}")
        content.append(f"[bold]Target:[/bold] {profile.target}")
        
        # Installation details
        try:
            date_str = profile.installed_date.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date_str = str(profile.installed_date)
        
        content.append(f"[bold]Installed:[/bold] {date_str}")
        content.append(f"[bold]Files:[/bold] {len(profile.files)}")
        
        # Show file list
        if profile.files:
            content.append(f"[bold]File List:[/bold]")
            for file_path in profile.files[:5]:  # Show first 5 files
                content.append(f"  • {file_path}")
            if len(profile.files) > 5:
                content.append(f"  ... and {len(profile.files) - 5} more files")
        
        panel_content = "\n".join(content)
        console.print(Panel(panel_content, title=f"Profile: {profile.name}"))


@library.command("performance")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format"
)
@click.option(
    "--clear",
    is_flag=True,
    help="Clear performance statistics after displaying"
)
def performance(format: str, clear: bool) -> None:
    """Show performance statistics for library operations."""
    try:
        # Get stats from both managers
        library_manager = LibraryManager()
        installer = LibraryInstallationManager()
        
        lib_stats = library_manager.get_performance_stats()
        install_stats = installer.get_performance_stats()
        
        if format == "json":
            import json
            combined_stats = {
                "library_manager": lib_stats,
                "installation_manager": install_stats
            }
            console.print(json.dumps(combined_stats, indent=2))
        else:
            console.print(Panel.fit("[bold blue]Performance Statistics[/bold blue]", border_style="blue"))
            
            # Library Manager Stats
            if lib_stats:
                lib_table = Table(title="Library Manager Performance")
                lib_table.add_column("Metric", style="cyan")
                lib_table.add_column("Value", style="white")
                
                lib_table.add_row("Cache Hits", str(lib_stats.get('cache_hits', 0)))
                lib_table.add_row("Cache Misses", str(lib_stats.get('cache_misses', 0)))
                
                if lib_stats.get('cache_hit_ratio'):
                    lib_table.add_row("Cache Hit Ratio", f"{lib_stats['cache_hit_ratio']:.1%}")
                
                if lib_stats.get('avg_load_time'):
                    lib_table.add_row("Avg Load Time", f"{lib_stats['avg_load_time']:.3f}s")
                
                if lib_stats.get('avg_search_time'):
                    lib_table.add_row("Avg Search Time", f"{lib_stats['avg_search_time']:.3f}s")
                
                console.print(lib_table)
            
            # Installation Manager Stats
            if install_stats:
                install_table = Table(title="Installation Manager Performance")
                install_table.add_column("Metric", style="cyan")
                install_table.add_column("Value", style="white")
                
                install_table.add_row("Total Installations", str(install_stats.get('installations', 0)))
                install_table.add_row("Concurrent Operations", str(install_stats.get('concurrent_installations', 0)))
                install_table.add_row("Cache Hits", str(install_stats.get('cache_hits', 0)))
                install_table.add_row("Cache Misses", str(install_stats.get('cache_misses', 0)))
                
                if install_stats.get('cache_hit_ratio'):
                    install_table.add_row("Cache Hit Ratio", f"{install_stats['cache_hit_ratio']:.1%}")
                
                if install_stats.get('avg_installation_time'):
                    install_table.add_row("Avg Installation Time", f"{install_stats['avg_installation_time']:.3f}s")
                
                if install_stats.get('total_installation_time'):
                    install_table.add_row("Total Installation Time", f"{install_stats['total_installation_time']:.3f}s")
                
                console.print(install_table)
        
        # Clear stats if requested
        if clear:
            library_manager.clear_cache()
            installer.clear_performance_stats()
            console.print("\n[green]Performance statistics cleared.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error retrieving performance statistics: {e}[/red]")


@library.command("validate")
@click.argument("profile_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--contribution",
    is_flag=True,
    help="Validate for contribution to the library (stricter requirements)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["detailed", "json", "summary"]),
    default="detailed",
    help="Output format"
)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to automatically fix common issues"
)
def validate(profile_path: Path, contribution: bool, format: str, fix: bool) -> None:
    """Validate a profile directory structure and content."""
    try:
        if contribution:
            report = ProfileValidator.validate_for_contribution(profile_path)
        else:
            report = ProfileValidator.validate_profile_comprehensive(profile_path)
        
        if format == "json":
            # JSON output
            report_dict = {
                "is_valid": report.is_valid,
                "errors": [
                    {
                        "file_path": error.file_path,
                        "error_type": error.error_type,
                        "message": error.message,
                        "severity": error.severity,
                        "line_number": error.line_number,
                        "column_number": error.column_number
                    }
                    for error in report.errors
                ],
                "warnings": [
                    {
                        "file_path": warning.file_path,
                        "error_type": warning.error_type,
                        "message": warning.message,
                        "severity": warning.severity,
                        "line_number": warning.line_number,
                        "column_number": warning.column_number
                    }
                    for warning in report.warnings
                ],
                "info": [
                    {
                        "file_path": info.file_path,
                        "error_type": info.error_type,
                        "message": info.message,
                        "severity": info.severity
                    }
                    for info in report.info
                ],
                "files_checked": report.files_checked,
                "summary": report.summary
            }
            console.print(json.dumps(report_dict, indent=2))
            
        elif format == "summary":
            # Summary output
            _display_validation_summary(report, profile_path, contribution)
            
        else:
            # Detailed output (default)
            _display_validation_detailed(report, profile_path, contribution)
        
        # Auto-fix if requested
        if fix and not report.is_valid:
            console.print("\n[blue]Attempting to fix common issues...[/blue]")
            fixed_count = _attempt_auto_fix(profile_path, report)
            if fixed_count > 0:
                console.print(f"[green]Fixed {fixed_count} issues. Re-run validation to check results.[/green]")
            else:
                console.print("[yellow]No issues could be automatically fixed.[/yellow]")
        
        # Exit with appropriate code
        if not report.is_valid:
            ctx = click.get_current_context()
            ctx.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        ctx = click.get_current_context()
        ctx.exit(1)


@library.command("checksum")
@click.argument("profile_path", type=click.Path(exists=True, path_type=Path))
def checksum(profile_path: Path) -> None:
    """Generate a checksum for a profile directory."""
    try:
        checksum_value = ProfileValidator.generate_profile_checksum(profile_path)
        
        if checksum_value:
            console.print(f"[green]Profile checksum:[/green] {checksum_value}")
            console.print(f"[dim]Profile path:[/dim] {profile_path}")
        else:
            console.print(f"[red]Failed to generate checksum for: {profile_path}[/red]")
            ctx = click.get_current_context()
            ctx.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error generating checksum: {e}[/red]")
        ctx = click.get_current_context()
        ctx.exit(1)


@library.command("validate-all")
@click.option(
    "--library-path", "-p",
    type=click.Path(exists=True, path_type=Path),
    help="Path to library directory (defaults to ./library)"
)
@click.option(
    "--contribution",
    is_flag=True,
    help="Validate for contribution (stricter requirements)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "json", "detailed"]),
    default="table",
    help="Output format"
)
@click.option(
    "--fail-fast",
    is_flag=True,
    help="Stop on first validation failure"
)
def validate_all(library_path: Optional[Path], contribution: bool, format: str, fail_fast: bool) -> None:
    """Validate all profiles in the library directory."""
    if not library_path:
        library_path = Path("library")
    
    if not library_path.exists():
        console.print(f"[red]Library directory not found: {library_path}[/red]")
        return
    
    # Find all profile directories
    profile_dirs = [d for d in library_path.iterdir() if d.is_dir() and (d / "profile.yaml").exists()]
    
    if not profile_dirs:
        console.print(f"[yellow]No profiles found in: {library_path}[/yellow]")
        return
    
    console.print(f"[blue]Validating {len(profile_dirs)} profiles...[/blue]")
    
    results = []
    valid_count = 0
    
    for profile_dir in profile_dirs:
        try:
            if contribution:
                report = ProfileValidator.validate_for_contribution(profile_dir)
            else:
                report = ProfileValidator.validate_profile_comprehensive(profile_dir)
            
            results.append((profile_dir.name, report))
            
            if report.is_valid:
                valid_count += 1
                console.print(f"  ✅ {profile_dir.name}")
            else:
                console.print(f"  ❌ {profile_dir.name} ({len(report.errors)} errors)")
                if fail_fast:
                    console.print(f"[red]Stopping validation due to --fail-fast[/red]")
                    break
            
        except Exception as e:
            console.print(f"  💥 {profile_dir.name} (validation error: {e})")
            if fail_fast:
                break
    
    # Display results
    console.print(f"\n[bold]Validation Results:[/bold]")
    console.print(f"Valid profiles: {valid_count}/{len(results)}")
    
    if format == "json":
        results_data = {}
        for profile_name, report in results:
            results_data[profile_name] = {
                "is_valid": report.is_valid,
                "error_count": len(report.errors),
                "warning_count": len(report.warnings),
                "completeness_score": report.summary.get("profile_completeness", 0)
            }
        console.print(json.dumps(results_data, indent=2))
        
    elif format == "detailed":
        for profile_name, report in results:
            console.print(f"\n[bold cyan]{profile_name}:[/bold cyan]")
            if report.errors:
                console.print(f"  [red]Errors ({len(report.errors)}):[/red]")
                for error in report.errors[:3]:  # Show first 3 errors
                    console.print(f"    • {error.message}")
                if len(report.errors) > 3:
                    console.print(f"    ... and {len(report.errors) - 3} more errors")
            
            if report.warnings:
                console.print(f"  [yellow]Warnings ({len(report.warnings)}):[/yellow]")
                for warning in report.warnings[:2]:  # Show first 2 warnings
                    console.print(f"    • {warning.message}")
                if len(report.warnings) > 2:
                    console.print(f"    ... and {len(report.warnings) - 2} more warnings")
    
    else:
        # Table format
        table = Table(title="Profile Validation Results")
        table.add_column("Profile", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Errors", style="red")
        table.add_column("Warnings", style="yellow")
        table.add_column("Completeness", style="green")
        
        for profile_name, report in results:
            status = "✅ Valid" if report.is_valid else "❌ Invalid"
            completeness = f"{report.summary.get('profile_completeness', 0):.0f}%"
            
            table.add_row(
                profile_name,
                status,
                str(len(report.errors)),
                str(len(report.warnings)),
                completeness
            )
        
        console.print(table)
    
    # Exit with error code if any profiles are invalid
    if valid_count < len(results):
        ctx = click.get_current_context()
        ctx.exit(1)


def _display_validation_summary(report, profile_path: Path, contribution: bool) -> None:
    """Display validation results in summary format."""
    validation_type = "Contribution" if contribution else "Standard"
    
    if report.is_valid:
        console.print(f"[bold green]✅ {validation_type} validation passed![/bold green]")
    else:
        console.print(f"[bold red]❌ {validation_type} validation failed![/bold red]")
    
    console.print(f"[dim]Profile:[/dim] {profile_path}")
    console.print(f"[dim]Files checked:[/dim] {len(report.files_checked)}")
    
    # Summary stats
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Count", style="white")
    
    summary_table.add_row("Errors", f"[red]{len(report.errors)}[/red]")
    summary_table.add_row("Warnings", f"[yellow]{len(report.warnings)}[/yellow]")
    summary_table.add_row("Info", f"[blue]{len(report.info)}[/blue]")
    
    if "profile_completeness" in report.summary:
        completeness = report.summary["profile_completeness"]
        summary_table.add_row("Completeness", f"[green]{completeness:.0f}%[/green]")
    
    console.print(summary_table)
    
    # Show first few errors if any
    if report.errors:
        console.print(f"\n[red]Top errors:[/red]")
        for error in report.errors[:3]:
            console.print(f"  • {error.message}")
        if len(report.errors) > 3:
            console.print(f"  ... and {len(report.errors) - 3} more")


def _display_validation_detailed(report, profile_path: Path, contribution: bool) -> None:
    """Display validation results in detailed format."""
    validation_type = "Contribution" if contribution else "Standard"
    
    # Header
    if report.is_valid:
        console.print(Panel.fit(f"[bold green]✅ {validation_type} Validation Passed[/bold green]", border_style="green"))
    else:
        console.print(Panel.fit(f"[bold red]❌ {validation_type} Validation Failed[/bold red]", border_style="red"))
    
    # Basic info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Field", style="bold cyan", width=20)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Profile Path", str(profile_path))
    info_table.add_row("Files Checked", str(len(report.files_checked)))
    info_table.add_row("Validation Time", report.summary.get("validation_timestamp", "Unknown"))
    
    if "profile_completeness" in report.summary:
        completeness = report.summary["profile_completeness"]
        info_table.add_row("Completeness Score", f"{completeness:.1f}%")
    
    console.print(info_table)
    
    # Errors
    if report.errors:
        console.print(f"\n[bold red]Errors ({len(report.errors)}):[/bold red]")
        for error in report.errors:
            location = error.file_path
            if error.line_number:
                location += f":{error.line_number}"
            console.print(f"  [red]•[/red] {location}: {error.message}")
    
    # Warnings
    if report.warnings:
        console.print(f"\n[bold yellow]Warnings ({len(report.warnings)}):[/bold yellow]")
        for warning in report.warnings:
            console.print(f"  [yellow]•[/yellow] {warning.file_path}: {warning.message}")
    
    # Info/suggestions
    if report.info:
        console.print(f"\n[bold blue]Suggestions ({len(report.info)}):[/bold blue]")
        for info in report.info:
            console.print(f"  [blue]•[/blue] {info.file_path}: {info.message}")
    
    # Files checked
    if report.files_checked:
        console.print(f"\n[dim]Files checked:[/dim]")
        for file_path in report.files_checked[:10]:  # Show first 10
            console.print(f"  [dim]•[/dim] {file_path}")
        if len(report.files_checked) > 10:
            console.print(f"  [dim]... and {len(report.files_checked) - 10} more files[/dim]")


def _attempt_auto_fix(profile_path: Path, report) -> int:
    """Attempt to automatically fix common validation issues."""
    fixed_count = 0
    
    # This is a placeholder for auto-fix functionality
    # In a real implementation, you would:
    # 1. Analyze the errors in the report
    # 2. Apply fixes for common, safe-to-fix issues
    # 3. Return the number of issues fixed
    
    # Example fixes could include:
    # - Adding missing README files
    # - Fixing common YAML syntax errors
    # - Standardizing file naming
    # - Adding missing required fields with default values
    
    console.print("[yellow]Auto-fix functionality not yet implemented.[/yellow]")
    return fixed_count