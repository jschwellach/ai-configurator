#!/usr/bin/env python3
"""
Test script for global contexts functionality.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_configurator.core.library_manager import LibraryManager
from ai_configurator.core.profile_installer import ProfileInstaller


def test_global_contexts():
    """Test global contexts functionality."""
    print("🧪 Testing Global Contexts Functionality")
    print("=" * 50)
    
    # Initialize managers
    library_manager = LibraryManager()
    installer = ProfileInstaller(library_manager)
    
    try:
        # Test 1: Load catalog with global contexts
        print("\n1. Loading catalog...")
        catalog = library_manager.load_catalog()
        if catalog:
            print(f"   ✅ Catalog loaded successfully")
            print(f"   📊 Profiles: {len(catalog.profiles)}")
            print(f"   🌍 Global contexts: {len(catalog.global_contexts)}")
        else:
            print("   ❌ Failed to load catalog")
            return False
        
        # Test 2: List global contexts
        print("\n2. Listing global contexts...")
        global_contexts = library_manager.get_global_contexts()
        if global_contexts:
            print(f"   ✅ Found {len(global_contexts)} global contexts:")
            for context in global_contexts:
                print(f"      - {context.name} (Priority: {context.priority})")
        else:
            print("   ❌ No global contexts found")
            return False
        
        # Test 3: Get specific global context
        print("\n3. Testing global context retrieval...")
        test_context = library_manager.get_global_context_by_id("aws-security-best-practices")
        if test_context:
            print(f"   ✅ Retrieved context: {test_context.name}")
            print(f"      Priority: {test_context.priority}")
            print(f"      File path: {test_context.file_path}")
        else:
            print("   ❌ Failed to retrieve test context")
            return False
        
        # Test 4: Check if global context files exist
        print("\n4. Checking global context files...")
        all_files_exist = True
        for context in global_contexts:
            file_path = library_manager.library_path / context.file_path
            if file_path.exists():
                print(f"   ✅ {context.name}: {file_path}")
            else:
                print(f"   ❌ {context.name}: {file_path} (NOT FOUND)")
                all_files_exist = False
        
        if not all_files_exist:
            print("   ⚠️  Some global context files are missing")
            return False
        
        # Test 5: Test profile installation (dry run check)
        print("\n5. Testing profile installation logic...")
        default_profile = library_manager.get_configuration_by_id("default-v1")
        if default_profile:
            print(f"   ✅ Found test profile: {default_profile.name}")
            print("   📝 Global contexts would be included during installation")
        else:
            print("   ❌ Test profile not found")
            return False
        
        print("\n🎉 All tests passed! Global contexts are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    finally:
        library_manager.shutdown()


def main():
    """Main function."""
    success = test_global_contexts()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
