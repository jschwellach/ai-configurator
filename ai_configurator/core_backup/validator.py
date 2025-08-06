"""Comprehensive validation system for YAML configurations."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import re
from collections import defaultdict, deque

import yaml
from pydantic import ValidationError

from .models import (
    EnhancedProfileConfig,
    HookConfig,
    ContextFile,
    ConfigurationError,
    ValidationReport,
    PathLike,
    YamlConfigDict,
    HookTrigger,
    HookType,
    ValidationLevel,
)


class ConfigurationValidator:
    """
    Comprehensive validator for YAML configuration files.
    
    This class provides schema validation, file reference validation,
    circular dependency detection, and detailed error reporting.
    """
    
    def __init__(self, base_path: Optional[PathLike] = None):
        """
        Initialize the configuration validator.
        
        Args:
            base_path: Base directory path for configuration files.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._reference_graph: Dict[str, Set[str]] = defaultdict(set)
        
    def validate_all_configurations(self) -> ValidationReport:
        """
        Validate all configuration files in the base directory.
        
        Returns:
            Comprehensive validation report for all configurations
        """
        errors = []
        warnings = []
        info = []
        files_checked = []
        
        # Discover all configuration files
        config_files = self._discover_all_config_files()
        
        # Validate each file
        for file_path in config_files:
            try:
                file_report = self.validate_configuration_file(file_path)
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
        
        # Perform cross-file validation
        cross_file_report = self._validate_cross_file_references(config_files)
        errors.extend(cross_file_report.errors)
        warnings.extend(cross_file_report.warnings)
        info.extend(cross_file_report.info)
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies()
        for cycle in circular_deps:
            errors.append(ConfigurationError(
                file_path=" -> ".join(cycle),
                error_type="CircularDependency",
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                severity="error"
            ))
        
        # Generate summary
        summary = {
            "total_files": len(set(files_checked)),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "valid_files": len([f for f in files_checked if not any(e.file_path == f for e in errors)]),
            "invalid_files": len(set(e.file_path for e in errors))
        }
        
        # Add configuration summary if validation passes
        if len(errors) == 0:
            config_summary = self._generate_configuration_summary(config_files)
            info.append(ConfigurationError(
                file_path="SUMMARY",
                error_type="ConfigurationSummary",
                message=config_summary,
                severity="info"
            ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=list(set(files_checked)),
            summary=summary
        )
    
    def validate_configuration_file(self, file_path: PathLike) -> ValidationReport:
        """
        Validate a single configuration file with comprehensive checks.
        
        Args:
            file_path: Path to the configuration file
            
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
                message=f"Configuration file not found: {file_path}",
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
        
        # Read and parse file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML with detailed error reporting
            yaml_data = self._parse_yaml_with_errors(content, file_path, errors)
            if yaml_data is None:
                return ValidationReport(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    info=info,
                    files_checked=[str(file_path)],
                    summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
                )
            
            # Determine configuration type and validate schema
            config_type = self._determine_config_type(file_path, yaml_data)
            self._validate_schema(file_path, yaml_data, config_type, errors, warnings, info)
            
            # Validate file references
            self._validate_file_references(file_path, yaml_data, errors, warnings)
            
            # Validate configuration-specific rules
            self._validate_configuration_rules(file_path, yaml_data, config_type, errors, warnings, info)
            
            # Build reference graph for circular dependency detection
            self._build_reference_graph(file_path, yaml_data)
            
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
    
    def validate_schema(self, file_path: PathLike, config_type: str) -> ValidationReport:
        """
        Validate configuration schema for a specific file type.
        
        Args:
            file_path: Path to the configuration file
            config_type: Type of configuration ('profile', 'hook', 'context')
            
        Returns:
            Schema validation report
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        if not file_path.exists():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="FileNotFound",
                message=f"Configuration file not found: {file_path}",
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_data = self._parse_yaml_with_errors(content, file_path, errors)
            if yaml_data is not None:
                self._validate_schema(file_path, yaml_data, config_type, errors, warnings, info)
        
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="UnexpectedError",
                message=f"Unexpected error during schema validation: {str(e)}",
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
    
    def _discover_all_config_files(self) -> List[Path]:
        """Discover all configuration files in the base directory."""
        config_files = []
        
        # Profile files
        profiles_dir = self.base_path / 'profiles'
        if profiles_dir.exists():
            config_files.extend(profiles_dir.glob('*.yaml'))
            config_files.extend(profiles_dir.glob('*.yml'))
        
        # Hook files
        hooks_dir = self.base_path / 'hooks'
        if hooks_dir.exists():
            config_files.extend(hooks_dir.glob('*.yaml'))
            config_files.extend(hooks_dir.glob('*.yml'))
        
        # Context files (Markdown)
        contexts_dir = self.base_path / 'contexts'
        if contexts_dir.exists():
            config_files.extend(contexts_dir.glob('*.md'))
            config_files.extend(contexts_dir.rglob('*.md'))
        
        return list(set(config_files))  # Remove duplicates
    
    def _parse_yaml_with_errors(
        self, 
        content: str, 
        file_path: Path, 
        errors: List[ConfigurationError]
    ) -> Optional[Dict[str, Any]]:
        """Parse YAML content with detailed error reporting."""
        try:
            # Handle Markdown files with frontmatter
            if file_path.suffix == '.md':
                return self._parse_markdown_frontmatter(content, file_path, errors)
            
            yaml_data = yaml.safe_load(content)
            
            if yaml_data is None:
                # Empty file - not necessarily an error
                return {}
            
            return yaml_data
            
        except yaml.YAMLError as e:
            # Extract detailed error information
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
    
    def _determine_config_type(self, file_path: Path, yaml_data: Dict[str, Any]) -> str:
        """Determine the type of configuration based on file path and content."""
        # Check file path patterns
        if 'profiles' in file_path.parts:
            return 'profile'
        elif 'hooks' in file_path.parts:
            return 'hook'
        elif file_path.suffix == '.md':
            return 'context'
        
        # Check content patterns
        if 'trigger' in yaml_data or 'type' in yaml_data:
            return 'hook'
        elif 'contexts' in yaml_data or 'mcp_servers' in yaml_data:
            return 'profile'
        
        return 'unknown'
    
    def _validate_schema(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        config_type: str,
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError],
        info: List[ConfigurationError]
    ) -> None:
        """Validate configuration against Pydantic schemas."""
        try:
            if config_type == 'profile':
                # Validate as profile configuration
                profile_config = EnhancedProfileConfig(**yaml_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="SchemaValidationSuccess",
                    message=f"Profile configuration schema is valid: {profile_config.name}",
                    severity="info"
                ))
                
            elif config_type == 'hook':
                # Validate as hook configuration
                hook_config = HookConfig(**yaml_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="SchemaValidationSuccess",
                    message=f"Hook configuration schema is valid: {hook_config.name}",
                    severity="info"
                ))
                
            elif config_type == 'context':
                # Context files are Markdown - validate frontmatter if present
                self._validate_context_frontmatter(file_path, yaml_data, errors, warnings, info)
                
            else:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="UnknownConfigType",
                    message=f"Could not determine configuration type for {file_path}",
                    severity="warning"
                ))
                
        except ValidationError as e:
            # Collect all validation errors into a single comprehensive message
            missing_fields = []
            invalid_fields = []
            
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                error_type = error['type']
                
                if error_type == 'missing':
                    missing_fields.append(field_path)
                else:
                    invalid_fields.append(f"Field '{field_path}': {error['msg']}")
            
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
                context=f"Configuration type: {config_type}",
                severity="error"
            ))
    
    def _validate_file_references(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError]
    ) -> None:
        """Validate that all file references exist."""
        # Check context file references
        if 'contexts' in yaml_data:
            for context_ref in yaml_data['contexts']:
                if isinstance(context_ref, str):
                    self._validate_single_file_reference(
                        file_path, context_ref, "context", errors, warnings
                    )
        
        # Check hook context sources
        if 'context' in yaml_data and isinstance(yaml_data['context'], dict):
            context_config = yaml_data['context']
            if 'sources' in context_config:
                for source_ref in context_config['sources']:
                    if isinstance(source_ref, str):
                        self._validate_single_file_reference(
                            file_path, source_ref, "context source", errors, warnings
                        )
        
        # Check script references
        if 'script' in yaml_data and isinstance(yaml_data['script'], dict):
            script_config = yaml_data['script']
            if 'command' in script_config:
                command = script_config['command']
                # Check if command is a file path (not a system command)
                if '/' in command or command.endswith('.py') or command.endswith('.sh'):
                    self._validate_single_file_reference(
                        file_path, command, "script", errors, warnings
                    )
    
    def _validate_single_file_reference(
        self,
        source_file: Path,
        reference: str,
        reference_type: str,
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError]
    ) -> None:
        """Validate a single file reference."""
        # Skip glob patterns and URLs
        if '*' in reference or reference.startswith(('http://', 'https://', 'ftp://')):
            return
        
        # Resolve relative paths
        if reference.startswith('/'):
            # Absolute path
            ref_path = Path(reference)
        else:
            # Relative to base path
            ref_path = self.base_path / reference
        
        if not ref_path.exists():
            errors.append(ConfigurationError(
                file_path=str(source_file),
                error_type="MissingFileReference",
                message=f"Referenced {reference_type} file not found: {reference}",
                context=f"Resolved path: {ref_path}",
                severity="error"
            ))
    
    def _validate_configuration_rules(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        config_type: str,
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError],
        info: List[ConfigurationError]
    ) -> None:
        """Validate configuration-specific business rules."""
        # Common validations
        if 'name' not in yaml_data:
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MissingName",
                message="Configuration does not specify a 'name' field (will use filename)",
                severity="info"
            ))
        
        # Profile-specific validations
        if config_type == 'profile':
            self._validate_profile_rules(file_path, yaml_data, errors, warnings, info)
        
        # Hook-specific validations
        elif config_type == 'hook':
            self._validate_hook_rules(file_path, yaml_data, errors, warnings, info)
    
    def _validate_profile_rules(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError],
        info: List[ConfigurationError]
    ) -> None:
        """Validate profile-specific rules."""
        # Check for empty contexts list
        if 'contexts' in yaml_data and len(yaml_data['contexts']) == 0:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="EmptyContextsList",
                message="Profile has no contexts defined - it may not provide any context",
                severity="warning"
            ))
        
        # Check for deprecated fields
        deprecated_fields = ['legacy_hooks', 'old_context_format', 'json_config']
        for field in deprecated_fields:
            if field in yaml_data:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="DeprecatedField",
                    message=f"Field '{field}' is deprecated and should be removed",
                    severity="warning"
                ))
        
        # Validate hook references
        if 'hooks' in yaml_data:
            for trigger, hook_list in yaml_data['hooks'].items():
                if not isinstance(hook_list, list):
                    errors.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="InvalidHookFormat",
                        message=f"Hook trigger '{trigger}' must contain a list of hooks",
                        severity="error"
                    ))
                    continue
                
                for hook_ref in hook_list:
                    if isinstance(hook_ref, dict) and 'name' not in hook_ref:
                        errors.append(ConfigurationError(
                            file_path=str(file_path),
                            error_type="MissingHookName",
                            message=f"Hook reference in trigger '{trigger}' is missing 'name' field",
                            severity="error"
                        ))
    
    def _validate_hook_rules(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError],
        info: List[ConfigurationError]
    ) -> None:
        """Validate hook-specific rules."""
        # Validate trigger values
        if 'trigger' in yaml_data:
            trigger = yaml_data['trigger']
            try:
                HookTrigger(trigger)
            except ValueError:
                valid_triggers = [t.value for t in HookTrigger]
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidTrigger",
                    message=f"Invalid hook trigger '{trigger}'. Valid triggers: {', '.join(valid_triggers)}",
                    severity="error"
                ))
        
        # Validate hook type
        if 'type' in yaml_data:
            hook_type = yaml_data['type']
            try:
                HookType(hook_type)
            except ValueError:
                valid_types = [t.value for t in HookType]
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidHookType",
                    message=f"Invalid hook type '{hook_type}'. Valid types: {', '.join(valid_types)}",
                    severity="error"
                ))
        
        # Validate that context or script is defined based on type
        hook_type = yaml_data.get('type', 'context')
        has_context = 'context' in yaml_data and yaml_data['context']
        has_script = 'script' in yaml_data and yaml_data['script']
        
        if hook_type == 'context' and not has_context:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MissingContext",
                message="Hook type is 'context' but no context configuration is provided",
                severity="warning"
            ))
        elif hook_type == 'script' and not has_script:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MissingScript",
                message="Hook type is 'script' but no script configuration is provided",
                severity="warning"
            ))
        elif hook_type == 'hybrid' and not (has_context or has_script):
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MissingHybridConfig",
                message="Hook type is 'hybrid' but neither context nor script configuration is provided",
                severity="warning"
            ))
    
    def _validate_context_frontmatter(
        self,
        file_path: Path,
        yaml_data: Dict[str, Any],
        errors: List[ConfigurationError],
        warnings: List[ConfigurationError],
        info: List[ConfigurationError]
    ) -> None:
        """Validate context file frontmatter."""
        # Context files are validated differently since they're Markdown
        # This would be called if frontmatter is detected
        if yaml_data:
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextFrontmatterValid",
                message="Context file frontmatter is valid",
                severity="info"
            ))
    
    def _build_reference_graph(self, file_path: Path, yaml_data: Dict[str, Any]) -> None:
        """Build reference graph for circular dependency detection."""
        file_key = str(file_path)
        
        # Add context references
        if 'contexts' in yaml_data:
            for context_ref in yaml_data['contexts']:
                if isinstance(context_ref, str) and '*' not in context_ref:
                    # Resolve to absolute path
                    if context_ref.startswith('/'):
                        ref_path = context_ref
                    else:
                        ref_path = str(self.base_path / context_ref)
                    self._reference_graph[file_key].add(ref_path)
        
        # Add hook context source references
        if 'context' in yaml_data and isinstance(yaml_data['context'], dict):
            context_config = yaml_data['context']
            if 'sources' in context_config:
                for source_ref in context_config['sources']:
                    if isinstance(source_ref, str) and '*' not in source_ref:
                        if source_ref.startswith('/'):
                            ref_path = source_ref
                        else:
                            ref_path = str(self.base_path / source_ref)
                        self._reference_graph[file_key].add(ref_path)
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in configuration references."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self._reference_graph.get(node, set()):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in self._reference_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _validate_cross_file_references(self, config_files: List[Path]) -> ValidationReport:
        """Validate references between configuration files."""
        errors = []
        warnings = []
        info = []
        
        # Create a map of available files
        available_files = {str(f): f for f in config_files}
        
        # Check that referenced files exist in the discovered set
        for file_path, references in self._reference_graph.items():
            for ref_path in references:
                if ref_path not in available_files and not Path(ref_path).exists():
                    errors.append(ConfigurationError(
                        file_path=file_path,
                        error_type="CrossFileReferenceError",
                        message=f"Referenced file not found in configuration set: {ref_path}",
                        severity="error"
                    ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def _generate_configuration_summary(self, config_files: List[Path]) -> str:
        """Generate a summary of loaded configurations."""
        profiles = []
        hooks = []
        contexts = []
        
        for file_path in config_files:
            if 'profiles' in file_path.parts or file_path.parent.name == 'profiles':
                profiles.append(file_path.stem)
            elif 'hooks' in file_path.parts or file_path.parent.name == 'hooks':
                hooks.append(file_path.stem)
            elif file_path.suffix == '.md':
                contexts.append(str(file_path.relative_to(self.base_path)))
        
        summary_parts = [
            f"Configuration Summary:",
            f"  Profiles: {len(profiles)} ({', '.join(sorted(profiles)) if profiles else 'none'})",
            f"  Hooks: {len(hooks)} ({', '.join(sorted(hooks)) if hooks else 'none'})",
            f"  Contexts: {len(contexts)} files",
            f"  Total files validated: {len(config_files)}"
        ]
        
        return "\n".join(summary_parts)
    
    def _parse_markdown_frontmatter(
        self, 
        content: str, 
        file_path: Path, 
        errors: List[ConfigurationError]
    ) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from Markdown content."""
        lines = content.split('\n')
        
        # Check if file starts with frontmatter delimiter
        if not lines or lines[0].strip() != '---':
            # No frontmatter, return empty dict
            return {}
        
        # Find the closing delimiter
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break
        
        if frontmatter_end == -1:
            # No closing delimiter found
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MalformedFrontmatter",
                message="Markdown frontmatter is missing closing '---' delimiter",
                severity="error"
            ))
            return {}
        
        # Extract frontmatter content
        frontmatter_content = '\n'.join(lines[1:frontmatter_end])
        
        if not frontmatter_content.strip():
            # Empty frontmatter
            return {}
        
        try:
            yaml_data = yaml.safe_load(frontmatter_content)
            return yaml_data if yaml_data is not None else {}
            
        except yaml.YAMLError as e:
            # Extract detailed error information for frontmatter
            line_num = None
            col_num = None
            context = None
            
            if hasattr(e, 'problem_mark') and e.problem_mark:
                # Adjust line numbers to account for frontmatter position in file
                line_num = e.problem_mark.line + 2  # +1 for opening ---, +1 for 0-based
                col_num = e.problem_mark.column + 1
                
                # Extract context from frontmatter
                fm_lines = frontmatter_content.split('\n')
                if 0 <= e.problem_mark.line < len(fm_lines):
                    start_line = max(0, e.problem_mark.line - 2)
                    end_line = min(len(fm_lines), e.problem_mark.line + 3)
                    context_lines = []
                    for i in range(start_line, end_line):
                        marker = " -> " if i == e.problem_mark.line else "    "
                        actual_line_num = i + 2  # Adjust for position in file
                        context_lines.append(f"{marker}{actual_line_num:3}: {fm_lines[i]}")
                    context = "\n".join(context_lines)
            
            errors.append(ConfigurationError(
                file_path=str(file_path),
                line_number=line_num,
                column_number=col_num,
                error_type="FrontmatterSyntaxError",
                message=f"YAML frontmatter syntax error: {str(e)}",
                context=context,
                severity="error"
            ))
            
            return None