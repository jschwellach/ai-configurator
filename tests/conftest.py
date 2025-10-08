#!/usr/bin/env python3
"""Pytest configuration and shared fixtures for Phase 2 testing."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    test_dir = Path(temp_dir)
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with basic configuration structure."""
    temp_dir = tempfile.mkdtemp()
    test_dir = Path(temp_dir)
    
    # Create directory structure for Phase 2
    (test_dir / 'library').mkdir(exist_ok=True)
    (test_dir / 'personal').mkdir(exist_ok=True)
    (test_dir / 'agents').mkdir(exist_ok=True)
    (test_dir / 'registry').mkdir(exist_ok=True)
    (test_dir / 'backups').mkdir(exist_ok=True)
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "phase2: mark test as Phase 2 functionality"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "phase2" in str(item.fspath):
            item.add_marker(pytest.mark.phase2)
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
