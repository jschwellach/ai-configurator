"""Template validation system for AI Configurator example templates."""

import json
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import re
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, validator
from .models import ConfigurationError, ValidationReport


class TemplateMetadata(BaseModel):
    """Metadata schema for all template types."""
    
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Template category (basic, professional, advanced)")
    version: str = Field(default="1.0.0", description="Template version")
    author: str = Field(default="AI Configurator Team", description="Template author")
    created: str = Field(..., description="Creation date (YYYY-MM-DD)")
    updated: Optional[str] = Field(None, description="Last update date (YYYY-MM-DD)")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    complexity: str = Field(..., description="Complexity level (low, medium, high)")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    related_templates: List[str] = Field(default_factory=list, description="Related template names")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = ['basic', 'professional', 'advanced', 'workflow']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v
    
    @validator('complexity')
    def validate_complexity(cls, v):
        valid_complexity = ['low', 'medium', 'high']
        if v not in valid_complexity:
            raise ValueError(f'Complexity must be one of: {", ".join(valid_complexity)}')
        return v
    
    @validator('created', 'updated')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class ProfileTemplateSchema(BaseModel):
    """Schema for profile template validation."""
    
    metadata: TemplateMetadata = Field(..., description="Template metadata")
    paths: List[str] = Field(default_factory=list, description="Context file paths")
    hooks: Dict[str, Any] = Field(default_factory=dict, description="Hook configurations")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Profile settings")
    
    @validator('paths')
    def validate_paths(cls, v):
        for path in v:
            if not isinstance(path, str):
                raise ValueError('All paths must be strings')
            if path.startswith('/') and not path.startswith('//'):
                raise ValueError('Absolute paths are not recommended in templates')
        return v


class ContextTemplateSchema(BaseModel):
    """Schema for context template validation."""
    
    metadata: Optional[TemplateMetadata] = Field(None, description="Template metadata (frontmatter)")
    content: str = Field(..., description="Context content")
    tags: List[str] = Field(default_factory=list, description="Context tags")
    categories: List[str] = Field(default_factory=list, description="Context categories")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) < 50:
            raise ValueError('Context content must be substantial (at least 50 characters)')
        return v


class HookTemplateSchema(BaseModel):
    """Schema for hook template validation."""
    
    name: str = Field(..., description="Hook name")
    description: Optional[str] = Field(None, description="Hook description")
    version: str = Field(default="1.0", description="Hook version")
    type: str = Field(default="context", description="Hook type")
    trigger: str = Field(..., description="Hook trigger")
    timeout: int = Field(default=30, description="Hook timeout")
    enabled: bool = Field(default=True, description="Hook enabled status")
    metadata: Optional[TemplateMetadata] = Field(None, description="Template metadata")
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['context', 'script', 'hybrid', 'automation']
        if v not in valid_types:
            raise ValueError(f'Hook type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('trigger')
    def validate_trigger(cls, v):
        valid_triggers = [
            'on_session_start', 'per_user_message', 'on_file_change', 
            'on_profile_switch', 'on_file_save', 'manual'
        ]
        if v not in valid_triggers:
            raise ValueError(f'Hook trigger must be one of: {", ".join(valid_triggers)}')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0 or v > 300:
            raise ValueError('Timeout must be between 1 and 300 seconds')
        return v


class TemplateValidator:
    """Comprehensive validator for AI Configurator example templates."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """Initialize the template validator.
        
        Args:
            base_path: Base directory path for template files (defaults to examples/)
        """
        if base_path is None:
            base_path = Path.cwd() / 'examples'
        self.base_path = Path(base_path)
        self._template_registry: Dict[str, Dict[str, Any]] = {}
        
    def validate_all_templates(self) -> ValidationReport:
        """Validate all templates in the examples directory.
        
        Returns:
            Comprehensive validation report for all templates
        """
        errors = []
        warnings = []
        info = []
        files_checked = []
        
        # Discover all template files
        template_files = self._discover_template_files()
        
        # Validate each template
        for file_path in template_files:
            try:
                file_report = self.validate_template_file(file_path)
                errors.extend(file_report.errors)
                warnings.extend(file_report.warnings)
                info.extend(file_report.info)
                files_checked.extend(file_report.files_checked)
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="ValidationException",
                    message=f"Unexpected error during validation: {str(e)}",
                    severity="error"
                ))
                files_checked.append(str(file_path))
        
        # Validate cross-template references
        cross_ref_report = self._validate_cross_template_references()
        errors.extend(cross_ref_report.errors)
        warnings.extend(cross_ref_report.warnings)
        info.extend(cross_ref_report.info)
        
        # Generate summary
        summary = {
            "total_files": len(set(files_checked)),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "valid_files": len([f for f in files_checked if not any(e.file_path == f for e in errors)]),
            "invalid_files": len(set(e.file_path for e in errors))
        }
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=list(set(files_checked)),
            summary=summary
        )
    
    def validate_template_file(self, file_path: Union[str, Path]) -> ValidationReport:
        """Validate a single template file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            Validation report for the file
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        # Basic file existence check
        if not file_path.exists():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="FileNotFound",
                message=f"Template file not found: {file_path}",
                severity="error"
            ))
            return ValidationReport(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                info=info,
                files_checked=[str(file_path)],
                summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
            )
        
        try:
            # Determine template type and validate
            template_type = self._determine_template_type(file_path)
            
            if template_type == 'profile':
                self._validate_profile_template(file_path, errors, warnings, info)
            elif template_type == 'context':
                self._validate_context_template(file_path, errors, warnings, info)
            elif template_type == 'hook':
                self._validate_hook_template(file_path, errors, warnings, info)
            else:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="UnknownTemplateType",
                    message=f"Could not determine template type for {file_path}",
                    severity="warning"
                ))
            
            # Validate file naming conventions
            self._validate_naming_conventions(file_path, template_type, errors, warnings)
            
            # Register template for cross-reference validation
            self._register_template(file_path, template_type)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="UnexpectedError",
                message=f"Unexpected error during validation: {str(e)}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[str(file_path)],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def validate_profile_template(self, file_path: Union[str, Path]) -> ValidationReport:
        """Validate a profile template specifically.
        
        Args:
            file_path: Path to the profile template file
            
        Returns:
            Validation report for the profile template
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        try:
            self._validate_profile_template(file_path, errors, warnings, info)
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ProfileValidationError",
                message=f"Error validating profile template: {str(e)}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[str(file_path)],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def validate_context_template(self, file_path: Union[str, Path]) -> ValidationReport:
        """Validate a context template specifically.
        
        Args:
            file_path: Path to the context template file
            
        Returns:
            Validation report for the context template
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        try:
            self._validate_context_template(file_path, errors, warnings, info)
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextValidationError",
                message=f"Error validating context template: {str(e)}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[str(file_path)],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def validate_hook_template(self, file_path: Union[str, Path]) -> ValidationReport:
        """Validate a hook template specifically.
        
        Args:
            file_path: Path to the hook template file
            
        Returns:
            Validation report for the hook template
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        try:
            self._validate_hook_template(file_path, errors, warnings, info)
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="HookValidationError",
                message=f"Error validating hook template: {str(e)}",
                severity="error"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[str(file_path)],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def _discover_template_files(self) -> List[Path]:
        """Discover all template files in the examples directory."""
        template_files = []
        
        if not self.base_path.exists():
            return template_files
        
        # Profile templates (JSON files in profiles/)
        profiles_dir = self.base_path / 'profiles'
        if profiles_dir.exists():
            template_files.extend(profiles_dir.rglob('*.json'))
        
        # Context templates (Markdown files in contexts/)
        contexts_dir = self.base_path / 'contexts'
        if contexts_dir.exists():
            template_files.extend(contexts_dir.rglob('*.md'))
        
        # Hook templates (YAML files in hooks/)
        hooks_dir = self.base_path / 'hooks'
        if hooks_dir.exists():
            template_files.extend(hooks_dir.rglob('*.yaml'))
            template_files.extend(hooks_dir.rglob('*.yml'))
        
        # Workflow templates
        workflows_dir = self.base_path / 'workflows'
        if workflows_dir.exists():
            template_files.extend(workflows_dir.rglob('*.json'))
            template_files.extend(workflows_dir.rglob('*.yaml'))
            template_files.extend(workflows_dir.rglob('*.yml'))
        
        return list(set(template_files))  # Remove duplicates
    
    def _determine_template_type(self, file_path: Path) -> str:
        """Determine the type of template based on file path and content."""
        # Check file path patterns
        if 'profiles' in file_path.parts and file_path.suffix == '.json':
            return 'profile'
        elif 'contexts' in file_path.parts and file_path.suffix == '.md':
            return 'context'
        elif 'hooks' in file_path.parts and file_path.suffix in ['.yaml', '.yml']:
            return 'hook'
        elif 'workflows' in file_path.parts:
            if file_path.suffix == '.json':
                return 'profile'  # Workflow profiles
            elif file_path.suffix in ['.yaml', '.yml']:
                return 'hook'  # Workflow hooks
        
        return 'unknown'
    
    def _validate_profile_template(
        self, 
        file_path: Path, 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate a profile template file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse JSON with comments support
            json_data = self._parse_json_with_comments(content, file_path, errors)
            if json_data is None:
                return
            
            # Validate against schema
            try:
                profile_template = ProfileTemplateSchema(**json_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="SchemaValidationSuccess",
                    message=f"Profile template schema is valid: {profile_template.metadata.name}",
                    severity="info"
                ))
            except ValidationError as e:
                self._handle_validation_error(file_path, e, "ProfileTemplate", errors)
                return
            
            # Validate profile-specific rules
            self._validate_profile_rules(file_path, json_data, errors, warnings, info)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ProfileParsingError",
                message=f"Error parsing profile template: {str(e)}",
                severity="error"
            ))
    
    def _validate_context_template(
        self, 
        file_path: Path, 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate a context template file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if present
            frontmatter, main_content = self._parse_markdown_frontmatter(content)
            
            # Validate against schema
            try:
                context_data = {
                    'content': main_content,
                    'metadata': frontmatter if frontmatter else None
                }
                context_template = ContextTemplateSchema(**context_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="SchemaValidationSuccess",
                    message="Context template schema is valid",
                    severity="info"
                ))
            except ValidationError as e:
                self._handle_validation_error(file_path, e, "ContextTemplate", errors)
                return
            
            # Validate context-specific rules
            self._validate_context_rules(file_path, main_content, frontmatter, errors, warnings, info)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextParsingError",
                message=f"Error parsing context template: {str(e)}",
                severity="error"
            ))
    
    def _validate_hook_template(
        self, 
        file_path: Path, 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate a hook template file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML
            yaml_data = self._parse_yaml_with_errors(content, file_path, errors)
            if yaml_data is None:
                return
            
            # Validate against schema
            try:
                hook_template = HookTemplateSchema(**yaml_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="SchemaValidationSuccess",
                    message=f"Hook template schema is valid: {hook_template.name}",
                    severity="info"
                ))
            except ValidationError as e:
                self._handle_validation_error(file_path, e, "HookTemplate", errors)
                return
            
            # Validate hook-specific rules
            self._validate_hook_rules(file_path, yaml_data, errors, warnings, info)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="HookParsingError",
                message=f"Error parsing hook template: {str(e)}",
                severity="error"
            ))
    
    def _parse_json_with_comments(
        self, 
        content: str, 
        file_path: Path, 
        errors: List[ConfigurationError]
    ) -> Optional[Dict[str, Any]]:
        """Parse JSON content that may contain comments."""
        try:
            # Remove single-line comments (// ...)
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Find comment start, but not inside strings
                in_string = False
                escape_next = False
                comment_start = -1
                
                for i, char in enumerate(line):
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if not in_string and i < len(line) - 1:
                        if line[i:i+2] == '//':
                            comment_start = i
                            break
                
                if comment_start >= 0:
                    cleaned_lines.append(line[:comment_start].rstrip())
                else:
                    cleaned_lines.append(line)
            
            cleaned_content = '\n'.join(cleaned_lines)
            return json.loads(cleaned_content)
            
        except json.JSONDecodeError as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                line_number=e.lineno,
                column_number=e.colno,
                error_type="JSONSyntaxError",
                message=f"JSON syntax error: {str(e)}",
                severity="error"
            ))
            return None
    
    def _parse_yaml_with_errors(
        self, 
        content: str, 
        file_path: Path, 
        errors: List[ConfigurationError]
    ) -> Optional[Dict[str, Any]]:
        """Parse YAML content with detailed error reporting."""
        try:
            yaml_data = yaml.safe_load(content)
            if yaml_data is None:
                return {}
            return yaml_data
            
        except yaml.YAMLError as e:
            line_num = None
            col_num = None
            context = None
            
            if hasattr(e, 'problem_mark') and e.problem_mark:
                line_num = e.problem_mark.line + 1
                col_num = e.problem_mark.column + 1
                
                # Extract context around the error
                lines = content.split('\n')
                if 0 <= e.problem_mark.line < len(lines):
                    start_line = max(0, e.problem_mark.line - 2)
                    end_line = min(len(lines), e.problem_mark.line + 3)
                    context_lines = []
                    for i in range(start_line, end_line):
                        marker = " -> " if i == e.problem_mark.line else "    "
                        context_lines.append(f"{marker}{i+1:3}: {lines[i]}")
                    context = "\n".join(context_lines)
            
            errors.append(ConfigurationError(
                file_path=str(file_path),
                line_number=line_num,
                column_number=col_num,
                error_type="YAMLSyntaxError",
                message=f"YAML syntax error: {str(e)}",
                context=context,
                severity="error"
            ))
            
            return None
    
    def _parse_markdown_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parse markdown frontmatter and return metadata and content."""
        if not content.startswith('---'):
            return None, content
        
        try:
            # Find the end of frontmatter
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                return None, content
            
            frontmatter_content = content[3:end_marker]
            main_content = content[end_marker + 4:].strip()
            
            frontmatter = yaml.safe_load(frontmatter_content)
            return frontmatter, main_content
            
        except yaml.YAMLError:
            return None, content
    
    def _handle_validation_error(
        self, 
        file_path: Path, 
        error: ValidationError, 
        schema_type: str, 
        errors: List[ConfigurationError]
    ) -> None:
        """Handle Pydantic validation errors."""
        missing_fields = []
        invalid_fields = []
        
        for err in error.errors():
            field_path = " -> ".join(str(loc) for loc in err['loc'])
            error_type = err['type']
            
            if error_type == 'missing':
                missing_fields.append(field_path)
            else:
                invalid_fields.append(f"Field '{field_path}': {err['msg']}")
        
        # Create comprehensive error message
        error_parts = []
        if missing_fields:
            error_parts.append(f"Missing required fields: {', '.join(missing_fields)}")
        if invalid_fields:
            error_parts.append("Invalid field values:\n  " + "\n  ".join(invalid_fields))
        
        comprehensive_message = "\n".join(error_parts)
        
        errors.append(ConfigurationError(
            file_path=str(file_path),
            error_type="SchemaValidationError",
            message=comprehensive_message,
            context=f"Schema type: {schema_type}",
            severity="error"
        ))
    
    def _validate_naming_conventions(
        self, 
        file_path: Path, 
        template_type: str, 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError]
    ) -> None:
        """Validate file naming conventions."""
        filename = file_path.stem
        
        # Check for kebab-case naming
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', filename):
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="NamingConvention",
                message=f"Template filename should use kebab-case: {filename}",
                severity="warning"
            ))
        
        # Check for appropriate file extensions
        expected_extensions = {
            'profile': ['.json'],
            'context': ['.md'],
            'hook': ['.yaml', '.yml']
        }
        
        if template_type in expected_extensions:
            if file_path.suffix not in expected_extensions[template_type]:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidFileExtension",
                    message=f"{template_type.title()} templates should use {' or '.join(expected_extensions[template_type])} extension",
                    severity="error"
                ))
    
    def _validate_profile_rules(
        self, 
        file_path: Path, 
        json_data: Dict[str, Any], 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate profile-specific business rules."""
        # Check for empty paths
        paths = json_data.get('paths', [])
        if not paths:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="EmptyPaths",
                message="Profile template has no context paths defined",
                severity="warning"
            ))
        
        # Validate path references
        for path in paths:
            if isinstance(path, str):
                self._validate_template_reference(file_path, path, "context", errors, warnings)
        
        # Check for comprehensive documentation
        if 'metadata' in json_data:
            metadata = json_data['metadata']
            if not metadata.get('description') or len(metadata.get('description', '')) < 20:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InsufficientDocumentation",
                    message="Profile template should have a comprehensive description (at least 20 characters)",
                    severity="warning"
                ))
    
    def _validate_context_rules(
        self, 
        file_path: Path, 
        content: str, 
        frontmatter: Optional[Dict[str, Any]], 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate context-specific business rules."""
        # Check content length and structure
        if len(content) < 500:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ShortContent",
                message="Context template content is quite short - consider adding more comprehensive guidance",
                severity="warning"
            ))
        
        # Check for proper markdown structure
        if not content.startswith('#'):
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MissingMainHeader",
                message="Context template should start with a main header (#)",
                severity="warning"
            ))
        
        # Check for code examples if it's a technical context
        if any(keyword in content.lower() for keyword in ['code', 'programming', 'development', 'script']):
            if '```' not in content:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MissingCodeExamples",
                    message="Technical context template should include code examples",
                    severity="warning"
                ))
    
    def _validate_hook_rules(
        self, 
        file_path: Path, 
        yaml_data: Dict[str, Any], 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError], 
        info: List[ConfigurationError]
    ) -> None:
        """Validate hook-specific business rules."""
        # Check for script file reference
        if 'script' in yaml_data:
            script_path = yaml_data['script']
            if isinstance(script_path, str):
                script_file = file_path.parent / script_path
                if not script_file.exists():
                    errors.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="MissingScriptFile",
                        message=f"Referenced script file not found: {script_path}",
                        severity="error"
                    ))
        
        # Check for context sources
        if 'context' in yaml_data and 'sources' in yaml_data['context']:
            for source in yaml_data['context']['sources']:
                self._validate_template_reference(file_path, source, "context", errors, warnings)
        
        # Validate timeout values
        timeout = yaml_data.get('timeout', 30)
        if timeout > 120:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="LongTimeout",
                message=f"Hook timeout of {timeout}s is quite long - consider optimizing",
                severity="warning"
            ))
    
    def _validate_template_reference(
        self, 
        source_file: Path, 
        reference: str, 
        reference_type: str, 
        errors: List[ConfigurationError], 
        warnings: List[ConfigurationError]
    ) -> None:
        """Validate a reference to another template."""
        # Skip glob patterns and URLs
        if '*' in reference or reference.startswith(('http://', 'https://')):
            return
        
        # Resolve relative paths
        if reference.startswith('/'):
            ref_path = Path(reference)
        else:
            ref_path = self.base_path / reference
        
        if not ref_path.exists():
            errors.append(ConfigurationError(
                file_path=str(source_file),
                error_type="MissingTemplateReference",
                message=f"Referenced {reference_type} template not found: {reference}",
                context=f"Resolved path: {ref_path}",
                severity="error"
            ))
    
    def _register_template(self, file_path: Path, template_type: str) -> None:
        """Register template for cross-reference validation."""
        template_name = file_path.stem
        self._template_registry[template_name] = {
            'path': str(file_path),
            'type': template_type,
            'category': self._get_template_category(file_path)
        }
    
    def _get_template_category(self, file_path: Path) -> str:
        """Determine template category from file path."""
        parts = file_path.parts
        if 'basic' in parts:
            return 'basic'
        elif 'professional' in parts:
            return 'professional'
        elif 'advanced' in parts:
            return 'advanced'
        elif 'workflows' in parts:
            return 'workflow'
        return 'unknown'
    
    def _validate_cross_template_references(self) -> ValidationReport:
        """Validate references between templates."""
        errors = []
        warnings = []
        info = []
        
        # This would check for broken references between templates
        # For now, we'll just report on the template registry
        if self._template_registry:
            info.append(ConfigurationError(
                file_path="REGISTRY",
                error_type="TemplateRegistryInfo",
                message=f"Registered {len(self._template_registry)} templates for cross-reference validation",
                severity="info"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )