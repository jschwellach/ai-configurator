"""System integration tests for template management components."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.ai_configurator.core.template_validator import TemplateValidator
from src.ai_configurator.core.template_quality_checker import TemplateQualityChecker
from src.ai_configurator.core.template_installer import TemplateInstaller, InstallationConfig
from src.ai_configurator.core.template_catalog_generator import TemplateCatalogGenerator
from src.ai_configurator.core.models import ValidationReport


class TestTemplateSystemIntegration:
    """System integration tests for complete template management workflows."""
    
    @pytest.fixture
    def integrated_system(self):
        """Create integrated template management system for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            examples_dir = workspace / "examples"
            target_dir = workspace / "target"
            
            # Create directory structures
            (examples_dir / "profiles" / "basic").mkdir(parents=True)
            (examples_dir / "contexts" / "domains").mkdir(parents=True)
            (examples_dir / "hooks" / "automation").mkdir(parents=True)
            target_dir.mkdir()
            
            # Create sample templates
            profile_data = {
                "metadata": {
                    "name": "test-profile",
                    "description": "Integration test profile",
                    "category": "basic",
                    "version": "1.0.0",
                    "created": "2024-01-01",
                    "complexity": "low"
                },
                "paths": ["contexts/domains/test-context.md"]
            }
            
            profile_file = examples_dir / "profiles" / "basic" / "test-profile.json"
            with open(profile_file, 'w') as f:
                json.dump(profile_data, f)
            
            context_content = """# Test Context

## Overview

Integration test context for system testing.

## Examples

```python
def test_function():
    return "test"
```
"""
            
            context_file = examples_dir / "contexts" / "domains" / "test-context.md"
            with open(context_file, 'w') as f:
                f.write(context_content)
            
            yield {
                "examples_dir": examples_dir,
                "target_dir": target_dir,
                "workspace": workspace
            }
    
    def test_complete_system_integration(self, integrated_system):
        """Test complete system integration workflow."""
        examples_dir = integrated_system["examples_dir"]
        target_dir = integrated_system["target_dir"]
        
        # Phase 1: Validation
        validator = TemplateValidator(examples_dir)
        validation_report = validator.validate_all_templates()
        assert validation_report.is_valid
        
        # Phase 2: Quality Assessment
        quality_checker = TemplateQualityChecker(examples_dir)
        quality_reports = quality_checker.assess_all_templates()
        assert len(quality_reports) > 0
        
        # Phase 3: Installation
        config = InstallationConfig(target_directory=target_dir, examples_directory=examples_dir)
        installer = TemplateInstaller(config)
        
        with patch.object(installer.validator, 'validate_profile_template') as mock_val:
            mock_val.return_value = ValidationReport(is_valid=True, errors=[], warnings=[])
            
            templates = installer.discover_templates()
            assert len(templates) > 0
            
            results = installer.install_multiple_templates(list(templates.keys()))
            assert all(r.success for r in results)
        
        # Phase 4: Catalog Generation
        generator = TemplateCatalogGenerator(str(examples_dir))
        catalog = generator.generate_catalog()
        assert catalog.total_count > 0
        
        # Verify end-to-end consistency
        assert len(quality_reports) == catalog.total_count
        assert len(templates) == catalog.total_count