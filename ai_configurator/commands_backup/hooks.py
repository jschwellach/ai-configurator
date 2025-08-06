"""Hook management CLI commands."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from ..core import HookManager

console = Console()


@click.group()
def hooks():
    """Manage hooks and automation scripts."""
    pass


@hooks.command("list")
@click.pass_context
def hooks_list(ctx: click.Context):
    """List available hooks."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    hooks_info = hook_manager.list_available_hooks()
    
    # Create table
    table = Table(title="Available Hooks")
    table.add_column("Type", style="cyan")
    table.add_column("Hook", style="green")
    table.add_column("Status", style="yellow")
    
    # Python hooks
    for hook in hooks_info["python"]:
        table.add_row("Python", hook, "🐍 Ready")
    
    # Shell hooks
    for hook in hooks_info["shell"]:
        table.add_row("Shell", hook, "🐚 Ready")
    
    # Config files
    for config in hooks_info["config"]:
        table.add_row("Config", config, "⚙️ Config")
    
    if not any(hooks_info.values()):
        console.print("[yellow]No hooks found[/yellow]")
        return
    
    console.print(table)


@hooks.command("run")
@click.argument("hook_name")
@click.option(
    "--args", "-a",
    help="Arguments to pass to the hook (space-separated)"
)
@click.option(
    "--timeout", "-t",
    default=30,
    help="Timeout in seconds"
)
@click.pass_context
def hooks_run(ctx: click.Context, hook_name: str, args: str = None, timeout: int = 30):
    """Execute a hook."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    # Parse arguments
    hook_args = args.split() if args else None
    
    console.print(f"[blue]Executing hook: {hook_name}[/blue]")
    if hook_args:
        console.print(f"[blue]Arguments: {' '.join(hook_args)}[/blue]")
    
    # Execute hook
    success, stdout, stderr = hook_manager.execute_hook(hook_name, hook_args, timeout=timeout)
    
    # Display results
    if success:
        console.print(f"[bold green]✅ Hook '{hook_name}' executed successfully[/bold green]")
    else:
        console.print(f"[bold red]❌ Hook '{hook_name}' failed[/bold red]")
    
    # Show output
    if stdout:
        console.print("\n[bold blue]Output:[/bold blue]")
        console.print(Panel(stdout, border_style="green"))
    
    if stderr:
        console.print("\n[bold red]Errors:[/bold red]")
        console.print(Panel(stderr, border_style="red"))


@hooks.command("test")
@click.argument("hook_name")
@click.pass_context
def hooks_test(ctx: click.Context, hook_name: str):
    """Test a hook and show detailed results."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    console.print(f"[blue]Testing hook: {hook_name}[/blue]")
    
    test_result = hook_manager.test_hook(hook_name)
    
    # Create test results table
    table = Table(title=f"Hook Test Results: {hook_name}")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    # File exists
    status = "✅ Pass" if test_result["exists"] else "❌ Fail"
    table.add_row("File Exists", status, "")
    
    # Executable
    if test_result["exists"]:
        status = "✅ Pass" if test_result["executable"] else "❌ Fail"
        table.add_row("Executable", status, "")
    
    # Execution
    if test_result["executable"]:
        status = "✅ Pass" if test_result["success"] else "❌ Fail"
        time_info = f"{test_result['execution_time']}s"
        table.add_row("Execution", status, time_info)
    
    console.print(table)
    
    # Show error if any
    if test_result["error"]:
        console.print(f"\n[bold red]Error:[/bold red] {test_result['error']}")
    
    # Show output
    if test_result["stdout"]:
        console.print("\n[bold blue]Output:[/bold blue]")
        console.print(Panel(test_result["stdout"], border_style="green"))
    
    if test_result["stderr"]:
        console.print("\n[bold red]Errors:[/bold red]")
        console.print(Panel(test_result["stderr"], border_style="red"))


@hooks.command("validate")
@click.pass_context
def hooks_validate(ctx: click.Context):
    """Validate all hooks."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    console.print("[blue]Validating hooks...[/blue]")
    
    validation = hook_manager.validate_hooks()
    
    # Create validation summary table
    table = Table(title="Hook Validation Summary")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    
    table.add_row("Valid Hooks", str(len(validation["valid_hooks"])))
    table.add_row("Invalid Hooks", str(len(validation["invalid_hooks"])))
    table.add_row("Executable Hooks", str(len(validation["executable_hooks"])))
    table.add_row("Config Issues", str(len(validation["config_issues"])))
    
    console.print(table)
    
    # Show invalid hooks
    if validation["invalid_hooks"]:
        console.print("\n[bold red]Invalid Hooks:[/bold red]")
        for hook_info in validation["invalid_hooks"]:
            console.print(f"  ❌ {hook_info['hook']}: {hook_info['issue']}")
    
    # Show config issues
    if validation["config_issues"]:
        console.print("\n[bold yellow]Configuration Issues:[/bold yellow]")
        for issue in validation["config_issues"]:
            console.print(f"  ⚠️ {issue}")
    
    # Show recommendations
    if validation["recommendations"]:
        console.print("\n[bold blue]Recommendations:[/bold blue]")
        for rec in validation["recommendations"]:
            console.print(f"  💡 {rec}")
    else:
        console.print("\n[bold green]✅ All hooks are valid![/bold green]")


@hooks.command("create")
@click.argument("hook_name")
@click.option(
    "--type", "-t",
    "hook_type",  # Use a different variable name to avoid shadowing built-in type()
    type=click.Choice(["python", "shell"]),
    default="python",
    help="Type of hook to create"
)
@click.pass_context
def hooks_create(ctx: click.Context, hook_name: str, hook_type: str):
    """Create a new hook from template."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    console.print(f"[blue]Creating {hook_type} hook: {hook_name}[/blue]")
    
    success = hook_manager.create_script_hook_template(hook_name, hook_type)
    
    if success:
        console.print(f"[bold green]✅ Hook '{hook_name}' created successfully[/bold green]")
        
        # Show the created file path
        hook_file = hook_manager.hooks_dir / f"{hook_name}.{'py' if hook_type == 'python' else 'sh'}"
        console.print(f"[blue]Location:[/blue] {hook_file}")
        
        # Show next steps
        console.print("\n[bold blue]Next steps:[/bold blue]")
        console.print(f"1. Edit the hook file: {hook_file}")
        console.print(f"2. Test the hook: [cyan]ai-config hooks test {hook_name}.{'py' if hook_type == 'python' else 'sh'}[/cyan]")
        console.print(f"3. Run the hook: [cyan]ai-config hooks run {hook_name}.{'py' if hook_type == 'python' else 'sh'}[/cyan]")
    else:
        console.print(f"[bold red]❌ Failed to create hook '{hook_name}'[/bold red]")


@hooks.command("context")
@click.argument("context_name")
@click.pass_context
def hooks_context(ctx: click.Context, context_name: str):
    """Load context using hooks."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    console.print(f"[blue]Loading context: {context_name}[/blue]")
    
    success, content = hook_manager.execute_context_hook(context_name)
    
    if success:
        console.print(f"[bold green]✅ Context '{context_name}' loaded successfully[/bold green]")
        
        if content and not ctx.obj.get("quiet", False):
            # Display context content with syntax highlighting
            syntax = Syntax(content, "markdown", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Context: {context_name}", border_style="blue"))
    else:
        console.print(f"[bold red]❌ Failed to load context '{context_name}'[/bold red]")
        console.print(f"[red]Error: {content}[/red]")


@hooks.command("config")
@click.pass_context
def hooks_config(ctx: click.Context):
    """Show hook configuration."""
    config_manager = ctx.obj["config_manager"]
    hook_manager = HookManager(
        config_dir=config_manager.config_dir,
        yaml_loader=config_manager.yaml_loader,
        platform_manager=ctx.obj["platform"]
    )
    
    config = hook_manager.load_hook_config()
    
    if not config:
        console.print("[yellow]No hook configuration found[/yellow]")
        return
    
    # Display configuration
    import yaml
    config_yaml = yaml.dump(config, default_flow_style=False, allow_unicode=True)
    
    syntax = Syntax(config_yaml, "yaml", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Hook Configuration", border_style="blue"))
    
    # Show available contexts
    contexts = config.get("contexts", {})
    if contexts:
        console.print("\n[bold blue]Available Contexts:[/bold blue]")
        for context_name, files in contexts.items():
            console.print(f"  📋 {context_name}: {len(files)} files")
            for file_path in files:
                console.print(f"    📄 {file_path}")
