"""Minimal workflow state manager."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class Workflow:
    """Simple workflow state manager using YAML file."""
    
    def __init__(self, state_file: str = "./ai-workflow.yaml"):
        self.state_file = Path(state_file)
        self._state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from YAML file."""
        if not self.state_file.exists():
            return {"steps": [], "current_step": 0, "status": "ready", "created_at": datetime.now().isoformat()}
        
        with open(self.state_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def _save_state(self) -> None:
        """Save state to YAML file."""
        self._state["updated_at"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            yaml.dump(self._state, f, default_flow_style=False)
    
    def add_step(self, name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add a step to the workflow."""
        step = {"name": name, "status": "pending", "data": data or {}}
        self._state["steps"].append(step)
        self._save_state()
    
    def complete_step(self, step_index: Optional[int] = None) -> bool:
        """Mark a step as completed."""
        if step_index is None:
            step_index = self._state["current_step"]
        
        if step_index >= len(self._state["steps"]):
            return False
        
        self._state["steps"][step_index]["status"] = "completed"
        self._state["steps"][step_index]["completed_at"] = datetime.now().isoformat()
        
        if step_index == self._state["current_step"]:
            self._state["current_step"] += 1
        
        self._save_state()
        return True
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get the current step."""
        current = self._state["current_step"]
        if current < len(self._state["steps"]):
            return self._state["steps"][current]
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get workflow status."""
        total_steps = len(self._state["steps"])
        completed_steps = sum(1 for step in self._state["steps"] if step["status"] == "completed")
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "current_step": self._state["current_step"],
            "status": "completed" if completed_steps == total_steps else "in_progress" if completed_steps > 0 else "ready"
        }
    
    def reset(self) -> None:
        """Reset workflow state."""
        self._state = {
            "steps": [],
            "current_step": 0,
            "status": "ready",
            "created_at": datetime.now().isoformat()
        }
        self._save_state()


def main():