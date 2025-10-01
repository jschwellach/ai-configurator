"""
Unit tests for Agent domain model.
"""

import pytest
from datetime import datetime

from ai_configurator.models import (
    Agent, AgentConfig, AgentSettings, MCPServerConfig,
    ResourcePath, ToolType, LibrarySource, HealthStatus
)


class TestAgentModel:
    """Test cases for Agent domain model."""
    
    def test_create_basic_agent(self):
        """Test creating a basic agent with minimal configuration."""
        config = AgentConfig(
            name="test-agent",
            description="Test agent",
            tool_type=ToolType.Q_CLI
        )
        agent = Agent(config=config)
        
        assert agent.name == "test-agent"
        assert agent.tool_type == ToolType.Q_CLI
        assert agent.health_status == HealthStatus.UNKNOWN
        assert len(agent.validation_errors) == 0
    
    def test_add_resource_to_agent(self):
        """Test adding a knowledge resource to an agent."""
        config = AgentConfig(name="test-agent", tool_type=ToolType.Q_CLI)
        agent = Agent(config=config)
        
        resource = ResourcePath(
            path="roles/software-engineer.md",
            source=LibrarySource.BASE
        )
        
        initial_time = agent.config.updated_at
        agent.add_resource(resource)
        
        assert len(agent.config.resources) == 1
        assert agent.config.resources[0] == resource
        assert agent.config.updated_at > initial_time
    
    def test_configure_mcp_server(self):
        """Test adding MCP server configuration to an agent."""
        config = AgentConfig(name="test-agent", tool_type=ToolType.Q_CLI)
        agent = Agent(config=config)
        
        mcp_config = MCPServerConfig(
            command="python",
            args=["-m", "test_server"],
            timeout=60000
        )
        
        initial_time = agent.config.updated_at
        agent.configure_mcp_server("test-server", mcp_config)
        
        assert "test-server" in agent.config.mcp_servers
        assert agent.config.mcp_servers["test-server"] == mcp_config
        assert agent.config.updated_at > initial_time
    
    def test_agent_validation_success(self):
        """Test successful agent validation."""
        config = AgentConfig(
            name="valid-agent",
            tool_type=ToolType.Q_CLI,
            resources=[
                ResourcePath(path="test.md", source=LibrarySource.BASE)
            ]
        )
        config.mcp_servers["test"] = MCPServerConfig(command="python")
        
        agent = Agent(config=config)
        is_valid = agent.validate()
        
        assert is_valid is True
        assert agent.health_status == HealthStatus.HEALTHY
        assert len(agent.validation_errors) == 0
    
    def test_agent_validation_empty_name(self):
        """Test agent validation fails with empty name."""
        config = AgentConfig(name="", tool_type=ToolType.Q_CLI)
        agent = Agent(config=config)
        
        is_valid = agent.validate()
        
        assert is_valid is False
        assert agent.health_status == HealthStatus.ERROR
        assert "Agent name cannot be empty" in agent.validation_errors
    
    def test_agent_validation_empty_resource_path(self):
        """Test agent validation fails with empty resource path."""
        config = AgentConfig(
            name="test-agent",
            tool_type=ToolType.Q_CLI,
            resources=[ResourcePath(path="", source=LibrarySource.BASE)]
        )
        agent = Agent(config=config)
        
        is_valid = agent.validate()
        
        assert is_valid is False
        assert agent.health_status == HealthStatus.ERROR
        assert "Empty resource path found" in agent.validation_errors
    
    def test_agent_validation_empty_mcp_command(self):
        """Test agent validation fails with empty MCP server command."""
        config = AgentConfig(name="test-agent", tool_type=ToolType.Q_CLI)
        config.mcp_servers["test"] = MCPServerConfig(command="")
        
        agent = Agent(config=config)
        is_valid = agent.validate()
        
        assert is_valid is False
        assert agent.health_status == HealthStatus.ERROR
        assert "MCP server 'test' has empty command" in agent.validation_errors
    
    def test_to_q_cli_format(self):
        """Test exporting agent to Q CLI format."""
        config = AgentConfig(
            name="test-agent",
            description="Test agent for Q CLI",
            tool_type=ToolType.Q_CLI,
            resources=[
                ResourcePath(path="roles/engineer.md", source=LibrarySource.BASE)
            ]
        )
        config.mcp_servers["aws"] = MCPServerConfig(
            command="python",
            args=["-m", "aws_server"],
            timeout=120000
        )
        
        agent = Agent(config=config)
        q_cli_config = agent.to_q_cli_format()
        
        expected_schema = "https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json"
        
        assert q_cli_config["$schema"] == expected_schema
        assert q_cli_config["name"] == "test-agent"
        assert q_cli_config["description"] == "Test agent for Q CLI"
        assert q_cli_config["resources"] == ["file://roles/engineer.md"]
        assert q_cli_config["tools"] == ["*"]
        assert q_cli_config["allowedTools"] == []
        assert "aws" in q_cli_config["mcpServers"]
        assert q_cli_config["mcpServers"]["aws"]["command"] == "python"
    
    def test_resource_path_to_file_uri(self):
        """Test ResourcePath conversion to file URI."""
        resource = ResourcePath(
            path="roles/software-engineer.md",
            source=LibrarySource.PERSONAL
        )
        
        assert resource.to_file_uri() == "file://roles/software-engineer.md"
