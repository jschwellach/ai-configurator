# Contributing to AI Configurator

Thank you for your interest in contributing to AI Configurator! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/ai-configurator.git
   cd ai-configurator
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

5. Run tests to ensure everything is working:
   ```bash
   pytest
   ```

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs
- Include detailed information about your environment
- Provide steps to reproduce the issue
- Include relevant error messages and logs

### Suggesting Features

- Open an issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would be valuable to the project

### Code Contributions

1. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Write or update tests** for your changes

4. **Run the test suite** to ensure all tests pass:
   ```bash
   pytest
   flake8 src/ tests/
   ```

5. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork** and create a pull request

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep line length under 88 characters (Black formatter standard)

### Code Quality

- Write unit tests for new functionality
- Maintain or improve test coverage
- Use meaningful variable and function names
- Add comments for complex logic

### Documentation

- Update documentation for any user-facing changes
- Include docstrings for all public APIs
- Update the README if necessary
- Add examples for new features

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ai_configurator

# Run specific test file
pytest tests/unit/test_config_manager.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies

## Documentation

### Writing Documentation

- Use clear, concise language
- Include practical examples
- Follow the existing documentation structure
- Test all code examples

### Documentation Structure

- User documentation goes in `docs/`
- API documentation is auto-generated from docstrings
- Development documentation goes in `docs/development/`

## Pull Request Process

1. **Ensure your PR addresses a specific issue** or implements a planned feature
2. **Update documentation** as needed
3. **Add or update tests** for your changes
4. **Ensure all tests pass** and code follows style guidelines
5. **Write a clear PR description** explaining your changes
6. **Link to relevant issues** in your PR description

### PR Review Process

- All PRs require at least one review from a maintainer
- Address any feedback or requested changes
- Keep your PR up to date with the main branch
- Be responsive to review comments

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information without permission
- Any conduct that would be inappropriate in a professional setting

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for sensitive issues

## Recognition

Contributors are recognized in the following ways:

- Listed in the project's contributors
- Mentioned in release notes for significant contributions
- Invited to become maintainers for sustained contributions

## License

By contributing to AI Configurator, you agree that your contributions will be licensed under the MIT License.

## Development Workflow

### Branch Naming

- `feature/description` for new features
- `bugfix/description` for bug fixes
- `docs/description` for documentation updates
- `refactor/description` for code refactoring

### Commit Messages

Use clear, descriptive commit messages:

```
Add profile validation for MCP server configurations

- Implement validation logic for MCP server profiles
- Add unit tests for validation functions
- Update documentation with validation examples

Fixes #123
```

### Release Process

Releases are handled by maintainers following semantic versioning:

- **Major** (x.0.0): Breaking changes
- **Minor** (0.x.0): New features, backward compatible
- **Patch** (0.0.x): Bug fixes, backward compatible

Thank you for contributing to AI Configurator!