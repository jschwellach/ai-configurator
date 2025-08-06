#!/usr/bin/env python3
"""
Template Catalog Generator

Automatically generates comprehensive documentation for all example templates
in the AI Configurator system. This includes profiles, contexts, hooks, and
complete workflows.
"""

import json
import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class TemplateMetadata:
    """Metadata for a template."""
    name: str
    description: str
    category: str
    template_type: str  # profile, context, hook, workflow
    version: str = "1.0.0"
    author: str = "AI Configurator Team"
    created: str = ""
    updated: str = ""
    tags: List[str] = None
    complexity: str = "medium"
    prerequisites: List[str] = None
    related_templates: List[str] = None
    file_path: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.prerequisites is None:
            self.prerequisites = []
        if self.related_templates is None:
            self.related_templates = []

@dataclass
class TemplateCatalog:
    """Complete catalog of all templates."""
    profiles: List[TemplateMetadata]
    contexts: List[TemplateMetadata]
    hooks: List[TemplateMetadata]
    workflows: List[TemplateMetadata]
    generated_at: str
    total_count: int
    
    def __post_init__(self):
        self.total_count = len(self.profiles) + len(self.contexts) + len(self.hooks) + len(self.workflows)

class TemplateCatalogGenerator:
    """Generates comprehensive documentation for all example templates."""
    
    def __init__(self, examples_dir: str = "examples"):
        self.examples_dir = Path(examples_dir)
        self.catalog = TemplateCatalog(
            profiles=[],
            contexts=[],
            hooks=[],
            workflows=[],
            generated_at=datetime.now().isoformat(),
            total_count=0
        )
    
    def generate_catalog(self) -> TemplateCatalog:
        """Generate complete template catalog."""
        print("🔍 Scanning templates...")
        
        # Scan each template type
        self._scan_profiles()
        self._scan_contexts()
        self._scan_hooks()
        self._scan_workflows()
        
        # Update total count
        self.catalog.total_count = (
            len(self.catalog.profiles) + 
            len(self.catalog.contexts) + 
            len(self.catalog.hooks) + 
            len(self.catalog.workflows)
        )
        
        print(f"✅ Found {self.catalog.total_count} templates")
        return self.catalog
    
    def _scan_profiles(self):
        """Scan profile templates."""
        profiles_dir = self.examples_dir / "profiles"
        if not profiles_dir.exists():
            return
        
        for profile_file in profiles_dir.rglob("*.json"):
            if profile_file.name.startswith('.'):
                continue
                
            try:
                metadata = self._extract_profile_metadata(profile_file)
                if metadata:
                    self.catalog.profiles.append(metadata)
            except Exception as e:
                print(f"⚠️  Error processing profile {profile_file}: {e}")
    
    def _scan_contexts(self):
        """Scan context templates."""
        contexts_dir = self.examples_dir / "contexts"
        if not contexts_dir.exists():
            return
        
        for context_file in contexts_dir.rglob("*.md"):
            if context_file.name.startswith('.'):
                continue
                
            try:
                metadata = self._extract_context_metadata(context_file)
                if metadata:
                    self.catalog.contexts.append(metadata)
            except Exception as e:
                print(f"⚠️  Error processing context {context_file}: {e}")
    
    def _scan_hooks(self):
        """Scan hook templates."""
        hooks_dir = self.examples_dir / "hooks"
        if not hooks_dir.exists():
            return
        
        for hook_file in hooks_dir.rglob("*.yaml"):
            if hook_file.name.startswith('.'):
                continue
                
            try:
                metadata = self._extract_hook_metadata(hook_file)
                if metadata:
                    self.catalog.hooks.append(metadata)
            except Exception as e:
                print(f"⚠️  Error processing hook {hook_file}: {e}")
    
    def _scan_workflows(self):
        """Scan workflow templates."""
        workflows_dir = self.examples_dir / "workflows"
        if not workflows_dir.exists():
            return
        
        for workflow_dir in workflows_dir.iterdir():
            if not workflow_dir.is_dir() or workflow_dir.name.startswith('.'):
                continue
                
            try:
                metadata = self._extract_workflow_metadata(workflow_dir)
                if metadata:
                    self.catalog.workflows.append(metadata)
            except Exception as e:
                print(f"⚠️  Error processing workflow {workflow_dir}: {e}")
    
    def _extract_profile_metadata(self, profile_file: Path) -> Optional[TemplateMetadata]:
        """Extract metadata from a profile JSON file."""
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Remove JSON comments for parsing
            content_clean = re.sub(r'//.*?\n', '\n', content)
            content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
            
            # Remove any control characters that might cause issues
            content_clean = re.sub(r'[\x00-\x1F\x7F]', '', content_clean)
            
            data = json.loads(content_clean)
            
            # Extract metadata from the profile
            metadata_section = data.get('metadata', {})
            
            # Determine category from file path
            category = self._determine_category_from_path(profile_file)
            
            return TemplateMetadata(
                name=metadata_section.get('name', profile_file.stem),
                description=metadata_section.get('description', 'Profile template'),
                category=category,
                template_type='profile',
                version=metadata_section.get('version', '1.0.0'),
                author=metadata_section.get('author', 'AI Configurator Team'),
                created=metadata_section.get('created', ''),
                updated=metadata_section.get('updated', ''),
                tags=metadata_section.get('tags', []),
                complexity=metadata_section.get('complexity', 'medium'),
                prerequisites=metadata_section.get('prerequisites', []),
                related_templates=metadata_section.get('related_templates', []),
                file_path=str(profile_file.relative_to(self.examples_dir))
            )
        except Exception as e:
            print(f"Error parsing profile {profile_file}: {e}")
            return None
    
    def _extract_context_metadata(self, context_file: Path) -> Optional[TemplateMetadata]:
        """Extract metadata from a context markdown file."""
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from first heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else context_file.stem
            
            # Extract description from overview section
            overview_match = re.search(r'## Overview\s*\n\n(.+?)(?=\n##|\n$)', content, re.DOTALL)
            description = overview_match.group(1).strip()[:200] + "..." if overview_match else "Context template"
            
            # Determine category from file path
            category = self._determine_category_from_path(context_file)
            
            # Extract tags from content (look for common keywords)
            tags = self._extract_tags_from_content(content)
            
            return TemplateMetadata(
                name=context_file.stem.replace('-', ' ').title(),
                description=description,
                category=category,
                template_type='context',
                tags=tags,
                complexity=self._determine_complexity_from_content(content),
                file_path=str(context_file.relative_to(self.examples_dir))
            )
        except Exception as e:
            print(f"Error parsing context {context_file}: {e}")
            return None
    
    def _extract_hook_metadata(self, hook_file: Path) -> Optional[TemplateMetadata]:
        """Extract metadata from a hook YAML file."""
        try:
            with open(hook_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return None
            
            # Determine category from file path
            category = self._determine_category_from_path(hook_file)
            
            # Extract metadata from hook configuration
            metadata_section = data.get('metadata', {})
            
            return TemplateMetadata(
                name=data.get('name', hook_file.stem),
                description=data.get('description', 'Hook template'),
                category=category,
                template_type='hook',
                version=data.get('version', '1.0.0'),
                author=metadata_section.get('author', 'AI Configurator Team'),
                tags=self._extract_hook_tags(data),
                complexity=metadata_section.get('complexity', 'medium'),
                prerequisites=metadata_section.get('prerequisites', []),
                related_templates=metadata_section.get('related_hooks', []),
                file_path=str(hook_file.relative_to(self.examples_dir))
            )
        except Exception as e:
            print(f"Error parsing hook {hook_file}: {e}")
            return None
    
    def _extract_workflow_metadata(self, workflow_dir: Path) -> Optional[TemplateMetadata]:
        """Extract metadata from a workflow directory."""
        try:
            # Look for README.md for description
            readme_file = workflow_dir / "README.md"
            description = "Complete workflow template"
            
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract description from first paragraph
                desc_match = re.search(r'^(?:# .+\n\n)?(.+?)(?=\n\n|\n#|\n$)', content, re.DOTALL)
                if desc_match:
                    description = desc_match.group(1).strip()[:200] + "..."
            
            # Look for profile.json for additional metadata
            profile_file = workflow_dir / "profile.json"
            tags = []
            complexity = "high"  # Workflows are typically complex
            
            if profile_file.exists():
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content_clean = re.sub(r'//.*?\n', '\n', content)
                    content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
                    data = json.loads(content_clean)
                    
                    metadata_section = data.get('metadata', {})
                    tags = metadata_section.get('tags', [])
                    complexity = metadata_section.get('complexity', 'high')
                except:
                    pass
            
            return TemplateMetadata(
                name=workflow_dir.name.replace('-', ' ').title(),
                description=description,
                category='workflow',
                template_type='workflow',
                tags=tags + ['workflow', 'complete'],
                complexity=complexity,
                file_path=str(workflow_dir.relative_to(self.examples_dir))
            )
        except Exception as e:
            print(f"Error parsing workflow {workflow_dir}: {e}")
            return None
    
    def _determine_category_from_path(self, file_path: Path) -> str:
        """Determine template category from file path."""
        path_parts = file_path.parts
        
        if 'basic' in path_parts:
            return 'basic'
        elif 'professional' in path_parts:
            return 'professional'
        elif 'advanced' in path_parts:
            return 'advanced'
        elif 'automation' in path_parts:
            return 'automation'
        elif 'enhancement' in path_parts:
            return 'enhancement'
        elif 'domains' in path_parts:
            return 'domain'
        elif 'workflows' in path_parts:
            return 'workflow'
        else:
            return 'general'
    
    def _extract_tags_from_content(self, content: str) -> List[str]:
        """Extract relevant tags from content."""
        tags = []
        
        # Common keywords to look for
        keywords = {
            'python': ['python', 'pip', 'conda', 'jupyter'],
            'javascript': ['javascript', 'node', 'npm', 'js'],
            'data-science': ['data science', 'machine learning', 'ml', 'pandas', 'numpy'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'deployment'],
            'security': ['security', 'authentication', 'authorization', 'encryption'],
            'documentation': ['documentation', 'docs', 'readme', 'markdown'],
            'testing': ['testing', 'test', 'pytest', 'unittest'],
            'automation': ['automation', 'script', 'workflow', 'pipeline']
        }
        
        content_lower = content.lower()
        for tag, words in keywords.items():
            if any(word in content_lower for word in words):
                tags.append(tag)
        
        return tags
    
    def _determine_complexity_from_content(self, content: str) -> str:
        """Determine complexity based on content length and structure."""
        lines = content.split('\n')
        sections = len([line for line in lines if line.startswith('##')])
        
        if len(content) < 1000 or sections < 3:
            return 'low'
        elif len(content) < 5000 or sections < 8:
            return 'medium'
        else:
            return 'high'
    
    def _extract_hook_tags(self, hook_data: Dict[str, Any]) -> List[str]:
        """Extract tags from hook configuration."""
        tags = []
        
        # Add trigger type as tag
        trigger = hook_data.get('trigger', '')
        if trigger:
            tags.append(f"trigger-{trigger.replace('_', '-')}")
        
        # Add type as tag
        hook_type = hook_data.get('type', '')
        if hook_type:
            tags.append(hook_type)
        
        # Add context tags if available
        context = hook_data.get('context', {})
        if context and 'tags' in context:
            tags.extend(context['tags'])
        
        return tags
    
    def generate_markdown_catalog(self, output_file: str = "docs/TEMPLATE_CATALOG.md") -> str:
        """Generate markdown documentation for the template catalog."""
        catalog = self.generate_catalog()
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        markdown_content = self._build_markdown_content(catalog)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📝 Generated catalog: {output_file}")
        return str(output_path)
    
    def _build_markdown_content(self, catalog: TemplateCatalog) -> str:
        """Build the markdown content for the catalog."""
        content = []
        
        # Header
        content.append("# AI Configurator Template Catalog")
        content.append("")
        content.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append("")
        content.append("This catalog provides a comprehensive overview of all available example templates in the AI Configurator system.")
        content.append("")
        
        # Summary
        content.append("## Summary")
        content.append("")
        content.append(f"- **Total Templates**: {catalog.total_count}")
        content.append(f"- **Profiles**: {len(catalog.profiles)}")
        content.append(f"- **Contexts**: {len(catalog.contexts)}")
        content.append(f"- **Hooks**: {len(catalog.hooks)}")
        content.append(f"- **Workflows**: {len(catalog.workflows)}")
        content.append("")
        
        # Table of Contents
        content.append("## Table of Contents")
        content.append("")
        content.append("- [Profiles](#profiles)")
        content.append("- [Contexts](#contexts)")
        content.append("- [Hooks](#hooks)")
        content.append("- [Workflows](#workflows)")
        content.append("- [Quick Reference](#quick-reference)")
        content.append("")
        
        # Profiles section
        if catalog.profiles:
            content.append("## Profiles")
            content.append("")
            content.append("Profile templates define which contexts and hooks to load for specific use cases.")
            content.append("")
            content.extend(self._build_template_section(catalog.profiles))
        
        # Contexts section
        if catalog.contexts:
            content.append("## Contexts")
            content.append("")
            content.append("Context templates provide domain-specific guidance and best practices.")
            content.append("")
            content.extend(self._build_template_section(catalog.contexts))
        
        # Hooks section
        if catalog.hooks:
            content.append("## Hooks")
            content.append("")
            content.append("Hook templates define automation workflows and triggers.")
            content.append("")
            content.extend(self._build_template_section(catalog.hooks))
        
        # Workflows section
        if catalog.workflows:
            content.append("## Workflows")
            content.append("")
            content.append("Complete workflow templates combine profiles, contexts, and hooks for specific use cases.")
            content.append("")
            content.extend(self._build_template_section(catalog.workflows))
        
        # Quick reference
        content.append("## Quick Reference")
        content.append("")
        content.extend(self._build_quick_reference(catalog))
        
        return "\n".join(content)
    
    def _build_template_section(self, templates: List[TemplateMetadata]) -> List[str]:
        """Build markdown section for a list of templates."""
        content = []
        
        # Group by category
        by_category = defaultdict(list)
        for template in templates:
            by_category[template.category].append(template)
        
        for category, category_templates in sorted(by_category.items()):
            content.append(f"### {category.title()} {category_templates[0].template_type.title()}s")
            content.append("")
            
            for template in sorted(category_templates, key=lambda t: t.name):
                content.append(f"#### {template.name}")
                content.append("")
                content.append(f"**Description**: {template.description}")
                content.append("")
                content.append(f"**File**: `{template.file_path}`")
                content.append("")
                
                if template.tags:
                    tags_str = " ".join([f"`{tag}`" for tag in template.tags])
                    content.append(f"**Tags**: {tags_str}")
                    content.append("")
                
                content.append(f"**Complexity**: {template.complexity}")
                content.append("")
                
                if template.prerequisites:
                    content.append("**Prerequisites**:")
                    for prereq in template.prerequisites:
                        content.append(f"- {prereq}")
                    content.append("")
                
                if template.related_templates:
                    content.append("**Related Templates**:")
                    for related in template.related_templates:
                        content.append(f"- {related}")
                    content.append("")
                
                content.append("---")
                content.append("")
        
        return content
    
    def _build_quick_reference(self, catalog: TemplateCatalog) -> List[str]:
        """Build quick reference tables."""
        content = []
        
        # By complexity
        content.append("### By Complexity")
        content.append("")
        content.append("| Complexity | Count | Templates |")
        content.append("|------------|-------|-----------|")
        
        all_templates = catalog.profiles + catalog.contexts + catalog.hooks + catalog.workflows
        by_complexity = defaultdict(list)
        for template in all_templates:
            by_complexity[template.complexity].append(template.name)
        
        for complexity in ['low', 'medium', 'high']:
            if complexity in by_complexity:
                templates_str = ", ".join(by_complexity[complexity][:5])
                if len(by_complexity[complexity]) > 5:
                    templates_str += f" (+{len(by_complexity[complexity]) - 5} more)"
                content.append(f"| {complexity.title()} | {len(by_complexity[complexity])} | {templates_str} |")
        
        content.append("")
        
        # By category
        content.append("### By Category")
        content.append("")
        content.append("| Category | Count | Description |")
        content.append("|----------|-------|-------------|")
        
        by_category = defaultdict(int)
        category_descriptions = {
            'basic': 'Simple templates for getting started',
            'professional': 'Templates for professional use cases',
            'advanced': 'Complex templates for power users',
            'automation': 'Templates for automation workflows',
            'enhancement': 'Templates for enhancing functionality',
            'domain': 'Domain-specific guidance templates',
            'workflow': 'Process and workflow templates',
            'general': 'General-purpose templates'
        }
        
        for template in all_templates:
            by_category[template.category] += 1
        
        for category, count in sorted(by_category.items()):
            description = category_descriptions.get(category, 'Template category')
            content.append(f"| {category.title()} | {count} | {description} |")
        
        content.append("")
        
        return content
    
    def generate_json_catalog(self, output_file: str = "docs/template_catalog.json") -> str:
        """Generate JSON catalog for programmatic access."""
        catalog = self.generate_catalog()
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        catalog_dict = asdict(catalog)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_dict, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Generated JSON catalog: {output_file}")
        return str(output_path)
    
    def generate_html_catalog(self, output_file: str = "docs/template_catalog.html") -> str:
        """Generate HTML catalog for web viewing."""
        catalog = self.generate_catalog()
        
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = self._build_html_content(catalog)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 Generated HTML catalog: {output_file}")
        return str(output_path)
    
    def _build_html_content(self, catalog: TemplateCatalog) -> str:
        """Build HTML content for the catalog."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Configurator Template Catalog</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .template {{ border: 1px solid #bdc3c7; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .template h4 {{ margin-top: 0; color: #2980b9; }}
        .tag {{ background: #3498db; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-right: 5px; }}
        .complexity {{ font-weight: bold; }}
        .complexity.low {{ color: #27ae60; }}
        .complexity.medium {{ color: #f39c12; }}
        .complexity.high {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 10px; text-align: left; }}
        th {{ background: #34495e; color: white; }}
        .generated {{ color: #7f8c8d; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Configurator Template Catalog</h1>
        <p class="generated">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <ul>
                <li><strong>Total Templates:</strong> {catalog.total_count}</li>
                <li><strong>Profiles:</strong> {len(catalog.profiles)}</li>
                <li><strong>Contexts:</strong> {len(catalog.contexts)}</li>
                <li><strong>Hooks:</strong> {len(catalog.hooks)}</li>
                <li><strong>Workflows:</strong> {len(catalog.workflows)}</li>
            </ul>
        </div>
"""
        
        # Add sections for each template type
        for template_type, templates in [
            ('Profiles', catalog.profiles),
            ('Contexts', catalog.contexts),
            ('Hooks', catalog.hooks),
            ('Workflows', catalog.workflows)
        ]:
            if templates:
                html += f"<h2>{template_type}</h2>\n"
                
                for template in sorted(templates, key=lambda t: t.name):
                    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in template.tags])
                    
                    html += f"""
                    <div class="template">
                        <h4>{template.name}</h4>
                        <p><strong>Description:</strong> {template.description}</p>
                        <p><strong>File:</strong> <code>{template.file_path}</code></p>
                        <p><strong>Category:</strong> {template.category}</p>
                        <p><strong>Complexity:</strong> <span class="complexity {template.complexity}">{template.complexity}</span></p>
                        {f'<p><strong>Tags:</strong> {tags_html}</p>' if template.tags else ''}
                        {f'<p><strong>Prerequisites:</strong> {", ".join(template.prerequisites)}</p>' if template.prerequisites else ''}
                    </div>
                    """
        
        html += """
    </div>
</body>
</html>"""
        
        return html

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate AI Configurator template catalog")
    parser.add_argument("--examples-dir", default="examples", help="Path to examples directory")
    parser.add_argument("--output-dir", default="docs", help="Output directory for generated files")
    parser.add_argument("--format", choices=["markdown", "json", "html", "all"], default="all", help="Output format")
    
    args = parser.parse_args()
    
    generator = TemplateCatalogGenerator(args.examples_dir)
    
    if args.format in ["markdown", "all"]:
        generator.generate_markdown_catalog(f"{args.output_dir}/TEMPLATE_CATALOG.md")
    
    if args.format in ["json", "all"]:
        generator.generate_json_catalog(f"{args.output_dir}/template_catalog.json")
    
    if args.format in ["html", "all"]:
        generator.generate_html_catalog(f"{args.output_dir}/template_catalog.html")
    
    print("✅ Template catalog generation complete!")

if __name__ == "__main__":
    main()