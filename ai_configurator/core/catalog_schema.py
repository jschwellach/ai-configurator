"""
Simplified catalog schema for AI Configurator library.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class ConfigItem(BaseModel):
    """Simplified configuration item."""
    id: str
    name: str
    description: str
    version: str
    file_path: str


class LibraryCatalog(BaseModel):
    """Simplified library catalog structure."""
    version: str = "1.0.0"
    profiles: List[ConfigItem] = Field(default_factory=list)


# JSON Schema for validation
CATALOG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Configuration Library Catalog",
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "profiles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "version": {"type": "string"},
                    "file_path": {"type": "string"}
                },
                "required": ["id", "name", "description", "version", "file_path"]
            }
        }
    },
    "required": ["version", "profiles"]
}
