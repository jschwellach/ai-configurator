"""
Workflow Definition loader for AI Configurator Workflow Engine.
Handles loading and validating workflow YAML definitions.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging


class WorkflowDefinition:
    """Loads and validates workflow definitions from YAML files."""
    
    def __init__(self, workflow_path: Path):
        """Initialize workflow definition.
        
        Args:
            workflow_path: Path to the workflow YAML file
        """
        self.logger = logging.getLogger(__name__)
        self.workflow_path = workflow_path
        self._definition = None
        self._load_definition()
    
    def _load_definition(self) -> None:
        """Load workflow definition from YAML file."""
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_path}")
        
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                self._definition = yaml.safe_load(f)
            
            self._validate_definition()
            self.logger.debug(f"Loaded workflow definition: {self.workflow_path}")
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in workflow file {self.workflow_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading workflow definition {self.workflow_path}: {e}")
    
    def _validate_definition(self) -> None:
        """Validate the workflow definition structure."""
        if not self._definition:
            raise ValueError("Workflow definition is empty")
        
        required_fields = ['name', 'description', 'phases']
        for field in required_fields:
            if field not in self._definition:
                raise ValueError(f"Missing required field '{field}' in workflow definition")
        
        # Validate phases
        phases = self._definition['phases']
        if not isinstance(phases, list) or len(phases) == 0:
            raise ValueError("Workflow must have at least one phase")
        
        for i, phase in enumerate(phases):
            if not isinstance(phase, dict):
                raise ValueError(f"Phase {i} must be a dictionary")
            
            if 'name' not in phase:
                raise ValueError(f"Phase {i} missing required 'name' field")
            
            if 'description' not in phase:
                raise ValueError(f"Phase {i} missing required 'description' field")
    
    @property
    def name(self) -> str:
        """Get workflow name."""
        return self._definition['name']
    
    @property
    def description(self) -> str:
        """Get workflow description."""
        return self._definition['description']
    
    @property
    def version(self) -> str:
        """Get workflow version."""
        return self._definition.get('version', '1.0.0')
    
    @property
    def phases(self) -> List[Dict[str, Any]]:
        """Get workflow phases."""
        return self._definition['phases']
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get workflow metadata."""
        return self._definition.get('metadata', {})
    
    def get_phase(self, phase_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific phase by name.
        
        Args:
            phase_name: Name of the phase
            
        Returns:
            Phase definition or None if not found
        """
        for phase in self.phases:
            if phase['name'] == phase_name:
                return phase
        return None
    
    def get_phase_steps(self, phase_name: str) -> List[str]:
        """Get steps for a specific phase.
        
        Args:
            phase_name: Name of the phase
            
        Returns:
            List of step descriptions
        """
        phase = self.get_phase(phase_name)
        if phase:
            return phase.get('steps', [])
        return []
    
    def get_phase_artifacts(self, phase_name: str) -> List[str]:
        """Get expected artifacts for a specific phase.
        
        Args:
            phase_name: Name of the phase
            
        Returns:
            List of artifact names/paths
        """
        phase = self.get_phase(phase_name)
        if phase:
            return phase.get('artifacts', [])
        return []
    
    def get_next_phase(self, current_phase: str) -> Optional[str]:
        """Get the name of the next phase.
        
        Args:
            current_phase: Name of the current phase
            
        Returns:
            Name of next phase or None if current is last
        """
        phase_names = [phase['name'] for phase in self.phases]
        try:
            current_index = phase_names.index(current_phase)
            if current_index + 1 < len(phase_names):
                return phase_names[current_index + 1]
        except ValueError:
            pass
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow definition to dictionary.
        
        Returns:
            Complete workflow definition as dictionary
        """
        return self._definition.copy()


class WorkflowLoader:
    """Loads workflow definitions from profile directories."""
    
    def __init__(self):
        """Initialize workflow loader."""
        self.logger = logging.getLogger(__name__)
        self._workflow_cache = {}
    
    def load_workflows_from_profile(self, profile_path: Path) -> Dict[str, WorkflowDefinition]:
        """Load all workflows from a profile directory.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dictionary mapping workflow names to WorkflowDefinition objects
        """
        workflows = {}
        workflows_dir = profile_path / "workflows"
        
        if not workflows_dir.exists():
            self.logger.debug(f"No workflows directory found in profile: {profile_path}")
            return workflows
        
        for workflow_file in workflows_dir.glob("*.yaml"):
            try:
                workflow_def = WorkflowDefinition(workflow_file)
                workflows[workflow_def.name] = workflow_def
                self.logger.info(f"Loaded workflow: {workflow_def.name}")
                
            except Exception as e:
                self.logger.error(f"Error loading workflow from {workflow_file}: {e}")
        
        return workflows
    
    def get_workflow_by_name(self, profile_path: Path, workflow_name: str) -> Optional[WorkflowDefinition]:
        """Get a specific workflow by name from a profile.
        
        Args:
            profile_path: Path to the profile directory
            workflow_name: Name of the workflow to load
            
        Returns:
            WorkflowDefinition object or None if not found
        """
        cache_key = f"{profile_path}:{workflow_name}"
        
        if cache_key in self._workflow_cache:
            return self._workflow_cache[cache_key]
        
        workflows_dir = profile_path / "workflows"
        workflow_file = workflows_dir / f"{workflow_name}.yaml"
        
        if not workflow_file.exists():
            return None
        
        try:
            workflow_def = WorkflowDefinition(workflow_file)
            self._workflow_cache[cache_key] = workflow_def
            return workflow_def
            
        except Exception as e:
            self.logger.error(f"Error loading workflow '{workflow_name}' from {profile_path}: {e}")
            return None
