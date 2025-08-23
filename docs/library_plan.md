# AI Configurator Library Redesign Plan

## Executive Summary

The current library structure is over-engineered and too tightly coupled to Amazon Q CLI's agent system. We should redesign it to be **tool-agnostic** - a simple knowledge base that can be consumed by any AI tool or system, not just Amazon Q CLI.

## Current Problems

### 1. Over-Engineering for Amazon Q CLI
- **Current**: Complex `profile.yaml` files with Amazon Q-specific structure
- **Problem**: Tied to Amazon Q CLI agent format, not reusable
- **Impact**: Can't easily use contexts with other AI tools (Claude, ChatGPT, etc.)

### 2. Complex Directory Structure
- **Current**: `profile.yaml` + `contexts/` subdirectories + catalog system
- **Problem**: Unnecessary complexity for what is essentially a collection of markdown files
- **Impact**: Hard to understand, maintain, and extend

### 3. Tool-Specific Concepts
- **Current**: "Profiles", "agents", "hooks", Amazon Q-specific terminology
- **Problem**: Concepts don't translate to other AI tools
- **Impact**: Library is not portable or reusable

### 4. Artificial Separation
- **Current**: Base contexts vs profile contexts vs MCP servers
- **Problem**: All are just knowledge/context - artificial boundaries
- **Impact**: Confusing organization, hard to discover content

## Final Architecture (All Questions Answered)

### Pure Knowledge Library
```
library/
├── README.md                    # Library overview and usage
├── common/                      # Organizational knowledge (was base-contexts)
│   ├── policies.md
│   ├── security-guidelines.md
│   ├── coding-standards.md
│   └── common-abbreviations.md
├── roles/                       # Role-specific knowledge folders
│   ├── product-owner/
│   │   ├── product-owner.md     # Main role knowledge
│   │   └── additional-config.md # User-specific additions
│   ├── software-architect/
│   │   ├── software-architect.md
│   │   └── patterns.md
│   └── software-engineer/
│       ├── software-engineer.md
│       └── best-practices.md
├── domains/                     # Domain-specific knowledge
│   ├── aws-best-practices.md
│   ├── security.md
│   ├── documentation.md
│   └── project-management.md
├── tools/                       # Tool-specific knowledge
│   ├── git.md
│   ├── docker.md
│   └── terraform.md
└── workflows/                   # Process and workflow knowledge
    ├── code-review.md
    ├── incident-response.md
    └── deployment.md
```

### Tool-Specific Configurations
```
~/.config/ai-configurator/
├── library/                     # Synced copy of knowledge library
├── q-cli/                       # Amazon Q CLI specific
│   ├── agents/
│   │   ├── product-owner.json       # References library files + MCP config
│   │   ├── software-architect.json
│   │   └── software-engineer.json
│   └── mcp-servers/
│       ├── git.json             # Preserved from current system
│       └── aws.json
├── claude-code/                 # Future: Claude Projects specific
│   └── projects/
└── chatgpt/                     # Future: ChatGPT specific
    └── custom-instructions/
```

### Enhanced CLI Commands
```bash
# Library management
ai-config library list                    # List all knowledge files
ai-config library sync                    # Sync library to config directory

# Agent creation and management
ai-config create-agent --name product-owner --rules roles/product-owner/ common/policies.md --tool q-cli
ai-config update-agent --name product-owner  # Opens interactive menu for:
                                             # - Add/remove rules from library
                                             # - Add/configure MCP servers
                                             # - Modify agent settings

# Agent operations
ai-config agents list --tool q-cli        # List Q CLI agents
ai-config agents remove product-owner --tool q-cli  # Remove agent

# Collections (folder-based)
ai-config collections list               # List available role folders
ai-config collections show product-owner # Show files in role folder
```

## Implementation Questions ✅ ALL ANSWERED

[Question] Should we completely flatten the structure and remove the concept of "profiles" entirely, making it just a knowledge library that tools can consume?
[Answer] ✅ Yes, pure knowledge library with tool-specific agents in config directory

[Question] How should we handle the transition from the current Amazon Q CLI agent system? Should we keep a compatibility layer or make a clean break?
[Answer] ✅ Clean break with careful cleanup of configuration files

[Question] Should the new library structure be completely tool-agnostic, or should we have some tool-specific adapters?
[Answer] ✅ Tool-agnostic library + tool-specific configs in `~/.config/ai-configurator/`

[Question] What should we do with the current MCP server configurations?
[Answer] ✅ Part of agents in tool-specific directories

[Question] Should we keep the concept of "collections" or let users/tools compose their own combinations?
[Answer] ✅ Folder-based collections (role folders) with copies, no JSON configs

[Question] How should we handle the migration of existing users?
[Answer] ✅ No users yet, breaking changes are fine

[Question] Should the AI Configurator tool become a generic "knowledge library manager"?
[Answer] ✅ Yes, but with tool-specific functionality not stored in library

[Question] What should we do with the current base contexts concept?
[Answer] ✅ Move to `common/` folder in library

[Question] Should we maintain backward compatibility with the current CLI commands?
[Answer] ✅ No, redesign CLI for new structure

[Question] How should we handle versioning of knowledge files?
[Answer] ✅ Version entire library, role folders support versioning naturally

[Question] For collections, should we use symlinks or copies?
[Answer] ✅ **Copies** (avoid Windows/Mac symlink issues), role folders structure

[Question] Should each role file contain all knowledge in one markdown file?
[Answer] ✅ **Role folders** with main file + additional configs (see structure above)

[Question] Should tool configs reference library files or embed content?
[Answer] ✅ **Reference files** using file paths (we know library location)

[Question] Should we have enhanced agent creation commands?
[Answer] ✅ **Yes** - `create-agent` with rules selection + interactive `update-agent` menu

[Question] How should we handle the `docs/ai-dlc-prompts.md` file?
[Answer] ✅ **Manual configuration** preferred, can use as test example

[Question] For versioning with folders, how should it work?
[Answer] ✅ **Role folders** make versioning natural (product-owner-v2/ folder)

[Question] Should cleanup remove all current structure?
[Answer] ✅ **Yes**, but **preserve MCP configurations**

## Migration Strategy

### Phase 1: Library Restructure ✅ BREAKING CHANGES
1. **Backup MCP Configs**: Preserve current MCP server configurations
2. **Clean Slate**: Remove all current library structure and agent configs
3. **Create New Structure**: Implement role folders with main + additional files
4. **Move Base Contexts**: Convert to `common/` folder
5. **Create Initial Roles**: Set up product-owner, software-architect, software-engineer folders

### Phase 2: Enhanced Agent System
1. **Tool Separation**: Move Amazon Q CLI agents to `~/.config/ai-configurator/q-cli/`
2. **Reference System**: Agents reference library files via file paths
3. **MCP Integration**: Include preserved MCP configs in agent definitions
4. **Interactive CLI**: Implement `create-agent` and `update-agent` commands

### Phase 3: Multi-Tool Support
1. **Export System**: Add support for Claude Projects, ChatGPT
2. **Collection Management**: Leverage role folders as natural collections
3. **Enhanced Discovery**: Library browsing and search capabilities

## Key Benefits

1. **Tool Agnostic**: Pure knowledge library works with any AI tool
2. **Role-Focused**: Natural organization around roles with extensible folders
3. **Interactive Management**: CLI app for agent configuration
4. **Flexible Composition**: Mix and match knowledge files as needed
5. **Version-Friendly**: Role folders support natural versioning
6. **Windows Compatible**: No symlinks, just copies and references

## Implementation Details

### Agent Configuration Example
```json
{
  "$schema": "https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json",
  "name": "product-owner",
  "description": "Product Owner with organizational policies and role-specific knowledge",
  "resources": [
    "file://~/.config/ai-configurator/library/common/policies.md",
    "file://~/.config/ai-configurator/library/roles/product-owner/product-owner.md",
    "file://~/.config/ai-configurator/library/roles/product-owner/additional-config.md",
    "file://~/.config/ai-configurator/library/workflows/project-management.md"
  ],
  "tools": ["*"],
  "allowedTools": ["fs_read"],
  "mcpServers": {
    "git": {
      "command": "git-mcp-server",
      "args": []
    }
  }
}
```

### Interactive Agent Update Menu
```
ai-config update-agent --name product-owner

Product Owner Agent Configuration:
1. Add/Remove Knowledge Files
   - Current: common/policies.md, roles/product-owner/*, workflows/project-management.md
2. Configure MCP Servers
   - Current: git
3. Modify Agent Settings
   - Tools, permissions, etc.
4. Save and Deploy

Select option (1-4):
```

## Success Criteria

1. **✅ Library Independence**: Knowledge library works without ai-configurator tool
2. **✅ Multi-Tool Support**: Same knowledge works with different AI tools  
3. **✅ Simple Maintenance**: Easy to add/update knowledge files
4. **✅ Clean Migration**: Complete restructure with MCP preservation
5. **✅ Extensible**: Role folders + interactive CLI for easy expansion
6. **✅ User-Friendly**: Interactive agent management with menu system

---

**Status**: 🚀 **IMPLEMENTATION IN PROGRESS** - Feature branch: `feature/library-redesign`

**Current Phase**: Phase 1 - Library Restructure (BREAKING CHANGES)

## Implementation Progress

### ✅ Phase 1: Library Restructure (COMPLETED)
- [x] Create feature branch: `feature/library-redesign`
- [x] Backup MCP configurations
- [x] Remove current library structure
- [x] Create new library structure with role folders
- [x] Move base contexts to `common/` folder
- [x] Create initial role folders (product-owner, software-architect, software-engineer)
- [x] Create domain knowledge (AWS, security)
- [x] Create tools knowledge (Git)
- [x] Create workflows knowledge (code review)
- [x] Create comprehensive library README

### 🚀 Phase 2: Enhanced Agent System (IN PROGRESS)
- [ ] Remove old agent management system
- [ ] Create new agent management system with file references
- [ ] Implement MCP integration to agents
- [ ] Implement interactive CLI commands (`create-agent`, `update-agent`)
- [ ] Update current state documentation

### ⏳ Phase 3: Multi-Tool Support (PENDING)
- [ ] Add export system for other tools
- [ ] Implement collection management
- [ ] Add library browsing capabilities

---
