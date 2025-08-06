# User Stories: Workflow Engine

## Epic: Intelligent Workflow Engine
**As a user**, I want AI Configurator to guide me through complex multi-phase processes so that I can complete sophisticated tasks with AI assistance and maintain progress across sessions.

---

## Story 1: Workflow State Management
**As a user**, I want my workflow progress to be automatically tracked and persisted so that I can resume work across different sessions without losing context.

### Acceptance Criteria:
- [ ] Workflow state is stored in `./.ai-configurator/<workflow_name>_state.yaml`
- [ ] State includes current phase, completion status, artifacts, and timestamps
- [ ] State is automatically created when workflow starts
- [ ] State is updated as user progresses through phases
- [ ] Completed workflows are archived with timestamp
- [ ] Only one active workflow per profile at a time

### Technical Notes:
- State file format: YAML with phases, status, artifacts, timestamps
- Auto-create `.ai-configurator/` directory if not exists
- Handle file locking for concurrent access

---

## Story 2: Workflow Definition System
**As a profile contributor**, I want to define workflows in YAML format so that I can create structured, multi-phase processes for users.

### Acceptance Criteria:
- [ ] Workflows are defined in `library/{profile}/workflows/{workflow_name}.yaml`
- [ ] Workflow YAML includes phases, steps, prompts, and transitions
- [ ] Workflows are automatically loaded when profile is installed
- [ ] Each workflow has metadata (name, description, version)
- [ ] Workflows can define artifacts to be created in each phase
- [ ] Validation ensures workflow YAML is well-formed

### Technical Notes:
- Workflow schema with phases, steps, conditions
- Support for conditional phase transitions
- Artifact templates and generation rules

---

## Story 3: Hook-Based Workflow Execution
**As a user**, I want workflows to automatically activate and provide context when I'm working with AI so that I receive relevant guidance without manual intervention.

### Acceptance Criteria:
- [ ] Hook triggers on AI messages when profile with workflow is active
- [ ] Hook reads current workflow state from local file
- [ ] Hook injects workflow context into AI conversation
- [ ] Hook updates workflow state based on user progress
- [ ] Hook provides clear phase guidance and next steps
- [ ] Hook handles workflow completion and archival

### Technical Notes:
- Replace existing hook system entirely
- Hook integration with Q CLI context injection
- State transition logic based on user responses

---

## Story 4: Document Creation Workflow (MVP)
**As a document writer**, I want to be guided through Amazon document creation (Narrative/PRFAQ) so that I follow best practices and create high-quality documents.

### Acceptance Criteria:
- [ ] Workflow includes Planning, Creation, and Refinement phases
- [ ] Planning phase: audience definition, purpose clarification, format selection
- [ ] Creation phase: template provision, section-by-section guidance
- [ ] Refinement phase: review checklist, feedback incorporation
- [ ] Generates document artifacts in project directory
- [ ] Provides Amazon-specific templates and guidelines

### Workflow Phases:
1. **Planning**: Define audience, purpose, success criteria
2. **Creation**: Write sections using templates and guidance
3. **Refinement**: Review, edit, and finalize document

---

## Story 5: SDLC Workflow (MVP)
**As a software developer**, I want to be guided through the software development lifecycle so that I follow structured development practices and maintain project documentation.

### Acceptance Criteria:
- [ ] Workflow includes Inception, Design, Construction, Implementation phases
- [ ] Inception: user story creation and refinement
- [ ] Design: technical breakdown, architecture, NFR definition
- [ ] Construction: task breakdown and planning
- [ ] Implementation: development guidance and progress tracking
- [ ] Generates project artifacts (user_stories.md, design.md, tasks.md)

### Workflow Phases:
1. **Inception**: Write and refine user stories
2. **Design**: Create technical design and define NFRs
3. **Construction**: Break down into implementable tasks
4. **Implementation**: Execute tasks with guidance

---

## Story 6: Workflow Status and Recovery
**As a user**, I want to understand my current workflow status and recover from interruptions so that I can always know where I am in the process.

### Acceptance Criteria:
- [ ] AI clearly communicates current phase and progress
- [ ] AI provides summary of completed steps
- [ ] AI suggests next actions based on current state
- [ ] AI handles workflow recovery after interruptions
- [ ] AI offers to restart or continue existing workflows
- [ ] Completed workflows show summary and offer new workflow start

### Technical Notes:
- Context injection includes progress summary
- Recovery logic for corrupted or incomplete state
- Clear messaging for workflow transitions

---

## Technical Architecture

### File Structure:
```
library/{profile}/
├── workflows/
│   ├── {workflow_name}.yaml
│   └── templates/
│       └── {template_files}
├── hooks/
│   └── workflow_engine.py
└── contexts/
    └── {existing_contexts}

./.ai-configurator/
├── {workflow_name}_state.yaml
└── archived/
    └── {workflow_name}_{timestamp}_completed.yaml
```

### Workflow YAML Schema:
```yaml
name: "amazon-narrative"
description: "Guide for creating Amazon narrative documents"
version: "1.0.0"
phases:
  - name: "planning"
    description: "Define document scope and audience"
    steps: [...]
    artifacts: [...]
  - name: "creation"
    description: "Write document content"
    steps: [...]
    artifacts: [...]
```

### State YAML Schema:
```yaml
workflow_name: "amazon-narrative"
profile_id: "document-helper-v1"
current_phase: "planning"
started_at: "2025-08-06T10:30:00Z"
last_updated: "2025-08-06T11:15:00Z"
phases:
  planning:
    status: "in_progress"
    completed_steps: ["audience_defined"]
    artifacts: []
```

---

## Definition of Done
- [ ] All acceptance criteria met for each story
- [ ] Unit tests for workflow engine components
- [ ] Integration tests with Q CLI hooks
- [ ] Documentation updated with workflow examples
- [ ] Two working example workflows (document creation, SDLC)
- [ ] Backward compatibility maintained with existing profiles
