"""
Comprehensive configuration validation system for the library marketplace architecture.
Validates all configuration types: contexts, profiles, hooks, and MCP servers.
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

from .models import (
    ConfigurationError, ValidationReport, EnhancedProfileConfig, HookConfig,
    ContextFile, MCPConfiguration, MCPServerConfig, InstallationStatus,
    InstalledConfigMetadata, HookTrigger, HookType
)
from .metadata_parser import MetadataParser, ParseResult
from .catalog_schema import ConfigMetadata

logger = logging.getLogger(__name__)


class ConfigurationType(str, Enum):
    """Types of configurations that can be validated."""
    CONTEXT = "context"
    PROFILE = "profile"
    HOOK = "hook"
    MCP_SERVER = "mcp-server"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    """Validation error severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class DependencyNode:
    """Node in the dependency graph for circular dependency detection."""
    config_id: str
    dependencies: Set[str]
    visited: bool = False
    in_stack: bool = False


class LibraryConfigurationValidator:
    """
    Comprehensive validator for library-based configurations.
    
    Validates all configuration types (contexts, profiles, hooks, MCP servers)
    with schema validation, dependency checking, and circular dependency detection.
    """
    
    def __init__(self, library_path: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration validator.
        
        Args:
            library_path: Path to the library directory (defaults to 'library/')
        """
        self.library_path = Path(library_path) if library_path else Path("library")
        self.metadata_parser = MetadataParser(strict_validation=True)
        self._dependency_graph: Dict[str, DependencyNode] = {}
        self._config_registry: Dict[str, Dict[str, Any]] = {}
        
    def validate_all_configurations(self) -> ValidationReport:
        """
        Validate all configurations in the library.
        
        Returns:
            Comprehensive validation report for all configurations
        """
        errors = []
        warnings = []
        info = []
        files_checked = []
        
        try:
            # Discover all configuration files
            config_files = self._discover_configuration_files()
            
            # Validate each configuration file
            for file_path in config_files:
                try:
                    file_report = self.validate_configuration_file(file_path)
                    errors.extend(file_report.errors)
                    warnings.extend(file_report.warnings)
                    info.extend(file_report.info)
                    files_checked.extend(file_report.files_checked)
                except Exception as e:
                    logger.exception(f"Unexpected error validating {file_path}")
                    errors.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="ValidationException",
                        message=f"Unexpected error during validation: {str(e)}",
                        severity="error"
                    ))
                    files_checked.append(str(file_path))
            
            # Validate cross-configuration dependencies
            dependency_report = self._validate_dependencies()
            errors.extend(dependency_report.errors)
            warnings.extend(dependency_report.warnings)
            info.extend(dependency_report.info)
            
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
            summary = self._generate_summary(files_checked, errors, warnings, info)
            
            return ValidationReport(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                info=info,
                files_checked=list(set(files_checked)),
                summary=summary
            )
            
        except Exception as e:
            logger.exception("Critical error during validation")
            return ValidationReport(
                is_valid=False,
                errors=[ConfigurationError(
                    file_path="SYSTEM",
                    error_type="CriticalValidationError",
                    message=f"Critical validation error: {str(e)}",
                    severity="error"
                )],
                warnings=[],
                info=[],
                files_checked=[],
                summary={
                    "total_files": 0,
                    "errors": 1,
                    "warnings": 0,
                    "info": 0,
                    "valid_files": 0,
                    "invalid_files": 0,
                    "critical_error": True
                }
            )
    
    def validate_configuration_file(self, file_path: Union[str, Path]) -> ValidationReport:
        """
        Validate a single configuration file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Validation report for the file
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        # Basic file existence and readability check
        if not file_path.exists():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="FileNotFound",
                message=f"Configuration file not found: {file_path}",
                severity="error"
            ))
            return self._create_validation_report(errors, warnings, info, [str(file_path)])
        
        if not file_path.is_file():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="NotAFile",
                message=f"Path is not a file: {file_path}",
                severity="error"
            ))
            return self._create_validation_report(errors, warnings, info, [str(file_path)])
        
        try:
            # Determine configuration type
            config_type = self._determine_configuration_type(file_path)
            
            # Validate based on type
            if config_type == ConfigurationType.CONTEXT:
                self._validate_context_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.PROFILE:
                self._validate_profile_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.HOOK:
                self._validate_hook_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.MCP_SERVER:
                self._validate_mcp_server_file(file_path, errors, warnings, info)
            else:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="UnknownConfigurationType",
                    message=f"Could not determine configuration type for {file_path}",
                    severity="warning"
                ))
            
            # Validate metadata if present
            self._validate_metadata(file_path, errors, warnings, info)
            
            # Register configuration for dependency validation
            self._register_configuration(file_path, config_type)
            
        except Exception as e:
            logger.exception(f"Error validating {file_path}")
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ValidationError",
                message=f"Error during validation: {str(e)}",
                severity="error"
            ))
        
        return self._create_validation_report(errors, warnings, info, [str(file_path)])
    
    def validate_configuration_type(self, config_type: ConfigurationType, file_path: Union[str, Path]) -> ValidationReport:
        """
        Validate a configuration file of a specific type.
        
        Args:
            config_type: Type of configuration to validate
            file_path: Path to the configuration file
            
        Returns:
            Validation report for the specific configuration type
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        try:
            if config_type == ConfigurationType.CONTEXT:
                self._validate_context_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.PROFILE:
                self._validate_profile_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.HOOK:
                self._validate_hook_file(file_path, errors, warnings, info)
            elif config_type == ConfigurationType.MCP_SERVER:
                self._validate_mcp_server_file(file_path, errors, warnings, info)
            else:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="UnsupportedConfigurationType",
                    message=f"Unsupported configuration type: {config_type}",
                    severity="error"
                ))
        
        except Exception as e:
            logger.exception(f"Error validating {config_type} configuration {file_path}")
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="TypeValidationError",
                message=f"Error validating {config_type} configuration: {str(e)}",
                severity="error"
            ))
        
        return self._create_validation_report(errors, warnings, info, [str(file_path)])
    
    def _discover_configuration_files(self) -> List[Path]:
        """Discover all configuration files in the library."""
        config_files = []
        
        if not self.library_path.exists():
            logger.warning(f"Library path does not exist: {self.library_path}")
            return config_files
        
        # Context files (markdown in contexts/)
        contexts_dir = self.library_path / "contexts"
        if contexts_dir.exists():
            config_files.extend(contexts_dir.rglob("*.md"))
        
        # Profile files (YAML in profiles/)
        profiles_dir = self.library_path / "profiles"
        if profiles_dir.exists():
            config_files.extend(profiles_dir.rglob("*.yaml"))
            config_files.extend(profiles_dir.rglob("*.yml"))
        
        # Hook files (YAML in hooks/)
        hooks_dir = self.library_path / "hooks"
        if hooks_dir.exists():
            config_files.extend(hooks_dir.rglob("*.yaml"))
            config_files.extend(hooks_dir.rglob("*.yml"))
        
        # MCP server files (JSON in mcp-servers/)
        mcp_dir = self.library_path / "mcp-servers"
        if mcp_dir.exists():
            config_files.extend(mcp_dir.rglob("*.json"))
        
        return list(set(config_files))  # Remove duplicates
    
    def _determine_configuration_type(self, file_path: Path) -> ConfigurationType:
        """Determine the type of configuration based on file path and content."""
        # Check file path patterns first
        if "contexts" in file_path.parts and file_path.suffix == ".md":
            return ConfigurationType.CONTEXT
        elif "profiles" in file_path.parts and file_path.suffix in [".yaml", ".yml"]:
            return ConfigurationType.PROFILE
        elif "hooks" in file_path.parts and file_path.suffix in [".yaml", ".yml"]:
            return ConfigurationType.HOOK
        elif "mcp-servers" in file_path.parts and file_path.suffix == ".json":
            return ConfigurationType.MCP_SERVER
        
        # Try to determine from content
        try:
            if file_path.suffix == ".md":
                return ConfigurationType.CONTEXT
            elif file_path.suffix in [".yaml", ".yml"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if isinstance(content, dict):
                    # Check for hook-specific fields
                    if 'trigger' in content or 'type' in content:
                        return ConfigurationType.HOOK
                    # Check for profile-specific fields
                    elif 'contexts' in content or 'mcp_servers' in content:
                        return ConfigurationType.PROFILE
            elif file_path.suffix == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                if isinstance(content, dict):
                    # Check for MCP server configuration
                    if 'mcpServers' in content or 'mcp_servers' in content:
                        return ConfigurationType.MCP_SERVER
        
        except Exception as e:
            logger.debug(f"Could not determine config type from content for {file_path}: {e}")
        
        return ConfigurationType.UNKNOWN
    
    def _validate_context_file(self, file_path: Path, errors: List[ConfigurationError], 
                              warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate a context configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if present
            frontmatter, main_content = self._parse_markdown_frontmatter(content)
            
            # Validate content length
            if len(main_content.strip()) < 50:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="ShortContent",
                    message="Context content is very short - consider adding more comprehensive guidance",
                    severity="warning"
                ))
            
            # Validate frontmatter metadata if present
            if frontmatter:
                try:
                    # Create ContextFile object for validation
                    context_file = ContextFile(
                        file_path=str(file_path),
                        content=main_content,
                        metadata=frontmatter,
                        tags=frontmatter.get('tags', []),
                        categories=frontmatter.get('categories', []),
                        priority=frontmatter.get('priority', 0)
                    )
                    info.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="ContextValidationSuccess",
                        message="Context file structure is valid",
                        severity="info"
                    ))
                except Exception as e:
                    errors.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="ContextStructureError",
                        message=f"Invalid context file structure: {str(e)}",
                        severity="error"
                    ))
            
            # Check for common context patterns
            self._validate_context_patterns(file_path, main_content, warnings, info)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextParsingError",
                message=f"Error parsing context file: {str(e)}",
                severity="error"
            ))
    
    def _validate_profile_file(self, file_path: Path, errors: List[ConfigurationError],
                              warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate a profile configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML content
            yaml_data = yaml.safe_load(content)
            
            if not isinstance(yaml_data, dict):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidProfileFormat",
                    message="Profile file must contain a YAML dictionary",
                    severity="error"
                ))
                return
            
            # Validate against Pydantic model
            try:
                profile_config = EnhancedProfileConfig(**yaml_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="ProfileValidationSuccess",
                    message=f"Profile configuration is valid: {profile_config.name}",
                    severity="info"
                ))
                
                # Register for dependency checking
                self._register_profile_dependencies(file_path, profile_config)
                
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="ProfileSchemaError",
                    message=f"Profile schema validation failed: {str(e)}",
                    severity="error"
                ))
                return
            
            # Validate profile-specific rules
            self._validate_profile_rules(file_path, yaml_data, errors, warnings, info)
            
        except yaml.YAMLError as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="YAMLSyntaxError",
                message=f"YAML syntax error: {str(e)}",
                severity="error"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ProfileParsingError",
                message=f"Error parsing profile file: {str(e)}",
                severity="error"
            ))
    
    def _validate_hook_file(self, file_path: Path, errors: List[ConfigurationError],
                           warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate a hook configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML content
            yaml_data = yaml.safe_load(content)
            
            if not isinstance(yaml_data, dict):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidHookFormat",
                    message="Hook file must contain a YAML dictionary",
                    severity="error"
                ))
                return
            
            # Validate against Pydantic model
            try:
                hook_config = HookConfig(**yaml_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="HookValidationSuccess",
                    message=f"Hook configuration is valid: {hook_config.name}",
                    severity="info"
                ))
                
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="HookSchemaError",
                    message=f"Hook schema validation failed: {str(e)}",
                    severity="error"
                ))
                return
            
            # Validate hook-specific rules
            self._validate_hook_rules(file_path, yaml_data, errors, warnings, info)
            
        except yaml.YAMLError as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="YAMLSyntaxError",
                message=f"YAML syntax error: {str(e)}",
                severity="error"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="HookParsingError",
                message=f"Error parsing hook file: {str(e)}",
                severity="error"
            ))
    
    def _validate_mcp_server_file(self, file_path: Path, errors: List[ConfigurationError],
                                 warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate an MCP server configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse JSON content
            json_data = json.loads(content)
            
            if not isinstance(json_data, dict):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidMCPFormat",
                    message="MCP server file must contain a JSON object",
                    severity="error"
                ))
                return
            
            # Validate against Pydantic model
            try:
                mcp_config = MCPConfiguration(**json_data)
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MCPValidationSuccess",
                    message=f"MCP server configuration is valid with {len(mcp_config.mcp_servers)} servers",
                    severity="info"
                ))
                
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MCPSchemaError",
                    message=f"MCP server schema validation failed: {str(e)}",
                    severity="error"
                ))
                return
            
            # Validate MCP-specific rules
            self._validate_mcp_rules(file_path, json_data, errors, warnings, info)
            
        except json.JSONDecodeError as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                line_number=e.lineno,
                column_number=e.colno,
                error_type="JSONSyntaxError",
                message=f"JSON syntax error: {str(e)}",
                severity="error"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="MCPParsingError",
                message=f"Error parsing MCP server file: {str(e)}",
                severity="error"
            ))    

    def _validate_metadata(self, file_path: Path, errors: List[ConfigurationError],
                          warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate configuration metadata using the metadata parser."""
        try:
            parse_result = self.metadata_parser.parse_file(file_path)
            
            if not parse_result.success:
                for error in parse_result.errors:
                    errors.append(ConfigurationError(
                        file_path=str(file_path),
                        line_number=error.line_number,
                        error_type="MetadataError",
                        message=f"Metadata validation failed [{error.field}]: {error.message}",
                        severity="error"
                    ))
            else:
                info.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MetadataValidationSuccess",
                    message="Configuration metadata is valid",
                    severity="info"
                ))
                
                # Register metadata for dependency checking
                if parse_result.metadata:
                    self._register_metadata_dependencies(file_path, parse_result.metadata)
            
            # Add warnings
            for warning in parse_result.warnings:
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MetadataWarning",
                    message=f"Metadata warning: {warning}",
                    severity="warning"
                ))
                
        except Exception as e:
            logger.debug(f"No metadata found or error parsing metadata for {file_path}: {e}")
            # Not having metadata is not necessarily an error
    
    def _parse_markdown_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parse markdown frontmatter and return metadata and content."""
        if not content.startswith('---\n'):
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
    
    def _validate_context_patterns(self, file_path: Path, content: str,
                                  warnings: List[ConfigurationError], info: List[ConfigurationError]) -> None:
        """Validate common context patterns and best practices."""
        # Check for role definitions
        if re.search(r'(?i)(you are|act as|role)', content):
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextPatternFound",
                message="Context contains role definition - good practice",
                severity="info"
            ))
        
        # Check for examples
        if re.search(r'(?i)(example|for instance|such as)', content):
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextPatternFound",
                message="Context contains examples - good practice",
                severity="info"
            ))
        
        # Check for constraints or guidelines
        if re.search(r'(?i)(must|should|always|never|do not)', content):
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ContextPatternFound",
                message="Context contains clear constraints - good practice",
                severity="info"
            ))
        
        # Warn about very generic content
        generic_words = ['help', 'assist', 'support', 'general', 'basic']
        if sum(1 for word in generic_words if word.lower() in content.lower()) > 3:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="GenericContent",
                message="Context appears to be very generic - consider making it more specific",
                severity="warning"
            ))
    
    def _validate_profile_rules(self, file_path: Path, yaml_data: Dict[str, Any],
                               errors: List[ConfigurationError], warnings: List[ConfigurationError],
                               info: List[ConfigurationError]) -> None:
        """Validate profile-specific business rules."""
        # Check for empty contexts list
        contexts = yaml_data.get('contexts', [])
        if not contexts:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="EmptyContextsList",
                message="Profile has no contexts defined - it may not provide any context",
                severity="warning"
            ))
        
        # Validate context file references
        for context_path in contexts:
            if isinstance(context_path, str):
                self._validate_file_reference(file_path, context_path, "context", errors, warnings)
        
        # Check for hook configurations
        hooks = yaml_data.get('hooks', {})
        if hooks:
            for trigger, hook_list in hooks.items():
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
        
        # Check MCP server references
        mcp_servers = yaml_data.get('mcp_servers', [])
        for server_name in mcp_servers:
            if not isinstance(server_name, str):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidMCPReference",
                    message=f"MCP server reference must be a string, got: {type(server_name)}",
                    severity="error"
                ))
    
    def _validate_hook_rules(self, file_path: Path, yaml_data: Dict[str, Any],
                            errors: List[ConfigurationError], warnings: List[ConfigurationError],
                            info: List[ConfigurationError]) -> None:
        """Validate hook-specific business rules."""
        # Validate trigger values
        trigger = yaml_data.get('trigger')
        if trigger:
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
        hook_type = yaml_data.get('type', 'context')
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
        
        # Validate timeout values
        timeout = yaml_data.get('timeout', 30)
        if not isinstance(timeout, int) or timeout <= 0 or timeout > 300:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="InvalidTimeout",
                message=f"Hook timeout should be between 1 and 300 seconds, got: {timeout}",
                severity="warning"
            ))
        
        # Validate that context or script is defined based on type
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
        
        # Validate script references if present
        if has_script:
            script_config = yaml_data['script']
            if isinstance(script_config, dict):
                command = script_config.get('command')
                if command and ('/' in command or command.endswith(('.py', '.sh', '.js'))):
                    self._validate_file_reference(file_path, command, "script", errors, warnings)
    
    def _validate_mcp_rules(self, file_path: Path, json_data: Dict[str, Any],
                           errors: List[ConfigurationError], warnings: List[ConfigurationError],
                           info: List[ConfigurationError]) -> None:
        """Validate MCP server-specific business rules."""
        mcp_servers = json_data.get('mcpServers', json_data.get('mcp_servers', {}))
        
        if not mcp_servers:
            warnings.append(ConfigurationError(
                file_path=str(file_path),
                error_type="EmptyMCPServers",
                message="MCP configuration file contains no server definitions",
                severity="warning"
            ))
            return
        
        for server_name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidServerConfig",
                    message=f"MCP server '{server_name}' configuration must be an object",
                    severity="error"
                ))
                continue
            
            # Validate required fields
            if 'command' not in server_config:
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="MissingCommand",
                    message=f"MCP server '{server_name}' is missing required 'command' field",
                    severity="error"
                ))
            
            # Validate command format
            command = server_config.get('command')
            if command and not isinstance(command, str):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidCommand",
                    message=f"MCP server '{server_name}' command must be a string",
                    severity="error"
                ))
            
            # Validate args format
            args = server_config.get('args', [])
            if not isinstance(args, list):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidArgs",
                    message=f"MCP server '{server_name}' args must be a list",
                    severity="error"
                ))
            
            # Validate env format
            env = server_config.get('env', {})
            if not isinstance(env, dict):
                errors.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="InvalidEnv",
                    message=f"MCP server '{server_name}' env must be an object",
                    severity="error"
                ))
            
            # Check for common security issues
            if command and any(dangerous in command.lower() for dangerous in ['rm ', 'del ', 'format', 'sudo']):
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="PotentialSecurityIssue",
                    message=f"MCP server '{server_name}' command contains potentially dangerous operations",
                    severity="warning"
                ))
    
    def _validate_file_reference(self, source_file: Path, reference: str, reference_type: str,
                                errors: List[ConfigurationError], warnings: List[ConfigurationError]) -> None:
        """Validate a file reference exists."""
        # Skip glob patterns and URLs
        if '*' in reference or reference.startswith(('http://', 'https://', 'ftp://')):
            return
        
        # Skip system commands
        if reference_type == "script" and not ('/' in reference or reference.endswith(('.py', '.sh', '.js'))):
            return
        
        # Resolve relative paths
        if reference.startswith('/'):
            # Absolute path
            ref_path = Path(reference)
        else:
            # Relative to library path
            ref_path = self.library_path / reference
        
        if not ref_path.exists():
            errors.append(ConfigurationError(
                file_path=str(source_file),
                error_type="MissingFileReference",
                message=f"Referenced {reference_type} file not found: {reference}",
                context=f"Resolved path: {ref_path}",
                severity="error"
            ))
    
    def _register_configuration(self, file_path: Path, config_type: ConfigurationType) -> None:
        """Register a configuration for dependency tracking."""
        config_id = self._generate_config_id(file_path)
        self._config_registry[config_id] = {
            'file_path': str(file_path),
            'config_type': config_type.value,
            'dependencies': set()
        }
    
    def _register_profile_dependencies(self, file_path: Path, profile_config: EnhancedProfileConfig) -> None:
        """Register profile dependencies for validation."""
        config_id = self._generate_config_id(file_path)
        dependencies = set()
        
        # Add context dependencies
        for context_path in profile_config.contexts:
            dep_id = self._path_to_config_id(context_path)
            dependencies.add(dep_id)
        
        # Add hook dependencies
        for trigger, hook_list in profile_config.hooks.items():
            for hook_ref in hook_list:
                if hasattr(hook_ref, 'name'):
                    dep_id = f"hook-{hook_ref.name}"
                    dependencies.add(dep_id)
        
        # Add MCP server dependencies
        for server_name in profile_config.mcp_servers:
            dep_id = f"mcp-{server_name}"
            dependencies.add(dep_id)
        
        if config_id in self._config_registry:
            self._config_registry[config_id]['dependencies'] = dependencies
    
    def _register_metadata_dependencies(self, file_path: Path, metadata: ConfigMetadata) -> None:
        """Register metadata dependencies for validation."""
        config_id = self._generate_config_id(file_path)
        dependencies = set(metadata.dependencies)
        
        if config_id in self._config_registry:
            self._config_registry[config_id]['dependencies'].update(dependencies)
        
        # Create dependency node for circular dependency detection
        self._dependency_graph[config_id] = DependencyNode(
            config_id=config_id,
            dependencies=dependencies
        )
    
    def _generate_config_id(self, file_path: Path) -> str:
        """Generate a configuration ID from file path."""
        relative_path = file_path.relative_to(self.library_path)
        return str(relative_path).replace('/', '-').replace('\\', '-')
    
    def _path_to_config_id(self, path: str) -> str:
        """Convert a file path to a configuration ID."""
        return path.replace('/', '-').replace('\\', '-')
    
    def _validate_dependencies(self) -> ValidationReport:
        """Validate cross-configuration dependencies."""
        errors = []
        warnings = []
        info = []
        
        # Check that all dependencies exist
        for config_id, config_info in self._config_registry.items():
            for dep_id in config_info['dependencies']:
                if dep_id not in self._config_registry and not self._is_external_dependency(dep_id):
                    errors.append(ConfigurationError(
                        file_path=config_info['file_path'],
                        error_type="MissingDependency",
                        message=f"Configuration depends on missing configuration: {dep_id}",
                        severity="error"
                    ))
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[],
            summary={"dependency_errors": len(errors)}
        )
    
    def _is_external_dependency(self, dep_id: str) -> bool:
        """Check if a dependency is external (e.g., system command, URL)."""
        return (
            dep_id.startswith(('http://', 'https://')) or
            dep_id.startswith('mcp-') or  # MCP servers might be external
            dep_id.startswith('hook-')    # Hooks might be external
        )
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        
        def dfs(node_id: str, path: List[str], visited: Set[str], rec_stack: Set[str]) -> None:
            if node_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(node_id)
                cycle = path[cycle_start:] + [node_id]
                cycles.append(cycle)
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            # Visit dependencies
            node = self._dependency_graph.get(node_id)
            if node:
                for dep_id in node.dependencies:
                    if dep_id in self._dependency_graph:
                        dfs(dep_id, path.copy(), visited, rec_stack)
            
            rec_stack.remove(node_id)
        
        visited = set()
        for node_id in self._dependency_graph:
            if node_id not in visited:
                dfs(node_id, [], visited, set())
        
        return cycles
    
    def _generate_summary(self, files_checked: List[str], errors: List[ConfigurationError],
                         warnings: List[ConfigurationError], info: List[ConfigurationError]) -> Dict[str, Any]:
        """Generate validation summary statistics."""
        return {
            "total_files": len(set(files_checked)),
            "errors": len(errors),
            "warnings": len(warnings),
            "info": len(info),
            "valid_files": len([f for f in files_checked if not any(e.file_path == f for e in errors)]),
            "invalid_files": len(set(e.file_path for e in errors if e.file_path != "SYSTEM")),
            "dependency_graph_size": len(self._dependency_graph)
        }
    
    def _count_configurations_by_type(self) -> Dict[str, int]:
        """Count configurations by type."""
        counts = {}
        for config_info in self._config_registry.values():
            config_type = config_info['config_type']
            counts[config_type] = counts.get(config_type, 0) + 1
        return counts
    
    def _create_validation_report(self, errors: List[ConfigurationError], warnings: List[ConfigurationError],
                                 info: List[ConfigurationError], files_checked: List[str]) -> ValidationReport:
        """Create a validation report."""
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=files_checked,
            summary={
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "files_checked": len(files_checked)
            }
        )


def validate_library_configurations(library_path: str = "library") -> ValidationReport:
    """
    CLI function to validate all library configurations.
    
    Args:
        library_path: Path to the library directory
        
    Returns:
        Comprehensive validation report
    """
    validator = LibraryConfigurationValidator(library_path)
    return validator.validate_all_configurations()


if __name__ == "__main__":
    import sys
    
    library_path = sys.argv[1] if len(sys.argv) > 1 else "library"
    report = validate_library_configurations(library_path)
    
    print("Library Configuration Validation Report")
    print("=" * 50)
    print(f"Valid: {report.is_valid}")
    print(f"Files checked: {len(report.files_checked)}")
    print(f"Errors: {len(report.errors)}")
    print(f"Warnings: {len(report.warnings)}")
    print(f"Info: {len(report.info)}")
    
    if report.errors:
        print("\nERRORS:")
        for error in report.errors:
            print(f"  {error.file_path}: {error.message}")
    
    if report.warnings:
        print("\nWARNINGS:")
        for warning in report.warnings:
            print(f"  {warning.file_path}: {warning.message}")
    
    # Exit with error code if validation failed
    sys.exit(0 if report.is_valid else 1)