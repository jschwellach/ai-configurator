#!/usr/bin/env python3
"""
uvx-compatible installation script for AI Configurator.
This script can be used with: uvx run --from . uvx_install.py
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Main installation function for uvx."""
    print("🚀 AI Configurator - YAML Configuration Manager")
    print("=" * 50)
    
    # Show help by default
    try:
        from ai_configurator.cli import main as cli_main
        
        # If no arguments provided, show help
        if len(sys.argv) == 1:
            sys.argv.append("--help")
        
        # Run the CLI
        cli_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTrying to install dependencies...")
        
        # Try to install the package
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-e", str(Path(__file__).parent)
            ])
            print("✅ Installation completed!")
            print("\nTry running: ai-config --help")
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()