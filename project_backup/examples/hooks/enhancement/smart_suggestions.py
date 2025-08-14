#!/usr/bin/env python3
"""
Smart suggestions hook script for AI Configurator.

This script generates context-aware suggestions based on current project state,
user activity, and loaded contexts to provide intelligent recommendations.
"""

import os
import sys
import json
import yaml
import argparse
import re
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import fnmatch


class SuggestionPattern:
    """Represents a suggestion pattern with metadata."""
    
    def __init__(self, pattern_id: str, name: str, description: str, 
                 pattern_type: str, confidence: float, impact: str):
        self.pattern_id = pattern_id
        self.name = name
        self.description = description
        self.pattern_type = pattern_type
        self.confidence = confidence
        self.impact = impact
        self.created_at = datetime.now()


class CodeAnalyzer:
    """Analyzes code files to identify improvement opportunities."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.patterns = self._load_code_patterns()
    
    def _load_code_patterns(self) -> Dict[str, Any]:
        """Load predefined code analysis patterns."""
        return {
            'missing_error_handling': {
                'python': [
                    r'open\s*\([^)]+\)\s*(?!.*except)',
                    r'requests\.\w+\([^)]+\)\s*(?!.*except)',
                    r'json\.loads?\([^)]+\)\s*(?!.*except)'
                ],
                'javascript': [
                    r'JSON\.parse\([^)]+\)\s*(?!.*catch)',
                    r'fetch\([^)]+\)\s*(?!.*catch)',
                    r'require\([^)]+\)\s*(?!.*catch)'
                ]
            },
            'unused_imports': {
                'python': [
                    r'^import\s+(\w+)(?:\s+as\s+\w+)?$',
                    r'^from\s+[\w.]+\s+import\s+(.+)$'
                ]
            },
            'long_functions': {
                'python': [r'def\s+\w+\([^)]*\):'],
                'javascript': [r'function\s+\w+\([^)]*\)\s*{']
            },
            'missing_docstrings': {
                'python': [r'def\s+\w+\([^)]*\):\s*(?!"""|\'\'\')']
            },
            'hardcoded_values': {
                'python': [
                    r'["\'][^"\']*(?:password|secret|key|token)[^"\']*["\']',
                    r'["\'][^"\']*(?:localhost|127\.0\.0\.1)[^"\']*["\']'
                ],
                'javascript': [
                    r'["\'][^"\']*(?:password|secret|key|token)[^"\']*["\']',
                    r'["\'][^"\']*(?:localhost|127\.0\.0\.1)[^"\']*["\']'
                ]
            },
            'security_vulnerabilities': {
                'python': [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'subprocess\.call\([^)]*shell\s*=\s*True'
                ],
                'javascript': [
                    r'eval\s*\(',
                    r'innerHTML\s*=',
                    r'document\.write\s*\('
                ]
            }
        }
    
    def analyze_file(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """
        Analyze a file for potential improvements.
        
        Args:
            file_path: Path to the file being analyzed
            content: File content as string
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        file_ext = file_path.suffix.lower()
        
        # Determine language
        language = self._detect_language(file_ext)
        if not language:
            return suggestions
        
        # Analyze for each pattern type
        for pattern_type, lang_patterns in self.patterns.items():
            if language in lang_patterns:
                pattern_suggestions = self._analyze_pattern(
                    content, pattern_type, lang_patterns[language], file_path
                )
                suggestions.extend(pattern_suggestions)
        
        # Language-specific analysis
        if language == 'python':
            suggestions.extend(self._analyze_python_specific(file_path, content))
        elif language == 'javascript':
            suggestions.extend(self._analyze_javascript_specific(file_path, content))
        
        return suggestions
    
    def _detect_language(self, file_ext: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',  # TypeScript treated as JavaScript for patterns
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }
        return language_map.get(file_ext)
    
    def _analyze_pattern(self, content: str, pattern_type: str, 
                        patterns: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Analyze content for specific patterns."""
        suggestions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    suggestion = self._create_suggestion(
                        pattern_type, line.strip(), i, file_path
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_python_specific(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Perform Python-specific analysis."""
        suggestions = []
        
        try:
            tree = ast.parse(content)
            
            # Check for long functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 50:  # Configurable threshold
                        suggestions.append({
                            'type': 'code_improvement',
                            'category': 'long_functions',
                            'message': f"Function '{node.name}' is {func_lines} lines long. Consider breaking it into smaller functions.",
                            'line': node.lineno,
                            'file': str(file_path),
                            'confidence': 0.8,
                            'impact': 'medium',
                            'suggestion': f"Break down the '{node.name}' function into smaller, more focused functions."
                        })
                
                # Check for missing docstrings
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        suggestions.append({
                            'type': 'documentation',
                            'category': 'missing_docstrings',
                            'message': f"{node.__class__.__name__.lower().replace('def', '')} '{node.name}' is missing a docstring.",
                            'line': node.lineno,
                            'file': str(file_path),
                            'confidence': 0.9,
                            'impact': 'low',
                            'suggestion': f"Add a docstring to explain the purpose and parameters of '{node.name}'."
                        })
        
        except SyntaxError:
            # File has syntax errors, suggest syntax check
            suggestions.append({
                'type': 'code_improvement',
                'category': 'syntax_error',
                'message': "File contains syntax errors that prevent analysis.",
                'line': 1,
                'file': str(file_path),
                'confidence': 1.0,
                'impact': 'high',
                'suggestion': "Fix syntax errors in the file to enable proper analysis and execution."
            })
        
        return suggestions
    
    def _analyze_javascript_specific(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Perform JavaScript-specific analysis."""
        suggestions = []
        lines = content.split('\n')
        
        # Check for console.log statements (should be removed in production)
        for i, line in enumerate(lines, 1):
            if re.search(r'console\.log\s*\(', line):
                suggestions.append({
                    'type': 'code_improvement',
                    'category': 'debug_statements',
                    'message': "Console.log statement found - consider removing for production.",
                    'line': i,
                    'file': str(file_path),
                    'confidence': 0.7,
                    'impact': 'low',
                    'suggestion': "Remove console.log statements or replace with proper logging."
                })
        
        return suggestions
    
    def _create_suggestion(self, pattern_type: str, line_content: str, 
                          line_number: int, file_path: Path) -> Dict[str, Any]:
        """Create a suggestion dictionary from pattern match."""
        suggestion_templates = {
            'missing_error_handling': {
                'message': "Potential operation without error handling detected.",
                'suggestion': "Add try-catch or error handling for this operation.",
                'confidence': 0.8,
                'impact': 'medium'
            },
            'unused_imports': {
                'message': "Potentially unused import detected.",
                'suggestion': "Remove unused imports to improve code clarity.",
                'confidence': 0.6,
                'impact': 'low'
            },
            'hardcoded_values': {
                'message': "Hardcoded sensitive value detected.",
                'suggestion': "Move sensitive values to environment variables or configuration files.",
                'confidence': 0.9,
                'impact': 'high'
            },
            'security_vulnerabilities': {
                'message': "Potential security vulnerability detected.",
                'suggestion': "Review and secure this code pattern to prevent security issues.",
                'confidence': 0.9,
                'impact': 'high'
            }
        }
        
        template = suggestion_templates.get(pattern_type, {
            'message': f"Code pattern '{pattern_type}' detected.",
            'suggestion': f"Review the '{pattern_type}' pattern for potential improvements.",
            'confidence': 0.5,
            'impact': 'medium'
        })
        
        return {
            'type': 'code_improvement',
            'category': pattern_type,
            'message': template['message'],
            'line': line_number,
            'file': str(file_path),
            'confidence': template['confidence'],
            'impact': template['impact'],
            'suggestion': template['suggestion'],
            'context': line_content[:100]  # First 100 chars for context
        }


class ContextAnalyzer:
    """Analyzes loaded contexts to generate context-aware suggestions."""
    
    def __init__(self, context_paths: List[str]):
        """Initialize with list of context file paths."""
        self.contexts = self._load_contexts(context_paths)
    
    def _load_contexts(self, context_paths: List[str]) -> Dict[str, str]:
        """Load context files and extract content."""
        contexts = {}
        
        for context_path in context_paths:
            try:
                path = Path(context_path)
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        contexts[context_path] = f.read()
                else:
                    print(f"Warning: Context file not found: {context_path}")
            except Exception as e:
                print(f"Error loading context {context_path}: {e}")
        
        return contexts
    
    def generate_context_suggestions(self, file_path: Path, 
                                   file_content: str) -> List[Dict[str, Any]]:
        """Generate suggestions based on loaded contexts."""
        suggestions = []
        
        for context_path, context_content in self.contexts.items():
            context_suggestions = self._analyze_against_context(
                file_path, file_content, context_path, context_content
            )
            suggestions.extend(context_suggestions)
        
        return suggestions
    
    def _analyze_against_context(self, file_path: Path, file_content: str,
                               context_path: str, context_content: str) -> List[Dict[str, Any]]:
        """Analyze file against a specific context."""
        suggestions = []
        
        # Extract best practices from context
        best_practices = self._extract_best_practices(context_content)
        
        # Check if file follows best practices
        for practice in best_practices:
            if not self._follows_practice(file_content, practice):
                suggestions.append({
                    'type': 'best_practices',
                    'category': 'context_recommendation',
                    'message': f"Consider following best practice: {practice['title']}",
                    'line': 1,
                    'file': str(file_path),
                    'confidence': 0.7,
                    'impact': 'medium',
                    'suggestion': practice['description'],
                    'context_source': context_path
                })
        
        return suggestions
    
    def _extract_best_practices(self, context_content: str) -> List[Dict[str, str]]:
        """Extract best practices from context content."""
        practices = []
        
        # Simple pattern matching for markdown headers and bullet points
        lines = context_content.split('\n')
        current_section = None
        
        for line in lines:
            # Check for headers
            if line.startswith('#'):
                current_section = line.strip('#').strip()
            
            # Check for bullet points that might be practices
            elif line.strip().startswith('-') or line.strip().startswith('*'):
                practice_text = line.strip().lstrip('-*').strip()
                if len(practice_text) > 10:  # Filter out short items
                    practices.append({
                        'title': practice_text[:50] + '...' if len(practice_text) > 50 else practice_text,
                        'description': practice_text,
                        'section': current_section or 'General'
                    })
        
        return practices[:5]  # Limit to top 5 practices
    
    def _follows_practice(self, file_content: str, practice: Dict[str, str]) -> bool:
        """Check if file content follows a specific practice."""
        # Simple heuristic - this could be much more sophisticated
        practice_keywords = practice['description'].lower().split()
        content_lower = file_content.lower()
        
        # If practice mentions specific keywords, check if they're present
        important_keywords = [kw for kw in practice_keywords 
                            if len(kw) > 4 and kw not in ['should', 'must', 'always', 'never']]
        
        if important_keywords:
            matches = sum(1 for kw in important_keywords if kw in content_lower)
            return matches / len(important_keywords) > 0.3
        
        return True  # Assume following if we can't determine


class SuggestionEngine:
    """Main engine for generating and ranking suggestions."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the suggestion engine."""
        self.config = config
        self.code_analyzer = CodeAnalyzer()
        self.context_analyzer = None
        self.learned_patterns = self._load_learned_patterns()
    
    def set_contexts(self, context_paths: List[str]) -> None:
        """Set the context analyzer with provided context paths."""
        if context_paths:
            self.context_analyzer = ContextAnalyzer(context_paths)
    
    def generate_suggestions(self, file_path: Path, trigger: str) -> List[Dict[str, Any]]:
        """
        Generate suggestions for a file based on trigger event.
        
        Args:
            file_path: Path to the file
            trigger: Event that triggered suggestion generation
            
        Returns:
            List of ranked suggestions
        """
        suggestions = []
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return suggestions
        
        # Get enabled suggestion types for this trigger
        enabled_types = self._get_enabled_types_for_trigger(trigger)
        
        # Generate suggestions by type
        for suggestion_type in enabled_types:
            type_suggestions = self._generate_by_type(
                suggestion_type, file_path, content, trigger
            )
            suggestions.extend(type_suggestions)
        
        # Generate context-aware suggestions
        if self.context_analyzer:
            context_suggestions = self.context_analyzer.generate_context_suggestions(
                file_path, content
            )
            suggestions.extend(context_suggestions)
        
        # Rank and filter suggestions
        ranked_suggestions = self._rank_suggestions(suggestions, file_path)
        
        # Apply limits
        max_suggestions = self._get_max_suggestions()
        return ranked_suggestions[:max_suggestions]
    
    def _get_enabled_types_for_trigger(self, trigger: str) -> List[str]:
        """Get suggestion types enabled for a specific trigger."""
        enabled_types = []
        suggestion_types = self.config.get('suggestion_types', {})
        
        for type_name, type_config in suggestion_types.items():
            if (type_config.get('enabled', True) and 
                trigger in type_config.get('triggers', [])):
                enabled_types.append(type_name)
        
        return enabled_types
    
    def _generate_by_type(self, suggestion_type: str, file_path: Path, 
                         content: str, trigger: str) -> List[Dict[str, Any]]:
        """Generate suggestions for a specific type."""
        suggestions = []
        
        if suggestion_type == 'code_improvement':
            suggestions = self.code_analyzer.analyze_file(file_path, content)
        
        elif suggestion_type == 'documentation':
            suggestions = self._generate_documentation_suggestions(file_path, content)
        
        elif suggestion_type == 'testing':
            suggestions = self._generate_testing_suggestions(file_path, content)
        
        elif suggestion_type == 'security':
            suggestions = self._generate_security_suggestions(file_path, content)
        
        elif suggestion_type == 'performance':
            suggestions = self._generate_performance_suggestions(file_path, content)
        
        elif suggestion_type == 'best_practices':
            suggestions = self._generate_best_practices_suggestions(file_path, content)
        
        # Filter by file patterns
        type_config = self.config.get('suggestion_types', {}).get(suggestion_type, {})
        file_patterns = type_config.get('file_patterns', ['**/*'])
        
        if not any(fnmatch.fnmatch(str(file_path), pattern) for pattern in file_patterns):
            return []
        
        # Limit suggestions per type
        max_per_type = type_config.get('max_suggestions', 5)
        return suggestions[:max_per_type]
    
    def _generate_documentation_suggestions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Generate documentation-specific suggestions."""
        suggestions = []
        
        if file_path.suffix.lower() == '.md':
            # Check for missing sections in README files
            if 'readme' in file_path.name.lower():
                required_sections = ['installation', 'usage', 'contributing', 'license']
                content_lower = content.lower()
                
                for section in required_sections:
                    if section not in content_lower:
                        suggestions.append({
                            'type': 'documentation',
                            'category': 'missing_section',
                            'message': f"README is missing '{section}' section.",
                            'line': 1,
                            'file': str(file_path),
                            'confidence': 0.8,
                            'impact': 'medium',
                            'suggestion': f"Add a '{section}' section to provide complete documentation."
                        })
        
        return suggestions
    
    def _generate_testing_suggestions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Generate testing-specific suggestions."""
        suggestions = []
        
        # Check if this is a test file
        is_test_file = any(pattern in str(file_path).lower() 
                          for pattern in ['test', 'spec'])
        
        if is_test_file:
            # Check for test coverage patterns
            if 'def test_' in content or 'it(' in content:
                # Count test functions
                test_count = len(re.findall(r'def test_|it\(', content))
                if test_count < 3:
                    suggestions.append({
                        'type': 'testing',
                        'category': 'test_coverage',
                        'message': f"Test file has only {test_count} test cases.",
                        'line': 1,
                        'file': str(file_path),
                        'confidence': 0.7,
                        'impact': 'medium',
                        'suggestion': "Consider adding more test cases to improve coverage."
                    })
        
        return suggestions
    
    def _generate_security_suggestions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Generate security-specific suggestions."""
        # This would typically integrate with security scanning tools
        # For now, return basic pattern-based suggestions
        return self.code_analyzer.analyze_file(file_path, content)
    
    def _generate_performance_suggestions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Generate performance-specific suggestions."""
        suggestions = []
        
        # Check for common performance anti-patterns
        if file_path.suffix.lower() == '.py':
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for loops with string concatenation
                if re.search(r'for\s+\w+\s+in.*:\s*\w+\s*\+=\s*["\']', line):
                    suggestions.append({
                        'type': 'performance',
                        'category': 'string_concatenation',
                        'message': "String concatenation in loop detected.",
                        'line': i,
                        'file': str(file_path),
                        'confidence': 0.8,
                        'impact': 'medium',
                        'suggestion': "Use list.join() or f-strings for better performance."
                    })
        
        return suggestions
    
    def _generate_best_practices_suggestions(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Generate best practices suggestions."""
        suggestions = []
        
        # Check for common best practice violations
        if file_path.suffix.lower() == '.py':
            lines = content.split('\n')
            
            # Check for proper imports organization
            import_lines = [i for i, line in enumerate(lines) 
                          if line.strip().startswith(('import ', 'from '))]
            
            if len(import_lines) > 1:
                # Check if imports are grouped properly
                stdlib_imports = []
                third_party_imports = []
                local_imports = []
                
                # This is a simplified check - real implementation would be more sophisticated
                for line_num in import_lines:
                    line = lines[line_num].strip()
                    if 'from .' in line or 'import .' in line:
                        local_imports.append(line_num)
                    elif any(stdlib in line for stdlib in ['os', 'sys', 'json', 're', 'datetime']):
                        stdlib_imports.append(line_num)
                    else:
                        third_party_imports.append(line_num)
                
                # Check if imports are properly ordered
                all_imports = stdlib_imports + third_party_imports + local_imports
                if import_lines != sorted(all_imports):
                    suggestions.append({
                        'type': 'best_practices',
                        'category': 'import_organization',
                        'message': "Imports are not organized according to PEP 8.",
                        'line': import_lines[0] + 1,
                        'file': str(file_path),
                        'confidence': 0.7,
                        'impact': 'low',
                        'suggestion': "Organize imports: stdlib, third-party, then local imports."
                    })
        
        return suggestions
    
    def _rank_suggestions(self, suggestions: List[Dict[str, Any]], 
                         file_path: Path) -> List[Dict[str, Any]]:
        """Rank suggestions by relevance score."""
        scoring_config = self.config.get('relevance_scoring', {})
        factors = scoring_config.get('factors', {})
        
        for suggestion in suggestions:
            score = self._calculate_relevance_score(suggestion, file_path, factors)
            suggestion['relevance_score'] = score
        
        # Filter by minimum score
        min_score = scoring_config.get('min_relevance_score', 0.4)
        filtered = [s for s in suggestions if s['relevance_score'] >= min_score]
        
        # Sort by relevance score descending
        return sorted(filtered, key=lambda x: x['relevance_score'], reverse=True)
    
    def _calculate_relevance_score(self, suggestion: Dict[str, Any], 
                                  file_path: Path, factors: Dict[str, float]) -> float:
        """Calculate relevance score for a suggestion."""
        score = 0.0
        
        # Base confidence score
        confidence = suggestion.get('confidence', 0.5)
        confidence_weight = factors.get('confidence_weight', 0.2)
        score += confidence * confidence_weight
        
        # Impact weight
        impact_map = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
        impact = impact_map.get(suggestion.get('impact', 'medium'), 0.6)
        impact_weight = factors.get('impact_weight', 0.2)
        score += impact * impact_weight
        
        # Context match (if suggestion came from context)
        if 'context_source' in suggestion:
            context_weight = factors.get('context_match_weight', 0.25)
            score += 0.8 * context_weight  # High context match score
        
        # File recency (simplified - would need file stats in real implementation)
        recency_weight = factors.get('recency_weight', 0.2)
        score += 0.7 * recency_weight  # Assume moderate recency
        
        # Frequency (simplified - would need access history)
        frequency_weight = factors.get('frequency_weight', 0.15)
        score += 0.5 * frequency_weight  # Assume moderate frequency
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_max_suggestions(self) -> int:
        """Get maximum number of suggestions to return."""
        return self.config.get('switching_rules', {}).get('max_suggestions', 10)
    
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load previously learned patterns."""
        pattern_file = self.config.get('pattern_recognition', {}).get(
            'pattern_storage', '.kiro/suggestions/learned_patterns.json'
        )
        
        try:
            if os.path.exists(pattern_file):
                with open(pattern_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load learned patterns: {e}")
        
        return {}


def main():
    """Main entry point for the smart suggestions script."""
    parser = argparse.ArgumentParser(description='Generate intelligent code suggestions')
    parser.add_argument('--file', required=True, help='File to analyze')
    parser.add_argument('--trigger', default='file_open', help='Event that triggered suggestions')
    parser.add_argument('--config', help='Path to hook configuration file')
    parser.add_argument('--contexts', nargs='*', help='Context files to use for suggestions')
    parser.add_argument('--output', help='Output file for suggestions')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            hook_config = yaml.safe_load(f)
            config = hook_config.get('config', {})
    
    # Set default configuration if none provided
    if not config:
        config = {
            'suggestion_types': {
                'code_improvement': {
                    'enabled': True,
                    'triggers': ['file_open', 'file_save'],
                    'max_suggestions': 5
                }
            },
            'relevance_scoring': {
                'min_relevance_score': 0.4,
                'factors': {
                    'confidence_weight': 0.3,
                    'impact_weight': 0.3,
                    'context_match_weight': 0.4
                }
            }
        }
    
    # Initialize suggestion engine
    engine = SuggestionEngine(config)
    
    # Set contexts if provided
    if args.contexts:
        engine.set_contexts(args.contexts)
    
    # Generate suggestions
    file_path = Path(args.file)
    suggestions = engine.generate_suggestions(file_path, args.trigger)
    
    # Format output
    if args.format == 'json':
        output = {
            'file': str(file_path),
            'trigger': args.trigger,
            'suggestions': suggestions,
            'generated_at': datetime.now().isoformat()
        }
        output_text = json.dumps(output, indent=2)
    else:
        output_lines = [f"Smart Suggestions for {file_path}"]
        output_lines.append("=" * 50)
        
        if not suggestions:
            output_lines.append("No suggestions found.")
        else:
            for i, suggestion in enumerate(suggestions, 1):
                output_lines.append(f"\n{i}. {suggestion['message']}")
                output_lines.append(f"   Type: {suggestion['type']}")
                output_lines.append(f"   Line: {suggestion.get('line', 'N/A')}")
                output_lines.append(f"   Confidence: {suggestion.get('confidence', 0.5):.1%}")
                output_lines.append(f"   Impact: {suggestion.get('impact', 'medium')}")
                output_lines.append(f"   Suggestion: {suggestion.get('suggestion', 'No specific suggestion')}")
                if 'context_source' in suggestion:
                    output_lines.append(f"   Context: {suggestion['context_source']}")
        
        output_text = '\n'.join(output_lines)
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Suggestions written to: {args.output}")
    else:
        print(output_text)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())