"""Context management CLI commands."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ..core import ContextManager

console = Console()


@click.group()
def context():
    """Manage context files and content."""
    pass


@context.command("list")
@click.option(
    "--profile", "-p",
    help="Show contexts for specific profile"
)
@click.pass_context
def context_list(ctx: click.Context, profile: str = None):
    """List available context files."""
    context_manager = ContextManager(ctx.obj["platform"], ctx.obj["config_manager"])
    
    contexts = context_manager.list_available_contexts()
    
    # Create table
    table = Table(title="Available Context Files")
    table.add_column("Category", style="cyan")
    table.add_column("Context", style="green")
    table.add_column("Status", style="yellow")
    
    # Global contexts
    for path in contexts["global"]:
        table.add_row("Global", path, "✅ Active")
    
    # Profile contexts
    if profile:
        if profile in contexts["profiles"]:
            for path in contexts["profiles"][profile]:
                table.add_row(f"Profile ({profile})", path, "✅ Active")
        else:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            return
    else:
        for prof, paths in contexts["profiles"].items():
            for path in paths:
                table.add_row(f"Profile ({prof})", path, "✅ Active")
    
    # Shared contexts
    for path in contexts["shared"]:
        table.add_row("Shared", path, "📁 Available")
    
    # Orphaned contexts
    for path in contexts["orphaned"]:
        table.add_row("Orphaned", path, "⚠️ Unused")
    
    console.print(table)


@context.command("show")
@click.option(
    "--profile", "-p",
    help="Show context for specific profile"
)
@click.option(
    "--global-only", "-g",
    is_flag=True,
    help="Show only global context"
)
@click.option(
    "--raw",
    is_flag=True,
    help="Show raw content without formatting"
)
@click.pass_context
def context_show(ctx: click.Context, profile: str = None, global_only: bool = False, raw: bool = False):
    """Show context content."""
    context_manager = ContextManager(ctx.obj["platform"], ctx.obj["config_manager"])
    
    if global_only:
        content = context_manager.get_global_context_content()
        title = "Global Context Content"
    elif profile:
        content = context_manager.get_profile_context_content(profile)
        title = f"Profile Context Content: {profile}"
    else:
        # Get active profile
        active_profile = ctx.obj["config_manager"].get_active_profile()
        content = context_manager.get_combined_context_content(active_profile)
        title = f"Combined Context Content (Profile: {active_profile or 'None'})"
    
    if not content:
        console.print("[yellow]No context content found[/yellow]")
        return
    
    if raw:
        console.print(content)
    else:
        # Display with syntax highlighting
        syntax = Syntax(content, "markdown", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=title, border_style="blue"))


@context.command("validate")
@click.option(
    "--profile", "-p",
    help="Validate contexts for specific profile"
)
@click.pass_context
def context_validate(ctx: click.Context, profile: str = None):
    """Validate context paths and files."""
    context_manager = ContextManager(ctx.obj["platform"], ctx.obj["config_manager"])
    
    if profile:
        profile_context = ctx.obj["config_manager"].load_profile_context(profile)
        if not profile_context:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            return
        
        paths = profile_context.paths
        title = f"Context Validation: {profile}"
    else:
        global_context = ctx.obj["config_manager"].load_global_context()
        if not global_context:
            console.print("[red]Global context not found[/red]")
            return
        
        paths = global_context.paths
        title = "Global Context Validation"
    
    validation = context_manager.validate_context_paths(paths)
    
    # Create validation table
    table = Table(title=title)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Paths", str(len(paths)))
    table.add_row("Valid Paths", str(len(validation["valid_paths"])))
    table.add_row("Invalid Paths", str(len(validation["invalid_paths"])))
    table.add_row("Glob Patterns", str(len(validation["glob_patterns"])))
    table.add_row("Resolved Files", str(validation["total_files"]))
    table.add_row("Total Size", f"{validation['total_size']:,} bytes")
    
    console.print(table)
    
    # Show invalid paths if any
    if validation["invalid_paths"]:
        console.print("\n[bold red]Invalid Paths:[/bold red]")
        for path in validation["invalid_paths"]:
            console.print(f"  ❌ {path}")
    
    # Show resolved files
    if validation["resolved_files"] and not ctx.obj.get("quiet", False):
        console.print(f"\n[bold blue]Resolved Files ({len(validation['resolved_files'])}):[/bold blue]")
        for file_path in validation["resolved_files"][:10]:  # Show first 10
            console.print(f"  📄 {file_path}")
        
        if len(validation["resolved_files"]) > 10:
            console.print(f"  ... and {len(validation['resolved_files']) - 10} more files")


@context.command("search")
@click.argument("query")
@click.option(
    "--case-sensitive", "-c",
    is_flag=True,
    help="Case sensitive search"
)
@click.option(
    "--limit", "-l",
    default=10,
    help="Maximum number of results"
)
@click.pass_context
def context_search(ctx: click.Context, query: str, case_sensitive: bool = False, limit: int = 10):
    """Search for content in context files."""
    context_manager = ContextManager(ctx.obj["platform"], ctx.obj["config_manager"])
    
    results = context_manager.search_context_content(query, case_sensitive)
    
    if not results:
        console.print(f"[yellow]No matches found for '{query}'[/yellow]")
        return
    
    # Limit results
    results = results[:limit]
    
    console.print(f"[bold blue]Search Results for '{query}'[/bold blue]\n")
    
    for result in results:
        console.print(f"[bold green]📄 {result['file']}[/bold green] ({result['match_count']} matches)")
        
        for match in result["matches"][:3]:  # Show first 3 matches per file
            console.print(f"  [cyan]Line {match['line_number']}:[/cyan] {match['line_content']}")
        
        if len(result["matches"]) > 3:
            console.print(f"  ... and {len(result['matches']) - 3} more matches")
        
        console.print()


@context.command("optimize")
@click.pass_context
def context_optimize(ctx: click.Context):
    """Analyze and optimize context loading performance."""
    context_manager = ContextManager(ctx.obj["platform"], ctx.obj["config_manager"])
    
    optimization = context_manager.optimize_context_loading()
    
    # Create optimization report
    table = Table(title="Context Optimization Report")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Files", str(optimization["total_files"]))
    table.add_row("Total Size", f"{optimization['total_size']:,} bytes")
    table.add_row("Large Files", str(len(optimization["large_files"])))
    table.add_row("Duplicate Files", str(len(optimization["duplicate_content"])))
    
    console.print(table)
    
    # Show large files
    if optimization["large_files"]:
        console.print("\n[bold yellow]Large Files (>100KB):[/bold yellow]")
        for file_info in optimization["large_files"]:
            console.print(f"  📄 {file_info['file']} ({file_info['size_mb']} MB)")
    
    # Show duplicate files
    if optimization["duplicate_content"]:
        console.print("\n[bold yellow]Duplicate Content:[/bold yellow]")
        for dup_info in optimization["duplicate_content"]:
            console.print(f"  🔄 {' = '.join(dup_info['files'])}")
    
    # Show recommendations
    if optimization["recommendations"]:
        console.print("\n[bold blue]Recommendations:[/bold blue]")
        for rec in optimization["recommendations"]:
            console.print(f"  💡 {rec}")
    else:
        console.print("\n[bold green]✅ Context configuration is optimized![/bold green]")
