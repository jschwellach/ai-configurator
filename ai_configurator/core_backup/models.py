"""Configuration data models using Pydantic."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, validator


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    command: str = Field(..., description="Command to run the MCP server")
    args: List[str] = Field(default_factory=list, description="Command line arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    disabled: bool = Field(default=False, description="Whether the server is disabled")
    auto_approve: List[str] = Field(default_factory=list, alias="autoApprove", description="Auto-approved tools")


class MCPConfiguration(BaseModel):
    """Complete MCP server configuration."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    mcp_servers: Dict[str, MCPServerConfig] = Field(alias="mcpServers")


class ProfileContext(BaseModel):
    """Profile context configuration."""
    
    paths: List[str] = Field(default_factory=list, description="Context file paths")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific hooks")


class GlobalContext(BaseModel):
    """Global context configuration."""
    
    paths: List[str] = Field(default_factory=list, description="Global context paths")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Hook configurations")


class ProfileConfig(BaseModel):
    """Configuration for a specific profile."""
    
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    context: ProfileContext = Field(default_factory=ProfileContext)
    mcp_servers: Optional[List[str]] = Field(None, description="Enabled MCP servers for this profile")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Profile-specific hooks")


class BackupMetadata(BaseModel):
    """Metadata for configuration backups."""
    
    backup_id: str = Field(..., description="Unique backup identifier")
    timestamp: str = Field(..., description="ISO timestamp of backup creation")
    description: Optional[str] = Field(None, description="Backup description")
    profile: Optional[str] = Field(None, description="Active profile at backup time")
    version: str = Field(..., description="AI Configurator version")
    platform: str = Field(..., description="Platform where backup was created")


class InstallationConfig(BaseModel):
    """Configuration for installation process."""
    
    profile: Optional[str] = Field(None, description="Profile to install")
    mcp_servers: Optional[List[str]] = Field(None, description="MCP server groups to install")
    preserve_existing: bool = Field(default=True, description="Preserve existing configurations")
    backup_before_install: bool = Field(default=True, description="Create backup before installation")
    force: bool = Field(default=False, description="Force installation even if config exists")


class ValidationResult(BaseModel):
    """Result of configuration validation."""
    
    is_valid: bool = Field(..., description="Whether the configuration is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    checked_items: Dict[str, bool] = Field(default_factory=dict, description="Items that were checked")


class ConfigurationState(BaseModel):
    """Current state of the Amazon Q CLI configuration."""
    
    amazonq_installed: bool = Field(..., description="Whether Amazon Q CLI is installed")
    amazonq_version: Optional[str] = Field(None, description="Amazon Q CLI version")
    config_dir_exists: bool = Field(..., description="Whether config directory exists")
    config_dir_path: str = Field(..., description="Path to config directory")
    active_profile: Optional[str] = Field(None, description="Currently active profile")
    installed_mcp_servers: List[str] = Field(default_factory=list, description="Installed MCP servers")
    last_backup: Optional[str] = Field(None, description="Last backup timestamp")
    ai_configurator_version: str = Field(..., description="AI Configurator version")
    platform: str = Field(..., description="Current platform")


# Enums for YAML configuration
class HookType(str, Enum):
    """Types of hooks supported in YAML configuration."""
    CONTEXT = "context"
    SCRIPT = "script"
    HYBRID = "hybrid"


class HookTrigger(str, Enum):
    """Hook trigger events."""
    ON_SESSION_START = "on_session_start"
    PER_USER_MESSAGE = "per_user_message"
    ON_FILE_CHANGE = "on_file_change"
    ON_PROFILE_SWITCH = "on_profile_switch"


class ValidationLevel(str, Enum):
    """Configuration validation levels."""
    STRICT = "strict"
    NORMAL = "normal"
    PERMISSIVE = "permissive"


# Enhanced YAML Configuration Models

class ConditionConfig(BaseModel):
    """Condition configuration for hooks."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    profile: Optional[List[str]] = Field(None, description="Profiles where this condition applies")
    platform: Optional[List[str]] = Field(None, description="Platforms where this condition applies")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables that must match")


class ScriptConfig(BaseModel):
    """Script configuration for hooks."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    working_dir: Optional[str] = Field(None, description="Working directory for script execution")
    timeout: int = Field(default=30, description="Script execution timeout in seconds")


class ContextConfig(BaseModel):
    """Context configuration for hooks and profiles."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    sources: List[str] = Field(default_factory=list, description="Context source file paths")
    tags: List[str] = Field(default_factory=list, description="Context tags for organization")
    categories: List[str] = Field(default_factory=list, description="Context categories")
    priority: int = Field(default=0, description="Context loading priority")
    cache_ttl: Optional[int] = Field(None, description="Cache time-to-live in seconds")


class HookReference(BaseModel):
    """Reference to a hook in profile configuration."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., description="Hook name")
    enabled: bool = Field(default=True, description="Whether the hook is enabled")
    timeout: Optional[int] = Field(None, description="Override timeout for this hook")
    config: Dict[str, Any] = Field(default_factory=dict, description="Hook-specific configuration")


class HookConfig(BaseModel):
    """Complete hook configuration for YAML files."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., description="Hook name")
    description: Optional[str] = Field(None, description="Hook description")
    version: str = Field(default="1.0", description="Hook configuration version")
    type: HookType = Field(default=HookType.CONTEXT, description="Hook type")
    trigger: HookTrigger = Field(..., description="Hook trigger event")
    timeout: int = Field(default=30, description="Hook execution timeout")
    enabled: bool = Field(default=True, description="Whether the hook is enabled by default")
    context: Optional[ContextConfig] = Field(None, description="Context configuration")
    script: Optional[ScriptConfig] = Field(None, description="Script configuration")
    conditions: List[ConditionConfig] = Field(default_factory=list, description="Execution conditions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('type', 'trigger')
    def validate_enums(cls, v):
        """Validate enum values."""
        return v


class ProfileSettings(BaseModel):
    """Profile-specific settings."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    auto_backup: bool = Field(default=True, description="Enable automatic backups")
    validation_level: ValidationLevel = Field(default=ValidationLevel.NORMAL, description="Validation strictness")
    hot_reload: bool = Field(default=True, description="Enable hot-reloading of configurations")
    cache_enabled: bool = Field(default=True, description="Enable configuration caching")
    max_context_size: Optional[int] = Field(None, description="Maximum context size in characters")


class EnhancedProfileConfig(BaseModel):
    """Enhanced profile configuration for YAML files."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    version: str = Field(default="1.0", description="Profile configuration version")
    contexts: List[str] = Field(default_factory=list, description="Context file paths")
    hooks: Dict[HookTrigger, List[HookReference]] = Field(default_factory=dict, description="Hook configurations by trigger")
    mcp_servers: List[str] = Field(default_factory=list, description="MCP server names to enable")
    settings: ProfileSettings = Field(default_factory=ProfileSettings, description="Profile settings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('hooks')
    def validate_hooks(cls, v):
        """Validate hook configuration structure."""
        if not isinstance(v, dict):
            return v
        
        # Convert string keys to HookTrigger enums if needed
        validated_hooks = {}
        for trigger, hook_list in v.items():
            if isinstance(trigger, str):
                try:
                    trigger_enum = HookTrigger(trigger)
                    validated_hooks[trigger_enum] = hook_list
                except ValueError:
                    # Keep original key if it's not a valid enum
                    validated_hooks[trigger] = hook_list
            else:
                validated_hooks[trigger] = hook_list
        
        return validated_hooks


class ContextFile(BaseModel):
    """Represents a context file with frontmatter metadata."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    file_path: str = Field(..., description="Path to the context file")
    content: str = Field(..., description="File content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="YAML frontmatter metadata")
    tags: List[str] = Field(default_factory=list, description="Context tags")
    categories: List[str] = Field(default_factory=list, description="Context categories")
    priority: int = Field(default=0, description="Context priority")
    last_modified: Optional[str] = Field(None, description="Last modification timestamp")


class ConfigurationError(BaseModel):
    """Represents a configuration error with context."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    file_path: str = Field(..., description="Path to the file with error")
    line_number: Optional[int] = Field(None, description="Line number where error occurred")
    column_number: Optional[int] = Field(None, description="Column number where error occurred")
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    context: Optional[str] = Field(None, description="Surrounding context")
    severity: Literal["error", "warning", "info"] = Field(default="error", description="Error severity")


class ValidationReport(BaseModel):
    """Comprehensive validation report for configurations."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    is_valid: bool = Field(..., description="Overall validation status")
    errors: List[ConfigurationError] = Field(default_factory=list, description="Validation errors")
    warnings: List[ConfigurationError] = Field(default_factory=list, description="Validation warnings")
    info: List[ConfigurationError] = Field(default_factory=list, description="Informational messages")
    files_checked: List[str] = Field(default_factory=list, description="Files that were validated")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")


class MigrationResult(BaseModel):
    """Result of configuration migration from JSON to YAML."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    success: bool = Field(..., description="Whether migration was successful")
    migrated_files: List[str] = Field(default_factory=list, description="Successfully migrated files")
    failed_files: List[str] = Field(default_factory=list, description="Files that failed to migrate")
    backup_path: Optional[str] = Field(None, description="Path to backup directory")
    errors: List[ConfigurationError] = Field(default_factory=list, description="Migration errors")
    warnings: List[ConfigurationError] = Field(default_factory=list, description="Migration warnings")


# Installed Configuration Tracking Models

class InstallationStatus(str, Enum):
    """Status of an installed configuration."""
    INSTALLED = "installed"
    OUTDATED = "outdated"
    BROKEN = "broken"
    PENDING_UPDATE = "pending_update"


class InstalledConfigMetadata(BaseModel):
    """Metadata for an installed configuration."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    config_id: str = Field(..., description="Unique configuration identifier")
    name: str = Field(..., description="Configuration name")
    version: str = Field(..., description="Installed version")
    config_type: str = Field(..., description="Type of configuration (context, profile, hook, mcp-server)")
    installation_date: str = Field(..., description="ISO timestamp of installation")
    source_path: str = Field(..., description="Original source path in library")
    target_path: str = Field(..., description="Installation target path")
    dependencies: List[str] = Field(default_factory=list, description="List of dependency config IDs")
    installed_by: str = Field(default="manual", description="How it was installed (manual, dependency, bundle)")
    status: InstallationStatus = Field(default=InstallationStatus.INSTALLED, description="Current status")
    checksum: Optional[str] = Field(None, description="File checksum for integrity checking")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class InstallationManifest(BaseModel):
    """Manifest tracking all installed configurations."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    version: str = Field(default="1.0", description="Manifest format version")
    created_date: str = Field(..., description="ISO timestamp of manifest creation")
    last_updated: str = Field(..., description="ISO timestamp of last update")
    ai_configurator_version: str = Field(..., description="AI Configurator version used")
    platform: str = Field(..., description="Platform where configurations are installed")
    target_directory: str = Field(..., description="Base installation directory")
    configurations: Dict[str, InstalledConfigMetadata] = Field(default_factory=dict, description="Installed configurations by ID")
    installation_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of installation operations")


class InstallationOperation(BaseModel):
    """Record of an installation operation."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: Literal["install", "update", "remove", "rollback"] = Field(..., description="Type of operation")
    timestamp: str = Field(..., description="ISO timestamp of operation")
    config_ids: List[str] = Field(..., description="Configuration IDs affected")
    success: bool = Field(..., description="Whether operation was successful")
    error_message: Optional[str] = Field(None, description="Error message if operation failed")
    duration_seconds: Optional[float] = Field(None, description="Operation duration in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional operation metadata")


class ConfigurationStatus(BaseModel):
    """Status information for a configuration."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    config_id: str = Field(..., description="Configuration identifier")
    is_installed: bool = Field(..., description="Whether configuration is installed")
    installed_version: Optional[str] = Field(None, description="Currently installed version")
    available_version: Optional[str] = Field(None, description="Latest available version")
    status: InstallationStatus = Field(..., description="Current status")
    needs_update: bool = Field(default=False, description="Whether an update is available")
    has_conflicts: bool = Field(default=False, description="Whether there are dependency conflicts")
    last_checked: str = Field(..., description="ISO timestamp of last status check")


# Type aliases for convenience
ConfigDict = Dict[str, Any]
PathLike = Union[str, Path]
YamlConfigDict = Dict[str, Any]

# AI Configuration Library Profile Models

from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class Profile:
    """Represents a profile configuration with metadata and installation targets."""
    name: str
    description: str
    version: str
    author: str
    category: str
    tags: List[str]
    contexts: List[str]
    hooks: List[str]
    targets: Dict[str, Dict[str, str]]
    dependencies: Optional[List[str]] = None

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'Profile':
        """Create Profile instance from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(
            name=data['name'],
            description=data['description'],
            version=data['version'],
            author=data['author'],
            category=data['category'],
            tags=data['tags'],
            contexts=data['contexts'],
            hooks=data['hooks'],
            targets=data['targets'],
            dependencies=data.get('dependencies')
        )

    def to_dict(self) -> Dict:
        """Convert Profile to dictionary for serialization."""
        result = {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'category': self.category,
            'tags': self.tags,
            'contexts': self.contexts,
            'hooks': self.hooks,
            'targets': self.targets
        }
        if self.dependencies:
            result['dependencies'] = self.dependencies
        return result


@dataclass
class InstalledProfile:
    """Represents an installed profile with tracking information."""
    name: str
    version: str
    installed_date: datetime
    target: str
    files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert InstalledProfile to dictionary for serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'installed_date': self.installed_date.isoformat(),
            'target': self.target,
            'files': self.files
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InstalledProfile':
        """Create InstalledProfile from dictionary."""
        return cls(
            name=data['name'],
            version=data['version'],
            installed_date=datetime.fromisoformat(data['installed_date']),
            target=data['target'],
            files=data.get('files', [])
        )


@dataclass
class ProfileInfo:
    """Extended profile information including file paths and status."""
    profile: Profile
    profile_path: Path
    contexts_available: List[str] = field(default_factory=list)
    hooks_available: List[str] = field(default_factory=list)
    is_installed: bool = False
    installed_version: Optional[str] = None

    def has_updates_available(self) -> bool:
        """Check if profile has updates available."""
        if not self.is_installed or not self.installed_version:
            return False
        return self.profile.version != self.installed_version