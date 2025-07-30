"""Main CLI interface for AI Configurator."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .commands.context import context
from .commands.hooks import hooks
from .commands.migrate import migrate
from .commands.structure import structure
from .core import ConfigurationManager, PlatformManager
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
    """AI Configurator - Cross-platform configuration manager for Amazon Q CLI.
    
    Supports both YAML and JSON configuration formats with automatic migration tools.
    Use 'ai-config formats' to learn about configuration formats and migration options.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    
    # Setup logging
    log_level = "DEBUG" if verbose else "WARNING" if quiet else "INFO"
    setup_logging(log_level)
    
    # Initialize managers
    ctx.obj["platform"] = PlatformManager()
    ctx.obj["config_manager"] = ConfigurationManager(ctx.obj["platform"])


@cli.command()
@click.option(
    "--profile", "-p",
    help="Install with specific profile (e.g., developer, solutions-architect)"
)
@click.option(
    "--mcp-servers",
    help="Comma-separated list of MCP server groups to install"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Force installation even if configuration exists"
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Skip creating backup before installation"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be installed without actually installing"
)
@click.option(
    "--format",
    type=click.Choice(["yaml", "json", "auto"]),
    default="auto",
    help="Configuration format to use (auto detects based on existing files)"
)
@click.pass_context
def install(
    ctx: click.Context, 
    profile: Optional[str], 
    mcp_servers: Optional[str], 
    force: bool,
    no_backup: bool,
    dry_run: bool,
    format: str
) -> None:
    """Install Amazon Q CLI configuration (supports both YAML and JSON formats)."""
    from .core import InstallationManager, InstallationConfig
    
    platform = ctx.obj["platform"]
    config_manager = ctx.obj["config_manager"]
    installer = InstallationManager(platform, config_manager)
    
    # Check if Amazon Q CLI is installed
    if not platform.is_amazonq_installed():
        console.print("[red]Error: Amazon Q CLI not found. Please install it first.[/red]")
        console.print("\nTo install Amazon Q CLI:")
        console.print("• Visit: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-getting-started-installing.html")
        sys.exit(1)
    
    # Parse MCP server groups
    mcp_groups = []
    if mcp_servers:
        mcp_groups = [group.strip() for group in mcp_servers.split(",")]
    
    # Create installation configuration
    install_config = InstallationConfig(
        profile=profile,
        mcp_servers=mcp_groups if mcp_groups else None,
        backup_before_install=not no_backup,
        force=force
    )
    
    # Show available options if no profile specified
    if not profile:
        available_profiles = installer.get_available_profiles()
        if available_profiles:
            console.print("[yellow]Available profiles:[/yellow]")
            for p in available_profiles:
                console.print(f"  • {p}")
            console.print("\nUse --profile to specify a profile, or continue with 'default'")
            install_config.profile = "default"
    
    # Show available MCP groups if none specified
    if not mcp_groups:
        available_groups = installer.get_available_mcp_groups()
        if available_groups:
            console.print("[yellow]Available MCP server groups:[/yellow]")
            for group in available_groups:
                console.print(f"  • {group}")
            console.print("\nUse --mcp-servers to specify groups, or continue with 'core'")
            install_config.mcp_servers = ["core"]
    
    # Check if configuration already exists
    if config_manager.config_dir.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_manager.config_dir}[/yellow]")
        console.print("Use --force to overwrite or run 'ai-config update' to update existing configuration.")
        sys.exit(1)
    
    # Show installation summary
    if not ctx.obj["quiet"]:
        console.print(Panel.fit(
            "[bold blue]AI Configurator Installation[/bold blue]\n"
            "Setting up your Amazon Q CLI configuration...",
            border_style="blue"
        ))
    
    summary = installer.get_installation_summary(install_config)
    
    # Create summary table
    table = Table(title="Installation Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="green")
    
    table.add_row("Profile", summary["profile"])
    table.add_row("MCP Groups", ", ".join(summary["mcp_groups"]))
    table.add_row("MCP Servers", f"{len(summary['mcp_servers'])} servers")
    table.add_row("Context Files", f"{len(summary['context_files'])} files")
    table.add_row("Hooks", f"{len(summary['hooks'])} files")
    table.add_row("Backup", "Yes" if summary["backup_before_install"] else "No")
    
    console.print(table)
    
    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        
        # Show detailed information
        if summary["mcp_servers"]:
            console.print("\n[bold]MCP Servers to be installed:[/bold]")
            for server in summary["mcp_servers"]:
                console.print(f"  • {server}")
        
        if summary["context_files"]:
            console.print("\n[bold]Context files to be copied:[/bold]")
            for file in summary["context_files"]:
                console.print(f"  • {file}")
        
        return
    
    # Confirm installation
    if not force and not ctx.obj["quiet"]:
        if not click.confirm("\nProceed with installation?"):
            console.print("[yellow]Installation cancelled.[/yellow]")
            return
    
    # Perform installation
    console.print("\n[blue]Installing configuration...[/blue]")
    
    success = installer.install(install_config)
    
    if success:
        console.print("\n[bold green]✅ Installation completed successfully![/bold green]")
        console.print(f"\nConfiguration installed to: {config_manager.config_dir}")
        console.print("\nNext steps:")
        console.print("1. Test your configuration: [cyan]q chat[/cyan]")
        console.print("2. Validate setup: [cyan]ai-config validate[/cyan]")
        console.print("3. View status: [cyan]ai-config status[/cyan]")
    else:
        console.print("\n[bold red]❌ Installation failed![/bold red]")
        console.print("Check the logs above for details.")
        sys.exit(1)


@cli.command()
@click.option(
    "--preserve-personal",
    is_flag=True,
    help="Preserve personal customizations during update"
)
@click.option(
    "--selective",
    help="Update only specific components (comma-separated: mcp,profiles,contexts,hooks)"
)
@click.option(
    "--check-only",
    is_flag=True,
    help="Only check for updates without applying them"
)
@click.pass_context
def update(ctx: click.Context, preserve_personal: bool, selective: str, check_only: bool) -> None:
    """Update existing Amazon Q CLI configuration."""
    from .core import UpdateManager
    
    config_manager = ctx.obj["config_manager"]
    update_manager = UpdateManager(ctx.obj["platform"], config_manager)
    
    if check_only:
        console.print("[blue]Checking for updates...[/blue]")
        
        update_info = update_manager.check_for_updates()
        
        # Create update summary table
        table = Table(title="Available Updates")
        table.add_column("Component", style="cyan")
        table.add_column("Updates", style="green")
        table.add_column("Status", style="yellow")
        
        table.add_row("MCP Servers", str(len(update_info["mcp_updates"])), 
                     "✅ Available" if update_info["mcp_updates"] else "✅ Up to date")
        table.add_row("Profiles", str(len(update_info["profile_updates"])), 
                     "✅ Available" if update_info["profile_updates"] else "✅ Up to date")
        table.add_row("Contexts", str(len(update_info["context_updates"])), 
                     "✅ Available" if update_info["context_updates"] else "✅ Up to date")
        table.add_row("Hooks", str(len(update_info["hook_updates"])), 
                     "✅ Available" if update_info["hook_updates"] else "✅ Up to date")
        
        console.print(table)
        
        # Show recommendations
        if update_info["recommendations"]:
            console.print("\n[bold blue]Recommendations:[/bold blue]")
            for rec in update_info["recommendations"]:
                console.print(f"  💡 {rec}")
        else:
            console.print("\n[bold green]✅ All components are up to date![/bold green]")
        
        return
    
    # Parse selective components
    selective_components = None
    if selective:
        selective_components = [comp.strip() for comp in selective.split(",")]
        valid_components = ["mcp", "profiles", "contexts", "hooks"]
        invalid_components = [comp for comp in selective_components if comp not in valid_components]
        
        if invalid_components:
            console.print(f"[red]Invalid components: {', '.join(invalid_components)}[/red]")
            console.print(f"Valid components: {', '.join(valid_components)}")
            return
    
    # Confirm update
    if not ctx.obj.get("quiet", False):
        update_type = "selective" if selective_components else "full"
        preserve_msg = " (preserving personal configs)" if preserve_personal else ""
        
        console.print(f"[yellow]This will perform a {update_type} update{preserve_msg}[/yellow]")
        
        if not click.confirm("Continue with update?"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return
    
    # Perform update
    console.print("[blue]Updating configuration...[/blue]")
    
    success = update_manager.update_configuration(
        preserve_personal=preserve_personal,
        selective_update=selective_components
    )
    
    if success:
        console.print("[bold green]✅ Configuration updated successfully![/bold green]")
        console.print("\nNext steps:")
        console.print("1. Validate configuration: [cyan]ai-config validate[/cyan]")
        console.print("2. Test your setup: [cyan]q chat[/cyan]")
    else:
        console.print("[bold red]❌ Configuration update failed![/bold red]")
        console.print("Your previous configuration has been restored from backup.")
        sys.exit(1)


@cli.group()
def profile() -> None:
    """Manage configuration profiles (supports both YAML and JSON formats)."""
    pass


@profile.command("list")
@click.option(
    "--format", "-f",
    type=click.Choice(["table", "yaml", "json"]),
    default="table",
    help="Output format for profile list"
)
@click.pass_context
def profile_list(ctx: click.Context, format: str) -> None:
    """List available profiles (supports both JSON and YAML configurations)."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    active_profile = config_manager.get_active_profile()
    
    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
        return
    
    # Get detailed profile information including format
    profile_details = []
    for profile_name in profiles:
        try:
            # Check if YAML version exists
            yaml_path = config_manager.config_dir / "profiles" / f"{profile_name}.yaml"
            json_path = config_manager.config_dir / "profiles" / profile_name / "context.json"
            
            config_format = "Unknown"
            if yaml_path.exists() and json_path.exists():
                config_format = "YAML+JSON"
            elif yaml_path.exists():
                config_format = "YAML"
            elif json_path.exists():
                config_format = "JSON"
            
            profile_details.append({
                "name": profile_name,
                "format": config_format,
                "active": profile_name == active_profile
            })
        except Exception:
            profile_details.append({
                "name": profile_name,
                "format": "Unknown",
                "active": profile_name == active_profile
            })
    
    if format == "json":
        import json
        console.print(json.dumps(profile_details, indent=2))
    elif format == "yaml":
        import yaml
        console.print(yaml.dump(profile_details, default_flow_style=False))
    else:
        # Table format (default)
        table = Table(title="Available Profiles")
        table.add_column("Profile", style="cyan")
        table.add_column("Format", style="blue")
        table.add_column("Status", style="green")
        
        for profile in profile_details:
            status = "✅ Active" if profile["active"] else ""
            table.add_row(profile["name"], profile["format"], status)
        
        console.print(table)


@profile.command("switch")
@click.argument("profile_name")
@click.pass_context
def profile_switch(ctx: click.Context, profile_name: str) -> None:
    """Switch to a different profile (supports both JSON and YAML configurations)."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    
    if profile_name not in profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        console.print(f"Available profiles: {', '.join(profiles)}")
        sys.exit(1)
    
    console.print(f"[yellow]Switching to profile '{profile_name}' - functionality coming soon![/yellow]")


@profile.command("create")
@click.argument("profile_name")
@click.option(
    "--format", "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Configuration format for new profile"
)
@click.option(
    "--description", "-d",
    help="Profile description"
)
@click.option(
    "--template", "-t",
    help="Template profile to copy from"
)
@click.pass_context
def profile_create(ctx: click.Context, profile_name: str, format: str, description: str, template: str) -> None:
    """Create a new profile in YAML or JSON format."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    
    if profile_name in profiles:
        console.print(f"[red]Profile '{profile_name}' already exists.[/red]")
        sys.exit(1)
    
    if format == "yaml":
        # Create YAML profile
        profile_path = config_manager.config_dir / "profiles" / f"{profile_name}.yaml"
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create basic YAML structure
        profile_config = {
            "name": profile_name,
            "description": description or f"Profile: {profile_name}",
            "version": "1.0",
            "contexts": [],
            "hooks": {},
            "mcp_servers": [],
            "settings": {
                "auto_backup": True,
                "validation_level": "normal",
                "hot_reload": True,
                "cache_enabled": True
            },
            "metadata": {
                "created_date": ctx.obj["config_manager"]._get_current_timestamp() if hasattr(ctx.obj["config_manager"], '_get_current_timestamp') else "unknown"
            }
        }
        
        # Copy from template if specified
        if template:
            if template in profiles:
                template_yaml = config_manager.config_dir / "profiles" / f"{template}.yaml"
                if template_yaml.exists():
                    import yaml
                    with open(template_yaml, 'r', encoding='utf-8') as f:
                        template_config = yaml.safe_load(f)
                    
                    # Merge template config but keep new name and description
                    profile_config.update(template_config)
                    profile_config["name"] = profile_name
                    if description:
                        profile_config["description"] = description
                else:
                    console.print(f"[yellow]Template '{template}' is not in YAML format, using default structure.[/yellow]")
            else:
                console.print(f"[red]Template profile '{template}' not found.[/red]")
                sys.exit(1)
        
        # Write YAML file
        import yaml
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(profile_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        console.print(f"[green]✅ YAML profile '{profile_name}' created at {profile_path}[/green]")
    
    else:
        # Create JSON profile (legacy format)
        profile_dir = config_manager.config_dir / "profiles" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        context_file = profile_dir / "context.json"
        hooks_file = profile_dir / "hooks.json"
        
        # Create basic JSON structure
        context_config = {
            "paths": [],
            "description": description or f"Profile: {profile_name}"
        }
        
        hooks_config = {
            "on_session_start": [],
            "per_user_message": [],
            "on_file_change": []
        }
        
        # Copy from template if specified
        if template:
            if template in profiles:
                template_dir = config_manager.config_dir / "profiles" / template
                template_context = template_dir / "context.json"
                template_hooks = template_dir / "hooks.json"
                
                if template_context.exists():
                    import json
                    with open(template_context, 'r', encoding='utf-8') as f:
                        context_config = json.load(f)
                    if description:
                        context_config["description"] = description
                
                if template_hooks.exists():
                    import json
                    with open(template_hooks, 'r', encoding='utf-8') as f:
                        hooks_config = json.load(f)
            else:
                console.print(f"[red]Template profile '{template}' not found.[/red]")
                sys.exit(1)
        
        # Write JSON files
        import json
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context_config, f, indent=2)
        
        with open(hooks_file, 'w', encoding='utf-8') as f:
            json.dump(hooks_config, f, indent=2)
        
        console.print(f"[green]✅ JSON profile '{profile_name}' created at {profile_dir}[/green]")
    
    # Show next steps
    console.print("\n[bold blue]Next steps:[/bold blue]")
    console.print(f"1. Edit the profile configuration")
    console.print(f"2. Add context paths and hook definitions")
    console.print(f"3. Test the profile: [cyan]ai-config profile validate {profile_name}[/cyan]")


@profile.command("validate")
@click.argument("profile_name", required=False)
@click.option(
    "--all", "-a",
    is_flag=True,
    help="Validate all profiles"
)
@click.pass_context
def profile_validate(ctx: click.Context, profile_name: str, all: bool) -> None:
    """Validate profile configurations (supports both JSON and YAML)."""
    config_manager = ctx.obj["config_manager"]
    
    if all:
        profiles = config_manager.list_profiles()
        if not profiles:
            console.print("[yellow]No profiles found to validate.[/yellow]")
            return
    else:
        if not profile_name:
            console.print("[red]Please specify a profile name or use --all flag.[/red]")
            sys.exit(1)
        
        profiles = [profile_name]
        if profile_name not in config_manager.list_profiles():
            console.print(f"[red]Profile '{profile_name}' not found.[/red]")
            sys.exit(1)
    
    console.print("[blue]Validating profile configurations...[/blue]\n")
    
    total_errors = 0
    total_warnings = 0
    
    for profile in profiles:
        console.print(f"[bold cyan]Validating profile: {profile}[/bold cyan]")
        
        # Check both YAML and JSON formats
        yaml_path = config_manager.config_dir / "profiles" / f"{profile}.yaml"
        json_dir = config_manager.config_dir / "profiles" / profile
        
        profile_errors = []
        profile_warnings = []
        
        if yaml_path.exists():
            # Validate YAML profile
            try:
                import yaml
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                
                # Basic validation
                required_fields = ["name", "version"]
                for field in required_fields:
                    if field not in yaml_config:
                        profile_errors.append(f"Missing required field: {field}")
                
                # Validate contexts exist
                if "contexts" in yaml_config:
                    for context_path in yaml_config["contexts"]:
                        if not context_path.startswith("*") and not context_path.endswith("*"):
                            full_path = config_manager.config_dir / context_path
                            if not full_path.exists():
                                profile_warnings.append(f"Context file not found: {context_path}")
                
                console.print(f"  ✅ YAML format validation passed")
                
            except yaml.YAMLError as e:
                profile_errors.append(f"YAML syntax error: {e}")
            except Exception as e:
                profile_errors.append(f"YAML validation error: {e}")
        
        if json_dir.exists() and (json_dir / "context.json").exists():
            # Validate JSON profile
            try:
                import json
                context_file = json_dir / "context.json"
                with open(context_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                
                # Validate contexts exist
                if "paths" in json_config:
                    for context_path in json_config["paths"]:
                        if not context_path.startswith("*") and not context_path.endswith("*"):
                            full_path = config_manager.config_dir / context_path
                            if not full_path.exists():
                                profile_warnings.append(f"Context file not found: {context_path}")
                
                console.print(f"  ✅ JSON format validation passed")
                
            except json.JSONDecodeError as e:
                profile_errors.append(f"JSON syntax error: {e}")
            except Exception as e:
                profile_errors.append(f"JSON validation error: {e}")
        
        # Show results for this profile
        if profile_errors:
            console.print(f"  [red]❌ {len(profile_errors)} errors found[/red]")
            for error in profile_errors:
                console.print(f"    • {error}")
            total_errors += len(profile_errors)
        
        if profile_warnings:
            console.print(f"  [yellow]⚠️ {len(profile_warnings)} warnings found[/yellow]")
            for warning in profile_warnings:
                console.print(f"    • {warning}")
            total_warnings += len(profile_warnings)
        
        if not profile_errors and not profile_warnings:
            console.print(f"  [green]✅ Profile is valid[/green]")
        
        console.print()
    
    # Summary
    if total_errors > 0:
        console.print(f"[bold red]❌ Validation completed with {total_errors} errors and {total_warnings} warnings[/bold red]")
        sys.exit(1)
    elif total_warnings > 0:
        console.print(f"[bold yellow]⚠️ Validation completed with {total_warnings} warnings[/bold yellow]")
    else:
        console.print(f"[bold green]✅ All profiles are valid![/bold green]")


@profile.command("convert")
@click.argument("profile_name")
@click.option(
    "--to-format", "-t",
    type=click.Choice(["yaml", "json"]),
    required=True,
    help="Target format for conversion"
)
@click.option(
    "--backup", "-b",
    is_flag=True,
    help="Create backup before conversion"
)
@click.pass_context
def profile_convert(ctx: click.Context, profile_name: str, to_format: str, backup: bool) -> None:
    """Convert profile between JSON and YAML formats."""
    config_manager = ctx.obj["config_manager"]
    profiles = config_manager.list_profiles()
    
    if profile_name not in profiles:
        console.print(f"[red]Profile '{profile_name}' not found.[/red]")
        sys.exit(1)
    
    yaml_path = config_manager.config_dir / "profiles" / f"{profile_name}.yaml"
    json_dir = config_manager.config_dir / "profiles" / profile_name
    
    if to_format == "yaml":
        # Convert JSON to YAML
        if not json_dir.exists() or not (json_dir / "context.json").exists():
            console.print(f"[red]No JSON configuration found for profile '{profile_name}'.[/red]")
            sys.exit(1)
        
        if yaml_path.exists():
            console.print(f"[yellow]YAML configuration already exists for profile '{profile_name}'.[/yellow]")
            if not click.confirm("Overwrite existing YAML configuration?"):
                return
        
        # Create backup if requested
        if backup:
            backup_id = config_manager.create_backup(f"Before converting {profile_name} to YAML")
            if backup_id:
                console.print(f"[green]Backup created: {backup_id}[/green]")
        
        # Load JSON configuration
        import json
        context_file = json_dir / "context.json"
        hooks_file = json_dir / "hooks.json"
        
        with open(context_file, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
        
        hooks_config = {}
        if hooks_file.exists():
            with open(hooks_file, 'r', encoding='utf-8') as f:
                hooks_config = json.load(f)
        
        # Convert to YAML format
        yaml_config = {
            "name": profile_name,
            "description": json_config.get("description", f"Converted profile: {profile_name}"),
            "version": "1.0",
            "contexts": json_config.get("paths", []),
            "hooks": {},
            "mcp_servers": [],
            "settings": {
                "auto_backup": True,
                "validation_level": "normal",
                "hot_reload": True,
                "cache_enabled": True
            },
            "metadata": {
                "converted_from": "json",
                "conversion_date": "unknown"
            }
        }
        
        # Convert hooks
        for trigger, commands in hooks_config.items():
            if commands:
                hook_refs = []
                for i, command in enumerate(commands):
                    hook_refs.append({
                        "name": f"{profile_name}_{trigger}_{i}",
                        "enabled": True,
                        "config": {
                            "command": command,
                            "converted": True
                        }
                    })
                yaml_config["hooks"][trigger] = hook_refs
        
        # Write YAML file
        import yaml
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        console.print(f"[green]✅ Profile '{profile_name}' converted to YAML format[/green]")
        console.print(f"[blue]YAML file created: {yaml_path}[/blue]")
    
    else:
        # Convert YAML to JSON
        if not yaml_path.exists():
            console.print(f"[red]No YAML configuration found for profile '{profile_name}'.[/red]")
            sys.exit(1)
        
        if json_dir.exists() and (json_dir / "context.json").exists():
            console.print(f"[yellow]JSON configuration already exists for profile '{profile_name}'.[/yellow]")
            if not click.confirm("Overwrite existing JSON configuration?"):
                return
        
        # Create backup if requested
        if backup:
            backup_id = config_manager.create_backup(f"Before converting {profile_name} to JSON")
            if backup_id:
                console.print(f"[green]Backup created: {backup_id}[/green]")
        
        # Load YAML configuration
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        
        # Convert to JSON format
        json_dir.mkdir(parents=True, exist_ok=True)
        
        context_config = {
            "paths": yaml_config.get("contexts", []),
            "description": yaml_config.get("description", f"Converted profile: {profile_name}")
        }
        
        hooks_config = {}
        for trigger, hook_refs in yaml_config.get("hooks", {}).items():
            commands = []
            for hook_ref in hook_refs:
                if isinstance(hook_ref, dict) and "config" in hook_ref:
                    command = hook_ref["config"].get("command", "")
                    if command:
                        commands.append(command)
            hooks_config[trigger] = commands
        
        # Write JSON files
        import json
        with open(json_dir / "context.json", 'w', encoding='utf-8') as f:
            json.dump(context_config, f, indent=2)
        
        with open(json_dir / "hooks.json", 'w', encoding='utf-8') as f:
            json.dump(hooks_config, f, indent=2)
        
        console.print(f"[green]✅ Profile '{profile_name}' converted to JSON format[/green]")
        console.print(f"[blue]JSON files created in: {json_dir}[/blue]")
    
    console.print("\n[bold blue]Next steps:[/bold blue]")
    console.print(f"1. Validate the converted profile: [cyan]ai-config profile validate {profile_name}[/cyan]")
    console.print(f"2. Test the profile configuration")
    console.print(f"3. Remove old format files if conversion was successful")


@cli.command()
@click.option(
    "--description", "-d",
    help="Description for the backup"
)
@click.pass_context
def backup(ctx: click.Context, description: Optional[str]) -> None:
    """Backup current configuration."""
    config_manager = ctx.obj["config_manager"]
    
    if not config_manager.config_dir.exists():
        console.print("[red]No configuration found to backup.[/red]")
        sys.exit(1)
    
    console.print("[blue]Creating backup...[/blue]")
    backup_id = config_manager.create_backup(description)
    
    if backup_id:
        console.print(f"[green]✅ Backup created successfully: {backup_id}[/green]")
    else:
        console.print("[red]❌ Failed to create backup.[/red]")
        sys.exit(1)


@cli.command()
@click.argument("backup_id")
@click.pass_context
def restore(ctx: click.Context, backup_id: str) -> None:
    """Restore configuration from backup."""
    config_manager = ctx.obj["config_manager"]
    
    # List available backups if backup_id is 'list'
    if backup_id.lower() == "list":
        backups = config_manager.list_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
            return
        
        table = Table(title="Available Backups")
        table.add_column("Backup ID", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Profile", style="magenta")
        
        for backup in backups:
            table.add_row(
                backup.backup_id,
                backup.timestamp,
                backup.description or "",
                backup.profile or ""
            )
        
        console.print(table)
        return
    
    console.print(f"[blue]Restoring from backup: {backup_id}[/blue]")
    success = config_manager.restore_backup(backup_id)
    
    if success:
        console.print(f"[green]✅ Configuration restored successfully from {backup_id}[/green]")
    else:
        console.print(f"[red]❌ Failed to restore from backup {backup_id}[/red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["all", "yaml", "json"]),
    default="all",
    help="Validate specific configuration format"
)
@click.option(
    "--strict",
    is_flag=True,
    help="Use strict validation mode"
)
@click.pass_context
def validate(ctx: click.Context, format: str, strict: bool) -> None:
    """Validate current configuration (supports both YAML and JSON formats)."""
    config_manager = ctx.obj["config_manager"]
    
    console.print("[bold blue]Validating Amazon Q CLI Configuration[/bold blue]\n")
    
    result = config_manager.validate_configuration()
    
    # Show validation results
    for item, status in result.checked_items.items():
        icon = "✅" if status else "❌"
        color = "green" if status else "red"
        item_name = item.replace("_", " ").title()
        console.print(f"{icon} {item_name}: [{color}]{'OK' if status else 'Failed'}[/{color}]")
    
    # Show errors
    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result.errors:
            console.print(f"  • {error}")
    
    # Show warnings
    if result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}")
    
    if result.is_valid:
        console.print("\n[bold green]✅ Configuration is valid![/bold green]")
    else:
        console.print("\n[bold red]❌ Configuration has errors that need to be fixed.[/bold red]")
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "yaml", "json"]),
    default="table",
    help="Output format for status information"
)
@click.pass_context
def status(ctx: click.Context, format: str) -> None:
    """Show current configuration status (includes YAML/JSON format information)."""
    config_manager = ctx.obj["config_manager"]
    state = config_manager.get_configuration_state()
    
    # Get configuration format information
    yaml_profiles = 0
    json_profiles = 0
    yaml_hooks = 0
    
    profiles_dir = config_manager.config_dir / "profiles"
    hooks_dir = config_manager.config_dir / "hooks"
    
    if profiles_dir.exists():
        yaml_profiles = len(list(profiles_dir.glob("*.yaml")))
        json_profiles = len([d for d in profiles_dir.iterdir() if d.is_dir() and (d / "context.json").exists()])
    
    if hooks_dir.exists():
        yaml_hooks = len(list(hooks_dir.glob("*.yaml")))
    
    # Prepare status data
    status_data = {
        "platform": state.platform,
        "ai_configurator_version": state.ai_configurator_version,
        "amazonq_installed": state.amazonq_installed,
        "amazonq_version": state.amazonq_version,
        "config_dir_path": state.config_dir_path,
        "config_dir_exists": state.config_dir_exists,
        "active_profile": state.active_profile,
        "installed_mcp_servers": len(state.installed_mcp_servers) if state.installed_mcp_servers else 0,
        "last_backup": state.last_backup,
        "yaml_profiles": yaml_profiles,
        "json_profiles": json_profiles,
        "yaml_hooks": yaml_hooks,
        "total_profiles": yaml_profiles + json_profiles
    }
    
    if format == "json":
        import json
        console.print(json.dumps(status_data, indent=2))
    elif format == "yaml":
        import yaml
        console.print(yaml.dump(status_data, default_flow_style=False))
    else:
        # Table format (default)
        table = Table(title="AI Configurator Status", show_header=False)
        table.add_column("Property", style="bold cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Platform", state.platform)
        table.add_row("AI Configurator Version", state.ai_configurator_version)
        table.add_row("Amazon Q CLI", "✅ Installed" if state.amazonq_installed else "❌ Not Found")
        
        if state.amazonq_version:
            table.add_row("Amazon Q Version", state.amazonq_version)
        
        table.add_row("Config Directory", state.config_dir_path)
        table.add_row("Config Exists", "✅ Yes" if state.config_dir_exists else "❌ No")
        
        if state.active_profile:
            table.add_row("Active Profile", state.active_profile)
        
        # Configuration format information
        table.add_row("YAML Profiles", str(yaml_profiles))
        table.add_row("JSON Profiles", str(json_profiles))
        table.add_row("YAML Hooks", str(yaml_hooks))
        
        if state.installed_mcp_servers:
            table.add_row("MCP Servers", f"{len(state.installed_mcp_servers)} installed")
        
        if state.last_backup:
            table.add_row("Last Backup", state.last_backup)
        
        console.print(table)


@cli.command()
@click.option(
    "--cleanup",
    is_flag=True,
    help="Clean up old files and free disk space"
)
@click.pass_context
def maintenance(ctx: click.Context, cleanup: bool) -> None:
    """Show maintenance status and perform cleanup."""
    from .core import UpdateManager
    
    config_manager = ctx.obj["config_manager"]
    update_manager = UpdateManager(ctx.obj["platform"], config_manager)
    
    if cleanup:
        console.print("[blue]Performing cleanup...[/blue]")
        
        cleanup_result = update_manager.cleanup_old_files()
        
        # Show cleanup results
        table = Table(title="Cleanup Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files Removed", str(len(cleanup_result["removed_files"])))
        table.add_row("Space Freed", f"{cleanup_result['freed_space']:,} bytes")
        table.add_row("Errors", str(len(cleanup_result["errors"])))
        
        console.print(table)
        
        if cleanup_result["removed_files"]:
            console.print("\n[bold blue]Removed Files:[/bold blue]")
            for file_path in cleanup_result["removed_files"][:10]:
                console.print(f"  🗑️ {file_path}")
            
            if len(cleanup_result["removed_files"]) > 10:
                console.print(f"  ... and {len(cleanup_result['removed_files']) - 10} more files")
        
        if cleanup_result["errors"]:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in cleanup_result["errors"]:
                console.print(f"  ❌ {error}")
        
        if cleanup_result["freed_space"] > 0:
            console.print(f"\n[bold green]✅ Cleanup completed! Freed {cleanup_result['freed_space']:,} bytes[/bold green]")
        else:
            console.print("\n[yellow]No cleanup needed[/yellow]")
    else:
        # Show maintenance status
        status = update_manager.get_maintenance_status()
        
        # Create status table
        table = Table(title="Maintenance Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # Health status
        health_color = {"good": "green", "fair": "yellow", "poor": "red"}.get(status["config_health"], "white")
        table.add_row("Configuration Health", status["config_health"].title(), f"[{health_color}]●[/{health_color}]")
        
        # Last update
        last_update = status["last_update"] or "Never"
        table.add_row("Last Update", last_update, "")
        
        # Backup count
        backup_status = "🟢 Good" if status["backup_count"] < 20 else "🟡 Many"
        table.add_row("Backup Count", str(status["backup_count"]), backup_status)
        
        # Disk usage
        disk_mb = status["disk_usage"] / (1024 * 1024)
        disk_status = "🟢 Good" if disk_mb < 100 else "🟡 Large"
        table.add_row("Disk Usage", f"{disk_mb:.1f} MB", disk_status)
        
        console.print(table)
        
        # Show recommendations
        if status["recommendations"]:
            console.print("\n[bold blue]Recommendations:[/bold blue]")
            for rec in status["recommendations"]:
                console.print(f"  💡 {rec}")
        else:
            console.print("\n[bold green]✅ System is well maintained![/bold green]")


# Add command groups
cli.add_command(context)
cli.add_command(hooks)
cli.add_command(migrate)
cli.add_command(structure)


@cli.group()
def yaml():
    """Manage YAML configuration files."""
    pass


@yaml.command("validate")
@click.option(
    "--strict", "-s",
    is_flag=True,
    help="Use strict validation mode"
)
@click.pass_context
def yaml_validate(ctx: click.Context, strict: bool) -> None:
    """Validate all YAML configuration files."""
    config_manager = ctx.obj["config_manager"]
    
    console.print("[blue]Validating YAML configuration files...[/blue]\n")
    
    # Find all YAML files
    yaml_files = []
    profiles_dir = config_manager.config_dir / "profiles"
    hooks_dir = config_manager.config_dir / "hooks"
    
    if profiles_dir.exists():
        yaml_files.extend(list(profiles_dir.glob("*.yaml")))
    if hooks_dir.exists():
        yaml_files.extend(list(hooks_dir.glob("*.yaml")))
    
    if not yaml_files:
        console.print("[yellow]No YAML configuration files found.[/yellow]")
        return
    
    total_errors = 0
    total_warnings = 0
    
    for yaml_file in yaml_files:
        console.print(f"[cyan]Validating: {yaml_file.name}[/cyan]")
        
        try:
            import yaml
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            errors = []
            warnings = []
            
            # Basic YAML structure validation
            if not isinstance(config, dict):
                errors.append("Configuration must be a YAML object/dictionary")
            else:
                # Common validation for all YAML configs
                if "name" not in config:
                    errors.append("Missing required field: name")
                
                if "version" not in config:
                    if strict:
                        errors.append("Missing required field: version")
                    else:
                        warnings.append("Missing recommended field: version")
                
                # Profile-specific validation
                if yaml_file.parent.name == "profiles":
                    if "contexts" in config and not isinstance(config["contexts"], list):
                        errors.append("Field 'contexts' must be a list")
                    
                    if "hooks" in config and not isinstance(config["hooks"], dict):
                        errors.append("Field 'hooks' must be a dictionary")
                    
                    if "mcp_servers" in config and not isinstance(config["mcp_servers"], list):
                        errors.append("Field 'mcp_servers' must be a list")
                
                # Hook-specific validation
                elif yaml_file.parent.name == "hooks":
                    required_hook_fields = ["trigger", "type"]
                    for field in required_hook_fields:
                        if field not in config:
                            errors.append(f"Missing required field: {field}")
                    
                    if "trigger" in config:
                        valid_triggers = ["on_session_start", "per_user_message", "on_file_change", "on_profile_switch"]
                        if config["trigger"] not in valid_triggers:
                            errors.append(f"Invalid trigger: {config['trigger']}. Valid triggers: {', '.join(valid_triggers)}")
                    
                    if "type" in config:
                        valid_types = ["context", "script", "hybrid"]
                        if config["type"] not in valid_types:
                            errors.append(f"Invalid type: {config['type']}. Valid types: {', '.join(valid_types)}")
            
            # Show results
            if errors:
                console.print(f"  [red]❌ {len(errors)} errors found[/red]")
                for error in errors:
                    console.print(f"    • {error}")
                total_errors += len(errors)
            
            if warnings:
                console.print(f"  [yellow]⚠️ {len(warnings)} warnings found[/yellow]")
                for warning in warnings:
                    console.print(f"    • {warning}")
                total_warnings += len(warnings)
            
            if not errors and not warnings:
                console.print(f"  [green]✅ Valid[/green]")
        
        except yaml.YAMLError as e:
            console.print(f"  [red]❌ YAML syntax error: {e}[/red]")
            total_errors += 1
        except Exception as e:
            console.print(f"  [red]❌ Validation error: {e}[/red]")
            total_errors += 1
        
        console.print()
    
    # Summary
    console.print(f"[bold blue]Validation Summary:[/bold blue]")
    console.print(f"• Files checked: {len(yaml_files)}")
    console.print(f"• Errors: {total_errors}")
    console.print(f"• Warnings: {total_warnings}")
    
    if total_errors > 0:
        console.print(f"\n[bold red]❌ Validation failed with {total_errors} errors[/bold red]")
        sys.exit(1)
    elif total_warnings > 0:
        console.print(f"\n[bold yellow]⚠️ Validation completed with {total_warnings} warnings[/bold yellow]")
    else:
        console.print(f"\n[bold green]✅ All YAML files are valid![/bold green]")


@yaml.command("format")
@click.option(
    "--check", "-c",
    is_flag=True,
    help="Check formatting without making changes"
)
@click.pass_context
def yaml_format(ctx: click.Context, check: bool) -> None:
    """Format YAML configuration files with consistent style."""
    config_manager = ctx.obj["config_manager"]
    
    # Find all YAML files
    yaml_files = []
    profiles_dir = config_manager.config_dir / "profiles"
    hooks_dir = config_manager.config_dir / "hooks"
    
    if profiles_dir.exists():
        yaml_files.extend(list(profiles_dir.glob("*.yaml")))
    if hooks_dir.exists():
        yaml_files.extend(list(hooks_dir.glob("*.yaml")))
    
    if not yaml_files:
        console.print("[yellow]No YAML configuration files found.[/yellow]")
        return
    
    console.print(f"[blue]{'Checking' if check else 'Formatting'} YAML files...[/blue]\n")
    
    formatted_files = []
    error_files = []
    
    for yaml_file in yaml_files:
        try:
            import yaml
            
            # Read current content
            with open(yaml_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
                config = yaml.safe_load(original_content)
            
            # Format with consistent style
            formatted_content = yaml.dump(
                config,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                width=120
            )
            
            # Add header comment if it's a profile or hook
            if yaml_file.parent.name == "profiles":
                header = f"# Profile Configuration: {config.get('name', yaml_file.stem)}\n"
                if config.get('description'):
                    header += f"# Description: {config['description']}\n"
                header += f"# Format: YAML\n\n"
                formatted_content = header + formatted_content
            elif yaml_file.parent.name == "hooks":
                header = f"# Hook Configuration: {config.get('name', yaml_file.stem)}\n"
                if config.get('description'):
                    header += f"# Description: {config['description']}\n"
                header += f"# Trigger: {config.get('trigger', 'unknown')}\n"
                header += f"# Format: YAML\n\n"
                formatted_content = header + formatted_content
            
            if original_content.strip() != formatted_content.strip():
                if check:
                    console.print(f"[yellow]📝 {yaml_file.name} needs formatting[/yellow]")
                else:
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
                    console.print(f"[green]✅ Formatted {yaml_file.name}[/green]")
                formatted_files.append(yaml_file)
            else:
                console.print(f"[blue]✓ {yaml_file.name} already formatted[/blue]")
        
        except Exception as e:
            console.print(f"[red]❌ Error processing {yaml_file.name}: {e}[/red]")
            error_files.append(yaml_file)
    
    # Summary
    console.print(f"\n[bold blue]Summary:[/bold blue]")
    console.print(f"• Files processed: {len(yaml_files)}")
    console.print(f"• Files {'needing formatting' if check else 'formatted'}: {len(formatted_files)}")
    console.print(f"• Errors: {len(error_files)}")
    
    if check and formatted_files:
        console.print(f"\n[yellow]Run without --check to format {len(formatted_files)} files[/yellow]")
    elif not check and formatted_files:
        console.print(f"\n[green]✅ Formatted {len(formatted_files)} files successfully![/green]")
    elif not formatted_files and not error_files:
        console.print(f"\n[green]✅ All files are already properly formatted![/green]")


@yaml.command("schema")
@click.option(
    "--type", "-t",
    type=click.Choice(["profile", "hook", "all"]),
    default="all",
    help="Show schema for specific configuration type"
)
@click.pass_context
def yaml_schema(ctx: click.Context, type: str) -> None:
    """Show YAML configuration schemas and examples."""
    
    if type in ["profile", "all"]:
        console.print("[bold blue]Profile YAML Schema:[/bold blue]")
        profile_schema = """
# Profile Configuration Schema
name: string                    # Required: Profile name
description: string             # Optional: Profile description  
version: string                 # Recommended: Configuration version (default: "1.0")

contexts:                       # Optional: List of context file paths
  - "contexts/development.md"
  - "contexts/shared/*.md"
  - "contexts/aws-*.md"

hooks:                          # Optional: Hook configurations by trigger
  on_session_start:
    - name: "setup-env"
      enabled: true
      timeout: 30
      config:
        custom_param: "value"
  
  per_user_message:
    - name: "context-enhancer"
      enabled: true

mcp_servers:                    # Optional: List of MCP server names
  - "development"
  - "core"

settings:                       # Optional: Profile settings
  auto_backup: true
  validation_level: "normal"    # strict, normal, permissive
  hot_reload: true
  cache_enabled: true
  max_context_size: 100000

metadata:                       # Optional: Additional metadata
  created_date: "2024-01-01"
  author: "team"
  tags: ["development", "aws"]
"""
        console.print(Panel(profile_schema.strip(), border_style="blue"))
    
    if type in ["hook", "all"]:
        if type == "all":
            console.print()
        
        console.print("[bold blue]Hook YAML Schema:[/bold blue]")
        hook_schema = """
# Hook Configuration Schema
name: string                    # Required: Hook name
description: string             # Optional: Hook description
version: string                 # Recommended: Configuration version (default: "1.0")
type: string                    # Required: "context", "script", or "hybrid"
trigger: string                 # Required: Hook trigger event
timeout: integer                # Optional: Execution timeout in seconds (default: 30)
enabled: boolean                # Optional: Whether hook is enabled (default: true)

# For context-type hooks
context:
  sources:                      # List of context source files
    - "contexts/setup.md"
    - "contexts/troubleshooting.md"
  tags: ["setup", "dev"]        # Optional: Context tags
  categories: ["development"]   # Optional: Context categories
  priority: 0                   # Optional: Loading priority
  cache_ttl: 3600              # Optional: Cache TTL in seconds

# For script-type hooks  
script:
  command: "python"             # Command to execute
  args: ["scripts/setup.py"]    # Command arguments
  env:                          # Environment variables
    DEV_MODE: "true"
    DEBUG: "1"
  working_dir: "scripts"        # Optional: Working directory
  timeout: 60                   # Optional: Script timeout

# Execution conditions
conditions:
  - profile: ["developer", "qa"] # Execute only for these profiles
    platform: ["darwin", "linux"] # Execute only on these platforms
    environment:                # Required environment variables
      CI: "true"

metadata:                       # Optional: Additional metadata
  created_date: "2024-01-01"
  author: "team"
  documentation: "docs/hooks.md"

# Valid trigger values:
# - on_session_start: Execute when session starts
# - per_user_message: Execute for each user message  
# - on_file_change: Execute when files change
# - on_profile_switch: Execute when switching profiles

# Valid type values:
# - context: Load context files only
# - script: Execute script only  
# - hybrid: Both load context and execute script
"""
        console.print(Panel(hook_schema.strip(), border_style="green"))
    
    console.print(f"\n[bold blue]Usage Examples:[/bold blue]")
    console.print("• Create profile: [cyan]ai-config profile create my-profile --format yaml[/cyan]")
    console.print("• Validate YAML: [cyan]ai-config yaml validate[/cyan]")
    console.print("• Format files: [cyan]ai-config yaml format[/cyan]")
    console.print("• Convert profile: [cyan]ai-config profile convert my-profile --to-format yaml[/cyan]")


cli.add_command(yaml)


@cli.command("formats")
@click.pass_context
def formats(ctx: click.Context) -> None:
    """Show information about configuration formats and migration options."""
    config_manager = ctx.obj["config_manager"]
    
    console.print("[bold blue]AI Configurator Configuration Formats[/bold blue]\n")
    
    # Format comparison table
    table = Table(title="Format Comparison")
    table.add_column("Feature", style="cyan")
    table.add_column("YAML", style="green")
    table.add_column("JSON", style="yellow")
    
    table.add_row("Human Readable", "✅ Excellent", "⚠️ Good")
    table.add_row("Comments Support", "✅ Yes", "❌ No")
    table.add_row("Frontmatter Support", "✅ Yes", "❌ No")
    table.add_row("Schema Validation", "✅ Enhanced", "✅ Basic")
    table.add_row("Hot Reload", "✅ Yes", "✅ Yes")
    table.add_row("IDE Support", "✅ Excellent", "✅ Good")
    table.add_row("Backward Compatibility", "✅ Full", "✅ Native")
    table.add_row("Migration Tools", "✅ Available", "✅ Available")
    
    console.print(table)
    
    # Current configuration status
    profiles_dir = config_manager.config_dir / "profiles"
    hooks_dir = config_manager.config_dir / "hooks"
    
    yaml_profiles = 0
    json_profiles = 0
    yaml_hooks = 0
    
    if profiles_dir.exists():
        yaml_profiles = len(list(profiles_dir.glob("*.yaml")))
        json_profiles = len([d for d in profiles_dir.iterdir() if d.is_dir() and (d / "context.json").exists()])
    
    if hooks_dir.exists():
        yaml_hooks = len(list(hooks_dir.glob("*.yaml")))
    
    console.print(f"\n[bold blue]Current Configuration:[/bold blue]")
    console.print(f"• YAML Profiles: {yaml_profiles}")
    console.print(f"• JSON Profiles: {json_profiles}")
    console.print(f"• YAML Hooks: {yaml_hooks}")
    
    # Migration recommendations
    console.print(f"\n[bold blue]Recommendations:[/bold blue]")
    
    if json_profiles > 0 and yaml_profiles == 0:
        console.print("🔄 Consider migrating to YAML format for better maintainability:")
        console.print("   [cyan]ai-config migrate run --all[/cyan]")
    elif json_profiles > 0 and yaml_profiles > 0:
        console.print("⚠️ Mixed format detected. Consider standardizing:")
        console.print("   [cyan]ai-config migrate run --all[/cyan] (to migrate remaining JSON)")
        console.print("   [cyan]ai-config profile convert <name> --to-format yaml[/cyan] (individual profiles)")
    elif yaml_profiles > 0:
        console.print("✅ Using modern YAML format - great choice!")
        if yaml_hooks == 0:
            console.print("💡 Consider creating YAML hooks for better organization:")
            console.print("   [cyan]ai-config hooks create my-hook --type python[/cyan]")
    else:
        console.print("🚀 No configurations found. Start with YAML format:")
        console.print("   [cyan]ai-config profile create my-profile --format yaml[/cyan]")
    
    # Available commands
    console.print(f"\n[bold blue]Useful Commands:[/bold blue]")
    console.print("• List profiles: [cyan]ai-config profile list --format table[/cyan]")
    console.print("• Validate YAML: [cyan]ai-config yaml validate[/cyan]")
    console.print("• Format YAML: [cyan]ai-config yaml format[/cyan]")
    console.print("• Show schemas: [cyan]ai-config yaml schema[/cyan]")
    console.print("• Migration preview: [cyan]ai-config migrate preview[/cyan]")
    console.print("• Convert profile: [cyan]ai-config profile convert <name> --to-format yaml[/cyan]")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
