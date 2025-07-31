"""Integration test for MarkdownProcessor with real context files."""

import tempfile
import shutil
from pathlib import Path

from src.ai_configurator.core.markdown_processor import MarkdownProcessor


def test_markdown_processor_integration():
    """Test MarkdownProcessor with realistic context files."""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        processor = MarkdownProcessor(base_path=temp_dir)
        
        # Create contexts directory
        contexts_dir = Path(temp_dir) / 'contexts'
        contexts_dir.mkdir()
        
        # Create a realistic context file with frontmatter
        aws_context = contexts_dir / 'aws-best-practices.md'
        aws_content = """---
title: AWS Best Practices
description: Guidelines for AWS development and deployment
tags: [aws, cloud, best-practices, infrastructure]
categories: [development, operations]
priority: 5
author: Solutions Architect
date: 2024-01-15
---

# AWS Best Practices

This document outlines key best practices for AWS development.

## Security

- Always use IAM roles instead of hardcoded credentials
- Enable CloudTrail for audit logging
- Use VPC for network isolation

## Cost Optimization

- Use appropriate instance types
- Implement auto-scaling
- Monitor usage with CloudWatch

## Performance

- Use CloudFront for content delivery
- Implement caching strategies
- Choose the right database service

## Code Examples

```python
import boto3

def get_s3_client():
    return boto3.client('s3')
```

For more information, see the [AWS Documentation](https://docs.aws.amazon.com/).
"""
        
        aws_context.write_text(aws_content, encoding='utf-8')
        
        # Create another context file without frontmatter
        dev_context = contexts_dir / 'development-guidelines.md'
        dev_content = """# Development Guidelines

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Write comprehensive tests

## Git Workflow

- Use feature branches
- Write clear commit messages
- Review all pull requests
"""
        
        dev_context.write_text(dev_content, encoding='utf-8')
        
        # Test loading the AWS context file
        aws_context_file = processor.load_context_file('contexts/aws-best-practices.md')
        
        print("=== AWS Context File ===")
        print(f"File Path: {aws_context_file.file_path}")
        print(f"Title: {aws_context_file.metadata.get('title')}")
        print(f"Tags: {aws_context_file.tags}")
        print(f"Categories: {aws_context_file.categories}")
        print(f"Priority: {aws_context_file.priority}")
        print(f"Content Length: {len(aws_context_file.content)} characters")
        print(f"Word Count: {aws_context_file.metadata.get('word_count')}")
        print(f"Header Count: {aws_context_file.metadata.get('header_count')}")
        print(f"Code Block Count: {aws_context_file.metadata.get('code_block_count')}")
        print(f"Link Count: {aws_context_file.metadata.get('link_count')}")
        
        # Test loading the dev context file (no frontmatter)
        dev_context_file = processor.load_context_file('contexts/development-guidelines.md')
        
        print("\n=== Development Context File ===")
        print(f"File Path: {dev_context_file.file_path}")
        print(f"Has Frontmatter: {dev_context_file.metadata.get('has_frontmatter')}")
        print(f"Tags: {dev_context_file.tags}")
        print(f"Priority: {dev_context_file.priority}")
        print(f"Content Length: {len(dev_context_file.content)} characters")
        
        # Test discovering all context files
        discovered_files = processor.discover_context_files()
        print(f"\n=== Discovered Files ===")
        for file_path in discovered_files:
            print(f"- {file_path}")
        
        # Test validation
        aws_validation = processor.validate_context_file('contexts/aws-best-practices.md')
        print(f"\n=== AWS Context Validation ===")
        print(f"Valid: {aws_validation.is_valid}")
        print(f"Errors: {len(aws_validation.errors)}")
        print(f"Warnings: {len(aws_validation.warnings)}")
        print(f"Info: {len(aws_validation.info)}")
        
        # Test loading multiple files
        all_contexts = processor.load_multiple_context_files(discovered_files)
        print(f"\n=== Loaded {len(all_contexts)} Context Files ===")
        for context in all_contexts:
            print(f"- {context.file_path}: {context.metadata.get('title', 'No title')}")
        
        # Test cache stats
        cache_stats = processor.get_cache_stats()
        print(f"\n=== Cache Statistics ===")
        print(f"Cache Size: {cache_stats['cache_size']}")
        print(f"Total Content Length: {cache_stats['total_cached_content_length']} characters")
        
        print("\n✅ Integration test completed successfully!")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    test_markdown_processor_integration()