"""
Integration tests for the AI Models module.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent_team import AgentTeam
from ai_models import AgentModelProvider, ModelConfig, ModelManager, PerformanceMonitor


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


@patch("agent_team.team_config.ResearchAgent")
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


@patch("ai_models.model_manager.ModelManager.load_model")
@patch("ai_models.model_manager.ModelManager.get_model_info")
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


@pytest.fixture
def mock_all_agents():
    """Create mock agents for all agent types."""
    mock_agents = {}

    agent_types = ["researcher", "developer", "monetization", "marketing"]

    for agent_type in agent_types:
        mock_agent = MagicMock(name=f"{agent_type.capitalize()}Agent")
        mock_agents[agent_type] = mock_agent

    return mock_agents


@patch("agent_team.team_config.ResearchAgent")
@patch("agent_team.team_config.DeveloperAgent")
@patch("agent_team.team_config.MonetizationAgent")
@patch("agent_team.team_config.MarketingAgent")
def test_multiple_agents_model_integration(
    mock_marketing_class,
    mock_monetization_class,
    mock_developer_class,
    mock_researcher_class,
    mock_all_agents,
    mock_model_manager,
):
    """Test integration between multiple agent types and their respective models."""
    # Set up the mock agents
    mock_researcher_class.return_value = mock_all_agents["researcher"]
    mock_developer_class.return_value = mock_all_agents["developer"]
    mock_monetization_class.return_value = mock_all_agents["monetization"]
    mock_marketing_class.return_value = mock_all_agents["marketing"]

    # Mock additional models in model manager
    models = {
        "research_model": {
            "id": "research_model",
            "name": "Research Model",
            "capabilities": ["text-generation", "summarization"],
        },
        "dev_model": {
            "id": "dev_model",
            "name": "Developer Model",
            "capabilities": ["code-generation", "code-explanation"],
        },
        "monetization_model": {
            "id": "monetization_model",
            "name": "Monetization Model",
            "capabilities": ["financial-analysis", "pricing-optimization"],
        },
        "marketing_model": {
            "id": "marketing_model",
            "name": "Marketing Model",
            "capabilities": ["content-generation", "audience-analysis"],
        },
    }

    mock_model_manager.get_model_info.side_effect = lambda model_id: models.get(
        model_id, None
    )
    mock_model_manager.load_model.side_effect = lambda model_id: MagicMock(
        name=models.get(model_id, {}).get("name", "Unknown Model")
    )

    # Create a model provider
    provider = AgentModelProvider(mock_model_manager)

    # Create a team
    team = AgentTeam("Test Team")

    # Assign models to each agent type for different capabilities
    provider.assign_model_to_agent("researcher", "research_model", "text-generation")
    provider.assign_model_to_agent("developer", "dev_model", "code-generation")
    provider.assign_model_to_agent(
        "monetization", "monetization_model", "financial-analysis"
    )
    provider.assign_model_to_agent("marketing", "marketing_model", "content-generation")

    # Get models for each agent
    research_model = provider.get_model_for_agent("researcher", "text-generation")
    dev_model = provider.get_model_for_agent("developer", "code-generation")
    monetization_model = provider.get_model_for_agent(
        "monetization", "financial-analysis"
    )
    marketing_model = provider.get_model_for_agent("marketing", "content-generation")

    # Check that appropriate models were returned
    assert research_model is not None
    assert dev_model is not None
    assert monetization_model is not None
    assert marketing_model is not None

    # Check that the model manager's load_model method was called for each agent
    mock_model_manager.load_model.assert_any_call("research_model")
    mock_model_manager.load_model.assert_any_call("dev_model")
    mock_model_manager.load_model.assert_any_call("monetization_model")
    mock_model_manager.load_model.assert_any_call("marketing_model")

    # Run a complete workflow
    niches = team.run_niche_analysis(["e-commerce"])
    solution = team.develop_solution(niches[0])
    monetization = team.create_monetization_strategy(solution)
    marketing_plan = team.create_marketing_plan(niches[0], solution, monetization)

    # Check that each agent's method was called
    mock_all_agents["researcher"].analyze_market_segments.assert_called_once()
    mock_all_agents["developer"].design_solution.assert_called_once()
    mock_all_agents["monetization"].create_strategy.assert_called_once()
    mock_all_agents["marketing"].create_plan.assert_called_once()


@patch("ai_models.model_manager.ModelManager.load_model")
def test_model_fallback_integration(mock_load_model, mock_model_manager):
    """Test integration with model fallbacks."""
    # Setup primary and fallback models
    primary_model = MagicMock(name="Primary Model")
    fallback_model = MagicMock(name="Fallback Model")

    # Configure the mock to fail on the first call, then return the fallback model
    mock_load_model.side_effect = [Exception("Model loading failed"), fallback_model]

    # Create a model provider with fallback configured
    provider = AgentModelProvider(mock_model_manager)
    provider.configure_fallback("primary_model", "fallback_model")

    # Attempt to get the model, which should trigger the fallback
    model = provider.get_model_with_fallback(
        "researcher", "primary_model", "text-generation"
    )

    # Check that both primary and fallback models were attempted
    assert mock_load_model.call_count == 2
    mock_load_model.assert_any_call("primary_model")
    mock_load_model.assert_any_call("fallback_model")

    # Check that the fallback model was returned
    assert model == fallback_model


@patch("ai_models.performance_monitor.PerformanceMonitor")
def test_model_performance_tracking_integration(
    mock_performance_monitor_class, mock_model_manager
):
    """Test integration with performance tracking."""
    # Create a mock performance monitor
    mock_performance_monitor = MagicMock(spec=PerformanceMonitor)
    mock_performance_monitor_class.return_value = mock_performance_monitor

    # Create a model
    model = MagicMock(name="Test Model")
    model.generate.return_value = "Generated text"
    mock_model_manager.load_model.return_value = model

    # Create a model provider with performance monitoring
    provider = AgentModelProvider(
        mock_model_manager, performance_monitor=mock_performance_monitor
    )

    # Assign a model to an agent
    provider.assign_model_to_agent("researcher", "model1", "text-generation")

    # Get the model for the agent
    tracked_model = provider.get_model_for_agent("researcher", "text-generation")

    # Use the model
    result = tracked_model.generate(prompt="Test prompt", max_tokens=100)

    # Check that the model's generate method was called
    model.generate.assert_called_once_with(prompt="Test prompt", max_tokens=100)

    # Check that the performance monitor's track_inference method was called
    mock_performance_monitor.track_inference.assert_called_once()

    # Check that the correct result was returned
    assert result == "Generated text"


@patch("agent_team.team_config.ResearchAgent")
def test_agent_model_error_handling_integration(
    mock_researcher_class, mock_model_manager
):
    """Test integration with model error handling in agents."""
    # Mock the ResearchAgent
    mock_researcher = MagicMock()
    mock_researcher_class.return_value = mock_researcher

    # Configure the model manager to raise an exception when loading a model
    mock_model_manager.load_model.side_effect = Exception("Model loading failed")

    # Create a model provider
    provider = AgentModelProvider(mock_model_manager)

    # Create a team
    team = AgentTeam("Test Team")

    # Assign a model to the researcher agent
    provider.assign_model_to_agent("researcher", "model1", "text-generation")

    # Check that an exception is raised when trying to get the model
    with pytest.raises(Exception) as excinfo:
        model = provider.get_model_for_agent("researcher", "text-generation")

    # Check that the exception message is correct
    assert "Model loading failed" in str(excinfo.value)


@patch("ai_models.model_manager.ModelManager.get_model_info")
def test_agent_model_capabilities_integration(mock_get_model_info, mock_model_manager):
    """Test integration with model capabilities checking."""
    # Mock model info with capabilities
    mock_get_model_info.return_value = {
        "id": "model1",
        "name": "Test Model",
        "capabilities": ["text-generation", "summarization"],
    }

    # Create a model provider
    provider = AgentModelProvider(mock_model_manager)

    # Check if model has capabilities
    has_capability = provider.model_has_capability("model1", "text-generation")
    missing_capability = provider.model_has_capability("model1", "code-generation")

    # Verify capability checks
    assert has_capability is True
    assert missing_capability is False

    # Assign a model to an agent for a specific capability
    provider.assign_model_to_agent("researcher", "model1", "text-generation")

    # Check that the assignment was successful
    assigned_model_id = provider.get_assigned_model_id("researcher", "text-generation")
    assert assigned_model_id == "model1"

    # Check that assignments for unsupported capabilities fail
    with pytest.raises(ValueError) as excinfo:
        provider.assign_model_to_agent("researcher", "model1", "code-generation")

    # Check that the exception message mentions the missing capability
    assert "code-generation" in str(excinfo.value)
