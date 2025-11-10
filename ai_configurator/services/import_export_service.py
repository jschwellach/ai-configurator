"""
Service for importing and exporting agent configurations.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models import Agent, AgentConfig, ResourcePath, ToolType, LibrarySource
from .agent_service import AgentService
from ..tui.config import get_library_paths


class ImportExportService:
    """Service for importing and exporting agent configurations."""
    
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service
        self.package_version = "1.0"
    
    def export_agent(self, agent_name: str, tool_type: ToolType, output_path: Path) -> bool:
        """
        Export an agent configuration and its referenced files to a package.
        
        Args:
            agent_name: Name of the agent to export
            tool_type: Tool type of the agent
            output_path: Path where the package should be created
            
        Returns:
            True if export was successful, False otherwise
        """
        # Load the agent
        agent = self.agent_service.load_agent(agent_name, tool_type)
        if not agent:
            return False
        
        # Create package directory structure
        package_dir = output_path / f"{agent_name}_package"
        library_dir = package_dir / "library"
        mcp_dir = package_dir / "mcp"
        
        # Clean up if package already exists
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        # Create directories
        package_dir.mkdir(parents=True, exist_ok=True)
        library_dir.mkdir(parents=True, exist_ok=True)
        mcp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy referenced library files
            library_manifest = self._copy_library_files(agent, library_dir)
            
            # Save agent configuration
            agent_file = package_dir / "agent.json"
            agent_data = agent.config.dict()
            agent_file.write_text(json.dumps(agent_data, indent=2, default=str))
            
            # Save MCP server configurations if any
            mcp_manifest = []
            if agent.config.mcp_servers:
                mcp_file = mcp_dir / "servers.json"
                mcp_data = {name: config.dict() for name, config in agent.config.mcp_servers.items()}
                mcp_file.write_text(json.dumps(mcp_data, indent=2))
                mcp_manifest = list(agent.config.mcp_servers.keys())
            
            # Create manifest
            manifest = {
                "version": self.package_version,
                "name": agent.name,
                "description": agent.config.description,
                "tool_type": agent.tool_type.value,
                "created": datetime.now().isoformat(),
                "library_files": library_manifest,
                "mcp_servers": mcp_manifest
            }
            
            manifest_file = package_dir / "manifest.json"
            manifest_file.write_text(json.dumps(manifest, indent=2))
            
            return True
        except Exception as e:
            # Clean up on failure
            if package_dir.exists():
                shutil.rmtree(package_dir)
            return False
    
    def import_agent(self, package_path: Path, new_agent_name: Optional[str] = None) -> Optional[Tuple[str, ToolType]]:
        """
        Import an agent configuration from a package.
        
        Args:
            package_path: Path to the package directory
            new_agent_name: Optional new name for the agent
            
        Returns:
            Tuple of (agent_name, tool_type) if successful, None otherwise
        """
        # Validate package
        if not self._validate_package(package_path):
            return None
        
        try:
            # Read manifest
            manifest_file = package_path / "manifest.json"
            manifest = json.loads(manifest_file.read_text())
            
            # Determine agent name
            agent_name = new_agent_name or manifest["name"]
            tool_type = ToolType(manifest["tool_type"])
            
            # Check if agent already exists
            if self.agent_service.agent_exists(agent_name, tool_type):
                # For now, we'll overwrite - in a real implementation, we'd ask the user
                pass
            
            # Install library files
            self._install_library_files(package_path, manifest)
            
            # Load agent configuration
            agent_file = package_path / "agent.json"
            agent_data = json.loads(agent_file.read_text())
            
            # Update agent name if needed
            if new_agent_name:
                agent_data["name"] = new_agent_name
            
            # Update resource paths to match local environment
            agent_data["resources"] = self._update_resource_paths(agent_data["resources"])
            
            # Load MCP server configurations if any
            mcp_dir = package_path / "mcp"
            mcp_file = mcp_dir / "servers.json"
            if mcp_file.exists():
                mcp_data = json.loads(mcp_file.read_text())
                agent_data["mcp_servers"] = mcp_data
            
            # Create and save agent
            config = AgentConfig(**agent_data)
            agent = Agent(config=config)
            
            if self.agent_service.update_agent(agent):
                return (agent_name, tool_type)
            else:
                return None
        except Exception:
            return None
    
    def _copy_library_files(self, agent: Agent, library_dir: Path) -> List[Dict]:
        """Copy referenced library files to the package."""
        manifest = []
        
        # Get library paths
        base_path, personal_path = get_library_paths()
        
        for resource in agent.config.resources:
            try:
                # Convert resource path to actual file path based on source
                if resource.source == LibrarySource.BASE:
                    # For base files, the path is relative to the base directory
                    # If the resource path starts with "base/", remove that prefix
                    if resource.path.startswith("base/"):
                        relative_path = resource.path[5:]  # Remove "base/" prefix
                        # Make sure it's not an absolute path
                        if relative_path.startswith('/'):
                            relative_path = relative_path[1:]
                        file_path = base_path / relative_path
                    else:
                        file_path = base_path / resource.path
                elif resource.source == LibrarySource.PERSONAL:
                    # For personal files, the path is relative to the personal directory
                    # If the resource path starts with "personal/", remove that prefix
                    if resource.path.startswith("personal/"):
                        relative_path = resource.path[8:]  # Remove "personal/" prefix
                        # Make sure it's not an absolute path
                        if relative_path.startswith('/'):
                            relative_path = relative_path[1:]
                        file_path = personal_path / relative_path
                    else:
                        file_path = personal_path / resource.path
                else:
                    # For local files, use the to_file_uri method
                    file_uri = resource.to_file_uri()
                    if file_uri.startswith("file://"):
                        file_path = Path(file_uri[7:])  # Remove "file://" prefix
                    else:
                        continue
                
                if file_path.exists():
                    # Determine relative path within library structure
                    relative_path = self._get_library_relative_path(file_path)
                    if relative_path:
                        # Create directory structure in package
                        dest_path = library_dir / relative_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(file_path, dest_path)
                        
                        # Add to manifest
                        manifest.append({
                            "source_path": str(file_path),
                            "package_path": str(relative_path),
                            "resource_path": resource.path,
                            "source": resource.source.value
                        })
            except Exception:
                # Skip files that can't be copied
                continue
        
        return manifest
    
    def _install_library_files(self, package_path: Path, manifest: Dict) -> None:
        """Install library files from package to local library."""
        library_files = manifest.get("library_files", [])
        if not library_files:
            return
        
        # Get local library paths
        base_path, personal_path = get_library_paths()
        
        for file_info in library_files:
            try:
                source_path = package_path / "library" / file_info["package_path"]
                
                # Determine destination based on source
                source_type = file_info.get("source", "personal")  # Default to personal
                if source_type == "base":
                    dest_path = base_path / file_info["resource_path"]
                else:
                    dest_path = personal_path / file_info["resource_path"]
                
                if source_path.exists():
                    # Create directory structure
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file (in a real implementation, we'd handle conflicts)
                    shutil.copy2(source_path, dest_path)
            except Exception:
                # Skip files that can't be installed
                continue
    
    def _update_resource_paths(self, resources: List[Dict]) -> List[Dict]:
        """Update resource paths to match local environment."""
        updated_resources = []
        
        for resource_data in resources:
            # For now, we'll assume the paths are correct
            # In a real implementation, we'd need to adjust paths for the local environment
            updated_resources.append(resource_data)
        
        return updated_resources
    
    def _get_library_relative_path(self, file_path: Path) -> Optional[Path]:
        """Get the relative path of a file within the library structure."""
        # Get library paths
        base_path, personal_path = get_library_paths()
        library_root = base_path.parent  # Get library root directory
        
        try:
            # Check if file is within library structure
            if file_path.is_relative_to(library_root):
                return file_path.relative_to(library_root)
        except ValueError:
            pass
        
        return None
    
    def _validate_package(self, package_path: Path) -> bool:
        """Validate that the package has the required files."""
        required_files = ["manifest.json", "agent.json"]
        for file_name in required_files:
            if not (package_path / file_name).exists():
                return False
        return True
