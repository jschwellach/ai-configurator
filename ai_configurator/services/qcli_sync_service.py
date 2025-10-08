"""Service for synchronizing Q CLI agents with AI Agent Manager."""
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ..models.agent import AgentConfig


class QCLISyncService:
    """Service for importing Q CLI agents."""
    
    def __init__(self, qcli_agents_dir: Path, local_agents_dir: Path, registry_dir: Path, library_dir: Path):
        """Initialize sync service.
        
        Args:
            qcli_agents_dir: Q CLI agents directory (~/.aws/amazonq/cli-agents/)
            local_agents_dir: Local agents directory (~/.config/ai-configurator/agents/)
            registry_dir: MCP registry directory (~/.config/ai-configurator/registry/)
            library_dir: Library directory (~/.config/ai-configurator/library/)
        """
        self.qcli_dir = qcli_agents_dir
        self.local_dir = local_agents_dir
        self.registry_dir = registry_dir
        self.library_dir = library_dir
        
        # Ensure directories exist
        self.qcli_dir.mkdir(parents=True, exist_ok=True)
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.library_dir.mkdir(parents=True, exist_ok=True)
    
    def list_qcli_agents(self) -> List[str]:
        """List all Q CLI agent names.
        
        Returns:
            List of agent names (without .json extension)
        """
        agents = []
        for agent_file in self.qcli_dir.glob("*.json"):
            agents.append(agent_file.stem)
        return sorted(agents)
    
    def list_importable_agents(self) -> List[str]:
        """List Q CLI agents that don't exist locally yet.
        
        Returns:
            List of agent names that can be imported
        """
        qcli_agents = set(self.list_qcli_agents())
        local_agents = set(agent_file.stem for agent_file in self.local_dir.glob("*.json"))
        return sorted(qcli_agents - local_agents)
    
    def list_conflicting_agents(self) -> List[str]:
        """List agents that exist in both locations.
        
        Returns:
            List of agent names that exist in both Q CLI and local
        """
        qcli_agents = set(self.list_qcli_agents())
        local_agents = set(agent_file.stem for agent_file in self.local_dir.glob("*.json"))
        return sorted(qcli_agents & local_agents)
    
    def load_qcli_agent(self, agent_name: str) -> Optional[Dict]:
        """Load Q CLI agent JSON.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent data dict or None if not found
        """
        agent_file = self.qcli_dir / f"{agent_name}.json"
        if not agent_file.exists():
            return None
        
        try:
            return json.loads(agent_file.read_text())
        except Exception as e:
            raise ValueError(f"Failed to load Q CLI agent {agent_name}: {e}")
    
    def convert_qcli_to_agent_config(
        self,
        qcli_data: Dict,
        resource_paths: List[str],
        mcp_server_names: List[str]
    ) -> AgentConfig:
        """Convert Q CLI agent format to AgentConfig.
        
        Args:
            qcli_data: Q CLI agent JSON data
            resource_paths: Resolved resource paths (relative to library)
            mcp_server_names: MCP server names (after extraction to registry)
            
        Returns:
            AgentConfig instance
        """
        return AgentConfig(
            name=qcli_data.get("name", "imported-agent"),
            description=qcli_data.get("description", ""),
            prompt=qcli_data.get("instruction", ""),
            tool_type="q-cli",
            resources=resource_paths,
            mcp_servers=mcp_server_names,
            settings={},
            created_at=datetime.now()
        )
    
    def extract_mcp_servers(self, qcli_data: Dict) -> List[str]:
        """Extract MCP servers from Q CLI agent and save to registry.
        
        Args:
            qcli_data: Q CLI agent JSON data
            
        Returns:
            List of server names (after saving to registry)
        """
        mcp_servers = qcli_data.get("mcpServers", {})
        if not mcp_servers:
            return []
        
        servers_dir = self.registry_dir / "servers"
        servers_dir.mkdir(parents=True, exist_ok=True)
        
        server_names = []
        for server_name, server_config in mcp_servers.items():
            # Find unique filename
            base_name = server_name
            counter = 1
            filename = f"{base_name}.json"
            
            while (servers_dir / filename).exists():
                counter += 1
                filename = f"{base_name}-{counter}.json"
            
            # Save server config
            server_data = {
                "name": server_name,
                **server_config
            }
            (servers_dir / filename).write_text(json.dumps(server_data, indent=2))
            
            # Use the base name (without number) for agent reference
            server_names.append(server_name)
        
        return server_names
    
    def resolve_resource_paths(
        self,
        qcli_data: Dict,
        copy_to_library_callback
    ) -> List[str]:
        """Resolve resource paths with user input.
        
        Args:
            qcli_data: Q CLI agent JSON data
            copy_to_library_callback: Function(path) -> bool that asks user whether to copy
            
        Returns:
            List of resolved resource paths (relative to library or absolute)
        """
        resources = qcli_data.get("resources", [])
        if not resources:
            return []
        
        resolved_paths = []
        for resource in resources:
            if isinstance(resource, dict):
                path = resource.get("path", "")
            else:
                path = str(resource)
            
            if not path:
                continue
            
            # Handle file:// URIs
            if path.startswith("file://"):
                path = path[7:]  # Remove file:// prefix
            
            resource_path = Path(path).expanduser()
            
            # Check if file exists
            if not resource_path.exists():
                # File doesn't exist, skip it
                continue
            
            # Check if path is already in library
            if self._is_in_library(resource_path):
                # Convert to relative path
                try:
                    rel_path = resource_path.relative_to(self.library_dir)
                    resolved_paths.append(str(rel_path))
                except ValueError:
                    # Not relative to library, keep absolute
                    resolved_paths.append(str(resource_path))
            else:
                # External file - ask user
                should_copy = copy_to_library_callback(resource_path)
                
                if should_copy:
                    # Copy to library/personal/imported/
                    dest_dir = self.library_dir / "personal" / "imported"
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest_file = dest_dir / resource_path.name
                    
                    # Handle duplicate filenames
                    counter = 1
                    while dest_file.exists():
                        dest_file = dest_dir / f"{resource_path.stem}-{counter}{resource_path.suffix}"
                        counter += 1
                    
                    shutil.copy2(resource_path, dest_file)
                    rel_path = dest_file.relative_to(self.library_dir)
                    resolved_paths.append(str(rel_path))
                else:
                    # Keep absolute path
                    resolved_paths.append(str(resource_path))
        
        return resolved_paths
    
    def _is_in_library(self, path: Path) -> bool:
        """Check if path is within library directory."""
        try:
            path.resolve().relative_to(self.library_dir.resolve())
            return True
        except ValueError:
            return False
    
    def smart_merge_agents(
        self,
        local_config: AgentConfig,
        qcli_data: Dict,
        qcli_resources: List[str],
        qcli_mcp_servers: List[str]
    ) -> Tuple[AgentConfig, List[str]]:
        """Smart merge local and Q CLI agent configurations.
        
        Combines resources and MCP servers from both versions.
        Prompts user for conflicts in description/prompt.
        
        Args:
            local_config: Existing local AgentConfig
            qcli_data: Q CLI agent JSON data
            qcli_resources: Resolved Q CLI resource paths
            qcli_mcp_servers: Q CLI MCP server names
            
        Returns:
            Tuple of (merged AgentConfig, list of merge messages)
        """
        merge_messages = []
        
        # Merge resources (union of both lists)
        merged_resources = list(set(local_config.resources + qcli_resources))
        if len(merged_resources) > len(local_config.resources):
            added = len(merged_resources) - len(local_config.resources)
            merge_messages.append(f"Added {added} resource(s) from Q CLI")
        
        # Merge MCP servers (union of both lists)
        merged_mcp_servers = list(set(local_config.mcp_servers + qcli_mcp_servers))
        if len(merged_mcp_servers) > len(local_config.mcp_servers):
            added = len(merged_mcp_servers) - len(local_config.mcp_servers)
            merge_messages.append(f"Added {added} MCP server(s) from Q CLI")
        
        # For description and prompt, keep local if different
        # (User can manually edit if they want Q CLI version)
        qcli_description = qcli_data.get("description", "")
        qcli_prompt = qcli_data.get("instruction", "")
        
        if local_config.description != qcli_description and qcli_description:
            merge_messages.append("Description differs - kept local version")
        
        if local_config.prompt != qcli_prompt and qcli_prompt:
            merge_messages.append("Prompt differs - kept local version")
        
        # Create merged config
        merged_config = AgentConfig(
            name=local_config.name,
            description=local_config.description,  # Keep local
            prompt=local_config.prompt,  # Keep local
            tool_type=local_config.tool_type,
            resources=merged_resources,
            mcp_servers=merged_mcp_servers,
            settings=local_config.settings,
            created_at=local_config.created_at
        )
        
        return merged_config, merge_messages
    
    def import_agent(
        self,
        agent_name: str,
        copy_to_library_callback
    ) -> Tuple[bool, str]:
        """Import a Q CLI agent.
        
        Args:
            agent_name: Name of the agent to import
            copy_to_library_callback: Function(path) -> bool for resource path resolution
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Load Q CLI agent
            qcli_data = self.load_qcli_agent(agent_name)
            if not qcli_data:
                return False, f"Agent {agent_name} not found in Q CLI"
            
            # Extract MCP servers
            mcp_server_names = self.extract_mcp_servers(qcli_data)
            
            # Resolve resource paths
            resource_paths = self.resolve_resource_paths(qcli_data, copy_to_library_callback)
            
            # Check if agent already exists locally (conflict)
            agent_file = self.local_dir / f"{agent_name}.json"
            if agent_file.exists():
                # Load existing local agent
                local_data = json.loads(agent_file.read_text())
                local_config = AgentConfig(**local_data)
                
                # Smart merge
                merged_config, merge_messages = self.smart_merge_agents(
                    local_config,
                    qcli_data,
                    resource_paths,
                    mcp_server_names
                )
                
                # Save merged config
                agent_file.write_text(json.dumps(merged_config.dict(), indent=2, default=str))
                
                message = f"Merged {agent_name}"
                if merge_messages:
                    message += ": " + ", ".join(merge_messages)
                return True, message
            else:
                # New agent - convert and save
                agent_config = self.convert_qcli_to_agent_config(
                    qcli_data,
                    resource_paths,
                    mcp_server_names
                )
                
                agent_file.write_text(json.dumps(agent_config.dict(), indent=2, default=str))
                return True, f"Successfully imported {agent_name}"
            
        except Exception as e:
            return False, f"Failed to import {agent_name}: {str(e)}"
