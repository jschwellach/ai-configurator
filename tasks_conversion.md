# AI Configurator: Q CLI Agents Output Format Conversion

## Current State Analysis

Our library structure remains unchanged with `profile.yaml` files. Q CLI now expects agent JSON format as output instead of the old profile `context.json` format.

### Our Library Structure (Unchanged)
- **Profiles**: `library/{profile}/profile.yaml`
- **Contexts**: `library/{profile}/contexts/*.md`
- **Global Contexts**: `library/global-contexts/*.md`
- **Catalog**: `library/catalog.json`

### Q CLI Target Format (New)
- **Agents**: `~/.aws/amazonq/cli-agents/{agent-name}.json`
- **Schema**: Official Q CLI agent schema
- **Resources**: File paths with `file://` prefix

## Conversion Tasks

### 1. Update Profile Installer Output
- [x] Change installation target from `profiles/` to `cli-agents/`
- [x] Generate agent JSON format instead of `context.json`
- [x] Convert context file paths to `resources` array with `file://` prefix
- [x] Include global contexts in each agent's resources

### 2. Update Core Models
- [x] Add `AgentConfig` class for output format
- [x] Keep existing `ProfileConfig` for library parsing
- [x] Add agent JSON generation methods

### 3. CLI Updates
- [x] Keep same command names (install, remove, list, info)
- [x] Update output messages to mention "agents" instead of "profiles"
- [x] Maintain backward compatibility for user experience

## Implementation Details

### Agent Output Format
```json
{
  "$schema": "https://raw.githubusercontent.com/aws/amazon-q-developer-cli/refs/heads/main/schemas/agent-v1.json",
  "name": "profile-id",
  "description": "Profile description from YAML",
  "prompt": null,
  "mcpServers": {},
  "tools": ["*"],
  "toolAliases": {},
  "allowedTools": [],
  "resources": [
    "file://~/.aws/amazonq/contexts/profile_context1.md",
    "file://~/.aws/amazonq/contexts/profile_context2.md",
    "file://~/.aws/amazonq/global-contexts/defaults.md"
  ],
  "hooks": {},
  "toolsSettings": {},
  "useLegacyMcpJson": true
}
```

### Key Changes Implemented

1. **Output Location**: Install to `~/.aws/amazonq/cli-agents/{profile-id}.json` ✅
2. **Output Format**: Generate agent JSON from our YAML profiles ✅
3. **Resource Paths**: Convert context files to `file://` prefixed paths ✅
4. **Global Context Integration**: Auto-include global contexts in resources ✅
5. **Context File Prefixing**: Add profile ID prefix to prevent conflicts ✅

### No Migration Needed
- Q CLI handles existing profile migration automatically ✅
- Our library structure stays the same ✅
- Only output format changes ✅

## Testing Results

✅ **Installation**: Successfully creates agent JSON with correct schema
✅ **Context Handling**: Profile-specific contexts prefixed with profile ID
✅ **Global Contexts**: Automatically included in all agents
✅ **Removal**: Properly removes agent JSON and profile-specific contexts
✅ **CLI Commands**: All commands work with updated messaging
✅ **Backward Compatibility**: Same command names and user experience

## Status: ✅ COMPLETED

The conversion to Q CLI agents format is complete and fully functional.
