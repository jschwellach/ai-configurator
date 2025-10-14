# AI Configurator - Development Workflow

## Development Process Overview

The AI Configurator follows a **structured, quality-focused development workflow** that emphasizes collaboration, automated testing, and continuous integration. The workflow is designed to maintain high code quality while enabling rapid feature development and reliable releases.

## Git Workflow Strategy

### Branching Model
**Strategy**: Feature Branch Workflow with Main Branch Protection
**Main Branch**: `main` (production-ready code)
**Development**: Feature branches from main
**Releases**: Tagged releases from main

```
main
├── feature/agent-creation-enhancement
├── feature/claude-projects-integration  
├── fix/library-sync-performance
└── docs/architecture-documentation
```

### Branch Naming Conventions
```bash
# Feature branches
feature/short-description-of-feature
feature/multi-tool-export-system
feature/interactive-menu-enhancement

# Bug fix branches  
fix/short-description-of-fix
fix/agent-creation-error-handling
fix/library-sync-permission-issue

# Documentation branches
docs/short-description-of-docs
docs/api-documentation-update
docs/user-guide-enhancement

# Refactoring branches
refactor/short-description-of-refactor
refactor/agent-manager-simplification
refactor/cli-command-structure
```

### Commit Message Standards
**Format**: Conventional Commits specification
**Structure**: `type(scope): description`

```bash
# Feature commits
feat(agent): add support for Claude Projects export
feat(cli): implement interactive agent update menu
feat(library): add knowledge file search functionality

# Bug fix commits
fix(sync): resolve library sync timeout issue
fix(agent): handle missing knowledge files gracefully
fix(cli): fix argument parsing for complex commands

# Documentation commits
docs(readme): update installation instructions
docs(api): add docstrings for AgentManager class
docs(architecture): create component interaction diagrams

# Refactoring commits
refactor(core): simplify file utility functions
refactor(cli): extract command handlers to separate modules
refactor(tests): improve test organization and fixtures
```

## Development Environment Setup

### Initial Setup
```bash
# Clone repository
git clone https://github.com/organization/ai-configurator.git
cd ai-configurator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .

# Setup pre-commit hooks
pre-commit install

# Verify setup
ai-config --version
pytest
```

### Development Dependencies
```python
# requirements-dev.txt
pytest>=7.0.0           # Testing framework
pytest-cov>=4.0.0       # Coverage reporting
pytest-benchmark>=4.0.0 # Performance testing
black>=22.0.0           # Code formatting
flake8>=5.0.0           # Linting
mypy>=1.0.0             # Type checking
pre-commit>=2.20.0      # Pre-commit hooks
twine>=4.0.0            # Package uploading
build>=0.8.0            # Package building
```

### IDE Configuration
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Feature Development Workflow

### 1. Planning Phase
```bash
# Create feature branch
git checkout main
git pull origin main
git checkout -b feature/new-feature-name

# Plan implementation
# - Review user stories and acceptance criteria
# - Design component interactions
# - Identify test requirements
# - Estimate development effort
```

### 2. Implementation Phase
```bash
# Development cycle
# 1. Write failing tests (TDD approach)
pytest tests/test_new_feature.py -v

# 2. Implement feature
# - Follow coding standards
# - Add comprehensive docstrings
# - Handle error conditions

# 3. Run tests and ensure they pass
pytest tests/test_new_feature.py -v
pytest --cov=ai_configurator

# 4. Format and lint code
black ai_configurator/
flake8 ai_configurator/
mypy ai_configurator/

# 5. Commit changes
git add .
git commit -m "feat(component): implement new feature functionality"
```

### 3. Testing and Quality Assurance
```bash
# Run comprehensive test suite
pytest --cov=ai_configurator --cov-report=html

# Performance testing
pytest --benchmark-only

# Integration testing
pytest tests/integration/

# Manual testing
ai-config create-agent --name test --role software-engineer --tool q-cli
ai-config agents list --tool q-cli
ai-config agents remove --name test --tool q-cli --confirm
```

### 4. Code Review Process
```bash
# Push feature branch
git push origin feature/new-feature-name

# Create pull request
# - Provide clear description of changes
# - Link to related issues or user stories
# - Include testing instructions
# - Add screenshots for UI changes
```

#### Pull Request Template
```markdown
## Description
Brief description of the changes and their purpose.

## Related Issues
- Closes #123
- Addresses #456

## Changes Made
- [ ] Added new feature X
- [ ] Updated documentation
- [ ] Added tests for new functionality
- [ ] Updated CLI help text

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance benchmarks meet targets

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

### 5. Review and Merge
```bash
# Address review feedback
git add .
git commit -m "fix(review): address code review feedback"
git push origin feature/new-feature-name

# After approval, merge to main
# Use squash merge for clean history
git checkout main
git pull origin main
git branch -d feature/new-feature-name
```

## Code Quality Workflow

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML]

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
        always_run: true
```

### Continuous Integration
```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        pip install -e .

    - name: Lint with flake8
      run: flake8 ai_configurator/

    - name: Type check with mypy
      run: mypy ai_configurator/

    - name: Test with pytest
      run: pytest --cov=ai_configurator --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Release Workflow

### Version Management
**Strategy**: Semantic Versioning (SemVer)
**Format**: MAJOR.MINOR.PATCH (e.g., 3.1.2)
**Tagging**: Git tags for releases

```bash
# Version bump examples
3.0.0 → 3.0.1  # Patch: bug fixes
3.0.1 → 3.1.0  # Minor: new features (backward compatible)
3.1.0 → 4.0.0  # Major: breaking changes
```

### Release Process
```bash
# 1. Prepare release
git checkout main
git pull origin main

# 2. Update version
# Update version in pyproject.toml
# Update CHANGELOG.md

# 3. Create release commit
git add .
git commit -m "chore(release): prepare version 3.1.0"

# 4. Create and push tag
git tag v3.1.0
git push origin main
git push origin v3.1.0

# 5. Build and upload to PyPI (automated via GitHub Actions)
# Manual process if needed:
python -m build
python -m twine upload dist/*
```

### Automated Release
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install build dependencies
      run: |
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Upload to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

## Documentation Workflow

### Documentation Standards
- **Code Documentation**: Docstrings for all public functions and classes
- **User Documentation**: README, installation guides, usage examples
- **Technical Documentation**: Architecture, API reference, development guides
- **Process Documentation**: Workflows, standards, guidelines

### Documentation Updates
```bash
# Documentation changes
git checkout -b docs/update-user-guide

# Update documentation files
# - README.md for user-facing changes
# - docs/ directory for technical documentation
# - Docstrings for code changes

# Test documentation
# - Verify markdown formatting
# - Test code examples
# - Check links and references

git add .
git commit -m "docs(guide): update user installation guide"
git push origin docs/update-user-guide
```

## Hotfix Workflow

### Critical Bug Fixes
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b fix/critical-security-issue

# Implement fix
# - Minimal changes to address issue
# - Add regression tests
# - Update documentation if needed

# Test thoroughly
pytest
# Manual testing of fix

# Commit and push
git add .
git commit -m "fix(security): resolve critical vulnerability in file handling"
git push origin fix/critical-security-issue

# Create urgent pull request
# - Mark as high priority
# - Request immediate review
# - Include detailed testing instructions

# After merge, create hotfix release
git checkout main
git pull origin main
git tag v3.0.1
git push origin v3.0.1
```

## Development Best Practices

### Code Review Guidelines
1. **Functionality**: Does the code work as intended?
2. **Code Quality**: Is the code clean, readable, and maintainable?
3. **Testing**: Are there adequate tests for the changes?
4. **Documentation**: Is documentation updated appropriately?
5. **Performance**: Are there any performance implications?
6. **Security**: Are there any security concerns?

### Testing Guidelines
```bash
# Before committing
pytest --cov=ai_configurator --cov-report=term-missing
black --check ai_configurator/
flake8 ai_configurator/
mypy ai_configurator/

# Before pushing
pytest tests/integration/
# Manual testing of affected functionality
```

### Communication Guidelines
- **Pull Requests**: Clear descriptions with context and testing instructions
- **Issues**: Detailed bug reports with reproduction steps
- **Commits**: Descriptive commit messages following conventional commits
- **Code Comments**: Explain complex logic and business decisions

## Troubleshooting Development Issues

### Common Issues and Solutions
```bash
# Import errors after installation
pip install -e .

# Test failures due to missing fixtures
pytest --setup-show tests/

# Pre-commit hook failures
pre-commit run --all-files

# Type checking errors
mypy ai_configurator/ --show-error-codes

# Coverage below threshold
pytest --cov=ai_configurator --cov-report=html
# Open htmlcov/index.html to identify uncovered code
```

### Development Environment Reset
```bash
# Clean environment reset
deactivate  # Exit virtual environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pre-commit install
```

---

**Development Workflow Status**: Active and Enforced  
**Branching Strategy**: Feature Branch Workflow  
**Quality Gates**: Automated testing, code review, CI/CD  
**Release Process**: Semantic versioning with automated PyPI deployment  
**Last Updated**: 2025-01-10  
**Next Review**: Quarterly workflow assessment
