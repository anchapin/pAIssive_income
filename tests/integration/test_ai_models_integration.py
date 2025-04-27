"""
Integration tests for the AI Models module.
"""
import pytest
from unittest.mock import patch, MagicMock

from ai_models import ModelManager, ModelConfig, AgentModelProvider
from agent_team import AgentTeam


@pytest.fixture
def mock_model_manager():
    """Create a mock ModelManager."""
    manager = MagicMock(spec=ModelManager)
    
    # Mock get_model_info method
    manager.get_model_info.return_value = {
        "id": "model1",
        "name": "Test Model",
        "description": "A test model",
        "type": "huggingface",
        "path": "/path/to/model",
        "capabilities": ["text-generation"],
    }
    
    # Mock load_model method
    manager.load_model.return_value = MagicMock(name="Test Model")
    
    return manager


@patch('agent_team.team_config.ResearchAgent')
def test_agent_model_integration(mock_researcher_class, mock_model_manager):
    """Test integration between AgentModelProvider and AgentTeam."""
    # Mock the ResearchAgent
    mock_researcher = MagicMock()
    mock_researcher_class.return_value = mock_researcher
    
    # Create a model provider
    provider = AgentModelProvider(mock_model_manager)
    
    # Create a team
    team = AgentTeam("Test Team")
    
    # Assign a model to the researcher agent
    provider.assign_model_to_agent("researcher", "model1", "text-generation")
    
    # Get the model for the researcher agent
    model = provider.get_model_for_agent("researcher", "text-generation")
    
    # Check that the model manager's load_model method was called
    mock_model_manager.load_model.assert_called_with("model1")
    
    # Check that a model was returned
    assert model is not None
    
    # Run niche analysis
    team.run_niche_analysis(["e-commerce"])
    
    # Check that the researcher's analyze_market_segments method was called
    mock_researcher.analyze_market_segments.assert_called_once_with(["e-commerce"])


@patch('ai_models.model_manager.ModelManager.load_model')
@patch('ai_models.model_manager.ModelManager.get_model_info')
def test_model_loading_integration(mock_get_model_info, mock_load_model):
    """Test integration between ModelManager and AgentModelProvider."""
    # Mock the get_model_info method
    mock_get_model_info.return_value = {
        "id": "model1",
        "name": "Test Model",
        "description": "A test model",
        "type": "huggingface",
        "path": "/path/to/model",
        "capabilities": ["text-generation"],
    }
    
    # Mock the load_model method
    mock_model = MagicMock(name="Test Model")
    mock_load_model.return_value = mock_model
    
    # Create a model manager
    manager = ModelManager()
    
    # Create a model provider
    provider = AgentModelProvider(manager)
    
    # Assign a model to the researcher agent
    provider.assign_model_to_agent("researcher", "model1", "text-generation")
    
    # Get the model for the researcher agent
    model = provider.get_model_for_agent("researcher", "text-generation")
    
    # Check that the model manager's methods were called
    mock_get_model_info.assert_called_with("model1")
    mock_load_model.assert_called_with("model1")
    
    # Check that the correct model was returned
    assert model == mock_model
