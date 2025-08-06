"""
Configuration catalog generator that scans the library directory and creates catalog.json.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import logging

try:
    from .catalog_schema import (
        LibraryCatalog, CatalogCategories, ConfigItem, PersonaInfo, 
        ConfigMetadata, CompatibilityInfo, UsageStats
    )
except ImportError:
    # For standalone execution
    from catalog_schema import (
        LibraryCatalog, CatalogCategories, ConfigItem, PersonaInfo, 
        ConfigMetadata, CompatibilityInfo, UsageStats
    )

logger = logging.getLogger(__name__)


class CatalogGenerator:
    """Generates catalog.json from library directory structure."""
    
    def __init__(self, library_path: str = "library"):
        self.library_path = Path(library_path)
        self.catalog = LibraryCatalog()
        self.personas_found: Set[str] = set()
        
    def generate_catalog(self) -> LibraryCatalog:
        """Generate complete catalog from library directory."""
        logger.info(f"Generating catalog from {self.library_path}")
        
        # Reset catalog
        self.catalog = LibraryCatalog()
        self.personas_found = set()
        
        # Scan each category
        self._scan_contexts()
        self._scan_profiles()
        self._scan_hooks()
        self._scan_mcp_servers()
        
        # Generate persona information
        self._generate_persona_info()
        
        # Update metadata
        self.catalog.last_updated = datetime.now().isoformat()
        self.catalog.total_configs = self._count_total_configs()
        
        logger.info(f"Generated catalog with {self.catalog.total_configs} configurations")
        return self.catalog
    
    def save_catalog(self, output_path: Optional[str] = None) -> str:
        """Save catalog to JSON file."""
        if output_path is None:
            output_path = self.library_path / "catalog.json"
        else:
            output_path = Path(output_path)
            
        # Convert to dict for JSON serialization
        catalog_dict = self.catalog.model_dump()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_dict, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Catalog saved to {output_path}")
        return str(output_path)
    
    def _scan_contexts(self):
        """Scan contexts directory."""
        contexts_path = self.library_path / "contexts"
        if not contexts_path.exists():
            return
            
        for domain_dir in contexts_path.iterdir():
            if not domain_dir.is_dir():
                continue
                
            domain_name = domain_dir.name
            domain_configs = []
            
            for config_file in domain_dir.glob("*.md"):
                config_item = self._parse_config_file(config_file, "contexts")
                if config_item:
                    domain_configs.append(config_item)
                    self.personas_found.update(config_item.personas)
            
            if domain_configs:
                self.catalog.categories.contexts[domain_name] = domain_configs
    
    def _scan_profiles(self):
        """Scan profiles directory."""
        profiles_path = self.library_path / "profiles"
        if not profiles_path.exists():
            return
            
        complete_configs = []
        
        for config_file in profiles_path.glob("*.yaml"):
            config_item = self._parse_config_file(config_file, "profiles")
            if config_item:
                complete_configs.append(config_item)
                self.personas_found.update(config_item.personas)
        
        if complete_configs:
            self.catalog.categories.profiles["complete"] = complete_configs
    
    def _scan_hooks(self):
        """Scan hooks directory."""
        hooks_path = self.library_path / "hooks"
        if not hooks_path.exists():
            return
            
        for category_dir in hooks_path.iterdir():
            if not category_dir.is_dir():
                continue
                
            category_name = category_dir.name
            category_configs = []
            
            for config_file in category_dir.glob("*.yaml"):
                config_item = self._parse_config_file(config_file, "hooks")
                if config_item:
                    category_configs.append(config_item)
                    self.personas_found.update(config_item.personas)
            
            if category_configs:
                self.catalog.categories.hooks[category_name] = category_configs
    
    def _scan_mcp_servers(self):
        """Scan mcp-servers directory."""
        mcp_path = self.library_path / "mcp-servers"
        if not mcp_path.exists():
            return
            
        for config_file in mcp_path.glob("*.json"):
            # Determine category from filename
            category_name = config_file.stem
            config_item = self._parse_config_file(config_file, "mcp-servers")
            
            if config_item:
                if category_name not in self.catalog.categories.mcp_servers:
                    self.catalog.categories.mcp_servers[category_name] = []
                self.catalog.categories.mcp_servers[category_name].append(config_item)
                self.personas_found.update(config_item.personas)
    
    def _parse_config_file(self, file_path: Path, category: str) -> Optional[ConfigItem]:
        """Parse a configuration file and extract metadata."""
        try:
            metadata = self._extract_metadata(file_path)
            if not metadata:
                logger.warning(f"No metadata found in {file_path}")
                return None
            
            # Create relative path from library root
            relative_path = file_path.relative_to(self.library_path)
            
            config_item = ConfigItem(
                id=metadata.get("id", f"{file_path.stem}-v1"),
                name=metadata.get("name", file_path.stem.replace("-", " ").title()),
                file_path=str(relative_path),
                personas=metadata.get("personas", []),
                version=metadata.get("version", "1.0.0"),
                downloads=metadata.get("usage_stats", {}).get("downloads", 0),
                rating=metadata.get("usage_stats", {}).get("rating", 0.0),
                dependencies=metadata.get("dependencies", []),
                domains=metadata.get("domains", []),
                tags=metadata.get("tags", []),
                description=metadata.get("description", ""),
                author=metadata.get("author", ""),
            )
            
            # Add compatibility info if available
            if "compatibility" in metadata:
                config_item.compatibility = CompatibilityInfo(**metadata["compatibility"])
            
            return config_item
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter metadata from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix == '.md':
                # Extract YAML frontmatter from markdown
                if content.startswith('---\n'):
                    parts = content.split('---\n', 2)
                    if len(parts) >= 2:
                        yaml_content = parts[1]
                        return yaml.safe_load(yaml_content)
            
            elif file_path.suffix in ['.yaml', '.yml']:
                # Parse YAML file - check for frontmatter first
                if content.startswith('---\n'):
                    parts = content.split('---\n', 2)
                    if len(parts) >= 2:
                        yaml_content = parts[1]
                        return yaml.safe_load(yaml_content)
                else:
                    # Try to parse entire file as YAML
                    data = yaml.safe_load(content)
                    # Check if it has metadata structure
                    if isinstance(data, dict) and 'id' in data:
                        return data
            
            elif file_path.suffix == '.json':
                # For JSON files, try to find metadata in the structure
                data = json.loads(content)
                if isinstance(data, dict):
                    # Look for metadata at root level or in a metadata key
                    if 'id' in data:
                        return data
                    elif 'metadata' in data:
                        return data['metadata']
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def _generate_persona_info(self):
        """Generate persona information based on found personas."""
        # Default persona descriptions
        persona_descriptions = {
            "developer": {
                "name": "Developer",
                "description": "Software developers and engineers working on applications and systems"
            },
            "solutions-architect": {
                "name": "Solutions Architect", 
                "description": "Technical architects designing and implementing cloud solutions"
            },
            "engagement-manager": {
                "name": "Engagement Manager",
                "description": "Project managers and engagement leads managing client relationships and delivery"
            },
            "general-user": {
                "name": "General User",
                "description": "General users looking for basic AI configuration"
            },
            "devops-engineer": {
                "name": "DevOps Engineer",
                "description": "Engineers focused on deployment, infrastructure, and operational excellence"
            },
            "network-admin": {
                "name": "Network Administrator",
                "description": "IT professionals managing network infrastructure and troubleshooting"
            },
            "content-creator": {
                "name": "Content Creator",
                "description": "Writers, bloggers, and content producers creating digital content"
            },
            "researcher": {
                "name": "Researcher",
                "description": "Academic and industry researchers conducting studies and analysis"
            }
        }
        
        for persona in self.personas_found:
            # Find recommended configs for this persona
            recommended_configs = self._find_recommended_configs(persona)
            
            persona_info = PersonaInfo(
                name=persona_descriptions.get(persona, {}).get("name", persona.replace("-", " ").title()),
                description=persona_descriptions.get(persona, {}).get("description", f"Configurations for {persona}"),
                recommended_configs=recommended_configs
            )
            
            self.catalog.personas[persona] = persona_info
    
    def _find_recommended_configs(self, persona: str) -> List[str]:
        """Find recommended configurations for a persona."""
        recommended = []
        
        # Look for profile configurations first
        for category_configs in self.catalog.categories.profiles.values():
            for config in category_configs:
                if persona in config.personas:
                    recommended.append(config.id)
        
        # Add key context configurations
        for category_configs in self.catalog.categories.contexts.values():
            for config in category_configs:
                if persona in config.personas and len(config.personas) <= 2:  # More specific configs
                    recommended.append(config.id)
        
        # Add specialized hooks
        for category_configs in self.catalog.categories.hooks.values():
            for config in category_configs:
                if persona in config.personas:
                    recommended.append(config.id)
        
        # Limit to top recommendations
        return recommended[:5]
    
    def _count_total_configs(self) -> int:
        """Count total number of configurations."""
        total = 0
        
        for category_dict in [
            self.catalog.categories.contexts,
            self.catalog.categories.profiles, 
            self.catalog.categories.hooks,
            self.catalog.categories.mcp_servers
        ]:
            for config_list in category_dict.values():
                total += len(config_list)
        
        return total


def generate_catalog_cli(library_path: str = "library", output_path: Optional[str] = None) -> str:
    """CLI function to generate catalog."""
    generator = CatalogGenerator(library_path)
    catalog = generator.generate_catalog()
    return generator.save_catalog(output_path)


if __name__ == "__main__":
    import sys
    
    library_path = sys.argv[1] if len(sys.argv) > 1 else "library"
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result_path = generate_catalog_cli(library_path, output_path)
    print(f"Catalog generated: {result_path}")