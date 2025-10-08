# Component Model - Phase 4 TUI Architecture

## Architecture Overview

Phase 4 introduces a dual-mode architecture with TUI and CLI interfaces sharing the same service layer.

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point Layer                        │
│                  (Mode Detection)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │  TUI Interface │         │  CLI Interface │
        │   (Textual)    │         │    (Click)     │
        └───────┬────────┘         └───────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │   Application Services    │
                │   (Unchanged - Reused)    │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │      Data Models          │
                │   (Unchanged - Reused)    │
                └───────────────────────────┘
```

## New Components

### 1. TUI Application Manager

**Responsibilities**:
- Launch and manage Textual application
- Handle screen navigation and routing
- Manage application state
- Coordinate between screens and services

**Key Methods**:
```python
class AIConfiguratorApp(App):
    """Main TUI application."""
    
    def on_mount(self) -> None:
        """Initialize application on startup."""
    
    def navigate_to(self, screen_name: str) -> None:
        """Navigate to a specific screen."""
    
    def show_notification(self, message: str, severity: str) -> None:
        """Display notification to user."""
    
    def handle_error(self, error: Exception) -> None:
        """Handle and display errors."""
```

**Interactions**:
- Manages all TUI screens
- Calls application services for business logic
- Handles keyboard shortcuts and navigation
- Displays notifications and errors

### 2. TUI Screen Components

#### Base Screen
```python
class BaseScreen(Screen):
    """Base class for all TUI screens."""
    
    def compose(self) -> ComposeResult:
        """Build screen layout."""
    
    def on_key(self, event: Key) -> None:
        """Handle keyboard input."""
    
    def refresh_data(self) -> None:
        """Refresh screen data from services."""
```

#### Main Menu Screen
```python
class MainMenuScreen(BaseScreen):
    """Dashboard with system overview and navigation."""
    
    def show_system_status(self) -> None:
        """Display system status summary."""
    
    def show_recent_activity(self) -> None:
        """Display recent operations."""
    
    def navigate_to_section(self, section: str) -> None:
        """Navigate to specific management section."""
```

#### Agent Manager Screen
```python
class AgentManagerScreen(BaseScreen):
    """Agent management interface."""
    
    def list_agents(self) -> None:
        """Display agent list with details."""
    
    def create_agent(self) -> None:
        """Launch agent creation wizard."""
    
    def edit_agent(self, agent_name: str) -> None:
        """Edit agent configuration."""
    
    def export_agent(self, agent_name: str) -> None:
        """Export agent to target tool."""
```

#### Library Manager Screen
```python
class LibraryManagerScreen(BaseScreen):
    """Library synchronization interface."""
    
    def show_sync_status(self) -> None:
        """Display library sync status."""
    
    def start_sync(self) -> None:
        """Initiate library synchronization."""
    
    def resolve_conflicts(self, conflicts: List[Conflict]) -> None:
        """Interactive conflict resolution."""
    
    def show_diff(self, file_path: str) -> None:
        """Display file differences."""
```

#### MCP Manager Screen
```python
class MCPManagerScreen(BaseScreen):
    """MCP server management interface."""
    
    def browse_registry(self) -> None:
        """Display available MCP servers."""
    
    def install_servers(self, server_names: List[str]) -> None:
        """Install selected servers."""
    
    def add_to_agent(self, agent_name: str, servers: List[str]) -> None:
        """Add servers to agent configuration."""
    
    def configure_server(self, server_name: str) -> None:
        """Configure server parameters."""
```

### 3. TUI Widgets (Reusable Components)

#### Agent List Widget
```python
class AgentListWidget(DataTable):
    """Displays list of agents with status."""
    
    def load_agents(self) -> None:
        """Load and display agents."""
    
    def on_row_selected(self, row: Row) -> None:
        """Handle agent selection."""
```

#### Conflict Resolution Widget
```python
class ConflictResolutionWidget(Container):
    """Side-by-side diff view with resolution options."""
    
    def show_conflict(self, conflict: Conflict) -> None:
        """Display conflict details."""
    
    def get_resolution(self) -> Resolution:
        """Get user's resolution choice."""
```

#### Server Browser Widget
```python
class ServerBrowserWidget(ListView):
    """Browsable list of MCP servers with checkboxes."""
    
    def load_servers(self) -> None:
        """Load servers from registry."""
    
    def get_selected_servers(self) -> List[str]:
        """Get user-selected servers."""
```

#### Progress Widget
```python
class ProgressWidget(Container):
    """Progress indicator for long operations."""
    
    def start(self, operation: str) -> None:
        """Start progress indicator."""
    
    def update(self, progress: float, message: str) -> None:
        """Update progress."""
    
    def complete(self) -> None:
        """Mark operation complete."""
```

### 4. CLI Command Groups (Simplified)

#### Agent Command Group
```python
@click.group()
def agent():
    """Agent management commands."""
    pass

@agent.command()
def list():
    """List all agents."""

@agent.command()
@click.argument('name')
def create(name: str):
    """Create new agent."""

@agent.command()
@click.argument('name')
def edit(name: str):
    """Edit agent configuration."""

@agent.command()
@click.argument('name')
def export(name: str):
    """Export agent to Q CLI."""
```

#### Library Command Group
```python
@click.group()
def library():
    """Library management commands."""
    pass

@library.command()
def status():
    """Show library status."""

@library.command()
def sync():
    """Sync library with conflict resolution."""

@library.command()
@click.argument('pattern')
def files(pattern: str):
    """Discover files matching pattern."""
```

#### MCP Command Group
```python
@click.group()
def mcp():
    """MCP server management commands."""
    pass

@mcp.command()
def list():
    """List installed servers."""

@mcp.command()
def browse():
    """Browse server registry."""

@mcp.command()
@click.argument('name')
def install(name: str):
    """Install MCP server."""
```

## Component Interactions

### TUI Mode Flow

```
User Action (Keyboard/Mouse)
    │
    ▼
TUI Screen (Handle Input)
    │
    ▼
Application Service (Business Logic)
    │
    ▼
Data Models (Validation)
    │
    ▼
Data Layer (Persistence)
    │
    ▼
TUI Screen (Update Display)
    │
    ▼
User Sees Result
```

### CLI Mode Flow

```
User Command
    │
    ▼
Click Command Handler
    │
    ▼
Application Service (Business Logic)
    │
    ▼
Data Models (Validation)
    │
    ▼
Data Layer (Persistence)
    │
    ▼
Console Output (Rich)
    │
    ▼
User Sees Result
```

## Service Layer (Unchanged)

The existing service layer from Phases 1-3 remains unchanged and is reused by both interfaces:

- **LibraryService**: Library management and synchronization
- **AgentService**: Agent CRUD operations
- **ConfigService**: Configuration management
- **SyncService**: Library synchronization logic
- **FileService**: File discovery and management
- **RegistryService**: MCP server registry
- **WizardService**: Interactive setup logic (adapted for TUI)

## Data Flow Examples

### Example 1: Create Agent in TUI

```
1. User navigates to Agent Manager
   → MainMenuScreen.navigate_to("agent_manager")

2. User presses 'N' for new agent
   → AgentManagerScreen.create_agent()

3. Screen displays creation form
   → AgentCreateWidget.show_form()

4. User fills form and submits
   → AgentCreateWidget.on_submit()

5. Widget calls service
   → AgentService.create_agent(config)

6. Service validates and saves
   → Agent model validation
   → Save to disk

7. Screen refreshes list
   → AgentManagerScreen.refresh_data()

8. User sees new agent in list
```

### Example 2: Sync Library with Conflicts (TUI)

```
1. User navigates to Library Manager
   → MainMenuScreen.navigate_to("library_manager")

2. User presses 'S' for sync
   → LibraryManagerScreen.start_sync()

3. Service detects conflicts
   → SyncService.sync_library()
   → Returns list of conflicts

4. Screen shows conflict resolution UI
   → ConflictResolutionWidget.show_conflict(conflict)

5. User chooses resolution for each
   → ConflictResolutionWidget.get_resolution()

6. Service applies resolutions
   → SyncService.apply_resolutions(resolutions)

7. Screen shows sync complete
   → LibraryManagerScreen.show_success()
```

### Example 3: Install MCP Server (CLI)

```
1. User runs command
   $ ai-config mcp install filesystem

2. Click handler invoked
   → mcp_install(name="filesystem")

3. Handler calls service
   → RegistryService.install_server("filesystem")

4. Service downloads and configures
   → Download server
   → Validate configuration
   → Save to registry

5. Handler displays result
   → console.print("✓ Installed filesystem")
```

## Design Patterns

### Observer Pattern (TUI)
- Screens observe service events
- Update UI when data changes
- Real-time status updates

### Command Pattern (CLI)
- Each CLI command is a command object
- Encapsulates operation and parameters
- Easy to test and extend

### Factory Pattern (Screens)
- Screen factory creates appropriate screen
- Based on navigation target
- Handles screen lifecycle

### Strategy Pattern (Conflict Resolution)
- Different resolution strategies
- User selects strategy in UI
- Applied by service layer

## State Management

### Application State
```python
class AppState:
    """Global application state."""
    
    current_screen: str
    selected_agent: Optional[str]
    sync_in_progress: bool
    notifications: List[Notification]
```

### Screen State
```python
class ScreenState:
    """Per-screen state."""
    
    data: Any
    selection: Any
    filters: Dict[str, Any]
    sort_order: str
```

## Error Handling

### TUI Error Display
- Modal error dialogs
- Non-blocking notifications
- Error log viewer
- Contextual help

### CLI Error Display
- Rich formatted error messages
- Stack traces in debug mode
- Suggestions for fixes
- Exit codes for scripting

## Performance Considerations

### TUI Performance
- Lazy loading of data
- Virtual scrolling for large lists
- Async operations with progress
- Debounced input handling

### CLI Performance
- Fast command execution
- Minimal output for scripting
- Progress bars for long operations
- Parallel operations where possible

## Accessibility

### TUI Accessibility
- Keyboard-only navigation
- Screen reader support (where possible)
- High contrast themes
- Configurable key bindings

### CLI Accessibility
- Plain text output option
- No color mode
- Verbose mode for screen readers
- Standard exit codes

## Testing Strategy

### TUI Testing
```python
# Screen unit tests
def test_agent_manager_screen():
    screen = AgentManagerScreen()
    screen.load_agents()
    assert len(screen.agent_list) > 0

# Widget tests
def test_conflict_resolution_widget():
    widget = ConflictResolutionWidget()
    widget.show_conflict(sample_conflict)
    resolution = widget.get_resolution()
    assert resolution in [Resolution.KEEP_LOCAL, Resolution.USE_REMOTE]
```

### CLI Testing
```python
# Command tests
def test_agent_create_command():
    result = runner.invoke(agent_create, ['test-agent'])
    assert result.exit_code == 0
    assert 'Created agent' in result.output
```

## Migration Path

### Phase 1: CLI Simplification
- New CLI commands available
- Old commands work with warnings
- Documentation updated

### Phase 2: TUI Introduction
- TUI available via `ai-config tui`
- Both interfaces fully functional
- User can choose preferred mode

### Phase 3: TUI as Default
- `ai-config` launches TUI by default
- CLI requires explicit commands
- Old commands still work

### Phase 4: Deprecation
- Old commands removed in v5.0.0
- TUI is primary interface
- CLI for automation only

---

**Next**: Technology stack updates with Textual framework
