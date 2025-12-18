"""
Multi-AI tool export service with pluggable export strategies.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..models.agent import Agent
from ..models.export_targets import AIToolType, ExportTarget, export_target_registry


class ExportStrategy(ABC):
    """Abstract base class for export strategies."""
    
    @abstractmethod
    def export_agent(self, agent: Agent, target: ExportTarget) -> tuple[bool, Optional[str]]:
        """Export agent to the target format."""
        pass


class KiroCliExportStrategy(ExportStrategy):
    """Export strategy for Kiro CLI."""
    
    def export_agent(self, agent: Agent, target: ExportTarget) -> tuple[bool, Optional[str]]:
        """Export agent to Kiro CLI format."""
        try:
            # Ensure export directory exists
            target.export_directory.mkdir(parents=True, exist_ok=True)
            
            # Convert agent to Kiro CLI format (same as Q CLI format)
            kiro_config = agent.to_q_cli_format()
            
            # Write to file
            agent_path = target.get_agent_path(agent.name)
            with open(agent_path, 'w', encoding='utf-8') as f:
                json.dump(kiro_config, f, indent=2, ensure_ascii=False)
            
            return True, None
        except Exception as e:
            return False, f"Failed to export to Kiro CLI: {e}"


class MultiExportService:
    """Service for exporting agents to multiple AI tools."""
    
    def __init__(self):
        self._strategies: Dict[AIToolType, ExportStrategy] = {
            AIToolType.KIRO_CLI: KiroCliExportStrategy(),
        }
        self._default_target = AIToolType.KIRO_CLI
    
    def export_agent(self, agent: Agent, target_type: Optional[AIToolType] = None) -> tuple[bool, Optional[str]]:
        """Export agent to specified target or default target."""
        # Use provided target or default
        if target_type is None:
            target_type = self._default_target
        
        # Get target configuration
        target = export_target_registry.get_target(target_type)
        if not target:
            return False, f"Export target not found: {target_type.value}"
        
        if not target.enabled:
            return False, f"Export target {target.name} is not enabled"
        
        # Get export strategy
        strategy = self._strategies.get(target_type)
        if not strategy:
            return False, f"No export strategy available for {target_type.value}"
        
        # Validate agent
        if not agent.validate():
            return False, f"Agent validation failed: {', '.join(agent.validation_errors)}"
        
        # Perform export
        return strategy.export_agent(agent, target)
    
    def get_available_targets(self) -> Dict[AIToolType, ExportTarget]:
        """Get available export targets."""
        return export_target_registry.get_enabled_targets()
    
    def set_default_target(self, target_type: AIToolType) -> bool:
        """Set the default export target."""
        target = export_target_registry.get_target(target_type)
        if target and target.enabled:
            self._default_target = target_type
            return True
        return False
