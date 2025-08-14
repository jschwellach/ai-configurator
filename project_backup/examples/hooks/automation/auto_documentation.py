#!/usr/bin/env python3
"""
Auto-documentation hook script for AI Configurator.

This script automatically generates and updates project documentation
based on source code analysis and predefined templates.
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import ast
import re


class DocumentationGenerator:
    """Main class for generating project documentation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the documentation generator with configuration."""
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'docs/generated'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_documentation(self, file_path: str) -> bool:
        """
        Generate documentation for the specified file or project.
        
        Args:
            file_path: Path to the file that triggered the hook
            
        Returns:
            bool: True if documentation was generated successfully
        """
        try:
            print(f"Generating documentation for: {file_path}")
            
            # Determine project root
            project_root = self._find_project_root(file_path)
            
            # Generate different documentation sections
            sections = self.config.get('sections', [])
            
            if 'api_reference' in sections:
                self._generate_api_reference(project_root)
                
            if 'code_structure' in sections:
                self._generate_code_structure(project_root)
                
            if 'changelog' in sections:
                self._generate_changelog(project_root)
                
            if 'dependencies' in sections:
                self._generate_dependencies(project_root)
            
            # Generate in requested formats
            formats = self.config.get('output_formats', ['markdown'])
            for fmt in formats:
                self._export_documentation(fmt)
                
            print("Documentation generation completed successfully")
            return True
            
        except Exception as e:
            print(f"Error generating documentation: {e}")
            return False
    
    def _find_project_root(self, file_path: str) -> Path:
        """Find the project root directory."""
        current = Path(file_path).parent
        
        # Look for common project indicators
        indicators = [
            'pyproject.toml', 'setup.py', 'package.json', 
            '.git', 'requirements.txt', 'Cargo.toml'
        ]
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
            
        return Path(file_path).parent
    
    def _generate_api_reference(self, project_root: Path) -> None:
        """Generate API reference documentation."""
        print("Generating API reference...")
        
        api_docs = {
            'title': 'API Reference',
            'generated_at': datetime.now().isoformat(),
            'modules': []
        }
        
        # Find Python files
        python_files = list(project_root.rglob('*.py'))
        
        for py_file in python_files:
            if self._should_include_file(py_file):
                module_doc = self._analyze_python_module(py_file)
                if module_doc:
                    api_docs['modules'].append(module_doc)
        
        # Save API reference
        self._save_documentation('api_reference', api_docs)
    
    def _generate_code_structure(self, project_root: Path) -> None:
        """Generate code structure documentation."""
        print("Generating code structure...")
        
        structure = {
            'title': 'Code Structure',
            'generated_at': datetime.now().isoformat(),
            'tree': self._build_directory_tree(project_root)
        }
        
        self._save_documentation('code_structure', structure)
    
    def _generate_changelog(self, project_root: Path) -> None:
        """Generate or update changelog."""
        print("Generating changelog...")
        
        changelog_file = project_root / 'CHANGELOG.md'
        if changelog_file.exists():
            # Parse existing changelog
            with open(changelog_file, 'r') as f:
                content = f.read()
        else:
            content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n"
        
        changelog = {
            'title': 'Changelog',
            'generated_at': datetime.now().isoformat(),
            'content': content
        }
        
        self._save_documentation('changelog', changelog)
    
    def _generate_dependencies(self, project_root: Path) -> None:
        """Generate dependencies documentation."""
        print("Generating dependencies...")
        
        deps = {
            'title': 'Dependencies',
            'generated_at': datetime.now().isoformat(),
            'python': self._get_python_dependencies(project_root),
            'javascript': self._get_javascript_dependencies(project_root)
        }
        
        self._save_documentation('dependencies', deps)
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in documentation."""
        # Skip test files, __pycache__, etc.
        exclude_patterns = [
            '__pycache__', '.git', '.pytest_cache', 
            'node_modules', '.venv', 'venv'
        ]
        
        return not any(pattern in str(file_path) for pattern in exclude_patterns)
    
    def _analyze_python_module(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a Python module and extract documentation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module_doc = {
                'name': file_path.stem,
                'path': str(file_path),
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_doc = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_doc = {
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'args': [arg.arg for arg in item.args.args]
                            }
                            class_doc['methods'].append(method_doc)
                    
                    module_doc['classes'].append(class_doc)
                
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    func_doc = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node),
                        'args': [arg.arg for arg in node.args.args]
                    }
                    module_doc['functions'].append(func_doc)
            
            return module_doc
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _build_directory_tree(self, root: Path, max_depth: int = 3) -> Dict[str, Any]:
        """Build a directory tree structure."""
        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {'name': path.name, 'type': 'directory', 'truncated': True}
            
            if path.is_file():
                return {
                    'name': path.name,
                    'type': 'file',
                    'size': path.stat().st_size
                }
            
            children = []
            try:
                for child in sorted(path.iterdir()):
                    if not child.name.startswith('.') and self._should_include_file(child):
                        children.append(build_tree(child, current_depth + 1))
            except PermissionError:
                pass
            
            return {
                'name': path.name,
                'type': 'directory',
                'children': children
            }
        
        return build_tree(root)
    
    def _get_python_dependencies(self, project_root: Path) -> List[Dict[str, str]]:
        """Extract Python dependencies."""
        deps = []
        
        # Check requirements.txt
        req_file = project_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        deps.append({'name': line, 'source': 'requirements.txt'})
        
        # Check pyproject.toml
        pyproject_file = project_root / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                import tomli
                with open(pyproject_file, 'rb') as f:
                    data = tomli.load(f)
                    
                project_deps = data.get('project', {}).get('dependencies', [])
                for dep in project_deps:
                    deps.append({'name': dep, 'source': 'pyproject.toml'})
            except ImportError:
                print("tomli not available, skipping pyproject.toml parsing")
        
        return deps
    
    def _get_javascript_dependencies(self, project_root: Path) -> List[Dict[str, str]]:
        """Extract JavaScript dependencies."""
        deps = []
        
        package_json = project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                
                for dep_type in ['dependencies', 'devDependencies']:
                    for name, version in data.get(dep_type, {}).items():
                        deps.append({
                            'name': f"{name}@{version}",
                            'source': f'package.json ({dep_type})'
                        })
            except Exception as e:
                print(f"Error parsing package.json: {e}")
        
        return deps
    
    def _save_documentation(self, section: str, data: Dict[str, Any]) -> None:
        """Save documentation section to file."""
        # Save as JSON
        json_file = self.output_dir / f"{section}.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Save as Markdown if requested
        if 'markdown' in self.config.get('output_formats', []):
            md_file = self.output_dir / f"{section}.md"
            with open(md_file, 'w') as f:
                f.write(self._convert_to_markdown(data))
    
    def _convert_to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert documentation data to Markdown format."""
        md_content = f"# {data.get('title', 'Documentation')}\n\n"
        md_content += f"*Generated at: {data.get('generated_at', 'Unknown')}*\n\n"
        
        if 'modules' in data:
            md_content += "## Modules\n\n"
            for module in data['modules']:
                md_content += f"### {module['name']}\n\n"
                if module.get('docstring'):
                    md_content += f"{module['docstring']}\n\n"
                
                if module.get('classes'):
                    md_content += "#### Classes\n\n"
                    for cls in module['classes']:
                        md_content += f"##### {cls['name']}\n\n"
                        if cls.get('docstring'):
                            md_content += f"{cls['docstring']}\n\n"
                
                if module.get('functions'):
                    md_content += "#### Functions\n\n"
                    for func in module['functions']:
                        args_str = ', '.join(func.get('args', []))
                        md_content += f"##### {func['name']}({args_str})\n\n"
                        if func.get('docstring'):
                            md_content += f"{func['docstring']}\n\n"
        
        return md_content
    
    def _export_documentation(self, format_type: str) -> None:
        """Export documentation in specified format."""
        if format_type == 'html':
            self._export_html()
        elif format_type == 'json':
            # JSON files are already created in _save_documentation
            pass
    
    def _export_html(self) -> None:
        """Export documentation as HTML."""
        try:
            # Simple HTML export - in a real implementation, you might use
            # a template engine like Jinja2
            html_dir = self.output_dir / 'html'
            html_dir.mkdir(exist_ok=True)
            
            # Create a simple index.html
            with open(html_dir / 'index.html', 'w') as f:
                f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Project Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1, h2, h3 { color: #333; }
        pre { background: #f4f4f4; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Project Documentation</h1>
    <p>Generated documentation files:</p>
    <ul>
        <li><a href="../api_reference.md">API Reference</a></li>
        <li><a href="../code_structure.md">Code Structure</a></li>
        <li><a href="../changelog.md">Changelog</a></li>
        <li><a href="../dependencies.md">Dependencies</a></li>
    </ul>
</body>
</html>
                """)
            
            print(f"HTML documentation exported to {html_dir}")
            
        except Exception as e:
            print(f"Error exporting HTML: {e}")


def main():
    """Main entry point for the auto-documentation script."""
    parser = argparse.ArgumentParser(description='Auto-generate project documentation')
    parser.add_argument('--file', required=True, help='File that triggered the hook')
    parser.add_argument('--config', help='Path to hook configuration file')
    parser.add_argument('--output-dir', help='Output directory for documentation')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            hook_config = yaml.safe_load(f)
            config = hook_config.get('config', {})
    
    # Override output directory if specified
    if args.output_dir:
        config['output_dir'] = args.output_dir
    
    # Set default configuration
    default_config = {
        'output_dir': 'docs/generated',
        'output_formats': ['markdown', 'json'],
        'sections': ['api_reference', 'code_structure', 'changelog', 'dependencies'],
        'languages': {
            'python': {
                'docstring_style': 'google',
                'include_private': False,
                'include_tests': True
            }
        }
    }
    
    # Merge configurations
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    # Generate documentation
    generator = DocumentationGenerator(config)
    success = generator.generate_documentation(args.file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()