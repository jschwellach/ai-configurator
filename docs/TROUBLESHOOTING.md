# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### ImportError: cannot import name 'main'
**Problem**: Entry point error when running `ai-config`
```
ImportError: cannot import name 'main' from 'ai_configurator.cli'
```

**Solution**:
```bash
# Reinstall the package
pip uninstall ai-configurator
pip install ai-configurator

# Or for development
pip install -e .
```

#### Command not found: ai-config
**Problem**: CLI command not available after installation

**Solution**:
```bash
# Check if installed correctly
pip show ai-configurator

# Reinstall with user flag if needed
pip install --user ai-configurator

# Add to PATH if necessary (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"
```

### Library Sync Issues

#### Sync Fails with Permission Errors
**Problem**: Cannot write to library directories
```
PermissionError: [Errno 13] Permission denied: '/path/to/library'
```

**Solution**:
```bash
# Check directory permissions
ls -la ~/.config/ai-configurator/

# Fix permissions
chmod -R 755 ~/.config/ai-configurator/
chown -R $USER ~/.config/ai-configurator/
```

#### Conflicts Not Resolving
**Problem**: Conflict resolution doesn't work as expected

**Solution**:
1. **Check File Status**:
   ```bash
   ai-config library status
   ai-config library diff --file problematic-file.md
   ```

2. **Manual Resolution**:
   ```bash
   # Edit the file directly
   nano ~/.config/ai-configurator/personal/problematic-file.md
   
   # Then sync again
   ai-config library sync
   ```

3. **Reset Personal Library** (last resort):
   ```bash
   # Backup first
   cp -r ~/.config/ai-configurator/personal ~/.config/ai-configurator/personal.backup
   
   # Remove conflicted files
   rm ~/.config/ai-configurator/personal/problematic-file.md
   
   # Sync to get base version
   ai-config library sync
   ```

#### Backup Restoration
**Problem**: Need to restore from backup after failed sync

**Solution**:
```bash
# List available backups
ls ~/.config/ai-configurator/backups/

# Restore from specific backup
cp -r ~/.config/ai-configurator/backups/backup_20231001_143022/* ~/.config/ai-configurator/personal/

# Verify restoration
ai-config library status
```

### File Management Issues

#### File Patterns Not Working
**Problem**: Glob patterns don't find expected files
```bash
ai-config files scan-files my-agent --pattern "**/*.md"
# Returns: No files found
```

**Solution**:
1. **Check Base Path**:
   ```bash
   # Verify you're in the right directory
   pwd
   ls *.md  # Should show some markdown files
   
   # Use absolute path if needed
   ai-config files scan-files my-agent --pattern "**/*.md" --base-path /full/path/to/project
   ```

2. **Test Pattern Manually**:
   ```bash
   # Test with shell glob
   ls **/*.md  # (if shell supports it)
   find . -name "*.md"  # Alternative test
   ```

3. **Use Simpler Patterns**:
   ```bash
   # Start simple and build up
   ai-config files scan-files my-agent --pattern "*.md"
   ai-config files scan-files my-agent --pattern "docs/*.md"
   ```

#### File Watching Not Working
**Problem**: File changes not detected

**Solution**:
1. **Check Watch Status**:
   ```bash
   ai-config files watch-files my-agent --status
   ```

2. **Restart Watching**:
   ```bash
   ai-config files watch-files my-agent --disable
   ai-config files watch-files my-agent --enable --pattern "**/*.md"
   ```

3. **Check File System Limits** (Linux):
   ```bash
   # Check current limits
   cat /proc/sys/fs/inotify/max_user_watches
   
   # Increase if needed (temporary)
   sudo sysctl fs.inotify.max_user_watches=524288
   
   # Make permanent
   echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf
   ```

### MCP Server Issues

#### Server Installation Fails
**Problem**: MCP server installation errors
```
❌ Installation failed: Server 'git' not found in registry
```

**Solution**:
1. **Check Registry Status**:
   ```bash
   ai-config mcp status
   ```

2. **Create Sample Registry**:
   ```bash
   ai-config mcp create-sample
   ai-config mcp browse
   ```

3. **Sync Registry** (if remote available):
   ```bash
   ai-config mcp sync --force
   ```

#### Registry Empty or Corrupted
**Problem**: No servers available in registry

**Solution**:
```bash
# Remove corrupted registry
rm -rf ~/.config/ai-configurator/registry/

# Recreate with samples
ai-config mcp create-sample

# Verify
ai-config mcp browse
```

#### Server Installation Timeout
**Problem**: Installation hangs or times out

**Solution**:
1. **Check Network Connection**:
   ```bash
   ping google.com
   ```

2. **Manual Installation** (for npm servers):
   ```bash
   # Install manually first
   npm install -g @modelcontextprotocol/server-filesystem
   
   # Then register with ai-config
   ai-config mcp install filesystem
   ```

3. **Increase Timeout** (if option available):
   ```bash
   # Check for timeout options
   ai-config mcp install --help
   ```

### Agent Issues

#### Agent Creation Fails
**Problem**: Cannot create new agents
```
❌ Failed to create agent 'my-agent'
```

**Solution**:
1. **Check Agent Directory**:
   ```bash
   ls -la ~/.config/ai-configurator/agents/
   
   # Create if missing
   mkdir -p ~/.config/ai-configurator/agents/
   ```

2. **Check Agent Name**:
   ```bash
   # Use valid characters only (alphanumeric, hyphens, underscores)
   ai-config create-agent --name "valid-agent-name"
   ```

3. **Check Existing Agents**:
   ```bash
   ai-config list-agents
   # Agent names must be unique
   ```

#### Agent Export Fails
**Problem**: Cannot export agent to Q CLI
```
❌ Failed to save agent configuration
```

**Solution**:
1. **Check Q CLI Configuration**:
   ```bash
   # Verify Q CLI is installed
   q --version
   
   # Check Q CLI config directory
   ls ~/.config/amazonq/
   ```

2. **Manual Export**:
   ```bash
   # Export to file first
   ai-config export-agent my-agent > my-agent-config.json
   
   # Check the output
   cat my-agent-config.json
   ```

3. **Check File Paths**:
   ```bash
   # Ensure all referenced files exist
   ai-config show-agent my-agent
   ```

### Wizard Issues

#### Wizard Hangs or Crashes
**Problem**: Interactive wizards stop responding

**Solution**:
1. **Interrupt and Restart**:
   ```bash
   # Press Ctrl+C to interrupt
   # Then restart
   ai-config wizard quick-start
   ```

2. **Use Non-Interactive Mode**:
   ```bash
   # Skip wizards, use direct commands
   ai-config create-agent --name my-agent --tool q-cli
   ```

3. **Check Terminal Compatibility**:
   ```bash
   # Test Rich compatibility
   python -c "from rich.console import Console; Console().print('Test')"
   ```

#### Template Selection Issues
**Problem**: Templates not appearing in wizard

**Solution**:
1. **Check Template Directory**:
   ```bash
   ls ~/.config/ai-configurator/library/templates/
   ```

2. **Verify Template Format**:
   ```bash
   # Templates should follow naming convention
   # {name}-{tool}.md
   ls ~/.config/ai-configurator/library/templates/*-q-cli.md
   ```

3. **Create Missing Templates**:
   ```bash
   # Copy from roles if needed
   cp ~/.config/ai-configurator/library/roles/software-engineer/software-engineer.md \
      ~/.config/ai-configurator/library/templates/software-engineer-q-cli.md
   ```

### Performance Issues

#### Slow File Discovery
**Problem**: File scanning takes too long

**Solution**:
1. **Use More Specific Patterns**:
   ```bash
   # Instead of scanning everything
   ai-config files scan-files my-agent --pattern "**/*"
   
   # Use specific patterns
   ai-config files scan-files my-agent --pattern "docs/**/*.md"
   ```

2. **Exclude Large Directories**:
   ```bash
   # Add exclusions to patterns
   # (This would need to be implemented in FilePattern model)
   ```

3. **Limit Scope**:
   ```bash
   # Use specific base paths
   ai-config files scan-files my-agent --pattern "*.md" --base-path ./docs
   ```

#### Large Library Sync Issues
**Problem**: Library sync is slow with many files

**Solution**:
1. **Sync Specific Files**:
   ```bash
   # Use diff to see what changed
   ai-config library diff
   
   # Sync only if needed
   ai-config library sync --dry-run
   ```

2. **Clean Up Old Backups**:
   ```bash
   # Remove old backups (be careful!)
   find ~/.config/ai-configurator/backups/ -type d -mtime +30 -exec rm -rf {} \;
   ```

### Configuration Issues

#### Configuration Corruption
**Problem**: System configuration appears corrupted

**Solution**:
1. **Reset Configuration**:
   ```bash
   # Backup current config
   cp -r ~/.config/ai-configurator ~/.config/ai-configurator.backup
   
   # Remove corrupted config
   rm -rf ~/.config/ai-configurator
   
   # Reinitialize
   ai-config status  # This will recreate basic structure
   ```

2. **Restore from Backup**:
   ```bash
   # If you have a good backup
   cp -r ~/.config/ai-configurator.backup ~/.config/ai-configurator
   ```

#### Path Issues
**Problem**: Incorrect paths in configuration

**Solution**:
```bash
# Check current paths
ai-config status

# Verify paths exist
ls ~/.config/ai-configurator/library/
ls ~/.config/ai-configurator/personal/

# Recreate missing directories
mkdir -p ~/.config/ai-configurator/{library,personal,agents,registry,backups}
```

## Getting Help

### Debug Information
When reporting issues, include:

```bash
# System information
ai-config status

# Version information
ai-config --version
python --version
pip show ai-configurator

# Error details
ai-config <failing-command> 2>&1 | tee error.log
```

### Log Files
Check for log files in:
- `~/.config/ai-configurator/logs/` (if logging is enabled)
- System logs for permission issues

### Community Support
- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share solutions
- **Documentation**: Check README and user guide first

### Emergency Recovery

If everything breaks:

```bash
# Complete reset (DANGER: loses all configuration)
rm -rf ~/.config/ai-configurator

# Reinstall
pip uninstall ai-configurator
pip install ai-configurator

# Start fresh
ai-config wizard quick-start
```

---

**Remember**: Always backup important configurations before making major changes!
