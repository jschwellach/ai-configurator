"""Automated quality checks for example templates."""

from pathlib import Path
from typing import Dict, List, Optional, Union
import json

from .template_quality_checker import TemplateQualityChecker, QualityLevel, QualityReport
from .template_validator import TemplateValidator
from .models import ValidationReport


class AutomatedQualityChecker:
    """Automated quality assessment system for template maintenance."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """Initialize automated quality checker.
        
        Args:
            base_path: Base directory path for template files (defaults to examples/)
        """
        if base_path is None:
            base_path = Path.cwd() / 'examples'
        self.base_path = Path(base_path)
        self.validator = TemplateValidator(base_path)
        self.quality_checker = TemplateQualityChecker(base_path)
    
    def run_comprehensive_checks(self) -> Dict[str, any]:
        """Run comprehensive validation and quality checks.
        
        Returns:
            Complete assessment results including validation and quality metrics
        """
        results = {
            'validation': None,
            'quality': None,
            'summary': None,
            'recommendations': [],
            'status': 'success'
        }
        
        try:
            # Run validation checks
            print("Running template validation...")
            validation_report = self.validator.validate_all_templates()
            results['validation'] = {
                'is_valid': validation_report.is_valid,
                'total_files': len(validation_report.files_checked),
                'errors': len(validation_report.errors),
                'warnings': len(validation_report.warnings),
                'error_details': [
                    {
                        'file': error.file_path,
                        'type': error.error_type,
                        'message': error.message,
                        'severity': error.severity
                    }
                    for error in validation_report.errors[:10]  # Limit to first 10 errors
                ]
            }
            
            # Run quality assessment
            print("Running quality assessment...")
            quality_reports = self.quality_checker.assess_all_templates()
            quality_summary = self.quality_checker.generate_quality_summary(quality_reports)
            
            results['quality'] = {
                'total_templates': len(quality_reports),
                'average_score': quality_summary['average_score'],
                'quality_distribution': quality_summary['quality_distribution'],
                'template_types': quality_summary['template_types'],
                'best_template': quality_summary['best_template'],
                'worst_template': quality_summary['worst_template']
            }
            
            # Generate comprehensive summary
            results['summary'] = self._generate_comprehensive_summary(
                validation_report, quality_reports, quality_summary
            )
            
            # Generate actionable recommendations
            results['recommendations'] = self._generate_actionable_recommendations(
                validation_report, quality_reports, quality_summary
            )
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def check_template_standards_compliance(self) -> Dict[str, any]:
        """Check compliance with template standards and best practices.
        
        Returns:
            Standards compliance report
        """
        compliance_results = {
            'overall_compliance': 0.0,
            'categories': {},
            'failing_templates': [],
            'recommendations': []
        }
        
        try:
            quality_reports = self.quality_checker.assess_all_templates()
            
            # Analyze compliance by category
            categories = {
                'naming_conventions': [],
                'documentation_standards': [],
                'structure_compliance': [],
                'example_quality': [],
                'metadata_completeness': []
            }
            
            for report in quality_reports:
                # Check naming conventions
                file_path = Path(report.file_path)
                filename = file_path.stem
                if not filename.replace('-', '').replace('_', '').isalnum():
                    categories['naming_conventions'].append(report.file_path)
                
                # Check documentation standards
                if report.documentation_completeness < 0.7:
                    categories['documentation_standards'].append(report.file_path)
                
                # Check structure compliance
                if report.best_practices_compliance < 0.8:
                    categories['structure_compliance'].append(report.file_path)
                
                # Check example quality
                if report.example_accuracy < 0.6:
                    categories['example_quality'].append(report.file_path)
                
                # Check metadata completeness (for templates with metadata)
                if hasattr(report, 'metadata_score') and report.metadata_score < 0.8:
                    categories['metadata_completeness'].append(report.file_path)
                
                # Track failing templates
                if report.overall_level == QualityLevel.POOR:
                    compliance_results['failing_templates'].append({
                        'path': report.file_path,
                        'score': report.overall_score,
                        'issues': report.suggestions[:3]
                    })
            
            # Calculate compliance scores
            total_templates = len(quality_reports)
            for category, failing_files in categories.items():
                compliance_score = (total_templates - len(failing_files)) / total_templates if total_templates > 0 else 1.0
                compliance_results['categories'][category] = {
                    'score': compliance_score,
                    'failing_count': len(failing_files),
                    'failing_files': failing_files
                }
            
            # Calculate overall compliance
            category_scores = [cat['score'] for cat in compliance_results['categories'].values()]
            compliance_results['overall_compliance'] = sum(category_scores) / len(category_scores) if category_scores else 0.0
            
            # Generate recommendations
            compliance_results['recommendations'] = self._generate_compliance_recommendations(categories, total_templates)
            
        except Exception as e:
            compliance_results['error'] = str(e)
        
        return compliance_results
    
    def generate_quality_report(self, output_path: Optional[Union[str, Path]] = None) -> str:
        """Generate a comprehensive quality report.
        
        Args:
            output_path: Optional path to save the report
            
        Returns:
            Report content as string
        """
        results = self.run_comprehensive_checks()
        
        report_lines = [
            "# Template Quality Assessment Report",
            f"Generated for: {self.base_path}",
            "",
            "## Executive Summary",
            ""
        ]
        
        if results['status'] == 'error':
            report_lines.extend([
                f"❌ **Error during assessment:** {results.get('error', 'Unknown error')}",
                ""
            ])
            return "\n".join(report_lines)
        
        # Validation summary
        validation = results['validation']
        if validation['is_valid']:
            report_lines.append("✅ **Validation Status:** All templates pass validation")
        else:
            report_lines.append(f"❌ **Validation Status:** {validation['errors']} errors found across {validation['total_files']} files")
        
        # Quality summary
        quality = results['quality']
        avg_score = quality['average_score']
        if avg_score >= 0.9:
            quality_status = "🌟 Excellent"
        elif avg_score >= 0.75:
            quality_status = "✅ Good"
        elif avg_score >= 0.6:
            quality_status = "⚠️ Fair"
        else:
            quality_status = "❌ Poor"
        
        report_lines.extend([
            f"📊 **Overall Quality:** {quality_status} (Average Score: {avg_score:.2f})",
            f"📁 **Templates Assessed:** {quality['total_templates']}",
            "",
            "## Quality Distribution",
            ""
        ])
        
        for level, count in quality['quality_distribution'].items():
            percentage = (count / quality['total_templates']) * 100 if quality['total_templates'] > 0 else 0
            report_lines.append(f"- **{level.title()}:** {count} templates ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "## Template Types",
            ""
        ])
        
        for template_type, count in quality['template_types'].items():
            report_lines.append(f"- **{template_type.title()}:** {count} templates")
        
        # Best and worst templates
        report_lines.extend([
            "",
            "## Performance Highlights",
            "",
            f"🏆 **Best Template:** {quality['best_template']['path']} (Score: {quality['best_template']['score']:.2f})",
            f"⚠️ **Needs Improvement:** {quality['worst_template']['path']} (Score: {quality['worst_template']['score']:.2f})",
            ""
        ])
        
        # Validation issues
        if validation['errors'] > 0:
            report_lines.extend([
                "## Validation Issues",
                ""
            ])
            
            for error in validation['error_details']:
                report_lines.append(f"- **{error['file']}:** {error['message']} ({error['type']})")
            
            report_lines.append("")
        
        # Recommendations
        if results['recommendations']:
            report_lines.extend([
                "## Recommendations",
                ""
            ])
            
            for i, rec in enumerate(results['recommendations'], 1):
                report_lines.append(f"{i}. {rec}")
            
            report_lines.append("")
        
        # Summary
        report_lines.extend([
            "## Summary",
            "",
            results['summary'],
            "",
            "---",
            "*Report generated by AI Configurator Template Quality Checker*"
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Quality report saved to: {output_path}")
        
        return report_content
    
    def _generate_comprehensive_summary(
        self, 
        validation_report: ValidationReport, 
        quality_reports: List[QualityReport], 
        quality_summary: Dict[str, any]
    ) -> str:
        """Generate a comprehensive summary of the assessment."""
        summary_parts = []
        
        # Validation summary
        if validation_report.is_valid:
            summary_parts.append("All templates pass validation checks.")
        else:
            error_count = len(validation_report.errors)
            warning_count = len(validation_report.warnings)
            summary_parts.append(f"Found {error_count} validation errors and {warning_count} warnings that need attention.")
        
        # Quality summary
        total_templates = len(quality_reports)
        avg_score = quality_summary['average_score']
        
        excellent_count = quality_summary['quality_distribution'].get('excellent', 0)
        poor_count = quality_summary['quality_distribution'].get('poor', 0)
        
        if avg_score >= 0.8:
            summary_parts.append(f"Template quality is generally high with an average score of {avg_score:.2f}.")
        elif avg_score >= 0.6:
            summary_parts.append(f"Template quality is moderate with an average score of {avg_score:.2f}.")
        else:
            summary_parts.append(f"Template quality needs improvement with an average score of {avg_score:.2f}.")
        
        if excellent_count > total_templates * 0.3:
            summary_parts.append(f"{excellent_count} templates achieve excellent quality standards.")
        
        if poor_count > 0:
            summary_parts.append(f"{poor_count} templates require significant improvement.")
        
        # Common issues
        if quality_summary.get('common_issues'):
            top_issue = quality_summary['common_issues'][0]
            summary_parts.append(f"The most common improvement area is: {top_issue[0]}.")
        
        return " ".join(summary_parts)
    
    def _generate_actionable_recommendations(
        self, 
        validation_report: ValidationReport, 
        quality_reports: List[QualityReport], 
        quality_summary: Dict[str, any]
    ) -> List[str]:
        """Generate actionable recommendations based on assessment results."""
        recommendations = []
        
        # Validation-based recommendations
        if not validation_report.is_valid:
            recommendations.append("Fix validation errors before focusing on quality improvements")
            
            # Specific error type recommendations
            error_types = [error.error_type for error in validation_report.errors]
            if 'JSONSyntaxError' in error_types:
                recommendations.append("Review and fix JSON syntax errors in profile templates")
            if 'YAMLSyntaxError' in error_types:
                recommendations.append("Review and fix YAML syntax errors in hook templates")
            if 'MissingFileReference' in error_types:
                recommendations.append("Update file references to point to existing templates")
        
        # Quality-based recommendations
        avg_score = quality_summary['average_score']
        if avg_score < 0.7:
            recommendations.append("Focus on improving overall template quality across all categories")
        
        # Specific quality dimension recommendations
        doc_scores = [r.documentation_completeness for r in quality_reports]
        example_scores = [r.example_accuracy for r in quality_reports]
        practice_scores = [r.best_practices_compliance for r in quality_reports]
        
        avg_doc = sum(doc_scores) / len(doc_scores) if doc_scores else 0
        avg_examples = sum(example_scores) / len(example_scores) if example_scores else 0
        avg_practices = sum(practice_scores) / len(practice_scores) if practice_scores else 0
        
        if avg_doc < 0.7:
            recommendations.append("Improve documentation completeness with better inline comments and descriptions")
        
        if avg_examples < 0.7:
            recommendations.append("Add more practical examples and code snippets to templates")
        
        if avg_practices < 0.8:
            recommendations.append("Review templates for adherence to naming conventions and best practices")
        
        # Template type specific recommendations
        type_scores = {}
        for report in quality_reports:
            if report.template_type not in type_scores:
                type_scores[report.template_type] = []
            type_scores[report.template_type].append(report.overall_score)
        
        for template_type, scores in type_scores.items():
            avg_type_score = sum(scores) / len(scores)
            if avg_type_score < 0.7:
                recommendations.append(f"Focus improvement efforts on {template_type} templates")
        
        # Poor quality template recommendations
        poor_templates = [r for r in quality_reports if r.overall_level == QualityLevel.POOR]
        if poor_templates:
            recommendations.append(f"Prioritize improving {len(poor_templates)} templates with poor quality ratings")
        
        return recommendations
    
    def _generate_compliance_recommendations(
        self, 
        categories: Dict[str, List[str]], 
        total_templates: int
    ) -> List[str]:
        """Generate compliance-specific recommendations."""
        recommendations = []
        
        for category, failing_files in categories.items():
            if not failing_files:
                continue
                
            failure_rate = len(failing_files) / total_templates if total_templates > 0 else 0
            
            if failure_rate > 0.2:  # More than 20% failing
                if category == 'naming_conventions':
                    recommendations.append("Standardize template naming to use kebab-case format")
                elif category == 'documentation_standards':
                    recommendations.append("Improve documentation with comprehensive descriptions and comments")
                elif category == 'structure_compliance':
                    recommendations.append("Review template structure to follow established best practices")
                elif category == 'example_quality':
                    recommendations.append("Enhance templates with more practical examples and use cases")
                elif category == 'metadata_completeness':
                    recommendations.append("Complete metadata fields for better template discoverability")
        
        return recommendations