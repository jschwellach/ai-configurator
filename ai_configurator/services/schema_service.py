"""
Schema management service for different AI tool formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.agent import Agent
from ..models.export_targets import AIToolType


class SchemaAdapter(ABC):
    """Abstract base class for schema adapters."""
    
    @abstractmethod
    def adapt_schema(self, agent: Agent) -> Dict[str, Any]:
        """Adapt agent schema for target AI tool."""
        pass
    
    @abstractmethod
    def validate_schema(self, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate schema for target AI tool."""
        pass


class KiroCliSchemaAdapter(SchemaAdapter):
    """Schema adapter for Kiro CLI format."""
    
    def adapt_schema(self, agent: Agent) -> Dict[str, Any]:
        """Adapt agent schema for Kiro CLI."""
        # Kiro CLI uses the same format as Q CLI
        return agent.to_q_cli_format()
    
    def validate_schema(self, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate schema for Kiro CLI."""
        required_fields = ["name", "resources", "tools", "allowedTools"]
        
        for field in required_fields:
            if field not in schema:
                return False, f"Missing required field: {field}"
        
        # Validate schema structure
        if not isinstance(schema.get("resources"), list):
            return False, "Resources must be a list"
        
        if not isinstance(schema.get("tools"), list):
            return False, "Tools must be a list"
        
        if not isinstance(schema.get("allowedTools"), list):
            return False, "AllowedTools must be a list"
        
        # Validate MCP servers if present
        if "mcpServers" in schema:
            if not isinstance(schema["mcpServers"], dict):
                return False, "MCP servers must be a dictionary"
            
            for server_name, server_config in schema["mcpServers"].items():
                if not isinstance(server_config, dict):
                    return False, f"MCP server config for '{server_name}' must be a dictionary"
                
                if "command" not in server_config:
                    return False, f"MCP server '{server_name}' missing required 'command' field"
        
        return True, None


class ClaudeCodeSchemaAdapter(SchemaAdapter):
    """Schema adapter for Claude Code format (future implementation)."""
    
    def adapt_schema(self, agent: Agent) -> Dict[str, Any]:
        """Adapt agent schema for Claude Code."""
        # Placeholder for future implementation
        return {
            "name": agent.config.name,
            "description": agent.config.description,
            "status": "not_implemented"
        }
    
    def validate_schema(self, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate schema for Claude Code."""
        return False, "Claude Code schema validation not yet implemented"


class SchemaService:
    """Service for managing schemas across different AI tools."""
    
    def __init__(self):
        self._adapters: Dict[AIToolType, SchemaAdapter] = {
            AIToolType.KIRO_CLI: KiroCliSchemaAdapter(),
            AIToolType.CLAUDE_CODE: ClaudeCodeSchemaAdapter(),
        }
    
    def adapt_agent_for_target(self, agent: Agent, target_type: AIToolType) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Adapt agent schema for target AI tool."""
        adapter = self._adapters.get(target_type)
        if not adapter:
            return None, f"No schema adapter available for {target_type.value}"
        
        try:
            adapted_schema = adapter.adapt_schema(agent)
            return adapted_schema, None
        except Exception as e:
            return None, f"Schema adaptation failed: {e}"
    
    def validate_schema_for_target(self, schema: Dict[str, Any], target_type: AIToolType) -> tuple[bool, Optional[str]]:
        """Validate schema for target AI tool."""
        adapter = self._adapters.get(target_type)
        if not adapter:
            return False, f"No schema adapter available for {target_type.value}"
        
        return adapter.validate_schema(schema)
    
    def get_base_agent_schema(self, agent: Agent) -> Dict[str, Any]:
        """Get base agent schema for internal use."""
        return {
            "name": agent.config.name,
            "description": agent.config.description,
            "prompt": agent.config.prompt,
            "tool_type": agent.config.tool_type.value,
            "resources": [r.dict() for r in agent.config.resources],
            "context_patterns": agent.config.context_patterns,
            "mcp_servers": {name: config.dict() for name, config in agent.config.mcp_servers.items()},
            "settings": agent.config.settings.dict(),
            "created_at": agent.config.created_at.isoformat(),
            "updated_at": agent.config.updated_at.isoformat()
        }
    
    def register_adapter(self, target_type: AIToolType, adapter: SchemaAdapter):
        """Register a new schema adapter."""
        self._adapters[target_type] = adapter
    
    def get_supported_targets(self) -> list[AIToolType]:
        """Get list of supported target types."""
        return list(self._adapters.keys())
