"""
Workflow State Manager for AI Configurator Workflow Engine.
Handles state persistence, transitions, and archival.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


class WorkflowStateManager:
    """Manages workflow state persistence and transitions."""
    
    def __init__(self, working_directory: Optional[Path] = None):
        """Initialize the workflow state manager.
        
        Args:
            working_directory: Directory to store state files (defaults to current directory)
        """
        self.logger = logging.getLogger(__name__)
        self.working_directory = working_directory or Path.cwd()
        self.state_directory = self.working_directory / ".ai-configurator"
        self.archived_directory = self.state_directory / "archived"
        
        # Ensure directories exist
        self.state_directory.mkdir(exist_ok=True)
        self.archived_directory.mkdir(exist_ok=True)
    
    def create_workflow_state(self, workflow_name: str, profile_id: str, 
                            workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow state.
        
        Args:
            workflow_name: Name of the workflow
            profile_id: ID of the profile containing the workflow
            workflow_definition: The workflow definition from YAML
            
        Returns:
            The created workflow state
        """
        now = datetime.now().isoformat()
        
        # Initialize phases from workflow definition
        phases = {}
        for phase in workflow_definition.get('phases', []):
            phases[phase['name']] = {
                'status': 'not_started',
                'description': phase.get('description', ''),
                'completed_steps': [],
                'artifacts': [],
                'started_at': None,
                'completed_at': None
            }
        
        # Set first phase as current
        first_phase = workflow_definition.get('phases', [{}])[0].get('name', 'unknown')
        if first_phase in phases:
            phases[first_phase]['status'] = 'in_progress'
            phases[first_phase]['started_at'] = now
        
        state = {
            'workflow_name': workflow_name,
            'profile_id': profile_id,
            'current_phase': first_phase,
            'status': 'active',
            'started_at': now,
            'last_updated': now,
            'phases': phases,
            'metadata': {
                'workflow_version': workflow_definition.get('version', '1.0.0'),
                'workflow_description': workflow_definition.get('description', ''),
                'total_phases': len(workflow_definition.get('phases', []))
            }
        }
        
        self.save_state(state)
        self.logger.info(f"Created new workflow state: {workflow_name}")
        return state
    
    def load_state(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from file.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            The workflow state or None if not found
        """
        state_file = self.state_directory / f"{workflow_name}_state.yaml"
        
        if not state_file.exists():
            return None
            
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = yaml.safe_load(f)
            
            self.logger.debug(f"Loaded workflow state: {workflow_name}")
            return state
            
        except Exception as e:
            self.logger.error(f"Error loading workflow state '{workflow_name}': {e}")
            return None
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save workflow state to file.
        
        Args:
            state: The workflow state to save
            
        Returns:
            True if successful, False otherwise
        """
        workflow_name = state.get('workflow_name')
        if not workflow_name:
            self.logger.error("Cannot save state: missing workflow_name")
            return False
            
        state_file = self.state_directory / f"{workflow_name}_state.yaml"
        
        try:
            # Update last_updated timestamp
            state['last_updated'] = datetime.now().isoformat()
            
            with open(state_file, 'w', encoding='utf-8') as f:
                yaml.dump(state, f, default_flow_style=False, indent=2)
            
            self.logger.debug(f"Saved workflow state: {workflow_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving workflow state '{workflow_name}': {e}")
            return False
    
    def update_phase_status(self, workflow_name: str, phase_name: str, 
                          status: str, completed_steps: Optional[List[str]] = None,
                          artifacts: Optional[List[str]] = None) -> bool:
        """Update the status of a workflow phase.
        
        Args:
            workflow_name: Name of the workflow
            phase_name: Name of the phase to update
            status: New status ('not_started', 'in_progress', 'completed')
            completed_steps: List of completed steps (optional)
            artifacts: List of generated artifacts (optional)
            
        Returns:
            True if successful, False otherwise
        """
        state = self.load_state(workflow_name)
        if not state:
            self.logger.error(f"Cannot update phase: workflow '{workflow_name}' not found")
            return False
        
        if phase_name not in state['phases']:
            self.logger.error(f"Phase '{phase_name}' not found in workflow '{workflow_name}'")
            return False
        
        now = datetime.now().isoformat()
        phase = state['phases'][phase_name]
        
        # Update phase status
        old_status = phase['status']
        phase['status'] = status
        
        # Update timestamps
        if old_status == 'not_started' and status == 'in_progress':
            phase['started_at'] = now
        elif status == 'completed':
            phase['completed_at'] = now
        
        # Update completed steps and artifacts
        if completed_steps is not None:
            phase['completed_steps'] = completed_steps
        if artifacts is not None:
            phase['artifacts'] = artifacts
        
        # Update current phase if this phase is now in progress
        if status == 'in_progress':
            state['current_phase'] = phase_name
        
        success = self.save_state(state)
        if success:
            self.logger.info(f"Updated phase '{phase_name}' status to '{status}' in workflow '{workflow_name}'")
        
        return success
    
    def advance_to_next_phase(self, workflow_name: str) -> Optional[str]:
        """Advance workflow to the next phase.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Name of the next phase or None if workflow is complete
        """
        state = self.load_state(workflow_name)
        if not state:
            return None
        
        current_phase = state['current_phase']
        phases = list(state['phases'].keys())
        
        try:
            current_index = phases.index(current_phase)
            
            # Mark current phase as completed
            self.update_phase_status(workflow_name, current_phase, 'completed')
            
            # Check if there's a next phase
            if current_index + 1 < len(phases):
                next_phase = phases[current_index + 1]
                self.update_phase_status(workflow_name, next_phase, 'in_progress')
                
                state['current_phase'] = next_phase
                self.save_state(state)
                
                self.logger.info(f"Advanced workflow '{workflow_name}' to phase '{next_phase}'")
                return next_phase
            else:
                # Workflow is complete
                self.complete_workflow(workflow_name)
                return None
                
        except ValueError:
            self.logger.error(f"Current phase '{current_phase}' not found in workflow '{workflow_name}'")
            return None
    
    def complete_workflow(self, workflow_name: str) -> bool:
        """Mark workflow as completed and archive it.
        
        Args:
            workflow_name: Name of the workflow to complete
            
        Returns:
            True if successful, False otherwise
        """
        state = self.load_state(workflow_name)
        if not state:
            return False
        
        # Update workflow status
        now = datetime.now().isoformat()
        state['status'] = 'completed'
        state['completed_at'] = now
        
        # Archive the completed workflow
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_filename = f"{workflow_name}_{timestamp}_completed.yaml"
        archived_path = self.archived_directory / archived_filename
        
        try:
            with open(archived_path, 'w', encoding='utf-8') as f:
                yaml.dump(state, f, default_flow_style=False, indent=2)
            
            # Remove active state file
            state_file = self.state_directory / f"{workflow_name}_state.yaml"
            if state_file.exists():
                state_file.unlink()
            
            self.logger.info(f"Completed and archived workflow: {workflow_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing workflow '{workflow_name}': {e}")
            return False
    
    def get_active_workflows(self) -> List[str]:
        """Get list of active workflow names.
        
        Returns:
            List of active workflow names
        """
        active_workflows = []
        
        for state_file in self.state_directory.glob("*_state.yaml"):
            workflow_name = state_file.stem.replace('_state', '')
            active_workflows.append(workflow_name)
        
        return active_workflows
    
    def get_workflow_summary(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get a summary of workflow progress.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Workflow summary or None if not found
        """
        state = self.load_state(workflow_name)
        if not state:
            return None
        
        total_phases = len(state['phases'])
        completed_phases = sum(1 for phase in state['phases'].values() 
                             if phase['status'] == 'completed')
        
        return {
            'workflow_name': workflow_name,
            'current_phase': state['current_phase'],
            'status': state['status'],
            'progress': f"{completed_phases}/{total_phases}",
            'started_at': state['started_at'],
            'last_updated': state['last_updated'],
            'description': state['metadata'].get('workflow_description', '')
        }
