#!/usr/bin/env python3
"""
Installation script for AI Configurator.
This script can be used with uvx for easy installation.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Install AI Configurator using pip."""
    try:
        # Get the directory containing this script
        script_dir = Path(__file__).parent
        
        print("🚀 Installing AI Configurator...")
        
        # Install the package in development mode if we're in the source directory
        if (script_dir / "pyproject.toml").exists():
            print("📦 Installing from source directory...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-e", str(script_dir)
            ])
        else:
            print("📦 Installing from PyPI...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "ai-configurator"
            ])
        
        print("✅ AI Configurator installed successfully!")
        print("\n🎯 Quick start:")
        print("  ai-config --help")
        print("  ai-config formats")
        print("  ai-config install")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()