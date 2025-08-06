# Development Setup

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-configurator.git
cd ai-configurator

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Verify installation
ai-config --help
```

## Project Structure

```
ai-configurator/
├── ai_configurator/               # Main package
│   ├── core/                      # Core functionality
│   │   ├── library_manager.py     # Library operations
│   │   ├── profile_installer.py   # Profile installation
│   │   ├── file_utils.py          # File utilities
│   │   └── catalog_schema.py      # Data models
│   └── cli.py                     # Command-line interface
├── library/                       # Configuration profiles
│   ├── default/                   # Default profile
│   ├── developer/                 # Developer profile
│   ├── solutions-architect/       # Solutions architect profile
│   └── documentation/             # Documentation profile
└── tests/                         # Test files
```

## Core Architecture

### LibraryManager
- Manages the library catalog
- Searches and retrieves configurations
- Simple file-based operations

### ProfileInstaller
- Installs profiles to Amazon Q directory
- Copies contexts to `~/.aws/amazonq/contexts/`
- Tracks installed profiles

### CLI
- 4 simple commands: list, install, remove, info
- Rich formatting for better user experience
- JSON output for automation

## Testing

```bash
# Run tests
pytest

# Test CLI commands
ai-config list
ai-config info developer-v1
ai-config install developer-v1
ai-config remove developer-v1
```

## Building

```bash
# Build wheel
python -m build --wheel

# Install from wheel
pip install dist/ai_configurator-*.whl
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## Simplified Architecture

The project has been dramatically simplified:

- **Core modules**: 5 files (down from 37)
- **CLI commands**: 4 commands (down from 10+)
- **Project directories**: 3 essential (down from 11+)

This makes the codebase much easier to understand, maintain, and contribute to.
