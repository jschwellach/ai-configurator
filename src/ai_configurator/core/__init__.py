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
)
from .platform import PlatformManager
from .update_manager import UpdateManager

__all__ = [
    "ConfigurationManager",
    "ContextManager",
    "HookManager",
    "InstallationManager",
    "PlatformManager",
    "UpdateManager",
    "BackupMetadata",
    "ConfigurationState",
    "GlobalContext",
    "InstallationConfig",
    "MCPConfiguration",
    "MCPServerConfig",
    "ProfileConfig",
    "ProfileContext",
    "ValidationResult",
]
