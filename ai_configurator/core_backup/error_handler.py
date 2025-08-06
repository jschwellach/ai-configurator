"""
Robust error handling and recovery system for the library marketplace architecture.
Provides comprehensive error handling for network issues, file system problems, and validation failures.
"""

import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Type
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from contextlib import contextmanager
import traceback
import time

from .models import ConfigurationError, ValidationReport, InstallationOperation


logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can occur in the system."""
    NETWORK_ERROR = "network_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    VALIDATION_ERROR = "validation_error"
    DEPENDENCY_ERROR = "dependency_error"
    PERMISSION_ERROR = "permission_error"
    CONFIGURATION_ERROR = "configuration_error"
    INSTALLATION_ERROR = "installation_error"
    ROLLBACK_ERROR = "rollback_error"
    CRITICAL_ERROR = "critical_error"


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(str, Enum):
    """Types of recovery actions that can be taken."""
    RETRY = "retry"
    ROLLBACK = "rollback"
    SKIP = "skip"
    ABORT = "abort"
    MANUAL_INTERVENTION = "manual_intervention"
    ALTERNATIVE_PATH = "alternative_path"


@dataclass
class ErrorContext:
    """Context information for an error."""
    operation: str
    file_path: Optional[str] = None
    config_id: Optional[str] = None
    user_action: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RecoveryStrategy:
    """Strategy for recovering from an error."""
    action: RecoveryAction
    description: str
    auto_execute: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0
    rollback_steps: List[str] = field(default_factory=list)
    user_message: Optional[str] = None
    suggested_solutions: List[str] = field(default_factory=list)


@dataclass
class ErrorRecord:
    """Record of an error that occurred."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    context: ErrorContext
    exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    recovery_strategy: Optional[RecoveryStrategy] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ConfigurationErrorHandler:
    """
    Comprehensive error handler for configuration operations.
    
    Provides error classification, recovery strategies, and rollback capabilities.
    """
    
    def __init__(self, backup_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the error handler.
        
        Args:
            backup_dir: Directory for storing backups during operations
        """
        self.backup_dir = Path(backup_dir) if backup_dir else Path.home() / ".kiro" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.error_log: List[ErrorRecord] = []
        self.operation_stack: List[Dict[str, Any]] = []
        self.rollback_handlers: Dict[str, Callable] = {}
        
        # Register default rollback handlers
        self._register_default_rollback_handlers()
    
    def handle_error(self, error: Exception, context: ErrorContext) -> RecoveryStrategy:
        """
        Handle an error and determine recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            Recovery strategy for the error
        """
        try:
            # Classify the error
            error_type, severity = self._classify_error(error, context)
            
            # Create error record
            error_record = ErrorRecord(
                error_type=error_type,
                severity=severity,
                message=str(error),
                context=context,
                exception=error,
                stack_trace=traceback.format_exc()
            )
            
            # Determine recovery strategy
            recovery_strategy = self._determine_recovery_strategy(error_record)
            error_record.recovery_strategy = recovery_strategy
            
            # Log the error
            self.error_log.append(error_record)
            self._log_error(error_record)
            
            return recovery_strategy
            
        except Exception as handler_error:
            logger.critical(f"Error in error handler: {handler_error}")
            # Fallback strategy
            return RecoveryStrategy(
                action=RecoveryAction.ABORT,
                description="Critical error in error handler - aborting operation",
                user_message="A critical error occurred. Please check the logs and try again.",
                suggested_solutions=[
                    "Check system logs for more details",
                    "Ensure sufficient disk space and permissions",
                    "Contact support if the problem persists"
                ]
            )
    
    def execute_recovery(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """
        Execute a recovery strategy.
        
        Args:
            strategy: Recovery strategy to execute
            context: Context for the recovery operation
            
        Returns:
            True if recovery was successful, False otherwise
        """
        try:
            if strategy.action == RecoveryAction.RETRY:
                return self._execute_retry(strategy, context)
            elif strategy.action == RecoveryAction.ROLLBACK:
                return self._execute_rollback(strategy, context)
            elif strategy.action == RecoveryAction.SKIP:
                return self._execute_skip(strategy, context)
            elif strategy.action == RecoveryAction.ALTERNATIVE_PATH:
                return self._execute_alternative_path(strategy, context)
            elif strategy.action == RecoveryAction.ABORT:
                return self._execute_abort(strategy, context)
            elif strategy.action == RecoveryAction.MANUAL_INTERVENTION:
                return self._request_manual_intervention(strategy, context)
            else:
                logger.warning(f"Unknown recovery action: {strategy.action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing recovery strategy: {e}")
            return False
    
    @contextmanager
    def operation_context(self, operation_name: str, **kwargs):
        """
        Context manager for tracking operations and enabling rollback.
        
        Args:
            operation_name: Name of the operation
            **kwargs: Additional context information
        """
        operation_id = f"{operation_name}_{int(time.time())}"
        operation_info = {
            'id': operation_id,
            'name': operation_name,
            'start_time': datetime.now().isoformat(),
            'context': kwargs,
            'rollback_steps': []
        }
        
        self.operation_stack.append(operation_info)
        
        try:
            yield operation_info
            # Operation completed successfully
            operation_info['status'] = 'completed'
            operation_info['end_time'] = datetime.now().isoformat()
            
        except Exception as e:
            # Operation failed - prepare for rollback
            operation_info['status'] = 'failed'
            operation_info['error'] = str(e)
            operation_info['end_time'] = datetime.now().isoformat()
            
            # Create error context
            context = ErrorContext(
                operation=operation_name,
                file_path=kwargs.get('file_path'),
                config_id=kwargs.get('config_id'),
                user_action=kwargs.get('user_action'),
                system_state=kwargs
            )
            
            # Handle the error
            recovery_strategy = self.handle_error(e, context)
            
            # Execute recovery if auto-execute is enabled
            if recovery_strategy.auto_execute:
                recovery_success = self.execute_recovery(recovery_strategy, context)
                if not recovery_success:
                    logger.error(f"Recovery failed for operation {operation_name}")
            
            raise
        finally:
            # Clean up operation from stack
            if self.operation_stack and self.operation_stack[-1]['id'] == operation_id:
                self.operation_stack.pop()
    
    def add_rollback_step(self, operation_id: str, step_description: str, rollback_func: Callable, *args, **kwargs):
        """
        Add a rollback step for an operation.
        
        Args:
            operation_id: ID of the operation
            step_description: Description of the rollback step
            rollback_func: Function to call for rollback
            *args: Arguments for the rollback function
            **kwargs: Keyword arguments for the rollback function
        """
        if self.operation_stack:
            current_op = self.operation_stack[-1]
            if current_op['id'] == operation_id:
                rollback_step = {
                    'description': step_description,
                    'function': rollback_func,
                    'args': args,
                    'kwargs': kwargs,
                    'timestamp': datetime.now().isoformat()
                }
                current_op['rollback_steps'].append(rollback_step)
    
    def create_backup(self, source_path: Union[str, Path], backup_name: Optional[str] = None) -> Path:
        """
        Create a backup of a file or directory.
        
        Args:
            source_path: Path to backup
            backup_name: Optional name for the backup
            
        Returns:
            Path to the created backup
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            if source_path.is_file():
                shutil.copy2(source_path, backup_path)
            else:
                shutil.copytree(source_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_backup(self, backup_path: Union[str, Path], target_path: Union[str, Path]) -> bool:
        """
        Restore a backup to the target location.
        
        Args:
            backup_path: Path to the backup
            target_path: Path where to restore the backup
            
        Returns:
            True if restore was successful, False otherwise
        """
        backup_path = Path(backup_path)
        target_path = Path(target_path)
        
        if not backup_path.exists():
            logger.error(f"Backup does not exist: {backup_path}")
            return False
        
        try:
            # Remove target if it exists
            if target_path.exists():
                if target_path.is_file():
                    target_path.unlink()
                else:
                    shutil.rmtree(target_path)
            
            # Restore from backup
            if backup_path.is_file():
                shutil.copy2(backup_path, target_path)
            else:
                shutil.copytree(backup_path, target_path)
            
            logger.info(f"Restored backup from {backup_path} to {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors that have occurred."""
        if not self.error_log:
            return {"total_errors": 0, "by_type": {}, "by_severity": {}}
        
        by_type = {}
        by_severity = {}
        resolved_count = 0
        
        for error in self.error_log:
            # Count by type
            error_type = error.error_type.value
            by_type[error_type] = by_type.get(error_type, 0) + 1
            
            # Count by severity
            severity = error.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count resolved
            if error.resolved:
                resolved_count += 1
        
        return {
            "total_errors": len(self.error_log),
            "resolved_errors": resolved_count,
            "unresolved_errors": len(self.error_log) - resolved_count,
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_errors": [
                {
                    "type": error.error_type.value,
                    "severity": error.severity.value,
                    "message": error.message,
                    "timestamp": error.timestamp
                }
                for error in self.error_log[-5:]  # Last 5 errors
            ]
        }
    
    def _classify_error(self, error: Exception, context: ErrorContext) -> tuple[ErrorType, ErrorSeverity]:
        """Classify an error by type and severity."""
        error_type = type(error)
        error_message = str(error).lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in ['connection', 'network', 'timeout', 'unreachable']):
            return ErrorType.NETWORK_ERROR, ErrorSeverity.MEDIUM
        
        # File system errors
        if issubclass(error_type, (FileNotFoundError, PermissionError, OSError, IOError)):
            if issubclass(error_type, PermissionError):
                return ErrorType.PERMISSION_ERROR, ErrorSeverity.HIGH
            return ErrorType.FILE_SYSTEM_ERROR, ErrorSeverity.MEDIUM
        
        # Validation errors
        if 'validation' in error_message or 'invalid' in error_message:
            return ErrorType.VALIDATION_ERROR, ErrorSeverity.LOW
        
        # Dependency errors
        if any(keyword in error_message for keyword in ['dependency', 'missing', 'not found']):
            return ErrorType.DEPENDENCY_ERROR, ErrorSeverity.MEDIUM
        
        # Configuration errors
        if any(keyword in error_message for keyword in ['config', 'yaml', 'json', 'parse']):
            return ErrorType.CONFIGURATION_ERROR, ErrorSeverity.MEDIUM
        
        # Installation errors
        if any(keyword in error_message for keyword in ['install', 'setup', 'deploy']):
            return ErrorType.INSTALLATION_ERROR, ErrorSeverity.HIGH
        
        # Default to critical for unknown errors
        return ErrorType.CRITICAL_ERROR, ErrorSeverity.CRITICAL
    
    def _determine_recovery_strategy(self, error_record: ErrorRecord) -> RecoveryStrategy:
        """Determine the appropriate recovery strategy for an error."""
        error_type = error_record.error_type
        severity = error_record.severity
        
        if error_type == ErrorType.NETWORK_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.RETRY,
                description="Retry operation after network issue",
                auto_execute=True,
                max_retries=3,
                retry_delay=2.0,
                user_message="Network issue detected. Retrying operation...",
                suggested_solutions=[
                    "Check your internet connection",
                    "Verify proxy settings if applicable",
                    "Try again in a few minutes"
                ]
            )
        
        elif error_type == ErrorType.FILE_SYSTEM_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.ALTERNATIVE_PATH,
                description="Try alternative file system operation",
                auto_execute=False,
                user_message="File system error occurred. Please check file permissions and disk space.",
                suggested_solutions=[
                    "Check file and directory permissions",
                    "Ensure sufficient disk space",
                    "Verify the target directory exists",
                    "Try running with elevated permissions if necessary"
                ]
            )
        
        elif error_type == ErrorType.PERMISSION_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.MANUAL_INTERVENTION,
                description="Permission error requires manual intervention",
                auto_execute=False,
                user_message="Permission denied. Please check file permissions or run with appropriate privileges.",
                suggested_solutions=[
                    "Check file and directory permissions",
                    "Run the command with sudo (Linux/macOS) or as Administrator (Windows)",
                    "Ensure you have write access to the target directory",
                    "Check if files are locked by another process"
                ]
            )
        
        elif error_type == ErrorType.VALIDATION_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.SKIP,
                description="Skip invalid configuration and continue",
                auto_execute=False,
                user_message="Configuration validation failed. Please fix the configuration or skip this item.",
                suggested_solutions=[
                    "Check the configuration file syntax",
                    "Verify all required fields are present",
                    "Ensure field values are in the correct format",
                    "Refer to the configuration documentation"
                ]
            )
        
        elif error_type == ErrorType.DEPENDENCY_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.ALTERNATIVE_PATH,
                description="Try to resolve or skip missing dependencies",
                auto_execute=False,
                user_message="Missing dependencies detected. Please install dependencies or choose alternative configurations.",
                suggested_solutions=[
                    "Install the missing dependencies manually",
                    "Choose a different configuration without these dependencies",
                    "Check if the dependency name is correct",
                    "Update the library catalog"
                ]
            )
        
        elif error_type == ErrorType.INSTALLATION_ERROR:
            return RecoveryStrategy(
                action=RecoveryAction.ROLLBACK,
                description="Rollback failed installation",
                auto_execute=True,
                user_message="Installation failed. Rolling back changes...",
                suggested_solutions=[
                    "Check the installation logs for details",
                    "Ensure all prerequisites are met",
                    "Try installing individual components",
                    "Clear any partial installations and retry"
                ]
            )
        
        elif severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy(
                action=RecoveryAction.ABORT,
                description="Critical error - abort operation",
                auto_execute=True,
                user_message="A critical error occurred. The operation has been aborted.",
                suggested_solutions=[
                    "Check system logs for more details",
                    "Ensure system requirements are met",
                    "Contact support if the problem persists",
                    "Try restarting the application"
                ]
            )
        
        else:
            # Default strategy
            return RecoveryStrategy(
                action=RecoveryAction.MANUAL_INTERVENTION,
                description="Unknown error - manual intervention required",
                auto_execute=False,
                user_message="An unexpected error occurred. Please review the error details and take appropriate action.",
                suggested_solutions=[
                    "Check the error message and logs for details",
                    "Verify system configuration",
                    "Try the operation again",
                    "Contact support if needed"
                ]
            )    

    def _execute_retry(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Execute retry recovery strategy."""
        for attempt in range(strategy.max_retries):
            try:
                logger.info(f"Retry attempt {attempt + 1}/{strategy.max_retries} for operation: {context.operation}")
                
                if attempt > 0:
                    time.sleep(strategy.retry_delay * attempt)  # Exponential backoff
                
                # The actual retry logic would be implemented by the calling code
                # This method just handles the retry mechanics
                return True
                
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
                if attempt == strategy.max_retries - 1:
                    logger.error(f"All retry attempts failed for operation: {context.operation}")
                    return False
        
        return False
    
    def _execute_rollback(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Execute rollback recovery strategy."""
        try:
            logger.info(f"Executing rollback for operation: {context.operation}")
            
            # Execute rollback steps in reverse order
            if self.operation_stack:
                current_op = self.operation_stack[-1]
                rollback_steps = current_op.get('rollback_steps', [])
                
                for step in reversed(rollback_steps):
                    try:
                        logger.info(f"Executing rollback step: {step['description']}")
                        step['function'](*step['args'], **step['kwargs'])
                    except Exception as e:
                        logger.error(f"Rollback step failed: {step['description']} - {e}")
                        # Continue with other rollback steps even if one fails
            
            # Execute strategy-specific rollback steps
            for step_description in strategy.rollback_steps:
                logger.info(f"Executing strategy rollback step: {step_description}")
                # The specific rollback logic would be implemented by the calling code
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback execution failed: {e}")
            return False
    
    def _execute_skip(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Execute skip recovery strategy."""
        logger.info(f"Skipping failed operation: {context.operation}")
        
        # Log the skip action
        skip_record = {
            'operation': context.operation,
            'reason': strategy.description,
            'timestamp': datetime.now().isoformat(),
            'context': context.__dict__
        }
        
        logger.info(f"Operation skipped: {skip_record}")
        return True
    
    def _execute_alternative_path(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Execute alternative path recovery strategy."""
        logger.info(f"Attempting alternative path for operation: {context.operation}")
        
        # The specific alternative path logic would be implemented by the calling code
        # This method just logs the attempt
        return True
    
    def _execute_abort(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Execute abort recovery strategy."""
        logger.error(f"Aborting operation: {context.operation}")
        
        # Perform any necessary cleanup
        try:
            # Execute any pending rollback steps
            self._execute_rollback(strategy, context)
        except Exception as e:
            logger.error(f"Error during abort cleanup: {e}")
        
        return False
    
    def _request_manual_intervention(self, strategy: RecoveryStrategy, context: ErrorContext) -> bool:
        """Request manual intervention from the user."""
        logger.warning(f"Manual intervention required for operation: {context.operation}")
        
        # In a real implementation, this would present options to the user
        # For now, we just log the request
        intervention_request = {
            'operation': context.operation,
            'message': strategy.user_message,
            'suggested_solutions': strategy.suggested_solutions,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Manual intervention requested: {intervention_request}")
        return False  # Requires user action
    
    def _register_default_rollback_handlers(self):
        """Register default rollback handlers for common operations."""
        self.rollback_handlers.update({
            'file_copy': self._rollback_file_copy,
            'file_move': self._rollback_file_move,
            'directory_create': self._rollback_directory_create,
            'config_install': self._rollback_config_install,
            'dependency_install': self._rollback_dependency_install
        })
    
    def _rollback_file_copy(self, source: str, destination: str):
        """Rollback a file copy operation."""
        try:
            dest_path = Path(destination)
            if dest_path.exists():
                dest_path.unlink()
                logger.info(f"Rolled back file copy: removed {destination}")
        except Exception as e:
            logger.error(f"Failed to rollback file copy: {e}")
    
    def _rollback_file_move(self, source: str, destination: str):
        """Rollback a file move operation."""
        try:
            dest_path = Path(destination)
            source_path = Path(source)
            
            if dest_path.exists() and not source_path.exists():
                shutil.move(str(dest_path), str(source_path))
                logger.info(f"Rolled back file move: {destination} -> {source}")
        except Exception as e:
            logger.error(f"Failed to rollback file move: {e}")
    
    def _rollback_directory_create(self, directory_path: str):
        """Rollback a directory creation operation."""
        try:
            dir_path = Path(directory_path)
            if dir_path.exists() and dir_path.is_dir():
                # Only remove if directory is empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.info(f"Rolled back directory creation: removed {directory_path}")
                else:
                    logger.warning(f"Cannot rollback directory creation: {directory_path} is not empty")
        except Exception as e:
            logger.error(f"Failed to rollback directory creation: {e}")
    
    def _rollback_config_install(self, config_id: str, target_path: str):
        """Rollback a configuration installation."""
        try:
            target = Path(target_path)
            if target.exists():
                if target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
                logger.info(f"Rolled back configuration install: removed {target_path}")
        except Exception as e:
            logger.error(f"Failed to rollback configuration install: {e}")
    
    def _rollback_dependency_install(self, dependency_id: str, install_path: str):
        """Rollback a dependency installation."""
        try:
            install_path_obj = Path(install_path)
            if install_path_obj.exists():
                if install_path_obj.is_file():
                    install_path_obj.unlink()
                else:
                    shutil.rmtree(install_path_obj)
                logger.info(f"Rolled back dependency install: removed {install_path}")
        except Exception as e:
            logger.error(f"Failed to rollback dependency install: {e}")
    
    def _log_error(self, error_record: ErrorRecord):
        """Log an error record."""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_record.severity, logging.ERROR)
        
        logger.log(
            log_level,
            f"Error in {error_record.context.operation}: {error_record.message} "
            f"[Type: {error_record.error_type.value}, Severity: {error_record.severity.value}]"
        )
        
        if error_record.stack_trace and error_record.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.debug(f"Stack trace: {error_record.stack_trace}")


class InstallationErrorHandler(ConfigurationErrorHandler):
    """
    Specialized error handler for installation operations.
    
    Provides installation-specific error handling and rollback capabilities.
    """
    
    def __init__(self, installation_dir: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the installation error handler.
        
        Args:
            installation_dir: Directory where configurations are installed
            backup_dir: Directory for storing backups
        """
        super().__init__(backup_dir)
        self.installation_dir = Path(installation_dir)
        self.installation_manifest: Dict[str, Any] = {}
        self.active_installations: List[str] = []
    
    def begin_installation(self, config_id: str, config_data: Dict[str, Any]) -> str:
        """
        Begin an installation operation with rollback tracking.
        
        Args:
            config_id: ID of the configuration being installed
            config_data: Configuration data
            
        Returns:
            Installation operation ID
        """
        operation_id = f"install_{config_id}_{int(time.time())}"
        
        # Create backup of existing configuration if it exists
        target_path = self.installation_dir / config_id
        backup_path = None
        
        if target_path.exists():
            try:
                backup_path = self.create_backup(target_path, f"{config_id}_pre_install")
            except Exception as e:
                logger.warning(f"Failed to create backup for {config_id}: {e}")
        
        # Track the installation
        installation_record = {
            'operation_id': operation_id,
            'config_id': config_id,
            'config_data': config_data,
            'target_path': str(target_path),
            'backup_path': str(backup_path) if backup_path else None,
            'start_time': datetime.now().isoformat(),
            'status': 'in_progress',
            'rollback_steps': []
        }
        
        self.installation_manifest[operation_id] = installation_record
        self.active_installations.append(operation_id)
        
        return operation_id
    
    def complete_installation(self, operation_id: str, success: bool = True):
        """
        Complete an installation operation.
        
        Args:
            operation_id: Installation operation ID
            success: Whether the installation was successful
        """
        if operation_id in self.installation_manifest:
            record = self.installation_manifest[operation_id]
            record['status'] = 'completed' if success else 'failed'
            record['end_time'] = datetime.now().isoformat()
            
            if operation_id in self.active_installations:
                self.active_installations.remove(operation_id)
            
            if success:
                logger.info(f"Installation completed successfully: {record['config_id']}")
            else:
                logger.error(f"Installation failed: {record['config_id']}")
    
    def rollback_installation(self, operation_id: str) -> bool:
        """
        Rollback a failed installation.
        
        Args:
            operation_id: Installation operation ID
            
        Returns:
            True if rollback was successful, False otherwise
        """
        if operation_id not in self.installation_manifest:
            logger.error(f"Installation record not found: {operation_id}")
            return False
        
        record = self.installation_manifest[operation_id]
        
        try:
            logger.info(f"Rolling back installation: {record['config_id']}")
            
            # Remove installed files
            target_path = Path(record['target_path'])
            if target_path.exists():
                if target_path.is_file():
                    target_path.unlink()
                else:
                    shutil.rmtree(target_path)
                logger.info(f"Removed installed files: {target_path}")
            
            # Restore backup if it exists
            backup_path = record.get('backup_path')
            if backup_path and Path(backup_path).exists():
                if self.restore_backup(backup_path, target_path):
                    logger.info(f"Restored backup for: {record['config_id']}")
                else:
                    logger.warning(f"Failed to restore backup for: {record['config_id']}")
            
            # Execute custom rollback steps
            for step in reversed(record.get('rollback_steps', [])):
                try:
                    step['function'](*step['args'], **step['kwargs'])
                    logger.info(f"Executed rollback step: {step['description']}")
                except Exception as e:
                    logger.error(f"Rollback step failed: {step['description']} - {e}")
            
            # Update record
            record['status'] = 'rolled_back'
            record['rollback_time'] = datetime.now().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for {record['config_id']}: {e}")
            record['status'] = 'rollback_failed'
            record['rollback_error'] = str(e)
            return False
    
    def rollback_all_active_installations(self) -> Dict[str, bool]:
        """
        Rollback all active installations.
        
        Returns:
            Dictionary mapping operation IDs to rollback success status
        """
        results = {}
        
        for operation_id in list(self.active_installations):
            results[operation_id] = self.rollback_installation(operation_id)
        
        return results
    
    def get_installation_status(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of an installation.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Installation status information or None if not found
        """
        for record in self.installation_manifest.values():
            if record['config_id'] == config_id:
                return {
                    'config_id': config_id,
                    'status': record['status'],
                    'start_time': record['start_time'],
                    'end_time': record.get('end_time'),
                    'has_backup': record.get('backup_path') is not None,
                    'rollback_available': record['status'] in ['completed', 'failed']
                }
        
        return None


def create_user_friendly_error_message(error_record: ErrorRecord) -> str:
    """
    Create a user-friendly error message from an error record.
    
    Args:
        error_record: Error record to format
        
    Returns:
        User-friendly error message
    """
    severity_emoji = {
        ErrorSeverity.LOW: "ℹ️",
        ErrorSeverity.MEDIUM: "⚠️",
        ErrorSeverity.HIGH: "❌",
        ErrorSeverity.CRITICAL: "🚨"
    }
    
    emoji = severity_emoji.get(error_record.severity, "❓")
    
    message_parts = [
        f"{emoji} {error_record.message}"
    ]
    
    if error_record.context.file_path:
        message_parts.append(f"File: {error_record.context.file_path}")
    
    if error_record.context.config_id:
        message_parts.append(f"Configuration: {error_record.context.config_id}")
    
    if error_record.recovery_strategy and error_record.recovery_strategy.user_message:
        message_parts.append(f"\n{error_record.recovery_strategy.user_message}")
    
    if error_record.recovery_strategy and error_record.recovery_strategy.suggested_solutions:
        message_parts.append("\nSuggested solutions:")
        for i, solution in enumerate(error_record.recovery_strategy.suggested_solutions, 1):
            message_parts.append(f"  {i}. {solution}")
    
    return "\n".join(message_parts)


# Decorator for automatic error handling
def handle_errors(error_handler: ConfigurationErrorHandler, operation_name: str):
    """
    Decorator for automatic error handling in functions.
    
    Args:
        error_handler: Error handler instance
        operation_name: Name of the operation for context
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            context = ErrorContext(
                operation=operation_name,
                user_action=f"call_{func.__name__}",
                system_state={'args': args, 'kwargs': kwargs}
            )
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                recovery_strategy = error_handler.handle_error(e, context)
                
                if recovery_strategy.auto_execute:
                    success = error_handler.execute_recovery(recovery_strategy, context)
                    if success and recovery_strategy.action == RecoveryAction.RETRY:
                        # Retry the function call
                        return func(*args, **kwargs)
                
                # Re-raise the exception if recovery didn't handle it
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    error_handler = ConfigurationErrorHandler()
    
    # Simulate an error
    try:
        raise FileNotFoundError("Configuration file not found")
    except Exception as e:
        context = ErrorContext(
            operation="load_configuration",
            file_path="/path/to/config.yaml",
            config_id="test-config"
        )
        
        strategy = error_handler.handle_error(e, context)
        print(f"Recovery strategy: {strategy.action.value}")
        print(f"Description: {strategy.description}")
        
        if strategy.suggested_solutions:
            print("Suggested solutions:")
            for solution in strategy.suggested_solutions:
                print(f"  - {solution}")