"""Tests for the MarkdownProcessor class."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime

import yaml

from src.ai_configurator.core.markdown_processor import MarkdownProcessor
from src.ai_configurator.core.models import ContextFile, ValidationReport


class TestMarkdownProcessor:
    """Test suite for MarkdownProcessor functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = MarkdownProcessor(base_path=self.temp_dir)
        
        # Create test directory structure
        self.contexts_dir = Path(self.temp_dir) / 'contexts'
        self.contexts_dir.mkdir(exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_frontmatter_with_valid_yaml(self):
        """Test parsing valid YAML frontmatter."""
        content = """---
title: Test Document
tags: [test, example]
priority: 5
---
# Main Content

This is the main content of the document.
"""
        
        frontmatter, markdown_content = self.processor.parse_frontmatter(content)
        
        assert frontmatter == {
            'title': 'Test Document',
            'tags': ['test', 'example'],
            'priority': 5
        }
        assert markdown_content.strip().startswith('# Main Content')
        assert 'This is the main content' in markdown_content
    
    def test_parse_frontmatter_without_frontmatter(self):
        """Test parsing content without frontmatter."""
        content = """# Regular Markdown

This document has no frontmatter.
"""
        
        frontmatter, markdown_content = self.processor.parse_frontmatter(content)
        
        assert frontmatter == {}
        assert markdown_content == content
    
    def test_parse_frontmatter_empty_frontmatter(self):
        """Test parsing with empty frontmatter."""
        content = """---
---
# Content Only

This has empty frontmatter.
"""
        
        frontmatter, markdown_content = self.processor.parse_frontmatter(content)
        
        assert frontmatter == {}
        assert markdown_content.strip().startswith('# Content Only')
    
    def test_parse_frontmatter_only(self):
        """Test parsing frontmatter-only content."""
        content = """---
title: Metadata Only
description: This file has only frontmatter
---"""
        
        frontmatter, markdown_content = self.processor.parse_frontmatter(content)
        
        assert frontmatter == {
            'title': 'Metadata Only',
            'description': 'This file has only frontmatter'
        }
        assert markdown_content == ""
    
    def test_parse_frontmatter_invalid_yaml(self):
        """Test parsing with invalid YAML frontmatter."""
        content = """---
title: Test
invalid: [unclosed list
---
# Content
"""
        
        with pytest.raises(yaml.YAMLError):
            self.processor.parse_frontmatter(content)
    
    def test_extract_metadata_comprehensive(self):
        """Test comprehensive metadata extraction."""
        content = """---
title: Test Document
tags: [ai, configuration]
priority: 3
author: Test Author
---
# Main Header

This is a test document with multiple elements.

## Sub Header

Here's some content with a [link](https://example.com).

```python
def example():
    return "code block"
```

### Another Header

More content here.
"""
        
        metadata = self.processor.extract_metadata(content)
        
        # Check basic metadata
        assert metadata['has_frontmatter'] is True
        assert metadata['title'] == 'Test Document'
        assert metadata['tags'] == ['ai', 'configuration']
        assert metadata['priority'] == 3
        assert metadata['author'] == 'Test Author'
        
        # Check content analysis
        assert metadata['header_count'] == 3
        assert 'Main Header' in metadata['headers']
        assert metadata['code_block_count'] == 1
        assert metadata['link_count'] == 1
        assert metadata['word_count'] > 0
        assert metadata['line_count'] > 0
    
    def test_load_context_file_success(self):
        """Test successful context file loading."""
        # Create test file
        test_file = self.contexts_dir / 'test-context.md'
        content = """---
title: Test Context
description: A test context file
tags: [test, context]
priority: 2
---
# Test Context

This is a test context for the AI system.

## Usage

Use this context for testing purposes.
"""
        
        test_file.write_text(content, encoding='utf-8')
        
        # Load the context file
        context_file = self.processor.load_context_file('contexts/test-context.md')
        
        # Verify the loaded context
        assert isinstance(context_file, ContextFile)
        assert context_file.file_path == 'contexts/test-context.md'
        assert context_file.content.strip().startswith('# Test Context')
        assert context_file.tags == ['test', 'context']
        assert context_file.priority == 2
        assert context_file.metadata['title'] == 'Test Context'
        assert context_file.last_modified is not None
    
    def test_load_context_file_not_found(self):
        """Test loading non-existent context file."""
        with pytest.raises(FileNotFoundError):
            self.processor.load_context_file('contexts/nonexistent.md')
    
    def test_load_context_file_caching(self):
        """Test context file caching functionality."""
        # Create test file
        test_file = self.contexts_dir / 'cached-test.md'
        content = """---
title: Cached Test
---
# Cached Content
"""
        
        test_file.write_text(content, encoding='utf-8')
        
        # Load file twice
        context1 = self.processor.load_context_file('contexts/cached-test.md')
        context2 = self.processor.load_context_file('contexts/cached-test.md')
        
        # Should be the same object due to caching
        assert context1.file_path == context2.file_path
        assert context1.content == context2.content
        
        # Check cache stats
        stats = self.processor.get_cache_stats()
        assert stats['cache_size'] == 1
        assert 'contexts/cached-test.md' in str(stats['cached_files'])
    
    def test_load_multiple_context_files(self):
        """Test loading multiple context files."""
        # Create multiple test files
        files_data = [
            ('context1.md', '---\ntitle: Context 1\n---\n# Context 1'),
            ('context2.md', '---\ntitle: Context 2\n---\n# Context 2'),
            ('context3.md', '# Context 3 (no frontmatter)'),
        ]
        
        file_paths = []
        for filename, content in files_data:
            file_path = self.contexts_dir / filename
            file_path.write_text(content, encoding='utf-8')
            file_paths.append(f'contexts/{filename}')
        
        # Load all files
        context_files = self.processor.load_multiple_context_files(file_paths)
        
        assert len(context_files) == 3
        assert all(isinstance(cf, ContextFile) for cf in context_files)
        
        # Check that files with frontmatter have metadata
        context1 = next(cf for cf in context_files if 'context1.md' in cf.file_path)
        assert context1.metadata['title'] == 'Context 1'
        
        context3 = next(cf for cf in context_files if 'context3.md' in cf.file_path)
        assert not context3.metadata['has_frontmatter']
    
    def test_discover_context_files(self):
        """Test context file discovery."""
        # Create test files in different subdirectories
        (self.contexts_dir / 'subdir').mkdir()
        
        files_to_create = [
            'context1.md',
            'context2.md',
            'subdir/nested-context.md',
        ]
        
        for file_path in files_to_create:
            full_path = self.contexts_dir / file_path
            full_path.write_text('# Test content', encoding='utf-8')
        
        # Discover files
        discovered = self.processor.discover_context_files()
        
        assert len(discovered) == 3
        assert 'contexts/context1.md' in discovered
        assert 'contexts/context2.md' in discovered
        assert 'contexts/subdir/nested-context.md' in discovered
    
    def test_validate_context_file_success(self):
        """Test successful context file validation."""
        # Create valid test file
        test_file = self.contexts_dir / 'valid-context.md'
        content = """---
title: Valid Context
description: A properly formatted context file
tags: [valid, test]
priority: 1
---
# Valid Context

This is a valid context file with proper structure.
"""
        
        test_file.write_text(content, encoding='utf-8')
        
        # Validate the file
        report = self.processor.validate_context_file('contexts/valid-context.md')
        
        assert report.is_valid is True
        assert len(report.errors) == 0
        assert len(report.info) >= 1  # Should have success message
        assert report.summary['errors'] == 0
    
    def test_validate_context_file_warnings(self):
        """Test context file validation with warnings."""
        # Create file with issues that generate warnings
        test_file = self.contexts_dir / 'warning-context.md'
        content = """---
tags: "should be a list"
priority: "should be an integer"
---
"""  # Empty content after frontmatter
        
        test_file.write_text(content, encoding='utf-8')
        
        # Validate the file
        report = self.processor.validate_context_file('contexts/warning-context.md')
        
        assert report.is_valid is True  # Warnings don't make it invalid
        assert len(report.warnings) >= 2  # Should have warnings about format and empty content
        assert any('Tags should be a list' in w.message for w in report.warnings)
        assert any('Priority should be an integer' in w.message for w in report.warnings)
    
    def test_validate_context_file_not_found(self):
        """Test validation of non-existent file."""
        report = self.processor.validate_context_file('contexts/nonexistent.md')
        
        assert report.is_valid is False
        assert len(report.errors) == 1
        assert 'not found' in report.errors[0].message.lower()
    
    def test_extract_tags_various_formats(self):
        """Test tag extraction from different formats."""
        # Test list format
        frontmatter1 = {'tags': ['tag1', 'tag2', 'tag3']}
        tags1 = self.processor._extract_tags(frontmatter1)
        assert tags1 == ['tag1', 'tag2', 'tag3']
        
        # Test comma-separated string format
        frontmatter2 = {'tags': 'tag1, tag2, tag3'}
        tags2 = self.processor._extract_tags(frontmatter2)
        assert tags2 == ['tag1', 'tag2', 'tag3']
        
        # Test no tags
        frontmatter3 = {}
        tags3 = self.processor._extract_tags(frontmatter3)
        assert tags3 == []
        
        # Test invalid format
        frontmatter4 = {'tags': 123}
        tags4 = self.processor._extract_tags(frontmatter4)
        assert tags4 == []
    
    def test_extract_categories_various_formats(self):
        """Test category extraction from different formats."""
        # Test list format
        frontmatter1 = {'categories': ['cat1', 'cat2']}
        cats1 = self.processor._extract_categories(frontmatter1)
        assert cats1 == ['cat1', 'cat2']
        
        # Test comma-separated string format
        frontmatter2 = {'categories': 'cat1, cat2'}
        cats2 = self.processor._extract_categories(frontmatter2)
        assert cats2 == ['cat1', 'cat2']
    
    def test_extract_priority_various_formats(self):
        """Test priority extraction with different formats."""
        # Test valid integer
        frontmatter1 = {'priority': 5}
        priority1 = self.processor._extract_priority(frontmatter1)
        assert priority1 == 5
        
        # Test string number
        frontmatter2 = {'priority': '3'}
        priority2 = self.processor._extract_priority(frontmatter2)
        assert priority2 == 3
        
        # Test invalid format
        frontmatter3 = {'priority': 'high'}
        priority3 = self.processor._extract_priority(frontmatter3)
        assert priority3 == 0  # Default value
        
        # Test missing priority
        frontmatter4 = {}
        priority4 = self.processor._extract_priority(frontmatter4)
        assert priority4 == 0  # Default value
    
    def test_cache_management(self):
        """Test cache management functionality."""
        # Create test file
        test_file = self.contexts_dir / 'cache-test.md'
        content = """---
title: Cache Test
---
# Cache Test Content
"""
        
        test_file.write_text(content, encoding='utf-8')
        
        # Load file to populate cache
        self.processor.load_context_file('contexts/cache-test.md')
        
        # Check cache stats
        stats = self.processor.get_cache_stats()
        assert stats['cache_size'] == 1
        
        # Clear specific file from cache
        self.processor.clear_cache('contexts/cache-test.md')
        stats = self.processor.get_cache_stats()
        assert stats['cache_size'] == 0
        
        # Load again and clear all cache
        self.processor.load_context_file('contexts/cache-test.md')
        self.processor.clear_cache()
        stats = self.processor.get_cache_stats()
        assert stats['cache_size'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])