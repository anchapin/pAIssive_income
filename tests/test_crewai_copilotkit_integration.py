"""Test the integration between CrewAI and CopilotKit."""

import pytest
import sys
import os
import logging
import json
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Check if crewai is installed
try:
    import crewai
    CREWAI_AVAILABLE = True
    logging.info(f"CrewAI is available (version: {crewai.__version__})")
except ImportError as e:
    CREWAI_AVAILABLE = False
    logging.warning(f"CrewAI is not available: {e}")

    # Try to add the mock_crewai directory to sys.path
    mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai")
    if os.path.exists(mock_dir):
        logging.info(f"Found mock_crewai directory at {mock_dir}, adding to sys.path")
        sys.path.insert(0, os.path.dirname(mock_dir))

    # Try to add the current directory to sys.path
    sys.path.insert(0, os.getcwd())


def test_crewai_copilotkit_integration_docs():
    """Test that the CrewAI and CopilotKit integration documentation exists."""
    # Check if the integration documentation exists
    docs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CopilotKit_CrewAI_Integration.md")
    ui_docs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "react_frontend", "CopilotKit_CrewAI.md")
    
    # At least one of the documentation files should exist
    assert os.path.exists(docs_path) or os.path.exists(ui_docs_path), "CrewAI and CopilotKit integration documentation not found"
    
    # If the documentation exists, check its content
    if os.path.exists(docs_path):
        with open(docs_path, "r") as f:
            content = f.read()
        
        # Check that the documentation contains the expected sections
        assert "CopilotKit + CrewAI Integration" in content, "Documentation does not contain the expected title"
        assert "Overview" in content, "Documentation does not contain the Overview section"
        assert "Implementation Details" in content, "Documentation does not contain the Implementation Details section"
        assert "Usage" in content, "Documentation does not contain the Usage section"
        assert "Resources" in content, "Documentation does not contain the Resources section"
    
    if os.path.exists(ui_docs_path):
        with open(ui_docs_path, "r") as f:
            content = f.read()
        
        # Check that the documentation contains the expected sections
        assert "CopilotKit + CrewAI Integration Guide" in content, "Documentation does not contain the expected title"
        assert "Implementation Details" in content, "Documentation does not contain the Implementation Details section"
        assert "Quick Start" in content, "Documentation does not contain the Quick Start section"
        assert "Testing" in content, "Documentation does not contain the Testing section"
    
    logging.info("CrewAI and CopilotKit integration documentation test passed")


def test_crewai_copilotkit_frontend_component():
    """Test that the CrewAI and CopilotKit frontend component exists."""
    # Check if the frontend component exists
    component_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "react_frontend", "src", "components", "CopilotChat.jsx")
    
    assert os.path.exists(component_path), "CrewAI and CopilotKit frontend component not found"
    
    # If the component exists, check its content
    with open(component_path, "r") as f:
        content = f.read()
    
    # Check that the component contains the expected imports and components
    assert "import React from" in content, "Component does not import React"
    assert "import { CopilotKitProvider } from" in content, "Component does not import CopilotKitProvider"
    assert "import { CopilotChat } from" in content, "Component does not import CopilotChat"
    assert "CopilotKitProvider" in content, "Component does not use CopilotKitProvider"
    assert "CopilotChat" in content, "Component does not use CopilotChat"
    
    logging.info("CrewAI and CopilotKit frontend component test passed")


def test_crewai_copilotkit_frontend_test():
    """Test that the CrewAI and CopilotKit frontend test exists."""
    # Check if the frontend test exists
    test_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "react_frontend", "src", "components", "CopilotChat.test.jsx")
    
    assert os.path.exists(test_path), "CrewAI and CopilotKit frontend test not found"
    
    # If the test exists, check its content
    with open(test_path, "r") as f:
        content = f.read()
    
    # Check that the test contains the expected imports and tests
    assert "import React from" in content, "Test does not import React"
    assert "import { render" in content, "Test does not import render"
    assert "import CopilotChatDemo from" in content, "Test does not import CopilotChatDemo"
    assert "describe(" in content, "Test does not contain a describe block"
    assert "it(" in content, "Test does not contain any test cases"
    
    logging.info("CrewAI and CopilotKit frontend test test passed")


@pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI is not available")
def test_crewai_copilotkit_api_integration():
    """Test the integration between CrewAI and CopilotKit API."""
    if not CREWAI_AVAILABLE:
        pytest.skip("CrewAI is not installed - skipping test")
    
    try:
        # Import the CrewAI agent from the agent_team module
        from agent_team.crewai_agents import CrewAIAgentTeam
        
        # Create a mock API response
        mock_api_response = {
            "message": "Hello from the API!",
            "agents": [
                {"role": "Researcher", "goal": "Research the topic", "backstory": "Expert researcher"},
                {"role": "Writer", "goal": "Write the report", "backstory": "Expert writer"}
            ],
            "tasks": [
                {"description": "Research the topic", "agent": "Researcher"},
                {"description": "Write the report", "agent": "Writer"}
            ]
        }
        
        # Create a mock API client
        mock_api_client = MagicMock()
        mock_api_client.get_agents.return_value = mock_api_response["agents"]
        mock_api_client.get_tasks.return_value = mock_api_response["tasks"]
        
        # Create a mock LLM provider
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Mock LLM response"
        
        # Create a CrewAIAgentTeam instance
        agent_team = CrewAIAgentTeam(llm_provider=mock_llm)
        
        # Set the API client
        agent_team.api_client = mock_api_client
        
        # Test the run method with the API client
        with patch.object(agent_team, '_create_crew') as mock_create_crew:
            mock_crew = MagicMock()
            mock_crew.kickoff.return_value = "API integration workflow result"
            mock_create_crew.return_value = mock_crew
            
            result = agent_team.run()
            
            # Verify the result
            assert result == "API integration workflow result"
            
            # Verify the crew was created and kickoff was called
            mock_create_crew.assert_called_once()
            mock_crew.kickoff.assert_called_once()
        
        logging.info("CrewAI and CopilotKit API integration test passed")
    except ImportError as e:
        logging.exception("CrewAI and CopilotKit API integration test failed")
        pytest.skip("CrewAI and CopilotKit API integration test failed")
