#!/usr/bin/env python3
"""
Export AI Configurator agent to Q CLI format.
"""

import json
import sys
from pathlib import Path
from ai_configurator.services import AgentService
from ai_configurator.models import ToolType

def export_agent_to_qcli(agent_name: str):
    """Export agent to Q CLI agents directory."""
    
    # Load agent
    config_dir = Path.home() / ".config" / "ai-configurator"
    agent_service = AgentService(config_dir / "agents")
    
    agent = agent_service.load_agent(agent_name, ToolType.Q_CLI)
    if not agent:
        print(f"Agent '{agent_name}' not found")
        return False
    
    # Export to Q CLI format
    q_cli_config = agent_service.export_for_tool(agent)
    
    # Fix resource paths to be absolute
    base_library = config_dir / "library"
    personal_library = config_dir / "personal"
    
    fixed_resources = []
    for resource_uri in q_cli_config.get("resources", []):
        # Remove file:// prefix
        resource_path = resource_uri.replace("file://", "")
        
        # Check if file exists in personal library first, then base
        personal_file = personal_library / resource_path
        base_file = base_library / resource_path
        
        if personal_file.exists():
            fixed_resources.append(f"file://{personal_file}")
        elif base_file.exists():
            fixed_resources.append(f"file://{base_file}")
        else:
            print(f"Warning: Resource not found: {resource_path}")
            fixed_resources.append(resource_uri)  # Keep original
    
    q_cli_config["resources"] = fixed_resources
    
    # Save to Q CLI agents directory
    q_cli_agents_dir = Path.home() / ".aws" / "amazonq" / "agents"
    q_cli_agents_dir.mkdir(parents=True, exist_ok=True)
    
    agent_file = q_cli_agents_dir / f"{agent_name}.json"
    
    try:
        with open(agent_file, 'w') as f:
            json.dump(q_cli_config, f, indent=2)
        
        print(f"✅ Agent exported to Q CLI: {agent_file}")
        print(f"📄 Resources: {len(fixed_resources)}")
        for resource in fixed_resources:
            print(f"   • {resource}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to export agent: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python export_to_qcli.py <agent_name>")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    success = export_agent_to_qcli(agent_name)
    sys.exit(0 if success else 1)
