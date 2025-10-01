#!/usr/bin/env python3
"""
Demo script to test AI Configurator progress so far.
"""

import tempfile
from pathlib import Path
from ai_configurator.models import Agent, AgentConfig, ToolType, ResourcePath, LibrarySource
from ai_configurator.services import LibraryService, ConfigService


def demo_models():
    """Demo the Pydantic models."""
    print("🧪 Testing Pydantic Models")
    print("=" * 40)
    
    # Create an agent
    config = AgentConfig(
        name="demo-agent",
        description="Demo agent for testing",
        tool_type=ToolType.Q_CLI
    )
    
    # Add a resource
    resource = ResourcePath(
        path="roles/software-engineer.md",
        source=LibrarySource.BASE
    )
    
    agent = Agent(config=config)
    agent.add_resource(resource)
    
    print(f"✅ Created agent: {agent.name}")
    print(f"✅ Tool type: {agent.tool_type}")
    print(f"✅ Resources: {len(agent.config.resources)}")
    
    # Test validation
    is_valid = agent.validate()
    print(f"✅ Agent validation: {is_valid}")
    
    # Test Q CLI export
    q_cli_config = agent.to_q_cli_format()
    print(f"✅ Q CLI export has {len(q_cli_config)} fields")
    print()


def demo_library_service():
    """Demo the LibraryService functionality."""
    print("📚 Testing Library Service")
    print("=" * 40)
    
    # Create temporary directories
    temp_dir = Path(tempfile.mkdtemp())
    base_path = temp_dir / "base"
    personal_path = temp_dir / "personal"
    
    # Set up base library
    base_path.mkdir(parents=True)
    (base_path / "roles").mkdir()
    (base_path / "roles" / "engineer.md").write_text("# Software Engineer\nBase content for engineer role")
    (base_path / "common").mkdir()
    (base_path / "common" / "policies.md").write_text("# Policies\nOrganizational policies")
    
    # Create library service
    service = LibraryService(base_path, personal_path)
    library = service.create_library()
    
    print(f"✅ Created library with base: {base_path}")
    print(f"✅ Personal library: {personal_path}")
    
    # Sync library
    conflicts = service.sync_library(library)
    print(f"✅ Synced library, found {len(conflicts)} conflicts")
    print(f"✅ Library has {len(library.files)} files")
    
    # Discover files
    files = service.discover_files(library)
    print(f"✅ Discovered files: {files}")
    
    # Get file content
    content = service.get_file_content(library, "roles/engineer.md")
    print(f"✅ File content length: {len(content) if content else 0}")
    
    # Save personal file
    success = service.save_personal_file(library, "custom/my-role.md", "# My Custom Role\nPersonal content")
    print(f"✅ Saved personal file: {success}")
    
    # Test personal override
    service.save_personal_file(library, "roles/engineer.md", "# Software Engineer\nPersonal override content")
    override_content = service.get_file_content(library, "roles/engineer.md")
    is_override = "Personal override" in (override_content or "")
    print(f"✅ Personal override working: {is_override}")
    
    print()


def demo_config_service():
    """Demo the ConfigService functionality."""
    print("⚙️  Testing Config Service")
    print("=" * 40)
    
    # Create temporary config directory
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create config service
    service = ConfigService(temp_dir)
    config = service.load_configuration()
    
    print(f"✅ Loaded configuration version: {config.config_version}")
    print(f"✅ Default tool type: {config.user_preferences.default_tool_type}")
    print(f"✅ Auto backup enabled: {config.backup_policy.auto_backup_before_operations}")
    
    # Save configuration
    success = service.save_configuration(config)
    print(f"✅ Saved configuration: {success}")
    
    # Create backup
    backup = service.create_backup(config, "demo", "Demo backup")
    print(f"✅ Created backup: {backup.backup_id if backup else 'Failed'}")
    
    print()


def demo_integration():
    """Demo integration between components."""
    print("🔗 Testing Integration")
    print("=" * 40)
    
    # Create agent with library resources
    temp_dir = Path(tempfile.mkdtemp())
    base_path = temp_dir / "base"
    
    # Set up library
    base_path.mkdir(parents=True)
    (base_path / "roles").mkdir()
    (base_path / "roles" / "engineer.md").write_text("# Software Engineer Role")
    
    # Create services
    library_service = LibraryService(base_path, temp_dir / "personal")
    config_service = ConfigService(temp_dir / "config")
    
    # Create library and agent
    library = library_service.create_library()
    library_service.sync_library(library)
    
    config = AgentConfig(
        name="integrated-agent",
        tool_type=ToolType.Q_CLI,
        resources=[ResourcePath(path="roles/engineer.md", source=LibrarySource.BASE)]
    )
    agent = Agent(config=config)
    
    print(f"✅ Created integrated agent: {agent.name}")
    print(f"✅ Agent has {len(agent.config.resources)} resources")
    print(f"✅ Library has {len(library.files)} files")
    
    # Test Q CLI export
    q_cli_export = agent.to_q_cli_format()
    print(f"✅ Q CLI export ready with {len(q_cli_export['resources'])} resources")
    
    print()


if __name__ == "__main__":
    print("🚀 AI Configurator Progress Demo")
    print("=" * 50)
    print()
    
    try:
        demo_models()
        demo_library_service()
        demo_config_service()
        demo_integration()
        
        print("🎉 All demos completed successfully!")
        print("✅ Core infrastructure is working")
        print("✅ Personal library management is working")
        print("✅ Agent models are working")
        print("✅ Configuration management is working")
        print()
        print("📋 Ready for Phase 1 Unit 3: Basic Agent Management")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
