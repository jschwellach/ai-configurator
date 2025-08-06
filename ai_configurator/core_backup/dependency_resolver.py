"""
Dependency resolver for configuration management.

This module provides advanced dependency resolution capabilities including
conflict detection, version constraints, and optional dependencies.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.logging import LoggerMixin
from .catalog_schema import ConfigItem, LibraryCatalog


class DependencyType(Enum):
    """Types of dependencies."""
    REQUIRED = "required"
    OPTIONAL = "optional"


class ConflictType(Enum):
    """Types of dependency conflicts."""
    VERSION_MISMATCH = "version_mismatch"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    MISSING_DEPENDENCY = "missing_dependency"
    INCOMPATIBLE_PLATFORM = "incompatible_platform"


@dataclass
class DependencySpec:
    """Specification for a dependency with version constraints."""
    config_id: str
    version_constraint: Optional[str] = None
    dependency_type: DependencyType = DependencyType.REQUIRED
    
    @classmethod
    def parse(cls, dep_string: str) -> 'DependencySpec':
        """
        Parse a dependency string into a DependencySpec.
        
        Formats supported:
        - "config-id" (required, any version)
        - "config-id>=1.0.0" (required, version constraint)
        - "config-id@optional" (optional, any version)
        - "config-id>=1.0.0@optional" (optional, version constraint)
        """
        # Check for optional marker
        if "@optional" in dep_string:
            dep_string = dep_string.replace("@optional", "")
            dep_type = DependencyType.OPTIONAL
        else:
            dep_type = DependencyType.REQUIRED
        
        # Parse version constraint
        version_pattern = r'^([^>=<]+)([>=<]+.*)$'
        match = re.match(version_pattern, dep_string.strip())
        
        if match:
            config_id = match.group(1).strip()
            version_constraint = match.group(2).strip()
        else:
            config_id = dep_string.strip()
            version_constraint = None
        
        return cls(
            config_id=config_id,
            version_constraint=version_constraint,
            dependency_type=dep_type
        )


@dataclass
class ConflictInfo:
    """Information about a dependency conflict."""
    conflict_type: ConflictType
    config_id: str
    conflicting_config_id: Optional[str] = None
    message: str = ""
    suggested_resolution: Optional[str] = None


@dataclass
class ResolutionResult:
    """Result of dependency resolution."""
    resolved_configs: List[str]
    conflicts: List[ConflictInfo]
    optional_configs: List[str]
    success: bool
    
    @property
    def has_conflicts(self) -> bool:
        """Check if there are any conflicts."""
        return len(self.conflicts) > 0
    
    @property
    def total_configs(self) -> int:
        """Total number of configurations to install."""
        return len(self.resolved_configs) + len(self.optional_configs)


class DependencyResolver(LoggerMixin):
    """
    Advanced dependency resolver with conflict detection and version constraints.
    """
    
    def __init__(self, catalog: LibraryCatalog):
        """
        Initialize the dependency resolver.
        
        Args:
            catalog: Library catalog containing all configurations
        """
        self.catalog = catalog
        self._config_map = self._build_config_map()
    
    def _build_config_map(self) -> Dict[str, ConfigItem]:
        """Build a map of config_id to ConfigItem for fast lookup."""
        config_map = {}
        
        for category_name, category_data in self.catalog.categories.dict().items():
            if not isinstance(category_data, dict):
                continue
            for subcategory_name, configs in category_data.items():
                if not isinstance(configs, list):
                    continue
                for config_data in configs:
                    if isinstance(config_data, dict):
                        config = ConfigItem(**config_data)
                    else:
                        config = config_data
                    config_map[config.id] = config
        
        return config_map
    
    def resolve_dependencies(
        self, 
        config_ids: List[str],
        platform: Optional[str] = None,
        kiro_version: Optional[str] = None
    ) -> ResolutionResult:
        """
        Resolve dependencies for a list of configuration IDs.
        
        Args:
            config_ids: List of configuration IDs to resolve
            platform: Target platform for compatibility checking
            kiro_version: Target Kiro version for compatibility checking
            
        Returns:
            ResolutionResult with resolved configurations and conflicts
        """
        self.logger.info(f"Resolving dependencies for {len(config_ids)} configurations")
        
        resolved_configs = set()
        optional_configs = set()
        conflicts = []
        visited = set()
        
        # Process each requested configuration
        for config_id in config_ids:
            result = self._resolve_single_config(
                config_id, 
                resolved_configs, 
                optional_configs,
                visited, 
                platform, 
                kiro_version
            )
            conflicts.extend(result)
        
        # Check for circular dependencies
        circular_conflicts = self._detect_circular_dependencies(list(resolved_configs))
        conflicts.extend(circular_conflicts)
        
        # Remove duplicates and sort
        resolved_list = sorted(list(resolved_configs))
        optional_list = sorted(list(optional_configs))
        
        success = len(conflicts) == 0 or all(
            c.conflict_type != ConflictType.MISSING_DEPENDENCY for c in conflicts
        )
        
        result = ResolutionResult(
            resolved_configs=resolved_list,
            conflicts=conflicts,
            optional_configs=optional_list,
            success=success
        )
        
        self.logger.info(
            f"Resolution complete: {len(resolved_list)} required, "
            f"{len(optional_list)} optional, {len(conflicts)} conflicts"
        )
        
        return result
    
    def _resolve_single_config(
        self,
        config_id: str,
        resolved_configs: Set[str],
        optional_configs: Set[str],
        visited: Set[str],
        platform: Optional[str],
        kiro_version: Optional[str]
    ) -> List[ConflictInfo]:
        """Resolve dependencies for a single configuration."""
        conflicts = []
        
        # Avoid infinite recursion
        if config_id in visited:
            return conflicts
        visited.add(config_id)
        
        # Check if configuration exists
        config = self._config_map.get(config_id)
        if not config:
            conflicts.append(ConflictInfo(
                conflict_type=ConflictType.MISSING_DEPENDENCY,
                config_id=config_id,
                message=f"Configuration '{config_id}' not found in catalog",
                suggested_resolution="Check configuration ID spelling or update catalog"
            ))
            return conflicts
        
        # Check platform compatibility
        if platform and config.compatibility:
            if platform not in config.compatibility.platforms:
                conflicts.append(ConflictInfo(
                    conflict_type=ConflictType.INCOMPATIBLE_PLATFORM,
                    config_id=config_id,
                    message=f"Configuration '{config_id}' not compatible with platform '{platform}'",
                    suggested_resolution=f"Use a different configuration or switch to supported platform: {', '.join(config.compatibility.platforms)}"
                ))
        
        # Check Kiro version compatibility
        if kiro_version and config.compatibility:
            if not self._is_version_compatible(kiro_version, config.compatibility.kiro_version):
                conflicts.append(ConflictInfo(
                    conflict_type=ConflictType.VERSION_MISMATCH,
                    config_id=config_id,
                    message=f"Configuration '{config_id}' requires Kiro {config.compatibility.kiro_version}, but {kiro_version} is available",
                    suggested_resolution=f"Upgrade Kiro to {config.compatibility.kiro_version} or use a compatible configuration version"
                ))
        
        # Add to resolved configs
        resolved_configs.add(config_id)
        
        # Process dependencies
        for dep_string in config.dependencies:
            dep_spec = DependencySpec.parse(dep_string)
            
            # Check version constraint
            dep_config = self._config_map.get(dep_spec.config_id)
            if dep_config and dep_spec.version_constraint:
                if not self._is_version_compatible(dep_config.version, dep_spec.version_constraint):
                    conflicts.append(ConflictInfo(
                        conflict_type=ConflictType.VERSION_MISMATCH,
                        config_id=config_id,
                        conflicting_config_id=dep_spec.config_id,
                        message=f"Dependency '{dep_spec.config_id}' version {dep_config.version} doesn't satisfy constraint {dep_spec.version_constraint}",
                        suggested_resolution="Update dependency to a compatible version"
                    ))
                    continue
            
            # Recursively resolve dependency
            dep_conflicts = self._resolve_single_config(
                dep_spec.config_id,
                resolved_configs if dep_spec.dependency_type == DependencyType.REQUIRED else optional_configs,
                optional_configs,
                visited,
                platform,
                kiro_version
            )
            conflicts.extend(dep_conflicts)
        
        return conflicts
    
    def _detect_circular_dependencies(self, config_ids: List[str]) -> List[ConflictInfo]:
        """Detect circular dependencies in the resolved configuration set."""
        conflicts = []
        
        def has_circular_dep(config_id: str, path: List[str]) -> bool:
            if config_id in path:
                # Found circular dependency
                cycle_start = path.index(config_id)
                cycle = path[cycle_start:] + [config_id]
                conflicts.append(ConflictInfo(
                    conflict_type=ConflictType.CIRCULAR_DEPENDENCY,
                    config_id=config_id,
                    message=f"Circular dependency detected: {' -> '.join(cycle)}",
                    suggested_resolution="Remove one of the dependencies to break the cycle"
                ))
                return True
            
            config = self._config_map.get(config_id)
            if not config:
                return False
            
            path.append(config_id)
            
            for dep_string in config.dependencies:
                dep_spec = DependencySpec.parse(dep_string)
                if dep_spec.dependency_type == DependencyType.REQUIRED:
                    if has_circular_dep(dep_spec.config_id, path.copy()):
                        return True
            
            return False
        
        for config_id in config_ids:
            has_circular_dep(config_id, [])
        
        return conflicts
    
    def _is_version_compatible(self, available_version: str, constraint: str) -> bool:
        """
        Check if an available version satisfies a version constraint.
        
        Supports: >=, >, <=, <, ==, !=
        """
        if not constraint:
            return True
        
        # Parse constraint
        constraint_pattern = r'^([>=<!=]+)(.+)$'
        match = re.match(constraint_pattern, constraint.strip())
        if not match:
            # No operator, assume exact match
            return available_version == constraint.strip()
        
        operator = match.group(1)
        required_version = match.group(2).strip()
        
        # Simple version comparison (assumes semantic versioning)
        try:
            available_parts = [int(x) for x in available_version.split('.')]
            required_parts = [int(x) for x in required_version.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(available_parts), len(required_parts))
            available_parts.extend([0] * (max_len - len(available_parts)))
            required_parts.extend([0] * (max_len - len(required_parts)))
            
            if operator == '>=':
                return available_parts >= required_parts
            elif operator == '>':
                return available_parts > required_parts
            elif operator == '<=':
                return available_parts <= required_parts
            elif operator == '<':
                return available_parts < required_parts
            elif operator == '==':
                return available_parts == required_parts
            elif operator == '!=':
                return available_parts != required_parts
            else:
                self.logger.warning(f"Unknown version operator: {operator}")
                return True
                
        except ValueError:
            # Fallback to string comparison
            self.logger.warning(f"Invalid version format, using string comparison: {available_version} vs {required_version}")
            if operator == '>=':
                return available_version >= required_version
            elif operator == '>':
                return available_version > required_version
            elif operator == '<=':
                return available_version <= required_version
            elif operator == '<':
                return available_version < required_version
            elif operator == '==':
                return available_version == required_version
            elif operator == '!=':
                return available_version != required_version
            else:
                return True
    
    def get_dependency_tree(self, config_id: str) -> Dict[str, Any]:
        """
        Get the complete dependency tree for a configuration.
        
        Args:
            config_id: Configuration ID to analyze
            
        Returns:
            Dictionary representing the dependency tree
        """
        def build_tree(cid: str, visited: Set[str]) -> Dict[str, Any]:
            if cid in visited:
                return {"id": cid, "circular": True, "dependencies": []}
            
            config = self._config_map.get(cid)
            if not config:
                return {"id": cid, "missing": True, "dependencies": []}
            
            visited.add(cid)
            
            tree = {
                "id": cid,
                "name": config.name,
                "version": config.version,
                "dependencies": []
            }
            
            for dep_string in config.dependencies:
                dep_spec = DependencySpec.parse(dep_string)
                dep_tree = build_tree(dep_spec.config_id, visited.copy())
                dep_tree["type"] = dep_spec.dependency_type.value
                dep_tree["constraint"] = dep_spec.version_constraint
                tree["dependencies"].append(dep_tree)
            
            return tree
        
        return build_tree(config_id, set())
    
    def suggest_resolution_order(self, resolved_configs: List[str]) -> List[str]:
        """
        Suggest an optimal installation order based on dependencies.
        
        Args:
            resolved_configs: List of configuration IDs to order
            
        Returns:
            List of configuration IDs in suggested installation order
        """
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for config_id in resolved_configs:
            graph[config_id] = []
            in_degree[config_id] = 0
        
        for config_id in resolved_configs:
            config = self._config_map.get(config_id)
            if not config:
                continue
            
            for dep_string in config.dependencies:
                dep_spec = DependencySpec.parse(dep_string)
                if dep_spec.config_id in resolved_configs:
                    graph[dep_spec.config_id].append(config_id)
                    in_degree[config_id] += 1
        
        # Topological sort
        queue = [config_id for config_id in resolved_configs if in_degree[config_id] == 0]
        result = []
        
        while queue:
            config_id = queue.pop(0)
            result.append(config_id)
            
            for dependent in graph[config_id]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # If we couldn't order all configs, there might be circular dependencies
        if len(result) != len(resolved_configs):
            remaining = [c for c in resolved_configs if c not in result]
            self.logger.warning(f"Could not determine order for configs with circular dependencies: {remaining}")
            result.extend(remaining)
        
        return result