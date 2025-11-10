# Agent Import/Export Feature Plan

## Overview

This document outlines the plan for implementing import and export functionality for AI agents. This feature will allow users to share agent configurations, including their referenced library files and MCP server configurations, with their team members.

## Goals

1. Enable exporting an agent configuration package that can be shared
2. Enable importing an agent configuration package from team members
3. Maintain proper file references across different environments
4. Handle MCP server configurations appropriately

## Implementation Approach

### Export Process

1. **Agent Configuration Extraction**

   - Read the agent JSON configuration file
   - Identify all referenced library files (file:// URLs)
   - Extract MCP server configurations

2. **File Packaging**

   - Create a package directory structure:
     ```
     agent-package/
       manifest.json     # Contains metadata about the package
       agent.json        # The agent configuration
       library/          # All referenced library files
         roles/
         domains/
         tools/
         workflows/
         common/
       mcp/              # MCP server configurations (if any)
     ```
   - Copy all referenced library files to the package maintaining their relative structure
   - Create a manifest file with package metadata

3. **Path Resolution**
   - Update file references in the agent configuration to be relative to the package structure
   - Record original path information in the manifest for import process

### Import Process

1. **Package Validation**

   - Verify package structure and manifest
   - Check for required files

2. **File Installation**

   - Copy library files to appropriate locations in the local library
   - Handle conflicts (overwrite, skip, rename)

3. **Agent Configuration Update**

   - Adjust file references to match local environment paths
   - Register the agent in the local agent directory
   - Handle MCP server configurations

4. **Path Resolution**
   - Convert relative paths in package to absolute paths in local environment
   - Update agent configuration with correct file references

## Technical Details

### Package Structure

```
agent-package/
  manifest.json
  agent.json
  library/
    [library files maintaining original structure]
  mcp/
    [MCP server configurations if applicable]
```

### Manifest File Format

```json
{
  "version": "1.0",
  "name": "agent-name",
  "description": "Agent description",
  "created": "timestamp",
  "library_files": [
    {
      "source_path": "library/roles/software-engineer/software-engineer.md",
      "original_reference": "file://~/.config/ai-configurator/library/base/roles/software-engineer/software-engineer.md",
      "package_path": "library/roles/software-engineer/software-engineer.md"
    }
  ],
  "mcp_servers": [
    {
      "name": "server-name",
      "config": {
        "command": "command",
        "args": ["args"]
      }
    }
  ]
}
```

## Implementation Steps

### Phase 1: Export Functionality

- [ ] Create export command interface
- [ ] Implement agent configuration reading
- [ ] Identify and collect referenced library files
- [ ] Create package directory structure
- [ ] Copy library files to package
- [ ] Generate manifest file
- [ ] Update file references to be package-relative
- [ ] Save agent configuration in package
- [ ] Implement package compression (optional)

### Phase 2: Import Functionality

- [ ] Create import command interface
- [ ] Implement package validation
- [ ] Parse manifest file
- [ ] Install library files to local library
- [ ] Handle file conflicts appropriately
- [ ] Adjust file references for local environment
- [ ] Register agent in local agent directory
- [ ] Handle MCP server configurations
- [ ] Test import process

### Phase 3: Integration and Testing

- [ ] Integrate with existing CLI commands
- [ ] Add TUI support for import/export
- [ ] Create documentation
- [ ] Test cross-platform compatibility
- [ ] Test with various agent configurations
- [ ] Performance testing with large agents

## Open Questions

[Question] Should we support importing to a different agent name than the original?
[Answer] no, but if the agent exists we should ask if we overwrite it

[Question] How should we handle conflicts when importing library files that already exist?
[Answer] ask the user

[Question] Should we include version compatibility checks in the manifest?
[Answer] yes

[Question] Do we need to support encryption for sensitive MCP server configurations?
[Answer] That would be great

## Considerations

1. **Path Handling**: Different operating systems use different path separators
2. **File Permissions**: Ensure proper file permissions are maintained
3. **Large Files**: Consider limitations with very large library files
4. **Dependencies**: Handle cases where library files reference other files
5. **Security**: Validate package contents to prevent malicious code injection
