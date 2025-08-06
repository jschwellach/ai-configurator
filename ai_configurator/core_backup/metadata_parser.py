"""
Configuration metadata parser with validation and error reporting.
Supports YAML frontmatter in markdown files and YAML configuration files.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import logging
from dataclasses import dataclass

try:
    from .catalog_schema import ConfigMetadata, CompatibilityInfo, UsageStats, CONFIG_METADATA_SCHEMA
except ImportError:
    from catalog_schema import ConfigMetadata, CompatibilityInfo, UsageStats, CONFIG_METADATA_SCHEMA

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    jsonschema = None

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    value: Any = None
    line_number: Optional[int] = None


@dataclass
class ParseResult:
    """Result of parsing a configuration file."""
    success: bool
    metadata: Optional[ConfigMetadata] = None
    errors: List[ValidationError] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class MetadataParser:
    """Parser for configuration metadata with validation."""
    
    def __init__(self, strict_validation: bool = True):
        self.strict_validation = strict_validation
        self.schema = CONFIG_METADATA_SCHEMA
        
    def parse_file(self, file_path: Union[str, Path]) -> ParseResult:
        """Parse metadata from a configuration file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ParseResult(
                success=False,
                errors=[ValidationError("file", f"File not found: {file_path}")]
            )
        
        try:
            # Extract raw metadata
            raw_metadata, content_start_line = self._extract_raw_metadata(file_path)
            
            if raw_metadata is None:
                return ParseResult(
                    success=False,
                    errors=[ValidationError("metadata", "No metadata found in file")]
                )
            
            # Validate against schema
            validation_result = self._validate_metadata(raw_metadata)
            
            if not validation_result.success:
                return validation_result
            
            # Create ConfigMetadata object
            try:
                metadata = self._create_metadata_object(raw_metadata)
                return ParseResult(
                    success=True,
                    metadata=metadata,
                    warnings=validation_result.warnings
                )
            except Exception as e:
                return ParseResult(
                    success=False,
                    errors=[ValidationError("creation", f"Failed to create metadata object: {e}")]
                )
                
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return ParseResult(
                success=False,
                errors=[ValidationError("parsing", f"Failed to parse file: {e}")]
            )
    
    def _extract_raw_metadata(self, file_path: Path) -> Tuple[Optional[Dict[str, Any]], int]:
        """Extract raw metadata from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None, 0
        
        if file_path.suffix == '.md':
            return self._extract_markdown_frontmatter(content)
        elif file_path.suffix in ['.yaml', '.yml']:
            return self._extract_yaml_metadata(content)
        elif file_path.suffix == '.json':
            return self._extract_json_metadata(content)
        else:
            logger.warning(f"Unsupported file type: {file_path.suffix}")
            return None, 0
    
    def _extract_markdown_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], int]:
        """Extract YAML frontmatter from markdown content."""
        if not content.startswith('---\n'):
            return None, 0
        
        # Find the end of frontmatter
        lines = content.split('\n')
        end_line = None
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_line = i
                break
        
        if end_line is None:
            return None, 0
        
        # Extract YAML content
        yaml_content = '\n'.join(lines[1:end_line])
        
        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata, end_line + 1
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return None, 0
    
    def _extract_yaml_metadata(self, content: str) -> Tuple[Optional[Dict[str, Any]], int]:
        """Extract metadata from YAML file."""
        # Check for frontmatter first
        if content.startswith('---\n'):
            return self._extract_markdown_frontmatter(content)
        
        # Try to parse entire file as YAML
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                # Check if it has metadata structure
                if self._has_metadata_structure(data):
                    return data, 0
                # Look for metadata key
                elif 'metadata' in data and isinstance(data['metadata'], dict):
                    return data['metadata'], 0
            
            return None, 0
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return None, 0
    
    def _extract_json_metadata(self, content: str) -> Tuple[Optional[Dict[str, Any]], int]:
        """Extract metadata from JSON file."""
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                # Check if it has metadata structure
                if self._has_metadata_structure(data):
                    return data, 0
                # Look for metadata key
                elif 'metadata' in data and isinstance(data['metadata'], dict):
                    return data['metadata'], 0
            
            return None, 0
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None, 0
    
    def _has_metadata_structure(self, data: Dict[str, Any]) -> bool:
        """Check if data has required metadata structure."""
        required_fields = ['id', 'name', 'description', 'version']
        return all(field in data for field in required_fields)
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> ParseResult:
        """Validate metadata against schema."""
        errors = []
        warnings = []
        
        if HAS_JSONSCHEMA:
            try:
                # Validate against JSON schema
                jsonschema.validate(metadata, self.schema)
            except jsonschema.ValidationError as e:
                field_path = '.'.join(str(p) for p in e.absolute_path) if e.absolute_path else 'root'
                errors.append(ValidationError(
                    field=field_path,
                    message=e.message,
                    value=e.instance
                ))
            except jsonschema.SchemaError as e:
                errors.append(ValidationError(
                    field="schema",
                    message=f"Schema error: {e.message}"
                ))
        else:
            # Basic validation without jsonschema
            self._basic_validation(metadata, errors)
        
        # Additional custom validations
        self._validate_version_format(metadata, errors, warnings)
        self._validate_date_format(metadata, errors, warnings)
        self._validate_personas(metadata, errors, warnings)
        self._validate_dependencies(metadata, errors, warnings)
        
        return ParseResult(
            success=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _basic_validation(self, metadata: Dict[str, Any], errors: List[ValidationError]):
        """Basic validation without jsonschema."""
        required_fields = ['id', 'name', 'description', 'version', 'author', 'personas', 'domains', 'tags', 'created_date', 'updated_date']
        
        for field in required_fields:
            if field not in metadata:
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing"
                ))
        
        # Type validations
        if 'personas' in metadata and not isinstance(metadata['personas'], list):
            errors.append(ValidationError(
                field='personas',
                message="Field 'personas' must be a list",
                value=metadata['personas']
            ))
        
        if 'domains' in metadata and not isinstance(metadata['domains'], list):
            errors.append(ValidationError(
                field='domains',
                message="Field 'domains' must be a list",
                value=metadata['domains']
            ))
        
        if 'tags' in metadata and not isinstance(metadata['tags'], list):
            errors.append(ValidationError(
                field='tags',
                message="Field 'tags' must be a list",
                value=metadata['tags']
            ))
        
        if 'dependencies' in metadata and not isinstance(metadata['dependencies'], list):
            errors.append(ValidationError(
                field='dependencies',
                message="Field 'dependencies' must be a list",
                value=metadata['dependencies']
            ))
    
    def _validate_version_format(self, metadata: Dict[str, Any], errors: List[ValidationError], warnings: List[str]):
        """Validate version format."""
        version = metadata.get('version')
        if version:
            # Check semantic versioning format
            if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?$', version):
                warnings.append(f"Version '{version}' does not follow semantic versioning (x.y.z)")
    
    def _validate_date_format(self, metadata: Dict[str, Any], errors: List[ValidationError], warnings: List[str]):
        """Validate date formats."""
        for date_field in ['created_date', 'updated_date']:
            date_value = metadata.get(date_field)
            if date_value:
                try:
                    datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    errors.append(ValidationError(
                        field=date_field,
                        message=f"Invalid date format. Expected YYYY-MM-DD, got: {date_value}",
                        value=date_value
                    ))
    
    def _validate_personas(self, metadata: Dict[str, Any], errors: List[ValidationError], warnings: List[str]):
        """Validate personas."""
        personas = metadata.get('personas', [])
        if not personas:
            warnings.append("No personas specified - configuration may be hard to discover")
        
        # Check for known personas
        known_personas = {
            'developer', 'solutions-architect', 'engagement-manager', 'general-user',
            'devops-engineer', 'network-admin', 'content-creator', 'researcher'
        }
        
        for persona in personas:
            if persona not in known_personas:
                warnings.append(f"Unknown persona '{persona}' - consider using standard personas")
    
    def _validate_dependencies(self, metadata: Dict[str, Any], errors: List[ValidationError], warnings: List[str]):
        """Validate dependencies."""
        dependencies = metadata.get('dependencies', [])
        
        # Check for circular dependencies (basic check)
        config_id = metadata.get('id')
        if config_id and config_id in dependencies:
            errors.append(ValidationError(
                field="dependencies",
                message="Configuration cannot depend on itself",
                value=config_id
            ))
        
        # Check dependency ID format
        for dep in dependencies:
            if not re.match(r'^[a-z0-9-]+-v\d+$', dep):
                warnings.append(f"Dependency '{dep}' does not follow standard ID format (name-vX)")
    
    def _create_metadata_object(self, raw_metadata: Dict[str, Any]) -> ConfigMetadata:
        """Create ConfigMetadata object from raw metadata."""
        # Handle compatibility info
        compatibility_data = raw_metadata.get('compatibility', {})
        compatibility = CompatibilityInfo(
            kiro_version=compatibility_data.get('kiro_version', '>=1.0.0'),
            platforms=compatibility_data.get('platforms', ['linux', 'macos', 'windows'])
        )
        
        # Handle usage stats
        usage_data = raw_metadata.get('usage_stats', {})
        usage_stats = UsageStats(
            downloads=usage_data.get('downloads', 0),
            rating=usage_data.get('rating', 0.0)
        )
        
        return ConfigMetadata(
            id=raw_metadata['id'],
            name=raw_metadata['name'],
            description=raw_metadata['description'],
            version=raw_metadata['version'],
            author=raw_metadata['author'],
            personas=raw_metadata['personas'],
            domains=raw_metadata['domains'],
            dependencies=raw_metadata.get('dependencies', []),
            tags=raw_metadata['tags'],
            compatibility=compatibility,
            created_date=raw_metadata['created_date'],
            updated_date=raw_metadata['updated_date'],
            usage_stats=usage_stats
        )
    
    def validate_directory(self, directory_path: Union[str, Path]) -> Dict[str, ParseResult]:
        """Validate all configuration files in a directory."""
        directory_path = Path(directory_path)
        results = {}
        
        # Find all configuration files
        patterns = ['**/*.md', '**/*.yaml', '**/*.yml', '**/*.json']
        
        for pattern in patterns:
            for file_path in directory_path.glob(pattern):
                # Skip certain files
                if file_path.name in ['catalog.json', 'README.md']:
                    continue
                
                relative_path = file_path.relative_to(directory_path)
                results[str(relative_path)] = self.parse_file(file_path)
        
        return results
    
    def generate_validation_report(self, results: Dict[str, ParseResult]) -> str:
        """Generate a human-readable validation report."""
        report_lines = []
        report_lines.append("Configuration Metadata Validation Report")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        total_files = len(results)
        successful_files = sum(1 for r in results.values() if r.success)
        failed_files = total_files - successful_files
        
        report_lines.append(f"Total files: {total_files}")
        report_lines.append(f"Successful: {successful_files}")
        report_lines.append(f"Failed: {failed_files}")
        report_lines.append("")
        
        # Report failures
        if failed_files > 0:
            report_lines.append("FAILURES:")
            report_lines.append("-" * 20)
            
            for file_path, result in results.items():
                if not result.success:
                    report_lines.append(f"\n{file_path}:")
                    for error in result.errors:
                        report_lines.append(f"  ERROR [{error.field}]: {error.message}")
                        if error.value is not None:
                            report_lines.append(f"    Value: {error.value}")
        
        # Report warnings
        warning_files = [f for f, r in results.items() if r.warnings]
        if warning_files:
            report_lines.append("\nWARNINGS:")
            report_lines.append("-" * 20)
            
            for file_path in warning_files:
                result = results[file_path]
                if result.warnings:
                    report_lines.append(f"\n{file_path}:")
                    for warning in result.warnings:
                        report_lines.append(f"  WARNING: {warning}")
        
        return "\n".join(report_lines)


def validate_library_cli(library_path: str = "library") -> None:
    """CLI function to validate library metadata."""
    parser = MetadataParser()
    results = parser.validate_directory(library_path)
    report = parser.generate_validation_report(results)
    print(report)
    
    # Exit with error code if there are failures
    failed_count = sum(1 for r in results.values() if not r.success)
    if failed_count > 0:
        exit(1)


if __name__ == "__main__":
    import sys
    
    library_path = sys.argv[1] if len(sys.argv) > 1 else "library"
    validate_library_cli(library_path)