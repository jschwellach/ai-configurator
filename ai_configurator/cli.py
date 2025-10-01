"""
AI Configurator CLI - Tool-agnostic knowledge library manager.
"""

import argparse
import json
import sys
from typing import List, Optional

from ai_configurator.core.library_manager import LibraryManager
from ai_configurator.core.agent_manager import AgentManager


def format_output(data, format_type: str = "table"):
    """Format output based on requested format."""
    if format_type == "json":
        return json.dumps(data, indent=2)
    return data


def cmd_library_list(args):
    """List all knowledge files in the library."""
    library = LibraryManager()
    categories = library.list_categories()
    
    if args.format == "json":
        print(json.dumps(categories, indent=2))
        return
    
    print("Knowledge Library Contents:")
    print("=" * 50)
    
    total_files = 0
    for category, files in categories.items():
        print(f"\n📁 {category.upper()}")
        print("-" * 30)
        for file_path in files:
            print(f"  📄 {file_path}")
        total_files += len(files)
    
    print(f"\nTotal: {total_files} knowledge files across {len(categories)} categories")


def cmd_library_sync(args):
    """Sync library from source to config directory."""
    library = LibraryManager()
    if library.sync_library():
        print("✅ Library synced successfully")
    else:
        print("❌ Failed to sync library")
        sys.exit(1)


def cmd_library_info(args):
    """Show library information."""
    library = LibraryManager()
    info = library.get_library_info()
    
    if args.format == "json":
        print(json.dumps(info, indent=2))
        return
    
    print("Library Information:")
    print("=" * 40)
    print(f"Source Path: {info.get('source_path', 'N/A')}")
    print(f"Library Path: {info.get('library_path', 'N/A')}")
    print(f"Total Files: {info.get('total_files', 0)}")
    print(f"Categories: {len(info.get('categories', {}))}")
    print(f"Roles: {len(info.get('roles', []))}")
    print(f"Synced: {'✅' if info.get('synced') else '❌'}")


def cmd_library_search(args):
    """Search library content."""
    library = LibraryManager()
    matches = library.search_files(args.query)
    
    if args.format == "json":
        print(json.dumps(matches, indent=2))
        return
    
    print(f"Search results for '{args.query}':")
    print("=" * 40)
    
    if not matches:
        print("No matches found")
        return
    
    for match in matches:
        print(f"  📄 {match}")
    
    print(f"\nFound {len(matches)} matches")


def cmd_create_agent(args):
    """Create a new agent."""
    agent_manager = AgentManager(args.tool)
    
    # Parse rules
    rules = []
    if args.rules:
        rules = [rule.strip() for rule in args.rules.split(',')]
    
    # Add common files if requested
    if args.include_common:
        library = LibraryManager()
        common_files = library.get_common_files()
        rules.extend(common_files)
    
    # Add role files if role specified
    if args.role:
        library = LibraryManager()
        role_files = library.get_role_files(args.role)
        if role_files:
            rules.extend(role_files)
        else:
            print(f"❌ Role '{args.role}' not found")
            sys.exit(1)
    
    if not rules:
        print("❌ No rules specified. Use --rules, --role, or --include-common")
        sys.exit(1)
    
    description = args.description or f"{args.name} agent created with AI Configurator"
    
    if agent_manager.create_agent(args.name, rules, description):
        print(f"✅ Agent '{args.name}' created successfully")
        if args.tool == "q-cli":
            print(f"Use: q chat --agent {args.name}")
    else:
        print(f"❌ Failed to create agent '{args.name}'")
        sys.exit(1)


def cmd_update_all(args):
    """Sync library and update all agents."""
    # First sync the library
    library = LibraryManager()
    if not library.sync_library():
        print("❌ Failed to sync library")
        sys.exit(1)
    print("✅ Library synced successfully")
    
    # Then update all agents
    agent_manager = AgentManager(args.tool)
    if agent_manager.update_all_agents():
        print("✅ All agents updated successfully")
    else:
        print("❌ Failed to update some agents")
        sys.exit(1)


def cmd_update_agent(args):
    """Update an existing agent or all agents."""
    agent_manager = AgentManager(args.tool)
    
    if args.all:
        if agent_manager.update_all_agents():
            print("✅ All agents updated successfully")
        else:
            print("❌ Failed to update some agents")
            sys.exit(1)
    else:
        if agent_manager.update_agent(args.name):
            print(f"✅ Agent '{args.name}' updated successfully")
        else:
            print(f"❌ Failed to update agent '{args.name}'")
            sys.exit(1)


def cmd_agents_list(args):
    """List all agents for a tool."""
    agent_manager = AgentManager(args.tool)
    agents = agent_manager.list_agents()
    
    if args.format == "json":
        agent_data = []
        for agent_name in agents:
            info = agent_manager.get_agent_info(agent_name)
            if info:
                agent_data.append({
                    "name": agent_name,
                    "description": info.get("description", ""),
                    "resources": len(info.get("resources", [])),
                    "mcp_servers": len(info.get("mcpServers", {}))
                })
        print(json.dumps(agent_data, indent=2))
        return
    
    if not agents:
        print(f"No agents found for {args.tool}")
        return
    
    print(f"{args.tool.upper()} Agents:")
    print("=" * 40)
    
    for agent_name in agents:
        info = agent_manager.get_agent_info(agent_name)
        if info:
            description = info.get("description", "No description")
            resource_count = len(info.get("resources", []))
            mcp_count = len(info.get("mcpServers", {}))
            
            print(f"\n🤖 {agent_name}")
            print(f"   Description: {description}")
            print(f"   Knowledge files: {resource_count}")
            print(f"   MCP servers: {mcp_count}")
            
            if args.tool == "q-cli":
                print(f"   Usage: q chat --agent {agent_name}")
    
    print(f"\nTotal: {len(agents)} agents")


def cmd_agents_remove(args):
    """Remove an agent."""
    agent_manager = AgentManager(args.tool)
    
    if agent_manager.remove_agent(args.name):
        print(f"✅ Agent '{args.name}' removed successfully")
    else:
        print(f"❌ Failed to remove agent '{args.name}'")
        sys.exit(1)


def cmd_agents_info(args):
    """Show agent information."""
    agent_manager = AgentManager(args.tool)
    info = agent_manager.get_agent_info(args.name)
    
    if not info:
        print(f"❌ Agent '{args.name}' not found")
        sys.exit(1)
    
    if args.format == "json":
        print(json.dumps(info, indent=2))
        return
    
    print(f"Agent: {args.name}")
    print("=" * 40)
    print(f"Description: {info.get('description', 'No description')}")
    print(f"Tools: {', '.join(info.get('tools', []))}")
    print(f"Allowed Tools: {', '.join(info.get('allowedTools', []))}")
    
    resources = info.get("resources", [])
    print(f"\nKnowledge Files ({len(resources)}):")
    for resource in resources:
        filename = resource.replace("file://", "").split("/")[-1]
        print(f"  📄 {filename}")
    
    mcp_servers = info.get("mcpServers", {})
    print(f"\nMCP Servers ({len(mcp_servers)}):")
    for name, config in mcp_servers.items():
        command = config.get("command", "N/A")
        print(f"  🔧 {name}: {command}")


def cmd_roles_list(args):
    """List all available roles."""
    library = LibraryManager()
    roles = library.list_roles()
    
    if args.format == "json":
        role_data = []
        for role in roles:
            role_info = library.get_role_info(role)
            role_data.append(role_info)
        print(json.dumps(role_data, indent=2))
        return
    
    if not roles:
        print("No roles found")
        return
    
    print("Available Roles:")
    print("=" * 30)
    
    for role in roles:
        role_info = library.get_role_info(role)
        print(f"\n👤 {role}")
        print(f"   Files: {role_info['file_count']}")
        
        if role_info['has_mcp_config']:
            print(f"   🔧 MCP: {role_info['mcp_server_count']} servers, {role_info['tools_settings_count']} tool settings")
        else:
            print(f"   🔧 MCP: No configuration")
        
        for file_path in role_info['files']:
            filename = file_path.split("/")[-1]
            if filename.endswith('.json'):
                print(f"     ⚙️  {filename}")
            else:
                print(f"     📄 {filename}")
    
    print(f"\nTotal: {len(roles)} roles")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Configurator - Tool-agnostic knowledge library manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Library management
  ai-config library list
  ai-config library sync
  ai-config library search "aws security"
  
  # Agent creation
  ai-config create-agent --name my-dev --role software-engineer --tool q-cli
  ai-config create-agent --name architect --rules "roles/software-architect/,domains/aws-best-practices.md" --tool q-cli
  
  # Agent management
  ai-config agents list --tool q-cli
  ai-config update-agent --name my-dev --tool q-cli
  ai-config update-agent --all --tool q-cli
  ai-config update-all --tool q-cli
  ai-config agents remove --name my-dev --tool q-cli
        """
    )
    
    parser.add_argument("--format", choices=["table", "json"], default="table",
                       help="Output format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Library commands
    library_parser = subparsers.add_parser("library", help="Library management")
    library_subparsers = library_parser.add_subparsers(dest="library_command")
    
    library_subparsers.add_parser("list", help="List all knowledge files")
    library_subparsers.add_parser("sync", help="Sync library from source")
    library_subparsers.add_parser("info", help="Show library information")
    
    search_parser = library_subparsers.add_parser("search", help="Search library content")
    search_parser.add_argument("query", help="Search query")
    
    # Agent creation
    create_parser = subparsers.add_parser("create-agent", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--rules", help="Comma-separated list of rule files")
    create_parser.add_argument("--role", help="Role to include (adds all role files)")
    create_parser.add_argument("--include-common", action="store_true", 
                              help="Include common organizational files")
    create_parser.add_argument("--description", help="Agent description")
    create_parser.add_argument("--tool", default="q-cli", 
                              choices=["q-cli", "claude-code", "chatgpt"],
                              help="Target tool")
    
    # Agent management
    update_parser = subparsers.add_parser("update-agent", help="Update an existing agent")
    update_parser.add_argument("--name", help="Agent name (required unless --all is used)")
    update_parser.add_argument("--all", action="store_true", help="Update all agents")
    update_parser.add_argument("--tool", default="q-cli", 
                              choices=["q-cli", "claude-code", "chatgpt"],
                              help="Target tool")
    
    # Update all (convenience command)
    update_all_parser = subparsers.add_parser("update-all", help="Sync library and update all agents")
    update_all_parser.add_argument("--tool", default="q-cli",
                                  choices=["q-cli", "claude-code", "chatgpt"],
                                  help="Target tool")
    
    # Agents commands
    agents_parser = subparsers.add_parser("agents", help="Agent management")
    agents_subparsers = agents_parser.add_subparsers(dest="agents_command")
    
    agents_list_parser = agents_subparsers.add_parser("list", help="List all agents")
    agents_list_parser.add_argument("--tool", default="q-cli",
                                   choices=["q-cli", "claude-code", "chatgpt"],
                                   help="Target tool")
    
    agents_remove_parser = agents_subparsers.add_parser("remove", help="Remove an agent")
    agents_remove_parser.add_argument("--name", required=True, help="Agent name")
    agents_remove_parser.add_argument("--tool", default="q-cli",
                                     choices=["q-cli", "claude-code", "chatgpt"],
                                     help="Target tool")
    
    agents_info_parser = agents_subparsers.add_parser("info", help="Show agent information")
    agents_info_parser.add_argument("--name", required=True, help="Agent name")
    agents_info_parser.add_argument("--tool", default="q-cli",
                                   choices=["q-cli", "claude-code", "chatgpt"],
                                   help="Target tool")
    
    # Roles commands
    roles_parser = subparsers.add_parser("roles", help="Role management")
    roles_subparsers = roles_parser.add_subparsers(dest="roles_command")
    roles_subparsers.add_parser("list", help="List all available roles")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Library commands
        if args.command == "library":
            if args.library_command == "list":
                cmd_library_list(args)
            elif args.library_command == "sync":
                cmd_library_sync(args)
            elif args.library_command == "info":
                cmd_library_info(args)
            elif args.library_command == "search":
                cmd_library_search(args)
            else:
                library_parser.print_help()
        
        # Agent creation
        elif args.command == "create-agent":
            cmd_create_agent(args)
        elif args.command == "update-agent":
            if not args.all and not args.name:
                print("❌ Either --name or --all must be specified")
                sys.exit(1)
            cmd_update_agent(args)
        elif args.command == "update-all":
            cmd_update_all(args)
        
        # Agents commands
        elif args.command == "agents":
            if args.agents_command == "list":
                cmd_agents_list(args)
            elif args.agents_command == "remove":
                cmd_agents_remove(args)
            elif args.agents_command == "info":
                cmd_agents_info(args)
            else:
                agents_parser.print_help()
        
        # Roles commands
        elif args.command == "roles":
            if args.roles_command == "list":
                cmd_roles_list(args)
            else:
                roles_parser.print_help()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
