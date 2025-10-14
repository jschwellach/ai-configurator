# AI Configurator - Testing Strategy

## Testing Philosophy

The AI Configurator testing strategy follows a **comprehensive, multi-layered approach** ensuring reliability, maintainability, and user confidence. Testing is integrated into the development workflow with automated execution and clear quality gates.

### Core Testing Principles
1. **Test-Driven Development**: Write tests before or alongside implementation
2. **Comprehensive Coverage**: Minimum 90% code coverage across all components
3. **Fast Feedback**: Quick test execution for rapid development cycles
4. **Realistic Testing**: Use realistic test data and scenarios
5. **Automated Quality Gates**: Automated testing in CI/CD pipeline

## Testing Pyramid

### Unit Tests (Foundation - 70%)
**Purpose**: Test individual components in isolation
**Scope**: Functions, methods, and classes
**Speed**: Fast execution (< 1 second per test)
**Coverage**: All core business logic

```python
# Example: LibraryManager unit test
class TestLibraryManager:
    def test_sync_library_creates_directory(self, tmp_path):
        """Test that sync_library creates target directory."""
        # Arrange
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        
        manager = LibraryManager(target_dir)
        
        # Act
        result = manager.sync_library(source_dir)
        
        # Assert
        assert result is True
        assert target_dir.exists()
        assert target_dir.is_dir()
```

### Integration Tests (Middle - 20%)
**Purpose**: Test component interactions and workflows
**Scope**: Multi-component operations
**Speed**: Medium execution (< 5 seconds per test)
**Coverage**: Critical user workflows

```python
# Example: Agent creation integration test
class TestAgentCreationWorkflow:
    def test_create_agent_end_to_end(self, test_config_dir):
        """Test complete agent creation workflow."""
        # Arrange
        library_manager = LibraryManager(test_config_dir)
        agent_manager = AgentManager(test_config_dir)
        
        # Sync library first
        library_manager.sync_library()
        
        # Act
        agent = agent_manager.create_agent(
            name="test-agent",
            role="software-engineer", 
            tool="q-cli",
            include_common=True
        )
        
        # Assert
        assert agent.name == "test-agent"
        assert len(agent.knowledge_files) > 0
        assert agent_manager.agent_exists("test-agent", "q-cli")
```

### End-to-End Tests (Top - 10%)
**Purpose**: Test complete user scenarios through CLI
**Scope**: Full system workflows
**Speed**: Slower execution (< 30 seconds per test)
**Coverage**: Critical user journeys

```python
# Example: CLI end-to-end test
class TestCLIWorkflows:
    def test_complete_agent_lifecycle(self, runner, test_config):
        """Test complete agent lifecycle through CLI."""
        # Create agent
        result = runner.invoke(cli, [
            'create-agent', 
            '--name', 'e2e-test',
            '--role', 'software-engineer',
            '--tool', 'q-cli'
        ])
        assert result.exit_code == 0
        
        # List agents
        result = runner.invoke(cli, ['agents', 'list', '--tool', 'q-cli'])
        assert 'e2e-test' in result.output
        
        # Remove agent
        result = runner.invoke(cli, [
            'agents', 'remove', 
            '--name', 'e2e-test',
            '--tool', 'q-cli',
            '--confirm'
        ])
        assert result.exit_code == 0
```

## Test Categories

### Functional Tests
**Purpose**: Verify feature functionality matches requirements
**Coverage**: All user stories and acceptance criteria

#### Library Management Tests
```python
class TestLibraryFunctionality:
    def test_library_sync_updates_existing_files(self):
        """Test library sync updates modified files."""
        
    def test_library_search_finds_relevant_content(self):
        """Test search functionality returns relevant results."""
        
    def test_library_info_shows_accurate_statistics(self):
        """Test library info displays correct file counts."""
```

#### Agent Management Tests
```python
class TestAgentFunctionality:
    def test_agent_creation_with_role(self):
        """Test agent creation with role-based knowledge."""
        
    def test_agent_creation_with_custom_rules(self):
        """Test agent creation with custom knowledge selection."""
        
    def test_agent_update_modifies_configuration(self):
        """Test agent updates change configuration correctly."""
```

### Non-Functional Tests

#### Performance Tests
**Target**: Meet performance requirements
**Tools**: pytest-benchmark for performance measurement

```python
class TestPerformance:
    def test_agent_creation_performance(self, benchmark):
        """Test agent creation completes within 2 seconds."""
        def create_test_agent():
            return agent_manager.create_agent(
                "perf-test", "software-engineer", "q-cli"
            )
        
        result = benchmark(create_test_agent)
        assert benchmark.stats.mean < 2.0  # 2 second target
    
    def test_library_sync_performance(self, benchmark):
        """Test library sync completes within 5 seconds."""
        def sync_test_library():
            return library_manager.sync_library()
        
        result = benchmark(sync_test_library)
        assert benchmark.stats.mean < 5.0  # 5 second target
```

#### Security Tests
**Purpose**: Validate security measures and input validation

```python
class TestSecurity:
    def test_agent_name_validation_prevents_injection(self):
        """Test agent name validation prevents malicious input."""
        malicious_names = [
            "../../../etc/passwd",
            "<script>alert('xss')</script>",
            "'; DROP TABLE agents; --"
        ]
        
        for name in malicious_names:
            with pytest.raises(ValidationError):
                agent_manager.create_agent(name, "software-engineer", "q-cli")
    
    def test_file_path_validation_prevents_traversal(self):
        """Test file path validation prevents directory traversal."""
        malicious_paths = [
            "../../sensitive/file.txt",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for path in malicious_paths:
            assert not file_utils.is_safe_path(Path(path))
```

#### Compatibility Tests
**Purpose**: Ensure cross-platform compatibility

```python
class TestCompatibility:
    @pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
    def test_config_directory_creation(self, platform, monkeypatch):
        """Test config directory creation on different platforms."""
        monkeypatch.setattr(sys, "platform", platform)
        
        config_dir = get_config_directory()
        assert config_dir.is_absolute()
        
    def test_file_operations_cross_platform(self):
        """Test file operations work across platforms."""
        # Test with different path separators and formats
```

## Test Data Management

### Test Fixtures
**Purpose**: Provide consistent, realistic test data
**Location**: `tests/fixtures/`
**Management**: Automated fixture generation and cleanup

```python
# conftest.py - Shared fixtures
@pytest.fixture
def sample_library(tmp_path):
    """Create sample knowledge library for testing."""
    library_dir = tmp_path / "library"
    
    # Create directory structure
    (library_dir / "roles" / "software-engineer").mkdir(parents=True)
    (library_dir / "common").mkdir(parents=True)
    (library_dir / "domains").mkdir(parents=True)
    
    # Create sample files
    (library_dir / "roles" / "software-engineer" / "software-engineer.md").write_text(
        "# Software Engineer Role\nSample content for testing."
    )
    
    return library_dir

@pytest.fixture
def test_config_dir(tmp_path):
    """Create temporary configuration directory."""
    config_dir = tmp_path / "ai-configurator"
    config_dir.mkdir()
    return config_dir
```

### Mock Data Strategy
**Purpose**: Isolate components from external dependencies
**Tools**: unittest.mock for mocking external calls

```python
class TestAgentManagerWithMocks:
    @patch('ai_configurator.core.file_utils.FileUtils.copy_files')
    def test_agent_creation_handles_file_copy_failure(self, mock_copy):
        """Test agent creation handles file copy failures gracefully."""
        # Arrange
        mock_copy.return_value = False
        
        # Act & Assert
        with pytest.raises(AgentError, match="Failed to copy knowledge files"):
            agent_manager.create_agent("test", "software-engineer", "q-cli")
```

## Test Automation

### Continuous Integration
**Platform**: GitHub Actions (or similar CI/CD platform)
**Triggers**: Pull requests, main branch commits
**Matrix Testing**: Multiple Python versions and platforms

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        pip install -e .
    
    - name: Run tests
      run: pytest --cov=ai_configurator --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Testing
**Purpose**: Catch issues before commit
**Tools**: pre-commit hooks with test execution

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
        always_run: true
```

### Test Execution Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_configurator --cov-report=html

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest -m "not slow"                  # Skip slow tests

# Run performance tests
pytest --benchmark-only

# Run with verbose output
pytest -v --tb=short
```

## Quality Gates

### Coverage Requirements
- **Minimum Coverage**: 90% overall
- **Critical Components**: 95% coverage for core modules
- **New Code**: 100% coverage for new features
- **Exclusions**: Only test files and generated code excluded

### Performance Benchmarks
- **Agent Creation**: < 2 seconds (95th percentile)
- **Library Sync**: < 5 seconds (95th percentile)
- **CLI Response**: < 100ms for interactive operations
- **Memory Usage**: < 100MB for typical operations

### Quality Metrics
```bash
# Coverage report
pytest --cov=ai_configurator --cov-report=term-missing

# Performance benchmarks
pytest --benchmark-only --benchmark-sort=mean

# Code quality checks
flake8 ai_configurator/
mypy ai_configurator/
black --check ai_configurator/
```

## Test Environment Management

### Development Environment
```bash
# Setup development environment with testing tools
pip install -r requirements-dev.txt
pip install -e .

# Run tests in development
pytest --cov=ai_configurator
```

### CI/CD Environment
- **Isolated**: Each test run in clean environment
- **Matrix**: Multiple Python versions and OS combinations
- **Parallel**: Tests run in parallel where possible
- **Artifacts**: Test reports and coverage data preserved

### Test Database/Storage
- **Temporary**: All tests use temporary directories
- **Cleanup**: Automatic cleanup after test completion
- **Isolation**: No shared state between tests

## Error and Edge Case Testing

### Error Condition Testing
```python
class TestErrorConditions:
    def test_library_sync_with_permission_denied(self):
        """Test library sync handles permission errors."""
        
    def test_agent_creation_with_missing_knowledge_files(self):
        """Test agent creation handles missing files gracefully."""
        
    def test_cli_with_invalid_arguments(self):
        """Test CLI handles invalid arguments appropriately."""
```

### Edge Case Testing
```python
class TestEdgeCases:
    def test_agent_creation_with_empty_library(self):
        """Test agent creation with empty knowledge library."""
        
    def test_library_sync_with_large_files(self):
        """Test library sync with large knowledge files."""
        
    def test_concurrent_agent_operations(self):
        """Test concurrent agent creation/modification."""
```

## Test Reporting and Metrics

### Test Reports
- **Coverage Reports**: HTML and XML formats
- **Performance Reports**: Benchmark results with trends
- **Test Results**: JUnit XML for CI/CD integration
- **Quality Reports**: Code quality metrics and trends

### Metrics Tracking
- **Test Execution Time**: Track test performance over time
- **Coverage Trends**: Monitor coverage changes
- **Failure Rates**: Track test stability
- **Performance Benchmarks**: Monitor performance regressions

### Reporting Tools
```bash
# Generate comprehensive test report
pytest --cov=ai_configurator \
       --cov-report=html \
       --cov-report=xml \
       --junit-xml=test-results.xml \
       --benchmark-json=benchmark-results.json
```

## Test Maintenance Strategy

### Test Review Process
- **Code Reviews**: All test code reviewed like production code
- **Test Quality**: Tests must be readable, maintainable, and reliable
- **Test Data**: Regular review and update of test fixtures
- **Performance**: Regular review of test execution performance

### Test Refactoring
- **Regular Cleanup**: Remove obsolete tests, update outdated tests
- **DRY Principle**: Eliminate duplicate test code
- **Maintainability**: Keep tests simple and focused
- **Documentation**: Document complex test scenarios

### Test Evolution
- **New Features**: Add tests for all new functionality
- **Bug Fixes**: Add regression tests for all bug fixes
- **Refactoring**: Update tests when code structure changes
- **Performance**: Add performance tests for critical paths

---

**Testing Strategy Status**: Comprehensive and Implemented  
**Coverage Target**: 90% minimum, 95% for core components  
**Automation**: Fully automated CI/CD pipeline  
**Last Updated**: 2025-01-10  
**Next Review**: Quarterly strategy assessment
