#!/usr/bin/env python3
"""
Engagement Manager Context Hook

This hook dynamically loads context based on the current engagement phase,
client type, and project complexity. It provides tailored guidance for
engagement managers based on the specific situation.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def get_engagement_context():
    """Get dynamic context based on engagement parameters."""
    
    # Get environment variables or use defaults
    engagement_phase = os.environ.get("ENGAGEMENT_PHASE", "planning")
    client_type = os.environ.get("CLIENT_TYPE", "enterprise")
    project_complexity = os.environ.get("PROJECT_COMPLEXITY", "medium")
    team_size = os.environ.get("TEAM_SIZE", "5-10")
    
    context_parts = []
    
    # Add header with current engagement info
    context_parts.append(f"""
# Engagement Manager Context - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Current Engagement Parameters
- **Phase**: {engagement_phase.title()}
- **Client Type**: {client_type.title()}
- **Project Complexity**: {project_complexity.title()}
- **Team Size**: {team_size}

---
""")
    
    # Phase-specific guidance
    if engagement_phase.lower() == "planning":
        context_parts.append("""
## Planning Phase Guidance

### Key Focus Areas
- **Requirements Gathering**: Conduct thorough stakeholder interviews
- **Risk Assessment**: Identify technical and business risks early
- **Resource Planning**: Ensure right skills and capacity allocation
- **Timeline Development**: Create realistic milestones with buffer time

### Critical Activities
1. Stakeholder mapping and communication plan
2. Technical architecture review and validation
3. Resource allocation and team formation
4. Risk register creation and mitigation planning

### Success Metrics
- Complete requirements documentation
- Approved technical architecture
- Signed statement of work
- Team onboarding completed
""")
    
    elif engagement_phase.lower() == "execution":
        context_parts.append("""
## Execution Phase Guidance

### Key Focus Areas
- **Progress Monitoring**: Track against milestones and KPIs
- **Quality Assurance**: Ensure deliverables meet standards
- **Stakeholder Management**: Maintain regular communication
- **Risk Mitigation**: Address issues before they escalate

### Daily Activities
1. Team standup and progress review
2. Client communication and updates
3. Risk and issue monitoring
4. Quality gate reviews

### Weekly Activities
1. Stakeholder status meetings
2. Sprint planning and reviews
3. Risk register updates
4. Team performance reviews
""")
    
    elif engagement_phase.lower() == "closure":
        context_parts.append("""
## Closure Phase Guidance

### Key Focus Areas
- **Deliverable Acceptance**: Ensure all items are completed
- **Knowledge Transfer**: Document and transfer knowledge
- **Lessons Learned**: Capture insights for future engagements
- **Relationship Maintenance**: Plan for ongoing partnership

### Critical Activities
1. Final deliverable review and acceptance
2. Comprehensive knowledge transfer sessions
3. Project retrospective and lessons learned
4. Transition planning and handover
""")
    
    # Client type specific guidance
    if client_type.lower() == "startup":
        context_parts.append("""
## Startup Client Considerations

### Communication Style
- Fast-paced, informal communication
- Direct access to decision makers
- Flexible scope and rapid iterations
- Cost-conscious decision making

### Key Success Factors
- Rapid prototyping and MVP delivery
- Scalable architecture for growth
- Cost-effective solutions
- Agile methodology adoption
""")
    
    elif client_type.lower() == "enterprise":
        context_parts.append("""
## Enterprise Client Considerations

### Communication Style
- Formal communication protocols
- Multiple stakeholder layers
- Structured approval processes
- Compliance and governance focus

### Key Success Factors
- Comprehensive documentation
- Security and compliance adherence
- Change management processes
- Executive-level reporting
""")
    
    elif client_type.lower() == "government":
        context_parts.append("""
## Government Client Considerations

### Communication Style
- Highly formal and documented
- Strict compliance requirements
- Lengthy approval processes
- Public sector accountability

### Key Success Factors
- FedRAMP and compliance adherence
- Detailed audit trails
- Security-first approach
- Transparent reporting
""")
    
    # Complexity-based guidance
    if project_complexity.lower() == "high":
        context_parts.append("""
## High Complexity Project Management

### Additional Considerations
- **Architecture Reviews**: Weekly architecture review sessions
- **Risk Management**: Daily risk assessment and mitigation
- **Quality Gates**: Strict quality checkpoints at each milestone
- **Stakeholder Alignment**: Frequent alignment sessions

### Recommended Practices
- Implement formal change control processes
- Conduct regular technical deep-dive sessions
- Maintain detailed project documentation
- Plan for extended testing and validation phases
""")
    
    # Add current priorities based on day of week
    current_day = datetime.now().strftime('%A')
    if current_day == 'Monday':
        context_parts.append("""
## Monday Focus: Week Planning
- Review previous week's progress and lessons learned
- Plan current week's priorities and activities
- Conduct team alignment and goal setting
- Update stakeholders on weekly objectives
""")
    elif current_day == 'Friday':
        context_parts.append("""
## Friday Focus: Week Wrap-up
- Review week's accomplishments and challenges
- Update project status and metrics
- Prepare weekly status report for stakeholders
- Plan for next week's activities and priorities
""")
    
    return "\n".join(context_parts)

def load_base_contexts():
    """Load base context files for engagement manager."""
    config_dir = Path(os.environ.get("AMAZONQ_CONFIG_DIR", ""))
    contexts_dir = config_dir / "contexts"
    
    base_contexts = [
        "engagement-management.md",
        "client-communication.md", 
        "project-delivery.md"
    ]
    
    context_content = []
    
    for context_file in base_contexts:
        file_path = contexts_dir / context_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                context_content.append(f"\n--- {context_file} ---\n{content}")
            except Exception as e:
                print(f"Warning: Failed to load {context_file}: {e}", file=sys.stderr)
    
    return "\n".join(context_content)

def main():
    """Main hook function."""
    try:
        # Get dynamic context
        dynamic_context = get_engagement_context()
        
        # Get base contexts
        base_contexts = load_base_contexts()
        
        # Combine all contexts
        full_context = dynamic_context + "\n\n" + base_contexts
        
        # Output the combined context
        print(full_context)
        
        return 0
        
    except Exception as e:
        print(f"Error in engagement manager context hook: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
