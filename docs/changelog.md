# Changelog

All notable changes to the pAIssive_income project will be documented in this file.

## [Unreleased]

### Added
- Support for MCP servers for AI agents
- Vector database for RAG capabilities
- Google's Agent Development Kit (ADK) demo
- CrewAI framework for multi-agent orchestration
- mem0 for enhanced AI memory
- ARTIST framework with initial agent and tool registry
- CopilotKit + CrewAI integration guide

### Changed
- Updated Flask from 3.1.0 to 3.1.1 in UI requirements
  - Fixed signing key selection order when key rotation is enabled
  - Fixed type hint for `cli_runner.invoke`
  - Improved `flask --help` command to load the app and plugins first
  - Enhanced typing support for views that return `AsyncIterable`
- Removed unused dependencies from Python and Node projects
- Updated GitHub Actions workflows to use Docker Buildx
- Increased test coverage threshold to 80% in GitHub Actions
- Cleaned up unused scripts and files

### Security
- Updated dependencies to address security vulnerabilities
- Implemented comprehensive security scanning

## [0.1.0] - 2025-04-27

### Added
- Initial release of pAIssive_income with core functionality
- Niche Analysis module
- AI Models module
- Agent Team module
- Monetization module
- Marketing module
- UI module
- Common Utilities
- Interface definitions
- Documentation
