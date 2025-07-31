"""Test the directory manager functionality."""

import tempfile
import pytest
from pathlib import Path

from src.ai_configurator.core.directory_manager import DirectoryManager, ConfigurationType


def test_directory_manager_creation():
    """Test directory manager initialization and directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Initialize directory manager
        dm = DirectoryManager(temp_path)
        
        # Test directory structure creation
        success = dm.create_directory_structure()
        assert success
        
        # Verify directories were created
        structure = dm.get_directory_structure()
        assert structure.profiles_dir.exists()
        assert structure.hooks_dir.exists()
        assert structure.contexts_dir.exists()
        assert structure.contexts_shared_dir.exists()


def test_naming_convention_validation():
    """Test naming convention validation for different configuration types."""
    dm = DirectoryManager()
    
    # Test valid names
    valid_names = [
        ("developer", ConfigurationType.PROFILE),
        ("solutions-architect", ConfigurationType.PROFILE),
        ("setup-dev-env", ConfigurationType.HOOK),
        ("context-enhancer", ConfigurationType.HOOK),
        ("aws-best-practices", ConfigurationType.CONTEXT),
        ("development-guidelines", ConfigurationType.CONTEXT)
    ]
    
    for name, config_type in valid_names:
        is_valid, error = dm.validate_naming_convention(name, config_type)
        assert is_valid, f"'{name}' should be valid for {config_type.value}: {error}"
    
    # Test invalid names
    invalid_names = [
        ("Developer", ConfigurationType.PROFILE),  # uppercase
        ("solutions_architect", ConfigurationType.PROFILE),  # underscore
        ("setup-dev-env-", ConfigurationType.HOOK),  # trailing hyphen
        ("-context-enhancer", ConfigurationType.HOOK),  # leading hyphen
        ("aws best practices", ConfigurationType.CONTEXT),  # space
        ("", ConfigurationType.CONTEXT),  # empty
        ("a", ConfigurationType.CONTEXT),  # too short
        ("a" * 51, ConfigurationType.CONTEXT),  # too long
    ]
    
    for name, config_type in invalid_names:
        is_valid, error = dm.validate_naming_convention(name, config_type)
        assert not is_valid, f"'{name}' should be invalid for {config_type.value}"
        assert error, f"Error message should be provided for invalid name '{name}'"


def test_directory_structure_validation():
    """Test directory structure validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dm = DirectoryManager(temp_path)
        
        # Before creation, validation should fail
        validation_results = dm.validate_directory_structure()
        assert not all(validation_results.values())
        
        # After creation, validation should pass
        dm.create_directory_structure()
        validation_results = dm.validate_directory_structure()
        assert all(validation_results.values())


def test_configuration_file_organization():
    """Test configuration file organization and validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dm = DirectoryManager(temp_path)
        dm.create_directory_structure()
        
        # Create some test files
        structure = dm.get_directory_structure()
        
        # Valid files
        (structure.profiles_dir / "developer.yaml").touch()
        (structure.hooks_dir / "setup-env.yaml").touch()
        (structure.contexts_dir / "aws-guide.md").touch()
        
        # Invalid files (naming convention violations)
        (structure.profiles_dir / "BadProfile.yaml").touch()  # uppercase
        (structure.hooks_dir / "setup_env.yaml").touch()  # underscore
        
        # Organize files
        organized = dm.organize_configuration_files()
        
        # Check results
        assert len(organized["profiles"]) == 1  # Only valid profile
        assert len(organized["hooks"]) == 1  # Only valid hook
        assert len(organized["contexts"]) == 1  # Only valid context
        assert len(organized["errors"]) == 2  # Two naming violations


def test_name_suggestion():
    """Test name suggestion for invalid names."""
    dm = DirectoryManager()
    
    test_cases = [
        ("Developer", ConfigurationType.PROFILE, "developer"),
        ("setup_dev_env", ConfigurationType.HOOK, "setup-dev-env"),
        ("AWS Best Practices", ConfigurationType.CONTEXT, "aws-best-practices"),
        ("", ConfigurationType.PROFILE, "default-profile"),
        ("123invalid", ConfigurationType.HOOK, "config-123invalid"),
    ]
    
    for invalid_name, config_type, expected_pattern in test_cases:
        suggested = dm.suggest_valid_name(invalid_name, config_type)
        
        # Verify the suggestion is valid
        is_valid, _ = dm.validate_naming_convention(suggested, config_type)
        assert is_valid, f"Suggested name '{suggested}' should be valid"
        
        # For non-empty inputs, check if the suggestion contains some part of the original
        if invalid_name and expected_pattern != f"default-{config_type.value}":
            assert expected_pattern in suggested or suggested in expected_pattern


def test_get_configuration_files():
    """Test getting configuration files by type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dm = DirectoryManager(temp_path)
        dm.create_directory_structure()
        
        structure = dm.get_directory_structure()
        
        # Create test files
        (structure.profiles_dir / "developer.yaml").touch()
        (structure.profiles_dir / "admin.yml").touch()
        (structure.hooks_dir / "setup.yaml").touch()
        (structure.contexts_dir / "guide.md").touch()
        (structure.contexts_shared_dir / "shared.md").touch()
        
        # Test getting files by type
        profile_files = dm.get_configuration_files(ConfigurationType.PROFILE)
        hook_files = dm.get_configuration_files(ConfigurationType.HOOK)
        context_files = dm.get_configuration_files(ConfigurationType.CONTEXT)
        
        assert len(profile_files) == 2
        assert len(hook_files) == 1
        assert len(context_files) == 2  # includes shared contexts


if __name__ == "__main__":
    test_directory_manager_creation()
    test_naming_convention_validation()
    test_directory_structure_validation()
    test_configuration_file_organization()
    test_name_suggestion()
    test_get_configuration_files()
    print("All tests passed!")