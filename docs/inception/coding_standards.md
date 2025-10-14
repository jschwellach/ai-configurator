# AI Configurator - Coding Standards

## Code Style and Formatting

### Python Style Guide
**Standard**: PEP 8 - Style Guide for Python Code
**Formatter**: Black (automatic code formatting)
**Line Length**: 88 characters (Black default)
**Indentation**: 4 spaces (no tabs)

### Code Formatting Tools
```bash
# Automatic formatting
black ai_configurator/
black tests/

# Configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

### Import Organization
**Standard**: isort for import sorting
**Order**: 
1. Standard library imports
2. Third-party imports  
3. Local application imports

```python
# Standard library
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import click
import yaml

# Local
from ai_configurator.core import LibraryManager
from ai_configurator.core.file_utils import FileUtils
```

## Naming Conventions

### Variables and Functions
- **Style**: snake_case
- **Descriptive**: Use clear, descriptive names
- **Avoid abbreviations**: Prefer `configuration` over `config` in variable names

```python
# Good
def create_agent_configuration(name: str, role: str) -> dict:
    knowledge_files = []
    agent_metadata = {}
    
# Avoid
def create_cfg(n: str, r: str) -> dict:
    kf = []
    meta = {}
```

### Classes
- **Style**: PascalCase
- **Descriptive**: Clear purpose indication
- **Suffix patterns**: Manager, Handler, Exporter, etc.

```python
class LibraryManager:
    """Manages knowledge library operations"""
    
class AgentConfigurationHandler:
    """Handles agent configuration operations"""
    
class QCLIExporter:
    """Exports agents for Amazon Q CLI"""
```

### Constants
- **Style**: UPPER_SNAKE_CASE
- **Location**: Module level or class level
- **Grouping**: Related constants together

```python
# Configuration constants
DEFAULT_CONFIG_DIR = "~/.config/ai-configurator"
LIBRARY_SYNC_TIMEOUT = 30
MAX_AGENT_NAME_LENGTH = 50

# File extensions
MARKDOWN_EXTENSION = ".md"
JSON_EXTENSION = ".json"
```

### Files and Directories
- **Python files**: snake_case.py
- **Test files**: test_module_name.py
- **Directories**: snake_case or kebab-case

## Documentation Standards

### Docstrings
**Standard**: Google-style docstrings
**Required**: All public functions, classes, and modules
**Format**: Triple quotes with structured sections

```python
def create_agent(name: str, role: str, tool: str, include_common: bool = False) -> Agent:
    """Create a new agent with specified configuration.
    
    Args:
        name: Unique name for the agent
        role: Role-based knowledge to include
        tool: Target AI tool (q-cli, claude-code, chatgpt)
        include_common: Whether to include common organizational knowledge
        
    Returns:
        Agent: Configured agent instance
        
    Raises:
        AgentError: If agent creation fails
        LibraryError: If required knowledge files are missing
        
    Example:
        >>> agent = create_agent("my-dev", "software-engineer", "q-cli", True)
        >>> print(agent.name)
        my-dev
    """
```

### Inline Comments
- **Purpose**: Explain complex logic, not obvious code
- **Style**: Complete sentences with proper punctuation
- **Placement**: Above the code being explained

```python
# Calculate the absolute path to the user's configuration directory
# This handles cross-platform differences in config locations
config_path = Path.home() / ".config" / "ai-configurator"

# Ensure the directory exists before attempting file operations
config_path.mkdir(parents=True, exist_ok=True)
```

### Type Hints
**Required**: All function signatures and class attributes
**Standard**: Python typing module
**Compatibility**: Python 3.8+ compatible syntax

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def load_knowledge_files(paths: List[Path]) -> Dict[str, str]:
    """Load knowledge files from specified paths."""
    
class AgentManager:
    """Manages agent lifecycle operations."""
    
    def __init__(self, config_dir: Path) -> None:
        self.config_dir: Path = config_dir
        self.agents: Dict[str, Agent] = {}
```

## Error Handling Standards

### Exception Hierarchy
```python
class AIConfiguratorError(Exception):
    """Base exception for AI Configurator operations."""
    pass

class LibraryError(AIConfiguratorError):
    """Raised when library operations fail."""
    pass

class AgentError(AIConfiguratorError):
    """Raised when agent operations fail."""
    pass

class ValidationError(AIConfiguratorError):
    """Raised when input validation fails."""
    pass
```

### Error Handling Patterns
```python
def create_agent(config: AgentConfig) -> Agent:
    """Create agent with proper error handling."""
    try:
        # Validate input
        if not config.name:
            raise ValidationError("Agent name is required")
            
        # Perform operation
        agent = Agent(config)
        return agent
        
    except FileNotFoundError as e:
        raise LibraryError(f"Required knowledge file not found: {e}")
    except PermissionError as e:
        raise AgentError(f"Permission denied creating agent: {e}")
    except Exception as e:
        raise AgentError(f"Unexpected error creating agent: {e}")
```

### Logging Standards
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def sync_library() -> bool:
    """Sync library with proper logging."""
    logger.info("Starting library synchronization")
    
    try:
        # Perform sync operation
        result = perform_sync()
        logger.info("Library synchronization completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Library synchronization failed: {e}")
        raise
```

## Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from ai_configurator.core import LibraryManager
from ai_configurator.core.exceptions import LibraryError

class TestLibraryManager:
    """Test suite for LibraryManager class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_config_dir = Path("/tmp/test-ai-configurator")
        self.library_manager = LibraryManager(self.test_config_dir)
    
    def test_sync_library_success(self):
        """Test successful library synchronization."""
        # Arrange
        source_dir = Path("/tmp/source-library")
        
        # Act
        result = self.library_manager.sync_library(source_dir)
        
        # Assert
        assert result is True
        assert self.test_config_dir.exists()
    
    def test_sync_library_missing_source(self):
        """Test library sync with missing source directory."""
        # Arrange
        missing_dir = Path("/tmp/nonexistent")
        
        # Act & Assert
        with pytest.raises(LibraryError, match="Source directory not found"):
            self.library_manager.sync_library(missing_dir)
```

### Test Naming
- **Pattern**: `test_method_name_scenario`
- **Descriptive**: Clear indication of what is being tested
- **Scenarios**: Include success and failure cases

### Test Coverage
- **Target**: Minimum 90% code coverage
- **Focus**: Critical paths and error conditions
- **Tools**: pytest-cov for coverage reporting

```bash
# Run tests with coverage
pytest --cov=ai_configurator --cov-report=html tests/
```

## Code Quality Tools

### Linting
**Tool**: flake8 with additional plugins
**Configuration**: Setup in `.flake8` or `pyproject.toml`

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist
```

### Type Checking
**Tool**: mypy for static type checking
**Configuration**: `mypy.ini` or `pyproject.toml`

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

## File Organization Standards

### Module Structure
```
ai_configurator/
├── __init__.py              # Package initialization
├── cli.py                   # CLI interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── library_manager.py   # Library management
│   ├── agent_manager.py     # Agent management
│   ├── file_utils.py        # File utilities
│   └── exceptions.py        # Custom exceptions
├── exporters/               # Tool-specific exporters
│   ├── __init__.py
│   ├── base.py             # Base exporter class
│   ├── qcli.py             # Amazon Q CLI exporter
│   └── claude.py           # Claude Projects exporter
└── utils/                   # Utility modules
    ├── __init__.py
    └── validation.py        # Input validation
```

### Import Standards
```python
# Absolute imports preferred
from ai_configurator.core.library_manager import LibraryManager
from ai_configurator.core.exceptions import LibraryError

# Relative imports only within packages
from .base import BaseExporter
from ..core.file_utils import FileUtils
```

## Configuration Management

### Configuration Files
**Format**: TOML for project configuration, JSON for runtime configuration
**Location**: `pyproject.toml` for project settings

```toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
```

### Environment Variables
```python
import os
from pathlib import Path

# Configuration with environment variable override
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "ai-configurator"
CONFIG_DIR = Path(os.getenv("AI_CONFIGURATOR_CONFIG_DIR", DEFAULT_CONFIG_DIR))

# Debug mode
DEBUG = os.getenv("AI_CONFIGURATOR_DEBUG", "false").lower() == "true"
```

## Performance Standards

### Efficiency Guidelines
- **File Operations**: Minimize I/O operations, use batch operations when possible
- **Memory Usage**: Avoid loading large files into memory unnecessarily
- **Caching**: Cache frequently accessed data appropriately
- **Lazy Loading**: Load resources only when needed

```python
from functools import lru_cache

class LibraryManager:
    @lru_cache(maxsize=128)
    def get_knowledge_file_content(self, file_path: Path) -> str:
        """Cache knowledge file content for performance."""
        return file_path.read_text(encoding='utf-8')
```

### Performance Targets
- **Agent Creation**: < 2 seconds
- **Library Sync**: < 5 seconds  
- **CLI Response**: < 100ms for interactive operations
- **Memory Usage**: < 100MB for typical operations

## Security Standards

### Input Validation
```python
import re
from pathlib import Path

def validate_agent_name(name: str) -> bool:
    """Validate agent name for security and compatibility."""
    if not name or len(name) > 50:
        return False
    
    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name))

def validate_file_path(path: Path, allowed_base: Path) -> bool:
    """Prevent directory traversal attacks."""
    try:
        resolved_path = path.resolve()
        allowed_base_resolved = allowed_base.resolve()
        return resolved_path.is_relative_to(allowed_base_resolved)
    except (OSError, ValueError):
        return False
```

### File Permissions
```python
import stat

def create_secure_file(file_path: Path, content: str) -> None:
    """Create file with appropriate permissions."""
    file_path.write_text(content, encoding='utf-8')
    
    # Set read/write for owner only
    file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)
```

## Version Control Standards

### Commit Messages
**Format**: Conventional Commits specification
**Structure**: `type(scope): description`

```
feat(agent): add support for Claude Projects export
fix(library): resolve sync issue with large files  
docs(readme): update installation instructions
test(core): add unit tests for AgentManager
refactor(cli): simplify command argument parsing
```

### Branch Naming
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-fix`
- **Documentation**: `docs/description-of-docs`
- **Refactoring**: `refactor/description-of-refactor`

### Code Review Standards
- **Required**: All changes require code review
- **Checklist**: Code style, tests, documentation, security
- **Approval**: At least one approval required for merge

---

**Coding Standards Status**: Active and Enforced  
**Last Updated**: 2025-01-10  
**Tools**: Black, flake8, mypy, pytest  
**Compliance**: Automated via pre-commit hooks
