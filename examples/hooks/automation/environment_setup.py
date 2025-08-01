#!/usr/bin/env python3
"""
Environment setup hook script for AI Configurator.

This script automatically detects project requirements and sets up
the development environment with necessary tools and dependencies.
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import tempfile


class Platform(Enum):
    """Supported platforms."""
    LINUX = "linux"
    DARWIN = "darwin"  # macOS
    WINDOWS = "windows"


class SetupPhase(Enum):
    """Setup phases."""
    DETECT = "detect_environment"
    INSTALL = "install_dependencies"
    CONFIGURE = "configure_tools"
    WORKSPACE = "setup_workspace"
    VALIDATE = "validate_setup"


@dataclass
class EnvironmentInfo:
    """Information about detected environment."""
    languages: List[str]
    package_managers: List[str]
    tools: List[str]
    platform: Platform
    project_root: Path
    requirements: Dict[str, Any]


@dataclass
class SetupResult:
    """Result of setup operation."""
    phase: SetupPhase
    success: bool
    message: str
    details: Dict[str, Any]
    timestamp: str


class EnvironmentDetector:
    """Detects project environment and requirements."""
    
    def __init__(self, config: Dict[str, Any], project_root: Path):
        self.config = config
        self.project_root = project_root
        self.detection_config = config.get('environment_detection', {})
    
    def detect(self) -> EnvironmentInfo:
        """Detect environment requirements."""
        languages = []
        tools = []
        requirements = {}
        
        # Detect languages
        for lang, lang_config in self.detection_config.items():
            if self._detect_language(lang, lang_config):
                languages.append(lang)
                requirements[lang] = self._get_language_requirements(lang, lang_config)
        
        # Detect platform
        platform_name = platform.system().lower()
        if platform_name == "darwin":
            current_platform = Platform.DARWIN
        elif platform_name == "windows":
            current_platform = Platform.WINDOWS
        else:
            current_platform = Platform.LINUX
        
        # Get platform-specific package managers
        platform_config = self.config.get('platforms', {}).get(current_platform.value, {})
        package_managers = platform_config.get('package_managers', [])
        
        # Detect available package managers
        available_managers = []
        for manager in package_managers:
            if shutil.which(manager):
                available_managers.append(manager)
        
        return EnvironmentInfo(
            languages=languages,
            package_managers=available_managers,
            tools=tools,
            platform=current_platform,
            project_root=self.project_root,
            requirements=requirements
        )
    
    def _detect_language(self, language: str, lang_config: Dict[str, Any]) -> bool:
        """Check if a language is used in the project."""
        indicators = lang_config.get('indicators', [])
        
        for indicator in indicators:
            if list(self.project_root.rglob(indicator)):
                return True
        
        return False
    
    def _get_language_requirements(self, language: str, lang_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific requirements for a language."""
        requirements = {
            'version': lang_config.get('versions', [])[-1] if lang_config.get('versions') else None,
            'package_files': []
        }
        
        # Find package files
        indicators = lang_config.get('indicators', [])
        for indicator in indicators:
            files = list(self.project_root.rglob(indicator))
            requirements['package_files'].extend([str(f) for f in files])
        
        return requirements


class DependencyInstaller:
    """Installs project dependencies."""
    
    def __init__(self, config: Dict[str, Any], env_info: EnvironmentInfo):
        self.config = config
        self.env_info = env_info
        self.platform_config = config.get('platforms', {}).get(env_info.platform.value, {})
    
    def install_dependencies(self) -> List[SetupResult]:
        """Install all detected dependencies."""
        results = []
        
        for language in self.env_info.languages:
            result = self._install_language_dependencies(language)
            results.append(result)
        
        return results
    
    def _install_language_dependencies(self, language: str) -> SetupResult:
        """Install dependencies for a specific language."""
        try:
            print(f"Installing {language} dependencies...")
            
            if language == 'python':
                return self._install_python_dependencies()
            elif language == 'node':
                return self._install_node_dependencies()
            elif language == 'java':
                return self._install_java_dependencies()
            elif language == 'go':
                return self._install_go_dependencies()
            elif language == 'rust':
                return self._install_rust_dependencies()
            else:
                return SetupResult(
                    phase=SetupPhase.INSTALL,
                    success=False,
                    message=f"Unsupported language: {language}",
                    details={},
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=False,
                message=f"Error installing {language} dependencies: {e}",
                details={'error': str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def _install_python_dependencies(self) -> SetupResult:
        """Install Python dependencies."""
        details = {}
        
        # Check if Python is installed
        python_cmd = self.platform_config.get('python_command', 'python3')
        if not shutil.which(python_cmd):
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=False,
                message=f"Python not found. Please install Python first.",
                details={'python_command': python_cmd},
                timestamp=datetime.now().isoformat()
            )
        
        # Install pip if not available
        pip_cmd = self.platform_config.get('pip_command', 'pip3')
        if not shutil.which(pip_cmd):
            self._run_command([python_cmd, '-m', 'ensurepip', '--upgrade'])
        
        # Install from requirements files
        requirements_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'dev-requirements.txt'
        ]
        
        installed_files = []
        for req_file in requirements_files:
            req_path = self.env_info.project_root / req_file
            if req_path.exists():
                exit_code, stdout, stderr = self._run_command([
                    pip_cmd, 'install', '-r', str(req_path)
                ])
                if exit_code == 0:
                    installed_files.append(req_file)
                    details[req_file] = 'installed'
                else:
                    details[req_file] = f'failed: {stderr}'
        
        # Install from pyproject.toml
        pyproject_path = self.env_info.project_root / 'pyproject.toml'
        if pyproject_path.exists():
            exit_code, stdout, stderr = self._run_command([
                pip_cmd, 'install', '-e', '.'
            ], cwd=str(self.env_info.project_root))
            if exit_code == 0:
                installed_files.append('pyproject.toml')
                details['pyproject.toml'] = 'installed'
            else:
                details['pyproject.toml'] = f'failed: {stderr}'
        
        success = len(installed_files) > 0 or not any(
            (self.env_info.project_root / f).exists() for f in requirements_files + ['pyproject.toml']
        )
        
        return SetupResult(
            phase=SetupPhase.INSTALL,
            success=success,
            message=f"Python dependencies: {', '.join(installed_files) if installed_files else 'none found'}",
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def _install_node_dependencies(self) -> SetupResult:
        """Install Node.js dependencies."""
        details = {}
        
        # Check if Node.js is installed
        if not shutil.which('node'):
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=False,
                message="Node.js not found. Please install Node.js first.",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        package_json = self.env_info.project_root / 'package.json'
        if not package_json.exists():
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=True,
                message="No package.json found, skipping Node.js dependencies",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        # Determine package manager
        if (self.env_info.project_root / 'yarn.lock').exists() and shutil.which('yarn'):
            package_manager = 'yarn'
            install_cmd = ['yarn', 'install']
        elif (self.env_info.project_root / 'pnpm-lock.yaml').exists() and shutil.which('pnpm'):
            package_manager = 'pnpm'
            install_cmd = ['pnpm', 'install']
        else:
            package_manager = 'npm'
            install_cmd = ['npm', 'install']
        
        # Install dependencies
        exit_code, stdout, stderr = self._run_command(
            install_cmd, 
            cwd=str(self.env_info.project_root)
        )
        
        success = exit_code == 0
        details['package_manager'] = package_manager
        details['command'] = ' '.join(install_cmd)
        
        if not success:
            details['error'] = stderr
        
        return SetupResult(
            phase=SetupPhase.INSTALL,
            success=success,
            message=f"Node.js dependencies installed using {package_manager}",
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def _install_java_dependencies(self) -> SetupResult:
        """Install Java dependencies."""
        details = {}
        
        # Check for Maven
        if (self.env_info.project_root / 'pom.xml').exists():
            if shutil.which('mvn'):
                exit_code, stdout, stderr = self._run_command([
                    'mvn', 'dependency:resolve'
                ], cwd=str(self.env_info.project_root))
                
                success = exit_code == 0
                details['build_tool'] = 'maven'
                details['command'] = 'mvn dependency:resolve'
                
                if not success:
                    details['error'] = stderr
                
                return SetupResult(
                    phase=SetupPhase.INSTALL,
                    success=success,
                    message="Java dependencies resolved using Maven",
                    details=details,
                    timestamp=datetime.now().isoformat()
                )
        
        # Check for Gradle
        gradle_files = ['build.gradle', 'build.gradle.kts']
        for gradle_file in gradle_files:
            if (self.env_info.project_root / gradle_file).exists():
                gradle_cmd = './gradlew' if (self.env_info.project_root / 'gradlew').exists() else 'gradle'
                
                if shutil.which(gradle_cmd) or (self.env_info.project_root / 'gradlew').exists():
                    exit_code, stdout, stderr = self._run_command([
                        gradle_cmd, 'dependencies'
                    ], cwd=str(self.env_info.project_root))
                    
                    success = exit_code == 0
                    details['build_tool'] = 'gradle'
                    details['command'] = f'{gradle_cmd} dependencies'
                    
                    if not success:
                        details['error'] = stderr
                    
                    return SetupResult(
                        phase=SetupPhase.INSTALL,
                        success=success,
                        message="Java dependencies resolved using Gradle",
                        details=details,
                        timestamp=datetime.now().isoformat()
                    )
        
        return SetupResult(
            phase=SetupPhase.INSTALL,
            success=True,
            message="No Java build files found",
            details={},
            timestamp=datetime.now().isoformat()
        )
    
    def _install_go_dependencies(self) -> SetupResult:
        """Install Go dependencies."""
        if not (self.env_info.project_root / 'go.mod').exists():
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=True,
                message="No go.mod found, skipping Go dependencies",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        if not shutil.which('go'):
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=False,
                message="Go not found. Please install Go first.",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        exit_code, stdout, stderr = self._run_command([
            'go', 'mod', 'download'
        ], cwd=str(self.env_info.project_root))
        
        success = exit_code == 0
        details = {'command': 'go mod download'}
        
        if not success:
            details['error'] = stderr
        
        return SetupResult(
            phase=SetupPhase.INSTALL,
            success=success,
            message="Go dependencies downloaded",
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def _install_rust_dependencies(self) -> SetupResult:
        """Install Rust dependencies."""
        if not (self.env_info.project_root / 'Cargo.toml').exists():
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=True,
                message="No Cargo.toml found, skipping Rust dependencies",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        if not shutil.which('cargo'):
            return SetupResult(
                phase=SetupPhase.INSTALL,
                success=False,
                message="Cargo not found. Please install Rust first.",
                details={},
                timestamp=datetime.now().isoformat()
            )
        
        exit_code, stdout, stderr = self._run_command([
            'cargo', 'fetch'
        ], cwd=str(self.env_info.project_root))
        
        success = exit_code == 0
        details = {'command': 'cargo fetch'}
        
        if not success:
            details['error'] = stderr
        
        return SetupResult(
            phase=SetupPhase.INSTALL,
            success=success,
            message="Rust dependencies fetched",
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)


class WorkspaceSetup:
    """Sets up workspace structure and files."""
    
    def __init__(self, config: Dict[str, Any], env_info: EnvironmentInfo):
        self.config = config
        self.env_info = env_info
        self.workspace_config = config.get('workspace', {})
    
    def setup_workspace(self) -> SetupResult:
        """Set up workspace structure."""
        try:
            details = {}
            
            # Create directories
            directories = self.workspace_config.get('directories', [])
            created_dirs = []
            
            for directory in directories:
                dir_path = self.env_info.project_root / directory
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(directory)
            
            details['created_directories'] = created_dirs
            
            # Create files
            files = self.workspace_config.get('files', [])
            created_files = []
            
            for file_name in files:
                file_path = self.env_info.project_root / file_name
                if not file_path.exists():
                    self._create_template_file(file_name, file_path)
                    created_files.append(file_name)
            
            details['created_files'] = created_files
            
            return SetupResult(
                phase=SetupPhase.WORKSPACE,
                success=True,
                message=f"Workspace setup complete. Created {len(created_dirs)} directories and {len(created_files)} files.",
                details=details,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return SetupResult(
                phase=SetupPhase.WORKSPACE,
                success=False,
                message=f"Error setting up workspace: {e}",
                details={'error': str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def _create_template_file(self, file_name: str, file_path: Path) -> None:
        """Create a file from template."""
        templates = self.workspace_config.get('templates', {})
        
        if file_name == '.gitignore':
            content = self._generate_gitignore()
        elif file_name == 'README.md':
            content = self._generate_readme()
        elif file_name == '.editorconfig':
            content = self._generate_editorconfig()
        else:
            content = f"# {file_name}\n\n# This file was created by AI Configurator environment setup\n"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore content based on detected languages."""
        gitignore_content = "# AI Configurator generated .gitignore\n\n"
        
        # Common ignores
        gitignore_content += "# OS generated files\n"
        gitignore_content += ".DS_Store\n.DS_Store?\n._*\n.Spotlight-V100\n.Trashes\n"
        gitignore_content += "ehthumbs.db\nThumbs.db\n\n"
        
        # IDE ignores
        gitignore_content += "# IDE files\n"
        gitignore_content += ".vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n"
        
        # Language-specific ignores
        for language in self.env_info.languages:
            if language == 'python':
                gitignore_content += "# Python\n"
                gitignore_content += "__pycache__/\n*.py[cod]\n*$py.class\n"
                gitignore_content += "*.so\n.Python\nbuild/\ndevelop-eggs/\n"
                gitignore_content += "dist/\ndownloads/\neggs/\n.eggs/\n"
                gitignore_content += "lib/\nlib64/\nparts/\nsdist/\nvar/\n"
                gitignore_content += "wheels/\n*.egg-info/\n.installed.cfg\n"
                gitignore_content += "*.egg\nPYTHONPATH\n.env\n.venv\n"
                gitignore_content += "env/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n"
            
            elif language == 'node':
                gitignore_content += "# Node.js\n"
                gitignore_content += "node_modules/\nnpm-debug.log*\nyarn-debug.log*\n"
                gitignore_content += "yarn-error.log*\n.npm\n.eslintcache\n"
                gitignore_content += ".node_repl_history\n*.tgz\n.yarn-integrity\n"
                gitignore_content += ".env.local\n.env.development.local\n"
                gitignore_content += ".env.test.local\n.env.production.local\n\n"
            
            elif language == 'java':
                gitignore_content += "# Java\n"
                gitignore_content += "*.class\n*.log\n*.ctxt\n.mtj.tmp/\n"
                gitignore_content += "*.jar\n*.war\n*.nar\n*.ear\n*.zip\n"
                gitignore_content += "*.tar.gz\n*.rar\nhs_err_pid*\n"
                gitignore_content += "target/\n.mvn/\nmvnw\nmvnw.cmd\n"
                gitignore_content += ".gradle/\nbuild/\n!gradle/wrapper/gradle-wrapper.jar\n\n"
        
        return gitignore_content
    
    def _generate_readme(self) -> str:
        """Generate README.md content."""
        project_name = self.env_info.project_root.name
        
        readme_content = f"# {project_name}\n\n"
        readme_content += "## Description\n\n"
        readme_content += "This project was set up using AI Configurator.\n\n"
        
        if self.env_info.languages:
            readme_content += "## Technologies\n\n"
            for language in self.env_info.languages:
                readme_content += f"- {language.title()}\n"
            readme_content += "\n"
        
        readme_content += "## Setup\n\n"
        readme_content += "1. Clone the repository\n"
        readme_content += "2. Install dependencies (see language-specific instructions below)\n"
        readme_content += "3. Run the project\n\n"
        
        # Add language-specific setup instructions
        for language in self.env_info.languages:
            if language == 'python':
                readme_content += "### Python Setup\n\n"
                readme_content += "```bash\n"
                readme_content += "# Create virtual environment\n"
                readme_content += "python -m venv venv\n"
                readme_content += "source venv/bin/activate  # On Windows: venv\\Scripts\\activate\n\n"
                readme_content += "# Install dependencies\n"
                readme_content += "pip install -r requirements.txt\n"
                readme_content += "```\n\n"
            
            elif language == 'node':
                readme_content += "### Node.js Setup\n\n"
                readme_content += "```bash\n"
                readme_content += "# Install dependencies\n"
                readme_content += "npm install\n\n"
                readme_content += "# Run development server\n"
                readme_content += "npm run dev\n"
                readme_content += "```\n\n"
        
        readme_content += "## Contributing\n\n"
        readme_content += "Please read the contributing guidelines before making changes.\n\n"
        readme_content += "## License\n\n"
        readme_content += "This project is licensed under the MIT License.\n"
        
        return readme_content
    
    def _generate_editorconfig(self) -> str:
        """Generate .editorconfig content."""
        return """# EditorConfig is awesome: https://EditorConfig.org

# top-most EditorConfig file
root = true

# Unix-style newlines with a newline ending every file
[*]
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
charset = utf-8

# 4 space indentation
[*.{py,java,c,cpp,h,hpp}]
indent_style = space
indent_size = 4

# 2 space indentation
[*.{js,jsx,ts,tsx,json,yaml,yml,html,css,scss,md}]
indent_style = space
indent_size = 2

# Tab indentation (Makefiles)
[Makefile]
indent_style = tab

# Matches the exact files either package.json or .travis.yml
[{package.json,.travis.yml}]
indent_style = space
indent_size = 2
"""


class EnvironmentValidator:
    """Validates the setup environment."""
    
    def __init__(self, config: Dict[str, Any], env_info: EnvironmentInfo):
        self.config = config
        self.env_info = env_info
        self.validation_config = config.get('validation', {})
    
    def validate(self) -> SetupResult:
        """Validate the environment setup."""
        try:
            details = {}
            issues = []
            
            # Check commands
            commands = self.validation_config.get('commands', [])
            command_results = {}
            
            for command in commands:
                cmd_parts = command.split()
                exit_code, stdout, stderr = self._run_command(cmd_parts)
                
                success = exit_code == 0
                command_results[command] = {
                    'success': success,
                    'output': stdout.strip() if success else stderr.strip()
                }
                
                if not success:
                    issues.append(f"Command '{command}' failed")
            
            details['commands'] = command_results
            
            # Check environment variables
            env_vars = self.validation_config.get('environment_variables', [])
            env_var_results = {}
            
            for env_var in env_vars:
                value = os.environ.get(env_var)
                env_var_results[env_var] = {
                    'set': value is not None,
                    'value': value if value else 'Not set'
                }
                
                if not value:
                    issues.append(f"Environment variable '{env_var}' not set")
            
            details['environment_variables'] = env_var_results
            
            # Check directories
            directories = self.validation_config.get('directories', [])
            dir_results = {}
            
            for directory in directories:
                dir_path = self.env_info.project_root / directory
                exists = dir_path.exists() and dir_path.is_dir()
                dir_results[directory] = {'exists': exists}
                
                if not exists:
                    issues.append(f"Directory '{directory}' not found")
            
            details['directories'] = dir_results
            
            # Check files
            files = self.validation_config.get('files', [])
            file_results = {}
            
            for file_name in files:
                file_path = self.env_info.project_root / file_name
                exists = file_path.exists() and file_path.is_file()
                file_results[file_name] = {'exists': exists}
                
                if not exists:
                    issues.append(f"File '{file_name}' not found")
            
            details['files'] = file_results
            details['issues'] = issues
            
            success = len(issues) == 0
            message = "Environment validation passed" if success else f"Validation failed with {len(issues)} issues"
            
            return SetupResult(
                phase=SetupPhase.VALIDATE,
                success=success,
                message=message,
                details=details,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return SetupResult(
                phase=SetupPhase.VALIDATE,
                success=False,
                message=f"Error during validation: {e}",
                details={'error': str(e)},
                timestamp=datetime.now().isoformat()
            )
    
    def _run_command(self, command: List[str]) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)


class EnvironmentSetup:
    """Main class for environment setup."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
    
    def setup_environment(self, project_path: str) -> bool:
        """
        Set up the development environment.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            bool: True if setup was successful
        """
        try:
            project_root = Path(project_path).resolve()
            print(f"Setting up environment for: {project_root}")
            
            phases = self.config.get('phases', [
                'detect_environment',
                'install_dependencies', 
                'configure_tools',
                'setup_workspace',
                'validate_setup'
            ])
            
            # Phase 1: Detect environment
            if 'detect_environment' in phases:
                print("\n=== Phase 1: Detecting Environment ===")
                detector = EnvironmentDetector(self.config, project_root)
                env_info = detector.detect()
                
                print(f"Detected languages: {', '.join(env_info.languages)}")
                print(f"Platform: {env_info.platform.value}")
                print(f"Available package managers: {', '.join(env_info.package_managers)}")
            
            # Phase 2: Install dependencies
            if 'install_dependencies' in phases:
                print("\n=== Phase 2: Installing Dependencies ===")
                installer = DependencyInstaller(self.config, env_info)
                install_results = installer.install_dependencies()
                self.results.extend(install_results)
                
                for result in install_results:
                    status = "✓" if result.success else "✗"
                    print(f"{status} {result.message}")
            
            # Phase 3: Configure tools (placeholder)
            if 'configure_tools' in phases:
                print("\n=== Phase 3: Configuring Tools ===")
                print("Tool configuration completed")
            
            # Phase 4: Setup workspace
            if 'setup_workspace' in phases:
                print("\n=== Phase 4: Setting Up Workspace ===")
                workspace = WorkspaceSetup(self.config, env_info)
                workspace_result = workspace.setup_workspace()
                self.results.append(workspace_result)
                
                status = "✓" if workspace_result.success else "✗"
                print(f"{status} {workspace_result.message}")
            
            # Phase 5: Validate setup
            if 'validate_setup' in phases:
                print("\n=== Phase 5: Validating Setup ===")
                validator = EnvironmentValidator(self.config, env_info)
                validation_result = validator.validate()
                self.results.append(validation_result)
                
                status = "✓" if validation_result.success else "✗"
                print(f"{status} {validation_result.message}")
                
                if not validation_result.success:
                    print("Issues found:")
                    for issue in validation_result.details.get('issues', []):
                        print(f"  - {issue}")
            
            # Print summary
            self._print_summary()
            
            # Check overall success
            success = all(result.success for result in self.results)
            return success
            
        except Exception as e:
            print(f"Error during environment setup: {e}")
            return False
    
    def _print_summary(self) -> None:
        """Print setup summary."""
        print(f"\n{'='*50}")
        print("Environment Setup Summary")
        print(f"{'='*50}")
        
        successful = sum(1 for result in self.results if result.success)
        total = len(self.results)
        
        print(f"Phases completed: {successful}/{total}")
        
        for result in self.results:
            status = "✓" if result.success else "✗"
            print(f"{status} {result.phase.value}: {result.message}")
        
        overall_status = "SUCCESS" if successful == total else "PARTIAL SUCCESS"
        print(f"\nOverall Status: {overall_status}")
        print(f"{'='*50}\n")


def main():
    """Main entry point for the environment setup script."""
    parser = argparse.ArgumentParser(description='Set up development environment')
    parser.add_argument('--project-path', default='.', help='Path to project directory')
    parser.add_argument('--config', help='Path to hook configuration file')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            hook_config = yaml.safe_load(f)
            config = hook_config.get('config', {})
    
    # Set default configuration
    default_config = {
        'phases': [
            'detect_environment',
            'install_dependencies',
            'setup_workspace',
            'validate_setup'
        ],
        'environment_detection': {
            'python': {
                'indicators': ['requirements.txt', 'pyproject.toml', 'setup.py'],
                'versions': ['3.8', '3.9', '3.10', '3.11', '3.12']
            },
            'node': {
                'indicators': ['package.json'],
                'versions': ['16', '18', '20']
            }
        },
        'platforms': {
            'linux': {
                'package_managers': ['apt', 'yum', 'dnf'],
                'python_command': 'python3',
                'pip_command': 'pip3'
            },
            'darwin': {
                'package_managers': ['brew'],
                'python_command': 'python3',
                'pip_command': 'pip3'
            },
            'windows': {
                'package_managers': ['choco', 'winget'],
                'python_command': 'python',
                'pip_command': 'pip'
            }
        },
        'workspace': {
            'directories': ['src', 'tests', 'docs'],
            'files': ['.gitignore', 'README.md', '.editorconfig']
        },
        'validation': {
            'commands': ['python --version', 'git --version'],
            'directories': ['src'],
            'files': ['.gitignore', 'README.md']
        }
    }
    
    # Merge configurations
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
    
    # Set up environment
    setup = EnvironmentSetup(config)
    success = setup.setup_environment(args.project_path)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()