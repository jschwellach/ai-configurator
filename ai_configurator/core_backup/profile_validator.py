"""Profile validation functions for AI Configuration Library."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import yaml
import re
import hashlib
from datetime import datetime
from .models import Profile, ConfigurationError, ValidationReport


class ProfileValidationError(Exception):
    """Exception raised when profile validation fails."""
    pass


class ProfileValidator:
    """Validates profile configurations and structure."""

    REQUIRED_FIELDS = {
        'name': str,
        'description': str,
        'version': str,
        'author': str,
        'category': str,
        'tags': list,
        'contexts': list,
        'hooks': list,
        'targets': dict
    }

    OPTIONAL_FIELDS = {
        'dependencies': list,
        'metadata': dict,
        'license': str,
        'homepage': str,
        'repository': str,
        'keywords': list,
        'maintainers': list
    }

    VALID_CATEGORIES = {
        'business', 'development', 'analysis', 'automation', 
        'communication', 'research', 'security', 'other'
    }

    VALID_TARGETS = {'kiro', 'amazonq'}
    
    # File naming patterns
    VALID_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+\.(md|yaml|yml|json)$')
    VALID_HOOK_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+\.(md|yaml|yml|json|py|sh)$')  # Allow scripts in hooks
    RESERVED_NAMES = {'profile', 'manifest', 'readme', 'license'}
    
    # Content validation patterns
    MARKDOWN_FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
    YAML_HOOK_REQUIRED_FIELDS = {'name', 'trigger', 'type'}
    
    # Size limits
    MAX_FILE_SIZE_MB = 10
    MAX_CONTEXT_FILES = 50
    MAX_HOOK_FILES = 20
    MAX_DESCRIPTION_LENGTH = 500
    MAX_NAME_LENGTH = 100

    @classmethod
    def validate_profile_yaml(cls, yaml_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a profile YAML file.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not yaml_path.exists():
            return False, [f"Profile file does not exist: {yaml_path}"]
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML syntax: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]

        if not isinstance(data, dict):
            return False, ["Profile must be a YAML dictionary"]

        # Validate required fields
        for field, expected_type in cls.REQUIRED_FIELDS.items():
            if field not in data:
                errors.append(f"Missing required field: {field}")
                continue
            
            if not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")

        # Validate optional fields if present
        for field, expected_type in cls.OPTIONAL_FIELDS.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")

        # Validate specific field constraints
        if 'category' in data:
            print(f"DEBUG: Validating category: {data['category']} (type: {type(data['category'])})")
            try:
                if data['category'] not in cls.VALID_CATEGORIES:
                    errors.append(f"Invalid category '{data['category']}'. Must be one of: {', '.join(cls.VALID_CATEGORIES)}")
            except TypeError as e:
                errors.append(f"Category validation error: {e}, category type: {type(data['category'])}, category value: {data['category']}")

        if 'tags' in data:
            if not all(isinstance(tag, str) for tag in data['tags']):
                errors.append("All tags must be strings")

        if 'contexts' in data:
            if not all(isinstance(ctx, str) for ctx in data['contexts']):
                errors.append("All context entries must be strings")

        if 'hooks' in data:
            if not all(isinstance(hook, str) for hook in data['hooks']):
                errors.append("All hook entries must be strings")

        # Validate targets structure
        if 'targets' in data:
            targets_errors = cls._validate_targets(data['targets'])
            errors.extend(targets_errors)

        # Validate version format (basic semver check)
        if 'version' in data:
            version_errors = cls._validate_version(data['version'])
            errors.extend(version_errors)

        return len(errors) == 0, errors

    @classmethod
    def _validate_targets(cls, targets: Dict) -> List[str]:
        """Validate targets configuration."""
        errors = []
        
        if not isinstance(targets, dict):
            return ["Targets must be a dictionary"]

        for target_name, target_config in targets.items():
            if target_name not in cls.VALID_TARGETS:
                errors.append(f"Invalid target '{target_name}'. Must be one of: {', '.join(cls.VALID_TARGETS)}")
                continue
            
            if not isinstance(target_config, dict):
                errors.append(f"Target '{target_name}' configuration must be a dictionary")
                continue
            
            # Validate target-specific directory configurations
            if target_name == 'kiro':
                required_dirs = ['contexts_dir', 'hooks_dir']
            elif target_name == 'amazonq':
                required_dirs = ['contexts_dir', 'hooks_dir']
            
            for dir_key in required_dirs:
                if dir_key not in target_config:
                    errors.append(f"Target '{target_name}' missing required directory: {dir_key}")
                elif not isinstance(target_config[dir_key], str):
                    errors.append(f"Target '{target_name}' directory '{dir_key}' must be a string")

        return errors

    @classmethod
    def _validate_version(cls, version: str) -> List[str]:
        """Validate version format (basic semver)."""
        errors = []
        
        if not isinstance(version, str):
            return ["Version must be a string"]
        
        parts = version.split('.')
        if len(parts) != 3:
            errors.append("Version must follow semantic versioning (x.y.z)")
        else:
            for i, part in enumerate(parts):
                try:
                    int(part)
                except ValueError:
                    errors.append(f"Version part {i+1} must be a number")
        
        return errors

    @classmethod
    def validate_profile_structure(cls, profile_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate the complete profile directory structure.
        
        Args:
            profile_dir: Path to profile directory
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not profile_dir.exists():
            return False, [f"Profile directory does not exist: {profile_dir}"]
        
        if not profile_dir.is_dir():
            return False, [f"Profile path is not a directory: {profile_dir}"]
        
        # Check for profile.yaml
        profile_yaml = profile_dir / 'profile.yaml'
        if not profile_yaml.exists():
            errors.append("Missing profile.yaml file")
            return False, errors
        
        # Validate the YAML file
        yaml_valid, yaml_errors = cls.validate_profile_yaml(profile_yaml)
        if not yaml_valid:
            errors.extend(yaml_errors)
            return False, errors
        
        # Load profile to check file references
        try:
            profile = Profile.from_yaml(profile_yaml)
        except Exception as e:
            errors.append(f"Error loading profile: {e}")
            return False, errors
        
        # Validate directory structure
        structure_errors = cls._validate_directory_structure(profile_dir, profile)
        errors.extend(structure_errors)
        
        # Validate file contents
        content_errors = cls._validate_file_contents(profile_dir, profile)
        errors.extend(content_errors)
        
        # Validate file naming conventions
        naming_errors = cls._validate_file_naming(profile_dir)
        errors.extend(naming_errors)
        
        # Validate file sizes
        size_errors = cls._validate_file_sizes(profile_dir)
        errors.extend(size_errors)
        
        return len(errors) == 0, errors

    @classmethod
    def _validate_directory_structure(cls, profile_dir: Path, profile: Profile) -> List[str]:
        """Validate the directory structure and file references."""
        errors = []
        
        # Check that referenced context files exist
        contexts_dir = profile_dir / 'contexts'
        if profile.contexts:
            if not contexts_dir.exists():
                errors.append("Profile references contexts but contexts/ directory does not exist")
            else:
                for context_file in profile.contexts:
                    context_path = contexts_dir / context_file
                    if not context_path.exists():
                        errors.append(f"Referenced context file does not exist: {context_file}")
        
        # Check that referenced hook files exist
        hooks_dir = profile_dir / 'hooks'
        if profile.hooks:
            if not hooks_dir.exists():
                errors.append("Profile references hooks but hooks/ directory does not exist")
            else:
                for hook_file in profile.hooks:
                    hook_path = hooks_dir / hook_file
                    if not hook_path.exists():
                        errors.append(f"Referenced hook file does not exist: {hook_file}")
        
        # Check for unexpected directories
        expected_dirs = {'contexts', 'hooks'}
        for item in profile_dir.iterdir():
            if item.is_dir() and item.name not in expected_dirs:
                errors.append(f"Unexpected directory found: {item.name}")
        
        return errors

    @classmethod
    def _validate_file_contents(cls, profile_dir: Path, profile: Profile) -> List[str]:
        """Validate the contents of context and hook files."""
        errors = []
        
        # Validate context files
        contexts_dir = profile_dir / 'contexts'
        if contexts_dir.exists():
            for context_file in profile.contexts:
                context_path = contexts_dir / context_file
                if context_path.exists():
                    content_errors = cls._validate_context_file(context_path)
                    errors.extend(content_errors)
        
        # Validate hook files
        hooks_dir = profile_dir / 'hooks'
        if hooks_dir.exists():
            for hook_file in profile.hooks:
                hook_path = hooks_dir / hook_file
                if hook_path.exists():
                    hook_errors = cls._validate_hook_file(hook_path)
                    errors.extend(hook_errors)
        
        return errors

    @classmethod
    def _validate_context_file(cls, context_path: Path) -> List[str]:
        """Validate a context markdown file."""
        errors = []
        
        try:
            content = context_path.read_text(encoding='utf-8')
        except Exception as e:
            return [f"Error reading context file {context_path.name}: {e}"]
        
        # Check for YAML frontmatter
        frontmatter_match = cls.MARKDOWN_FRONTMATTER_PATTERN.match(content)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if not isinstance(frontmatter, dict):
                    errors.append(f"Context file {context_path.name}: frontmatter must be a dictionary")
            except yaml.YAMLError as e:
                errors.append(f"Context file {context_path.name}: invalid YAML frontmatter: {e}")
        
        # Check for minimum content length
        content_without_frontmatter = cls.MARKDOWN_FRONTMATTER_PATTERN.sub('', content).strip()
        if len(content_without_frontmatter) < 50:
            errors.append(f"Context file {context_path.name}: content too short (minimum 50 characters)")
        
        # Check for basic markdown structure
        if not content_without_frontmatter.startswith('#'):
            errors.append(f"Context file {context_path.name}: should start with a markdown header")
        
        return errors

    @classmethod
    def _validate_hook_file(cls, hook_path: Path) -> List[str]:
        """Validate a hook file."""
        errors = []
        
        # Only validate YAML files, skip scripts
        if hook_path.suffix.lower() not in ['.yaml', '.yml']:
            # For non-YAML files (like .py, .sh), just check if they exist and are readable
            if not hook_path.exists():
                return [f"Hook file {hook_path.name}: file not found"]
            if not hook_path.is_file():
                return [f"Hook file {hook_path.name}: not a regular file"]
            return []  # Skip further validation for scripts
        
        try:
            with open(hook_path, 'r', encoding='utf-8') as f:
                hook_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return [f"Hook file {hook_path.name}: invalid YAML syntax: {e}"]
        except Exception as e:
            return [f"Hook file {hook_path.name}: error reading file: {e}"]
        
        if not isinstance(hook_data, dict):
            return [f"Hook file {hook_path.name}: must be a YAML dictionary"]
        
        # Check required fields
        for field in cls.YAML_HOOK_REQUIRED_FIELDS:
            if field not in hook_data:
                errors.append(f"Hook file {hook_path.name}: missing required field '{field}'")
        
        # Validate trigger field
        if 'trigger' in hook_data:
            trigger = hook_data['trigger']
            if isinstance(trigger, dict):
                # New format: trigger is a dict with 'event' field
                if 'event' in trigger:
                    valid_events = {'manual', 'on_session_start', 'per_user_message', 'on_file_change', 'on_profile_switch'}
                    if trigger['event'] not in valid_events:
                        errors.append(f"Hook file {hook_path.name}: invalid trigger event '{trigger['event']}'")
                else:
                    errors.append(f"Hook file {hook_path.name}: trigger dict missing required 'event' field")
            elif isinstance(trigger, str):
                # Legacy format: trigger is a string
                valid_triggers = {'on_session_start', 'per_user_message', 'on_file_change', 'on_profile_switch', 'conversation_start', 'per_prompt'}
                if trigger not in valid_triggers:
                    errors.append(f"Hook file {hook_path.name}: invalid trigger '{trigger}'")
            else:
                errors.append(f"Hook file {hook_path.name}: trigger must be a string or dict")
        
        # Validate type field
        if 'type' in hook_data:
            valid_types = {'context', 'script', 'hybrid', 'inline'}
            if hook_data['type'] not in valid_types:
                errors.append(f"Hook file {hook_path.name}: invalid type '{hook_data['type']}'")
        
        return errors

    @classmethod
    def _validate_file_naming(cls, profile_dir: Path) -> List[str]:
        """Validate file naming conventions."""
        errors = []
        
        # Check contexts directory
        contexts_dir = profile_dir / 'contexts'
        if contexts_dir.exists():
            for file_path in contexts_dir.iterdir():
                if file_path.is_file():
                    if not cls.VALID_FILENAME_PATTERN.match(file_path.name):
                        errors.append(f"Invalid filename in contexts/: {file_path.name}")
                    
                    name_without_ext = file_path.stem.lower()
                    if name_without_ext in cls.RESERVED_NAMES:
                        errors.append(f"Reserved filename in contexts/: {file_path.name}")
        
        # Check hooks directory
        hooks_dir = profile_dir / 'hooks'
        if hooks_dir.exists():
            for file_path in hooks_dir.iterdir():
                if file_path.is_file():
                    if not cls.VALID_HOOK_FILENAME_PATTERN.match(file_path.name):
                        errors.append(f"Invalid filename in hooks/: {file_path.name}")
                    
                    name_without_ext = file_path.stem.lower()
                    if name_without_ext in cls.RESERVED_NAMES:
                        errors.append(f"Reserved filename in hooks/: {file_path.name}")
        
        return errors

    @classmethod
    def _validate_file_sizes(cls, profile_dir: Path) -> List[str]:
        """Validate file sizes are within limits."""
        errors = []
        max_size_bytes = cls.MAX_FILE_SIZE_MB * 1024 * 1024
        
        for file_path in profile_dir.rglob('*'):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size > max_size_bytes:
                        errors.append(f"File too large: {file_path.relative_to(profile_dir)} ({size / 1024 / 1024:.1f}MB > {cls.MAX_FILE_SIZE_MB}MB)")
                except OSError as e:
                    errors.append(f"Error checking file size for {file_path.relative_to(profile_dir)}: {e}")
        
        return errors

    @classmethod
    def validate_profile_comprehensive(cls, profile_dir: Path) -> ValidationReport:
        """
        Perform comprehensive validation of a profile with detailed reporting.
        
        Args:
            profile_dir: Path to profile directory
            
        Returns:
            ValidationReport with detailed results
        """
        errors = []
        warnings = []
        info = []
        files_checked = []
        
        # Basic structure validation
        is_valid, basic_errors = cls.validate_profile_structure(profile_dir)
        for error in basic_errors:
            errors.append(ConfigurationError(
                file_path=str(profile_dir),
                error_type="structure",
                message=error,
                severity="error"
            ))
        
        if not profile_dir.exists():
            return ValidationReport(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                info=info,
                files_checked=files_checked,
                summary={"total_errors": len(errors), "total_warnings": len(warnings)}
            )
        
        # Check profile.yaml
        profile_yaml = profile_dir / 'profile.yaml'
        if profile_yaml.exists():
            files_checked.append(str(profile_yaml))
            
            # Load and validate profile
            try:
                profile = Profile.from_yaml(profile_yaml)
                
                # Validate profile completeness
                completeness_warnings = cls._check_profile_completeness(profile)
                warnings.extend(completeness_warnings)
                
                # Validate profile quality
                quality_warnings = cls._check_profile_quality(profile)
                warnings.extend(quality_warnings)
                
                # Check for best practices
                best_practice_info = cls._check_best_practices(profile_dir, profile)
                info.extend(best_practice_info)
                
            except Exception as e:
                errors.append(ConfigurationError(
                    file_path=str(profile_yaml),
                    error_type="parsing",
                    message=f"Error loading profile: {e}",
                    severity="error"
                ))
        
        # Validate all files in the profile
        for file_path in profile_dir.rglob('*'):
            if file_path.is_file() and file_path != profile_yaml:
                files_checked.append(str(file_path))
                file_errors, file_warnings = cls._validate_individual_file(file_path, profile_dir)
                errors.extend(file_errors)
                warnings.extend(file_warnings)
        
        # Calculate summary
        summary = {
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "total_info": len(info),
            "files_checked": len(files_checked),
            "profile_completeness": cls._calculate_completeness_score(profile_dir),
            "validation_timestamp": datetime.now().isoformat()
        }
        
        return ValidationReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=files_checked,
            summary=summary
        )

    @classmethod
    def _check_profile_completeness(cls, profile: Profile) -> List[ConfigurationError]:
        """Check profile completeness and suggest improvements."""
        warnings = []
        
        # Check optional but recommended fields
        if not profile.dependencies:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="completeness",
                message="Consider adding dependencies field if this profile builds on others",
                severity="warning"
            ))
        
        # Check description quality
        if len(profile.description) < 50:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="completeness",
                message="Description is quite short, consider adding more detail",
                severity="warning"
            ))
        
        # Check tag quantity
        if len(profile.tags) < 2:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="completeness",
                message="Consider adding more tags for better discoverability",
                severity="warning"
            ))
        
        # Check if both contexts and hooks are empty
        if not profile.contexts and not profile.hooks:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="completeness",
                message="Profile has no contexts or hooks - consider adding some content",
                severity="warning"
            ))
        
        return warnings

    @classmethod
    def _check_profile_quality(cls, profile: Profile) -> List[ConfigurationError]:
        """Check profile quality and adherence to standards."""
        warnings = []
        
        # Check name quality
        if len(profile.name) > cls.MAX_NAME_LENGTH:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="quality",
                message=f"Profile name is too long ({len(profile.name)} > {cls.MAX_NAME_LENGTH} characters)",
                severity="warning"
            ))
        
        # Check description quality
        if len(profile.description) > cls.MAX_DESCRIPTION_LENGTH:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="quality",
                message=f"Description is too long ({len(profile.description)} > {cls.MAX_DESCRIPTION_LENGTH} characters)",
                severity="warning"
            ))
        
        # Check for duplicate tags
        if len(profile.tags) != len(set(profile.tags)):
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="quality",
                message="Profile has duplicate tags",
                severity="warning"
            ))
        
        # Check context file limits
        if len(profile.contexts) > cls.MAX_CONTEXT_FILES:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="quality",
                message=f"Too many context files ({len(profile.contexts)} > {cls.MAX_CONTEXT_FILES})",
                severity="warning"
            ))
        
        # Check hook file limits
        if len(profile.hooks) > cls.MAX_HOOK_FILES:
            warnings.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="quality",
                message=f"Too many hook files ({len(profile.hooks)} > {cls.MAX_HOOK_FILES})",
                severity="warning"
            ))
        
        return warnings

    @classmethod
    def _check_best_practices(cls, profile_dir: Path, profile: Profile) -> List[ConfigurationError]:
        """Check adherence to best practices."""
        info = []
        
        # Check for README file
        readme_files = list(profile_dir.glob('README*'))
        if not readme_files:
            info.append(ConfigurationError(
                file_path=str(profile_dir),
                error_type="best_practice",
                message="Consider adding a README file to document the profile",
                severity="info"
            ))
        
        # Check for LICENSE file
        license_files = list(profile_dir.glob('LICENSE*'))
        if not license_files and 'license' not in [tag.lower() for tag in profile.tags]:
            info.append(ConfigurationError(
                file_path=str(profile_dir),
                error_type="best_practice",
                message="Consider adding license information",
                severity="info"
            ))
        
        # Check version format best practices
        version_parts = profile.version.split('.')
        if len(version_parts) == 3 and version_parts[0] == '0':
            info.append(ConfigurationError(
                file_path="profile.yaml",
                error_type="best_practice",
                message="Version 0.x.x indicates pre-release - consider 1.0.0 for stable profiles",
                severity="info"
            ))
        
        return info

    @classmethod
    def _validate_individual_file(cls, file_path: Path, profile_dir: Path) -> Tuple[List[ConfigurationError], List[ConfigurationError]]:
        """Validate an individual file within the profile."""
        errors = []
        warnings = []
        relative_path = str(file_path.relative_to(profile_dir))
        
        try:
            # Check file encoding
            try:
                file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                errors.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="encoding",
                    message="File is not valid UTF-8",
                    severity="error"
                ))
                return errors, warnings
            
            # Validate based on file type
            if file_path.suffix.lower() in ['.md', '.markdown']:
                md_errors, md_warnings = cls._validate_markdown_file(file_path, relative_path)
                errors.extend(md_errors)
                warnings.extend(md_warnings)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                yaml_errors, yaml_warnings = cls._validate_yaml_file(file_path, relative_path)
                errors.extend(yaml_errors)
                warnings.extend(yaml_warnings)
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=relative_path,
                error_type="validation",
                message=f"Error validating file: {e}",
                severity="error"
            ))
        
        return errors, warnings

    @classmethod
    def _validate_markdown_file(cls, file_path: Path, relative_path: str) -> Tuple[List[ConfigurationError], List[ConfigurationError]]:
        """Validate a markdown file."""
        errors = []
        warnings = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check for empty file
            if not content.strip():
                errors.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="content",
                    message="Markdown file is empty",
                    severity="error"
                ))
                return errors, warnings
            
            # Check for basic markdown structure
            lines = content.split('\n')
            has_header = any(line.strip().startswith('#') for line in lines[:10])
            if not has_header:
                warnings.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="structure",
                    message="Markdown file should start with a header",
                    severity="warning"
                ))
            
            # Check content length
            content_without_frontmatter = cls.MARKDOWN_FRONTMATTER_PATTERN.sub('', content).strip()
            if len(content_without_frontmatter) < 100:
                warnings.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="content",
                    message="Markdown content is quite short, consider adding more detail",
                    severity="warning"
                ))
            
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=relative_path,
                error_type="validation",
                message=f"Error validating markdown: {e}",
                severity="error"
            ))
        
        return errors, warnings

    @classmethod
    def _validate_yaml_file(cls, file_path: Path, relative_path: str) -> Tuple[List[ConfigurationError], List[ConfigurationError]]:
        """Validate a YAML file."""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if yaml_data is None:
                errors.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="content",
                    message="YAML file is empty or contains only comments",
                    severity="error"
                ))
                return errors, warnings
            
            if not isinstance(yaml_data, dict):
                warnings.append(ConfigurationError(
                    file_path=relative_path,
                    error_type="structure",
                    message="YAML file should contain a dictionary at root level",
                    severity="warning"
                ))
            
        except yaml.YAMLError as e:
            errors.append(ConfigurationError(
                file_path=relative_path,
                error_type="syntax",
                message=f"Invalid YAML syntax: {e}",
                severity="error"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=relative_path,
                error_type="validation",
                message=f"Error validating YAML: {e}",
                severity="error"
            ))
        
        return errors, warnings

    @classmethod
    def _calculate_completeness_score(cls, profile_dir: Path) -> float:
        """Calculate a completeness score for the profile (0-100)."""
        score = 0.0
        max_score = 100.0
        
        # Basic structure (40 points)
        profile_yaml = profile_dir / 'profile.yaml'
        if profile_yaml.exists():
            score += 20
            try:
                profile = Profile.from_yaml(profile_yaml)
                
                # Required fields present (already validated, so +20)
                score += 20
                
                # Optional fields (20 points)
                if profile.dependencies:
                    score += 5
                if len(profile.description) >= 100:
                    score += 5
                if len(profile.tags) >= 3:
                    score += 5
                if len(profile.contexts) > 0 or len(profile.hooks) > 0:
                    score += 5
                
                # Content quality (20 points)
                contexts_dir = profile_dir / 'contexts'
                hooks_dir = profile_dir / 'hooks'
                
                if contexts_dir.exists() and any(contexts_dir.iterdir()):
                    score += 10
                if hooks_dir.exists() and any(hooks_dir.iterdir()):
                    score += 10
                
                # Documentation (20 points)
                readme_files = list(profile_dir.glob('README*'))
                if readme_files:
                    score += 10
                
                license_files = list(profile_dir.glob('LICENSE*'))
                if license_files:
                    score += 10
                
            except Exception:
                pass  # Score remains at basic structure level
        
        return min(score, max_score)

    @classmethod
    def validate_for_contribution(cls, profile_dir: Path) -> ValidationReport:
        """
        Validate a profile for contribution to the library.
        This includes stricter checks for public profiles.
        
        Args:
            profile_dir: Path to profile directory
            
        Returns:
            ValidationReport with contribution-specific validation
        """
        # Start with comprehensive validation
        report = cls.validate_profile_comprehensive(profile_dir)
        
        # Add contribution-specific checks
        contribution_errors = []
        contribution_warnings = []
        
        if profile_dir.exists():
            profile_yaml = profile_dir / 'profile.yaml'
            if profile_yaml.exists():
                try:
                    profile = Profile.from_yaml(profile_yaml)
                    
                    # Stricter requirements for contributions
                    if len(profile.description) < 100:
                        contribution_errors.append(ConfigurationError(
                            file_path="profile.yaml",
                            error_type="contribution",
                            message="Description must be at least 100 characters for contributions",
                            severity="error"
                        ))
                    
                    if len(profile.tags) < 2:
                        contribution_errors.append(ConfigurationError(
                            file_path="profile.yaml",
                            error_type="contribution",
                            message="At least 2 tags required for contributions",
                            severity="error"
                        ))
                    
                    if not profile.contexts and not profile.hooks:
                        contribution_errors.append(ConfigurationError(
                            file_path="profile.yaml",
                            error_type="contribution",
                            message="Profile must include either contexts or hooks for contribution",
                            severity="error"
                        ))
                    
                    # Check for README
                    readme_files = list(profile_dir.glob('README*'))
                    if not readme_files:
                        contribution_warnings.append(ConfigurationError(
                            file_path=str(profile_dir),
                            error_type="contribution",
                            message="README file strongly recommended for contributions",
                            severity="warning"
                        ))
                    
                    # Check author field quality
                    if not profile.author or profile.author.strip() == "":
                        contribution_errors.append(ConfigurationError(
                            file_path="profile.yaml",
                            error_type="contribution",
                            message="Author field is required for contributions",
                            severity="error"
                        ))
                    
                except Exception as e:
                    contribution_errors.append(ConfigurationError(
                        file_path="profile.yaml",
                        error_type="contribution",
                        message=f"Error validating for contribution: {e}",
                        severity="error"
                    ))
        
        # Merge with existing report
        report.errors.extend(contribution_errors)
        report.warnings.extend(contribution_warnings)
        report.is_valid = report.is_valid and len(contribution_errors) == 0
        report.summary["contribution_ready"] = len(contribution_errors) == 0
        report.summary["total_errors"] = len(report.errors)
        report.summary["total_warnings"] = len(report.warnings)
        
        return report

    @classmethod
    def generate_profile_checksum(cls, profile_dir: Path) -> Optional[str]:
        """
        Generate a checksum for the entire profile directory.
        
        Args:
            profile_dir: Path to profile directory
            
        Returns:
            SHA256 checksum string or None if error
        """
        if not profile_dir.exists() or not profile_dir.is_dir():
            return None
        
        try:
            hasher = hashlib.sha256()
            
            # Sort files for consistent hashing
            files = sorted(profile_dir.rglob('*'))
            
            for file_path in files:
                if file_path.is_file():
                    # Add file path to hash
                    relative_path = file_path.relative_to(profile_dir)
                    hasher.update(str(relative_path).encode('utf-8'))
                    
                    # Add file content to hash
                    try:
                        content = file_path.read_bytes()
                        hasher.update(content)
                    except Exception:
                        # If we can't read the file, include its name only
                        hasher.update(b'<unreadable>')
            
            return hasher.hexdigest()
        
        except Exception:
            return None

    @classmethod
    def validate_profile_instance(cls, profile: Profile) -> Tuple[bool, List[str]]:
        """
        Validate a Profile instance.
        
        Args:
            profile: Profile instance to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields are not empty
        if not profile.name or not profile.name.strip():
            errors.append("Profile name cannot be empty")
        
        if not profile.description or not profile.description.strip():
            errors.append("Profile description cannot be empty")
        
        if not profile.version or not profile.version.strip():
            errors.append("Profile version cannot be empty")
        
        if not profile.author or not profile.author.strip():
            errors.append("Profile author cannot be empty")
        
        # Validate category
        if profile.category not in cls.VALID_CATEGORIES:
            errors.append(f"Invalid category '{profile.category}'. Must be one of: {', '.join(cls.VALID_CATEGORIES)}")
        
        # Validate version format
        version_errors = cls._validate_version(profile.version)
        errors.extend(version_errors)
        
        # Validate targets
        if not profile.targets:
            errors.append("Profile must specify at least one target")
        else:
            targets_errors = cls._validate_targets(profile.targets)
            errors.extend(targets_errors)
        
        return len(errors) == 0, errors