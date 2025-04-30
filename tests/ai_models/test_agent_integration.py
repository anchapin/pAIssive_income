"""
Tests for the AgentModelProvider class.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

from ai_models.agent_integration import AgentModelProvider
from ai_models.model_manager import ModelManager, ModelInfo
from interfaces.model_interfaces import IModelManager, IModelInfo


class MockModelInfo(IModelInfo):
    """Mock model info for testing."""

    def __init__(self, id, name, description, type, path, capabilities=None):
        self._id = id
        self._name = name
        self._description = description
        self._type = type
        self._path = path
        self._capabilities = capabilities or []

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        return self._path

    @property
    def type(self) -> str:
        return self._type

    @property
    def description(self) -> str:
        return self._description

    @property
    def capabilities(self) -> list:
        return self._capabilities

    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "type": self._type,
            "path": self._path,
            "capabilities": self._capabilities,
        }


@pytest.fixture
def mock_model_manager():
    """Create a mock ModelManager."""
    manager = MagicMock(spec=ModelManager)

    # Mock get_models_by_type method
    def get_models_by_type(model_type):
        if model_type == "huggingface":
            return [
                MockModelInfo(
                    id="model1",
                    name="Model 1",
                    description="A test model",
                    type="huggingface",
                    path="/path/to/model1",
                    capabilities=["text-generation"],
                ),
                MockModelInfo(
                    id="model2",
                    name="Model 2",
                    description="Another test model",
                    type="huggingface",
                    path="/path/to/model2",
                    capabilities=["text-generation", "embedding"],
                ),
            ]
        elif model_type == "embedding":
            return [
                MockModelInfo(
                    id="model3",
                    name="Model 3",
                    description="An embedding model",
                    type="embedding",
                    path="/path/to/model3",
                    capabilities=["embedding"],
                )
            ]
        else:
            return []

    manager.get_models_by_type.side_effect = get_models_by_type

    # Mock get_model_info method
    def get_model_info(model_id):
        if model_id == "model1":
            return MockModelInfo(
                id="model1",
                name="Model 1",
                description="A test model",
                type="huggingface",
                path="/path/to/model1",
                capabilities=["text-generation"],
            )
        elif model_id == "model2":
            return MockModelInfo(
                id="model2",
                name="Model 2",
                description="Another test model",
                type="huggingface",
                path="/path/to/model2",
                capabilities=["text-generation", "embedding"],
            )
        elif model_id == "model3":
            return MockModelInfo(
                id="model3",
                name="Model 3",
                description="An embedding model",
                type="embedding",
                path="/path/to/model3",
                capabilities=["embedding"],
            )
        else:
            return None

    manager.get_model_info.side_effect = get_model_info

    # Mock load_model method
    def load_model(model_id, **kwargs):
        if model_id == "model1":
            return MagicMock(name="Model 1")
        elif model_id == "model2":
            return MagicMock(name="Model 2")
        elif model_id == "model3":
            return MagicMock(name="Model 3")
        else:
            raise ValueError(f"Model with ID {model_id} not found")

    manager.load_model.side_effect = load_model

    return manager


def test_agent_model_provider_init(mock_model_manager):
    """Test AgentModelProvider initialization."""
    provider = AgentModelProvider(mock_model_manager)

    # Check that the model manager is set
    assert provider.model_manager == mock_model_manager

    # Check that the agent models dictionary is empty
    assert provider.agent_models == {}


@patch("ai_models.agent_integration.get_container")
def test_agent_model_provider_init_with_container(
    mock_get_container, mock_model_manager
):
    """Test initializing with a model manager from the container."""
    # Mock the container
    container = MagicMock()
    container.resolve.return_value = mock_model_manager
    mock_get_container.return_value = container

    # Create the provider
    provider = AgentModelProvider()

    # Verify the model manager was resolved from the container
    assert provider.model_manager is mock_model_manager
    container.resolve.assert_called_once_with(IModelManager)


@patch("ai_models.agent_integration.get_container")
@patch("ai_models.agent_integration.ModelManager")
def test_agent_model_provider_init_fallback(
    mock_model_manager_class, mock_get_container, mock_model_manager
):
    """Test initializing with fallback to ModelManager."""
    # Mock the container to raise an error
    container = MagicMock()
    container.resolve.side_effect = ValueError("Not registered")
    mock_get_container.return_value = container

    # Mock the ModelManager class
    mock_model_manager_class.return_value = mock_model_manager

    # Create the provider
    provider = AgentModelProvider()

    # Verify the model manager was created
    assert provider.model_manager is mock_model_manager
    container.resolve.assert_called_once_with(IModelManager)
    mock_model_manager_class.assert_called_once()


def test_get_model_for_agent_no_assignment(mock_model_manager):
    """Test get_model_for_agent method with no previous assignment."""
    provider = AgentModelProvider(mock_model_manager)

    # Get a model for the researcher agent
    model = provider.get_model_for_agent("researcher", "text-generation")

    # Check that the model manager's get_models_by_type method was called
    mock_model_manager.get_models_by_type.assert_called_with("huggingface")

    # Check that the model manager's load_model method was called
    mock_model_manager.load_model.assert_called_once()

    # Check that the agent model assignment was stored
    assert "researcher" in provider.agent_models
    assert "text-generation" in provider.agent_models["researcher"]


def test_get_model_for_agent_with_assignment(mock_model_manager):
    """Test get_model_for_agent method with a previous assignment."""
    provider = AgentModelProvider(mock_model_manager)

    # Assign a model to the researcher agent
    provider.agent_models["researcher"] = {"text-generation": "model1"}

    # Get a model for the researcher agent
    model = provider.get_model_for_agent("researcher", "text-generation")

    # Check that the model manager's load_model method was called with the assigned model ID
    mock_model_manager.load_model.assert_called_with("model1")


def test_assign_model_to_agent(mock_model_manager):
    """Test assign_model_to_agent method."""
    provider = AgentModelProvider(mock_model_manager)

    # Assign a model to the researcher agent
    provider.assign_model_to_agent("researcher", "model1", "text-generation")

    # Check that the agent model assignment was stored
    assert "researcher" in provider.agent_models
    assert "text-generation" in provider.agent_models["researcher"]
    assert provider.agent_models["researcher"]["text-generation"] == "model1"


def test_assign_model_to_agent_invalid_model(mock_model_manager):
    """Test assign_model_to_agent method with an invalid model ID."""
    provider = AgentModelProvider(mock_model_manager)

    # Try to assign an invalid model to the researcher agent
    with pytest.raises(ValueError):
        provider.assign_model_to_agent("researcher", "invalid_model", "text-generation")


def test_get_agent_model_assignments(mock_model_manager):
    """Test get_agent_model_assignments method."""
    provider = AgentModelProvider(mock_model_manager)

    # Assign models to agents
    provider.agent_models["researcher"] = {"text-generation": "model1"}
    provider.agent_models["developer"] = {
        "text-generation": "model2",
        "embedding": "model3",
    }

    # Get the agent model assignments
    assignments = provider.get_agent_model_assignments()

    # Check that the assignments are correct
    assert "researcher" in assignments
    assert "developer" in assignments
    assert assignments["researcher"]["text-generation"] == "model1"
    assert assignments["developer"]["text-generation"] == "model2"
    assert assignments["developer"]["embedding"] == "model3"
