# AI Agent Manager Roadmap

## Current Version: v0.2.2

### ✅ Completed (v0.1.x - v0.2.x)

- **v0.1.0**: Initial beta release with TUI
  - Agent management (create, edit, rename, delete)
  - Library management (base + personal files)
  - MCP server management
  - Auto-export to Q CLI
  - 5 default templates
  - 4 default MCP servers

- **v0.2.0**: Q CLI Import Feature
  - Import existing Q CLI agents
  - Smart merge for conflicts
  - Resource path resolution
  - MCP server extraction

- **v0.2.1-0.2.2**: Polish
  - Dynamic title and version
  - Fixed PyPI URLs

---

## Planned Features

### 🎯 v0.3.0 - Enhanced Agent Management
**Target: Q1 2025**

- [ ] Agent templates system
  - Create agents from templates
  - Save custom templates
  - Template marketplace/sharing
- [ ] Agent validation improvements
  - Validate resource file existence
  - Check MCP server availability
  - Syntax validation for prompts
- [ ] Agent search and filtering
  - Search by name, description, tags
  - Filter by tool type, resources used
- [ ] Agent tags/categories
  - Organize agents with tags
  - Category-based browsing

**GitHub Issues**: #1, #2, #3, #4

---

### 🔄 v0.4.0 - Bidirectional Sync (Phase 2)
**Target: Q2 2025**

- [ ] Detect external changes to Q CLI agents
- [ ] Sync status indicators (✓ synced, ↑ local changes, ↓ remote changes, ⚠ conflict)
- [ ] Manual sync trigger per agent
- [ ] Sync history/log
- [ ] Undo/rollback sync operations

**GitHub Issues**: #5, #6, #7

---

### 📚 v0.5.0 - Library Enhancements
**Target: Q2 2025**

- [ ] Library search and filtering
- [ ] File preview in TUI
- [ ] Markdown rendering for templates
- [ ] Version control for library files
- [ ] Import/export library bundles
- [ ] Remote library sync (Git integration)

**GitHub Issues**: #8, #9, #10

---

### 🔌 v0.6.0 - MCP Server Enhancements
**Target: Q3 2025**

- [ ] MCP server testing/validation
- [ ] Server status monitoring
- [ ] Browse MCP registry in TUI
- [ ] One-click install from registry
- [ ] Server configuration wizard
- [ ] Custom server templates

**GitHub Issues**: #11, #12, #13

---

### 🤖 v0.7.0 - Multi-Tool Support
**Target: Q3 2025**

- [ ] Claude Desktop integration
- [ ] Cursor IDE integration
- [ ] Windsurf integration
- [ ] Generic AI tool adapter
- [ ] Tool-specific export formats
- [ ] Cross-tool agent migration

**GitHub Issues**: #14, #15, #16

---

### 🎨 v0.8.0 - UI/UX Improvements
**Target: Q4 2025**

- [ ] Customizable themes
- [ ] Keyboard shortcut customization
- [ ] Split-screen multi-agent editing
- [ ] Drag-and-drop file management
- [ ] Context menu support
- [ ] Quick actions palette (Ctrl+K)

**GitHub Issues**: #17, #18, #19

---

### 🔐 v0.9.0 - Security & Secrets Management
**Target: Q4 2025**

- [ ] Secure storage for API keys
- [ ] Environment variable management
- [ ] Secrets encryption
- [ ] Per-agent permissions
- [ ] Audit log for sensitive operations

**GitHub Issues**: #20, #21, #22

---

### 🚀 v1.0.0 - Production Ready
**Target: Q1 2026**

- [ ] Comprehensive documentation
- [ ] Video tutorials
- [ ] Plugin system for extensions
- [ ] REST API for automation
- [ ] Web UI (optional)
- [ ] Performance optimizations
- [ ] Extensive test coverage
- [ ] Production deployment guide

**GitHub Issues**: #23, #24, #25

---

## Community Requests

Have a feature request? [Open an issue](https://github.com/jschwellach/ai-configurator/issues/new) with the label `enhancement`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to the roadmap.

---

## Version History

- **v0.2.2** (2025-10-08): Fix PyPI URLs
- **v0.2.1** (2025-10-08): Dynamic title and version
- **v0.2.0** (2025-10-08): Q CLI import feature
- **v0.1.3** (2025-10-08): Fix MCP server location
- **v0.1.2** (2025-10-08): Add default MCP servers
- **v0.1.1** (2025-10-08): Fix package build
- **v0.1.0** (2025-10-08): Initial beta release
