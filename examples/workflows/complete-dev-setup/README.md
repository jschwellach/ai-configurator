# Complete Development Setup Workflow

This workflow provides a comprehensive development environment that integrates multiple contexts and automation hooks to create a complete, production-ready development experience. It's designed for developers who want a fully automated setup with code quality, testing, documentation, and security built-in from day one.

## Overview

The Complete Development Setup Workflow combines:

- **Environment Management**: Automated virtual environment setup and dependency management
- **Code Quality**: Real-time linting, formatting, and security scanning
- **Testing Automation**: Automated test execution with coverage reporting
- **Documentation Generation**: Automatic API docs and project documentation
- **Git Workflow Integration**: Pre-commit hooks and branch protection
- **Security Scanning**: Vulnerability detection and dependency auditing

## Quick Start

1. **Copy the workflow to your project**:

   ```bash
   cp -r examples/workflows/complete-dev-setup/ .kiro/profiles/
   ```

2. **Activate the profile**:

   ```bash
   ai-configurator profile activate complete-dev-setup
   ```

3. **Initialize your development environment**:
   The environment-setup hook will automatically run and configure your development environment.

## What Gets Set Up

### Development Environment

- Python virtual environment (`.venv/`)
- Development dependencies installation
- Pre-commit hooks configuration
- Git configuration and hooks
- Directory structure creation (`src/`, `tests/`, `docs/`, `reports/`)

### Code Quality Tools

- **Black**: Code formatting
- **Flake8**: Style and error checking
- **isort**: Import sorting
- **MyPy**: Type checking
- **Bandit**: Security linting
- **Pylint**: Comprehensive code analysis

### Testing Infrastructure

- **Pytest**: Test runner with coverage
- **Coverage.py**: Code coverage reporting
- Automated test execution on file changes
- HTML and XML coverage reports

### Documentation System

- Automatic API documentation generation
- Code structure documentation
- Changelog generation
- Usage examples and tutorials

### Security Features

- Dependency vulnerability scanning
- Code security analysis
- Secrets detection
- License compliance checking

## Hooks and Automation

### Environment Setup Hook

**Trigger**: On session start
**Purpose**: Initialize complete development environment

```yaml
Features:
  - Virtual environment creation
  - Dependency installation
  - Development tools setup
  - Git configuration
  - Directory structure creation
```

### Code Quality Check Hook

**Trigger**: On file save
**Purpose**: Real-time code quality analysis

```yaml
Features:
  - Multi-linter analysis
  - Automatic code formatting
  - Security vulnerability detection
  - Quality gate enforcement
```

### Auto Documentation Hook

**Trigger**: On commit
**Purpose**: Generate comprehensive documentation

```yaml
Features:
  - API reference generation
  - Code structure documentation
  - Changelog updates
  - Usage examples
```

### Test Automation Hook

**Trigger**: On file save
**Purpose**: Automated testing with coverage

```yaml
Features:
  - Automatic test discovery
  - Coverage reporting
  - Performance benchmarking
  - Quality gate validation
```

### Git Workflow Hook

**Trigger**: On git events
**Purpose**: Automated git workflow management

```yaml
Features:
  - Pre-commit quality checks
  - Commit message validation
  - Branch protection
  - Automated changelog
```

### Security Scan Hook

**Trigger**: On dependency changes
**Purpose**: Security vulnerability detection

```yaml
Features:
  - Dependency vulnerability scanning
  - Code security analysis
  - Secrets detection
  - License compliance
```

## Directory Structure

After setup, your project will have this structure:

```
your-project/
├── .venv/                 # Virtual environment
├── src/                   # Source code
├── tests/                 # Test files
├── docs/                  # Documentation
│   ├── generated/         # Auto-generated docs
│   └── manual/           # Manual documentation
├── reports/              # Quality and coverage reports
│   ├── quality/          # Code quality reports
│   ├── coverage/         # Test coverage reports
│   ├── security/         # Security scan reports
│   └── performance/      # Performance reports
├── scripts/              # Utility scripts
├── .pre-commit-config.yaml
├── pytest.ini
├── setup.cfg
└── .gitignore
```

## Configuration Files

### Pre-commit Configuration

The workflow automatically creates a `.pre-commit-config.yaml` with:

- Code formatting (Black, isort)
- Linting (Flake8, Pylint)
- Security scanning (Bandit)
- Type checking (MyPy)

### Pytest Configuration

Creates `pytest.ini` with:

- Test discovery patterns
- Coverage configuration
- Output formatting
- Plugin settings

### Setup Configuration

Creates `setup.cfg` with:

- Tool configurations
- Quality thresholds
- Ignore patterns
- Output settings

## Customization

### For Different Project Types

#### Web Development Projects

```json
{
  "paths": [
    "contexts/development-guidelines.md",
    "contexts/web-development-practices.md",
    "contexts/frontend-testing-strategies.md"
  ],
  "hooks": {
    "javascript-quality": { "enabled": true },
    "build-automation": { "enabled": true },
    "deployment-pipeline": { "enabled": true }
  }
}
```

#### Data Science Projects

```json
{
  "paths": [
    "contexts/development-guidelines.md",
    "examples/contexts/domains/data-science-best-practices.md",
    "contexts/jupyter-best-practices.md"
  ],
  "hooks": {
    "notebook-quality": { "enabled": true },
    "data-validation": { "enabled": true },
    "model-validation": { "enabled": true }
  }
}
```

#### DevOps/Infrastructure Projects

```json
{
  "paths": [
    "contexts/development-guidelines.md",
    "examples/contexts/domains/devops-methodologies.md",
    "contexts/infrastructure-as-code.md"
  ],
  "hooks": {
    "infrastructure-validation": { "enabled": true },
    "security-compliance": { "enabled": true },
    "deployment-automation": { "enabled": true }
  }
}
```

### Hook Configuration

#### Adjusting Quality Gates

```json
{
  "hooks": {
    "code-quality-check": {
      "config": {
        "quality_gates": {
          "max_line_length": 100,
          "max_complexity": 15,
          "min_test_coverage": 90,
          "max_security_issues": 0
        }
      }
    }
  }
}
```

#### Customizing Test Automation

```json
{
  "hooks": {
    "test-automation": {
      "config": {
        "coverage_threshold": 95,
        "parallel_execution": true,
        "performance_benchmarks": true,
        "integration_tests": true
      }
    }
  }
}
```

#### Security Configuration

```json
{
  "hooks": {
    "security-scan": {
      "config": {
        "severity_threshold": "high",
        "auto_update_dependencies": true,
        "compliance_frameworks": ["OWASP", "CIS"]
      }
    }
  }
}
```

## Team Collaboration

### Code Review Integration

The workflow integrates with code review processes:

- Pre-commit hooks ensure quality before commits
- Automated documentation updates with changes
- Security scans prevent vulnerable code
- Test coverage requirements for new code

### CI/CD Integration

Works seamlessly with CI/CD pipelines:

- Quality reports in standard formats
- Test results and coverage data
- Security scan results
- Performance benchmarks

### Team Standards

Enforces consistent team standards:

- Code formatting and style
- Testing requirements
- Documentation standards
- Security practices

## Troubleshooting

### Common Issues

#### Virtual Environment Problems

```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
pip install -r requirements-dev.txt
```

#### Pre-commit Hook Failures

```bash
# Update pre-commit hooks
pre-commit autoupdate
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Test Coverage Issues

```bash
# Generate detailed coverage report
pytest --cov=src --cov-report=html
# Open reports/coverage/htmlcov/index.html
```

#### Documentation Generation Problems

```bash
# Manually generate documentation
python -m sphinx.cmd.build -b html docs/ docs/_build/html
```

### Performance Optimization

#### For Large Projects

- Adjust `max_contexts` setting
- Enable selective hook execution
- Use parallel test execution
- Configure incremental documentation builds

#### For Slow Machines

- Disable real-time hooks
- Reduce quality check frequency
- Use lightweight linters only
- Disable performance monitoring

## Advanced Features

### Custom Hook Development

Create custom hooks for specific needs:

1. Create hook YAML configuration
2. Implement Python script
3. Add to workflow profile
4. Test and validate

### Integration with External Tools

- **Slack/Teams**: Notifications for quality issues
- **Jira**: Automatic issue creation for security vulnerabilities
- **SonarQube**: Advanced code quality metrics
- **Grafana**: Performance monitoring dashboards

### Metrics and Reporting

The workflow generates comprehensive metrics:

- Code quality trends
- Test coverage evolution
- Security vulnerability tracking
- Performance benchmarks
- Team productivity metrics

## Support and Resources

### Documentation

- [Hook Development Guide](docs/hooks/development-guide.md)
- [Customization Examples](docs/examples/customization.md)
- [Troubleshooting Guide](docs/troubleshooting/common-issues.md)

### Community

- [GitHub Discussions](https://github.com/ai-configurator/discussions)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/ai-configurator)
- [Discord Community](https://discord.gg/ai-configurator)

### Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This workflow is part of the AI Configurator project and is licensed under the MIT License.
