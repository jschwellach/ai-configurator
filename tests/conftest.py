#!/usr/bin/env python3
"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path

import sys
sys.path.insert(0, 'src')

from ai_configurator.core.yaml_loader import YamlConfigLoader
from ai_configurator.core.validator import ConfigurationValidator


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with basic configuration structure."""
    temp_dir = tempfile.mkdtemp()
    test_dir = Path(temp_dir)
    
    # Create directory structure
    (test_dir / 'profiles').mkdir(exist_ok=True)
    (test_dir / 'hooks').mkdir(exist_ok=True)
    (test_dir / 'contexts').mkdir(exist_ok=True)
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def yaml_loader(temp_config_dir):
    """Create a YamlConfigLoader instance with temporary directory."""
    return YamlConfigLoader(temp_config_dir)


@pytest.fixture
def validator(temp_config_dir):
    """Create a ConfigurationValidator instance with temporary directory."""
    return ConfigurationValidator(temp_config_dir)


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        'name': 'test-profile',
        'description': 'Test profile for unit testing',
        'version': '1.0',
        'contexts': ['contexts/test-context.md'],
        'hooks': {
            'on_session_start': [
                {'name': 'test-hook', 'enabled': True}
            ]
        },
        'mcp_servers': ['core', 'development'],
        'settings': {
            'auto_backup': True,
            'validation_level': 'normal'
        }
    }


@pytest.fixture
def sample_hook_data():
    """Sample hook data for testing."""
    return {
        'name': 'test-hook',
        'description': 'Test hook for unit testing',
        'version': '1.0',
        'type': 'context',
        'trigger': 'on_session_start',
        'timeout': 30,
        'enabled': True,
        'context': {
            'sources': ['contexts/test-context.md'],
            'tags': ['test', 'development'],
            'priority': 1
        }
    }


@pytest.fixture
def sample_context_content():
    """Sample context file content for testing."""
    return """---
tags: [test, context, development]
priority: 1
category: testing
---

# Test Context

This is a test context file used for unit testing.

## Purpose

This context provides test data for validating the YAML configuration system.

## Usage

This context should be referenced by test profiles and hooks.
"""


@pytest.fixture
def populated_config_dir(temp_config_dir, sample_profile_data, sample_hook_data, sample_context_content):
    """Create a temporary directory populated with test configurations."""
    
    # Create profile file
    profile_file = temp_config_dir / 'profiles' / 'test-profile.yaml'
    with open(profile_file, 'w') as f:
        yaml.dump(sample_profile_data, f)
    
    # Create hook file
    hook_file = temp_config_dir / 'hooks' / 'test-hook.yaml'
    with open(hook_file, 'w') as f:
        yaml.dump(sample_hook_data, f)
    
    # Create context file
    context_file = temp_config_dir / 'contexts' / 'test-context.md'
    context_file.write_text(sample_context_content)
    
    return temp_config_dir


@pytest.fixture
def invalid_yaml_content():
    """Invalid YAML content for testing error handling."""
    return """
name: invalid-yaml
description: This has syntax errors
contexts:
  - context1.md
  - context2.md
    invalid_indentation: true
hooks:
  on_session_start:
    - name: test
      enabled: true
    - name: broken
      enabled: false
      invalid_yaml: [unclosed_list
"""


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
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if "comprehensive" in item.name.lower() or "workflow" in item.name.lower():
            item.add_marker(pytest.mark.slow)