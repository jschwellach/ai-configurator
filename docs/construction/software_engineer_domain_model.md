# Domain Model - AI Configurator Enhancement

## Domain Overview

The AI Configurator domain manages knowledge libraries, AI agent configurations, and MCP server integrations. The domain is organized around four core entities that work together to provide personalized AI agent management.

## Core Domain Entities

### 1. Library
**Responsibility**: Manages knowledge files and synchronization between base and personal libraries

**Attributes:**
- `base_path: Path` - Location of base (read-only) library
- `personal_path: Path` - Location of personal (user-writable) library
- `metadata: LibraryMetadata` - Version and sync information
- `files: Dict[str, LibraryFile]` - Indexed library files

**Behaviors:**
- `sync_from_base()` - Synchronize with base library
- `detect_conflicts()` - Find conflicts between base and personal
- `resolve_conflict(conflict, resolution)` - Apply conflict resolution
- `discover_files(pattern)` - Find files matching pattern
- `get_effective_content(path)` - Get content with personal overrides

**Business Rules:**
- Personal library files override base library files
- Conflicts must be resolved before sync completion
- File discovery respects personal library precedence

### 2. Agent
**Responsibility**: Represents AI agent configurations with knowledge and tool settings

**Attributes:**
- `name: str` - Unique agent identifier
- `description: str` - Human-readable description
- `tool_type: ToolType` - Target AI tool (Q_CLI, CLAUDE, CHATGPT)
- `resources: List[ResourcePath]` - Knowledge file references
- `mcp_servers: Dict[str, MCPServerConfig]` - MCP server configurations
- `settings: AgentSettings` - Tool-specific settings
- `health_status: HealthStatus` - Agent validation status

**Behaviors:**
- `add_resource(path)` - Add knowledge file reference
- `configure_mcp_server(name, config)` - Add/update MCP server
- `validate()` - Check agent configuration validity
- `export_for_tool()` - Generate tool-specific configuration
- `update_from_library_changes()` - Refresh when library changes

**Business Rules:**
- Agent names must be unique within tool type
- Resources must reference existing library files
- MCP server configurations must be valid
- Agent must pass validation before export

### 3. MCPServer
**Responsibility**: Manages MCP server definitions and configurations

**Attributes:**
- `name: str` - Server identifier
- `description: str` - Server description
- `command: str` - Execution command
- `args: List[str]` - Command arguments
- `env: Dict[str, str]` - Environment variables
- `timeout: int` - Request timeout in milliseconds
- `category: ServerCategory` - Server functionality category
- `status: ServerStatus` - Installation/availability status

**Behaviors:**
- `install()` - Install server if needed
- `validate_config()` - Validate server configuration
- `test_connection()` - Test server connectivity
- `get_available_tools()` - List server's available tools
- `update_from_registry()` - Update from remote registry

**Business Rules:**
- Server names must be unique in registry
- Command must be executable
- Timeout must be positive
- Server must be testable before use

### 4. Configuration
**Responsibility**: Manages user preferences and system settings

**Attributes:**
- `user_preferences: UserPreferences` - User-specific settings
- `sync_settings: SyncSettings` - Library synchronization preferences
- `backup_policy: BackupPolicy` - Backup retention settings
- `tool_settings: Dict[ToolType, ToolSettings]` - Tool-specific configurations

**Behaviors:**
- `load_from_file()` - Load configuration from storage
- `save_to_file()` - Persist configuration changes
- `create_backup()` - Create configuration backup
- `restore_backup(backup_id)` - Restore from backup
- `migrate_from_legacy()` - Import from old system

**Business Rules:**
- Configuration must be valid before saving
- Backups are created before major changes
- User preferences override system defaults
- Migration preserves existing data

## Value Objects

### LibraryMetadata
```python
@dataclass(frozen=True)
class LibraryMetadata:
    version: str
    last_sync: datetime
    base_hash: str
    personal_hash: str
    conflicts: List[ConflictInfo]
    sync_status: SyncStatus
```

### ResourcePath
```python
@dataclass(frozen=True)
class ResourcePath:
    path: str
    source: LibrarySource  # BASE, PERSONAL, LOCAL
    
    def to_file_uri(self) -> str:
        return f"file://{self.path}"
```

### MCPServerConfig
```python
@dataclass
class MCPServerConfig:
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    timeout: int = 120000
    disabled: bool = False
```

### ConflictInfo
```python
@dataclass(frozen=True)
class ConflictInfo:
    file_path: str
    base_content_hash: str
    personal_content_hash: str
    conflict_type: ConflictType  # MODIFIED, DELETED, ADDED
    resolution: Optional[Resolution] = None
```

## Domain Services

### LibraryService
**Responsibility**: Orchestrates library operations and conflict resolution

**Key Operations:**
- `sync_libraries(strategy: SyncStrategy)` - Coordinate library synchronization
- `resolve_conflicts(conflicts: List[ConflictInfo])` - Handle conflict resolution
- `index_library_files()` - Build searchable file index
- `watch_for_changes()` - Monitor file system changes

### AgentService
**Responsibility**: Manages agent lifecycle and validation

**Key Operations:**
- `create_agent(spec: AgentSpec)` - Create new agent with validation
- `update_agent(name: str, updates: AgentUpdates)` - Update existing agent
- `validate_agent(agent: Agent)` - Comprehensive agent validation
- `export_agent(agent: Agent, tool: ToolType)` - Generate tool configuration

### MCPService
**Responsibility**: Manages MCP server registry and configurations

**Key Operations:**
- `discover_servers()` - Find available MCP servers
- `install_server(server: MCPServer)` - Install and configure server
- `test_server_health(server: MCPServer)` - Validate server functionality
- `sync_remote_registry()` - Update from remote server catalog

### ConfigService
**Responsibility**: Manages system configuration and preferences

**Key Operations:**
- `load_configuration()` - Load user configuration
- `save_configuration(config: Configuration)` - Persist configuration
- `create_backup()` - Create configuration backup
- `migrate_legacy_config()` - Import from previous system

## Repositories

### LibraryRepository
**Interface for library data access**

```python
class LibraryRepository(ABC):
    @abstractmethod
    def get_base_files(self) -> Dict[str, LibraryFile]: ...
    
    @abstractmethod
    def get_personal_files(self) -> Dict[str, LibraryFile]: ...
    
    @abstractmethod
    def save_personal_file(self, path: str, content: str): ...
    
    @abstractmethod
    def get_metadata(self) -> LibraryMetadata: ...
```

### AgentRepository
**Interface for agent data access**

```python
class AgentRepository(ABC):
    @abstractmethod
    def save_agent(self, agent: Agent): ...
    
    @abstractmethod
    def load_agent(self, name: str, tool: ToolType) -> Agent: ...
    
    @abstractmethod
    def list_agents(self, tool: ToolType) -> List[Agent]: ...
    
    @abstractmethod
    def delete_agent(self, name: str, tool: ToolType): ...
```

### MCPRepository
**Interface for MCP server data access**

```python
class MCPRepository(ABC):
    @abstractmethod
    def get_local_registry(self) -> Dict[str, MCPServer]: ...
    
    @abstractmethod
    def save_server(self, server: MCPServer): ...
    
    @abstractmethod
    def get_remote_catalog(self) -> Dict[str, MCPServer]: ...
    
    @abstractmethod
    def cache_remote_data(self, data: Dict[str, MCPServer]): ...
```

### ConfigRepository
**Interface for configuration data access**

```python
class ConfigRepository(ABC):
    @abstractmethod
    def load_config(self) -> Configuration: ...
    
    @abstractmethod
    def save_config(self, config: Configuration): ...
    
    @abstractmethod
    def create_backup(self) -> BackupInfo: ...
    
    @abstractmethod
    def restore_backup(self, backup_id: str): ...
```

## Domain Events

### LibraryEvents
- `LibrarySynced(base_version: str, conflicts: List[ConflictInfo])`
- `ConflictResolved(file_path: str, resolution: Resolution)`
- `PersonalFileModified(file_path: str, content_hash: str)`

### AgentEvents
- `AgentCreated(agent_name: str, tool_type: ToolType)`
- `AgentUpdated(agent_name: str, changes: Dict[str, Any])`
- `AgentValidationFailed(agent_name: str, errors: List[ValidationError])`

### MCPEvents
- `ServerInstalled(server_name: str, version: str)`
- `ServerHealthChanged(server_name: str, status: HealthStatus)`
- `RegistrySynced(server_count: int, updated_servers: List[str])`

## Business Invariants

### Library Invariants
1. Personal library files always override base library files
2. Conflicts must be resolved before sync completion
3. Library metadata must be consistent with file system state

### Agent Invariants
1. Agent names must be unique within each tool type
2. All agent resources must reference existing files
3. Agent must pass validation before being exported

### MCP Server Invariants
1. Server names must be unique in the registry
2. Server commands must be executable
3. Server configurations must be valid before use

### Configuration Invariants
1. Configuration must be valid before persistence
2. Backups are created before destructive operations
3. User preferences override system defaults

## Aggregates and Boundaries

### Library Aggregate
- **Root**: Library
- **Entities**: LibraryFile, ConflictInfo
- **Value Objects**: LibraryMetadata, ResourcePath
- **Boundary**: Library synchronization and conflict resolution

### Agent Aggregate
- **Root**: Agent
- **Entities**: None (Agent is self-contained)
- **Value Objects**: AgentSettings, ResourcePath, MCPServerConfig
- **Boundary**: Agent configuration and validation

### MCPServer Aggregate
- **Root**: MCPServer
- **Entities**: None (MCPServer is self-contained)
- **Value Objects**: ServerStatus, ServerCategory
- **Boundary**: Server management and health monitoring

### Configuration Aggregate
- **Root**: Configuration
- **Entities**: BackupInfo
- **Value Objects**: UserPreferences, SyncSettings, BackupPolicy
- **Boundary**: System configuration and backup management

## Domain Model Relationships

```
Library 1---* LibraryFile
Library 1---1 LibraryMetadata
Library 1---* ConflictInfo

Agent 1---* ResourcePath
Agent 1---* MCPServerConfig
Agent 1---1 AgentSettings

MCPServer 1---1 ServerStatus
MCPServer 1---1 ServerCategory

Configuration 1---1 UserPreferences
Configuration 1---1 SyncSettings
Configuration 1---1 BackupPolicy
Configuration 1---* BackupInfo
```

---

**Domain Model Status**: ✅ Complete and ready for implementation
**Next Step**: Begin implementing core infrastructure with TDD approach
