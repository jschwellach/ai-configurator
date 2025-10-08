# Phase 4 Implementation Plan - TUI Redesign

## Planning Date: October 5, 2025

## Executive Summary

Phase 4 transforms AI Configurator into a dual-mode application with both TUI (Terminal User Interface) and simplified CLI. This is a **breaking change release (v4.0.0)** that dramatically improves user experience while maintaining all functionality from Phases 1-3.

## Objectives

1. **Add TUI Interface**: Visual, menu-driven interface using Textual framework
2. **Simplify CLI**: Restructure to consistent `ai-config <resource> <action>` pattern
3. **Dual-Mode Entry**: `ai-config` launches TUI, explicit commands run CLI
4. **Maintain Functionality**: All Phase 1-3 features available in both modes
5. **Breaking Changes**: Clean slate with v4.0.0, no backward compatibility

## Architecture Reference

- **Component Model**: `docs/inception/phase_4_component_model.md`
- **Technology Stack**: `docs/inception/phase_4_technology_stack.md`
- **CLI Simplification**: `docs/inception/phase_4_cli_simplification.md`
- **User Workflows**: `docs/inception/phase_4_user_workflows.md`
- **Executive Summary**: `docs/inception/phase_4_executive_summary.md`

## Implementation Timeline

**Total Duration**: 10 weeks (5 sprints)
**Start Date**: October 5, 2025
**Target Completion**: December 14, 2025

---

## Sprint 1: CLI Simplification & Foundation (Weeks 1-2)

### Objectives

- Restructure CLI to resource-based pattern
- Create new entry point with mode detection
- Update dependencies
- Prepare foundation for TUI

### Tasks

#### 1.1 Update Dependencies

- [ ] Add `textual>=0.40.0` to requirements.txt
- [ ] Add `textual-dev>=1.0.0` to requirements-dev.txt
- [ ] Add `click-default-group>=1.2.2` to requirements.txt
- [ ] Add `pytest-asyncio>=0.21.0` to requirements-dev.txt
- [ ] Update pyproject.toml with new dependencies
- [ ] Test installation with `pip install -e .`

#### 1.2 Create New Entry Point

- [ ] Create `ai_configurator/main.py` with mode detection logic
- [ ] Implement `main()` function that detects TUI vs CLI mode
- [ ] Update `pyproject.toml` to use new entry point
- [ ] Test entry point: `ai-config --help` should work

#### 1.3 Restructure CLI Commands - Agent Management

- [ ] Create `ai_configurator/cli/agent_commands.py`
- [ ] Implement `agent list` command
- [ ] Implement `agent show <name>` command
- [ ] Implement `agent create <name>` command with options
- [ ] Implement `agent edit <name>` command
- [ ] Implement `agent delete <name>` command
- [ ] Implement `agent export <name>` command
- [ ] Test all agent commands

#### 1.4 Restructure CLI Commands - Library Management

- [ ] Create `ai_configurator/cli/library_commands.py`
- [ ] Implement `library status` command
- [ ] Implement `library sync` command
- [ ] Implement `library diff` command
- [ ] Implement `library update` command
- [ ] Implement `library files <pattern>` command
- [ ] Implement `library add <pattern>` command
- [ ] Implement `library watch` command
- [ ] Test all library commands

#### 1.5 Restructure CLI Commands - MCP Management

- [ ] Create `ai_configurator/cli/mcp_commands.py`
- [ ] Implement `mcp list` command
- [ ] Implement `mcp browse` command
- [ ] Implement `mcp search <query>` command
- [ ] Implement `mcp install <name>` command
- [ ] Implement `mcp configure <name>` command
- [ ] Implement `mcp init-registry` command
- [ ] Test all MCP commands

#### 1.6 Restructure CLI Commands - System Commands

- [ ] Create `ai_configurator/cli/system_commands.py`
- [ ] Implement `init` command (replaces wizard quick-start)
- [ ] Implement `status` command (system overview)
- [ ] Implement `health` command (system health check)
- [ ] Implement `logs` command (view logs)
- [ ] Implement `stats` command (cache stats)
- [ ] Test all system commands

#### 1.7 Update Main CLI Module

- [ ] Update `ai_configurator/cli_enhanced.py` to use new command groups
- [ ] Register all command groups with Click
- [ ] Remove old command patterns
- [ ] Add version command showing v4.0.0
- [ ] Test complete CLI: `ai-config --help` shows new structure

#### 1.8 Documentation Updates

- [ ] Update README.md with new command structure
- [ ] Create MIGRATION_GUIDE.md for v3.x to v4.0 changes
- [ ] Update CLI reference documentation
- [ ] Add examples for new command patterns

[Question] Should we keep any old commands with deprecation warnings, or do a complete clean break?
[Answer] clean break

[Question] Do you want interactive mode flags (e.g., `--interactive`) for commands that need user input?
[Answer] good idea

---

## Sprint 2: TUI Foundation (Weeks 3-4)

### Objectives

- Set up Textual application structure
- Create base screen classes
- Implement main menu and navigation
- Create reusable widgets

### Tasks

#### 2.1 TUI Project Structure

- [ ] Create `ai_configurator/tui/` directory
- [ ] Create `ai_configurator/tui/__init__.py`
- [ ] Create `ai_configurator/tui/app.py` for main application
- [ ] Create `ai_configurator/tui/screens/` directory
- [ ] Create `ai_configurator/tui/widgets/` directory
- [ ] Create `ai_configurator/tui/styles/` directory

#### 2.2 Main TUI Application

- [ ] Implement `AIConfiguratorApp` class in `app.py`
- [ ] Set up application bindings (q=quit, ?=help, esc=back)
- [ ] Configure screen registry
- [ ] Add Header and Footer widgets
- [ ] Implement navigation system
- [ ] Test TUI launches: `ai-config` or `ai-config tui`

#### 2.3 Base Screen Classes

- [ ] Create `ai_configurator/tui/screens/base.py`
- [ ] Implement `BaseScreen` class with common functionality
- [ ] Add standard key bindings
- [ ] Add error handling methods
- [ ] Add notification display methods
- [ ] Add data refresh methods

#### 2.4 Main Menu Screen

- [ ] Create `ai_configurator/tui/screens/main_menu.py`
- [ ] Implement `MainMenuScreen` with dashboard layout
- [ ] Add system status display
- [ ] Add navigation menu (Agent, Library, MCP, Settings)
- [ ] Add recent activity panel
- [ ] Add keyboard shortcuts panel
- [ ] Test navigation to each section

#### 2.5 Common Widgets

- [ ] Create `ai_configurator/tui/widgets/status_panel.py`
- [ ] Create `ai_configurator/tui/widgets/navigation_menu.py`
- [ ] Create `ai_configurator/tui/widgets/notification.py`
- [ ] Create `ai_configurator/tui/widgets/progress_indicator.py`
- [ ] Test widgets in isolation

#### 2.6 Styling System

- [ ] Create `ai_configurator/tui/styles/default.css`
- [ ] Define color scheme and themes
- [ ] Style common widgets
- [ ] Test styling across different terminals

#### 2.7 TUI Testing Setup

- [ ] Create `tests/tui/` directory
- [ ] Create `tests/tui/test_app.py`
- [ ] Implement basic TUI tests using Textual's test framework
- [ ] Test application launch and navigation
- [ ] Test keyboard shortcuts

[Question] What color scheme do you prefer for the TUI? (e.g., dark theme, light theme, custom colors)
[Answer] can we use the terminal configuration somehow?

---

## Sprint 3: Agent Management TUI (Weeks 5-6)

### Objectives

- Build complete agent management interface
- Implement agent creation wizard
- Add agent editing capabilities
- Integrate with existing AgentService

### Tasks

#### 3.1 Agent List Screen

- [ ] Create `ai_configurator/tui/screens/agent_manager.py`
- [ ] Implement `AgentManagerScreen` class
- [ ] Add agent list table with columns (Name, Tool, Resources, Status)
- [ ] Add action buttons (New, Edit, Delete, Export)
- [ ] Add keyboard shortcuts (n=new, e=edit, d=delete, x=export)
- [ ] Integrate with `AgentService.list_agents()`
- [ ] Test agent list display

#### 3.2 Agent List Widget

- [ ] Create `ai_configurator/tui/widgets/agent_list.py`
- [ ] Implement `AgentListWidget` using DataTable
- [ ] Add sorting capabilities
- [ ] Add filtering capabilities
- [ ] Add row selection handling
- [ ] Test widget with sample data

#### 3.3 Agent Creation Wizard

- [ ] Create `ai_configurator/tui/screens/agent_create.py`
- [ ] Implement multi-step creation form
- [ ] Step 1: Basic info (name, tool type)
- [ ] Step 2: Resource selection (library files)
- [ ] Step 3: MCP server selection
- [ ] Step 4: Review and confirm
- [ ] Integrate with `AgentService.create_agent()`
- [ ] Test complete creation flow

#### 3.4 Agent Detail/Edit Screen

- [ ] Create `ai_configurator/tui/screens/agent_detail.py`
- [ ] Display agent configuration
- [ ] Add edit mode with form fields
- [ ] Add resource management (add/remove files)
- [ ] Add MCP server management (add/remove servers)
- [ ] Integrate with `AgentService.update_agent()`
- [ ] Test editing existing agents

#### 3.5 Agent Export Dialog

- [ ] Create `ai_configurator/tui/widgets/export_dialog.py`
- [ ] Show export options (Q CLI, other tools)
- [ ] Display export preview
- [ ] Add confirmation dialog
- [ ] Integrate with export functionality
- [ ] Test export to Q CLI

#### 3.6 Agent Deletion Confirmation

- [ ] Create confirmation dialog widget
- [ ] Add safety checks (prevent accidental deletion)
- [ ] Show what will be deleted
- [ ] Integrate with `AgentService.delete_agent()`
- [ ] Test deletion flow

#### 3.7 Testing

- [ ] Create `tests/tui/test_agent_screens.py`
- [ ] Test agent list display
- [ ] Test agent creation wizard
- [ ] Test agent editing
- [ ] Test agent export
- [ ] Test agent deletion

---

## Sprint 4: Library & MCP Management TUI (Weeks 7-8)

### Objectives

- Build library synchronization interface
- Implement visual conflict resolution
- Build MCP server browser
- Add server installation workflow

### Tasks

#### 4.1 Library Manager Screen

- [ ] Create `ai_configurator/tui/screens/library_manager.py`
- [ ] Implement `LibraryManagerScreen` class
- [ ] Display library sync status
- [ ] Add action buttons (Sync, Diff, Update, Files)
- [ ] Show recent sync history
- [ ] Integrate with `SyncService`
- [ ] Test library status display

#### 4.2 Library Sync with Progress

- [ ] Create sync progress dialog
- [ ] Show real-time sync progress
- [ ] Display files being processed
- [ ] Handle sync errors gracefully
- [ ] Show sync completion summary
- [ ] Test sync operation

#### 4.3 Conflict Resolution Widget

- [ ] Create `ai_configurator/tui/widgets/conflict_resolver.py`
- [ ] Implement side-by-side diff view
- [ ] Add resolution options (Keep Local, Use Remote, Manual Edit)
- [ ] Show file metadata (modified date, size)
- [ ] Add "Resolve All" options
- [ ] Integrate with `SyncService.resolve_conflicts()`
- [ ] Test conflict resolution flow

#### 4.4 File Browser Widget

- [ ] Create `ai_configurator/tui/widgets/file_browser.py`
- [ ] Implement tree view for library files
- [ ] Add file preview panel
- [ ] Add file search/filter
- [ ] Add file selection (checkboxes)
- [ ] Test file browsing

#### 4.5 MCP Manager Screen

- [ ] Create `ai_configurator/tui/screens/mcp_manager.py`
- [ ] Implement `MCPManagerScreen` class
- [ ] Display installed servers
- [ ] Add action buttons (Browse, Install, Configure)
- [ ] Show server status
- [ ] Integrate with `RegistryService`
- [ ] Test MCP manager display

#### 4.6 MCP Server Browser

- [ ] Create `ai_configurator/tui/screens/mcp_browser.py`
- [ ] Display available servers from registry
- [ ] Add category filtering
- [ ] Add search functionality
- [ ] Show server details (description, version, rating)
- [ ] Add multi-select for installation
- [ ] Test server browsing

#### 4.7 MCP Server Installation

- [ ] Create installation wizard
- [ ] Show installation progress
- [ ] Handle server configuration
- [ ] Add to agent configuration option
- [ ] Show installation summary
- [ ] Integrate with `RegistryService.install_server()`
- [ ] Test installation flow

#### 4.8 MCP Server Configuration

- [ ] Create server configuration dialog
- [ ] Display server parameters
- [ ] Add form for parameter values
- [ ] Validate configuration
- [ ] Save configuration
- [ ] Test configuration editing

#### 4.9 Testing

- [ ] Create `tests/tui/test_library_screens.py`
- [ ] Test library sync interface
- [ ] Test conflict resolution
- [ ] Test file browsing
- [ ] Create `tests/tui/test_mcp_screens.py`
- [ ] Test MCP browser
- [ ] Test server installation
- [ ] Test server configuration

---

## Sprint 5: Polish & Integration (Weeks 9-10)

### Objectives

- Add settings and configuration screens
- Implement help system
- Add log viewer
- Performance optimization
- Final testing and documentation

### Tasks

#### 5.1 Settings Screen

- [ ] Create `ai_configurator/tui/screens/settings.py`
- [ ] Implement `SettingsScreen` class
- [ ] Add general settings (theme, editor, paths)
- [ ] Add library settings (sync behavior, conflict resolution)
- [ ] Add MCP settings (registry URL, auto-update)
- [ ] Save settings to configuration
- [ ] Test settings management

#### 5.2 Help System

- [ ] Create `ai_configurator/tui/screens/help.py`
- [ ] Add keyboard shortcuts reference
- [ ] Add feature documentation
- [ ] Add troubleshooting guide
- [ ] Add searchable help content
- [ ] Test help navigation

#### 5.3 Log Viewer

- [ ] Create `ai_configurator/tui/screens/logs.py`
- [ ] Display application logs
- [ ] Add log filtering (level, component)
- [ ] Add log search
- [ ] Add auto-refresh option
- [ ] Test log viewing

#### 5.4 About/Status Screen

- [ ] Create system status overview
- [ ] Display version information
- [ ] Show system health metrics
- [ ] Display cache statistics
- [ ] Add diagnostic information
- [ ] Test status display

#### 5.5 Performance Optimization

- [ ] Profile TUI performance
- [ ] Optimize screen rendering
- [ ] Implement lazy loading for large lists
- [ ] Add caching for frequently accessed data
- [ ] Optimize service calls
- [ ] Test performance improvements

#### 5.6 Error Handling & Recovery

- [ ] Implement global error handler
- [ ] Add error reporting dialog
- [ ] Add recovery suggestions
- [ ] Add error logging
- [ ] Test error scenarios

#### 5.7 Keyboard Shortcuts

- [ ] Document all keyboard shortcuts
- [ ] Ensure consistency across screens
- [ ] Add shortcut hints in UI
- [ ] Create quick reference card
- [ ] Test all shortcuts

#### 5.8 Accessibility

- [ ] Test with different terminal sizes
- [ ] Ensure keyboard-only navigation works
- [ ] Add screen reader hints (where possible)
- [ ] Test color contrast
- [ ] Test on different terminals (Linux, macOS, Windows)

#### 5.9 Integration Testing

- [ ] Create `tests/integration/test_tui_workflows.py`
- [ ] Test complete agent creation workflow
- [ ] Test library sync workflow
- [ ] Test MCP installation workflow
- [ ] Test navigation between all screens
- [ ] Test error recovery

#### 5.10 Documentation

- [ ] Create `docs/TUI_GUIDE.md` - Complete TUI usage guide
- [ ] Create `docs/KEYBOARD_SHORTCUTS.md` - Quick reference
- [ ] Update `docs/USER_GUIDE.md` with TUI sections
- [ ] Create `docs/DEVELOPER_TUI.md` - TUI development guide
- [ ] Update README.md with TUI screenshots/demos
- [ ] Create video/GIF demos of key workflows

#### 5.11 Final Testing

- [ ] Run complete test suite
- [ ] Test on Linux
- [ ] Test on macOS (if available)
- [ ] Test on Windows (if available)
- [ ] Test over SSH connection
- [ ] Fix any remaining bugs

#### 5.12 Release Preparation

- [ ] Update version to 4.0.0 in pyproject.toml
- [ ] Update CHANGELOG.md with all changes
- [ ] Create release notes
- [ ] Tag release in git
- [ ] Build distribution packages
- [ ] Test installation from packages

---

## Success Criteria

### Functional Requirements

- [ ] TUI launches successfully with `ai-config`
- [ ] All Phase 1-3 features available in TUI
- [ ] CLI commands follow consistent `<resource> <action>` pattern
- [ ] All CLI commands work correctly
- [ ] No data loss during operations
- [ ] Error handling works correctly

### User Experience Requirements

- [ ] TUI is intuitive and easy to navigate
- [ ] Keyboard shortcuts work consistently
- [ ] Visual feedback for all operations
- [ ] Help system is comprehensive
- [ ] Performance is acceptable (< 1s launch time)

### Technical Requirements

- [ ] All tests pass
- [ ] Code follows existing patterns
- [ ] Documentation is complete
- [ ] No breaking changes to service layer
- [ ] Clean separation between TUI and CLI

### Quality Metrics

- [ ] Test coverage > 80%
- [ ] No critical bugs
- [ ] Performance benchmarks met
- [ ] Cross-platform compatibility verified

---

## Risk Management

### High Risk Items

1. **Textual Learning Curve**

   - Risk: Team unfamiliar with Textual framework
   - Mitigation: Start with simple screens, iterate based on learning
   - Contingency: Use simpler UI library if needed

2. **TUI Performance**

   - Risk: TUI may be slow with large datasets
   - Mitigation: Implement lazy loading and caching
   - Contingency: Add pagination and filtering

3. **Terminal Compatibility**
   - Risk: TUI may not work on all terminals
   - Mitigation: Test on multiple terminals early
   - Contingency: Provide CLI fallback

### Medium Risk Items

1. **Breaking Changes Impact**

   - Risk: Users may be confused by new commands
   - Mitigation: Comprehensive migration guide
   - Contingency: Provide command mapping reference

2. **Testing Complexity**
   - Risk: TUI testing is more complex than CLI
   - Mitigation: Use Textual's testing framework
   - Contingency: Focus on integration tests

---

## Dependencies

### New Python Packages

- `textual>=0.40.0` - TUI framework
- `textual-dev>=1.0.0` - Development tools
- `click-default-group>=1.2.2` - CLI grouping
- `pytest-asyncio>=0.21.0` - Async testing

### Existing Packages (Retained)

- All Phase 1-3 dependencies unchanged
- Service layer remains unchanged
- Models remain unchanged

---

## Deliverables

### Code Deliverables

1. New entry point (`main.py`)
2. Restructured CLI commands (resource-based)
3. Complete TUI application
4. TUI screens for all features
5. Reusable TUI widgets
6. Comprehensive test suite

### Documentation Deliverables

1. TUI User Guide
2. Keyboard Shortcuts Reference
3. Migration Guide (v3.x to v4.0)
4. Developer Guide for TUI
5. Updated README
6. Release Notes

### Testing Deliverables

1. Unit tests for TUI components
2. Integration tests for workflows
3. CLI command tests
4. Cross-platform test results

---

## Notes for Implementation

### Code Style

- Follow existing code patterns from Phases 1-3
- Use Pydantic models for data validation
- Use Rich for CLI output (already in use)
- Use Textual widgets for TUI components
- Keep service layer unchanged

### Testing Strategy

- Test TUI screens in isolation
- Test CLI commands independently
- Integration tests for complete workflows
- Manual testing on different terminals

### Development Workflow

1. Implement feature
2. Write tests
3. Update documentation
4. Manual testing
5. Mark checkbox as complete
6. Commit changes

---

## Questions for Review

[Question] Do you want to implement all 5 sprints, or should we start with Sprint 1 and get your approval before proceeding?
[Answer] All 5

[Question] Should we create a feature branch for Phase 4 development, or work on main?
[Answer] We can work on the same feature branch we are at the moment

[Question] Do you want daily progress updates, or updates after each sprint?
[Answer] We should be done today, so let's just get started

[Question] Are there any specific TUI features or workflows you want to prioritize?
[Answer] No, just come up with the right approach

[Question] Should we maintain the old CLI commands with deprecation warnings, or do a complete clean break?
[Answer] no, clean break

---

## Status

**Status**: 📋 **AWAITING APPROVAL**  
**Created**: October 5, 2025  
**Version**: 1.0  
**Author**: Software Engineer

---

## Approval

- [x] Plan reviewed by stakeholder
- [x] Questions answered
- [x] Ready to begin implementation

**Approved By**: **Janos**  
**Date**: 2025-10-05  
**Signature**: XXX
