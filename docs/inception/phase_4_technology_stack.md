# Technology Stack - Phase 4 TUI Enhancement

## Overview

Phase 4 adds Textual TUI framework while maintaining all existing technologies from Phases 1-3.

## New Dependencies

### TUI Framework
```python
textual>=0.40.0              # Modern Python TUI framework
textual-dev>=1.0.0           # Development tools and live reload
```

**Rationale**:
- Built on Rich (already in use)
- Modern async architecture
- Excellent documentation
- Active development
- Widget library included
- CSS-like styling

### CLI Enhancement
```python
click-default-group>=1.2.2   # Better command grouping
```

**Rationale**:
- Enables default subcommands
- Better help organization
- Cleaner CLI structure

## Existing Dependencies (Retained)

### Core Framework (Unchanged)
```python
click>=8.0.0                 # CLI framework
rich>=13.0.0                 # Terminal formatting (used by Textual)
pydantic>=2.0.0              # Data validation
pyyaml>=6.0.0                # YAML configuration
jsonschema>=4.0.0            # JSON validation
```

### File Operations (Unchanged)
```python
watchdog>=3.0.0              # File system monitoring
gitpython>=3.1.0             # Git operations
```

### Utilities (Unchanged)
```python
requests>=2.28.0             # HTTP requests
packaging>=21.0.0            # Version handling
prompt-toolkit>=3.0.0        # Interactive prompts (CLI fallback)
```

### Development (Unchanged)
```python
pytest>=7.0.0                # Testing framework
pytest-cov>=4.0.0            # Coverage reporting
pytest-mock>=3.10.0          # Mocking
black>=23.0.0                # Code formatting
flake8>=6.0.0                # Linting
mypy>=1.0.0                  # Type checking
```

## Updated Requirements Files

### requirements.txt
```python
# Core Framework
click>=8.0.0
click-default-group>=1.2.2
rich>=13.0.0
pydantic>=2.0.0
pyyaml>=6.0.0
jsonschema>=4.0.0

# TUI Framework (NEW)
textual>=0.40.0

# File Operations
watchdog>=3.0.0
gitpython>=3.1.0

# Utilities
requests>=2.28.0
packaging>=21.0.0
prompt-toolkit>=3.0.0
```

### requirements-dev.txt
```python
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0       # NEW: For async TUI tests

# Code Quality
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# TUI Development (NEW)
textual-dev>=1.0.0
```

## Technology Decisions

### Why Textual?

**Alternatives Considered**:
1. **urwid**: Older, less intuitive API
2. **blessed**: Lower-level, more work
3. **py-cui**: Less mature, smaller community
4. **rich only**: No full TUI support

**Textual Advantages**:
- Modern async/await support
- Built on Rich (already using)
- Excellent widget library
- CSS-like styling system
- Active development
- Great documentation
- Hot reload for development

### Why Keep Click?

- Already integrated
- Excellent for CLI commands
- Works alongside Textual
- Industry standard
- Good testing support

### Why Not Replace Rich?

- Textual uses Rich internally
- Rich still useful for CLI output
- No breaking changes needed
- Smooth integration

## Architecture Integration

### Entry Point Structure

```python
# ai_configurator/main.py
import sys
from .cli_enhanced import cli
from .tui.app import AIConfiguratorApp

def main():
    """Main entry point - detects mode."""
    
    # If no args or 'tui' command, launch TUI
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == 'tui'):
        app = AIConfiguratorApp()
        app.run()
    else:
        # Run CLI commands
        cli()

if __name__ == '__main__':
    main()
```

### Project Structure

```
ai_configurator/
├── __init__.py
├── main.py                  # Entry point (NEW)
├── cli_enhanced.py          # CLI commands (UPDATED)
├── tui/                     # TUI components (NEW)
│   ├── __init__.py
│   ├── app.py              # Main TUI application
│   ├── screens/            # Screen components
│   │   ├── __init__.py
│   │   ├── base.py         # Base screen class
│   │   ├── main_menu.py    # Dashboard
│   │   ├── agent_manager.py
│   │   ├── library_manager.py
│   │   ├── mcp_manager.py
│   │   └── settings.py
│   ├── widgets/            # Reusable widgets
│   │   ├── __init__.py
│   │   ├── agent_list.py
│   │   ├── conflict_resolver.py
│   │   ├── server_browser.py
│   │   └── progress.py
│   └── styles/             # CSS-like styles
│       └── default.css
├── models/                  # Data models (UNCHANGED)
├── services/                # Business logic (UNCHANGED)
└── core/                    # Core utilities (UNCHANGED)
```

## Textual Application Structure

### Main Application

```python
# ai_configurator/tui/app.py
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from .screens.main_menu import MainMenuScreen
from .screens.agent_manager import AgentManagerScreen
from .screens.library_manager import LibraryManagerScreen
from .screens.mcp_manager import MCPManagerScreen
from .screens.settings import SettingsScreen

class AIConfiguratorApp(App):
    """AI Configurator TUI Application."""
    
    CSS_PATH = "styles/default.css"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("?", "help", "Help"),
        Binding("escape", "back", "Back"),
    ]
    
    SCREENS = {
        "main_menu": MainMenuScreen,
        "agent_manager": AgentManagerScreen,
        "library_manager": LibraryManagerScreen,
        "mcp_manager": MCPManagerScreen,
        "settings": SettingsScreen,
    }
    
    def on_mount(self) -> None:
        """Initialize application."""
        self.push_screen("main_menu")
    
    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header()
        yield Footer()
```

### Screen Example

```python
# ai_configurator/tui/screens/agent_manager.py
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Button
from textual.containers import Container, Horizontal

from ...services import AgentService
from ..widgets.agent_list import AgentListWidget

class AgentManagerScreen(Screen):
    """Agent management screen."""
    
    BINDINGS = [
        ("n", "new_agent", "New"),
        ("e", "edit_agent", "Edit"),
        ("d", "delete_agent", "Delete"),
        ("x", "export_agent", "Export"),
    ]
    
    def __init__(self):
        super().__init__()
        self.agent_service = AgentService()
    
    def compose(self) -> ComposeResult:
        """Build screen layout."""
        yield Container(
            Horizontal(
                Button("New", id="new"),
                Button("Edit", id="edit"),
                Button("Delete", id="delete"),
                Button("Export", id="export"),
            ),
            AgentListWidget(id="agent_list"),
        )
    
    def on_mount(self) -> None:
        """Load data on mount."""
        self.refresh_agents()
    
    def refresh_agents(self) -> None:
        """Refresh agent list."""
        agents = self.agent_service.list_agents()
        self.query_one(AgentListWidget).load_agents(agents)
    
    def action_new_agent(self) -> None:
        """Create new agent."""
        # Show agent creation form
        pass
```

### Widget Example

```python
# ai_configurator/tui/widgets/agent_list.py
from textual.widgets import DataTable

class AgentListWidget(DataTable):
    """Widget for displaying agent list."""
    
    def on_mount(self) -> None:
        """Initialize table."""
        self.add_columns("Name", "Tool", "Resources", "Status")
    
    def load_agents(self, agents: List[Agent]) -> None:
        """Load agents into table."""
        self.clear()
        for agent in agents:
            self.add_row(
                agent.name,
                agent.tool_type.value,
                str(len(agent.config.resources)),
                agent.health_status.value,
            )
```

### Styling Example

```css
/* ai_configurator/tui/styles/default.css */

Screen {
    background: $surface;
}

Header {
    background: $primary;
    color: $text;
}

Footer {
    background: $panel;
}

Button {
    background: $primary;
    color: $text;
}

Button:hover {
    background: $primary-lighten-1;
}

DataTable {
    background: $surface;
    border: solid $primary;
}

DataTable > .datatable--cursor {
    background: $primary;
}
```

## CLI Command Structure

### Updated CLI with Groups

```python
# ai_configurator/cli_enhanced.py
import click
from click_default_group import DefaultGroup

@click.group(cls=DefaultGroup, default='status', default_if_no_args=True)
def cli():
    """AI Configurator - Tool-agnostic knowledge library manager."""
    pass

# Agent commands
@cli.group()
def agent():
    """Agent management commands."""
    pass

@agent.command()
def list():
    """List all agents."""
    pass

@agent.command()
@click.argument('name')
def create(name: str):
    """Create new agent."""
    pass

# Library commands
@cli.group()
def library():
    """Library management commands."""
    pass

@library.command()
def status():
    """Show library status."""
    pass

@library.command()
def sync():
    """Sync library."""
    pass

# MCP commands
@cli.group()
def mcp():
    """MCP server management."""
    pass

@mcp.command()
def browse():
    """Browse MCP registry."""
    pass

@mcp.command()
@click.argument('name')
def install(name: str):
    """Install MCP server."""
    pass

# Top-level commands
@cli.command()
def status():
    """Show system status."""
    pass

@cli.command()
def tui():
    """Launch TUI interface."""
    from .tui.app import AIConfiguratorApp
    app = AIConfiguratorApp()
    app.run()
```

## Testing Strategy

### TUI Testing with Textual

```python
# tests/tui/test_agent_manager_screen.py
from textual.pilot import Pilot
from ai_configurator.tui.app import AIConfiguratorApp

async def test_agent_manager_screen():
    """Test agent manager screen."""
    app = AIConfiguratorApp()
    async with app.run_test() as pilot:
        # Navigate to agent manager
        await pilot.press("enter")  # Select agent management
        
        # Check screen loaded
        assert app.screen.id == "agent_manager"
        
        # Check agents displayed
        agent_list = app.query_one(AgentListWidget)
        assert agent_list.row_count > 0
```

### CLI Testing (Unchanged)

```python
# tests/cli/test_agent_commands.py
from click.testing import CliRunner
from ai_configurator.cli_enhanced import agent

def test_agent_list():
    """Test agent list command."""
    runner = CliRunner()
    result = runner.invoke(agent, ['list'])
    assert result.exit_code == 0
    assert 'agents' in result.output.lower()
```

## Development Workflow

### TUI Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run with hot reload
textual run --dev ai_configurator/tui/app.py

# Debug with console
textual console

# Run in separate terminal
textual run --dev ai_configurator/tui/app.py
```

### CLI Development (Unchanged)

```bash
# Install in editable mode
pip install -e .

# Run CLI
ai-config agent list

# Run tests
pytest tests/cli/
```

## Performance Considerations

### TUI Performance
- **Async Operations**: All I/O operations async
- **Lazy Loading**: Load data on-demand
- **Virtual Scrolling**: For large lists
- **Debouncing**: Input handling debounced

### CLI Performance (Unchanged)
- Fast command execution
- Minimal dependencies loaded
- Efficient service calls

## Cross-Platform Compatibility

### Terminal Support
- **Linux**: Full support (all terminals)
- **macOS**: Full support (Terminal, iTerm2)
- **Windows**: Full support (Windows Terminal, ConEmu)
- **SSH**: Works over SSH connections

### Fallback Strategy
- If TUI fails to initialize, fall back to CLI
- Detect terminal capabilities
- Graceful degradation

## Deployment

### Package Updates

```toml
# pyproject.toml
[project]
name = "ai-configurator"
version = "4.0.0"
dependencies = [
    "click>=8.0.0",
    "click-default-group>=1.2.2",
    "rich>=13.0.0",
    "textual>=0.40.0",
    "pydantic>=2.0.0",
    # ... other dependencies
]

[project.scripts]
ai-config = "ai_configurator.main:main"

[project.optional-dependencies]
dev = [
    "textual-dev>=1.0.0",
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    # ... other dev dependencies
]
```

### Installation

```bash
# Standard installation
pip install ai-configurator

# Development installation
pip install ai-configurator[dev]

# From source
git clone <repo>
cd ai-configurator
pip install -e ".[dev]"
```

## Migration Impact

### For Users
- **No Breaking Changes**: All existing commands work
- **New Default**: `ai-config` launches TUI
- **CLI Still Available**: Explicit commands work
- **Gradual Adoption**: Can use either interface

### For Developers
- **New Dependencies**: Textual added
- **New Structure**: TUI code in separate module
- **Service Layer Unchanged**: No refactoring needed
- **Tests Updated**: Add TUI tests

## Documentation Updates

### User Documentation
- TUI usage guide
- Keyboard shortcuts reference
- Screen navigation guide
- CLI command reference (updated)

### Developer Documentation
- TUI architecture guide
- Screen development guide
- Widget creation guide
- Testing TUI components

---

**Next**: CLI command structure simplification plan
