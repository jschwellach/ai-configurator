"""Advanced context management for Amazon Q CLI."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..utils.logging import LoggerMixin
from .config_manager import ConfigurationManager
from .models import GlobalContext, ProfileContext
from .platform import PlatformManager


class ContextManager(LoggerMixin):
    """Manages context files and dynamic context loading."""
    
    def __init__(
        self,
        platform_manager: Optional[PlatformManager] = None,
        config_manager: Optional[ConfigurationManager] = None
    ):
        self.platform = platform_manager or PlatformManager()
        self.config_manager = config_manager or ConfigurationManager(self.platform)
        self.contexts_dir = self.config_manager.config_dir / "contexts"
    
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
    
    def load_context_content(self, paths: List[Path]) -> str:
        """Load and combine content from multiple context files."""
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
    
    def get_profile_context_content(self, profile_name: str) -> str:
        """Get the complete context content for a profile."""
        profile_context = self.config_manager.load_profile_context(profile_name)
        if not profile_context:
            self.logger.warning(f"Profile context not found: {profile_name}")
            return ""
        
        # Resolve context paths
        resolved_paths = self.resolve_context_paths(profile_context.paths)
        
        # Load and combine content
        return self.load_context_content(resolved_paths)
    
    def get_global_context_content(self) -> str:
        """Get the complete global context content."""
        global_context = self.config_manager.load_global_context()
        if not global_context:
            self.logger.warning("Global context not found")
            return ""
        
        # Resolve context paths
        resolved_paths = self.resolve_context_paths(global_context.paths)
        
        # Load and combine content
        return self.load_context_content(resolved_paths)
    
    def get_combined_context_content(self, profile_name: Optional[str] = None) -> str:
        """Get combined global and profile context content."""
        content_parts = []
        
        # Add global context
        global_content = self.get_global_context_content()
        if global_content:
            content_parts.append("=== GLOBAL CONTEXT ===")
            content_parts.append(global_content)
        
        # Add profile context
        if profile_name:
            profile_content = self.get_profile_context_content(profile_name)
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
            "global": [],
            "profiles": {},
            "shared": [],
            "orphaned": []
        }
        
        # Get global context files
        global_context = self.config_manager.load_global_context()
        if global_context:
            contexts["global"] = global_context.paths
        
        # Get profile context files
        profiles = self.config_manager.list_profiles()
        for profile in profiles:
            profile_context = self.config_manager.load_profile_context(profile)
            if profile_context:
                contexts["profiles"][profile] = profile_context.paths
        
        # Find shared context files (in contexts directory)
        if self.contexts_dir.exists():
            for context_file in self.contexts_dir.rglob("*.md"):
                relative_path = f"contexts/{context_file.relative_to(self.contexts_dir)}"
                contexts["shared"].append(relative_path)
        
        # Find orphaned context files (not referenced anywhere)
        all_referenced = set(contexts["global"])
        for profile_paths in contexts["profiles"].values():
            all_referenced.update(profile_paths)
        
        if self.contexts_dir.exists():
            for context_file in self.contexts_dir.rglob("*.md"):
                relative_path = f"contexts/{context_file.relative_to(self.contexts_dir)}"
                if relative_path not in all_referenced:
                    contexts["orphaned"].append(relative_path)
        
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
