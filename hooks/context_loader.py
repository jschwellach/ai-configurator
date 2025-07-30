#!/usr/bin/env python3
"""Context loader hook for Amazon Q CLI."""

import sys
import yaml
from pathlib import Path

def load_context(context_name):
    """Load context files for the specified context."""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        print(f"Hook configuration not found: {config_path}", file=sys.stderr)
        return
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Failed to load hook configuration: {e}", file=sys.stderr)
        return
    
    files = config.get("contexts", {}).get(context_name, [])
    
    if not files:
        print(f"No context files defined for '{context_name}'", file=sys.stderr)
        return
    
    # Load and print context files
    for file_name in files:
        file_path = Path(file_name)
        
        # Try relative to Amazon Q config directory
        if not file_path.is_absolute():
            amazonq_dir = Path.home() / ".aws" / "amazonq"
            file_path = amazonq_dir / file_path
        
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                print(content, end="")
            except Exception as e:
                print(f"Failed to read '{file_path}': {e}", file=sys.stderr)
        else:
            print(f"Context file not found: '{file_path}'", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python context_loader.py <context_name>", file=sys.stderr)
        sys.exit(1)
    
    load_context(sys.argv[1])
