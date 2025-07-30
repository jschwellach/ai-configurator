"""Advanced context management for Amazon Q CLI."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

from ..utils.logging import LoggerMixin
# Removed circular import - ConfigurationManager will be passed as parameter
from .models import GlobalContext, ProfileContext, ContextFile
from .platform import PlatformManager
from .markdown_processor import MarkdownProcessor
# Removed directory_manager import to avoid circular dependencies


class ContextManager(LoggerMixin):
    """Manages context files and dynamic context loading with Markdown support."""
    
    def __init__(
        self,
        config_dir: Path,
        markdown_processor: MarkdownProcessor,
        platform_manager: Optional[PlatformManager] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_dir = config_dir
        self.contexts_dir = self.config_dir / "contexts"
        self.contexts_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_processor = markdown_processor
        
        # Cache for loaded context files to prevent duplication
        self._context_cache: Dict[str, ContextFile] = {}
        self._organized_contexts: Dict[str, List[ContextFile]] = {}
    
    def resolve_context_paths(self, paths: List[str], base_dir: Optional[Path] = None) -> List[Path]:
        """Resolve context paths with glob patterns and relative paths."""
        if base_dir is None:
            base_dir = self.config_manager.config_dir
        
        resolved_paths = []
        
        for path_str in paths:
            path = Path(path_str)
            
            # Handle absolute paths
            if path.is_absolute():
                if path.exists():
                    if path.is_file():
                        resolved_paths.append(path)
                    elif path.is_dir():
                        # Add all markdown files in directory
                        resolved_paths.extend(path.rglob("*.md"))
                else:
                    self.logger.warning(f"Absolute path not found: {path}")
                continue
            
            # Handle relative paths with glob patterns
            if "*" in path_str or "?" in path_str:
                # Use glob pattern matching
                try:
                    matches = list(base_dir.glob(path_str))
                    if matches:
                        # Filter for files only
                        file_matches = [p for p in matches if p.is_file()]
                        resolved_paths.extend(file_matches)
                    else:
                        self.logger.warning(f"No matches found for pattern: {path_str}")
                except Exception as e:
                    self.logger.error(f"Error processing glob pattern '{path_str}': {e}")
            else:
                # Regular relative path
                full_path = base_dir / path
                if full_path.exists():
                    if full_path.is_file():
                        resolved_paths.append(full_path)
                    elif full_path.is_dir():
                        # Add all markdown files in directory
                        resolved_paths.extend(full_path.rglob("*.md"))
                else:
                    self.logger.warning(f"Context path not found: {full_path}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for path in resolved_paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)
        
        return unique_paths
    
    def validate_context_name(self, context_name: str) -> tuple[bool, str]:
        """
        Validate a context name against naming conventions.
        
        Args:
            context_name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Simple naming validation
        if not context_name or not context_name.replace('-', '').replace('_', '').replace('.', '').isalnum():
            return False, "Context name must contain only alphanumeric characters, hyphens, underscores, and dots"
        return True, ""
    
    def load_context_files(self, paths: List[str]) -> List[ContextFile]:
        """Load context files with Markdown frontmatter support and caching."""
        context_files = []
        
        for path_str in paths:
            # Check cache first
            if path_str in self._context_cache:
                context_files.append(self._context_cache[path_str])
                continue
            
            try:
                # Use MarkdownProcessor to load with frontmatter support
                context_file = self.markdown_processor.load_context_file(path_str)
                
                # Cache the loaded context file
                self._context_cache[path_str] = context_file
                context_files.append(context_file)
                
                self.logger.debug(f"Loaded context from: {path_str}")
            except Exception as e:
                self.logger.error(f"Failed to load context from {path_str}: {e}")
        
        return context_files
    
    def organize_contexts_by_tags(self, context_files: List[ContextFile]) -> Dict[str, List[ContextFile]]:
        """Organize context files by their tags."""
        organized = defaultdict(list)
        
        for context_file in context_files:
            if context_file.tags:
                for tag in context_file.tags:
                    organized[tag].append(context_file)
            else:
                # Files without tags go to 'untagged'
                organized['untagged'].append(context_file)
        
        return dict(organized)
    
    def organize_contexts_by_categories(self, context_files: List[ContextFile]) -> Dict[str, List[ContextFile]]:
        """Organize context files by their categories."""
        organized = defaultdict(list)
        
        for context_file in context_files:
            if context_file.categories:
                for category in context_file.categories:
                    organized[category].append(context_file)
            else:
                # Files without categories go to 'general'
                organized['general'].append(context_file)
        
        return dict(organized)
    
    def sort_contexts_by_priority(self, context_files: List[ContextFile]) -> List[ContextFile]:
        """Sort context files by priority (higher priority first)."""
        return sorted(context_files, key=lambda cf: cf.priority, reverse=True)
    
    def load_context_content(self, paths: List[Path]) -> str:
        """Load and combine content from multiple context files (legacy method)."""
        content_parts = []
        
        for path in paths:
            try:
                if path.exists() and path.is_file():
                    content = path.read_text(encoding='utf-8')
                    
                    # Add a header with the file name
                    header = f"\n--- {path.name} ---\n"
                    content_parts.append(header + content)
                    
                    self.logger.debug(f"Loaded context from: {path}")
                else:
                    self.logger.warning(f"Context file not accessible: {path}")
            except Exception as e:
                self.logger.error(f"Failed to load context from {path}: {e}")
        
        return "\n".join(content_parts)
    
    def load_organized_context_content(self, paths: List[str], organize_by: str = "priority") -> str:
        """Load and organize context content with frontmatter support."""
        context_files = self.load_context_files(paths)
        
        if organize_by == "priority":
            context_files = self.sort_contexts_by_priority(context_files)
        elif organize_by == "tags":
            organized = self.organize_contexts_by_tags(context_files)
            return self._format_organized_content(organized, "Tags")
        elif organize_by == "categories":
            organized = self.organize_contexts_by_categories(context_files)
            return self._format_organized_content(organized, "Categories")
        
        return self._format_context_content(context_files)
    
    def _format_context_content(self, context_files: List[ContextFile]) -> str:
        """Format context files into a single content string."""
        content_parts = []
        
        for context_file in context_files:
            # Create header with metadata
            header_parts = [f"--- {Path(context_file.file_path).name} ---"]
            
            if context_file.tags:
                header_parts.append(f"Tags: {', '.join(context_file.tags)}")
            if context_file.categories:
                header_parts.append(f"Categories: {', '.join(context_file.categories)}")
            if context_file.priority != 0:
                header_parts.append(f"Priority: {context_file.priority}")
            
            header = "\n".join(header_parts) + "\n"
            content_parts.append(header + context_file.content)
        
        return "\n\n".join(content_parts)
    
    def _format_organized_content(self, organized: Dict[str, List[ContextFile]], organization_type: str) -> str:
        """Format organized context content with section headers."""
        content_parts = []
        
        for key, context_files in organized.items():
            if context_files:
                content_parts.append(f"=== {organization_type.upper()}: {key.upper()} ===")
                
                # Sort by priority within each group
                sorted_files = self.sort_contexts_by_priority(context_files)
                formatted_content = self._format_context_content(sorted_files)
                content_parts.append(formatted_content)
        
        return "\n\n".join(content_parts)
    
    def get_profile_context_content(self, profile_name: str, organize_by: str = "priority") -> str:
        """Get the complete context content for a profile with Markdown support."""
        profile_context = self.config_manager.load_profile_context(profile_name)
        if not profile_context:
            self.logger.warning(f"Profile context not found: {profile_name}")
            return ""
        
        # Use new organized loading method
        return self.load_organized_context_content(profile_context.paths, organize_by)
    
    def get_global_context_content(self, organize_by: str = "priority") -> str:
        """Get the complete global context content with Markdown support."""
        global_context = self.config_manager.load_global_context()
        if not global_context:
            self.logger.warning("Global context not found")
            return ""
        
        # Use new organized loading method
        return self.load_organized_context_content(global_context.paths, organize_by)
    
    def get_combined_context_content(self, profile_name: Optional[str] = None, organize_by: str = "priority") -> str:
        """Get combined global and profile context content with Markdown support."""
        content_parts = []
        
        # Add global context
        global_content = self.get_global_context_content(organize_by)
        if global_content:
            content_parts.append("=== GLOBAL CONTEXT ===")
            content_parts.append(global_content)
        
        # Add profile context
        if profile_name:
            profile_content = self.get_profile_context_content(profile_name, organize_by)
            if profile_content:
                content_parts.append(f"=== PROFILE CONTEXT: {profile_name.upper()} ===")
                content_parts.append(profile_content)
        
        return "\n\n".join(content_parts)
    
    def validate_context_paths(self, paths: List[str]) -> Dict[str, any]:
        """Validate context paths and return detailed information."""
        validation_result = {
            "valid_paths": [],
            "invalid_paths": [],
            "glob_patterns": [],
            "resolved_files": [],
            "total_files": 0,
            "total_size": 0
        }
        
        for path_str in paths:
            path = Path(path_str)
            
            # Check if it's a glob pattern
            if "*" in path_str or "?" in path_str:
                validation_result["glob_patterns"].append(path_str)
                
                # Try to resolve the pattern
                try:
                    base_dir = self.config_manager.config_dir
                    matches = list(base_dir.glob(path_str))
                    file_matches = [p for p in matches if p.is_file()]
                    
                    if file_matches:
                        validation_result["valid_paths"].append(path_str)
                        validation_result["resolved_files"].extend([str(p) for p in file_matches])
                        validation_result["total_files"] += len(file_matches)
                        
                        # Calculate total size
                        for file_path in file_matches:
                            try:
                                validation_result["total_size"] += file_path.stat().st_size
                            except Exception:
                                pass
                    else:
                        validation_result["invalid_paths"].append(path_str)
                except Exception as e:
                    validation_result["invalid_paths"].append(f"{path_str} (error: {e})")
            else:
                # Regular path
                if path.is_absolute():
                    full_path = path
                else:
                    full_path = self.config_manager.config_dir / path
                
                if full_path.exists():
                    validation_result["valid_paths"].append(path_str)
                    
                    if full_path.is_file():
                        validation_result["resolved_files"].append(str(full_path))
                        validation_result["total_files"] += 1
                        try:
                            validation_result["total_size"] += full_path.stat().st_size
                        except Exception:
                            pass
                    elif full_path.is_dir():
                        # Count markdown files in directory
                        md_files = list(full_path.rglob("*.md"))
                        validation_result["resolved_files"].extend([str(p) for p in md_files])
                        validation_result["total_files"] += len(md_files)
                        
                        for md_file in md_files:
                            try:
                                validation_result["total_size"] += md_file.stat().st_size
                            except Exception:
                                pass
                else:
                    validation_result["invalid_paths"].append(path_str)
        
        return validation_result
    
    def list_available_contexts(self) -> Dict[str, List[str]]:
        """List all available context files organized by category."""
        contexts = {
            "markdown": [],
            "shared": [],
            "total": []
        }
        
        # Find all context files in contexts directory
        if self.contexts_dir.exists():
            for context_file in self.contexts_dir.rglob("*.md"):
                relative_path = f"contexts/{context_file.relative_to(self.contexts_dir)}"
                contexts["markdown"].append(relative_path)
                contexts["total"].append(relative_path)
                
                # Check if it's in a shared subdirectory
                if "shared" in context_file.parts:
                    contexts["shared"].append(relative_path)
        
        return contexts
    
    def search_context_content(self, query: str, case_sensitive: bool = False) -> List[Dict[str, any]]:
        """Search for content across all context files."""
        results = []
        
        # Prepare search pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query, flags)
        except re.error as e:
            self.logger.error(f"Invalid search pattern '{query}': {e}")
            return results
        
        # Search in all context files
        if self.contexts_dir.exists():
            for context_file in self.contexts_dir.rglob("*.md"):
                try:
                    content = context_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    matches = []
                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            matches.append({
                                "line_number": line_num,
                                "line_content": line.strip(),
                                "context": self._get_line_context(lines, line_num - 1, 2)
                            })
                    
                    if matches:
                        results.append({
                            "file": str(context_file.relative_to(self.contexts_dir)),
                            "full_path": str(context_file),
                            "matches": matches,
                            "match_count": len(matches)
                        })
                
                except Exception as e:
                    self.logger.warning(f"Failed to search in {context_file}: {e}")
        
        return results
    
    def _get_line_context(self, lines: List[str], line_index: int, context_lines: int = 2) -> List[str]:
        """Get surrounding lines for context."""
        start = max(0, line_index - context_lines)
        end = min(len(lines), line_index + context_lines + 1)
        return lines[start:end]
    
    def optimize_context_loading(self) -> Dict[str, any]:
        """Analyze and optimize context loading performance."""
        optimization_report = {
            "total_files": 0,
            "total_size": 0,
            "large_files": [],
            "duplicate_content": [],
            "recommendations": []
        }
        
        if not self.contexts_dir.exists():
            return optimization_report
        
        file_contents = {}
        
        for context_file in self.contexts_dir.rglob("*.md"):
            try:
                size = context_file.stat().st_size
                optimization_report["total_files"] += 1
                optimization_report["total_size"] += size
                
                # Check for large files (>100KB)
                if size > 100 * 1024:
                    optimization_report["large_files"].append({
                        "file": str(context_file.relative_to(self.contexts_dir)),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2)
                    })
                
                # Check for duplicate content
                content = context_file.read_text(encoding='utf-8')
                content_hash = hash(content)
                
                if content_hash in file_contents:
                    optimization_report["duplicate_content"].append({
                        "files": [file_contents[content_hash], str(context_file.relative_to(self.contexts_dir))],
                        "size": size
                    })
                else:
                    file_contents[content_hash] = str(context_file.relative_to(self.contexts_dir))
            
            except Exception as e:
                self.logger.warning(f"Failed to analyze {context_file}: {e}")
        
        # Generate recommendations
        if optimization_report["large_files"]:
            optimization_report["recommendations"].append(
                f"Consider splitting {len(optimization_report['large_files'])} large files for better performance"
            )
        
        if optimization_report["duplicate_content"]:
            optimization_report["recommendations"].append(
                f"Found {len(optimization_report['duplicate_content'])} duplicate files that could be consolidated"
            )
        
        if optimization_report["total_size"] > 10 * 1024 * 1024:  # 10MB
            optimization_report["recommendations"].append(
                "Total context size is large - consider using more specific context paths"
            )
        
        return optimization_report
    
    def get_context_by_tags(self, tags: List[str], profile_name: Optional[str] = None) -> List[ContextFile]:
        """Get context files that match any of the specified tags."""
        all_paths = []
        
        # Collect paths from global and profile contexts
        global_context = self.config_manager.load_global_context()
        if global_context:
            all_paths.extend(global_context.paths)
        
        if profile_name:
            profile_context = self.config_manager.load_profile_context(profile_name)
            if profile_context:
                all_paths.extend(profile_context.paths)
        
        # Load context files and filter by tags
        context_files = self.load_context_files(all_paths)
        matching_files = []
        
        for context_file in context_files:
            if any(tag in context_file.tags for tag in tags):
                matching_files.append(context_file)
        
        return self.sort_contexts_by_priority(matching_files)
    
    def get_context_by_categories(self, categories: List[str], profile_name: Optional[str] = None) -> List[ContextFile]:
        """Get context files that match any of the specified categories."""
        all_paths = []
        
        # Collect paths from global and profile contexts
        global_context = self.config_manager.load_global_context()
        if global_context:
            all_paths.extend(global_context.paths)
        
        if profile_name:
            profile_context = self.config_manager.load_profile_context(profile_name)
            if profile_context:
                all_paths.extend(profile_context.paths)
        
        # Load context files and filter by categories
        context_files = self.load_context_files(all_paths)
        matching_files = []
        
        for context_file in context_files:
            if any(category in context_file.categories for category in categories):
                matching_files.append(context_file)
        
        return self.sort_contexts_by_priority(matching_files)
    
    def get_high_priority_contexts(self, min_priority: int = 1, profile_name: Optional[str] = None) -> List[ContextFile]:
        """Get context files with priority above the specified threshold."""
        all_paths = []
        
        # Collect paths from global and profile contexts
        global_context = self.config_manager.load_global_context()
        if global_context:
            all_paths.extend(global_context.paths)
        
        if profile_name:
            profile_context = self.config_manager.load_profile_context(profile_name)
            if profile_context:
                all_paths.extend(profile_context.paths)
        
        # Load context files and filter by priority
        context_files = self.load_context_files(all_paths)
        high_priority_files = [cf for cf in context_files if cf.priority >= min_priority]
        
        return self.sort_contexts_by_priority(high_priority_files)
    
    def clear_context_cache(self, file_path: Optional[str] = None) -> None:
        """Clear the context file cache."""
        if file_path:
            self._context_cache.pop(file_path, None)
            # Also clear from markdown processor cache
            self.markdown_processor.clear_cache(file_path)
        else:
            self._context_cache.clear()
            self.markdown_processor.clear_cache()
        
        # Clear organized contexts cache
        self._organized_contexts.clear()
    
    def get_context_metadata_summary(self, profile_name: Optional[str] = None) -> Dict[str, any]:
        """Get a summary of context metadata for analysis."""
        all_paths = []
        
        # Collect paths from global and profile contexts
        global_context = self.config_manager.load_global_context()
        if global_context:
            all_paths.extend(global_context.paths)
        
        if profile_name:
            profile_context = self.config_manager.load_profile_context(profile_name)
            if profile_context:
                all_paths.extend(profile_context.paths)
        
        # Load context files
        context_files = self.load_context_files(all_paths)
        
        # Analyze metadata
        all_tags = set()
        all_categories = set()
        priority_distribution = defaultdict(int)
        files_with_frontmatter = 0
        
        for context_file in context_files:
            all_tags.update(context_file.tags)
            all_categories.update(context_file.categories)
            priority_distribution[context_file.priority] += 1
            
            if context_file.metadata.get('has_frontmatter', False):
                files_with_frontmatter += 1
        
        return {
            'total_files': len(context_files),
            'files_with_frontmatter': files_with_frontmatter,
            'unique_tags': sorted(list(all_tags)),
            'unique_categories': sorted(list(all_categories)),
            'priority_distribution': dict(priority_distribution),
            'cache_size': len(self._context_cache),
            'markdown_processor_cache_stats': self.markdown_processor.get_cache_stats()
        }
    
    def validate_context_references(self, profile_name: Optional[str] = None) -> Dict[str, any]:
        """Validate that all context file references are valid and accessible."""
        validation_result = {
            'valid_files': [],
            'invalid_files': [],
            'files_with_errors': [],
            'total_files': 0,
            'validation_errors': []
        }
        
        all_paths = []
        
        # Collect paths from global and profile contexts
        global_context = self.config_manager.load_global_context()
        if global_context:
            all_paths.extend(global_context.paths)
        
        if profile_name:
            profile_context = self.config_manager.load_profile_context(profile_name)
            if profile_context:
                all_paths.extend(profile_context.paths)
        
        validation_result['total_files'] = len(all_paths)
        
        for path_str in all_paths:
            try:
                # Try to validate using markdown processor
                validation_report = self.markdown_processor.validate_context_file(path_str)
                
                if validation_report.is_valid:
                    validation_result['valid_files'].append(path_str)
                else:
                    validation_result['files_with_errors'].append(path_str)
                    validation_result['validation_errors'].extend(validation_report.errors)
                
            except FileNotFoundError:
                validation_result['invalid_files'].append(path_str)
            except Exception as e:
                validation_result['files_with_errors'].append(path_str)
                validation_result['validation_errors'].append(f"Error validating {path_str}: {str(e)}")
        
        return validation_result
