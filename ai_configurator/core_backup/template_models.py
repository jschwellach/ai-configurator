"""Base template classes and interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from enum import Enum


class TemplateCategory(Enum):
    """Template category enumeration."""
    BASIC = "basic"
    PROFESSIONAL = "professional" 
    ADVANCED = "advanced"


class TemplateComplexity(Enum):
    """Template complexity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TemplateType(Enum):
    """Template type enumeration."""
    PROFILE = "profile"
    CONTEXT = "context"
    HOOK = "hook"
    WORKFLOW = "workflow"


@dataclass
class TemplateMetadata:
    """Template metadata structure."""
    name: str
    description: str
    category: TemplateCategory
    version: str
    author: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    complexity: Optional[TemplateComplexity] = None
    prerequisites: List[str] = field(default_factory=list)
    related_templates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        result = {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version
        }
        
        if self.author:
            result["author"] = self.author
        if self.created:
            result["created"] = self.created
        if self.updated:
            result["updated"] = self.updated
        if self.tags:
            result["tags"] = self.tags
        if self.complexity:
            result["complexity"] = self.complexity.value
        if self.prerequisites:
            result["prerequisites"] = self.prerequisites
        if self.related_templates:
            result["related_templates"] = self.related_templates
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create metadata from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            category=TemplateCategory(data["category"]),
            version=data["version"],
            author=data.get("author"),
            created=data.get("created"),
            updated=data.get("updated"),
            tags=data.get("tags", []),
            complexity=TemplateComplexity(data["complexity"]) if data.get("complexity") else None,
            prerequisites=data.get("prerequisites", []),
            related_templates=data.get("related_templates", [])
        )


@dataclass
class TemplateInfo:
    """Template information structure."""
    name: str
    path: Path
    template_type: TemplateType
    metadata: TemplateMetadata
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate template info after initialization."""
        if not self.path.exists():
            raise FileNotFoundError(f"Template file does not exist: {self.path}")


class BaseTemplate(ABC):
    """Abstract base class for all templates."""
    
    def __init__(self, metadata: TemplateMetadata, file_path: Optional[Path] = None):
        self.metadata = metadata
        self.file_path = file_path
        self._content: Optional[Any] = None
        
    @property
    def name(self) -> str:
        """Get template name."""
        return self.metadata.name
        
    @property
    def description(self) -> str:
        """Get template description."""
        return self.metadata.description
        
    @property
    def category(self) -> TemplateCategory:
        """Get template category."""
        return self.metadata.category
        
    @property
    def template_type(self) -> TemplateType:
        """Get template type."""
        return self._get_template_type()
        
    @abstractmethod
    def _get_template_type(self) -> TemplateType:
        """Get the specific template type."""
        pass
        
    @abstractmethod
    def load_content(self) -> Any:
        """Load template content from file."""
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        """Validate template structure and content."""
        pass
        
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        pass
        
    def get_dependencies(self) -> List[str]:
        """Get template dependencies."""
        return self.metadata.prerequisites + self.metadata.related_templates


class ProfileTemplate(BaseTemplate):
    """Profile template implementation."""
    
    def __init__(self, metadata: TemplateMetadata, file_path: Optional[Path] = None,
                 paths: Optional[List[str]] = None, hooks: Optional[Dict[str, Any]] = None,
                 settings: Optional[Dict[str, Any]] = None):
        super().__init__(metadata, file_path)
        self.paths = paths or []
        self.hooks = hooks or {}
        self.settings = settings or {}
        
    def _get_template_type(self) -> TemplateType:
        return TemplateType.PROFILE
        
    def load_content(self) -> Dict[str, Any]:
        """Load profile content from JSON file."""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(f"Profile file not found: {self.file_path}")
            
        import json
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            
        self.paths = content.get("paths", [])
        self.hooks = content.get("hooks", {})
        self.settings = content.get("settings", {})
        self._content = content
        
        return content
        
    def validate(self) -> bool:
        """Validate profile template."""
        from .template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_profile_template(self.to_dict())
        return result.is_valid
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "paths": self.paths,
            "hooks": self.hooks,
            "settings": self.settings
        }


class ContextTemplate(BaseTemplate):
    """Context template implementation."""
    
    def __init__(self, metadata: TemplateMetadata, file_path: Optional[Path] = None,
                 content: Optional[str] = None, tags: Optional[List[str]] = None):
        super().__init__(metadata, file_path)
        self.content = content or ""
        self.tags = tags or []
        
    def _get_template_type(self) -> TemplateType:
        return TemplateType.CONTEXT
        
    def load_content(self) -> str:
        """Load context content from markdown file."""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(f"Context file not found: {self.file_path}")
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
            
        self._content = self.content
        return self.content
        
    def validate(self) -> bool:
        """Validate context template."""
        from .template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_context_template(self.to_dict())
        return result.is_valid
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "content": self.content,
            "tags": self.tags
        }


class HookTemplate(BaseTemplate):
    """Hook template implementation."""
    
    def __init__(self, metadata: TemplateMetadata, file_path: Optional[Path] = None,
                 name: Optional[str] = None, trigger: Optional[str] = None,
                 conditions: Optional[List[Dict[str, Any]]] = None,
                 actions: Optional[List[Dict[str, Any]]] = None):
        super().__init__(metadata, file_path)
        self.hook_name = name or metadata.name
        self.trigger = trigger or ""
        self.conditions = conditions or []
        self.actions = actions or []
        
    def _get_template_type(self) -> TemplateType:
        return TemplateType.HOOK
        
    def load_content(self) -> Dict[str, Any]:
        """Load hook content from YAML file."""
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(f"Hook file not found: {self.file_path}")
            
        import yaml
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            
        self.hook_name = content.get("name", self.metadata.name)
        self.trigger = content.get("trigger", "")
        self.conditions = content.get("conditions", [])
        self.actions = content.get("actions", [])
        self._content = content
        
        return content
        
    def validate(self) -> bool:
        """Validate hook template."""
        from .template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_hook_template(self.to_dict())
        return result.is_valid
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert hook to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "name": self.hook_name,
            "trigger": self.trigger,
            "conditions": self.conditions,
            "actions": self.actions
        }


@dataclass
class TemplateRegistry:
    """Registry for managing templates."""
    templates: Dict[str, TemplateInfo] = field(default_factory=dict)
    categories: Dict[str, List[str]] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    
    def register_template(self, template_info: TemplateInfo) -> None:
        """Register a template in the registry."""
        self.templates[template_info.name] = template_info
        
        # Update categories
        category = template_info.metadata.category.value
        if category not in self.categories:
            self.categories[category] = []
        if template_info.name not in self.categories[category]:
            self.categories[category].append(template_info.name)
            
        # Update relationships
        if template_info.metadata.related_templates:
            self.relationships[template_info.name] = template_info.metadata.related_templates
            
    def get_template(self, name: str) -> Optional[TemplateInfo]:
        """Get template by name."""
        return self.templates.get(name)
        
    def get_templates_by_category(self, category: TemplateCategory) -> List[TemplateInfo]:
        """Get all templates in a category."""
        template_names = self.categories.get(category.value, [])
        return [self.templates[name] for name in template_names if name in self.templates]
        
    def get_templates_by_type(self, template_type: TemplateType) -> List[TemplateInfo]:
        """Get all templates of a specific type."""
        return [info for info in self.templates.values() 
                if info.template_type == template_type]
        
    def get_related_templates(self, template_name: str) -> List[TemplateInfo]:
        """Get templates related to the given template."""
        related_names = self.relationships.get(template_name, [])
        return [self.templates[name] for name in related_names if name in self.templates]