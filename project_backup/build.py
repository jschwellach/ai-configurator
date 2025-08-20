#!/usr/bin/env python3
"""
Build script for AI Configurator.
Creates distributable packages for PyPI and uvx installation.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔨 {description}...")
    try:
        subprocess.check_call(cmd)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Build the package."""
    print("🚀 Building AI Configurator package...")
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    if not (project_root / "pyproject.toml").exists():
        print("❌ pyproject.toml not found. Run this script from the project root.")
        sys.exit(1)
    
    # Clean previous builds
    import shutil
    for dir_name in ["dist", "build"]:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_path)
    
    # Clean egg-info directories
    for egg_info in project_root.glob("*.egg-info"):
        if egg_info.exists():
            print(f"🧹 Cleaning {egg_info.name}...")
            shutil.rmtree(egg_info)
    
    # Install build dependencies
    if not run_command([sys.executable, "-m", "pip", "install", "build", "twine"], "Installing build dependencies"):
        sys.exit(1)
    
    # Build the package
    if not run_command([sys.executable, "-m", "build"], "Building package"):
        sys.exit(1)
    
    # Check the built package
    if not run_command([sys.executable, "-m", "twine", "check", "dist/*"], "Checking package"):
        sys.exit(1)
    
    print("\n🎉 Package built successfully!")
    print("\n📦 Built files:")
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  • {file.name}")
    
    print("\n🚀 Next steps:")
    print("  • Test installation: pip install dist/*.whl")
    print("  • Test with uvx: uvx install --from dist/*.whl ai-configurator")
    print("  • Upload to PyPI: twine upload dist/*")
    
    # Test installation
    print("\n🧪 Testing installation...")
    whl_files = list(dist_dir.glob("*.whl"))
    if whl_files:
        test_cmd = [sys.executable, "-m", "pip", "install", "--force-reinstall", str(whl_files[0])]
        if run_command(test_cmd, "Testing package installation"):
            # Test the CLI
            if run_command(["ai-config", "--version"], "Testing CLI command"):
                print("✅ Package installation test passed!")
            else:
                print("⚠️ Package installed but CLI test failed")
        else:
            print("⚠️ Package installation test failed")


if __name__ == "__main__":
    main()