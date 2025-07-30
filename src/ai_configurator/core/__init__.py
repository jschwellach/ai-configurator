"""Core functionality for AI Configurator."""

from .config_manager import ConfigurationManager
from .context_manager import ContextManager
from .hook_manager import HookManager
from .installer import InstallationManager
from .models import (
    BackupMetadata,
    ConfigurationState,
    GlobalContext,
    InstallationConfig,
    MCPConfiguration,
    MCPServerConfig,
    ProfileConfig,
    ProfileContext,
    ValidationResult,
    EnhancedProfileConfig,
    HookConfig,
    ContextFile,
    ConfigurationError,
    ValidationReport,
)
from .platform import PlatformManager
from .update_manager import UpdateManager
from .yaml_loader import YamlConfigLoader
from .file_watcher import FileWatcher
from .profile_manager import ProfileManager
from .config_merger import ConfigurationMerger
from .markdown_processor import MarkdownProcessor

__all__ = [
    "ConfigurationManager",
    "ContextManager",
    "HookManager",
    "InstallationManager",
    "PlatformManager",
    "UpdateManager",
    "YamlConfigLoader",
    "FileWatcher",
    "ProfileManager",
    "ConfigurationMerger",
    "MarkdownProcessor",
    "BackupMetadata",
    "ConfigurationState",
    "GlobalContext",
    "InstallationConfig",
    "MCPConfiguration",
    "MCPServerConfig",
    "ProfileConfig",
    "ProfileContext",
    "ValidationResult",
    "EnhancedProfileConfig",
    "HookConfig",
    "ContextFile",
    "ConfigurationError",
    "ValidationReport",
]
