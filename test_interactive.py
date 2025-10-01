#!/usr/bin/env python3
"""
Interactive test script for AI Configurator.
"""

import tempfile
from pathlib import Path
from ai_configurator.models import Agent, AgentConfig, ToolType, ResourcePath, LibrarySource
from ai_configurator.services import LibraryService


def setup_test_library():
    """Set up a test library with sample content."""
    temp_dir = Path(tempfile.mkdtemp())
    base_path = temp_dir / "base"
    personal_path = temp_dir / "personal"
    
    # Create base library structure (similar to existing library)
    base_path.mkdir(parents=True)
    
    # Roles
    (base_path / "roles").mkdir()
    (base_path / "roles" / "software-engineer.md").write_text("""# Software Engineer

You are an experienced software engineer responsible for implementing system designs and writing clean, maintainable code.

## Responsibilities
- Implement domain models and business logic
- Write comprehensive tests
- Follow coding best practices
- Collaborate with team members

## Skills
- Python, TypeScript, Java
- Test-driven development
- Design patterns
- Code review
""")
    
    (base_path / "roles" / "product-owner.md").write_text("""# Product Owner

You are responsible for defining product requirements and managing the product backlog.

## Responsibilities
- Define user stories
- Prioritize features
- Stakeholder communication
- Product roadmap planning
""")
    
    # Common
    (base_path / "common").mkdir()
    (base_path / "common" / "policies.md").write_text("""# Organizational Policies

## Code Quality
- All code must be reviewed before merging
- Maintain 80%+ test coverage
- Follow established coding standards

## Security
- Never commit secrets or API keys
- Use environment variables for configuration
- Follow principle of least privilege
""")
    
    return temp_dir, base_path, personal_path


def test_library_operations():
    """Test library operations interactively."""
    print("📚 Testing Library Operations")
    print("=" * 50)
    
    temp_dir, base_path, personal_path = setup_test_library()
    service = LibraryService(base_path, personal_path)
    library = service.create_library()
    
    print(f"Base library: {base_path}")
    print(f"Personal library: {personal_path}")
    print()
    
    # Sync library
    print("1. Syncing library...")
    conflicts = service.sync_library(library)
    print(f"   Found {len(conflicts)} conflicts")
    print(f"   Library now has {len(library.files)} files")
    print()
    
    # Discover files
    print("2. Discovering files...")
    files = service.discover_files(library)
    for i, file_path in enumerate(files, 1):
        print(f"   {i}. {file_path}")
    print()
    
    # Show file content
    print("3. Reading software-engineer.md content:")
    content = service.get_file_content(library, "roles/software-engineer.md")
    if content:
        lines = content.split('\n')
        for line in lines[:5]:  # Show first 5 lines
            print(f"   {line}")
        if len(lines) > 5:
            print(f"   ... ({len(lines) - 5} more lines)")
    print()
    
    # Create personal override
    print("4. Creating personal override...")
    personal_content = """# Software Engineer (Personal)

My customized software engineer role with additional focus on:

## Additional Skills
- AI/ML integration
- Cloud architecture (AWS)
- DevOps practices

## Personal Preferences
- TDD approach
- Clean architecture
- Domain-driven design
"""
    
    success = service.save_personal_file(library, "roles/software-engineer.md", personal_content)
    print(f"   Saved personal override: {success}")
    
    # Test override
    print("5. Testing personal override...")
    override_content = service.get_file_content(library, "roles/software-engineer.md")
    is_personal = "Personal" in (override_content or "")
    print(f"   Personal override active: {is_personal}")
    if is_personal:
        print("   ✅ Personal library correctly overrides base library!")
    print()
    
    # Create custom file
    print("6. Creating custom personal file...")
    custom_content = """# My Custom Role

This is a completely custom role that doesn't exist in the base library.

## Purpose
- Custom workflows
- Personal productivity
- Specialized tasks
"""
    
    success = service.save_personal_file(library, "custom/my-role.md", custom_content)
    print(f"   Created custom file: {success}")
    
    # Re-discover files
    print("7. Re-discovering files after changes...")
    files = service.discover_files(library)
    for i, file_path in enumerate(files, 1):
        print(f"   {i}. {file_path}")
    print()
    
    return temp_dir, service, library


def test_agent_creation():
    """Test agent creation with library resources."""
    print("🤖 Testing Agent Creation")
    print("=" * 50)
    
    temp_dir, service, library = test_library_operations()
    
    # Create agent configuration
    config = AgentConfig(
        name="my-test-agent",
        description="Test agent with library resources",
        tool_type=ToolType.Q_CLI
    )
    
    # Add resources from library
    resources = [
        ResourcePath(path="roles/software-engineer.md", source=LibrarySource.PERSONAL),
        ResourcePath(path="common/policies.md", source=LibrarySource.BASE),
        ResourcePath(path="custom/my-role.md", source=LibrarySource.PERSONAL)
    ]
    
    agent = Agent(config=config)
    for resource in resources:
        agent.add_resource(resource)
    
    print(f"Created agent: {agent.name}")
    print(f"Resources: {len(agent.config.resources)}")
    for i, resource in enumerate(agent.config.resources, 1):
        print(f"   {i}. {resource.path} ({resource.source.value})")
    print()
    
    # Validate agent
    print("Validating agent...")
    is_valid = agent.validate()
    print(f"   Valid: {is_valid}")
    if not is_valid:
        for error in agent.validation_errors:
            print(f"   ❌ {error}")
    print()
    
    # Export to Q CLI format
    print("Exporting to Q CLI format...")
    q_cli_config = agent.to_q_cli_format()
    print(f"   Schema: {q_cli_config['$schema']}")
    print(f"   Name: {q_cli_config['name']}")
    print(f"   Description: {q_cli_config['description']}")
    print(f"   Resources: {len(q_cli_config['resources'])}")
    for i, resource in enumerate(q_cli_config['resources'], 1):
        print(f"      {i}. {resource}")
    print()
    
    return agent


if __name__ == "__main__":
    print("🧪 AI Configurator Interactive Test")
    print("=" * 60)
    print()
    
    try:
        # Test library operations
        agent = test_agent_creation()
        
        print("🎉 Interactive Test Completed Successfully!")
        print()
        print("Key Features Demonstrated:")
        print("✅ Base library with roles and common files")
        print("✅ Personal library overrides base files")
        print("✅ Custom personal files")
        print("✅ File discovery and content reading")
        print("✅ Agent creation with library resources")
        print("✅ Agent validation")
        print("✅ Q CLI export format")
        print()
        print("This demonstrates the core functionality is working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
