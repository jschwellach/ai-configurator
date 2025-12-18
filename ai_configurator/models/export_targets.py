"""
Export target models and enumerations for multi-AI tool support.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field


class AIToolType(Enum):
    """Supported AI tool types for export."""
    KIRO_CLI = "kiro-cli"
    CLAUDE_CODE = "claude-code"
    # Legacy support during transition
    QCLI = "qcli"  # Deprecated


class ExportTarget(BaseModel):
    """Export target configuration for AI tools."""
    tool_type: AIToolType
    name: str = Field(..., description="Human-readable name")
    export_directory: Path = Field(..., description="Target export directory")
    schema_version: str = Field(default="v1", description="Agent schema version")
    enabled: bool = Field(default=True, description="Whether target is enabled")
    
    @property
    def is_deprecated(self) -> bool:
        """Check if this export target is deprecated."""
        return self.tool_type == AIToolType.QCLI
    
    def get_agent_path(self, agent_name: str) -> Path:
        """Get the full path for an agent export file."""
        return self.export_directory / f"{agent_name}.json"


class ExportTargetRegistry:
    """Registry of available export targets."""
    
    def __init__(self):
        self._targets: Dict[AIToolType, ExportTarget] = {}
        self._initialize_default_targets()
    
    def _initialize_default_targets(self):
        """Initialize default export targets."""
        # Kiro CLI target
        kiro_target = ExportTarget(
            tool_type=AIToolType.KIRO_CLI,
            name="Kiro CLI",
            export_directory=Path.home() / ".kiro" / "agents",
            schema_version="v1"
        )
        self._targets[AIToolType.KIRO_CLI] = kiro_target
        
        # Claude Code target (future)
        claude_target = ExportTarget(
            tool_type=AIToolType.CLAUDE_CODE,
            name="Claude Code",
            export_directory=Path.home() / ".claude" / "agents",
            schema_version="v1",
            enabled=False  # Not yet implemented
        )
        self._targets[AIToolType.CLAUDE_CODE] = claude_target
    
    def get_target(self, tool_type: AIToolType) -> Optional[ExportTarget]:
        """Get export target by tool type."""
        return self._targets.get(tool_type)
    
    def get_enabled_targets(self) -> Dict[AIToolType, ExportTarget]:
        """Get all enabled export targets."""
        return {k: v for k, v in self._targets.items() if v.enabled}


# Global registry instance
export_target_registry = ExportTargetRegistry()
