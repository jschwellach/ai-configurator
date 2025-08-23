# AI Configurator Migration to Agent-Based Architecture

## Executive Summary

Based on the Amazon Q Developer CLI documentation, the context management system has fundamentally changed from a global context approach to an agent-based architecture. This requires significant changes to our AI Configurator implementation.

## Key Changes in Amazon Q Developer CLI

### 1. Context Management Evolution

- **Old System**: Global contexts in `~/.aws/amazonq/contexts/` and `global_context.json`
- **New System**: Agent-based context through `resources` field in agent configuration files
- **Impact**: Global contexts are no longer supported; all context must be agent-specific

### 2. Agent Configuration Structure

- **Location**: `~/.aws/amazonq/cli-agents/`
- **Format**: JSON files with specific schema
- **Context**: Defined via `resources` array with `file://` prefixes
- **Tools**: Configurable tool access and permissions

## Required Changes to AI Configurator

### 1. Remove Global Context Support

**Current Implementation Issues:**

- Our `install_global_contexts()` method creates `global_context.json` which is no longer used
- Global contexts directory `~/.aws/amazonq/global-contexts/` is not recognized by new CLI
- The concept of "global contexts applied to all profiles" doesn't exist in agent architecture

**Required Actions:**

- [ ] Remove `install_global_contexts()` method from ProfileInstaller
- [ ] Remove `remove_global_contexts()` method from ProfileInstaller
- [ ] Update catalog schema to remove `global_contexts` field
- [ ] Remove global contexts from library structure

[Question] Should we completely remove global contexts or convert them to a "base agent" that other agents can inherit from?
[Answer] Yes I think this is a good Idea, we can still use a "global" context or a base context file that we load within each agent though. For example if I want to always enforce the usage of git, I could write it there and each agent will just use it. So the logic will move into our ai-configurator for "global" contexts instead of Amazon Q Dev CLI. Does that make sense?

### 2. Update Agent Configuration Generation

**Current Implementation Issues:**

- Our `AgentConfig` class includes deprecated fields like `useLegacyMcpJson`
- We're not properly handling the new agent schema requirements
- Missing proper tool configuration and permissions

**Required Actions:**

- [ ] Update `AgentConfig` schema to match latest Amazon Q CLI agent format
- [ ] Remove deprecated fields (`useLegacyMcpJson`, etc.)
- [ ] Add proper tool configuration with default tools and permissions
- [ ] Update schema URL to point to correct agent schema

[Question] What default tools should we include in generated agents? The documentation shows `["*"]` for all tools, but should we be more restrictive?
[Answer] I think we can rely on `["*"]` because even if all tools are allowed, Q CLI will ask for permission the first time. Let's keep it simple for now. We might want to add specific tools later though.

### 3. Restructure Profile Installation Process

**Current Implementation Issues:**

- We're copying contexts to `~/.aws/amazonq/contexts/` which is not used by agents
- We're creating both context files AND agent configs, but agents only use resources
- Global context integration is broken

**Required Actions:**

- [ ] Modify `install_profile()` to only create agent configuration files
- [ ] Update resource paths to point directly to library files (no copying needed)
- [ ] Remove context file copying to `~/.aws/amazonq/contexts/`
- [ ] Update resource paths to use absolute paths with `file://` prefix

[Question] Should we copy context files to a central location or reference them directly from the library? Direct reference would be simpler but requires the library to remain in place.
[Answer] I think we should remove us from the config folders of any client. So what if we install the library in our own config folder (e.g. ~/.config/ai-configurator/library) this way we know where we reference it and we can manage it through our code?

### 4. Update Library Structure

**Current Structure Issues:**

- Global contexts are separate from profiles
- Profile contexts are in subdirectories that may not align with agent expectations

**Required Actions:**

- [ ] Decide how to handle former "global contexts" - convert to base contexts or remove
- [ ] Update profile structure to better align with agent resource expectations
- [ ] Consider flattening context structure for easier agent resource referencing

[Question] How should we handle the concept of "organizational contexts" that were previously global? Should these become a "base-agent" that others extend, or should they be included in every agent's resources?
[Answer] As written above, the logic will move to our ai-configurator instead of relying on the tool. We can still have the concept of global contexts or base contexts for agents. For example if something is defined as global context, we will just install it in each agent as reference. Or can you describe me the concept of base-agent more? Maybe we mean the same.

### 5. Update CLI Commands and User Experience

**Current Issues:**

- Users expect global contexts to work across all profiles
- Installation process doesn't align with agent workflow
- No guidance on using agents vs profiles

**Required Actions:**

- [ ] Update CLI help text to explain agent-based approach
- [ ] Add commands to list installed agents (`q chat --agent list` equivalent)
- [ ] Update installation success messages to guide users on agent usage
- [ ] Add validation to ensure agent configs are valid

[Question] Should we maintain backward compatibility by automatically migrating old installations, or should we require users to reinstall profiles?
[Answer] as this tool is only used by myself at the moment we can ignore backward compatibility. We should however have a quick script to clean-up my existing config folder of ~/.aws/amazonq or at least a list of what I can remove.

### 6. Update Documentation and Examples

**Required Actions:**

- [ ] Update README.md to explain agent-based approach
- [ ] Add examples of using installed agents with `q chat --agent <name>`
- [ ] Document the new resource-based context system
- [ ] Update profile creation guidelines for agent compatibility

## Implementation Priority

### Phase 1: Core Agent Support (High Priority)

1. Update `AgentConfig` schema to match current Amazon Q CLI requirements
2. Modify `install_profile()` to generate proper agent configurations
3. Remove global context installation logic
4. Update resource path generation to use `file://` prefixes

### Phase 2: Library Restructure (Medium Priority)

1. Decide on global context migration strategy
2. Update catalog schema to remove global contexts
3. Restructure library to align with agent approach
4. Update existing profiles to work with new structure

### Phase 3: Enhanced User Experience (Low Priority)

1. Add agent management commands
2. Update documentation and examples
3. Add validation and error handling
4. Implement migration tools for existing installations

## Technical Questions Requiring Decisions

[Question] The documentation shows agents can include MCP servers. Should our profiles support MCP server configuration, and if so, how should this be structured in our library?
[Answer] Yes definitely. The MCP servers were in the global context and we need to add them to agent specifics. I don't have a concept yet, we need to create a new feature for that, but let's do that after we configured the new agents.

[Question] Should we implement agent inheritance/composition where one agent can extend another, or keep each agent completely self-contained?
[Answer] What is your recommendation from my input?

**Follow-up**: Based on your answers, I recommend keeping agents self-contained for now. Since you want global contexts to be included in each agent's resources (rather than inheritance), each agent will have its own complete resource list. This is simpler to implement and understand. We can add inheritance later if needed.

[Question] For the new config folder approach (`~/.config/ai-configurator/library`), should we copy the entire library there during installation, or only copy it when installing the first profile?
[Answer] Whatever is easier. As this tool should work with other clients too, let's copy the whole library during installation, this way we can have a library that consists on just rules and then even if a tool is not supported yet, the user can refer to those rule files.

[Question] How should we handle profile versioning in the new agent system? Should agent names include versions (e.g., "developer-v1") or use a different approach?
[Answer] I think we can remove the versions and just have specific agent names. If a user want to have a more specific developer agent, the user can copy it and name it my-developer-agent or so.

[Question] The current implementation copies context files to Amazon Q directories. With agents using resources, should we reference files in-place from the library, or continue copying them to a central location?
[Answer] As mentioned above, let's have a config folder for ai-configurator and within have the library installed and reference it there.

[Question] Should we add validation to ensure generated agent configurations are valid according to the Amazon Q CLI schema before installation?
[Answer] Yes please.

## Migration Strategy for Existing Users

[Question] How should we handle users who have already installed profiles using the old system? Should we provide an automatic migration tool, or require manual reinstallation?
[Answer] No, just need to clean-up my installation. However I can just create a new .aws/amazonq folder myself and copy some files over.

[Question] Should we maintain any backward compatibility, or make a clean break with the old approach?
[Answer] No, we start fresh.

## Next Steps

1. **Review and Answer Questions**: Address all [Question] items above to finalize the approach
2. **Create Implementation Plan**: Break down the required changes into specific tasks
3. **Update Schemas**: Modify data models to align with agent architecture
4. **Implement Core Changes**: Start with Phase 1 items to get basic agent support working
5. **Test and Validate**: Ensure generated agents work correctly with Amazon Q CLI
6. **Update Documentation**: Reflect the new agent-based approach in all documentation

---

**Status**: Plan created, awaiting decisions on key questions before implementation begins.
