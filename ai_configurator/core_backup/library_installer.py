"""Installation system for AI Configuration Library profiles."""

import shutil
import json
import subprocess
import tempfile
import uuid
import threading
import time
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import os
import logging

from ..utils.logging import LoggerMixin
from .models import Profile, InstalledProfile, ProfileInfo
from .profile_validator import ProfileValidator


class InstallationError(Exception):
    """Custom exception for installation errors."""
    pass


class RollbackError(Exception):
    """Custom exception for rollback errors."""
    pass


class LibraryInstallationManager(LoggerMixin):
    """Manages installation of AI Configuration Library profiles with production-ready features."""
    
    def __init__(self, library_path: Optional[Path] = None, independent_storage: Optional[Path] = None, max_workers: int = 4):
        """
        Initialize the installation manager.
        
        Args:
            library_path: Path to the AI Configuration Library. If None, uses default location.
            independent_storage: Path to independent storage directory. If None, uses ~/.config/ai-configurations/
            max_workers: Maximum number of worker threads for concurrent operations
        """
        self.library_path = library_path or self._get_default_library_path()
        self.independent_storage = independent_storage or self._get_default_independent_storage()
        self.installation_manifest_path = self._get_installation_manifest_path()
        self.max_workers = max_workers
        
        # Target detection cache with thread safety
        self._target_paths_cache = {}
        self._cache_lock = threading.RLock()
        
        # Rollback tracking
        self._rollback_operations = []
        self._rollback_lock = threading.RLock()
        
        # Thread pool for concurrent operations
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance tracking
        self._performance_stats = {
            'installations': 0,
            'installation_times': [],
            'concurrent_installations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._stats_lock = threading.RLock()
        
        # Setup enhanced logging
        self._setup_enhanced_logging()
        
        # Ensure independent storage exists
        self._ensure_independent_storage()
    
    def _get_default_library_path(self) -> Path:
        """Get the default library path."""
        # Try to find library in package data first (for installed packages)
        try:
            import ai_configurator
            package_path = Path(ai_configurator.__file__).parent
            library_path = package_path / 'library'
            if library_path.exists():
                return library_path
        except (ImportError, AttributeError):
            pass
        
        # Fallback to relative path (for development)
        package_root = Path(__file__).parent.parent.parent.parent
        library_path = package_root / "library"
        if library_path.exists():
            return library_path
            
        # Last resort: current directory
        return Path("library")
    
    def _get_default_independent_storage(self) -> Path:
        """Get the default independent storage path."""
        return Path.home() / ".config" / "ai-configurations"
    
    def _get_installation_manifest_path(self) -> Path:
        """Get path to installation manifest file."""
        return self.independent_storage / "installed_profiles.json"
    
    def _setup_enhanced_logging(self) -> None:
        """Setup enhanced logging with debug capabilities."""
        # Create a file handler for detailed logging
        log_file = self.independent_storage / "installation.log"
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.debug("LibraryInstallationManager initialized with enhanced logging")
    
    def _ensure_independent_storage(self) -> None:
        """Ensure independent storage directory structure exists."""
        try:
            # Create main directories
            directories = [
                self.independent_storage,
                self.independent_storage / "contexts",
                self.independent_storage / "hooks",
                self.independent_storage / "backups",
                self.independent_storage / "temp"
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {directory}")
                
        except Exception as e:
            self.logger.error(f"Failed to create independent storage structure: {e}")
            raise InstallationError(f"Failed to initialize storage: {e}")
    
    def detect_target_paths(self, target: str) -> Optional[Dict[str, str]]:
        """
        Detect target installation paths for the specified target with caching.
        
        Args:
            target: Target system ('kiro', 'amazonq', or 'auto')
            
        Returns:
            Dictionary with target paths or None if target not available
        """
        with self._cache_lock:
            if target in self._target_paths_cache:
                with self._stats_lock:
                    self._performance_stats['cache_hits'] += 1
                return self._target_paths_cache[target]
        
        paths = {}
        
        if target == "kiro" or target == "auto":
            # Check for Kiro installation
            kiro_paths = self._detect_kiro_paths()
            if kiro_paths:
                paths.update(kiro_paths)
                if target == "kiro":
                    with self._cache_lock:
                        self._target_paths_cache[target] = paths
                    with self._stats_lock:
                        self._performance_stats['cache_misses'] += 1
                    return paths
        
        if target == "amazonq" or target == "auto":
            # Check for Amazon Q CLI installation
            amazonq_paths = self._detect_amazonq_paths()
            if amazonq_paths:
                paths.update(amazonq_paths)
                if target == "amazonq":
                    with self._cache_lock:
                        self._target_paths_cache[target] = paths
                    with self._stats_lock:
                        self._performance_stats['cache_misses'] += 1
                    return paths
        
        if target == "auto" and paths:
            with self._cache_lock:
                self._target_paths_cache[target] = paths
            with self._stats_lock:
                self._performance_stats['cache_misses'] += 1
            return paths
        
        return None if not paths else paths
    
    def _detect_kiro_paths(self) -> Optional[Dict[str, str]]:
        """Detect Kiro installation paths."""
        # Check current directory for .kiro folder
        current_dir = Path.cwd()
        kiro_dir = current_dir / ".kiro"
        
        if kiro_dir.exists():
            return {
                "contexts_dir": str(kiro_dir / "steering"),
                "hooks_dir": str(kiro_dir / "hooks"),
                "target_type": "kiro"
            }
        
        # Check parent directories up to 3 levels
        for parent in [current_dir.parent, current_dir.parent.parent, current_dir.parent.parent.parent]:
            kiro_dir = parent / ".kiro"
            if kiro_dir.exists():
                return {
                    "contexts_dir": str(kiro_dir / "steering"),
                    "hooks_dir": str(kiro_dir / "hooks"),
                    "target_type": "kiro"
                }
        
        return None
    
    def _detect_amazonq_paths(self) -> Optional[Dict[str, str]]:
        """Detect Amazon Q CLI installation paths."""
        home = Path.home()
        
        # Check for Amazon Q CLI configuration directory
        amazonq_config_dir = home / ".aws" / "amazonq"
        
        if amazonq_config_dir.exists() or self._is_amazonq_installed():
            return {
                "profiles_dir": str(amazonq_config_dir / "profiles"),
                "contexts_dir": str(self.independent_storage / "contexts"),  # Use independent storage
                "hooks_dir": str(amazonq_config_dir / "hooks"),  # Amazon Q CLI expects hooks in ~/.aws/amazonq/hooks/
                "project_rules_dir": str(Path.cwd() / ".amazonq" / "rules"),
                "target_type": "amazonq"
            }
        
        return None
    
    def _is_amazonq_installed(self) -> bool:
        """Check if Amazon Q CLI is installed."""
        try:
            import subprocess
            result = subprocess.run(["q", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of an existing file before overwriting.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file or None if backup failed
        """
        if not file_path.exists():
            self.logger.debug(f"No backup needed, file doesn't exist: {file_path}")
            return None
        
        try:
            # Use independent storage backup directory
            backup_dir = self.independent_storage / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            
            # Track for rollback
            self._rollback_operations.append({
                'type': 'restore_backup',
                'original_path': str(file_path),
                'backup_path': str(backup_path)
            })
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup of {file_path}: {e}")
            raise InstallationError(f"Backup creation failed: {e}")
    
    def _add_rollback_operation(self, operation_type: str, **kwargs) -> None:
        """Add an operation to the rollback stack."""
        operation = {
            'type': operation_type,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        self._rollback_operations.append(operation)
        self.logger.debug(f"Added rollback operation: {operation}")
    
    def _clear_rollback_operations(self) -> None:
        """Clear the rollback operations stack."""
        self._rollback_operations.clear()
        self.logger.debug("Cleared rollback operations")
    
    def _execute_rollback(self) -> bool:
        """Execute rollback operations in reverse order."""
        self.logger.info(f"Executing rollback for {len(self._rollback_operations)} operations")
        
        success = True
        errors = []
        
        # Execute operations in reverse order
        for operation in reversed(self._rollback_operations):
            try:
                self._execute_rollback_operation(operation)
                self.logger.debug(f"Rollback operation successful: {operation['type']}")
            except Exception as e:
                error_msg = f"Rollback operation failed: {operation['type']} - {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                success = False
        
        if errors:
            raise RollbackError(f"Rollback partially failed: {'; '.join(errors)}")
        
        self._clear_rollback_operations()
        return success
    
    def _execute_rollback_operation(self, operation: Dict[str, Any]) -> None:
        """Execute a single rollback operation."""
        op_type = operation['type']
        
        if op_type == 'remove_file':
            file_path = Path(operation['file_path'])
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Removed file during rollback: {file_path}")
        
        elif op_type == 'remove_directory':
            dir_path = Path(operation['dir_path'])
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                self.logger.debug(f"Removed directory during rollback: {dir_path}")
        
        elif op_type == 'restore_backup':
            original_path = Path(operation['original_path'])
            backup_path = Path(operation['backup_path'])
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                self.logger.debug(f"Restored backup during rollback: {original_path}")
        
        elif op_type == 'update_manifest':
            # Restore previous manifest state
            manifest_backup = operation.get('previous_manifest')
            if manifest_backup:
                with open(self.installation_manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest_backup, f, indent=2, ensure_ascii=False)
                self.logger.debug("Restored manifest during rollback")
        
        else:
            self.logger.warning(f"Unknown rollback operation type: {op_type}")
    
    def ensure_directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            dir_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        dir_path = Path(dir_path)
        
        try:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created directory: {dir_path}")
                
                # Track for rollback if this is a new directory
                self._add_rollback_operation('remove_directory', dir_path=str(dir_path))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create directory {dir_path}: {e}")
            raise InstallationError(f"Directory creation failed: {e}")
    
    def copy_profile_files(self, profile: Profile, profile_dir: Path, target_paths: Dict[str, str]) -> List[str]:
        """
        Copy profile files to target directories with optimized operations.
        
        Args:
            profile: Profile to install
            profile_dir: Source profile directory
            target_paths: Target installation paths
            
        Returns:
            List of installed file paths
        """
        installed_files = []
        
        try:
            # Copy context files
            if profile.contexts:
                installed_files.extend(
                    self._copy_file_group(
                        profile.contexts,
                        profile_dir / "contexts",
                        Path(target_paths["contexts_dir"]),
                        "context"
                    )
                )
            
            # Copy hook files
            if profile.hooks:
                installed_files.extend(
                    self._copy_file_group(
                        profile.hooks,
                        profile_dir / "hooks",
                        Path(target_paths["hooks_dir"]),
                        "hook"
                    )
                )
            
            return installed_files
            
        except Exception as e:
            self.logger.error(f"Failed to copy profile files: {e}")
            raise InstallationError(f"File copy operation failed: {e}")
    
    def _copy_file_group(self, file_list: List[str], source_dir: Path, target_dir: Path, file_type: str) -> List[str]:
        """
        Copy a group of files with optimized operations and error handling.
        
        Args:
            file_list: List of files to copy
            source_dir: Source directory
            target_dir: Target directory
            file_type: Type of files being copied (for logging)
            
        Returns:
            List of successfully copied file paths
        """
        if not file_list:
            return []
        
        self.logger.debug(f"Copying {len(file_list)} {file_type} files from {source_dir} to {target_dir}")
        
        # Ensure target directory exists
        self.ensure_directory_exists(target_dir)
        
        installed_files = []
        errors = []
        
        for file_name in file_list:
            try:
                source_path = source_dir / file_name
                target_path = target_dir / file_name
                
                if not source_path.exists():
                    error_msg = f"{file_type.capitalize()} file not found: {file_name}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                
                # Validate file before copying
                if not self._validate_file_for_copy(source_path):
                    error_msg = f"File validation failed: {file_name}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
                
                # Create backup if file exists
                if target_path.exists():
                    self.create_backup(target_path)
                
                # Ensure target subdirectory exists
                self.ensure_directory_exists(target_path.parent)
                
                # Copy file with metadata preservation
                shutil.copy2(source_path, target_path)
                installed_files.append(str(target_path))
                
                # Track for rollback
                self._add_rollback_operation('remove_file', file_path=str(target_path))
                
                self.logger.info(f"Installed {file_type}: {file_name}")
                
            except Exception as e:
                error_msg = f"Failed to copy {file_type} file {file_name}: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        if errors and not installed_files:
            # All files failed to copy
            raise InstallationError(f"All {file_type} files failed to copy: {'; '.join(errors)}")
        elif errors:
            # Some files failed, log warnings but continue
            self.logger.warning(f"Some {file_type} files failed to copy: {'; '.join(errors)}")
        
        return installed_files
    
    def _validate_file_for_copy(self, file_path: Path) -> bool:
        """
        Validate a file before copying.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file is valid for copying
        """
        try:
            # Check file size (prevent copying extremely large files)
            max_size = 10 * 1024 * 1024  # 10MB limit
            if file_path.stat().st_size > max_size:
                self.logger.warning(f"File too large to copy: {file_path} ({file_path.stat().st_size} bytes)")
                return False
            
            # Check if file is readable
            with open(file_path, 'r', encoding='utf-8') as f:
                # Try to read first few bytes to ensure it's readable
                f.read(1024)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"File validation failed for {file_path}: {e}")
            return False
    
    def load_installation_manifest(self) -> Dict[str, InstalledProfile]:
        """Load the installation manifest with enhanced error handling."""
        if not self.installation_manifest_path.exists():
            self.logger.debug("Installation manifest doesn't exist, returning empty manifest")
            return {}
        
        try:
            with open(self.installation_manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            manifest = {}
            for profile_name, profile_data in data.items():
                try:
                    manifest[profile_name] = InstalledProfile.from_dict(profile_data)
                except Exception as e:
                    self.logger.warning(f"Failed to parse installed profile {profile_name}: {e}")
                    continue
            
            self.logger.debug(f"Loaded manifest with {len(manifest)} profiles")
            return manifest
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Manifest file is corrupted: {e}")
            # Try to create backup of corrupted manifest
            try:
                corrupted_backup = self.installation_manifest_path.with_suffix('.corrupted')
                shutil.copy2(self.installation_manifest_path, corrupted_backup)
                self.logger.info(f"Created backup of corrupted manifest: {corrupted_backup}")
            except Exception:
                pass
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to load installation manifest: {e}")
            return {}
    
    def save_installation_manifest(self, manifest: Dict[str, InstalledProfile]) -> bool:
        """Save the installation manifest with atomic operations."""
        try:
            # Ensure directory exists
            self.installation_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for profile_name, installed_profile in manifest.items():
                try:
                    data[profile_name] = installed_profile.to_dict()
                except Exception as e:
                    self.logger.warning(f"Failed to serialize profile {profile_name}: {e}")
                    continue
            
            # Use atomic write operation
            temp_path = self.installation_manifest_path.with_suffix('.tmp')
            
            try:
                # Write to temporary file first
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic move to final location
                temp_path.replace(self.installation_manifest_path)
                
                self.logger.debug(f"Saved manifest with {len(data)} profiles")
                return True
                
            except Exception as e:
                # Clean up temporary file if it exists
                if temp_path.exists():
                    temp_path.unlink()
                raise e
            
        except Exception as e:
            self.logger.error(f"Failed to save installation manifest: {e}")
            return False
    
    def install_multiple_profiles(
        self, 
        profile_names: List[str], 
        target: str = "auto", 
        force: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, bool]:
        """
        Install multiple profiles concurrently with progress tracking.
        
        Args:
            profile_names: List of profile names to install
            target: Target system ('kiro', 'amazonq', 'auto', or 'both')
            force: Force installation even if profiles are already installed
            progress_callback: Optional callback for progress updates (message, current, total)
            
        Returns:
            Dictionary mapping profile_name to installation success status
        """
        if not profile_names:
            return {}
        
        self.logger.info(f"Starting concurrent installation of {len(profile_names)} profiles")
        
        with self._stats_lock:
            self._performance_stats['concurrent_installations'] += 1
        
        results = {}
        
        def install_single_profile(profile_name: str) -> Tuple[str, bool]:
            """Install a single profile and return result."""
            try:
                success = self.install_profile(profile_name, target, force)
                return profile_name, success
            except Exception as e:
                self.logger.error(f"Concurrent installation failed for {profile_name}: {e}")
                return profile_name, False
        
        # Use thread pool for concurrent installations
        max_concurrent = min(self.max_workers, len(profile_names))
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all installation tasks
            future_to_profile = {
                executor.submit(install_single_profile, profile_name): profile_name 
                for profile_name in profile_names
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_profile):
                profile_name, success = future.result()
                results[profile_name] = success
                completed += 1
                
                if progress_callback:
                    status = "✅" if success else "❌"
                    progress_callback(f"{status} {profile_name}", completed, len(profile_names))
        
        success_count = sum(1 for success in results.values() if success)
        self.logger.info(f"Concurrent installation completed: {success_count}/{len(profile_names)} successful")
        
        return results
    
    def install_profile(self, profile_name: str, target: str = "auto", force: bool = False, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Install a profile to the specified target with rollback capabilities and progress tracking.
        
        Args:
            profile_name: Name of profile to install
            target: Target system ('kiro', 'amazonq', 'auto', or 'both')
            force: Force installation even if profile is already installed
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if installation was successful
        """
        print(f"DEBUG: install_profile called with {profile_name}, {target}")
        start_time = time.time()
        
        # Clear any previous rollback operations
        with self._rollback_lock:
            self._clear_rollback_operations()
        
        self.logger.info(f"Starting installation of profile '{profile_name}' to target '{target}'")
        
        if progress_callback:
            progress_callback(f"Starting installation of {profile_name}...")
        
        try:
            # Validate inputs
            if not profile_name or not profile_name.strip():
                raise InstallationError("Profile name cannot be empty")
            
            if progress_callback:
                progress_callback("Validating profile...")
            
            print(f"DEBUG: Starting installation of {profile_name}")
            
            # Find profile in library using catalog
            from .library_manager import LibraryManager
            library_manager = LibraryManager(library_path=self.library_path)
            catalog = library_manager.load_catalog()
            
            if not catalog:
                raise InstallationError("Failed to load library catalog")
            
            print(f"DEBUG: Catalog loaded successfully")
            
            # Find the profile in the catalog
            profile_config = None
            print(f"DEBUG: Searching for profile {profile_name} in catalog")
            for category_name, category_profiles in catalog.categories.profiles.items():
                print(f"DEBUG: Checking category {category_name} with {len(category_profiles)} profiles")
                for config in category_profiles:
                    if config.id == profile_name:
                        profile_config = config
                        break
                if profile_config:
                    break
            
            if not profile_config:
                raise InstallationError(f"Profile not found: {profile_name}")
            
            print(f"DEBUG: Found profile config: {profile_config.id}")
            
            # Get the directory path from the catalog
            profile_dir = self.library_path / profile_config.file_path.split('/')[0]
            if not profile_dir.exists():
                raise InstallationError(f"Profile directory not found: {profile_dir}")
            
            print(f"DEBUG: Profile directory: {profile_dir}")
            
            # Validate profile structure
            print(f"DEBUG: Starting profile validation")
            is_valid, errors = ProfileValidator.validate_profile_structure(profile_dir)
            if not is_valid:
                raise InstallationError(f"Profile validation failed: {'; '.join(errors)}")
            
            print(f"DEBUG: Profile validation passed")
            
            if progress_callback:
                progress_callback("Loading profile configuration...")
            
            # Load profile
            try:
                print(f"DEBUG: Loading profile YAML")
                profile = Profile.from_yaml(profile_dir / "profile.yaml")
                self.logger.debug(f"Loaded profile: {profile.name} v{profile.version}")
                print(f"DEBUG: Profile loaded successfully")
            except Exception as e:
                print(f"DEBUG: Failed to load profile: {e}")
                raise InstallationError(f"Failed to load profile: {e}")
            
            if progress_callback:
                progress_callback("Checking installation manifest...")
            
            # Load installation manifest and create backup for rollback
            manifest = self.load_installation_manifest()
            previous_manifest = {k: v.to_dict() for k, v in manifest.items()}
            with self._rollback_lock:
                self._add_rollback_operation('update_manifest', previous_manifest=previous_manifest)
            
            # Check if already installed
            if profile_name in manifest and not force:
                installed = manifest[profile_name]
                if installed.version == profile.version:
                    self.logger.info(f"Profile '{profile_name}' version {profile.version} is already installed")
                    if progress_callback:
                        progress_callback("Profile already installed")
                    return True
                else:
                    self.logger.info(f"Profile '{profile_name}' has update available: {installed.version} -> {profile.version}")
                    if progress_callback:
                        progress_callback(f"Updating from v{installed.version} to v{profile.version}")
            
            # Handle 'both' target
            if target == "both":
                if progress_callback:
                    progress_callback("Installing to multiple targets...")
                success = True
                for single_target in ["kiro", "amazonq"]:
                    if not self.install_profile(profile_name, single_target, force, progress_callback):
                        success = False
                return success
            
            if progress_callback:
                progress_callback("Detecting target paths...")
            
            # Detect target paths
            target_paths = self.detect_target_paths(target)
            if not target_paths:
                raise InstallationError(f"Target '{target}' not available or not detected")
            
            actual_target = target_paths["target_type"]
            self.logger.info(f"Installing to {actual_target} at {target_paths['contexts_dir']}")
            
            if progress_callback:
                progress_callback(f"Installing files to {actual_target}...")
            
            # Perform installation
            installed_files = []
            
            if actual_target == "amazonq":
                installed_files = self._install_amazonq_profile(profile, profile_name, profile_dir, target_paths)
            else:
                installed_files = self._install_kiro_profile(profile, profile_dir, target_paths)
            
            if progress_callback:
                progress_callback("Updating installation manifest...")
            
            # Update installation manifest
            installed_profile = InstalledProfile(
                name=profile_name,
                version=profile.version,
                installed_date=datetime.now(),
                target=actual_target,
                files=installed_files
            )
            
            manifest[profile_name] = installed_profile
            
            if not self.save_installation_manifest(manifest):
                raise InstallationError("Failed to save installation manifest")
            
            # Clear rollback operations on success
            with self._rollback_lock:
                self._clear_rollback_operations()
            
            # Update performance stats
            installation_time = time.time() - start_time
            with self._stats_lock:
                self._performance_stats['installations'] += 1
                self._performance_stats['installation_times'].append(installation_time)
            
            self.logger.info(f"Successfully installed profile '{profile_name}' version {profile.version} in {installation_time:.2f}s")
            
            if progress_callback:
                progress_callback(f"Installation completed successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Installation failed for profile '{profile_name}': {e}")
            
            # Attempt rollback
            try:
                self.logger.info("Attempting rollback due to installation failure")
                self._execute_rollback()
                self.logger.info("Rollback completed successfully")
            except Exception as rollback_error:
                self.logger.error(f"Rollback failed: {rollback_error}")
                # Don't raise rollback error, just log it
            
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the installation manager."""
        with self._stats_lock:
            stats = self._performance_stats.copy()
        
        # Calculate averages
        if stats['installation_times']:
            stats['avg_installation_time'] = sum(stats['installation_times']) / len(stats['installation_times'])
            stats['total_installation_time'] = sum(stats['installation_times'])
        
        # Cache hit ratio
        total_cache_requests = stats['cache_hits'] + stats['cache_misses']
        if total_cache_requests > 0:
            stats['cache_hit_ratio'] = stats['cache_hits'] / total_cache_requests
        
        return stats
    
    def clear_performance_stats(self) -> None:
        """Clear performance statistics."""
        with self._stats_lock:
            self._performance_stats = {
                'installations': 0,
                'installation_times': [],
                'concurrent_installations': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }
        self.logger.info("Performance statistics cleared")
    
    def shutdown(self) -> None:
        """Shutdown the installation manager and cleanup resources."""
        try:
            # Shutdown thread pool
            self._executor.shutdown(wait=True)
            
            self.logger.info("LibraryInstallationManager shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during LibraryInstallationManager shutdown: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during destruction
    
    def _install_amazonq_profile(self, profile: Profile, profile_name: str, profile_dir: Path, target_paths: Dict[str, str]) -> List[str]:
        """Install profile for Amazon Q CLI."""
        try:
            installed_files = []
            
            # Create profile directory
            target_profile_dir = Path(target_paths["profiles_dir"]) / profile_name
            self.ensure_directory_exists(target_profile_dir)
            
            # Install context files to independent storage
            contexts_dir = Path(target_paths["contexts_dir"])
            self.ensure_directory_exists(contexts_dir)
            
            context_paths = []
            profile_source_dir = profile_dir
            
            # Copy context files and collect their paths
            if profile.contexts:
                contexts_source_dir = profile_source_dir / "contexts"
                for context_file in profile.contexts:
                    source_path = contexts_source_dir / context_file
                    if source_path.exists():
                        # Install to independent storage with profile prefix
                        target_filename = f"{profile_name}_{context_file}"
                        target_path = contexts_dir / target_filename
                        
                        # Create backup if file exists
                        if target_path.exists():
                            self.create_backup(target_path)
                        
                        # Copy file
                        shutil.copy2(source_path, target_path)
                        context_paths.append(str(target_path))
                        installed_files.append(str(target_path))
                        
                        # Track for rollback
                        self._add_rollback_operation('remove_file', file_path=str(target_path))
                        
                        self.logger.info(f"Installed context: {target_filename}")
                    else:
                        self.logger.warning(f"Context file not found: {context_file}")
            
            # Install hook files to Amazon Q CLI hooks directory
            hooks_dir = Path(target_paths["hooks_dir"])
            self.ensure_directory_exists(hooks_dir)
            
            hook_configs = {}
            if profile.hooks:
                hooks_source_dir = profile_source_dir / "hooks"
                for hook_file in profile.hooks:
                    source_path = hooks_source_dir / hook_file
                    if source_path.exists():
                        # Install hook with profile prefix to avoid conflicts
                        target_filename = f"{profile_name}_{hook_file}"
                        target_path = hooks_dir / target_filename
                        
                        # Create backup if file exists
                        if target_path.exists():
                            self.create_backup(target_path)
                        
                        # Copy file
                        shutil.copy2(source_path, target_path)
                        installed_files.append(str(target_path))
                        
                        # Track for rollback
                        self._add_rollback_operation('remove_file', file_path=str(target_path))
                        
                        # Add hook configuration
                        hook_configs[hook_file] = {
                            "path": str(target_path),
                            "enabled": True
                        }
                        
                        self.logger.info(f"Installed hook: {target_filename}")
                    else:
                        self.logger.warning(f"Hook file not found: {hook_file}")
            
            # Create context.json file with hook support
            context_config = {
                "paths": context_paths,
                "hooks": {}
            }
            
            # Add hook configurations directly to context.json
            if profile.hooks:
                for hook_file in profile.hooks:
                    if hook_file.endswith('.yaml') or hook_file.endswith('.yml'):
                        # Load hook YAML configuration
                        hook_yaml_path = hooks_source_dir / hook_file
                        if hook_yaml_path.exists():
                            try:
                                with open(hook_yaml_path, 'r', encoding='utf-8') as f:
                                    hook_config = yaml.safe_load(f)
                                
                                # Convert to Amazon Q CLI format
                                hook_name = hook_config.get('name', hook_file.replace('.yaml', '').replace('.yml', ''))
                                hook_id = hook_file.replace('.yaml', '').replace('.yml', '')
                                
                                # Map trigger types to Amazon Q CLI supported values
                                trigger = hook_config.get('trigger', 'conversation_start')
                                if trigger in ['on_session_start', 'session_start']:
                                    trigger = 'conversation_start'
                                elif trigger not in ['conversation_start', 'per_prompt']:
                                    trigger = 'conversation_start'  # Default fallback
                                
                                # Map type to Amazon Q CLI supported values
                                hook_type = hook_config.get('type', 'inline')
                                if hook_type == 'script':
                                    hook_type = 'inline'
                                
                                # Find corresponding script file
                                script_file = hook_config.get('script', '')
                                script_path = None
                                if script_file:
                                    script_path = str(hooks_dir / f"{profile_name}_{script_file}")
                                
                                context_config["hooks"][hook_id] = {
                                    "name": hook_name,
                                    "description": hook_config.get('description', ''),
                                    "trigger": trigger,
                                    "type": hook_type,
                                    "script": script_path,
                                    "enabled": hook_config.get('enabled', True)
                                }
                                
                            except Exception as e:
                                self.logger.warning(f"Failed to parse hook configuration {hook_file}: {e}")
            
            context_json_path = target_profile_dir / "context.json"
            with open(context_json_path, 'w', encoding='utf-8') as f:
                json.dump(context_config, f, indent=2)
            
            installed_files.append(str(context_json_path))
            self._add_rollback_operation('remove_file', file_path=str(context_json_path))
            
            self.logger.info(f"Created Amazon Q CLI profile: {profile_name}")
            return installed_files
            
        except Exception as e:
            raise InstallationError(f"Failed to install Amazon Q CLI profile {profile_name}: {e}")
    
    def _install_kiro_profile(self, profile: Profile, profile_dir: Path, target_paths: Dict[str, str]) -> List[str]:
        """Install profile for Kiro."""
        try:
            return self.copy_profile_files(profile, profile_dir, target_paths)
        except Exception as e:
            raise InstallationError(f"Failed to install Kiro profile: {e}")
    
    def list_installed(self) -> List[InstalledProfile]:
        """List currently installed profiles."""
        manifest = self.load_installation_manifest()
        return list(manifest.values())
    
    def is_profile_installed(self, profile_name: str) -> bool:
        """Check if a profile is installed."""
        manifest = self.load_installation_manifest()
        return profile_name in manifest
    
    def get_installed_profile(self, profile_name: str) -> Optional[InstalledProfile]:
        """Get information about an installed profile."""
        manifest = self.load_installation_manifest()
        return manifest.get(profile_name)
    
    def remove_profile(self, profile_name: str) -> bool:
        """
        Remove an installed profile with enhanced error handling.
        
        Args:
            profile_name: Name of profile to remove
            
        Returns:
            True if removal was successful
        """
        self.logger.info(f"Starting removal of profile '{profile_name}'")
        
        try:
            # Validate input
            if not profile_name or not profile_name.strip():
                raise InstallationError("Profile name cannot be empty")
            
            # Load installation manifest
            manifest = self.load_installation_manifest()
            
            if profile_name not in manifest:
                self.logger.warning(f"Profile '{profile_name}' is not installed")
                return True  # Consider this success since the end state is achieved
            
            installed_profile = manifest[profile_name]
            self.logger.debug(f"Found installed profile: {installed_profile.name} v{installed_profile.version}")
            
            # Remove installed files
            removal_errors = []
            removed_files = []
            
            for file_path in installed_profile.files:
                try:
                    file_path_obj = Path(file_path)
                    if file_path_obj.exists():
                        # Create backup before removal (for safety)
                        backup_path = self.create_backup(file_path_obj)
                        
                        file_path_obj.unlink()
                        removed_files.append(file_path)
                        self.logger.info(f"Removed file: {file_path}")
                        
                        # Clean up empty parent directories
                        self._cleanup_empty_directories(file_path_obj.parent)
                        
                    else:
                        self.logger.warning(f"File not found during removal: {file_path}")
                        
                except Exception as e:
                    error_msg = f"Failed to remove file {file_path}: {e}"
                    self.logger.error(error_msg)
                    removal_errors.append(error_msg)
            
            # Remove from manifest
            del manifest[profile_name]
            
            if not self.save_installation_manifest(manifest):
                raise InstallationError("Failed to save installation manifest after removal")
            
            if removal_errors:
                self.logger.warning(f"Profile '{profile_name}' removed with errors: {'; '.join(removal_errors)}")
            else:
                self.logger.info(f"Successfully removed profile '{profile_name}'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove profile '{profile_name}': {e}")
            return False
    
    def _cleanup_empty_directories(self, directory: Path) -> None:
        """
        Clean up empty directories after file removal.
        
        Args:
            directory: Directory to check and potentially remove
        """
        try:
            # Don't remove the main independent storage directories
            protected_dirs = {
                self.independent_storage,
                self.independent_storage / "contexts",
                self.independent_storage / "hooks",
                self.independent_storage / "backups",
                self.independent_storage / "temp"
            }
            
            if directory in protected_dirs:
                return
            
            # Only remove if directory is empty and within our storage
            if (directory.exists() and 
                directory.is_dir() and 
                not any(directory.iterdir()) and
                self.independent_storage in directory.parents):
                
                directory.rmdir()
                self.logger.debug(f"Removed empty directory: {directory}")
                
                # Recursively check parent directory
                self._cleanup_empty_directories(directory.parent)
                
        except Exception as e:
            self.logger.debug(f"Failed to cleanup directory {directory}: {e}")
    


    def get_installation_summary(self, profile_name: str, target: str = "auto") -> Optional[Dict]:
        """
        Get a summary of what would be installed with enhanced information.
        
        Args:
            profile_name: Name of profile
            target: Target system
            
        Returns:
            Dictionary with installation summary or None if profile not found
        """
        try:
            # Find profile in library
            profile_dir = self.library_path / profile_name
            if not profile_dir.exists():
                self.logger.debug(f"Profile directory not found: {profile_dir}")
                return None
            
            # Load profile
            try:
                profile = Profile.from_yaml(profile_dir / "profile.yaml")
            except Exception as e:
                self.logger.warning(f"Failed to load profile {profile_name}: {e}")
                return None
            
            # Detect target paths
            target_paths = self.detect_target_paths(target)
            
            # Check if already installed
            manifest = self.load_installation_manifest()
            is_installed = profile_name in manifest
            installed_version = manifest[profile_name].version if is_installed else None
            
            # Calculate file counts
            context_count = len(profile.contexts) if profile.contexts else 0
            hook_count = len(profile.hooks) if profile.hooks else 0
            
            return {
                "profile_name": profile_name,
                "version": profile.version,
                "description": profile.description,
                "author": profile.author,
                "category": profile.category,
                "tags": profile.tags,
                "contexts": profile.contexts,
                "hooks": profile.hooks,
                "context_count": context_count,
                "hook_count": hook_count,
                "target_available": target_paths is not None,
                "target_paths": target_paths,
                "dependencies": profile.dependencies,
                "is_installed": is_installed,
                "installed_version": installed_version,
                "needs_update": is_installed and installed_version != profile.version,
                "storage_path": str(self.independent_storage)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get installation summary for {profile_name}: {e}")
            return None
    
    def get_installation_health(self) -> Dict[str, Any]:
        """
        Get health status of the installation system.
        
        Returns:
            Dictionary with health information
        """
        try:
            health = {
                "status": "healthy",
                "issues": [],
                "warnings": [],
                "storage_path": str(self.independent_storage),
                "storage_exists": self.independent_storage.exists(),
                "manifest_exists": self.installation_manifest_path.exists(),
                "installed_profiles": 0,
                "storage_size_mb": 0,
                "last_check": datetime.now().isoformat()
            }
            
            # Check storage directory
            if not self.independent_storage.exists():
                health["status"] = "unhealthy"
                health["issues"].append("Independent storage directory does not exist")
            else:
                # Calculate storage size
                try:
                    total_size = sum(f.stat().st_size for f in self.independent_storage.rglob('*') if f.is_file())
                    health["storage_size_mb"] = round(total_size / (1024 * 1024), 2)
                except Exception:
                    health["warnings"].append("Could not calculate storage size")
            
            # Check manifest
            if self.installation_manifest_path.exists():
                try:
                    manifest = self.load_installation_manifest()
                    health["installed_profiles"] = len(manifest)
                    
                    # Check for broken installations
                    broken_profiles = []
                    for profile_name, installed_profile in manifest.items():
                        missing_files = []
                        for file_path in installed_profile.files:
                            if not Path(file_path).exists():
                                missing_files.append(file_path)
                        
                        if missing_files:
                            broken_profiles.append({
                                "profile": profile_name,
                                "missing_files": missing_files
                            })
                    
                    if broken_profiles:
                        health["status"] = "degraded"
                        health["issues"].extend([
                            f"Profile {bp['profile']} has missing files: {', '.join(bp['missing_files'])}"
                            for bp in broken_profiles
                        ])
                        
                except Exception as e:
                    health["status"] = "unhealthy"
                    health["issues"].append(f"Failed to load manifest: {e}")
            
            # Check target availability
            targets_available = []
            for target in ["kiro", "amazonq"]:
                if self.detect_target_paths(target):
                    targets_available.append(target)
            
            health["targets_available"] = targets_available
            
            if not targets_available:
                health["warnings"].append("No installation targets detected")
            
            return health
            
        except Exception as e:
            return {
                "status": "error",
                "issues": [f"Health check failed: {e}"],
                "warnings": [],
                "last_check": datetime.now().isoformat()
            }