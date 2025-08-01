#!/usr/bin/env python3
"""
Code quality check hook script for AI Configurator.

This script performs automated code analysis and quality metrics collection
for various programming languages using configurable linters and analyzers.
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import re


class Severity(Enum):
    """Severity levels for code quality issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class QualityIssue:
    """Represents a code quality issue."""
    file_path: str
    line: int
    column: int
    rule: str
    message: str
    severity: Severity
    category: str
    tool: str


@dataclass
class QualityReport:
    """Represents a complete quality analysis report."""
    timestamp: str
    file_path: str
    language: str
    issues: List[QualityIssue]
    metrics: Dict[str, Any]
    summary: Dict[str, int]


class LanguageAnalyzer:
    """Base class for language-specific code analyzers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.language_config = config.get('languages', {})
    
    def analyze(self, file_path: str) -> QualityReport:
        """Analyze a file and return quality report."""
        raise NotImplementedError
    
    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)


class PythonAnalyzer(LanguageAnalyzer):
    """Python code quality analyzer."""
    
    def analyze(self, file_path: str) -> QualityReport:
        """Analyze Python file."""
        issues = []
        metrics = {}
        
        python_config = self.language_config.get('python', {})
        linters = python_config.get('linters', ['flake8'])
        
        # Run each configured linter
        for linter in linters:
            if linter == 'flake8':
                issues.extend(self._run_flake8(file_path, python_config))
            elif linter == 'pylint':
                issues.extend(self._run_pylint(file_path, python_config))
            elif linter == 'mypy':
                issues.extend(self._run_mypy(file_path, python_config))
            elif linter == 'bandit':
                issues.extend(self._run_bandit(file_path, python_config))
        
        # Calculate metrics
        metrics = self._calculate_python_metrics(file_path)
        
        # Generate summary
        summary = self._generate_summary(issues)
        
        return QualityReport(
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            language='python',
            issues=issues,
            metrics=metrics,
            summary=summary
        )
    
    def _run_flake8(self, file_path: str, config: Dict[str, Any]) -> List[QualityIssue]:
        """Run flake8 linter."""
        issues = []
        max_line_length = config.get('max_line_length', 88)
        max_complexity = config.get('max_complexity', 10)
        
        command = [
            'flake8',
            '--max-line-length', str(max_line_length),
            '--max-complexity', str(max_complexity),
            '--format', '%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
            file_path
        ]
        
        exit_code, stdout, stderr = self._run_command(command)
        
        if exit_code == 0:
            return issues
        
        # Parse flake8 output
        for line in stdout.strip().split('\n'):
            if line:
                match = re.match(r'(.+):(\d+):(\d+): (\w+) (.+)', line)
                if match:
                    path, line_num, col, code, message = match.groups()
                    severity = Severity.ERROR if code.startswith('E') else Severity.WARNING
                    
                    issues.append(QualityIssue(
                        file_path=path,
                        line=int(line_num),
                        column=int(col),
                        rule=code,
                        message=message,
                        severity=severity,
                        category='style' if code.startswith('E') else 'complexity',
                        tool='flake8'
                    ))
        
        return issues
    
    def _run_pylint(self, file_path: str, config: Dict[str, Any]) -> List[QualityIssue]:
        """Run pylint analyzer."""
        issues = []
        
        command = ['pylint', '--output-format=json', file_path]
        exit_code, stdout, stderr = self._run_command(command)
        
        try:
            if stdout:
                pylint_results = json.loads(stdout)
                for result in pylint_results:
                    severity_map = {
                        'error': Severity.ERROR,
                        'warning': Severity.WARNING,
                        'info': Severity.INFO,
                        'convention': Severity.INFO,
                        'refactor': Severity.WARNING
                    }
                    
                    issues.append(QualityIssue(
                        file_path=result['path'],
                        line=result['line'],
                        column=result['column'],
                        rule=result['message-id'],
                        message=result['message'],
                        severity=severity_map.get(result['type'], Severity.INFO),
                        category=result['category'] if 'category' in result else 'general',
                        tool='pylint'
                    ))
        except json.JSONDecodeError:
            pass
        
        return issues
    
    def _run_mypy(self, file_path: str, config: Dict[str, Any]) -> List[QualityIssue]:
        """Run mypy type checker."""
        issues = []
        
        command = ['mypy', '--show-error-codes', file_path]
        exit_code, stdout, stderr = self._run_command(command)
        
        # Parse mypy output
        for line in stdout.strip().split('\n'):
            if line and ':' in line:
                match = re.match(r'(.+):(\d+): (\w+): (.+) \[(.+)\]', line)
                if match:
                    path, line_num, severity_str, message, code = match.groups()
                    severity = Severity.ERROR if severity_str == 'error' else Severity.WARNING
                    
                    issues.append(QualityIssue(
                        file_path=path,
                        line=int(line_num),
                        column=0,
                        rule=code,
                        message=message,
                        severity=severity,
                        category='typing',
                        tool='mypy'
                    ))
        
        return issues
    
    def _run_bandit(self, file_path: str, config: Dict[str, Any]) -> List[QualityIssue]:
        """Run bandit security analyzer."""
        issues = []
        
        command = ['bandit', '-f', 'json', file_path]
        exit_code, stdout, stderr = self._run_command(command)
        
        try:
            if stdout:
                bandit_results = json.loads(stdout)
                for result in bandit_results.get('results', []):
                    severity_map = {
                        'HIGH': Severity.ERROR,
                        'MEDIUM': Severity.WARNING,
                        'LOW': Severity.INFO
                    }
                    
                    issues.append(QualityIssue(
                        file_path=result['filename'],
                        line=result['line_number'],
                        column=0,
                        rule=result['test_id'],
                        message=result['issue_text'],
                        severity=severity_map.get(result['issue_severity'], Severity.INFO),
                        category='security',
                        tool='bandit'
                    ))
        except json.JSONDecodeError:
            pass
        
        return issues
    
    def _calculate_python_metrics(self, file_path: str) -> Dict[str, Any]:
        """Calculate Python-specific metrics."""
        metrics = {
            'lines_of_code': 0,
            'cyclomatic_complexity': 0,
            'maintainability_index': 0,
            'functions': 0,
            'classes': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Count lines of code (excluding empty lines and comments)
                loc = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        loc += 1
                
                metrics['lines_of_code'] = loc
                
                # Count functions and classes
                metrics['functions'] = content.count('def ')
                metrics['classes'] = content.count('class ')
                
                # Simple complexity estimation
                complexity_indicators = ['if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except:', 'with ']
                complexity = sum(content.count(indicator) for indicator in complexity_indicators)
                metrics['cyclomatic_complexity'] = complexity
                
                # Simple maintainability index (0-100, higher is better)
                if loc > 0:
                    metrics['maintainability_index'] = max(0, 100 - (complexity * 2) - (loc / 10))
                
        except Exception as e:
            print(f"Error calculating metrics for {file_path}: {e}")
        
        return metrics


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/TypeScript code quality analyzer."""
    
    def analyze(self, file_path: str) -> QualityReport:
        """Analyze JavaScript/TypeScript file."""
        issues = []
        metrics = {}
        
        file_ext = Path(file_path).suffix
        language = 'typescript' if file_ext in ['.ts', '.tsx'] else 'javascript'
        lang_config = self.language_config.get(language, {})
        
        linters = lang_config.get('linters', ['eslint'])
        
        # Run each configured linter
        for linter in linters:
            if linter == 'eslint':
                issues.extend(self._run_eslint(file_path, lang_config))
        
        # Calculate metrics
        metrics = self._calculate_js_metrics(file_path)
        
        # Generate summary
        summary = self._generate_summary(issues)
        
        return QualityReport(
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            language=language,
            issues=issues,
            metrics=metrics,
            summary=summary
        )
    
    def _run_eslint(self, file_path: str, config: Dict[str, Any]) -> List[QualityIssue]:
        """Run ESLint analyzer."""
        issues = []
        
        command = ['eslint', '--format', 'json', file_path]
        exit_code, stdout, stderr = self._run_command(command)
        
        try:
            if stdout:
                eslint_results = json.loads(stdout)
                for file_result in eslint_results:
                    for message in file_result.get('messages', []):
                        severity_map = {
                            1: Severity.WARNING,
                            2: Severity.ERROR
                        }
                        
                        issues.append(QualityIssue(
                            file_path=file_result['filePath'],
                            line=message['line'],
                            column=message['column'],
                            rule=message.get('ruleId', 'unknown'),
                            message=message['message'],
                            severity=severity_map.get(message['severity'], Severity.INFO),
                            category='style',
                            tool='eslint'
                        ))
        except json.JSONDecodeError:
            pass
        
        return issues
    
    def _calculate_js_metrics(self, file_path: str) -> Dict[str, Any]:
        """Calculate JavaScript/TypeScript metrics."""
        metrics = {
            'lines_of_code': 0,
            'cyclomatic_complexity': 0,
            'functions': 0,
            'classes': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Count lines of code
                loc = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                        loc += 1
                
                metrics['lines_of_code'] = loc
                
                # Count functions and classes
                metrics['functions'] = len(re.findall(r'\bfunction\b|\b=>\b', content))
                metrics['classes'] = content.count('class ')
                
                # Simple complexity estimation
                complexity_indicators = ['if ', 'else ', 'for ', 'while ', 'switch ', 'case ', 'catch ', '&&', '||']
                complexity = sum(content.count(indicator) for indicator in complexity_indicators)
                metrics['cyclomatic_complexity'] = complexity
                
        except Exception as e:
            print(f"Error calculating metrics for {file_path}: {e}")
        
        return metrics


class CodeQualityChecker:
    """Main class for code quality checking."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get('output_dir', 'reports/quality'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize language analyzers
        self.analyzers = {
            '.py': PythonAnalyzer(config),
            '.js': JavaScriptAnalyzer(config),
            '.jsx': JavaScriptAnalyzer(config),
            '.ts': JavaScriptAnalyzer(config),
            '.tsx': JavaScriptAnalyzer(config)
        }
    
    def check_quality(self, file_path: str) -> bool:
        """
        Perform quality check on the specified file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            bool: True if quality check passed, False otherwise
        """
        try:
            print(f"Checking code quality for: {file_path}")
            
            file_ext = Path(file_path).suffix
            
            if file_ext not in self.analyzers:
                print(f"No analyzer available for file type: {file_ext}")
                return True
            
            # Run analysis
            analyzer = self.analyzers[file_ext]
            report = analyzer.analyze(file_path)
            
            # Save report
            self._save_report(report)
            
            # Check quality gates
            passed = self._check_quality_gates(report)
            
            # Print summary
            self._print_summary(report, passed)
            
            return passed
            
        except Exception as e:
            print(f"Error during quality check: {e}")
            return False
    
    def _save_report(self, report: QualityReport) -> None:
        """Save quality report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"quality_report_{Path(report.file_path).stem}_{timestamp}"
        
        # Save as JSON
        json_file = self.output_dir / f"{base_name}.json"
        report_dict = {
            'timestamp': report.timestamp,
            'file_path': report.file_path,
            'language': report.language,
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line': issue.line,
                    'column': issue.column,
                    'rule': issue.rule,
                    'message': issue.message,
                    'severity': issue.severity.value,
                    'category': issue.category,
                    'tool': issue.tool
                }
                for issue in report.issues
            ],
            'metrics': report.metrics,
            'summary': report.summary
        }
        
        with open(json_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        # Save as Markdown if requested
        if 'markdown' in self.config.get('report_formats', []):
            md_file = self.output_dir / f"{base_name}.md"
            with open(md_file, 'w') as f:
                f.write(self._generate_markdown_report(report))
    
    def _generate_markdown_report(self, report: QualityReport) -> str:
        """Generate Markdown report."""
        md = f"# Code Quality Report\n\n"
        md += f"**File:** {report.file_path}  \n"
        md += f"**Language:** {report.language}  \n"
        md += f"**Generated:** {report.timestamp}  \n\n"
        
        # Summary
        md += "## Summary\n\n"
        for severity, count in report.summary.items():
            md += f"- **{severity.title()}:** {count}\n"
        md += "\n"
        
        # Metrics
        if report.metrics:
            md += "## Metrics\n\n"
            for metric, value in report.metrics.items():
                md += f"- **{metric.replace('_', ' ').title()}:** {value}\n"
            md += "\n"
        
        # Issues
        if report.issues:
            md += "## Issues\n\n"
            for issue in sorted(report.issues, key=lambda x: (x.line, x.severity.value)):
                md += f"### Line {issue.line}:{issue.column} - {issue.severity.value.upper()}\n\n"
                md += f"**Rule:** {issue.rule}  \n"
                md += f"**Category:** {issue.category}  \n"
                md += f"**Tool:** {issue.tool}  \n"
                md += f"**Message:** {issue.message}  \n\n"
        
        return md
    
    def _check_quality_gates(self, report: QualityReport) -> bool:
        """Check if report passes quality gates."""
        gates = self.config.get('quality_gates', {})
        
        # Check critical and major issues
        critical_count = report.summary.get('error', 0)
        major_count = report.summary.get('warning', 0)
        
        max_critical = gates.get('max_critical_issues', 0)
        max_major = gates.get('max_major_issues', 5)
        
        if critical_count > max_critical:
            print(f"Quality gate failed: {critical_count} critical issues (max: {max_critical})")
            return False
        
        if major_count > max_major:
            print(f"Quality gate failed: {major_count} major issues (max: {max_major})")
            return False
        
        return True
    
    def _print_summary(self, report: QualityReport, passed: bool) -> None:
        """Print quality check summary."""
        print(f"\n{'='*50}")
        print(f"Quality Check Summary for {Path(report.file_path).name}")
        print(f"{'='*50}")
        
        for severity, count in report.summary.items():
            print(f"{severity.title()}: {count}")
        
        if report.metrics:
            print(f"\nMetrics:")
            for metric, value in report.metrics.items():
                print(f"  {metric.replace('_', ' ').title()}: {value}")
        
        status = "PASSED" if passed else "FAILED"
        print(f"\nOverall Status: {status}")
        print(f"{'='*50}\n")


def main():
    """Main entry point for the code quality check script."""
    parser = argparse.ArgumentParser(description='Check code quality')
    parser.add_argument('--file', required=True, help='File to analyze')
    parser.add_argument('--config', help='Path to hook configuration file')
    parser.add_argument('--output-dir', help='Output directory for reports')
    
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
        'output_dir': 'reports/quality',
        'report_formats': ['json', 'markdown'],
        'severity_levels': ['error', 'warning', 'info'],
        'languages': {
            'python': {
                'linters': ['flake8'],
                'max_line_length': 88,
                'max_complexity': 10
            },
            'javascript': {
                'linters': ['eslint'],
                'max_line_length': 100,
                'max_complexity': 15
            }
        },
        'quality_gates': {
            'max_critical_issues': 0,
            'max_major_issues': 5
        }
    }
    
    # Merge configurations
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    # Check code quality
    checker = CodeQualityChecker(config)
    success = checker.check_quality(args.file)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()