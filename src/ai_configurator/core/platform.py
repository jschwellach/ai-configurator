"""Platform-specific utilities and path management."""

import platform
import shutil
from pathlib import Path
from typing import Optional

import platformdirs


class PlatformManager:
    """Manages platform-specific operations and paths."""
    
    def __init__(self) -> None:
        self._platform = platform.system().lower()
        self._home = Path.home()
    
    def get_platform_name(self) -> str:
        """Get the current platform name."""
        return self._platform.title()
    
    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return self._platform == "windows"
    
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self._platform == "darwin"
    
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self._platform == "linux"
    
    def get_amazonq_config_dir(self) -> Path:
        """Get the Amazon Q CLI configuration directory."""
        if self.is_windows():
            # Windows: %USERPROFILE%\.aws\amazonq
            return self._home / ".aws" / "amazonq"
        else:
            # macOS/Linux: ~/.aws/amazonq
            return self._home / ".aws" / "amazonq"
    
    def get_app_data_dir(self) -> Path:
        """Get the application data directory for AI Configurator."""
        return Path(platformdirs.user_data_dir("ai-configurator", "ai-configurator"))
    
    def get_app_config_dir(self) -> Path:
        """Get the application configuration directory for AI Configurator."""
        return Path(platformdirs.user_config_dir("ai-configurator", "ai-configurator"))
    
    def get_app_cache_dir(self) -> Path:
        """Get the application cache directory for AI Configurator."""
        return Path(platformdirs.user_cache_dir("ai-configurator", "ai-configurator"))
    
    def is_amazonq_installed(self) -> bool:
        """Check if Amazon Q CLI is installed and accessible."""
        return shutil.which("q") is not None
    
    def get_amazonq_version(self) -> Optional[str]:
        """Get the installed Amazon Q CLI version."""
        import subprocess
        
        try:
            result = subprocess.run(
                ["q", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output (format may vary)
                return result.stdout.strip()
            return None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        directories = [
            self.get_app_data_dir(),
            self.get_app_config_dir(),
            self.get_app_cache_dir(),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_shell_type(self) -> str:
        """Detect the current shell type."""
        import os
        
        shell = os.environ.get("SHELL", "")
        if "bash" in shell:
            return "bash"
        elif "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        elif self.is_windows():
            # Check for PowerShell vs Command Prompt
            if os.environ.get("PSModulePath"):
                return "powershell"
            else:
                return "cmd"
        else:
            return "unknown"
    
    def get_executable_extension(self) -> str:
        """Get the executable file extension for the current platform."""
        return ".exe" if self.is_windows() else ""
    
    def get_script_extension(self) -> str:
        """Get the script file extension for the current platform."""
        if self.is_windows():
            shell = self.get_shell_type()
            if shell == "powershell":
                return ".ps1"
            else:
                return ".bat"
        else:
            return ".sh"
