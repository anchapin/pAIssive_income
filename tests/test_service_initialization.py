"""
Tests for the service initialization module.
"""

import pytest
from unittest.mock import MagicMock, patch

from service_initialization import (
    initialize_services,
    _register_configuration,
    _register_ai_models,
    _register_agent_team,
    _register_niche_analysis,
    _register_monetization,
    _register_marketing,
)
from ui.service_registry import get_service

from dependency_container import DependencyContainer
from interfaces.agent_interfaces import IAgentTeam, IAgentProfile, IResearchAgent
from interfaces.model_interfaces import IModelManager, IModelConfig
from interfaces.niche_interfaces import INicheAnalyzer
from interfaces.monetization_interfaces import IMonetizationCalculator
from interfaces.marketing_interfaces import IMarketingStrategy


@pytest.fixture
def mock_container():
    """Create a mock dependency container."""
    container = MagicMock(spec=DependencyContainer)
    return container


@patch("service_initialization.ModelConfig")
@patch("service_initialization.get_container")
def test_initialize_services(mock_get_container, mock_model_config, mock_container):
    """Test initialize_services function."""
    # Mock the get_container function to return same container for both core and UI services
    mock_get_container.return_value = mock_container

    # Also patch the UI service registry's get_container to return same mock
    with patch("ui.service_registry.get_container", return_value=mock_container):
        # Mock the ModelConfig.get_default method
        mock_config_instance = MagicMock()
        mock_model_config.get_default.return_value = mock_config_instance

        # Call the function
        result = initialize_services()

        # Verify the result
        assert result is mock_container

        # Verify that all register functions were called
        assert mock_container.register.call_count > 0

        # Verify that all services were registered (core + UI services)
        # Core services: IModelConfig, IModelManager, IAgentProfile, IResearchAgent, IAgentTeam, INicheAnalyzer, IMonetizationCalculator, IMarketingStrategy
        # UI services: IAgentTeamService, INicheAnalysisService, IDeveloperService, IMonetizationService, IMarketingService
        assert mock_container.register.call_count >= 13


@patch("service_initialization.ModelConfig")
def test_register_configuration_with_config(mock_model_config, mock_container):
    """Test _register_configuration with a config dictionary."""
    # Mock the ModelConfig class
    mock_config_instance = MagicMock()
    mock_model_config.return_value = mock_config_instance

    # Call the function with a config dictionary
    config = {"model_config": {"models_dir": "/path/to/models"}}
    _register_configuration(mock_container, config)

    # Verify that ModelConfig was called with the config
    mock_model_config.assert_called_once_with(models_dir="/path/to/models")

    # Verify that the container.register was called with the correct interface
    mock_container.register.assert_called_once()
    args, kwargs = mock_container.register.call_args
    assert args[0] == IModelConfig
    assert kwargs.get("singleton") 


@patch("service_initialization.ModelConfig")
def test_register_configuration_without_config(mock_model_config, mock_container):
    """Test _register_configuration without a config dictionary."""
    # Mock the ModelConfig class
    mock_config_instance = MagicMock()
    mock_model_config.get_default.return_value = mock_config_instance

    # Call the function without a config dictionary
    _register_configuration(mock_container)

    # Verify that ModelConfig.get_default was called
    mock_model_config.get_default.assert_called_once()

    # Verify that the container.register was called with the correct interface
    mock_container.register.assert_called_once()
    args, kwargs = mock_container.register.call_args
    assert args[0] == IModelConfig
    assert kwargs.get("singleton") 


@patch("service_initialization.ModelManager")
@patch("service_initialization.get_adapter_factory")
def test_register_ai_models(
    mock_get_adapter_factory, mock_model_manager, mock_container
):
    """Test _register_ai_models function."""
    # Mock the ModelManager class
    mock_manager_instance = MagicMock()
    mock_model_manager.return_value = mock_manager_instance

    # Mock the get_adapter_factory function
    mock_adapter_factory = MagicMock()
    mock_get_adapter_factory.return_value = mock_adapter_factory

    # Mock the container.resolve method
    mock_model_config = MagicMock()
    mock_container.resolve.return_value = mock_model_config

    # Call the function
    _register_ai_models(mock_container)

    # Verify that the container.register was called for IModelManager
    mock_container.register.assert_called_with(
        IModelManager, mock_container.register.call_args[0][1], singleton=True
    )
    args, kwargs = mock_container.register.call_args
    assert args[0] == IModelManager
    assert kwargs.get("singleton") 

    # Verify that the container.register_instance was called for adapter_factory
    mock_container.register_instance.assert_called_once_with(
        "adapter_factory", mock_adapter_factory
    )


@patch("service_initialization.AgentTeam")
@patch("service_initialization.ResearchAgent")
@patch("service_initialization.AgentProfile")
def test_register_agent_team(
    mock_agent_profile, mock_research_agent, mock_agent_team, mock_container
):
    """Test _register_agent_team function."""
    # Mock the classes
    mock_profile_instance = MagicMock()
    mock_agent_profile.return_value = mock_profile_instance

    mock_research_agent_instance = MagicMock()
    mock_research_agent.return_value = mock_research_agent_instance

    mock_agent_team_instance = MagicMock()
    mock_agent_team.return_value = mock_agent_team_instance

    # Mock the container.resolve method
    def resolve_side_effect(service_type):
        if service_type == IAgentProfile:
            return mock_profile_instance
        elif service_type == IResearchAgent:
            return mock_research_agent_instance
        elif service_type == IModelManager:
            return MagicMock()
        else:
            return None

    mock_container.resolve.side_effect = resolve_side_effect

    # Call the function
    _register_agent_team(mock_container)

    # Verify that the container.register was called for all agent services
    assert mock_container.register.call_count == 3


@patch("service_initialization.NicheAnalyzer")
def test_register_niche_analysis(mock_niche_analyzer, mock_container):
    """Test _register_niche_analysis function."""
    # Mock the NicheAnalyzer class
    mock_analyzer_instance = MagicMock()
    mock_niche_analyzer.return_value = mock_analyzer_instance

    # Mock the container.resolve method
    mock_agent_team = MagicMock()
    mock_container.resolve.return_value = mock_agent_team

    # Call the function
    _register_niche_analysis(mock_container)

    # Verify that the container.register was called with the correct interface
    mock_container.register.assert_called_once()
    args, kwargs = mock_container.register.call_args
    assert args[0] == INicheAnalyzer
    assert kwargs.get("singleton") 


@patch("service_initialization.MonetizationCalculator")
def test_register_monetization(mock_monetization_calculator, mock_container):
    """Test _register_monetization function."""
    # Mock the MonetizationCalculator class
    mock_calculator_instance = MagicMock()
    mock_monetization_calculator.return_value = mock_calculator_instance

    # Call the function
    _register_monetization(mock_container)

    # Verify that the container.register was called with the correct interface
    mock_container.register.assert_called_once()
    args, kwargs = mock_container.register.call_args
    assert args[0] == IMonetizationCalculator
    assert kwargs.get("singleton") 


@patch("service_initialization.StrategyGenerator")
def test_register_marketing(mock_strategy_generator, mock_container):
    """Test _register_marketing function."""
    # Mock the StrategyGenerator class
    mock_generator_instance = MagicMock()
    mock_strategy_generator.return_value = mock_generator_instance

    # Mock the container.resolve method
    mock_agent_team = MagicMock()
    mock_container.resolve.return_value = mock_agent_team

    # Call the function
    _register_marketing(mock_container)

    # Verify that the container.register was called with the correct interface
    mock_container.register.assert_called_once()
    args, kwargs = mock_container.register.call_args
    assert args[0] == IMarketingStrategy
    assert kwargs.get("singleton") 


@patch("ui.service_registry.get_container")
def test_get_service(mock_get_container):
    """Test get_service function."""
    # Mock the get_container function
    mock_container = MagicMock()
    mock_get_container.return_value = mock_container

    # Mock the container.resolve method
    mock_service = MagicMock()
    mock_container.resolve.return_value = mock_service

    # Register a service to resolve
    mock_container.register(IAgentTeam, lambda: mock_service)

    # Call the function
    result = get_service(IAgentTeam)

    # Verify the result
    assert result is mock_service

    # Verify that container.resolve was called
    mock_container.resolve.assert_called_once_with(IAgentTeam)
