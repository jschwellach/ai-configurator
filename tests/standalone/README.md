# Standalone Test Scripts

This directory contains standalone test scripts that can be run directly without pytest. These are typically used for manual testing, debugging, or demonstration purposes.

## Scripts

- `test_yaml_loader.py` - Standalone script for testing YAML loader functionality
- `test_comprehensive_validation.py` - Comprehensive validation testing script
- `test_validation_requirements.py` - Validation requirements testing script

## Usage

Run these scripts directly with Python:

```bash
python tests/standalone/test_yaml_loader.py
python tests/standalone/test_comprehensive_validation.py
python tests/standalone/test_validation_requirements.py
```

These scripts are self-contained and will create their own test data and environments.