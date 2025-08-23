# Contributing to AI Configurator

Thank you for your interest in contributing to AI Configurator! This guide will help you get started with contributing to our tool-agnostic knowledge library manager.

## 🎯 Project Overview

AI Configurator is a tool-agnostic knowledge library manager that creates and manages AI tool configurations. The system provides a pure knowledge library that can be consumed by any AI tool while maintaining tool-specific agent configurations separately.

## 🏗️ Architecture

### Core Components

- **LibraryManager**: Manages the tool-agnostic knowledge library
- **AgentManager**: Creates and manages tool-specific agents
- **CLI**: Interactive command-line interface with menu system

### Knowledge Library Structure

```
library/
├── common/      # Organizational knowledge (policies, standards)
├── roles/       # Role-specific knowledge folders
├── domains/     # Domain expertise (AWS, security, etc.)
├── tools/       # Tool-specific knowledge (Git, Docker, etc.)
└── workflows/   # Process documentation (code review, etc.)
```

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-configurator
   ```

2. **Set up development environment**:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. **Test the installation**:
   ```bash
   ai-config library list
   ai-config roles list
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_configurator

# Run specific test file
pytest tests/test_library_manager.py
```

## 📝 Types of Contributions

### 1. Knowledge Library Contributions

#### Adding New Roles
Create a new role folder in `library/roles/`:

```bash
mkdir library/roles/new-role
```

Create the main role file:
```markdown
# library/roles/new-role/new-role.md

# New Role

## Core Responsibilities
- Responsibility 1
- Responsibility 2

## Key Skills & Competencies
- Skill 1
- Skill 2

## Best Practices
- Practice 1
- Practice 2
```

#### Adding Domain Knowledge
Create domain expertise files in `library/domains/`:

```markdown
# library/domains/new-domain.md

# New Domain Best Practices

## Overview
Brief description of the domain.

## Key Concepts
- Concept 1
- Concept 2

## Best Practices
- Practice 1
- Practice 2
```

#### Adding Tool Knowledge
Create tool-specific knowledge in `library/tools/`:

```markdown
# library/tools/new-tool.md

# New Tool Best Practices

## Overview
Tool description and purpose.

## Configuration
- Setup instructions
- Configuration examples

## Best Practices
- Usage patterns
- Common pitfalls to avoid
```

### 2. Code Contributions

#### Core System Improvements
- **LibraryManager**: Enhance library management functionality
- **AgentManager**: Improve agent creation and management
- **CLI**: Add new commands or improve existing ones

#### Multi-Tool Support
Help implement support for additional AI tools:
- Claude Projects export
- ChatGPT custom instructions
- Other AI tool integrations

### 3. Documentation Improvements

- Update README.md for new features
- Improve inline code documentation
- Add usage examples
- Create tutorials and guides

## 🔧 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions focused and small

### Knowledge Content Guidelines

- Use clear, concise language
- Structure content with headers and bullet points
- Include practical examples where possible
- Focus on actionable advice
- Avoid tool-specific references in general knowledge

### Commit Messages

Use conventional commit format:
```
type(scope): description

Examples:
feat(library): add DevOps role knowledge
fix(agent): resolve file reference issue
docs(readme): update installation instructions
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing Your Changes

### Library Changes
```bash
# Sync library and test
ai-config library sync
ai-config library list

# Test role discovery
ai-config roles list

# Test agent creation
ai-config create-agent --name test --role your-new-role --tool q-cli
```

### Code Changes
```bash
# Run tests
pytest

# Test CLI functionality
ai-config --help
ai-config library info
```

### Agent Testing
```bash
# Create test agent
ai-config create-agent --name test-agent --role software-engineer --tool q-cli

# Test with Amazon Q CLI (if available)
q chat --agent test-agent

# Clean up
ai-config agents remove --name test-agent --tool q-cli
```

## 📋 Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Add/modify knowledge files
   - Update code as needed
   - Add tests for new functionality

3. **Test thoroughly**:
   - Run all tests
   - Test CLI functionality
   - Test agent creation if applicable

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(scope): description of changes"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **PR Requirements**:
   - Clear description of changes
   - Tests pass
   - Documentation updated if needed
   - Knowledge content follows guidelines

## 🎯 Contribution Ideas

### High Priority
- **Multi-tool export**: Implement Claude Projects and ChatGPT support
- **Enhanced roles**: Add more role-specific knowledge (DevOps, QA, etc.)
- **Domain expertise**: Add more domain knowledge (Kubernetes, Terraform, etc.)
- **Interactive improvements**: Enhance the CLI menu system

### Medium Priority
- **Template system**: Templates for creating new knowledge files
- **Validation**: Enhanced agent config validation
- **Search improvements**: Better library search functionality
- **Collection management**: Folder-based knowledge combinations

### Low Priority
- **Performance**: Optimize library syncing and searching
- **UI improvements**: Better CLI output formatting
- **Documentation**: More usage examples and tutorials

## 🤝 Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and contribute
- Focus on practical, actionable knowledge
- Keep discussions focused and productive

## 📞 Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions or discuss ideas
- **Documentation**: Check existing docs first
- **Code Review**: Learn from PR feedback

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for helping make AI Configurator better for everyone! 🎉
