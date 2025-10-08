# Template Creation Guide

## Overview

Templates in AI Configurator provide pre-configured agent setups for common roles and use cases. They are stored in the library system and can be customized, shared, and versioned like other knowledge resources.

## Template System Architecture

### Storage Location
- **Base Templates**: `library/templates/` (shared templates)
- **Personal Templates**: `personal/templates/` (your customizations)

### Template Discovery
Templates are discovered through the library system using the pattern `templates/**/*-{tool}.md`

### Naming Convention
Templates follow the pattern: `{role-name}-{tool-type}.md`

Examples:
- `software-engineer-q-cli.md`
- `data-analyst-claude.md`
- `system-admin-q-cli.md`

## Creating Templates

### Method 1: Copy from Existing Roles

The easiest way to create templates is to copy existing role files:

```bash
# Copy a role to templates directory
cp library/roles/software-engineer/software-engineer.md \
   library/templates/software-engineer-q-cli.md

# Copy to personal templates for customization
cp library/roles/daily-assistant/daily-assistant.md \
   personal/templates/my-assistant-q-cli.md
```

### Method 2: Create from Scratch

Create a new template file in the templates directory:

```bash
# Create new template
nano library/templates/my-custom-role-q-cli.md
```

## Template Structure

### Basic Template Format

```markdown
# Role Name

Brief description of the role and its purpose.

## Your Role

You are an experienced [role title]. You have [number] years of experience in [domain].

## Responsibilities

- Primary responsibility 1
- Primary responsibility 2
- Primary responsibility 3

## Key Skills

- Skill 1: Description
- Skill 2: Description
- Skill 3: Description

## Approach

Describe the approach this role should take when helping users.

## Tools and Technologies

List relevant tools and technologies for this role.

## Communication Style

Describe how this role should communicate with users.

## Examples

Provide examples of how this role would handle common scenarios.
```

### Advanced Template Features

#### Parameterization (Future Enhancement)
Templates can include placeholders for customization:

```markdown
# {role_name}

You are an experienced {role_title} with {experience_years} years of experience.

## Specialization

Your primary focus is on {specialization_area}.
```

#### Resource Recommendations
Include suggested knowledge resources:

```markdown
## Recommended Knowledge Resources

This role works best with the following library resources:
- `common/aws-security-best-practices.md`
- `workflows/code-review.md`
- `tools/git.md`

## Suggested MCP Servers

- `filesystem` - For file operations
- `git` - For version control
- `database` - For data operations
```

## Available Templates

### Current Templates

1. **Software Engineer** (`software-engineer-q-cli.md`)
   - Focus: Software development and implementation
   - Skills: Coding, testing, debugging, code review
   - Tools: Git, IDEs, testing frameworks

2. **Software Architect** (`software-architect-q-cli.md`)
   - Focus: System design and architecture
   - Skills: Design patterns, scalability, technology selection
   - Tools: Diagramming, documentation, analysis

3. **System Administrator** (`system-administrator-q-cli.md`)
   - Focus: Infrastructure and operations
   - Skills: Server management, monitoring, security
   - Tools: Command line, monitoring tools, automation

4. **Daily Assistant** (`daily-assistant-q-cli.md`)
   - Focus: General productivity and task management
   - Skills: Organization, communication, problem-solving
   - Tools: Productivity apps, calendars, note-taking

5. **Product Owner** (`product-owner-q-cli.md`)
   - Focus: Product management and strategy
   - Skills: Requirements gathering, prioritization, stakeholder management
   - Tools: Project management, analytics, user research

### Template Categories

Templates can be organized by:
- **Role Type**: Engineering, Management, Operations
- **Domain**: Web Development, Data Science, DevOps
- **Experience Level**: Junior, Senior, Lead
- **Tool Type**: Q CLI, Claude, ChatGPT

## Customizing Templates

### Personal Customizations

1. **Copy to Personal Library**:
   ```bash
   cp library/templates/software-engineer-q-cli.md \
      personal/templates/my-engineer-q-cli.md
   ```

2. **Edit the Template**:
   ```bash
   nano personal/templates/my-engineer-q-cli.md
   ```

3. **Use in Agent Creation**:
   The customized template will appear in the wizard alongside base templates.

### Team Customizations

For team-specific templates:

1. **Create Team Templates**:
   ```bash
   # Create team-specific versions
   cp library/templates/software-engineer-q-cli.md \
      personal/templates/frontend-engineer-q-cli.md
   
   cp library/templates/software-engineer-q-cli.md \
      personal/templates/backend-engineer-q-cli.md
   ```

2. **Customize for Team Needs**:
   - Add team-specific processes
   - Include company-specific tools
   - Reference internal documentation

3. **Share via Library Sync**:
   Team templates in personal library can be shared through the sync system.

## Template Best Practices

### Content Guidelines

1. **Clear Role Definition**:
   - Start with a clear, concise role description
   - Define scope and boundaries
   - Specify experience level expectations

2. **Actionable Responsibilities**:
   - Use specific, actionable language
   - Focus on what the role does, not just what they know
   - Include both technical and soft skills

3. **Practical Examples**:
   - Include real-world scenarios
   - Show how the role would handle common situations
   - Provide sample responses or approaches

4. **Tool Integration**:
   - Recommend relevant MCP servers
   - Suggest useful knowledge resources
   - Include tool-specific guidance

### Technical Guidelines

1. **Naming Consistency**:
   ```bash
   # Good naming
   software-engineer-q-cli.md
   data-scientist-claude.md
   devops-engineer-q-cli.md
   
   # Avoid
   SoftwareEngineer.md
   engineer_template.md
   my-template-file.md
   ```

2. **File Organization**:
   - Keep templates focused and single-purpose
   - Use consistent markdown formatting
   - Include proper headings and structure

3. **Version Control**:
   - Templates are versioned through library sync
   - Document changes in commit messages
   - Test templates before sharing

### Content Structure

#### Essential Sections
- **Role Definition**: What this role is and does
- **Responsibilities**: Key duties and expectations
- **Skills**: Required technical and soft skills
- **Approach**: How this role should work

#### Optional Sections
- **Tools**: Recommended tools and technologies
- **Communication Style**: How to interact with users
- **Examples**: Sample scenarios and responses
- **Resources**: Suggested knowledge files and MCP servers

## Using Templates

### In Wizards

Templates are automatically available in the agent creation wizard:

```bash
ai-config wizard create-agent
```

The wizard will:
1. Show available templates for the selected tool type
2. Allow preview of template content
3. Apply template configuration to the new agent

### Manual Application

Templates can also be referenced manually:

```bash
# View available templates
ai-config files scan-files temp --pattern "templates/**/*.md" --base-path library

# Copy template content for manual use
cat library/templates/software-engineer-q-cli.md
```

## Sharing Templates

### Via Library Sync

Templates in the library system are automatically shared:

1. **Base Templates**: Available to all users
2. **Personal Templates**: Synced with personal library
3. **Conflict Resolution**: Handled like other library files

### Export/Import

Templates can be shared outside the library system:

```bash
# Export template
cp personal/templates/my-template-q-cli.md /path/to/share/

# Import template
cp /path/from/share/shared-template-q-cli.md personal/templates/
```

## Advanced Template Features

### Template Inheritance (Future)

Templates could support inheritance for role hierarchies:

```markdown
# Senior Software Engineer
# Inherits: software-engineer-q-cli.md

Additional responsibilities for senior level:
- Code review and mentoring
- Architecture decisions
- Technical leadership
```

### Dynamic Content (Future)

Templates could include dynamic content based on context:

```markdown
# Context-Aware Responses

When working on {project_type} projects, focus on:
- {project_specific_practices}
- {relevant_technologies}
```

### Multi-Tool Templates (Future)

Templates could be adapted for different AI tools:

```markdown
# Universal Template Format

## For Q CLI
[Q CLI specific instructions]

## For Claude
[Claude specific instructions]

## For ChatGPT
[ChatGPT specific instructions]
```

## Troubleshooting Templates

### Template Not Appearing

1. **Check Naming Convention**:
   ```bash
   # Must end with -{tool}.md
   ls library/templates/*-q-cli.md
   ```

2. **Verify File Location**:
   ```bash
   # Should be in templates directory
   ls library/templates/
   ls personal/templates/
   ```

3. **Test Discovery**:
   ```bash
   ai-config files scan-files temp --pattern "templates/**/*-q-cli.md" --base-path library
   ```

### Template Content Issues

1. **Validate Markdown**:
   - Check for proper markdown syntax
   - Ensure headings are properly formatted
   - Verify no special characters causing issues

2. **Test Template**:
   - Create test agent using template
   - Verify all content appears correctly
   - Check for any formatting issues

### Sync Issues

Templates follow the same sync rules as other library files:

1. **Check Sync Status**:
   ```bash
   ai-config library status
   ```

2. **Resolve Conflicts**:
   ```bash
   ai-config library sync
   ```

3. **Manual Resolution**:
   Edit conflicted templates directly if needed.

---

**Next Steps**:
- Create your first custom template
- Test it in the agent creation wizard
- Share useful templates with your team
- Contribute templates back to the community
