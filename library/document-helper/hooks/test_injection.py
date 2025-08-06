#!/usr/bin/env python3
"""
Test hook for Q CLI context injection - Proof of Concept
This hook will inject simple workflow context to test if Q CLI picks it up.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def main():
    """
    Simple test hook that injects workflow context into Q CLI.
    This is a proof of concept to test the injection mechanism.
    """
    
    # Create test workflow state
    current_time = datetime.now().isoformat()
    
    # Simple test context to inject
    workflow_context = {
        "workflow_status": "🧪 TEST INJECTION WORKING",
        "current_phase": "proof_of_concept",
        "message": "If you can see this message, the Q CLI hook injection is working!",
        "timestamp": current_time,
        "next_steps": [
            "Verify this context appears in your AI conversation",
            "Test with different messages to ensure consistent injection",
            "Proceed with full workflow engine implementation"
        ],
        "test_data": {
            "hook_location": str(Path(__file__).parent),
            "working_directory": os.getcwd(),
            "profile": "document-helper-v1"
        }
    }
    
    # Format context for AI injection
    context_message = f"""
=== WORKFLOW ENGINE TEST ===
Status: {workflow_context['workflow_status']}
Phase: {workflow_context['current_phase']}
Time: {workflow_context['timestamp']}

Message: {workflow_context['message']}

Next Steps:
{chr(10).join(f"- {step}" for step in workflow_context['next_steps'])}

Technical Details:
- Hook Location: {workflow_context['test_data']['hook_location']}
- Working Directory: {workflow_context['test_data']['working_directory']}
- Profile: {workflow_context['test_data']['profile']}

=== END WORKFLOW CONTEXT ===
"""
    
    # Output the context (this should be picked up by Q CLI)
    print(context_message)
    
    # Also create a simple state file for testing
    state_dir = Path(".ai-configurator")
    state_dir.mkdir(exist_ok=True)
    
    state_file = state_dir / "test_injection_state.yaml"
    with open(state_file, 'w') as f:
        f.write(f"""# Test Workflow State - Generated at {current_time}
workflow_name: "test_injection"
profile_id: "document-helper-v1"
current_phase: "proof_of_concept"
started_at: "{current_time}"
last_updated: "{current_time}"
status: "testing_injection"

phases:
  proof_of_concept:
    status: "active"
    description: "Testing Q CLI hook injection mechanism"
    completed_steps: ["hook_created", "context_generated"]
    next_steps: ["verify_injection", "test_consistency", "build_full_engine"]

test_results:
  hook_executed: true
  context_generated: true
  state_file_created: true
  timestamp: "{current_time}"
""")
    
    return 0

if __name__ == "__main__":
    exit(main())
