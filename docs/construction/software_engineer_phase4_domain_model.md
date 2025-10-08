# Phase 4 Domain Model - TUI Architecture

## Overview

Phase 4 introduces a dual-mode architecture with TUI (Terminal User Interface) and CLI interfaces. The domain model extends the existing Phase 1-3 architecture without modifying the core service and model layers.

## Architecture Principles

1. **Separation of Concerns**: TUI and CLI are separate presentation layers
2. **Shared Services**: Both interfaces use the same service layer
3. **No Business Logic in UI**: All business logic remains in services
4. **Reusable Components**: TUI widgets are composable and reusable
5. **Consistent Behavior**: Same operations produce same results in both modes

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Point Layer                        │
│                  main.py (Mode Router)                      │
│                                                             │
│  Detects: No args → TUI | Args → CLI                       │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │  TUI Layer     │         │  CLI Layer     │
        │  (Textual)     │         │  (Click)       │
        │                │         │                │
        │  - Screens     │         │  - Commands    │
        │  - Widgets     │         │  - Groups      │
        │  - Styles      │         │  - Output      │
        └───────┬────────┘         └───────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │   Service Layer           │
                │   (UNCHANGED)             │
                │                           │
                │  - AgentService           │
                │  - LibraryService         │
                │  - SyncService            │
                │  - FileService            │
                │  - RegistryService        │
                │  - WizardService          │
                │  - ConfigService          │
                └─────────────┬─────────────┘
                              │
                ┌─────────────▼─────────────┐
                │   Model Layer             │
                │   (UNCHANGED)             │
                │                           │
                │  - Agent                  │
                │  - Library                │
                │  - MCPServer              │
                │  - Configuration          │
                └───────────────────────────┘
```

## New Components

### 1. Entry Point Layer

#### Main Entry Point
```python
class ApplicationRouter:
    """Routes execution to TUI or CLI based on arguments."""
    
    def detect_mode(self, args: List[str]) -> Mode:
        """Determine if user wants TUI or CLI."""
        if len(args) == 0 or args[0] == 'tui':
            return Mode.TUI
        return Mode.CLI
    
    def launch_tui(self) -> None:
        """Launch TUI application."""
        app = AIConfiguratorApp()
        app.run()
    
    def launch_cli(self, args: List[str]) -> None:
        """Launch CLI with arguments."""
        cli(args)
```

**Responsibilities**:
- Detect user intent (TUI vs CLI)
- Route to appropriate interface
- Handle initialization errors

**Interactions**:
- Called by `main()` function
- Launches either TUI or CLI
- No business logic

---

### 2. TUI Layer Components

#### 2.1 TUI Application Manager

```python
class AIConfiguratorApp(App):
    """Main TUI application using Textual framework."""
    
    # Application configuration
    CSS_PATH = "styles/default.css"
    TITLE = "AI Configurator"
    
    # Key bindings
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("escape", "back", "Back"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]
    
    # Screen registry
    SCREENS = {
        "main_menu": MainMenuScreen,
        "agent_manager": AgentManagerScreen,
        "library_manager": LibraryManagerScreen,
        "mcp_manager": MCPManagerScreen,
        "settings": SettingsScreen,
        "help": HelpScreen,
        "logs": LogsScreen,
    }
    
    def on_mount(self) -> None:
        """Initialize application on startup."""
        self.push_screen("main_menu")
    
    def navigate_to(self, screen_name: str, **kwargs) -> None:
        """Navigate to a specific screen."""
        self.push_screen(screen_name, **kwargs)
    
    def show_notification(self, message: str, severity: str = "info") -> None:
        """Display notification to user."""
        self.notify(message, severity=severity)
    
    def handle_error(self, error: Exception) -> None:
        """Handle and display errors."""
        self.notify(str(error), severity="error")
```

**Responsibilities**:
- Manage application lifecycle
- Handle screen navigation
- Manage global key bindings
- Display notifications
- Handle errors

**Interactions**:
- Manages all TUI screens
- Coordinates between screens
- No direct service calls

---

#### 2.2 Base Screen Class

```python
class BaseScreen(Screen):
    """Base class for all TUI screens."""
    
    # Common bindings for all screens
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("f5", "refresh", "Refresh"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading = False
        self.error_message = None
    
    def compose(self) -> ComposeResult:
        """Build screen layout. Override in subclasses."""
        raise NotImplementedError
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh screen data. Override in subclasses."""
        pass
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh current screen data."""
        self.refresh_data()
    
    def show_loading(self, message: str = "Loading...") -> None:
        """Show loading indicator."""
        self.loading = True
        self.app.notify(message)
    
    def hide_loading(self) -> None:
        """Hide loading indicator."""
        self.loading = False
    
    def show_error(self, error: Exception) -> None:
        """Display error message."""
        self.error_message = str(error)
        self.app.notify(str(error), severity="error")
```

**Responsibilities**:
- Provide common screen functionality
- Handle standard key bindings
- Manage loading states
- Handle errors
- Provide data refresh mechanism

**Interactions**:
- Base class for all screens
- Interacts with app for navigation
- No direct service calls

---

#### 2.3 Screen Components

##### Main Menu Screen
```python
class MainMenuScreen(BaseScreen):
    """Dashboard with system overview and navigation."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            SystemStatusPanel(id="status"),
            NavigationMenu(id="nav"),
            RecentActivityPanel(id="activity"),
            id="main-container"
        )
        yield Footer()
    
    def refresh_data(self) -> None:
        """Refresh dashboard data."""
        # Get system status
        status = self.get_system_status()
        self.query_one("#status").update(status)
        
        # Get recent activity
        activity = self.get_recent_activity()
        self.query_one("#activity").update(activity)
    
    def get_system_status(self) -> SystemStatus:
        """Get system status from services."""
        # Aggregate status from multiple services
        return SystemStatus(
            agents_count=len(AgentService().list_agents()),
            library_status=LibraryService().get_status(),
            mcp_servers_count=len(RegistryService().list_installed()),
        )
```

**Responsibilities**:
- Display system overview
- Provide navigation to main sections
- Show recent activity
- Display system health

**Interactions**:
- Calls multiple services for status
- Navigates to other screens
- Updates widgets with data

---

##### Agent Manager Screen
```python
class AgentManagerScreen(BaseScreen):
    """Agent management interface."""
    
    BINDINGS = [
        Binding("n", "new_agent", "New"),
        Binding("e", "edit_agent", "Edit"),
        Binding("d", "delete_agent", "Delete"),
        Binding("x", "export_agent", "Export"),
    ]
    
    def __init__(self):
        super().__init__()
        self.agent_service = AgentService()
        self.selected_agent = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("New", id="new", variant="primary"),
                Button("Edit", id="edit"),
                Button("Delete", id="delete", variant="error"),
                Button("Export", id="export"),
                id="actions"
            ),
            AgentListWidget(id="agent_list"),
            id="agent-container"
        )
        yield Footer()
    
    def refresh_data(self) -> None:
        """Refresh agent list."""
        agents = self.agent_service.list_agents()
        self.query_one(AgentListWidget).load_agents(agents)
    
    def action_new_agent(self) -> None:
        """Create new agent."""
        self.app.push_screen("agent_create")
    
    def action_edit_agent(self) -> None:
        """Edit selected agent."""
        if self.selected_agent:
            self.app.push_screen("agent_edit", agent_name=self.selected_agent)
    
    def action_delete_agent(self) -> None:
        """Delete selected agent."""
        if self.selected_agent:
            self.show_delete_confirmation(self.selected_agent)
    
    def action_export_agent(self) -> None:
        """Export selected agent."""
        if self.selected_agent:
            self.show_export_dialog(self.selected_agent)
    
    def on_agent_selected(self, event: AgentSelected) -> None:
        """Handle agent selection."""
        self.selected_agent = event.agent_name
```

**Responsibilities**:
- Display list of agents
- Handle agent CRUD operations
- Manage agent selection
- Navigate to agent detail screens

**Interactions**:
- Uses `AgentService` for operations
- Navigates to create/edit screens
- Updates agent list widget

---

##### Library Manager Screen
```python
class LibraryManagerScreen(BaseScreen):
    """Library synchronization interface."""
    
    BINDINGS = [
        Binding("s", "sync", "Sync"),
        Binding("d", "diff", "Diff"),
        Binding("u", "update", "Update"),
        Binding("f", "files", "Files"),
    ]
    
    def __init__(self):
        super().__init__()
        self.sync_service = SyncService()
        self.library_service = LibraryService()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("Sync", id="sync", variant="primary"),
                Button("Diff", id="diff"),
                Button("Update", id="update"),
                Button("Files", id="files"),
                id="actions"
            ),
            LibraryStatusPanel(id="status"),
            SyncHistoryWidget(id="history"),
            id="library-container"
        )
        yield Footer()
    
    def refresh_data(self) -> None:
        """Refresh library status."""
        status = self.library_service.get_status()
        self.query_one(LibraryStatusPanel).update(status)
        
        history = self.sync_service.get_history()
        self.query_one(SyncHistoryWidget).update(history)
    
    def action_sync(self) -> None:
        """Start library synchronization."""
        self.show_loading("Syncing library...")
        try:
            result = self.sync_service.sync_library()
            if result.conflicts:
                self.show_conflict_resolution(result.conflicts)
            else:
                self.app.notify("Sync completed successfully")
        except Exception as e:
            self.show_error(e)
        finally:
            self.hide_loading()
            self.refresh_data()
    
    def show_conflict_resolution(self, conflicts: List[Conflict]) -> None:
        """Show conflict resolution dialog."""
        self.app.push_screen("conflict_resolution", conflicts=conflicts)
```

**Responsibilities**:
- Display library sync status
- Handle synchronization operations
- Manage conflict resolution
- Show sync history

**Interactions**:
- Uses `SyncService` for sync operations
- Uses `LibraryService` for status
- Navigates to conflict resolution screen

---

##### MCP Manager Screen
```python
class MCPManagerScreen(BaseScreen):
    """MCP server management interface."""
    
    BINDINGS = [
        Binding("b", "browse", "Browse"),
        Binding("i", "install", "Install"),
        Binding("c", "configure", "Configure"),
    ]
    
    def __init__(self):
        super().__init__()
        self.registry_service = RegistryService()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("Browse Registry", id="browse", variant="primary"),
                Button("Install", id="install"),
                Button("Configure", id="configure"),
                id="actions"
            ),
            MCPServerListWidget(id="server_list"),
            id="mcp-container"
        )
        yield Footer()
    
    def refresh_data(self) -> None:
        """Refresh MCP server list."""
        servers = self.registry_service.list_installed()
        self.query_one(MCPServerListWidget).load_servers(servers)
    
    def action_browse(self) -> None:
        """Browse MCP server registry."""
        self.app.push_screen("mcp_browser")
    
    def action_install(self) -> None:
        """Install selected servers."""
        selected = self.query_one(MCPServerListWidget).get_selected()
        if selected:
            self.install_servers(selected)
    
    def action_configure(self) -> None:
        """Configure selected server."""
        selected = self.query_one(MCPServerListWidget).get_selected_one()
        if selected:
            self.app.push_screen("mcp_configure", server_name=selected)
```

**Responsibilities**:
- Display installed MCP servers
- Handle server installation
- Manage server configuration
- Navigate to server browser

**Interactions**:
- Uses `RegistryService` for operations
- Navigates to browser/config screens
- Updates server list widget

---

#### 2.4 Widget Components

##### Agent List Widget
```python
class AgentListWidget(DataTable):
    """Widget for displaying agent list."""
    
    def on_mount(self) -> None:
        """Initialize table columns."""
        self.add_columns("Name", "Tool", "Resources", "Status")
        self.cursor_type = "row"
    
    def load_agents(self, agents: List[Agent]) -> None:
        """Load agents into table."""
        self.clear()
        for agent in agents:
            self.add_row(
                agent.name,
                agent.tool_type.value,
                str(len(agent.config.resources)),
                self.format_status(agent.health_status),
            )
    
    def format_status(self, status: HealthStatus) -> str:
        """Format status with color."""
        colors = {
            HealthStatus.HEALTHY: "[green]●[/green] Healthy",
            HealthStatus.WARNING: "[yellow]●[/yellow] Warning",
            HealthStatus.ERROR: "[red]●[/red] Error",
        }
        return colors.get(status, "Unknown")
    
    def on_row_selected(self, event: RowSelected) -> None:
        """Handle row selection."""
        agent_name = self.get_cell_at(Coordinate(event.cursor_row, 0))
        self.post_message(AgentSelected(agent_name))
```

**Responsibilities**:
- Display agents in table format
- Handle row selection
- Format data for display
- Emit selection events

**Interactions**:
- Receives agent data from screen
- Emits events to parent screen
- No direct service calls

---

##### Conflict Resolution Widget
```python
class ConflictResolutionWidget(Container):
    """Side-by-side diff view with resolution options."""
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Container(
                Static("Local Version", classes="header"),
                TextArea(id="local", read_only=True),
                classes="diff-panel"
            ),
            Container(
                Static("Remote Version", classes="header"),
                TextArea(id="remote", read_only=True),
                classes="diff-panel"
            ),
        )
        yield Horizontal(
            Button("Keep Local", id="keep_local", variant="primary"),
            Button("Use Remote", id="use_remote", variant="primary"),
            Button("Manual Edit", id="manual_edit"),
            Button("Skip", id="skip"),
            id="resolution-actions"
        )
    
    def show_conflict(self, conflict: Conflict) -> None:
        """Display conflict details."""
        self.query_one("#local").text = conflict.local_content
        self.query_one("#remote").text = conflict.remote_content
        self.current_conflict = conflict
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle resolution button press."""
        resolution = self.get_resolution(event.button.id)
        self.post_message(ConflictResolved(self.current_conflict, resolution))
    
    def get_resolution(self, button_id: str) -> Resolution:
        """Map button ID to resolution."""
        mapping = {
            "keep_local": Resolution.KEEP_LOCAL,
            "use_remote": Resolution.USE_REMOTE,
            "manual_edit": Resolution.MANUAL_EDIT,
            "skip": Resolution.SKIP,
        }
        return mapping[button_id]
```

**Responsibilities**:
- Display file differences
- Provide resolution options
- Handle user choice
- Emit resolution events

**Interactions**:
- Receives conflict data from screen
- Emits resolution events
- No direct service calls

---

##### MCP Server Browser Widget
```python
class MCPServerBrowserWidget(ListView):
    """Browsable list of MCP servers with checkboxes."""
    
    def __init__(self):
        super().__init__()
        self.selected_servers = set()
    
    def load_servers(self, servers: List[MCPServerMetadata]) -> None:
        """Load servers into list."""
        self.clear()
        for server in servers:
            item = ServerListItem(server)
            self.append(item)
    
    def on_list_item_selected(self, event: ListItem.Selected) -> None:
        """Handle server selection."""
        server_name = event.item.server.name
        if server_name in self.selected_servers:
            self.selected_servers.remove(server_name)
        else:
            self.selected_servers.add(server_name)
    
    def get_selected_servers(self) -> List[str]:
        """Get list of selected server names."""
        return list(self.selected_servers)


class ServerListItem(ListItem):
    """List item for MCP server."""
    
    def __init__(self, server: MCPServerMetadata):
        super().__init__()
        self.server = server
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Checkbox(value=False, id=f"check_{self.server.name}"),
            Static(self.server.name, classes="server-name"),
            Static(self.server.category, classes="server-category"),
            Static(f"⭐ {self.server.rating}", classes="server-rating"),
        )
```

**Responsibilities**:
- Display available servers
- Handle multi-selection
- Show server metadata
- Track selected servers

**Interactions**:
- Receives server data from screen
- Manages selection state
- No direct service calls

---

### 3. CLI Layer Components

#### 3.1 Command Groups

##### Agent Command Group
```python
@click.group()
def agent():
    """Agent management commands."""
    pass

@agent.command()
def list():
    """List all agents."""
    service = AgentService()
    agents = service.list_agents()
    
    table = Table(title="Agents")
    table.add_column("Name")
    table.add_column("Tool")
    table.add_column("Resources")
    table.add_column("Status")
    
    for agent in agents:
        table.add_row(
            agent.name,
            agent.tool_type.value,
            str(len(agent.config.resources)),
            agent.health_status.value
        )
    
    console.print(table)

@agent.command()
@click.argument('name')
@click.option('--tool', type=click.Choice(['q-cli', 'cursor', 'windsurf']))
@click.option('--interactive', is_flag=True, help='Interactive mode')
def create(name: str, tool: str, interactive: bool):
    """Create new agent."""
    service = AgentService()
    
    if interactive:
        # Use wizard service for interactive creation
        wizard = WizardService()
        result = wizard.create_agent_interactive(name)
    else:
        # Direct creation
        config = AgentConfig(name=name, tool_type=tool)
        result = service.create_agent(config)
    
    console.print(f"[green]✓[/green] Created agent: {name}")
```

**Responsibilities**:
- Parse command-line arguments
- Call appropriate services
- Format output for console
- Handle errors

**Interactions**:
- Uses services for operations
- Uses Rich for output
- No UI components

---

## Data Flow Examples

### Example 1: Create Agent via TUI

```
1. User navigates to Agent Manager
   → MainMenuScreen → AgentManagerScreen

2. User presses 'N' for new agent
   → AgentManagerScreen.action_new_agent()
   → app.push_screen("agent_create")

3. Agent Create Screen displays form
   → AgentCreateScreen.compose()
   → Shows form fields

4. User fills form and submits
   → AgentCreateScreen.on_submit()
   → Validates input

5. Screen calls service
   → AgentService.create_agent(config)
   → Service validates and saves

6. Service returns result
   → AgentCreateScreen receives result
   → Shows success message

7. Screen navigates back
   → app.pop_screen()
   → AgentManagerScreen.refresh_data()

8. User sees new agent in list
```

### Example 2: Sync Library with Conflicts (TUI)

```
1. User navigates to Library Manager
   → MainMenuScreen → LibraryManagerScreen

2. User presses 'S' for sync
   → LibraryManagerScreen.action_sync()
   → Shows loading indicator

3. Service detects conflicts
   → SyncService.sync_library()
   → Returns ConflictReport

4. Screen shows conflict resolution
   → app.push_screen("conflict_resolution", conflicts=conflicts)
   → ConflictResolutionScreen displays first conflict

5. User chooses resolution
   → ConflictResolutionWidget.on_button_pressed()
   → Emits ConflictResolved event

6. Screen applies resolution
   → ConflictResolutionScreen.on_conflict_resolved()
   → Moves to next conflict or completes

7. Service applies all resolutions
   → SyncService.apply_resolutions(resolutions)
   → Completes sync

8. Screen shows success
   → app.pop_screen()
   → LibraryManagerScreen.refresh_data()
   → Shows sync completion message
```

### Example 3: Install MCP Server (CLI)

```
1. User runs command
   $ ai-config mcp install filesystem

2. Click parses arguments
   → mcp_install(name="filesystem")

3. Handler calls service
   → RegistryService.install_server("filesystem")

4. Service downloads and configures
   → Downloads server files
   → Validates configuration
   → Saves to registry

5. Service returns result
   → InstallationResult(success=True)

6. Handler displays result
   → console.print("✓ Installed filesystem")
   → Shows installation details

7. Command exits
   → Return code 0
```

## Design Patterns

### 1. Observer Pattern (TUI)
- Screens observe widget events
- Widgets emit custom events
- Screens react to events
- Decouples widgets from screens

### 2. Command Pattern (CLI)
- Each CLI command is a function
- Commands encapsulate operations
- Easy to test independently
- Composable for scripting

### 3. Factory Pattern (Screens)
- App creates screens on demand
- Screen registry maps names to classes
- Lazy instantiation
- Easy to add new screens

### 4. Strategy Pattern (Conflict Resolution)
- Different resolution strategies
- User selects strategy
- Service applies strategy
- Easy to add new strategies

### 5. Facade Pattern (Services)
- Services provide simple interface
- Hide complex operations
- Used by both TUI and CLI
- Consistent behavior

## State Management

### Application State
```python
class AppState:
    """Global application state."""
    current_screen: str
    navigation_history: List[str]
    notifications: List[Notification]
    user_preferences: UserPreferences
```

### Screen State
```python
class ScreenState:
    """Per-screen state."""
    data: Any
    selection: Any
    filters: Dict[str, Any]
    sort_order: str
    loading: bool
    error: Optional[str]
```

## Error Handling

### TUI Error Handling
1. Catch exceptions in screen methods
2. Display error in notification
3. Log error for debugging
4. Provide recovery options
5. Don't crash application

### CLI Error Handling
1. Catch exceptions in command handlers
2. Display formatted error message
3. Log error for debugging
4. Return appropriate exit code
5. Provide helpful suggestions

## Testing Strategy

### TUI Testing
```python
async def test_agent_manager_screen():
    """Test agent manager screen."""
    app = AIConfiguratorApp()
    async with app.run_test() as pilot:
        # Navigate to agent manager
        await pilot.press("enter")
        
        # Verify screen loaded
        assert app.screen.id == "agent_manager"
        
        # Verify agents displayed
        agent_list = app.query_one(AgentListWidget)
        assert agent_list.row_count > 0
```

### CLI Testing
```python
def test_agent_list_command():
    """Test agent list command."""
    runner = CliRunner()
    result = runner.invoke(agent_list)
    
    assert result.exit_code == 0
    assert 'agents' in result.output.lower()
```

## Performance Considerations

### TUI Performance
- Lazy load data
- Virtual scrolling for large lists
- Debounce input handling
- Cache frequently accessed data
- Async operations with progress

### CLI Performance
- Fast command execution
- Minimal output for scripting
- Parallel operations where possible
- Efficient service calls

## Extensibility

### Adding New Screens
1. Create screen class extending `BaseScreen`
2. Implement `compose()` method
3. Add to `SCREENS` registry
4. Add navigation from other screens

### Adding New Widgets
1. Create widget class extending Textual widget
2. Implement `compose()` method
3. Add event handlers
4. Use in screens

### Adding New CLI Commands
1. Create command function with `@click.command()`
2. Add to appropriate command group
3. Call services for operations
4. Format output with Rich

---

## Summary

The Phase 4 domain model extends the existing architecture with:

1. **Entry Point Layer**: Routes to TUI or CLI
2. **TUI Layer**: Screens and widgets for visual interface
3. **CLI Layer**: Simplified resource-based commands
4. **Shared Services**: Both interfaces use same services
5. **Unchanged Core**: Models and services remain unchanged

This architecture provides:
- Clear separation of concerns
- Reusable components
- Consistent behavior
- Easy testing
- Future extensibility

---

**Status**: 📋 **READY FOR IMPLEMENTATION**  
**Date**: October 5, 2025  
**Version**: 1.0  
**Author**: Software Engineer
