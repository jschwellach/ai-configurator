# AI Agent Manager - System Knowledge Base

VERSION: 0.2.7 (Beta)
PURPOSE: LLM-optimized system knowledge for AI agents
AUDIENCE: AI assistants, not humans

---

## SYSTEM_CORE

### Architecture
```yaml
type: tool-agnostic_knowledge_library_manager
paradigm: pure_knowledge_library + tool_specific_agents
separation: knowledge(tool-agnostic) | agents(tool-specific)
```

### Directory Structure
```
~/.config/ai-configurator/
  library/              # synced knowledge base (tool-agnostic markdown)
    base/               # shared templates, rules (5 default templates)
      roles/            # role-specific knowledge folders
      domains/          # domain expertise (aws, security)
      tools/            # tool-specific knowledge (git)
      workflows/        # process documentation (code-review)
      common/           # organizational knowledge
    personal/           # user customizations (cloned from base)
  agents/               # agent configurations (JSON)
  registry/
    servers/            # MCP server configs
  logs/
    tui.log            # application logs

~/.aws/amazonq/cli-agents/  # Q CLI agents (auto-exported)
```

### Core Components
```yaml
LibraryManager:
  purpose: manage tool-agnostic knowledge base
  operations: [sync, clone, diff, status]
  storage: ~/.config/ai-configurator/library/

AgentManager:
  purpose: create/manage tool-specific agents
  operations: [create, edit, export, list]
  storage: ~/.config/ai-configurator/agents/
  export_targets: [q-cli, claude, chatgpt]

MCPManager:
  purpose: manage Model Context Protocol servers
  operations: [browse, install, configure, paste]
  registry: ~/.config/ai-configurator/registry/servers/
```

### Data Models
```yaml
Agent:
  name: string
  tool: enum[q-cli, claude, chatgpt]
  resources: list[file_path]  # references to library files
  mcp_servers: dict[server_name, config]
  
LibraryFile:
  category: enum[base, personal]
  type: enum[role, domain, tool, workflow, common]
  path: relative_path
  
MCPServer:
  name: string
  command: string
  args: list[string]
  env: dict[string, string]
  auto_approve: list[tool_name]
```

### State Evolution
```yaml
v0.1.0:
  - initial: global contexts + profiles
  - problem: tied to Q CLI, not reusable
  
v0.2.0:
  - migration: global→agent-based architecture
  - change: removed global_context.json
  - change: agents use resources field
  
v0.2.7:
  - current: tool-agnostic library + dual-pane TUI
  - feature: base/personal library separation
  - feature: visual agent editor with checkboxes
  - feature: MCP server paste from JSON
```

### Key Principles
```yaml
tool_agnostic: knowledge works with any AI tool
file_references: agents reference, not embed
role_based: organized around roles with folders
visual_management: TUI for configuration
auto_export: changes sync to Q CLI automatically
```

---

## OPERATIONS

### Command Pattern
```
ai-config [mode] [resource] [action] [options]

modes: [tui, cli]
resources: [agent, library, mcp]
actions: context-dependent
```

### Agent Operations
```yaml
create:
  pattern: agent create <name> --tool <tool>
  effect: creates agent JSON + exports to tool
  
edit:
  pattern: agent edit <name>
  interface: dual-pane TUI (resources left, current right)
  interaction: space=toggle, ctrl+s=save
  
list:
  pattern: agent list
  output: all agents with tool type
  
export:
  pattern: agent export <name>
  targets: [~/.aws/amazonq/cli-agents/]
```

### Library Operations
```yaml
sync:
  pattern: library sync
  logic: base→personal with conflict detection
  conflicts: [keep_local, accept_remote, manual_merge]
  backup: automatic before changes
  
clone:
  pattern: library clone <file>
  effect: base→personal for customization
  
status:
  pattern: library status
  output: sync state, conflicts, file counts
  
files:
  pattern: library files <pattern>
  glob: supports **/*.md, ./docs/**/*.md
```

### MCP Operations
```yaml
browse:
  pattern: mcp browse
  output: available servers from registry
  
install:
  pattern: mcp install <name>
  effect: adds to registry, available for agents
  
paste:
  pattern: mcp paste
  input: JSON from clipboard/stdin
  formats: [mcpServers_wrapper, direct_entry]
  auto_fix: wraps direct entries
  
configure:
  pattern: mcp configure <name>
  editor: $EDITOR or system default
```

### Workflow Patterns
```yaml
new_agent:
  1. ai-config (launch TUI)
  2. navigate: Agent Management
  3. press: n (new)
  4. edit: e (dual-pane editor)
  5. select: space (toggle resources/servers)
  6. save: ctrl+s
  7. auto_export: to Q CLI
  
library_update:
  1. ai-config library sync
  2. review: conflicts if any
  3. resolve: interactive choice
  4. backup: automatic
  
mcp_add:
  1. copy: JSON from fastmcp.me
  2. ai-config mcp paste
  3. validate: auto-fix format
  4. add: to agent via TUI
```

---

## CONFIGURATION

### Agent Configuration Schema
```json
{
  "$schema": "https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json",
  "name": "agent-name",
  "description": "agent purpose",
  "resources": [
    "file://~/.config/ai-configurator/library/base/roles/role-name/role.md",
    "file://~/.config/ai-configurator/library/base/common/policies.md"
  ],
  "tools": ["*"],
  "allowedTools": ["fs_read", "fs_write"],
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["mcp-package"],
      "autoApprove": ["safe-tool"]
    }
  }
}
```

### Library Organization
```yaml
base_library:
  roles/:
    product-owner/
      - product-owner.md (main role definition)
      - additional-config.md (extensions)
    software-architect/
      - software-architect.md
      - patterns.md
    software-engineer/
      - software-engineer.md
      - best-practices.md
  
  domains/:
    - aws-best-practices.md
    - security.md
  
  tools/:
    - git.md
  
  workflows/:
    - code-review.md
  
  common/:
    - policies.md (organizational standards)
    - aws-security-best-practices.md
    - common-abbreviations.md

personal_library:
  # mirrors base structure
  # user customizations override base
```

### MCP Server Configuration
```yaml
format_1_mcpServers_wrapper:
  mcpServers:
    server-name:
      command: "npx"
      args: ["@package/server"]

format_2_direct_entry:
  # auto-wrapped by system
  server-name:
    command: "npx"
    args: ["@package/server"]

integration:
  location: agent.mcpServers field
  scope: per-agent (not global)
  management: via TUI or paste command
```

### File Pattern Syntax
```yaml
glob_patterns:
  recursive: "**/*.md"
  directory: "./docs/**/*.md"
  current: "*.txt"
  specific: "rules/**/*"

usage:
  scan: library files <pattern>
  add: library add <pattern> <agent>
  watch: library watch <pattern>
```

### Template System
```yaml
location: library/base/templates/
naming: {role-name}-{tool}.md
available:
  - software-engineer-q-cli.md
  - software-architect-q-cli.md
  - system-administrator-q-cli.md
  - daily-assistant-q-cli.md
  - product-owner-q-cli.md

usage:
  create: copy from roles/ to templates/
  customize: clone to personal/templates/
  apply: automatic in agent creation wizard
```

---

## INTERFACES

### TUI Mode
```yaml
launch: ai-config (no args)
navigation:
  main_menu: [1=agents, 2=library, 3=mcp, 4=settings]
  global: [q=quit, ?=help, esc=back, ctrl+r=refresh]

agent_editor:
  layout: dual-pane (available left, current right)
  left_pane:
    - available library files (checkboxes)
    - available MCP servers (checkboxes)
  right_pane:
    - current agent resources (view-only)
    - current agent MCP servers (view-only)
  interaction:
    - space: toggle selection
    - tab: switch panes
    - ctrl+s: save all selections
    - esc: cancel

library_management:
  actions: [s=sync, d=diff, u=update]
  display: status, file counts, conflicts

mcp_management:
  actions: [a=add, e=edit, d=delete, s=sync]
  display: installed servers, registry status
```

### CLI Mode
```yaml
invocation: ai-config <command> [args]
output_formats: [text, json]
json_flag: --format json

characteristics:
  - automation-friendly
  - scriptable
  - consistent patterns
  - explicit actions
```

### Interaction Modes
```yaml
visual:
  interface: TUI
  use_case: interactive configuration
  features: [checkboxes, navigation, real-time preview]

command:
  interface: CLI
  use_case: automation, scripting
  features: [json output, piping, batch operations]

hybrid:
  example: ai-config agent create --interactive
  behavior: CLI launches TUI for specific task
```

---

## TROUBLESHOOTING_PATTERNS

### Common Issues
```yaml
agent_not_in_qcli:
  check: ls ~/.aws/amazonq/cli-agents/
  fix: ai-config agent export <name>

library_conflicts:
  detect: ai-config library status
  resolve: ai-config library sync (interactive)
  options: [keep_local, accept_remote, manual_merge]

mcp_paste_fails:
  cause: invalid JSON format
  fix: system auto-wraps direct entries
  validate: check mcpServers wrapper

tui_not_launching:
  check: terminal size (min 80x24)
  check: color support
  fallback: ai-config <command> (CLI mode)

file_patterns_no_match:
  verify: pwd (current directory)
  test: ls <pattern> (shell glob)
  simplify: start with *.md, then expand
```

### Recovery Procedures
```yaml
corrupted_config:
  backup: cp -r ~/.config/ai-configurator ~/.config/ai-configurator.backup
  reset: rm -rf ~/.config/ai-configurator
  reinit: ai-config (recreates structure)

failed_sync:
  backup_location: ~/.config/ai-configurator/backups/
  restore: cp -r backups/backup_<timestamp>/* personal/

broken_agent:
  validate: check JSON syntax
  recreate: delete + create new
  export: ai-config agent export <name>
```

---

## METADATA

### Version History
```yaml
0.1.0:
  architecture: global contexts + profiles
  limitation: Q CLI-specific, not portable

0.2.0:
  migration: agent-based architecture
  breaking: removed global contexts
  change: resources field in agents

0.2.7:
  current: true
  features:
    - dual-pane TUI editor
    - base/personal library separation
    - MCP JSON paste with auto-fix
    - visual checkbox selection
    - auto-export to Q CLI
  status: beta
```

### Migration Context
```yaml
v0.1_to_v0.2:
  reason: Q CLI deprecated global contexts
  change: global_context.json → agent resources
  impact: all context now agent-specific

v0.2_to_v0.2.7:
  reason: usability improvements
  additions: [TUI, visual editor, library cloning]
  compatibility: backward compatible
```

### System Capabilities
```yaml
supported_tools:
  current: [q-cli]
  planned: [claude, chatgpt]

library_features:
  - tool-agnostic markdown
  - base/personal separation
  - conflict-aware sync
  - glob pattern discovery
  - file watching (planned)

agent_features:
  - visual dual-pane editor
  - multi-select with checkboxes
  - auto-export to tools
  - MCP server integration
  - template-based creation

mcp_features:
  - JSON paste from clipboard
  - auto-format correction
  - registry browsing
  - per-agent configuration
```

### Technical Stack
```yaml
language: python 3.9+
dependencies:
  - pydantic: data models
  - click: CLI framework
  - rich: TUI rendering
  - watchdog: file monitoring (planned)

packaging:
  - pip installable
  - entry_point: ai-config
  - config_dir: ~/.config/ai-configurator/
```

### Key Constraints
```yaml
context_limits:
  - Q CLI: ~100 files recommended
  - token budget: optimize for context window

file_references:
  - absolute paths with file:// prefix
  - no content embedding
  - library must remain in place

tool_integration:
  - Q CLI: auto-export to ~/.aws/amazonq/cli-agents/
  - others: manual export (planned)
```

---

## SEMANTIC_RELATIONSHIPS

### Concept Map
```
Library (knowledge base)
  ├─→ Base (shared, read-only)
  │    ├─→ Roles (job functions)
  │    ├─→ Domains (expertise areas)
  │    ├─→ Tools (technology knowledge)
  │    ├─→ Workflows (processes)
  │    └─→ Common (organizational)
  └─→ Personal (user customizations)
       └─→ mirrors base structure

Agent (tool-specific config)
  ├─→ references Library files
  ├─→ includes MCP servers
  └─→ exports to Tool

MCP Server (capabilities)
  ├─→ stored in Registry
  ├─→ configured per Agent
  └─→ provides Tools to AI

Tool (AI platform)
  ├─→ Q CLI (current)
  ├─→ Claude (planned)
  └─→ ChatGPT (planned)
```

### Operation Dependencies
```
agent.create → library.sync (ensure latest)
agent.edit → tui.launch (visual mode)
agent.export → tool.validate (schema check)
library.sync → backup.create (safety)
mcp.paste → json.validate → format.fix
```

### Data Flow
```
Source (GitHub/local)
  ↓ sync
Library (base)
  ↓ clone
Library (personal)
  ↓ reference
Agent (JSON)
  ↓ export
Tool (Q CLI/Claude/ChatGPT)
```

---

## IMPLEMENTATION_NOTES

### Critical Paths
```yaml
agent_creation:
  1. ensure library synced
  2. create agent JSON
  3. add resource references (file://)
  4. configure MCP servers
  5. export to tool directory
  6. validate tool can load

library_management:
  1. detect changes (base vs personal)
  2. identify conflicts (both modified)
  3. present options (keep/accept/merge)
  4. backup before changes
  5. apply resolution
  6. update agent references if needed

mcp_integration:
  1. receive JSON (paste/file)
  2. detect format (wrapper vs direct)
  3. normalize to mcpServers format
  4. validate schema
  5. add to agent config
  6. test server availability
```

### Edge Cases
```yaml
empty_library:
  behavior: create default structure
  templates: copy 5 default templates

no_editor:
  fallback: use nano/vi
  env_var: $EDITOR

conflicting_names:
  agents: suffix with -2, -3
  library: prompt for resolution

invalid_mcp_json:
  auto_fix: wrap direct entries
  validation: check required fields
  error: show specific issue

tool_not_installed:
  detect: check tool directory
  warn: export may not work
  continue: save agent anyway
```

### Performance Considerations
```yaml
library_size:
  recommended: ~100 files
  reason: context window limits
  optimization: selective inclusion

sync_frequency:
  manual: user-triggered
  auto: not implemented (avoid conflicts)

file_watching:
  status: planned
  use_case: auto-update on changes
  concern: performance with many files
```

---

## QUICK_REFERENCE

### Essential Commands
```
ai-config                          # launch TUI
ai-config agent create <name>      # new agent
ai-config agent edit <name>        # visual editor
ai-config library sync             # update library
ai-config mcp paste                # add MCP server
```

### File Locations
```
~/.config/ai-configurator/library/base/     # shared knowledge
~/.config/ai-configurator/library/personal/ # customizations
~/.config/ai-configurator/agents/           # agent configs
~/.aws/amazonq/cli-agents/                  # Q CLI agents
```

### Key Concepts
```
tool-agnostic: knowledge works everywhere
file-reference: agents point to files, not embed
base/personal: shared vs custom separation
dual-pane: visual editor with checkboxes
auto-export: changes sync to Q CLI
```

---

END OF SYSTEM KNOWLEDGE BASE
