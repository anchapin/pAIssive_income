# PR #193: mem0 Integration

This document provides an overview of the changes made in PR #193, which integrates mem0 for memory capabilities in agents.

## Overview

[mem0](https://mem0.ai) is a memory layer for AI agents that enables persistent memory capabilities across conversations and sessions. It has been integrated into our project to enhance agent personalization, improve contextual awareness, and provide cross-session continuity.

## Changes Made

### Agent Team Module

- Added `MemoryEnhancedCrewAIAgentTeam` class in `agent_team/mem0_enhanced_agents.py`
- Implemented memory hooks at agent initialization, task assignment, and team execution

### ADK Demo Module

- Added `MemoryEnhancedAgent` base class in `adk_demo/mem0_enhanced_adk_agents.py`
- Added specialized memory-enhanced agents:
  - `MemoryEnhancedDataGathererAgent`
  - `MemoryEnhancedSummarizerAgent`
- Implemented memory hooks at message processing, skill execution, and response generation

### Testing

- Added `test_mem0_integration.py` to verify mem0 integration

### GitHub Workflows

- Updated CodeQL workflows to include mem0-related files in security scanning:
  - `.github/workflows/codeql.yml`
  - `.github/workflows/codeql-ubuntu.yml`
  - `.github/workflows/codeql-macos.yml`
  - `.github/workflows/codeql-windows.yml`
- Updated CI/CD workflow to include mem0 integration tests:
  - `.github/workflows/consolidated-ci-cd.yml`
- Updated Docker Compose workflows to include mem0 services:
  - `.github/workflows/docker-compose-workflow.yml`
  - `.github/workflows/docker-compose.yml`

### Documentation

- Added comprehensive documentation for mem0 integration:
  - `docs/04_security_and_compliance/05_mem0_integration.md`: Security and compliance considerations
  - Updated `docs/README_mem0.md`: Overview of mem0 integration
  - Added `docs/02_developer_guide/06_module_deep_dives/adk_demo.md`: ADK module documentation
  - Updated `docs/02_developer_guide/06_module_deep_dives/agent_team.md`: Agent team module documentation
  - Added `docs/03_operations_guide/github_workflows.md`: GitHub workflows documentation

## Security Considerations

The mem0 integration includes several security considerations:

1. **Data Isolation**: Memories are isolated by user_id to prevent cross-user data leakage
2. **Metadata Filtering**: Sensitive data can be filtered using metadata
3. **Storage Location**: By default, data is stored locally, but can be configured for remote storage
4. **API Key Security**: API keys are stored securely using environment variables

## Getting Started

To use mem0 in your project:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key (required by mem0):
   ```bash
   export OPENAI_API_KEY='your-api-key'
   ```

3. Verify the integration:
   ```bash
   python test_mem0_integration.py
   ```

4. Use memory-enhanced agents in your code:
   ```python
   # For CrewAI agents
   from agent_team.mem0_enhanced_agents import MemoryEnhancedCrewAIAgentTeam
   
   team = MemoryEnhancedCrewAIAgentTeam(user_id="user123")
   researcher = team.add_agent(
       role="Researcher",
       goal="Find relevant information",
       backstory="Expert at gathering data"
   )
   result = team.run()
   
   # For ADK agents
   from adk_demo.mem0_enhanced_adk_agents import MemoryEnhancedDataGathererAgent
   
   agent = MemoryEnhancedDataGathererAgent(name="DataGatherer", user_id="user123")
   response = agent.handle_message(message)
   ```

## References

- [mem0 Official Website](https://mem0.ai)
- [mem0 GitHub Repository](https://github.com/mem0ai/mem0)
- [docs/README_mem0.md](docs/README_mem0.md)
- [docs/04_security_and_compliance/05_mem0_integration.md](docs/04_security_and_compliance/05_mem0_integration.md)
