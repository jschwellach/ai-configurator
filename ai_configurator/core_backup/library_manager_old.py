"""
Library Manager for configuration library operations.

This module provides the LibraryManager class that handles reading from the local
library/ directory, loading catalogs, searching configurations, and resolving dependencies.
"""

import json
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
import hashlib
import pickle

from ..utils.logging import LoggerMixin
from .catalog_schema import (
    LibraryCatalog, 
    ConfigItem, 
    PersonaInfo, 
    ConfigMetadata,
    CompatibilityInfo,
    UsageStats
)
from .metadata_parser import MetadataParser
from .dependency_resolver import DependencyResolver, ResolutionResult
from .installation_planner import InstallationPlanner, InstallationPlan, ValidationLevel, PlatformInfo


class LibraryManager(LoggerMixin):
    """
    Manages configuration library operations including catalog loading,
    configuration search, and dependency resolution.
    """
    
    def __init__(self, library_path: Optional[Path] = None, cache_ttl: int = 300, target_path: Optional[Path] = None, max_workers: int = 4):
        """
        Initialize LibraryManager.
        
        Args:
            library_path: Path to the library directory. Defaults to ./library/
            cache_ttl: Cache time-to-live in seconds. Defaults to 300 (5 minutes)
            target_path: Target installation directory. Defaults to ~/.kiro/
            max_workers: Maximum number of worker threads for concurrent operations
        """
        self.library_path = library_path or self._get_default_library_path()
        self.target_path = target_path or Path.home() / ".kiro"
        self.cache_ttl = cache_ttl
        self.max_workers = max_workers
        self.metadata_parser = MetadataParser()
        
        # Cache storage with enhanced features
        self._catalog_cache: Optional[LibraryCatalog] = None
        self._catalog_cache_time: Optional[datetime] = None
        self._catalog_cache_hash: Optional[str] = None
        self._config_cache: Dict[str, ConfigMetadata] = {}
        self._config_cache_time: Dict[str, datetime] = {}
        self._config_cache_hash: Dict[str, str] = {}
        
        # Persistent cache directory
        self._cache_dir = Path.home() / ".cache" / "ai-configurator"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._persistent_cache_file = self._cache_dir / "library_cache.pkl"
        
        # Thread pool for concurrent operations
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._cache_lock = threading.RLock()
        
        # Performance tracking
        self._performance_stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'load_times': [],
            'search_times': []
        }
        
        # Dependency management components
        self._dependency_resolver: Optional[DependencyResolver] = None
        self._installation_planner: Optional[InstallationPlanner] = None
        
        # Load persistent cache on startup
        self._load_persistent_cache()
        
        # Ensure library directory exists
        if not self.library_path.exists():
            self.logger.warning(f"Library directory not found: {self.library_path}")
    
    def _get_default_library_path(self) -> Path:
        """Get the default library path - always use project root library."""
        # Always use project root library directory
        # This works for both development and installed packages
        package_root = Path(__file__).parent.parent.parent.parent
        library_path = package_root / "library"
        
        if library_path.exists():
            return library_path
            
        # Fallback: current directory
        return Path("library")
    
    def _is_cache_valid(self, cache_time: Optional[datetime]) -> bool:
        """Check if cache is still valid based on TTL."""
        if cache_time is None:
            return False
        return datetime.now() - cache_time < timedelta(seconds=self.cache_ttl)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file for cache invalidation."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return str(file_path.stat().st_mtime)
    
    def _load_persistent_cache(self) -> None:
        """Load cache from persistent storage."""
        if not self._persistent_cache_file.exists():
            return
        
        try:
            with open(self._persistent_cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Validate cache version and structure
            if cache_data.get('version') == '1.0':
                self._config_cache = cache_data.get('config_cache', {})
                self._config_cache_time = cache_data.get('config_cache_time', {})
                self._config_cache_hash = cache_data.get('config_cache_hash', {})
                self.logger.debug(f"Loaded persistent cache with {len(self._config_cache)} entries")
        
        except Exception as e:
            self.logger.warning(f"Failed to load persistent cache: {e}")
            # Clear corrupted cache file
            try:
                self._persistent_cache_file.unlink()
            except Exception:
                pass
    
    def _save_persistent_cache(self) -> None:
        """Save cache to persistent storage."""
        try:
            cache_data = {
                'version': '1.0',
                'config_cache': self._config_cache,
                'config_cache_time': self._config_cache_time,
                'config_cache_hash': self._config_cache_hash,
                'saved_at': datetime.now()
            }
            
            with open(self._persistent_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.debug("Saved persistent cache")
        
        except Exception as e:
            self.logger.warning(f"Failed to save persistent cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self._cache_lock:
            self._catalog_cache = None
            self._catalog_cache_time = None
            self._catalog_cache_hash = None
            self._config_cache.clear()
            self._config_cache_time.clear()
            self._config_cache_hash.clear()
            
            # Clear persistent cache
            try:
                if self._persistent_cache_file.exists():
                    self._persistent_cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to clear persistent cache: {e}")
            
            self.logger.info("Library cache cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = self._performance_stats.copy()
        
        # Calculate averages
        if stats['load_times']:
            stats['avg_load_time'] = sum(stats['load_times']) / len(stats['load_times'])
        if stats['search_times']:
            stats['avg_search_time'] = sum(stats['search_times']) / len(stats['search_times'])
        
        # Cache hit ratio
        total_requests = stats['cache_hits'] + stats['cache_misses']
        if total_requests > 0:
            stats['cache_hit_ratio'] = stats['cache_hits'] / total_requests
        
        return stats
    
    def load_catalog(self, force_refresh: bool = False, progress_callback: Optional[Callable[[str], None]] = None) -> Optional[LibraryCatalog]:
        """
        Load the configuration catalog from library/catalog.json with enhanced caching.
        
        Args:
            force_refresh: If True, bypass cache and reload from disk
            progress_callback: Optional callback for progress updates
            
        Returns:
            LibraryCatalog object or None if loading fails
        """
        start_time = time.time()
        
        if progress_callback:
            progress_callback("Checking catalog cache...")
        
        catalog_file = self.library_path / "catalog.json"
        
        if not catalog_file.exists():
            self.logger.error(f"Catalog file not found: {catalog_file}")
            return None
        
        # Calculate current file hash
        current_hash = self._calculate_file_hash(catalog_file)
        
        # Check cache with hash validation
        with self._cache_lock:
            if not force_refresh and self._is_cache_valid(self._catalog_cache_time):
                if self._catalog_cache and self._catalog_cache_hash == current_hash:
                    self.logger.debug("Returning cached catalog (hash validated)")
                    self._performance_stats['cache_hits'] += 1
                    return self._catalog_cache
        
        if progress_callback:
            progress_callback("Loading catalog from disk...")
        
        try:
            with open(catalog_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if progress_callback:
                progress_callback("Parsing catalog data...")
            
            catalog = LibraryCatalog(**data)
            
            # Update cache with hash
            with self._cache_lock:
                self._catalog_cache = catalog
                self._catalog_cache_time = datetime.now()
                self._catalog_cache_hash = current_hash
                self._performance_stats['cache_misses'] += 1
            
            load_time = time.time() - start_time
            self._performance_stats['load_times'].append(load_time)
            
            self.logger.info(f"Loaded catalog with {len(catalog.profiles)} configurations in {load_time:.2f}s")
            
            if progress_callback:
                progress_callback(f"Catalog loaded successfully ({len(catalog.profiles)} configurations)")
            
            return catalog
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Failed to load catalog: {e}")
            if progress_callback:
                progress_callback(f"Failed to load catalog: {e}")
            return None
    
    def get_configuration_metadata(self, config_id: str, force_refresh: bool = False) -> Optional[ConfigMetadata]:
        """
        Get detailed metadata for a specific configuration with enhanced caching.
        
        Args:
            config_id: Unique identifier for the configuration
            force_refresh: If True, bypass cache and reload from disk
            
        Returns:
            ConfigMetadata object or None if not found
        """
        # Check cache first with hash validation
        with self._cache_lock:
            if not force_refresh and config_id in self._config_cache:
                if self._is_cache_valid(self._config_cache_time.get(config_id)):
                    # Validate cache with file hash
                    catalog = self.load_catalog()
                    if catalog:
                        config_item = self._find_config_in_catalog(catalog, config_id)
                        if config_item:
                            config_file = self.library_path / config_item.file_path
                            if config_file.exists():
                                current_hash = self._calculate_file_hash(config_file)
                                cached_hash = self._config_cache_hash.get(config_id)
                                if cached_hash == current_hash:
                                    self.logger.debug(f"Returning cached metadata for {config_id}")
                                    self._performance_stats['cache_hits'] += 1
                                    return self._config_cache[config_id]
        
        # Find configuration in catalog
        catalog = self.load_catalog()
        if not catalog:
            return None
        
        config_item = self._find_config_in_catalog(catalog, config_id)
        if not config_item:
            self.logger.warning(f"Configuration not found in catalog: {config_id}")
            return None
        
        # Load full metadata from file
        config_file = self.library_path / config_item.file_path
        if not config_file.exists():
            self.logger.error(f"Configuration file not found: {config_file}")
            return None
        
        try:
            parse_result = self.metadata_parser.parse_file(config_file)
            if parse_result.success and parse_result.metadata:
                # Update cache with hash
                current_hash = self._calculate_file_hash(config_file)
                with self._cache_lock:
                    self._config_cache[config_id] = parse_result.metadata
                    self._config_cache_time[config_id] = datetime.now()
                    self._config_cache_hash[config_id] = current_hash
                    self._performance_stats['cache_misses'] += 1
                
                # Save to persistent cache periodically
                if len(self._config_cache) % 10 == 0:
                    self._save_persistent_cache()
                
                self.logger.debug(f"Loaded metadata for {config_id}")
                return parse_result.metadata
            else:
                if parse_result.errors:
                    error_msgs = [f"{err.field}: {err.message}" for err in parse_result.errors]
                    self.logger.warning(f"Metadata parsing errors for {config_file}: {'; '.join(error_msgs)}")
                else:
                    self.logger.warning(f"No metadata found in file: {config_file}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load metadata for {config_id}: {e}")
            return None
    
    def get_multiple_configuration_metadata(self, config_ids: List[str], progress_callback: Optional[Callable[[str, int, int], None]] = None) -> Dict[str, Optional[ConfigMetadata]]:
        """
        Get metadata for multiple configurations concurrently.
        
        Args:
            config_ids: List of configuration IDs
            progress_callback: Optional callback for progress updates (message, current, total)
            
        Returns:
            Dictionary mapping config_id to metadata (or None if not found)
        """
        results = {}
        
        if not config_ids:
            return results
        
        def load_single_metadata(config_id: str) -> Tuple[str, Optional[ConfigMetadata]]:
            """Load metadata for a single configuration."""
            metadata = self.get_configuration_metadata(config_id)
            return config_id, metadata
        
        # Use thread pool for concurrent loading
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(config_ids))) as executor:
            # Submit all tasks
            future_to_config = {
                executor.submit(load_single_metadata, config_id): config_id 
                for config_id in config_ids
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_config):
                config_id, metadata = future.result()
                results[config_id] = metadata
                completed += 1
                
                if progress_callback:
                    progress_callback(f"Loaded metadata for {config_id}", completed, len(config_ids))
        
        return results
    
    def _find_config_in_catalog(self, catalog: LibraryCatalog, config_id: str) -> Optional[ConfigItem]:
        """Find a configuration item in the catalog by ID."""
        for category_name, category_data in catalog.categories.dict().items():
            if not isinstance(category_data, dict):
                continue
            for subcategory_name, configs in category_data.items():
                if not isinstance(configs, list):
                    continue
                for config in configs:
                    if isinstance(config, dict) and config.get('id') == config_id:
                        return ConfigItem(**config)
                    elif hasattr(config, 'id') and config.id == config_id:
                        return config
        return None
    
    def search_configurations(
        self, 
        query: Optional[str] = None,
        **kwargs  # Ignore other parameters for now during transition
    ) -> List[ConfigItem]:
        """
        Search configurations based on query.
        
        Args:
            query: Text search query (searches name and description)
            
        Returns:
            List of matching ConfigItem objects
        """
        start_time = time.time()
        
        catalog = self.load_catalog()
        if not catalog:
            return []
        
        results = []
        
        # Search through all profiles
        for profile in catalog.profiles:
            # If no query, return all profiles
            if not query:
                results.append(profile)
                continue
                
            # Search in name and description
            query_lower = query.lower()
            if (query_lower in profile.name.lower() or 
                query_lower in profile.description.lower()):
                results.append(profile)
        
        search_time = time.time() - start_time
        self.logger.info(f"Search returned {len(results)} configurations in {search_time:.2f}s")
        
        return results
            if category and category != category_name:
                continue
                
            if not isinstance(category_data, dict):
                continue
                
            for subcategory_name, configs in category_data.items():
                # Filter by subcategory if specified
                if subcategory and subcategory != subcategory_name:
                    continue
                    
                if not isinstance(configs, list):
                    continue
                
                # Process configurations in batches for better performance
                batch_size = 50
                for i in range(0, len(configs), batch_size):
                    batch = configs[i:i + batch_size]
                    batch_results = []
                    
                    for config_data in batch:
                        if isinstance(config_data, dict):
                            config = ConfigItem(**config_data)
                        else:
                            config = config_data
                        
                        # Apply filters
                        if self._matches_filters(config, query, personas, domains, tags):
                            batch_results.append(config)
                        
                        processed_configs += 1
                        
                        # Update progress periodically
                        if progress_callback and processed_configs % 10 == 0:
                            progress = 25 + int((processed_configs / total_configs) * 50)
                            progress_callback(f"Processed {processed_configs}/{total_configs} configurations", progress, 100)
                    
                    results.extend(batch_results)
        
        if progress_callback:
            progress_callback("Sorting results...", 75, 100)
        
        # Sort by relevance (downloads, rating, name) with optimized sorting
        results.sort(key=lambda x: (-x.downloads, -x.rating, x.name))
        
        search_time = time.time() - start_time
        self._performance_stats['search_times'].append(search_time)
        
        self.logger.info(f"Search returned {len(results)} configurations in {search_time:.2f}s")
        
        if progress_callback:
            progress_callback(f"Found {len(results)} configurations", 100, 100)
        
        return results
    
    def _matches_filters(
        self, 
        config: ConfigItem, 
        query: Optional[str],
        personas: Optional[List[str]],
        domains: Optional[List[str]],
        tags: Optional[List[str]]
    ) -> bool:
        """Check if a configuration matches the given filters."""
        
        # Text query filter
        if query:
            query_lower = query.lower()
            searchable_text = f"{config.name} {config.description} {' '.join(config.tags)}".lower()
            if query_lower not in searchable_text:
                return False
        
        # Personas filter
        if personas:
            if not any(persona in config.personas for persona in personas):
                return False
        
        # Domains filter
        if domains:
            if not any(domain in config.domains for domain in domains):
                return False
        
        # Tags filter
        if tags:
            if not any(tag in config.tags for tag in tags):
                return False
        
        return True
    
    def get_configurations_by_persona(self, persona: str) -> List[ConfigItem]:
        """
        Get all configurations recommended for a specific persona.
        
        Args:
            persona: Target persona name
            
        Returns:
            List of ConfigItem objects
        """
        catalog = self.load_catalog()
        if not catalog:
            return []
        
        # Get recommended configs for persona
        persona_info = catalog.personas.get(persona)
        if not persona_info:
            self.logger.warning(f"Persona not found: {persona}")
            return []
        
        # Find configurations by ID
        results = []
        for config_id in persona_info.recommended_configs:
            config_item = self._find_config_in_catalog(catalog, config_id)
            if config_item:
                results.append(config_item)
            else:
                self.logger.warning(f"Recommended config not found: {config_id}")
        
        return results
    
    def resolve_dependencies(self, config_ids: List[str]) -> Dict[str, List[str]]:
        """
        Resolve dependencies for a list of configuration IDs.
        
        Args:
            config_ids: List of configuration IDs to resolve dependencies for
            
        Returns:
            Dictionary mapping config_id to list of dependency IDs
        """
        catalog = self.load_catalog()
        if not catalog:
            return {}
        
        dependency_map = {}
        visited = set()
        
        def resolve_config_deps(config_id: str) -> List[str]:
            """Recursively resolve dependencies for a single config."""
            if config_id in visited:
                return []  # Avoid circular dependencies
            
            visited.add(config_id)
            
            config_item = self._find_config_in_catalog(catalog, config_id)
            if not config_item:
                self.logger.warning(f"Configuration not found for dependency resolution: {config_id}")
                return []
            
            all_deps = []
            for dep_id in config_item.dependencies:
                all_deps.append(dep_id)
                # Recursively resolve dependencies of dependencies
                nested_deps = resolve_config_deps(dep_id)
                all_deps.extend(nested_deps)
            
            return all_deps
        
        # Resolve dependencies for each requested config
        for config_id in config_ids:
            visited.clear()  # Reset for each top-level config
            dependencies = resolve_config_deps(config_id)
            dependency_map[config_id] = list(set(dependencies))  # Remove duplicates
        
        self.logger.info(f"Resolved dependencies for {len(config_ids)} configurations")
        return dependency_map
    
    def get_all_dependencies(self, config_ids: List[str]) -> Set[str]:
        """
        Get all unique dependencies for a list of configuration IDs.
        
        Args:
            config_ids: List of configuration IDs
            
        Returns:
            Set of all unique dependency IDs
        """
        dependency_map = self.resolve_dependencies(config_ids)
        all_deps = set()
        
        for deps in dependency_map.values():
            all_deps.update(deps)
        
        return all_deps
    
    def validate_dependencies(self, config_ids: List[str]) -> Dict[str, List[str]]:
        """
        Validate that all dependencies exist and are available.
        
        Args:
            config_ids: List of configuration IDs to validate
            
        Returns:
            Dictionary mapping config_id to list of missing dependency IDs
        """
        catalog = self.load_catalog()
        if not catalog:
            return {config_id: ["catalog_unavailable"] for config_id in config_ids}
        
        missing_deps = {}
        
        for config_id in config_ids:
            config_item = self._find_config_in_catalog(catalog, config_id)
            if not config_item:
                missing_deps[config_id] = ["config_not_found"]
                continue
            
            config_missing = []
            for dep_id in config_item.dependencies:
                dep_item = self._find_config_in_catalog(catalog, dep_id)
                if not dep_item:
                    config_missing.append(dep_id)
            
            if config_missing:
                missing_deps[config_id] = config_missing
        
        return missing_deps
    
    def list_personas(self) -> Dict[str, PersonaInfo]:
        """
        Get all available personas.
        
        Returns:
            Dictionary mapping persona ID to PersonaInfo
        """
        catalog = self.load_catalog()
        if not catalog:
            return {}
        
        return catalog.personas
    
    def list_categories(self) -> Dict[str, List[str]]:
        """
        Get all available categories and subcategories.
        
        Returns:
            Dictionary mapping category to list of subcategories
        """
        catalog = self.load_catalog()
        if not catalog:
            return {}
        
        categories = {}
        for category_name, category_data in catalog.categories.dict().items():
            if isinstance(category_data, dict):
                categories[category_name] = list(category_data.keys())
            else:
                categories[category_name] = []
        
        return categories
    
    def get_configuration_file_path(self, config_id: str) -> Optional[Path]:
        """
        Get the file path for a configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Path to the configuration file or None if not found
        """
        catalog = self.load_catalog()
        if not catalog:
            return None
        
        config_item = self._find_config_in_catalog(catalog, config_id)
        if not config_item:
            return None
        
        return self.library_path / config_item.file_path
    
    def refresh_catalog(self) -> bool:
        """
        Force refresh the catalog from disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.clear_cache()
            catalog = self.load_catalog(force_refresh=True)
            return catalog is not None
        except Exception as e:
            self.logger.error(f"Failed to refresh catalog: {e}")
            return False
    
    def get_library_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the library.
        
        Returns:
            Dictionary with library statistics
        """
        catalog = self.load_catalog()
        if not catalog:
            return {}
        
        stats = {
            "total_configs": len(catalog.profiles),
            "version": catalog.version,
            "profiles": len(catalog.profiles)
        }
                category_count = sum(len(configs) for configs in category_data.values() if isinstance(configs, list))
                stats["categories"][category_name] = category_count
        
        return stats
    
    def get_dependency_resolver(self) -> Optional[DependencyResolver]:
        """Get or create a dependency resolver instance."""
        catalog = self.load_catalog()
        if not catalog:
            return None
        
        if not self._dependency_resolver:
            self._dependency_resolver = DependencyResolver(catalog)
        
        return self._dependency_resolver
    
    def get_installation_planner(self, platform_info: Optional[PlatformInfo] = None) -> Optional[InstallationPlanner]:
        """Get or create an installation planner instance."""
        catalog = self.load_catalog()
        if not catalog:
            return None
        
        if not self._installation_planner:
            self._installation_planner = InstallationPlanner(
                catalog=catalog,
                library_path=self.library_path,
                target_path=self.target_path,
                platform_info=platform_info
            )
        
        return self._installation_planner
    
    def resolve_dependencies_advanced(
        self, 
        config_ids: List[str],
        platform: Optional[str] = None,
        kiro_version: Optional[str] = None
    ) -> Optional[ResolutionResult]:
        """
        Advanced dependency resolution with conflict detection.
        
        Args:
            config_ids: List of configuration IDs to resolve
            platform: Target platform for compatibility checking
            kiro_version: Target Kiro version for compatibility checking
            
        Returns:
            ResolutionResult with resolved configurations and conflicts
        """
        resolver = self.get_dependency_resolver()
        if not resolver:
            return None
        
        return resolver.resolve_dependencies(config_ids, platform, kiro_version)
    
    def create_installation_plan(
        self,
        config_ids: List[str],
        validation_level: ValidationLevel = ValidationLevel.BASIC,
        dry_run: bool = False,
        force_reinstall: bool = False,
        platform_info: Optional[PlatformInfo] = None
    ) -> Optional[InstallationPlan]:
        """
        Create an installation plan for the given configurations.
        
        Args:
            config_ids: List of configuration IDs to install
            validation_level: Level of validation to perform
            dry_run: If True, create plan without actually installing
            force_reinstall: If True, reinstall even if already installed
            platform_info: Platform information for compatibility checking
            
        Returns:
            InstallationPlan with all steps and validation results
        """
        planner = self.get_installation_planner(platform_info)
        if not planner:
            return None
        
        return planner.create_installation_plan(
            config_ids=config_ids,
            validation_level=validation_level,
            dry_run=dry_run,
            force_reinstall=force_reinstall
        )
    
    def validate_installation_plan(self, plan: InstallationPlan) -> Tuple[bool, List[str]]:
        """
        Validate an installation plan.
        
        Args:
            plan: Installation plan to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        planner = self.get_installation_planner()
        if not planner:
            return False, ["Installation planner not available"]
        
        return planner.validate_plan(plan)
    
    def preview_installation_plan(self, plan: InstallationPlan) -> str:
        """
        Generate a human-readable preview of an installation plan.
        
        Args:
            plan: Installation plan to preview
            
        Returns:
            Formatted string describing the plan
        """
        planner = self.get_installation_planner()
        if not planner:
            return "Installation planner not available"
        
        return planner.preview_plan(plan)
    
    def get_dependency_tree(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the complete dependency tree for a configuration.
        
        Args:
            config_id: Configuration ID to analyze
            
        Returns:
            Dictionary representing the dependency tree
        """
        resolver = self.get_dependency_resolver()
        if not resolver:
            return None
        
        return resolver.get_dependency_tree(config_id)
    
    def suggest_installation_order(self, config_ids: List[str]) -> List[str]:
        """
        Suggest an optimal installation order based on dependencies.
        
        Args:
            config_ids: List of configuration IDs to order
            
        Returns:
            List of configuration IDs in suggested installation order
        """
        resolver = self.get_dependency_resolver()
        if not resolver:
            return config_ids
        
        return resolver.suggest_resolution_order(config_ids)
    
    def clear_dependency_cache(self) -> None:
        """Clear dependency resolver and installation planner caches."""
        self._dependency_resolver = None
        self._installation_planner = None
        self.logger.info("Dependency management caches cleared")
    
    def shutdown(self) -> None:
        """Shutdown the library manager and cleanup resources."""
        try:
            # Save persistent cache before shutdown
            self._save_persistent_cache()
            
            # Shutdown thread pool
            self._executor.shutdown(wait=True)
            
            self.logger.info("LibraryManager shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during LibraryManager shutdown: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during destruction