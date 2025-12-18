"""Agent management screen."""
import logging
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Footer, Button, DataTable, Static
from textual.binding import Binding

from ai_configurator.tui.screens.base import BaseScreen
from ai_configurator.services.agent_service import AgentService
from ai_configurator.services.import_export_service import ImportExportService
from ai_configurator.models import ToolType

# Set up logging
logger = logging.getLogger(__name__)


class AgentManagerScreen(BaseScreen):
    """Agent management interface."""
    
    BINDINGS = [
        Binding("n", "new_agent", "New"),
        Binding("e", "edit_agent", "Edit"),
        Binding("m", "rename_agent", "Rename"),
        Binding("d", "delete_agent", "Delete"),
        Binding("i", "import_qcli", "Import Q CLI"),
        Binding("x", "export_agent", "Export"),
        Binding("p", "export_package", "Export Package"),
        Binding("I", "import_package", "Import Package"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        from ai_configurator.tui.config import get_agents_dir
        self.agent_service = AgentService(get_agents_dir())
        self.selected_agent = None
        self.selected_tool = None
    
    def compose(self) -> ComposeResult:
        """Build screen layout."""
        yield Header()
        yield Container(
            Static("[bold cyan]Agent Management[/bold cyan]\n[dim]n=New e=Edit m=Rename d=Delete i=Import x=Export p=Export Package I=Import Package r=Refresh[/dim]", id="title"),
            DataTable(id="agent_table", classes="agent-list"),
            id="agent-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize table and load data."""
        table = self.query_one(DataTable)
        table.add_columns("Name", "Tool", "Resources", "Status")
        table.cursor_type = "row"
        table.focus()
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh agent list."""
        table = self.query_one(DataTable)
        
        # Save cursor position
        cursor_row = table.cursor_row if table.cursor_row is not None else 0
        
        table.clear()
        
        try:
            agents = self.agent_service.list_agents()
            for agent in agents:
                table.add_row(
                    agent.name,
                    agent.tool_type.value,
                    str(len(agent.config.resources)),
                    agent.health_status.value
                )
            
            # Restore cursor position or select first row
            if len(agents) > 0:
                target_row = min(cursor_row, len(agents) - 1)
                table.move_cursor(row=target_row)
                self.selected_agent = agents[target_row].name
                self.selected_tool = agents[target_row].tool_type
                
        except Exception as e:
            logger.error(f"Error loading agents: {e}", exc_info=True)
            self.show_notification(f"Error loading agents: {e}", "error")
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlight (cursor movement)."""
        try:
            table = self.query_one(DataTable)
            if event.cursor_row < table.row_count:
                row = table.get_row_at(event.cursor_row)
                self.selected_agent = str(row[0])
                # Parse tool type from string
                tool_str = str(row[1])
                self.selected_tool = ToolType(tool_str)
        except Exception as e:
            logger.error(f"Error highlighting row: {e}", exc_info=True)
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (Enter key) - open edit."""
        self.action_edit_agent()
    
    def action_new_agent(self) -> None:
        """Create new agent."""
        from textual.widgets import Input
        from textual.screen import ModalScreen
        from textual.containers import Vertical, Horizontal
        from textual.widgets import Button, Label
        
        class AgentNameInputScreen(ModalScreen):
            """Agent name input screen."""
            
            def compose(self):
                yield Vertical(
                    Label("Enter agent name:"),
                    Input(placeholder="my-agent", id="agent_name_input"),
                    Horizontal(
                        Button("Create", variant="primary", id="create_btn"),
                        Button("Cancel", variant="default", id="cancel_btn"),
                        classes="button_row"
                    ),
                    id="input_dialog"
                )
            
            def on_input_submitted(self, event: Input.Submitted):
                if event.input.id == "agent_name_input":
                    self.dismiss(event.value)
            
            def on_button_pressed(self, event: Button.Pressed):
                if event.button.id == "create_btn":
                    name_input = self.query_one("#agent_name_input", Input)
                    self.dismiss(name_input.value)
                elif event.button.id == "cancel_btn":
                    self.dismiss(None)
        
        def handle_agent_name(name: str):
            if name and name.strip():
                try:
                    agent = self.agent_service.create_agent(name.strip(), ToolType.Q_CLI)
                    if agent:
                        self.show_notification(f"Created agent: {name.strip()}", "information")
                        self.refresh_data()
                    else:
                        self.show_notification(f"Agent '{name.strip()}' already exists", "warning")
                except Exception as e:
                    logger.error(f"Error creating agent: {e}", exc_info=True)
                    self.show_notification(f"Error: {e}", "error")
        
        self.app.push_screen(AgentNameInputScreen(), handle_agent_name)
    
    def action_edit_agent(self) -> None:
        """Edit selected agent."""
        if not self.selected_agent or not self.selected_tool:
            self.show_notification("Please select an agent first", "warning")
            return
        
        try:
            agent = self.agent_service.load_agent(self.selected_agent, self.selected_tool)
            if not agent:
                self.show_notification(f"Agent '{self.selected_agent}' not found", "error")
                return
            
            # Open edit screen
            from ai_configurator.tui.screens.agent_edit import AgentEditScreen
            
            def on_edit_complete(result=None):
                """Refresh list after editing."""
                self.refresh_data()
            
            self.app.push_screen(AgentEditScreen(agent, self.agent_service), on_edit_complete)
            
        except Exception as e:
            logger.error(f"Error editing agent: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_delete_agent(self) -> None:
        """Delete selected agent."""
        if not self.selected_agent or not self.selected_tool:
            self.show_notification("Please select an agent first", "warning")
            return
        
        try:
            self.agent_service.delete_agent(self.selected_agent, self.selected_tool)
            self.show_notification(f"Deleted agent: {self.selected_agent}", "information")
            self.selected_agent = None
            self.selected_tool = None
            self.refresh_data()
        except Exception as e:
            logger.error(f"Error deleting agent: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_export_agent(self) -> None:
        """Export selected agent using multi-export service."""
        if not self.selected_agent or not self.selected_tool:
            self.show_notification("Please select an agent first", "warning")
            return
        
        try:
            agent = self.agent_service.load_agent(self.selected_agent, self.selected_tool)
            if not agent:
                self.show_notification(f"Agent '{self.selected_agent}' not found", "error")
                return
            
            # Use the new multi-export service (defaults to kiro-cli)
            success, error_msg = self.agent_service.export_agent(agent)
            if success:
                self.show_notification(f"Exported to Kiro CLI: {self.selected_agent}", "information")
            else:
                self.show_notification(f"Export failed: {error_msg}", "error")
        except Exception as e:
            logger.error(f"Error exporting agent: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_export_package(self) -> None:
        """Export selected agent as a shareable package."""
        if not self.selected_agent or not self.selected_tool:
            self.show_notification("Please select an agent first", "warning")
            return
        
        # Prompt user for export directory
        from textual.widgets import Input
        from textual.containers import Vertical
        from textual.screen import ModalScreen
        
        class ExportPathScreen(ModalScreen):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
            
            def compose(self) -> ComposeResult:
                yield Vertical(
                    Static("Enter export directory path:"),
                    Input(placeholder="/path/to/export/directory", id="export_path"),
                    Button("Export", variant="primary", id="export_btn"),
                    Button("Cancel", variant="error", id="cancel_btn"),
                )
            
            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "export_btn":
                    path_input = self.query_one("#export_path", Input)
                    self.callback(path_input.value)
                    self.app.pop_screen()
                elif event.button.id == "cancel_btn":
                    self.app.pop_screen()
        
        def export_callback(path: str) -> None:
            if not path:
                self.show_notification("Export path is required", "warning")
                return
            
            try:
                from pathlib import Path
                from ai_configurator.services.import_export_service import ImportExportService
                
                export_path = Path(path)
                if not export_path.exists():
                    self.show_notification(f"Export path does not exist: {path}", "error")
                    return
                
                import_export_service = ImportExportService(self.agent_service)
                result = import_export_service.export_agent(
                    self.selected_agent, self.selected_tool, export_path
                )
                
                if result:
                    self.show_notification(
                        f"Exported package: {self.selected_agent}\nLocation: {export_path / f'{self.selected_agent}_package'}", 
                        "information"
                    )
                else:
                    self.show_notification("Package export failed", "error")
            except Exception as e:
                logger.error(f"Error exporting agent package: {e}", exc_info=True)
                self.show_notification(f"Error: {e}", "error")
        
        self.app.push_screen(ExportPathScreen(export_callback))
    
    def action_import_package(self) -> None:
        """Import agent from a package."""
        # Prompt user for package directory
        from textual.widgets import Input
        from textual.containers import Vertical
        from textual.screen import ModalScreen
        
        class ImportPathScreen(ModalScreen):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
            
            def compose(self) -> ComposeResult:
                yield Vertical(
                    Static("Enter package directory path:"),
                    Input(placeholder="/path/to/package/directory", id="import_path"),
                    Input(placeholder="New agent name (optional)", id="agent_name"),
                    Button("Import", variant="primary", id="import_btn"),
                    Button("Cancel", variant="error", id="cancel_btn"),
                )
            
            def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "import_btn":
                    path_input = self.query_one("#import_path", Input)
                    name_input = self.query_one("#agent_name", Input)
                    self.callback(path_input.value, name_input.value)
                    self.app.pop_screen()
                elif event.button.id == "cancel_btn":
                    self.app.pop_screen()
        
        def import_callback(path: str, new_name: str) -> None:
            if not path:
                self.show_notification("Package path is required", "warning")
                return
            
            try:
                from pathlib import Path
                from ai_configurator.services.import_export_service import ImportExportService
                
                package_path = Path(path)
                if not package_path.exists():
                    self.show_notification(f"Package path does not exist: {path}", "error")
                    return
                
                import_export_service = ImportExportService(self.agent_service)
                result = import_export_service.import_agent(
                    package_path, new_name if new_name else None
                )
                
                if result:
                    agent_name, tool_type = result
                    self.show_notification(
                        f"Imported agent: {agent_name}\nTool type: {tool_type.value}", 
                        "information"
                    )
                    self.refresh_data()  # Refresh the agent list
                else:
                    self.show_notification("Package import failed", "error")
            except Exception as e:
                logger.error(f"Error importing agent package: {e}", exc_info=True)
                self.show_notification(f"Error: {e}", "error")
        
        self.app.push_screen(ImportPathScreen(import_callback))
    
    def action_import_qcli(self) -> None:
        """Import agents from Q CLI."""
        from ai_configurator.tui.screens.qcli_import import QCLIImportScreen
        self.app.push_screen(QCLIImportScreen())
    
    def action_rename_agent(self) -> None:
        """Rename selected agent."""
        if not self.selected_agent or not self.selected_tool:
            self.show_notification("Please select an agent first", "warning")
            return
        
        from textual.widgets import Input
        from textual.screen import ModalScreen
        from textual.containers import Vertical
        
        class InputScreen(ModalScreen):
            """Simple input screen."""
            def compose(self):
                yield Vertical(
                    Static(f"[bold]Rename Agent[/bold]\nCurrent: {self.app.screen.selected_agent}\nNew name:"),
                    Input(placeholder="new-name", id="name_input", value=self.app.screen.selected_agent),
                    id="input_dialog"
                )
            
            def on_input_submitted(self, event: Input.Submitted):
                self.dismiss(event.value)
        
        def handle_input(new_name):
            if not new_name or new_name == self.selected_agent:
                return
            
            self._rename_agent(new_name)
        
        self.app.push_screen(InputScreen(), handle_input)
    
    def _rename_agent(self, new_name: str) -> None:
        """Perform the rename."""
        try:
            # Load the agent
            agent = self.agent_service.load_agent(self.selected_agent, self.selected_tool)
            if not agent:
                self.show_notification(f"Agent '{self.selected_agent}' not found", "error")
                return
            
            # Check if new name already exists
            if self.agent_service.agent_exists(new_name, self.selected_tool):
                self.show_notification(f"Agent '{new_name}' already exists", "warning")
                return
            
            # Create new config with new name
            from ai_configurator.models import AgentConfig, Agent
            new_config = AgentConfig(
                name=new_name,
                description=agent.config.description,
                prompt=agent.config.prompt,
                tool_type=agent.config.tool_type,
                resources=agent.config.resources,
                mcp_servers=agent.config.mcp_servers,
                settings=agent.config.settings,
                created_at=agent.config.created_at
            )
            
            new_agent = Agent(config=new_config)
            
            # Save with new name
            if self.agent_service.update_agent(new_agent):
                # Delete old agent
                self.agent_service.delete_agent(self.selected_agent, self.selected_tool)
                self.show_notification(f"Renamed to: {new_name}", "information")
                self.selected_agent = new_name
                self.refresh_data()
            else:
                self.show_notification("Failed to rename agent", "error")
                
        except Exception as e:
            logger.error(f"Error renaming agent: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
