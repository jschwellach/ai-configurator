#!/usr/bin/env python3
"""
Cleanup script for old Amazon Q CLI configuration.
Removes old context files and global_context.json that are no longer used.
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any

def main():
    """Main cleanup function."""
    amazonq_dir = Path.home() / ".aws" / "amazonq"
    
    if not amazonq_dir.exists():
        print("❌ Amazon Q directory not found. Nothing to clean up.")
        return
    
    print("🧹 Amazon Q CLI Configuration Cleanup")
    print("=====================================")
    print(f"Checking: {amazonq_dir}")
    print()
    
    # Files and directories to potentially remove
    cleanup_items = []
    
    # Check for old contexts directory
    contexts_dir = amazonq_dir / "contexts"
    if contexts_dir.exists():
        context_files = list(contexts_dir.glob("*"))
        if context_files:
            cleanup_items.append({
                "path": contexts_dir,
                "type": "directory",
                "description": f"Old contexts directory ({len(context_files)} files)",
                "files": [f.name for f in context_files]
            })
    
    # Check for global_context.json
    global_context_json = amazonq_dir / "global_context.json"
    if global_context_json.exists():
        try:
            with open(global_context_json, 'r') as f:
                data = json.load(f)
            paths = data.get("paths", [])
            cleanup_items.append({
                "path": global_context_json,
                "type": "file",
                "description": f"Old global context configuration ({len(paths)} paths)",
                "content": data
            })
        except Exception as e:
            cleanup_items.append({
                "path": global_context_json,
                "type": "file",
                "description": f"Old global context configuration (corrupted: {e})",
                "content": None
            })
    
    # Check for global-contexts directory
    global_contexts_dir = amazonq_dir / "global-contexts"
    if global_contexts_dir.exists():
        global_files = list(global_contexts_dir.glob("*"))
        if global_files:
            cleanup_items.append({
                "path": global_contexts_dir,
                "type": "directory", 
                "description": f"Old global contexts directory ({len(global_files)} files)",
                "files": [f.name for f in global_files]
            })
    
    # Check for old MCP configuration
    mcp_json = amazonq_dir / "mcp.json"
    if mcp_json.exists():
        cleanup_items.append({
            "path": mcp_json,
            "type": "file",
            "description": "Old MCP configuration (may still be needed)",
            "content": "MCP config"
        })
    
    if not cleanup_items:
        print("✅ No old configuration files found. Your Amazon Q setup is clean!")
        return
    
    print("Found the following old configuration items:")
    print()
    
    for i, item in enumerate(cleanup_items, 1):
        print(f"{i}. {item['description']}")
        print(f"   Path: {item['path']}")
        if item['type'] == 'directory' and 'files' in item:
            print(f"   Files: {', '.join(item['files'][:5])}")
            if len(item['files']) > 5:
                print(f"          ... and {len(item['files']) - 5} more")
        print()
    
    # Show current agents
    agents_dir = amazonq_dir / "cli-agents"
    if agents_dir.exists():
        agent_files = list(agents_dir.glob("*.json"))
        if agent_files:
            print(f"✅ Current agents ({len(agent_files)} installed):")
            for agent_file in agent_files:
                print(f"   - {agent_file.stem}")
            print()
    
    # Ask for confirmation
    print("⚠️  WARNING: This will permanently delete the old configuration files.")
    print("   Make sure you have migrated to the new agent-based system first!")
    print()
    
    response = input("Do you want to proceed with cleanup? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Cleanup cancelled.")
        return
    
    # Perform cleanup
    print("\n🗑️  Cleaning up old configuration...")
    
    for item in cleanup_items:
        try:
            if item['path'].exists():
                if item['type'] == 'directory':
                    shutil.rmtree(item['path'])
                    print(f"✅ Removed directory: {item['path']}")
                else:
                    item['path'].unlink()
                    print(f"✅ Removed file: {item['path']}")
            else:
                print(f"⚠️  Already removed: {item['path']}")
        except Exception as e:
            print(f"❌ Failed to remove {item['path']}: {e}")
    
    print("\n🎉 Cleanup completed!")
    print("\nYour Amazon Q CLI is now using the new agent-based configuration.")
    print("Use 'ai-config list' to see available profiles.")
    print("Use 'ai-config agents' to see installed agents.")
    print("Use 'q chat --agent <agent-name>' to start a chat with an agent.")

if __name__ == "__main__":
    main()
