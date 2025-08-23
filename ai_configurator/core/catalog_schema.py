"""
Simplified catalog schema for AI Configurator library.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ConfigItem(BaseModel):
    """Simplified configuration item."""
    id: str
    name: str
    description: str
    version: str
    file_path: str


class GlobalContext(BaseModel):
    """Global context configuration item."""
    id: str
    name: str
    description: str
    version: str
    file_path: str
    priority: int = Field(default=0, description="Priority for context loading (higher = loaded first)")


class HookCommand(BaseModel):
    """Hook command configuration."""
    command: str


class McpServerConfig(BaseModel):
    """MCP Server configuration."""
    command: str
    args: List[str] = Field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    timeout: int = Field(default=120000)
    disabled: bool = Field(default=False)


class AgentConfig(BaseModel):
    """Q CLI Agent configuration format matching official schema."""
    schema_url: str = Field(
        default="https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json",
        alias="$schema"
    )
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    mcpServers: Dict[str, McpServerConfig] = Field(default_factory=dict)
    tools: List[str] = Field(default_factory=lambda: ["*"])
    toolAliases: Dict[str, str] = Field(default_factory=dict)
    allowedTools: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    hooks: Dict[str, List[HookCommand]] = Field(default_factory=dict)
    toolsSettings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    useLegacyMcpJson: bool = Field(default=False)

    class Config:
        populate_by_name = True


class LibraryCatalog(BaseModel):
    """Simplified library catalog structure."""
    version: str = "1.0.0"
    profiles: List[ConfigItem] = Field(default_factory=list)
    global_contexts: List[GlobalContext] = Field(default_factory=list)


# JSON Schema for validation
CATALOG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Configuration Library Catalog",
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "profiles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "version": {"type": "string"},
                    "file_path": {"type": "string"}
                },
                "required": ["id", "name", "description", "version", "file_path"]
            }
        },
        "global_contexts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "version": {"type": "string"},
                    "file_path": {"type": "string"},
                    "priority": {"type": "integer", "default": 0}
                },
                "required": ["id", "name", "description", "version", "file_path"]
            }
        }
    },
    "required": ["version", "profiles"]
}
