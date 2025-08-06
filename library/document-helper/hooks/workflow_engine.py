#!/usr/bin/env python3
"""
Workflow Engine Hook for AI Configurator.
Manages workflow state and provides context injection for Q CLI.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the AI Configurator package to the path
sys.path.insert(0, str(Path.home() / ".local" / "lib" / "python3.12" / "site-packages"))

try:
    from ai_configurator.core.workflow_state_manager import WorkflowStateManager
    from ai_configurator.core.workflow_definition import WorkflowLoader
except ImportError:
    # Fallback for development environment
    sys.path.insert(0, "/Users/janossch/dev/ai-configurator")
    from ai_configurator.core.workflow_state_manager import WorkflowStateManager
    from ai_configurator.core.workflow_definition import WorkflowLoader


def detect_workflow_intent(user_message: str = "") -> str:
    """Detect which workflow the user wants to start based on their message.
    
    Args:
        user_message: The user's message (if available)
        
    Returns:
        Workflow name or empty string if no workflow detected
    """
    # Simple keyword-based detection for now
    message_lower = user_message.lower()
    
    # Document creation workflows
    if any(keyword in message_lower for keyword in [
        'document', 'write', 'create', 'narrative', 'prfaq', 'pr/faq'
    ]):
        if 'narrative' in message_lower:
            return 'amazon-narrative'
        elif any(keyword in message_lower for keyword in ['prfaq', 'pr/faq', 'press release']):
            return 'prfaq'
        else:
            return 'document-creation'
    
    return ""


def get_workflow_context(state_manager: WorkflowStateManager, workflow_name: str) -> str:
    """Generate workflow context for AI injection.
    
    Args:
        state_manager: The workflow state manager
        workflow_name: Name of the active workflow
        
    Returns:
        Formatted context string for AI
    """
    state = state_manager.load_state(workflow_name)
    if not state:
        return ""
    
    current_phase = state['current_phase']
    phase_info = state['phases'].get(current_phase, {})
    
    # Calculate progress using the correct phase order from workflow definition
    # Load the workflow definition to get the correct phase order
    profile_path = Path("/Users/janossch/dev/ai-configurator/library/document-helper")
    workflow_loader = WorkflowLoader()
    workflow_def = workflow_loader.get_workflow_by_name(profile_path, workflow_name)
    
    if workflow_def:
        # Use the original phase order from the workflow definition
        phase_names = [phase['name'] for phase in workflow_def.phases]
    else:
        # Fallback to state order if workflow definition not found
        phase_names = list(state['phases'].keys())
    
    total_phases = len(phase_names)
    completed_phases = sum(1 for p in state['phases'].values() if p['status'] == 'completed')
    current_phase_num = phase_names.index(current_phase) + 1
    
    # Get phase steps
    completed_steps = phase_info.get('completed_steps', [])
    
    context = f"""
=== AI INSTRUCTIONS: WORKFLOW ACTIVE ===
IMPORTANT: You MUST start your response with the workflow status in this exact format:

[Workflow Status: {state['workflow_name']} - Phase {current_phase_num}/{total_phases}: {current_phase}]

Current Workflow Details:
- Workflow: {state['workflow_name']}
- Current Phase: {current_phase} ({current_phase_num} of {total_phases})
- Phase Description: {phase_info.get('description', 'No description')}
- Completed Phases: {completed_phases}/{total_phases}

Completed Steps in Current Phase:
{chr(10).join(f"✅ {step}" for step in completed_steps) if completed_steps else "None yet"}

AI BEHAVIOR INSTRUCTIONS:
1. ALWAYS start your response with the workflow status line above
2. Guide the user through the current phase: {current_phase}
3. Help them complete these phase objectives: {phase_info.get('description', '')}
4. When they complete steps, acknowledge progress and update them on next steps
5. Use the document creation guidelines from your context to provide specific help
6. Keep the user focused on the current phase until it's complete

Phase Started: {phase_info.get('started_at', 'Not started')}
Workflow Started: {state['started_at']}
Last Updated: {state['last_updated']}

=== END WORKFLOW CONTEXT ===
"""
    
    return context


def main():
    """Main workflow engine hook function."""
    try:
        # Initialize managers
        state_manager = WorkflowStateManager()
        workflow_loader = WorkflowLoader()
        
        # Check for active workflows
        active_workflows = state_manager.get_active_workflows()
        
        if active_workflows:
            # Use the first active workflow (we only support one for now)
            workflow_name = active_workflows[0]
            context = get_workflow_context(state_manager, workflow_name)
            print(context)
            
        else:
            # No active workflow - since user is using document-helper profile,
            # they likely want document creation help, so start the workflow
            workflow_name = "document-creation"
            
            # Try to load workflow definition
            profile_path = Path("/Users/janossch/dev/ai-configurator/library/document-helper")
            workflow_def = workflow_loader.get_workflow_by_name(profile_path, workflow_name)
            
            if workflow_def:
                # Start new workflow
                state = state_manager.create_workflow_state(
                    workflow_name, 
                    "document-helper-v1", 
                    workflow_def.to_dict()
                )
                
                context = get_workflow_context(state_manager, workflow_name)
                print(context)
            else:
                # Workflow definition not found, provide general guidance
                print(f"""
=== AI INSTRUCTIONS: WORKFLOW READY ===
IMPORTANT: You MUST start your response with:

[Workflow Status: Ready to start - No active workflow]

AI BEHAVIOR INSTRUCTIONS:
1. ALWAYS start with the status line above
2. Explain that you can guide them through structured document creation workflows
3. Ask what type of document they want to create
4. Offer these workflow options:
   - General document creation process
   - Amazon Narratives 
   - PR/FAQ documents
5. Once they choose, a workflow will automatically start

Available Workflows:
• Document Creation Process (planning → creation → refinement)
• Amazon Narratives and PR/FAQs
• Technical documentation
• User guides and specifications

=== END CONTEXT ===
""")
        
        return 0
        
    except Exception as e:
        # Fallback context in case of errors
        print(f"""
=== AI INSTRUCTIONS: WORKFLOW ENGINE ERROR ===
IMPORTANT: You MUST start your response with:

[Workflow Status: Error - Fallback mode active]

AI BEHAVIOR INSTRUCTIONS:
1. ALWAYS start with the status line above
2. Explain that there was a technical issue with the workflow engine
3. Offer basic document creation help using your context guidelines
4. Suggest they try again or ask for specific document help

Error Details: {str(e)}
Time: {datetime.now().isoformat()}

=== END CONTEXT ===
""")
        return 1


if __name__ == "__main__":
    exit(main())
