#!/usr/bin/env python3
"""
Context switcher hook script for AI Configurator.

This script intelligently selects and loads contexts based on project type,
file patterns, and working environment to provide relevant guidance.
"""

import os
import sys
import json
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import fnmatch


class ProjectAnalyzer:
    """Analyzes project structure to determine project type and characteristics."""
    
    def __init__(self, project_root: Path):
        """Initialize the project analyzer."""
        self.project_root = project_root
        self.file_cache = {}
        self._scan_project()
    
    def _scan_project(self) -> None:
        """Scan the project directory to build file cache."""
        try:
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file() and not self._should_ignore_file(file_path):
                    relative_path = file_path.relative_to(self.project_root)
                    self.file_cache[str(relative_path)] = file_path
        except Exception as e:
            print(f"Warning: Error scanning project: {e}")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored during scanning."""
        ignore_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', '.DS_Store', '*.pyc', '*.pyo'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def detect_project_types(self, detection_config: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Detect project types based on configuration.
        
        Returns:
            List of (project_type, confidence_score) tuples
        """
        project_scores = defaultdict(float)
        
        for project_type, config in detection_config.items():
            score = self._calculate_project_score(project_type, config)
            if score > 0:
                project_scores[project_type] = score
        
        # Sort by score descending
        return sorted(project_scores.items(), key=lambda x: x[1], reverse=True)
    
    def _calculate_project_score(self, project_type: str, config: Dict[str, Any]) -> float:
        """Calculate confidence score for a specific project type."""
        total_score = 0.0
        max_possible_score = 0.0
        
        # Check file indicators
        indicators = config.get('indicators', [])
        if indicators:
            indicator_score = self._check_indicators(indicators)
            weight = 0.4  # From priority_weights in config
            total_score += indicator_score * weight
            max_possible_score += weight
        
        # Check file patterns
        patterns = config.get('file_patterns', [])
        if patterns:
            pattern_score = self._check_file_patterns(patterns)
            weight = 0.3
            total_score += pattern_score * weight
            max_possible_score += weight
        
        # Check keywords in files
        keywords = config.get('keywords', [])
        if keywords:
            keyword_score = self._check_keywords(keywords)
            weight = 0.2
            total_score += keyword_score * weight
            max_possible_score += weight
        
        # Apply project priority
        priority = config.get('priority', 5)
        priority_weight = priority / 10.0  # Normalize to 0-1
        total_score *= priority_weight
        
        # Return normalized score
        return total_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def _check_indicators(self, indicators: List[str]) -> float:
        """Check for presence of project indicator files."""
        found_indicators = 0
        
        for indicator in indicators:
            # Check if indicator exists as file or directory
            indicator_path = self.project_root / indicator
            if indicator_path.exists():
                found_indicators += 1
            else:
                # Check if it matches any files in cache
                for cached_file in self.file_cache.keys():
                    if fnmatch.fnmatch(cached_file, indicator):
                        found_indicators += 1
                        break
        
        return found_indicators / len(indicators) if indicators else 0.0
    
    def _check_file_patterns(self, patterns: List[str]) -> float:
        """Check for files matching specified patterns."""
        if not patterns:
            return 0.0
        
        matching_files = 0
        total_files = len(self.file_cache)
        
        if total_files == 0:
            return 0.0
        
        for file_path in self.file_cache.keys():
            for pattern in patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    matching_files += 1
                    break
        
        # Return ratio of matching files, capped at 1.0
        return min(matching_files / total_files * 10, 1.0)  # Scale up for better scoring
    
    def _check_keywords(self, keywords: List[str]) -> float:
        """Check for keywords in project files."""
        if not keywords:
            return 0.0
        
        keyword_matches = 0
        files_checked = 0
        
        # Check text files for keywords
        text_extensions = {'.py', '.js', '.ts', '.md', '.txt', '.yml', '.yaml', '.json'}
        
        for file_path, full_path in self.file_cache.items():
            if full_path.suffix.lower() in text_extensions:
                files_checked += 1
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                keyword_matches += 1
                                break
                except Exception:
                    continue
        
        return keyword_matches / files_checked if files_checked > 0 else 0.0


class ContextSwitcher:
    """Main class for intelligent context switching."""
    
    def __init__(self, config: Dict[str, Any], project_root: Path):
        """Initialize the context switcher."""
        self.config = config
        self.project_root = project_root
        self.analyzer = ProjectAnalyzer(project_root)
        self.switching_rules = config.get('switching_rules', {})
    
    def select_contexts(self, current_directory: Optional[str] = None) -> List[str]:
        """
        Select appropriate contexts based on project analysis.
        
        Args:
            current_directory: Current working directory for context switching
            
        Returns:
            List of context file paths to load
        """
        selected_contexts = []
        
        # 1. Detect project types
        detection_config = self.config.get('project_detection', {})
        project_types = self.analyzer.detect_project_types(detection_config)
        
        print(f"Detected project types: {project_types}")
        
        # 2. Apply manual overrides first
        override_contexts = self._apply_manual_overrides(current_directory)
        selected_contexts.extend(override_contexts)
        
        # 3. Select contexts from detected project types
        min_confidence = self.switching_rules.get('min_confidence', 0.6)
        max_contexts = self.switching_rules.get('max_contexts', 5)
        merge_types = self.switching_rules.get('merge_project_types', True)
        
        project_contexts = []
        for project_type, confidence in project_types:
            if confidence >= min_confidence:
                type_config = detection_config.get(project_type, {})
                contexts = type_config.get('contexts', [])
                
                if merge_types:
                    project_contexts.extend(contexts)
                else:
                    # Only use the highest confidence project type
                    project_contexts = contexts
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        for context in project_contexts:
            if context not in seen and context not in selected_contexts:
                selected_contexts.append(context)
                seen.add(context)
        
        # 4. Add fallback contexts if needed
        if not selected_contexts or len(selected_contexts) < 2:
            fallback_contexts = self.config.get('fallback_contexts', [])
            for context in fallback_contexts:
                if context not in selected_contexts:
                    selected_contexts.append(context)
        
        # 5. Limit to max contexts
        selected_contexts = selected_contexts[:max_contexts]
        
        # 6. Validate context files exist
        validated_contexts = self._validate_contexts(selected_contexts)
        
        return validated_contexts
    
    def _apply_manual_overrides(self, current_directory: Optional[str]) -> List[str]:
        """Apply manual context overrides based on directory and file types."""
        override_contexts = []
        overrides = self.config.get('manual_overrides', {})
        
        if current_directory:
            # Check directory-specific contexts
            dir_contexts = overrides.get('directory_contexts', {})
            for dir_pattern, contexts in dir_contexts.items():
                if fnmatch.fnmatch(current_directory, dir_pattern):
                    override_contexts.extend(contexts)
            
            # Check file type contexts for files in current directory
            file_type_contexts = overrides.get('file_type_contexts', {})
            current_path = Path(current_directory)
            
            if current_path.exists() and current_path.is_file():
                file_ext = current_path.suffix
                if file_ext in file_type_contexts:
                    override_contexts.extend(file_type_contexts[file_ext])
        
        return override_contexts
    
    def _validate_contexts(self, context_paths: List[str]) -> List[str]:
        """Validate that context files exist and are accessible."""
        validated = []
        
        for context_path in context_paths:
            # Try relative to project root first
            full_path = self.project_root / context_path
            if full_path.exists():
                validated.append(context_path)
                continue
            
            # Try as absolute path
            abs_path = Path(context_path)
            if abs_path.exists():
                validated.append(context_path)
                continue
            
            # Try relative to common locations
            common_locations = [
                Path.cwd(),
                Path.cwd() / 'examples',
                Path.home() / '.kiro'
            ]
            
            for location in common_locations:
                test_path = location / context_path
                if test_path.exists():
                    validated.append(str(test_path))
                    break
            else:
                print(f"Warning: Context file not found: {context_path}")
        
        return validated
    
    def generate_context_report(self, selected_contexts: List[str]) -> Dict[str, Any]:
        """Generate a report of the context switching decision."""
        project_types = self.analyzer.detect_project_types(
            self.config.get('project_detection', {})
        )
        
        return {
            'timestamp': str(Path.cwd()),
            'project_root': str(self.project_root),
            'detected_project_types': project_types,
            'selected_contexts': selected_contexts,
            'switching_rules': self.switching_rules,
            'total_files_analyzed': len(self.analyzer.file_cache)
        }


def find_project_root(start_path: Path) -> Path:
    """Find the project root directory."""
    current = start_path if start_path.is_dir() else start_path.parent
    
    # Look for common project indicators
    indicators = [
        '.git', 'pyproject.toml', 'setup.py', 'package.json',
        'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle'
    ]
    
    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent
    
    return start_path.parent if start_path.is_file() else start_path


def main():
    """Main entry point for the context switcher script."""
    parser = argparse.ArgumentParser(description='Intelligently switch contexts based on project type')
    parser.add_argument('--directory', help='Current working directory')
    parser.add_argument('--config', help='Path to hook configuration file')
    parser.add_argument('--output', help='Output file for selected contexts')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    # Determine working directory
    if args.directory:
        working_dir = Path(args.directory)
    else:
        working_dir = Path.cwd()
    
    # Find project root
    project_root = find_project_root(working_dir)
    print(f"Project root: {project_root}")
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            hook_config = yaml.safe_load(f)
            config = hook_config.get('config', {})
    
    # Set default configuration if none provided
    if not config:
        config = {
            'project_detection': {
                'python': {
                    'indicators': ['requirements.txt', 'pyproject.toml', 'setup.py'],
                    'file_patterns': ['**/*.py'],
                    'contexts': ['contexts/domains/data-science-best-practices.md'],
                    'priority': 8
                }
            },
            'switching_rules': {
                'max_contexts': 5,
                'min_confidence': 0.6,
                'merge_project_types': True
            },
            'fallback_contexts': ['contexts/workflows/code-review-process.md']
        }
    
    # Initialize context switcher
    switcher = ContextSwitcher(config, project_root)
    
    # Select contexts
    current_dir = str(working_dir.relative_to(project_root)) if working_dir != project_root else None
    selected_contexts = switcher.select_contexts(current_dir)
    
    print(f"Selected contexts: {selected_contexts}")
    
    # Output results
    if args.output:
        output_data = {
            'contexts': selected_contexts,
            'project_root': str(project_root),
            'working_directory': str(working_dir)
        }
        
        if args.report:
            output_data['report'] = switcher.generate_context_report(selected_contexts)
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Results written to: {args.output}")
    
    # Print contexts to stdout for consumption by other tools
    for context in selected_contexts:
        print(f"CONTEXT: {context}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())