"""Markdown processor with YAML frontmatter support."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import yaml
from pydantic import ValidationError

from .models import (
    ContextFile,
    ConfigurationError,
    ValidationReport,
    PathLike,
)


class MarkdownProcessor:
    """
    Markdown processor that handles YAML frontmatter parsing and content separation.
    
    This class provides functionality to parse Markdown files with YAML frontmatter,
    extract metadata, and load context files with proper organization and validation.
    """
    
    # Regex pattern to match YAML frontmatter
    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n(.*)',
        re.DOTALL | re.MULTILINE
    )
    
    def __init__(self, base_path: Optional[PathLike] = None):
        """
        Initialize the Markdown processor.
        
        Args:
            base_path: Base directory path for context files.
                      Defaults to current working directory.
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._cache: Dict[str, Tuple[ContextFile, float]] = {}  # file_path -> (context_file, mtime)
    
    def parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from Markdown content.
        
        Args:
            content: Raw Markdown content that may contain YAML frontmatter
            
        Returns:
            Tuple of (frontmatter_dict, markdown_content)
            If no frontmatter is found, returns (empty_dict, original_content)
            
        Raises:
            yaml.YAMLError: If frontmatter YAML is malformed
        """
        # Check if content starts with frontmatter delimiter
        if not content.strip().startswith('---'):
            return {}, content
        
        # Try to match frontmatter pattern
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            # Check for frontmatter without content after
            frontmatter_only_pattern = re.compile(
                r'^---\s*\n(.*?)\n---\s*$',
                re.DOTALL | re.MULTILINE
            )
            match = frontmatter_only_pattern.match(content)
            if match:
                try:
                    frontmatter_yaml = match.group(1).strip()
                    if not frontmatter_yaml:
                        return {}, ""
                    frontmatter = yaml.safe_load(frontmatter_yaml)
                    return frontmatter or {}, ""
                except yaml.YAMLError as e:
                    raise yaml.YAMLError(f"Invalid YAML frontmatter: {str(e)}") from e
            
            # Check for empty frontmatter (just --- --- with nothing between)
            empty_frontmatter_pattern = re.compile(
                r'^---\s*\n---\s*\n(.*)',
                re.DOTALL | re.MULTILINE
            )
            match = empty_frontmatter_pattern.match(content)
            if match:
                return {}, match.group(1)
            
            # No valid frontmatter found
            return {}, content
        
        frontmatter_yaml = match.group(1).strip()
        markdown_content = match.group(2)
        
        try:
            if not frontmatter_yaml:
                return {}, markdown_content
            frontmatter = yaml.safe_load(frontmatter_yaml)
            return frontmatter or {}, markdown_content
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML frontmatter: {str(e)}") from e
    
    def extract_metadata(self, markdown_content: str) -> Dict[str, Any]:
        """
        Extract metadata from Markdown content including frontmatter and content analysis.
        
        Args:
            markdown_content: Raw Markdown content
            
        Returns:
            Dictionary containing extracted metadata
        """
        frontmatter, content = self.parse_frontmatter(markdown_content)
        
        metadata = {
            'frontmatter': frontmatter,
            'content_length': len(content),
            'has_frontmatter': bool(frontmatter),
            'word_count': len(content.split()) if content else 0,
            'line_count': len(content.splitlines()) if content else 0,
        }
        
        # Extract additional metadata from content
        if content:
            # Count headers
            header_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
            headers = header_pattern.findall(content)
            metadata['header_count'] = len(headers)
            metadata['headers'] = headers[:5]  # First 5 headers for preview
            
            # Check for code blocks
            code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
            code_blocks = code_block_pattern.findall(content)
            metadata['code_block_count'] = len(code_blocks)
            
            # Check for links
            link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
            links = link_pattern.findall(content)
            metadata['link_count'] = len(links)
        
        # Merge frontmatter into top-level metadata
        if frontmatter:
            # Preserve certain frontmatter fields at top level
            for key in ['title', 'description', 'tags', 'categories', 'priority', 'author', 'date']:
                if key in frontmatter:
                    metadata[key] = frontmatter[key]
        
        return metadata
    
    def load_context_file(self, file_path: PathLike) -> ContextFile:
        """
        Load a context file with frontmatter metadata parsing.
        
        Args:
            file_path: Path to the Markdown context file
            
        Returns:
            ContextFile object with parsed content and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If frontmatter YAML is malformed
            ValidationError: If the resulting ContextFile is invalid
        """
        file_path = Path(file_path)
        
        # Make path relative to base_path if it's absolute and within base_path
        if file_path.is_absolute() and self.base_path in file_path.parents:
            relative_path = file_path.relative_to(self.base_path)
        else:
            relative_path = file_path
            # Resolve relative to base_path
            file_path = self.base_path / file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Context file not found: {file_path}")
        
        # Check cache first
        cache_key = str(file_path)
        current_mtime = file_path.stat().st_mtime
        
        if cache_key in self._cache:
            cached_context, cached_mtime = self._cache[cache_key]
            if cached_mtime >= current_mtime:
                return cached_context
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter and content
            frontmatter, markdown_content = self.parse_frontmatter(content)
            
            # Extract metadata
            full_metadata = self.extract_metadata(content)
            
            # Get file modification time
            last_modified = datetime.fromtimestamp(current_mtime).isoformat()
            
            # Create ContextFile object
            context_file = ContextFile(
                file_path=str(relative_path),
                content=markdown_content,
                metadata=full_metadata,
                tags=self._extract_tags(frontmatter),
                categories=self._extract_categories(frontmatter),
                priority=self._extract_priority(frontmatter),
                last_modified=last_modified
            )
            
            # Cache the result
            self._cache[cache_key] = (context_file, current_mtime)
            
            return context_file
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"YAML frontmatter error in {file_path}: {str(e)}"
            ) from e
        except ValidationError as e:
            raise ValidationError(
                f"Context file validation error in {file_path}: {str(e)}"
            ) from e
    
    def load_multiple_context_files(self, file_paths: List[PathLike]) -> List[ContextFile]:
        """
        Load multiple context files efficiently.
        
        Args:
            file_paths: List of paths to Markdown context files
            
        Returns:
            List of ContextFile objects
            
        Note:
            Files that fail to load will be skipped and errors logged.
            This method is designed to be resilient to individual file failures.
        """
        context_files = []
        errors = []
        
        for file_path in file_paths:
            try:
                context_file = self.load_context_file(file_path)
                context_files.append(context_file)
            except Exception as e:
                errors.append(f"Failed to load {file_path}: {str(e)}")
        
        # Log errors if any (in a real implementation, use proper logging)
        if errors:
            print(f"Warning: {len(errors)} context files failed to load:")
            for error in errors:
                print(f"  - {error}")
        
        return context_files
    
    def discover_context_files(self, directory: Optional[PathLike] = None) -> List[str]:
        """
        Discover all Markdown files in a directory that can be used as context files.
        
        Args:
            directory: Directory to search in. Defaults to base_path/contexts
            
        Returns:
            List of relative file paths to discovered Markdown files
        """
        if directory is None:
            directory = self.base_path / 'contexts'
        else:
            directory = Path(directory)
        
        if not directory.exists():
            return []
        
        markdown_files = []
        
        # Find all .md files recursively
        for file_path in directory.rglob('*.md'):
            relative_path = file_path.relative_to(self.base_path)
            markdown_files.append(str(relative_path))
        
        return sorted(markdown_files)
    
    def validate_context_file(self, file_path: PathLike) -> ValidationReport:
        """
        Validate a context file with detailed error reporting.
        
        Args:
            file_path: Path to the context file to validate
            
        Returns:
            Comprehensive validation report
        """
        file_path = Path(file_path)
        errors = []
        warnings = []
        info = []
        
        # Resolve file path relative to base_path if needed
        if not file_path.is_absolute():
            full_file_path = self.base_path / file_path
        else:
            full_file_path = file_path
        
        # Check if file exists
        if not full_file_path.exists():
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="FileNotFound",
                message=f"Context file not found: {file_path}",
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
            # Try to load the context file
            context_file = self.load_context_file(file_path)
            
            # Validate content
            if not context_file.content.strip():
                warnings.append(ConfigurationError(
                    file_path=str(file_path),
                    error_type="EmptyContent",
                    message="Context file has no content after frontmatter",
                    severity="warning"
                ))
            
            # Check frontmatter structure
            if context_file.metadata.get('has_frontmatter'):
                frontmatter = context_file.metadata.get('frontmatter', {})
                
                # Check for recommended frontmatter fields
                recommended_fields = ['title', 'description', 'tags']
                missing_recommended = [field for field in recommended_fields if field not in frontmatter]
                
                if missing_recommended:
                    info.append(ConfigurationError(
                        file_path=str(file_path),
                        error_type="MissingRecommendedFields",
                        message=f"Consider adding recommended frontmatter fields: {', '.join(missing_recommended)}",
                        severity="info"
                    ))
                
                # Validate tags format
                if 'tags' in frontmatter:
                    tags = frontmatter['tags']
                    if not isinstance(tags, list):
                        warnings.append(ConfigurationError(
                            file_path=str(file_path),
                            error_type="InvalidTagsFormat",
                            message="Tags should be a list/array in frontmatter",
                            severity="warning"
                        ))
                
                # Validate priority format
                if 'priority' in frontmatter:
                    priority = frontmatter['priority']
                    if not isinstance(priority, int):
                        warnings.append(ConfigurationError(
                            file_path=str(file_path),
                            error_type="InvalidPriorityFormat",
                            message="Priority should be an integer in frontmatter",
                            severity="warning"
                        ))
            
            info.append(ConfigurationError(
                file_path=str(file_path),
                error_type="ValidationSuccess",
                message="Context file is valid",
                severity="info"
            ))
            
        except yaml.YAMLError as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="YAMLError",
                message=f"YAML frontmatter error: {str(e)}",
                severity="error"
            ))
        except Exception as e:
            errors.append(ConfigurationError(
                file_path=str(file_path),
                error_type="UnexpectedError",
                message=f"Unexpected error: {str(e)}",
                severity="error"
            ))
        
        is_valid = len(errors) == 0
        return ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
            files_checked=[str(file_path)],
            summary={"errors": len(errors), "warnings": len(warnings), "info": len(info)}
        )
    
    def clear_cache(self, file_path: Optional[PathLike] = None) -> None:
        """
        Clear context file cache.
        
        Args:
            file_path: Specific file to clear from cache. If None, clears entire cache.
        """
        if file_path:
            file_path = Path(file_path)
            # Try both relative and absolute paths as cache keys
            if not file_path.is_absolute():
                full_path = self.base_path / file_path
            else:
                full_path = file_path
            
            cache_key = str(full_path)
            self._cache.pop(cache_key, None)
        else:
            self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring and debugging.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cache_size": len(self._cache),
            "cached_files": list(self._cache.keys()),
            "total_cached_content_length": sum(
                len(context_file.content) for context_file, _ in self._cache.values()
            )
        }
    
    def _extract_tags(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Extract tags from frontmatter, ensuring they are strings."""
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            # Handle comma-separated tags
            return [tag.strip() for tag in tags.split(',')]
        elif isinstance(tags, list):
            return [str(tag) for tag in tags]
        else:
            return []
    
    def _extract_categories(self, frontmatter: Dict[str, Any]) -> List[str]:
        """Extract categories from frontmatter, ensuring they are strings."""
        categories = frontmatter.get('categories', [])
        if isinstance(categories, str):
            # Handle comma-separated categories
            return [cat.strip() for cat in categories.split(',')]
        elif isinstance(categories, list):
            return [str(cat) for cat in categories]
        else:
            return []
    
    def _extract_priority(self, frontmatter: Dict[str, Any]) -> int:
        """Extract priority from frontmatter, with default value."""
        priority = frontmatter.get('priority', 0)
        try:
            return int(priority)
        except (ValueError, TypeError):
            return 0