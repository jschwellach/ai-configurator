#!/usr/bin/env python3
"""
Update Template Catalog Script

This script automatically updates the template catalog when templates are added or modified.
It can be run manually or integrated into CI/CD pipelines.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_configurator.core.template_catalog_generator import TemplateCatalogGenerator

def main():
    """Update the template catalog."""
    print("🔄 Updating AI Configurator Template Catalog...")
    
    # Determine paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    examples_dir = project_root / "examples"
    output_dir = project_root / "docs" / "generated"
    
    # Create generator
    generator = TemplateCatalogGenerator(str(examples_dir))
    
    # Generate all formats
    try:
        # Generate markdown catalog
        markdown_file = generator.generate_markdown_catalog(str(output_dir / "TEMPLATE_CATALOG.md"))
        print(f"✅ Updated markdown catalog: {markdown_file}")
        
        # Generate JSON catalog
        json_file = generator.generate_json_catalog(str(output_dir / "template_catalog.json"))
        print(f"✅ Updated JSON catalog: {json_file}")
        
        # Generate HTML catalog
        html_file = generator.generate_html_catalog(str(output_dir / "template_catalog.html"))
        print(f"✅ Updated HTML catalog: {html_file}")
        
        print("\n🎉 Template catalog update complete!")
        print(f"📊 Total templates cataloged: {generator.catalog.total_count}")
        
    except Exception as e:
        print(f"❌ Error updating catalog: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()