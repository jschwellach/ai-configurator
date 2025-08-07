#!/usr/bin/env python3
"""
Test script to verify the global context implementation fix.
"""

import json
import tempfile
from pathlib import Path
from ai_configurator.core.profile_installer import ProfileInstaller
from ai_configurator.core.library_manager import LibraryManager

def test_global_context_implementation():
    """Test that global contexts are properly implemented."""
    
    print("🧪 Testing global context implementation...")
    
    # Create installer
    installer = ProfileInstaller()
    library_manager = LibraryManager()
    
    # Test 1: Install global contexts
    print("\n1. Testing global context installation...")
    success = installer.install_global_contexts()
    assert success, "Global context installation should succeed"
    print("   ✅ Global contexts installed successfully")
    
    # Test 2: Check global_context.json exists and has correct structure
    print("\n2. Testing global_context.json structure...")
    global_context_path = Path.home() / ".aws" / "amazonq" / "global_context.json"
    assert global_context_path.exists(), "global_context.json should exist"
    
    with open(global_context_path, 'r') as f:
        global_config = json.load(f)
    
    assert "paths" in global_config, "global_context.json should have 'paths' key"
    assert "hooks" in global_config, "global_context.json should have 'hooks' key"
    assert isinstance(global_config["paths"], list), "paths should be a list"
    print("   ✅ global_context.json has correct structure")
    
    # Test 3: Check that global context files exist in global-contexts folder
    print("\n3. Testing global context files in global-contexts folder...")
    global_contexts = library_manager.get_global_contexts()
    amazonq_dir = Path.home() / ".aws" / "amazonq"
    global_contexts_dir = amazonq_dir / "global-contexts"
    
    assert global_contexts_dir.exists(), "global-contexts directory should exist"
    
    for global_context in global_contexts:
        filename = Path(global_context.file_path).name
        file_path = global_contexts_dir / filename
        assert file_path.exists(), f"Global context file {filename} should exist in global-contexts folder"
        
        # Check that the path is in global_context.json
        assert str(file_path) in global_config["paths"], f"Path {file_path} should be in global_context.json"
    
    print(f"   ✅ All {len(global_contexts)} global context files exist in global-contexts folder and are referenced")
    
    # Test 4: Check that no global context files exist in root amazonq directory
    print("\n4. Testing no global context files in root amazonq directory...")
    global_filenames = {Path(gc.file_path).name for gc in global_contexts}
    
    for filename in global_filenames:
        root_file_path = amazonq_dir / filename
        assert not root_file_path.exists(), f"Global context file {filename} should NOT exist in root amazonq directory"
    
    print("   ✅ No global context files in root amazonq directory (prevents double-loading)")
    
    # Test 5: Install a profile and check it doesn't duplicate global contexts
    print("\n5. Testing profile installation doesn't duplicate global contexts...")
    profile_success = installer.install_profile("default-v1")
    assert profile_success, "Profile installation should succeed"
    
    # Check profile context.json
    profile_context_path = Path.home() / ".aws" / "amazonq" / "profiles" / "default" / "context.json"
    assert profile_context_path.exists(), "Profile context.json should exist"
    
    with open(profile_context_path, 'r') as f:
        profile_config = json.load(f)
    
    # Check that profile context doesn't contain global context files
    for path in profile_config["paths"]:
        assert "global-contexts" not in path, f"Profile should not contain global context path {path}"
    
    print("   ✅ Profile context.json doesn't contain global contexts")
    
    # Test 6: Remove global contexts
    print("\n6. Testing global context removal...")
    remove_success = installer.remove_global_contexts()
    assert remove_success, "Global context removal should succeed"
    
    # Check that global context files are removed
    for global_context in global_contexts:
        filename = Path(global_context.file_path).name
        file_path = global_contexts_dir / filename
        assert not file_path.exists(), f"Global context file {filename} should be removed"
    
    # Check that global-contexts directory is removed if empty
    if not any(global_contexts_dir.iterdir()) if global_contexts_dir.exists() else True:
        print("   ✅ Empty global-contexts directory was cleaned up")
    
    # Check that global_context.json is updated
    with open(global_context_path, 'r') as f:
        updated_global_config = json.load(f)
    
    for global_context in global_contexts:
        filename = Path(global_context.file_path).name
        file_path = global_contexts_dir / filename
        assert str(file_path) not in updated_global_config["paths"], f"Path {file_path} should be removed from global_context.json"
    
    print("   ✅ Global contexts removed successfully")
    
    print("\n🎉 All tests passed! Global context implementation is working correctly.")
    print("   📁 Global contexts are stored in ~/.aws/amazonq/global-contexts/")
    print("   🚫 No double-loading issue - contexts only loaded via global_context.json")
    
    # Cleanup: Reinstall global contexts for normal use
    installer.install_global_contexts()
    print("\n🔄 Reinstalled global contexts for normal use")

if __name__ == "__main__":
    test_global_context_implementation()
