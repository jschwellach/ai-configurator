# Requirements Document

## Introduction

This feature aims to simplify the AI Configurator project by restructuring it to use YAML + Markdown files for configuration instead of the current complex JSON and Python-based system. The goal is to make it easier for users to add new hooks and profiles without needing to understand complex data structures or write Python code. This will reduce the barrier to entry for customization and make the system more maintainable.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to define new profiles using simple YAML files, so that I can quickly create custom configurations without dealing with complex JSON structures.

#### Acceptance Criteria

1. WHEN a user creates a new YAML file in the profiles directory THEN the system SHALL automatically recognize and load the profile
2. WHEN a profile YAML file contains context paths and hook definitions THEN the system SHALL apply these configurations correctly
3. IF a profile YAML file has syntax errors THEN the system SHALL provide clear error messages with line numbers
4. WHEN a user lists available profiles THEN the system SHALL display all YAML-defined profiles with their descriptions

### Requirement 2

**User Story:** As a team lead, I want to define hooks using YAML configuration with Markdown documentation, so that I can create reusable automation without writing Python code.

#### Acceptance Criteria

1. WHEN a user creates a hook definition in YAML format THEN the system SHALL support common hook types (on_session_start, per_user_message, on_file_change)
2. WHEN a hook YAML file references a Markdown file THEN the system SHALL load and apply the Markdown content as context
3. WHEN multiple hooks are defined for the same trigger THEN the system SHALL execute them in the specified order
4. IF a hook configuration is invalid THEN the system SHALL log the error and continue with other valid hooks

### Requirement 3

**User Story:** As a configuration manager, I want to organize contexts using Markdown files with YAML frontmatter, so that I can maintain documentation and metadata in a single file.

#### Acceptance Criteria

1. WHEN a Markdown file contains YAML frontmatter THEN the system SHALL parse both the metadata and content
2. WHEN frontmatter includes tags, categories, or priority THEN the system SHALL use these for context organization
3. WHEN a context file is referenced by multiple profiles THEN the system SHALL load it efficiently without duplication
4. IF a Markdown file has malformed frontmatter THEN the system SHALL treat it as plain Markdown and log a warning

### Requirement 4

**User Story:** As a system administrator, I want the new YAML/MD system to be backward compatible with existing configurations, so that I can migrate gradually without breaking current setups.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL load both legacy JSON configs and new YAML configs
2. WHEN both formats define the same profile THEN the YAML format SHALL take precedence
3. WHEN migrating from JSON to YAML THEN the system SHALL provide a conversion utility
4. IF legacy configurations exist THEN the system SHALL continue to support them until explicitly migrated

### Requirement 5

**User Story:** As a developer, I want simplified directory structure for configurations, so that I can easily understand and modify the project layout.

#### Acceptance Criteria

1. WHEN the new structure is implemented THEN profiles SHALL be stored as individual YAML files in a single directory
2. WHEN hooks are defined THEN they SHALL be stored as YAML files with optional companion Markdown files
3. WHEN contexts are organized THEN they SHALL be Markdown files with optional YAML frontmatter
4. WHEN the system loads configurations THEN it SHALL automatically discover files based on naming conventions

### Requirement 6

**User Story:** As a contributor, I want clear validation and error handling for YAML/MD configurations, so that I can quickly identify and fix configuration issues.

#### Acceptance Criteria

1. WHEN a YAML file has syntax errors THEN the system SHALL provide specific error messages with file names and line numbers
2. WHEN required fields are missing THEN the system SHALL list all missing fields in a single error message
3. WHEN file references are broken THEN the system SHALL report which files cannot be found
4. WHEN validation passes THEN the system SHALL provide a summary of loaded configurations

### Requirement 7

**User Story:** As a user, I want hot-reloading of YAML/MD configurations during development, so that I can test changes without restarting the application.

#### Acceptance Criteria

1. WHEN a YAML configuration file is modified THEN the system SHALL detect the change within 2 seconds
2. WHEN a Markdown context file is updated THEN the system SHALL reload the content automatically
3. WHEN configuration changes are detected THEN the system SHALL validate and apply them if valid
4. IF configuration reload fails THEN the system SHALL keep the previous valid configuration and log the error