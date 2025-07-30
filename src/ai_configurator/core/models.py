"""Configuration data models using Pydantic."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    command: str = Field(..., description="Command to run the MCP server")
    args: List[str] = Field(default_factory=list, description="Command line arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    disabled: bool = Field(default=False, description="Whether the server is disabled")
    auto_approve: List[str] = Field(default_factory=list, alias="autoApprove", description="Auto-approved tools")


class MCPConfiguration(BaseModel):
    """Complete MCP server configuration."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    mcp_servers: Dict[str, MCPServerConfig] = Field(alias="mcpServers")


class ProfileContext(BaseModel):
    """Profile context configuration."""
    
    paths: List[str] = Field(default_factory=list, description="Context file paths")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific hooks")


class GlobalContext(BaseModel):
    """Global context configuration."""
    
    paths: List[str] = Field(default_factory=list, description="Global context paths")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Hook configurations")


class ProfileConfig(BaseModel):
    """Configuration for a specific profile."""
    
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    context: ProfileContext = Field(default_factory=ProfileContext)
    mcp_servers: Optional[List[str]] = Field(None, description="Enabled MCP servers for this profile")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific hooks")


class BackupMetadata(BaseModel):
    """Metadata for configuration backups."""
    
    backup_id: str = Field(..., description="Unique backup identifier")
    timestamp: str = Field(..., description="ISO timestamp of backup creation")
    description: Optional[str] = Field(None, description="Backup description")
    profile: Optional[str] = Field(None, description="Active profile at backup time")
    version: str = Field(..., description="AI Configurator version")
    platform: str = Field(..., description="Platform where backup was created")


class InstallationConfig(BaseModel):
    """Configuration for installation process."""
    
    profile: Optional[str] = Field(None, description="Profile to install")
    mcp_servers: Optional[List[str]] = Field(None, description="MCP server groups to install")
    preserve_existing: bool = Field(default=True, description="Preserve existing configurations")
    backup_before_install: bool = Field(default=True, description="Create backup before installation")
    force: bool = Field(default=False, description="Force installation even if config exists")


class ValidationResult(BaseModel):
    """Result of configuration validation."""
    
    is_valid: bool = Field(..., description="Whether the configuration is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    checked_items: Dict[str, bool] = Field(default_factory=dict, description="Items that were checked")


class ConfigurationState(BaseModel):
    """Current state of the Amazon Q CLI configuration."""
    
    amazonq_installed: bool = Field(..., description="Whether Amazon Q CLI is installed")
    amazonq_version: Optional[str] = Field(None, description="Amazon Q CLI version")
    config_dir_exists: bool = Field(..., description="Whether config directory exists")
    config_dir_path: str = Field(..., description="Path to config directory")
    active_profile: Optional[str] = Field(None, description="Currently active profile")
    installed_mcp_servers: List[str] = Field(default_factory=list, description="Installed MCP servers")
    last_backup: Optional[str] = Field(None, description="Last backup timestamp")
    ai_configurator_version: str = Field(..., description="AI Configurator version")
    platform: str = Field(..., description="Current platform")


# Type aliases for convenience
ConfigDict = Dict[str, Any]
PathLike = Union[str, Path]
