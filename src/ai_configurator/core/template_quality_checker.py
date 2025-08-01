"""Template quality assessment system for AI Configurator example templates."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .models import ConfigurationError, ValidationReport
from .template_validator import TemplateValidator


class QualityLevel(str, Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class QualityMetric:
    """Represents a quality metric assessment."""
    name: str
    score: float  # 0.0 to 1.0
    level: QualityLevel
    message: str
    suggestions: List[str]


@dataclass
class QualityReport:
    """Comprehensive quality assessment report."""
    file_path: str
    template_type: str
    overall_score: float
    overall_level: QualityLevel
    metrics: List[QualityMetric]
    documentation_completeness: float
    example_accuracy: float
    best_practices_compliance: float
    suggestions: List[str]


class TemplateQualityChecker:
    """Comprehensive quality assessment system for AI Configurator templates."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """Initialize the quality checker.
        
        Args:
            base_path: Base directory path for template files (defaults to examples/)
        """
        if base_path is None:
            base_path = Path.cwd() / 'examples'
        self.base_path = Path(base_path)
        self.validator = TemplateValidator(base_path)
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 0.9,
            QualityLevel.GOOD: 0.75,
            QualityLevel.FAIR: 0.6,
            QualityLevel.POOR: 0.0
        }
    
    def assess_all_templates(self) -> List[QualityReport]:
        """Assess quality of all templates in the examples directory.
        
        Returns:
            List of quality reports for all templates
        """
        reports = []
        template_files = self.validator._discover_template_files()
        
        for file_path in template_files:
            try:
                report = self.assess_template_quality(file_path)
                reports.append(report)
            except Exception as e:
                # Create a poor quality report for files that can't be assessed
                reports.append(QualityReport(
                    file_path=str(file_path),
                    template_type="unknown",
                    overall_score=0.0,
                    overall_level=QualityLevel.POOR,
                    metrics=[],
                    documentation_completeness=0.0,
                    example_accuracy=0.0,
                    best_practices_compliance=0.0,
                    suggestions=[f"Failed to assess template quality: {str(e)}"]
                ))
        
        return reports
    
    def assess_template_quality(self, file_path: Union[str, Path]) -> QualityReport:
        """Assess the quality of a single template.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            Quality assessment report
        """
        file_path = Path(file_path)
        template_type = self.validator._determine_template_type(file_path)
        
        # Perform quality assessments
        metrics = []
        
        if template_type == 'profile':
            metrics = self._assess_profile_quality(file_path)
        elif template_type == 'context':
            metrics = self._assess_context_quality(file_path)
        elif template_type == 'hook':
            metrics = self._assess_hook_quality(file_path)
        else:
            metrics = [QualityMetric(
                name="Unknown Template Type",
                score=0.0,
                level=QualityLevel.POOR,
                message="Could not determine template type for quality assessment",
                suggestions=["Ensure template is in correct directory with proper file extension"]
            )]
        
        # Calculate overall scores
        overall_score = sum(m.score for m in metrics) / len(metrics) if metrics else 0.0
        overall_level = self._score_to_level(overall_score)
        
        # Calculate specific quality dimensions
        doc_metrics = [m for m in metrics if 'documentation' in m.name.lower()]
        example_metrics = [m for m in metrics if 'example' in m.name.lower()]
        practices_metrics = [m for m in metrics if 'practice' in m.name.lower() or 'standard' in m.name.lower()]
        
        documentation_completeness = sum(m.score for m in doc_metrics) / len(doc_metrics) if doc_metrics else 0.0
        example_accuracy = sum(m.score for m in example_metrics) / len(example_metrics) if example_metrics else 0.0
        best_practices_compliance = sum(m.score for m in practices_metrics) / len(practices_metrics) if practices_metrics else 0.0
        
        # Collect all suggestions
        suggestions = []
        for metric in metrics:
            suggestions.extend(metric.suggestions)
        
        # Add overall suggestions based on quality level
        if overall_level == QualityLevel.POOR:
            suggestions.append("Consider significant improvements to meet basic quality standards")
        elif overall_level == QualityLevel.FAIR:
            suggestions.append("Template meets basic requirements but has room for improvement")
        elif overall_level == QualityLevel.GOOD:
            suggestions.append("Template is well-structured with minor areas for enhancement")
        
        return QualityReport(
            file_path=str(file_path),
            template_type=template_type,
            overall_score=overall_score,
            overall_level=overall_level,
            metrics=metrics,
            documentation_completeness=documentation_completeness,
            example_accuracy=example_accuracy,
            best_practices_compliance=best_practices_compliance,
            suggestions=list(set(suggestions))  # Remove duplicates
        )
    
    def _assess_profile_quality(self, file_path: Path) -> List[QualityMetric]:
        """Assess quality of a profile template."""
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse JSON with comments
            json_data = self.validator._parse_json_with_comments(content, file_path, [])
            if json_data is None:
                return [QualityMetric(
                    name="JSON Parsing",
                    score=0.0,
                    level=QualityLevel.POOR,
                    message="Failed to parse JSON content",
                    suggestions=["Fix JSON syntax errors"]
                )]
            
            # Assess metadata completeness
            metrics.append(self._assess_metadata_completeness(json_data))
            
            # Assess documentation quality
            metrics.append(self._assess_profile_documentation(json_data, content))
            
            # Assess configuration completeness
            metrics.append(self._assess_profile_configuration(json_data))
            
            # Assess best practices compliance
            metrics.append(self._assess_profile_best_practices(json_data, file_path))
            
            # Assess example quality
            metrics.append(self._assess_profile_examples(json_data, content))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Profile Assessment Error",
                score=0.0,
                level=QualityLevel.POOR,
                message=f"Error assessing profile quality: {str(e)}",
                suggestions=["Check file format and content structure"]
            ))
        
        return metrics
    
    def _assess_context_quality(self, file_path: Path) -> List[QualityMetric]:
        """Assess quality of a context template."""
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            frontmatter, main_content = self.validator._parse_markdown_frontmatter(content)
            
            # Assess content structure and quality
            metrics.append(self._assess_context_structure(main_content))
            
            # Assess content depth and comprehensiveness
            metrics.append(self._assess_context_depth(main_content))
            
            # Assess documentation standards
            metrics.append(self._assess_context_documentation_standards(main_content))
            
            # Assess practical examples
            metrics.append(self._assess_context_examples(main_content))
            
            # Assess frontmatter if present
            if frontmatter:
                metrics.append(self._assess_context_frontmatter(frontmatter))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Context Assessment Error",
                score=0.0,
                level=QualityLevel.POOR,
                message=f"Error assessing context quality: {str(e)}",
                suggestions=["Check file format and markdown structure"]
            ))
        
        return metrics
    
    def _assess_hook_quality(self, file_path: Path) -> List[QualityMetric]:
        """Assess quality of a hook template."""
        metrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            yaml_data = self.validator._parse_yaml_with_errors(content, file_path, [])
            if yaml_data is None:
                return [QualityMetric(
                    name="YAML Parsing",
                    score=0.0,
                    level=QualityLevel.POOR,
                    message="Failed to parse YAML content",
                    suggestions=["Fix YAML syntax errors"]
                )]
            
            # Assess hook configuration completeness
            metrics.append(self._assess_hook_configuration(yaml_data))
            
            # Assess hook documentation
            metrics.append(self._assess_hook_documentation(yaml_data))
            
            # Assess hook best practices
            metrics.append(self._assess_hook_best_practices(yaml_data, file_path))
            
            # Assess hook examples and usage
            metrics.append(self._assess_hook_examples(yaml_data))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Hook Assessment Error",
                score=0.0,
                level=QualityLevel.POOR,
                message=f"Error assessing hook quality: {str(e)}",
                suggestions=["Check file format and YAML structure"]
            ))
        
        return metrics
    
    def _assess_metadata_completeness(self, json_data: Dict[str, Any]) -> QualityMetric:
        """Assess completeness of template metadata."""
        metadata = json_data.get('metadata', {})
        
        required_fields = ['name', 'description', 'category', 'complexity', 'created']
        optional_fields = ['version', 'author', 'updated', 'tags', 'prerequisites', 'related_templates']
        
        required_score = sum(1 for field in required_fields if field in metadata and metadata[field]) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if field in metadata and metadata[field]) / len(optional_fields)
        
        overall_score = (required_score * 0.7) + (optional_score * 0.3)
        
        suggestions = []
        missing_required = [field for field in required_fields if field not in metadata or not metadata[field]]
        if missing_required:
            suggestions.append(f"Add missing required metadata fields: {', '.join(missing_required)}")
        
        missing_optional = [field for field in optional_fields if field not in metadata or not metadata[field]]
        if missing_optional:
            suggestions.append(f"Consider adding optional metadata fields: {', '.join(missing_optional)}")
        
        return QualityMetric(
            name="Metadata Completeness",
            score=overall_score,
            level=self._score_to_level(overall_score),
            message=f"Metadata is {overall_score:.1%} complete",
            suggestions=suggestions
        )
    
    def _assess_profile_documentation(self, json_data: Dict[str, Any], content: str) -> QualityMetric:
        """Assess documentation quality in profile templates."""
        score = 0.0
        suggestions = []
        
        # Check for inline comments
        comment_lines = [line for line in content.split('\n') if '//' in line]
        if len(comment_lines) >= 10:
            score += 0.4
        else:
            suggestions.append("Add more inline comments explaining configuration options")
        
        # Check description quality
        metadata = json_data.get('metadata', {})
        description = metadata.get('description', '')
        if len(description) >= 50:
            score += 0.3
        else:
            suggestions.append("Provide a more comprehensive description (at least 50 characters)")
        
        # Check for section headers in comments
        section_headers = len(re.findall(r'//\s*={10,}', content))
        if section_headers >= 3:
            score += 0.3
        else:
            suggestions.append("Add clear section headers in comments for better organization")
        
        return QualityMetric(
            name="Profile Documentation",
            score=score,
            level=self._score_to_level(score),
            message=f"Documentation quality score: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_profile_configuration(self, json_data: Dict[str, Any]) -> QualityMetric:
        """Assess profile configuration completeness."""
        score = 0.0
        suggestions = []
        
        # Check for paths
        paths = json_data.get('paths', [])
        if paths:
            score += 0.4
        else:
            suggestions.append("Add context paths to make the profile functional")
        
        # Check for settings
        settings = json_data.get('settings', {})
        if settings:
            score += 0.3
        else:
            suggestions.append("Consider adding settings section for configuration options")
        
        # Check for hooks (optional but good to have)
        hooks = json_data.get('hooks', {})
        if hooks:
            score += 0.3
        else:
            suggestions.append("Consider adding hooks for automation capabilities")
        
        return QualityMetric(
            name="Profile Configuration",
            score=score,
            level=self._score_to_level(score),
            message=f"Configuration completeness: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_profile_best_practices(self, json_data: Dict[str, Any], file_path: Path) -> QualityMetric:
        """Assess profile best practices compliance."""
        score = 1.0
        suggestions = []
        
        # Check naming convention
        filename = file_path.stem
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', filename):
            score -= 0.2
            suggestions.append("Use kebab-case naming convention for file names")
        
        # Check for absolute paths (should be avoided)
        paths = json_data.get('paths', [])
        absolute_paths = [p for p in paths if isinstance(p, str) and p.startswith('/')]
        if absolute_paths:
            score -= 0.3
            suggestions.append("Avoid absolute paths in templates; use relative paths instead")
        
        # Check for appropriate category placement
        category = json_data.get('metadata', {}).get('category', '')
        expected_category = self.validator._get_template_category(file_path)
        if category != expected_category and expected_category != 'unknown':
            score -= 0.2
            suggestions.append(f"Template category '{category}' doesn't match directory structure '{expected_category}'")
        
        # Check for reasonable complexity rating
        complexity = json_data.get('metadata', {}).get('complexity', '')
        if not complexity:
            score -= 0.3
            suggestions.append("Add complexity rating to help users choose appropriate templates")
        
        return QualityMetric(
            name="Profile Best Practices",
            score=max(0.0, score),
            level=self._score_to_level(max(0.0, score)),
            message=f"Best practices compliance: {max(0.0, score):.1%}",
            suggestions=suggestions
        )
    
    def _assess_profile_examples(self, json_data: Dict[str, Any], content: str) -> QualityMetric:
        """Assess quality of examples in profile templates."""
        score = 0.0
        suggestions = []
        
        # Check for commented-out examples
        commented_examples = len(re.findall(r'//\s*"[^"]+"\s*:', content))
        if commented_examples >= 2:
            score += 0.5
        else:
            suggestions.append("Add commented-out examples to show users how to extend the template")
        
        # Check for customization notes
        customization_notes = len(re.findall(r'//.*(?:customize|modify|change|adapt)', content, re.IGNORECASE))
        if customization_notes >= 3:
            score += 0.5
        else:
            suggestions.append("Add more customization notes to guide users")
        
        return QualityMetric(
            name="Profile Examples",
            score=score,
            level=self._score_to_level(score),
            message=f"Example quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_context_structure(self, content: str) -> QualityMetric:
        """Assess markdown structure quality of context templates."""
        score = 0.0
        suggestions = []
        
        # Check for main header
        if content.strip().startswith('#'):
            score += 0.3
        else:
            suggestions.append("Start context with a main header (#)")
        
        # Check for multiple header levels
        header_levels = set(re.findall(r'^(#{1,6})', content, re.MULTILINE))
        if len(header_levels) >= 3:
            score += 0.3
        else:
            suggestions.append("Use multiple header levels for better content organization")
        
        # Check for overview section
        if re.search(r'##?\s*overview', content, re.IGNORECASE):
            score += 0.2
        else:
            suggestions.append("Include an overview section to introduce the context")
        
        # Check for conclusion or summary
        if re.search(r'##?\s*(conclusion|summary)', content, re.IGNORECASE):
            score += 0.2
        else:
            suggestions.append("Consider adding a conclusion or summary section")
        
        return QualityMetric(
            name="Context Structure",
            score=score,
            level=self._score_to_level(score),
            message=f"Structure quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_context_depth(self, content: str) -> QualityMetric:
        """Assess depth and comprehensiveness of context content."""
        score = 0.0
        suggestions = []
        
        # Check content length
        word_count = len(content.split())
        if word_count >= 1000:
            score += 0.4
        elif word_count >= 500:
            score += 0.2
        else:
            suggestions.append("Expand content to provide more comprehensive guidance (aim for 500+ words)")
        
        # Check for multiple sections
        sections = len(re.findall(r'^##\s+', content, re.MULTILINE))
        if sections >= 5:
            score += 0.3
        elif sections >= 3:
            score += 0.2
        else:
            suggestions.append("Add more sections to cover the topic comprehensively")
        
        # Check for lists and structured content
        lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        if lists >= 10:
            score += 0.3
        elif lists >= 5:
            score += 0.2
        else:
            suggestions.append("Use more lists and structured content for better readability")
        
        return QualityMetric(
            name="Context Depth",
            score=score,
            level=self._score_to_level(score),
            message=f"Content depth: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_context_documentation_standards(self, content: str) -> QualityMetric:
        """Assess adherence to documentation standards."""
        score = 0.0
        suggestions = []
        
        # Check for proper markdown formatting
        if '```' in content:
            score += 0.3
        else:
            suggestions.append("Include code blocks for better technical examples")
        
        # Check for links (internal or external)
        links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        if links >= 3:
            score += 0.2
        else:
            suggestions.append("Add relevant links to external resources or documentation")
        
        # Check for emphasis and formatting
        emphasis = len(re.findall(r'\*\*[^*]+\*\*|__[^_]+__', content))
        if emphasis >= 5:
            score += 0.2
        else:
            suggestions.append("Use bold text to emphasize important concepts")
        
        # Check for consistent formatting
        if re.search(r'^\s*\d+\.', content, re.MULTILINE):
            score += 0.3
        else:
            suggestions.append("Use numbered lists for step-by-step procedures")
        
        return QualityMetric(
            name="Documentation Standards",
            score=score,
            level=self._score_to_level(score),
            message=f"Documentation standards compliance: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_context_examples(self, content: str) -> QualityMetric:
        """Assess quality and quantity of examples in context."""
        score = 0.0
        suggestions = []
        
        # Check for code examples
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        if code_blocks >= 3:
            score += 0.4
        elif code_blocks >= 1:
            score += 0.2
        else:
            suggestions.append("Add practical code examples to illustrate concepts")
        
        # Check for different types of examples
        example_keywords = ['example', 'for instance', 'such as', 'like this']
        example_count = sum(len(re.findall(keyword, content, re.IGNORECASE)) for keyword in example_keywords)
        if example_count >= 5:
            score += 0.3
        elif example_count >= 2:
            score += 0.2
        else:
            suggestions.append("Include more practical examples throughout the content")
        
        # Check for real-world scenarios
        scenario_keywords = ['scenario', 'use case', 'situation', 'when you']
        scenario_count = sum(len(re.findall(keyword, content, re.IGNORECASE)) for keyword in scenario_keywords)
        if scenario_count >= 3:
            score += 0.3
        else:
            suggestions.append("Add real-world scenarios to make content more practical")
        
        return QualityMetric(
            name="Context Examples",
            score=score,
            level=self._score_to_level(score),
            message=f"Example quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_context_frontmatter(self, frontmatter: Dict[str, Any]) -> QualityMetric:
        """Assess quality of context frontmatter."""
        score = 0.0
        suggestions = []
        
        # Check for basic metadata
        basic_fields = ['name', 'description']
        for field in basic_fields:
            if field in frontmatter and frontmatter[field]:
                score += 0.3
            else:
                suggestions.append(f"Add {field} to frontmatter")
        
        # Check for categorization
        if 'tags' in frontmatter and frontmatter['tags']:
            score += 0.2
        else:
            suggestions.append("Add tags for better categorization")
        
        if 'categories' in frontmatter and frontmatter['categories']:
            score += 0.2
        else:
            suggestions.append("Add categories for organization")
        
        return QualityMetric(
            name="Context Frontmatter",
            score=score,
            level=self._score_to_level(score),
            message=f"Frontmatter quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_hook_configuration(self, yaml_data: Dict[str, Any]) -> QualityMetric:
        """Assess hook configuration completeness."""
        score = 0.0
        suggestions = []
        
        # Check required fields
        required_fields = ['name', 'trigger']
        for field in required_fields:
            if field in yaml_data and yaml_data[field]:
                score += 0.3
            else:
                suggestions.append(f"Add required field: {field}")
        
        # Check recommended fields
        recommended_fields = ['description', 'type', 'timeout']
        for field in recommended_fields:
            if field in yaml_data and yaml_data[field]:
                score += 0.1
            else:
                suggestions.append(f"Consider adding recommended field: {field}")
        
        # Check for configuration section
        if 'config' in yaml_data or 'context' in yaml_data or 'script' in yaml_data:
            score += 0.1
        else:
            suggestions.append("Add configuration section (config, context, or script)")
        
        return QualityMetric(
            name="Hook Configuration",
            score=score,
            level=self._score_to_level(score),
            message=f"Configuration completeness: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_hook_documentation(self, yaml_data: Dict[str, Any]) -> QualityMetric:
        """Assess hook documentation quality."""
        score = 0.0
        suggestions = []
        
        # Check for description
        description = yaml_data.get('description', '')
        if len(description) >= 30:
            score += 0.4
        elif description:
            score += 0.2
            suggestions.append("Expand description to be more comprehensive")
        else:
            suggestions.append("Add a description explaining the hook's purpose")
        
        # Check for metadata
        metadata = yaml_data.get('metadata', {})
        if metadata:
            score += 0.3
        else:
            suggestions.append("Add metadata section for better documentation")
        
        # Check for comments in YAML (inline documentation)
        if 'comments' in str(yaml_data) or len(str(yaml_data)) > len(str(yaml_data).replace('#', '')):
            score += 0.3
        else:
            suggestions.append("Add inline comments to explain configuration options")
        
        return QualityMetric(
            name="Hook Documentation",
            score=score,
            level=self._score_to_level(score),
            message=f"Documentation quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _assess_hook_best_practices(self, yaml_data: Dict[str, Any], file_path: Path) -> QualityMetric:
        """Assess hook best practices compliance."""
        score = 1.0
        suggestions = []
        
        # Check timeout values
        timeout = yaml_data.get('timeout', 30)
        if timeout > 120:
            score -= 0.2
            suggestions.append("Consider reducing timeout for better user experience")
        
        # Check for appropriate trigger
        trigger = yaml_data.get('trigger', '')
        if not trigger:
            score -= 0.3
            suggestions.append("Specify an appropriate trigger for the hook")
        
        # Check for conditions (good practice for complex hooks)
        if 'conditions' in yaml_data:
            score += 0.1
        
        # Check naming convention
        filename = file_path.stem
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', filename):
            score -= 0.2
            suggestions.append("Use kebab-case naming convention")
        
        return QualityMetric(
            name="Hook Best Practices",
            score=max(0.0, score),
            level=self._score_to_level(max(0.0, score)),
            message=f"Best practices compliance: {max(0.0, score):.1%}",
            suggestions=suggestions
        )
    
    def _assess_hook_examples(self, yaml_data: Dict[str, Any]) -> QualityMetric:
        """Assess hook examples and usage guidance."""
        score = 0.0
        suggestions = []
        
        # Check for configuration examples
        config = yaml_data.get('config', {})
        if config and len(config) >= 3:
            score += 0.4
        elif config:
            score += 0.2
        else:
            suggestions.append("Add configuration examples to show hook capabilities")
        
        # Check for context sources (if applicable)
        context = yaml_data.get('context', {})
        if context and 'sources' in context:
            score += 0.3
        
        # Check for metadata with examples
        metadata = yaml_data.get('metadata', {})
        if 'related_hooks' in metadata or 'prerequisites' in metadata:
            score += 0.3
        else:
            suggestions.append("Add related hooks or prerequisites in metadata")
        
        return QualityMetric(
            name="Hook Examples",
            score=score,
            level=self._score_to_level(score),
            message=f"Example quality: {score:.1%}",
            suggestions=suggestions
        )
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """Convert numeric score to quality level."""
        if score >= self.quality_thresholds[QualityLevel.EXCELLENT]:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds[QualityLevel.GOOD]:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds[QualityLevel.FAIR]:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def generate_quality_summary(self, reports: List[QualityReport]) -> Dict[str, Any]:
        """Generate a summary of quality assessment results.
        
        Args:
            reports: List of quality reports
            
        Returns:
            Summary statistics and insights
        """
        if not reports:
            return {"error": "No reports to summarize"}
        
        # Calculate overall statistics
        total_templates = len(reports)
        avg_score = sum(r.overall_score for r in reports) / total_templates
        
        # Count by quality level
        level_counts = {}
        for level in QualityLevel:
            level_counts[level.value] = len([r for r in reports if r.overall_level == level])
        
        # Count by template type
        type_counts = {}
        for report in reports:
            type_counts[report.template_type] = type_counts.get(report.template_type, 0) + 1
        
        # Find common issues
        all_suggestions = []
        for report in reports:
            all_suggestions.extend(report.suggestions)
        
        suggestion_counts = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
        
        common_issues = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Best and worst templates
        best_template = max(reports, key=lambda r: r.overall_score)
        worst_template = min(reports, key=lambda r: r.overall_score)
        
        return {
            "total_templates": total_templates,
            "average_score": avg_score,
            "quality_distribution": level_counts,
            "template_types": type_counts,
            "common_issues": common_issues,
            "best_template": {
                "path": best_template.file_path,
                "score": best_template.overall_score,
                "level": best_template.overall_level.value
            },
            "worst_template": {
                "path": worst_template.file_path,
                "score": worst_template.overall_score,
                "level": worst_template.overall_level.value
            },
            "recommendations": self._generate_overall_recommendations(reports)
        }
    
    def _generate_overall_recommendations(self, reports: List[QualityReport]) -> List[str]:
        """Generate overall recommendations based on quality assessment."""
        recommendations = []
        
        # Calculate average scores by dimension
        avg_doc = sum(r.documentation_completeness for r in reports) / len(reports)
        avg_examples = sum(r.example_accuracy for r in reports) / len(reports)
        avg_practices = sum(r.best_practices_compliance for r in reports) / len(reports)
        
        if avg_doc < 0.7:
            recommendations.append("Focus on improving documentation completeness across templates")
        
        if avg_examples < 0.7:
            recommendations.append("Add more practical examples and usage scenarios")
        
        if avg_practices < 0.8:
            recommendations.append("Review and improve adherence to best practices")
        
        # Quality level distribution recommendations
        poor_count = len([r for r in reports if r.overall_level == QualityLevel.POOR])
        if poor_count > len(reports) * 0.2:
            recommendations.append("Prioritize improving templates with poor quality ratings")
        
        return recommendations