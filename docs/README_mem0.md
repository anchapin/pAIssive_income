# mem0 Integration

This directory contains documentation for the mem0 integration in the pAIssive_income project.

## Overview

[mem0](https://mem0.ai) is a memory system that enables AI agents to remember user preferences, past interactions, and important information across conversations. It has been successfully integrated into our project to enhance agent personalization and effectiveness.

## Contents

- [mem0_integration.md](../05_sdk_and_integrations/mem0_integration.md): **Integration/setup guide**
- [mem0_investigation.md](mem0_investigation.md): Comprehensive overview of mem0, its features, and integration considerations
- [mem0_integration_options.md](mem0_integration_options.md): Detailed analysis of different integration approaches
- [mem0_core_apis.md](mem0_core_apis.md): Documentation of mem0's core APIs, classes, and usage patterns
- [04_security_and_compliance/05_mem0_integration.md](04_security_and_compliance/05_mem0_integration.md): Security and compliance considerations for mem0 integration
- [../agent_team/mem0_enhanced_agents.py](../agent_team/mem0_enhanced_agents.py): Memory-enhanced CrewAI agents
- [../adk_demo/mem0_enhanced_adk_agents.py](../adk_demo/mem0_enhanced_adk_agents.py): Memory-enhanced ADK agents
- [../test_mem0_integration.py](../test_mem0_integration.py): Test script for verifying mem0 integration

## Implementation Status

The mem0 integration has been successfully implemented with the following components:

1. **Memory-Enhanced CrewAI Agents**: `MemoryEnhancedCrewAIAgentTeam` class in `agent_team/mem0_enhanced_agents.py`
2. **Memory-Enhanced ADK Agents**: `MemoryEnhancedAgent`, `MemoryEnhancedDataGathererAgent`, and `MemoryEnhancedSummarizerAgent` classes in `adk_demo/mem0_enhanced_adk_agents.py`
3. **Integration Tests**: Test script in `test_mem0_integration.py` to verify the integration

## Key Features

1. **Persistent Memory**: Agents remember user preferences, past interactions, and important information
2. **Memory Search**: Retrieve relevant memories based on context and queries
3. **Conversation Storage**: Store entire conversations for future reference
4. **Memory-Enhanced Agents**: Both ADK and CrewAI agents are enhanced with memory capabilities

## Getting Started

To use mem0 in your project:

1. Install the required dependencies:
   ```bash
   # Using pip
   pip install -r requirements.txt

   # Using uv (recommended)
   uv pip install -r requirements.txt
   ```

2. Set your OpenAI API key (required by mem0):
   ```bash
   # Linux/macOS
   export OPENAI_API_KEY='your-api-key'

   # Windows (PowerShell)
   $env:OPENAI_API_KEY='your-api-key'

   # Windows (Command Prompt)
   set OPENAI_API_KEY=your-api-key
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

## Security and Compliance

For security and compliance considerations when using mem0, see [04_security_and_compliance/05_mem0_integration.md](04_security_and_compliance/05_mem0_integration.md).

## Future Enhancements

Planned enhancements for the mem0 integration:

1. **Advanced Context Enhancement**: Improve how memories are integrated into agent context
2. **Memory Management UI**: Add a user interface for viewing and managing stored memories
3. **Memory Analytics**: Add analytics for tracking memory usage and effectiveness
4. **Multi-Provider Support**: Add support for alternative embedding providers beyond OpenAI

## Conclusion

The mem0 integration enhances our agents with persistent memory capabilities, making them more personalized and effective. The implementation provides a solid foundation for future enhancements and can be easily extended to support additional agent types and use cases.
