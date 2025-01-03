# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-01-03

### Added
- Browser extension integration for enhanced functionality
  - Background script for handling requests
  - Rule-based URL handling
  - Extension configuration via manifest.json
- New documentation for:
  - Browser extension usage and setup
  - URL redirection functionality
  - URL replacement features
- New HTML templates:
  - Base template for consistent layout
  - Error page template
  - Repository view template
  - Task input template
- Environment validation improvements

### Changed
- Major refactoring of core components:
  - Agent session management
  - Application routing and handlers
  - Database operations and structure
  - Orchestrator functionality
- Enhanced frontend JavaScript functionality:
  - Agent view improvements
  - Configuration view updates
  - Index page reorganization
- Restructured static and template files for better organization

### Fixed
- Various bug fixes across agent session handling
- Frontend UI/UX improvements and bug fixes

### Removed
- Legacy test cases that were no longer relevant
- Outdated configuration approaches

## [0.1.0] - 2024-12-30

### Added
- Support for DeepSeek Chat model as an alternative to OpenRouter
- Flexible model selection based on available API keys
- Added action validation functionality

### Changed
- Updated LiteLLMClient to support both OpenRouter and DeepSeek API keys
- Modified environment variable loading to use project directory instead of home directory
- Improved error handling in create_agent endpoint with separate validation for repo_url and tasks
- Updated package versions in requirements.txt for better compatibility

### Fixed
- Task text concatenation in create_agent endpoint
- Error messages for missing repository URL and tasks
