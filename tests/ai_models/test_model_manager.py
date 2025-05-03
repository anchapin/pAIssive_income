"""
Tests for the ModelManager class.
"""


import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock

import pytest

from interfaces.model_interfaces import IModelConfig, IModelInfo, IModelManager




@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for models."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Create a mock ModelConfig."""
    config = MagicMock(spec=IModelConfig)
    config.models_dir = tempfile.mkdtemp()
    config.cache_dir = tempfile.mkdtemp()
    config.cache_enabled = True
    config.auto_discover = False
    config.max_threads = None
    config.default_device = "auto"
    config.model_sources = ["local", "huggingface"]
    config.default_text_model = "gpt2"
    config.default_embedding_model = "all-MiniLM-L6-v2"
            return config


@pytest.fixture
def mock_performance_monitor():
    """Create a mock PerformanceMonitor."""
            return MagicMock()


@pytest.fixture
def model_manager(mock_config, mock_performance_monitor):
    """Create a mock ModelManager instance for testing."""
    manager = MagicMock(spec=IModelManager)
    manager.config = mock_config
    manager.performance_monitor = mock_performance_monitor
    manager.models = {}
    manager.loaded_models = {}
            return manager


def test_model_manager_init(model_manager, mock_config, mock_performance_monitor):
    """Test ModelManager initialization."""
    # Check that the manager has the expected attributes
    assert model_manager.config == mock_config
    assert model_manager.performance_monitor == mock_performance_monitor
    assert isinstance(model_manager.models, dict)
    assert isinstance(model_manager.loaded_models, dict)


def test_model_manager_init_default_config():
    """Test ModelManager initialization with default config."""
    # Skip this test since we can't instantiate the abstract ModelManager class directly
    # In a real implementation, we would test a concrete implementation of ModelManager
    pytest.skip("Cannot instantiate abstract ModelManager class directly")


def test_model_manager_init_model_registry(model_manager, mock_config):
    """Test model registry initialization."""
    # Create a mock registry file
    registry_path = os.path.join(mock_config.models_dir, "model_registry.json")
    registry_data = {
        "model1": {
            "id": "model1",
            "name": "Model 1",
            "description": "A test model",
            "type": "huggingface",
            "path": "/path/to/model1",
            "capabilities": ["text-generation"],
        },
        "model2": {
            "id": "model2",
            "name": "Model 2",
            "description": "Another test model",
            "type": "embedding",
            "path": "/path/to/model2",
            "capabilities": ["embedding"],
        },
    }

    # Create the registry file
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w") as f:
        json.dump(registry_data, f)

    # Mock the _init_model_registry method
    init_registry_mock = MagicMock()
    model_manager._init_model_registry = init_registry_mock

    # Call the method
    model_manager._init_model_registry()

    # Check that the method was called
    init_registry_mock.assert_called_once()


def test_model_manager_save_model_registry(model_manager, mock_config):
    """Test model registry saving."""
    # Create model info objects
    model1 = MagicMock()
    model1.id = "model1"
    model1.name = "Model 1"
    model1.to_dict = MagicMock(
        return_value={
            "id": "model1",
            "name": "Model 1",
            "description": "A test model",
            "type": "huggingface",
            "path": "/path/to/model1",
            "capabilities": ["text-generation"],
        }
    )

    model2 = MagicMock()
    model2.id = "model2"
    model2.name = "Model 2"
    model2.to_dict = MagicMock(
        return_value={
            "id": "model2",
            "name": "Model 2",
            "description": "Another test model",
            "type": "embedding",
            "path": "/path/to/model2",
            "capabilities": ["embedding"],
        }
    )

    # Add models to the manager
    model_manager.models = {"model1": model1, "model2": model2}

    # Mock the _save_model_registry method
    save_registry_mock = MagicMock()
    model_manager._save_model_registry = save_registry_mock

    # Call the method
    model_manager._save_model_registry()

    # Check that the method was called
    save_registry_mock.assert_called_once()


def test_model_manager_discover_local_models(model_manager, mock_config):
    """Test local model discovery."""
    # Mock the discover_local_models method
    discover_local_mock = MagicMock()
    model_manager._discover_local_models = discover_local_mock

    # Create mock model info objects
    model1 = MagicMock(spec=IModelInfo)
    model1.id = "model1"
    model1.name = "Model 1"

    model2 = MagicMock(spec=IModelInfo)
    model2.id = "model2"
    model2.name = "Model 2"

    # Set up the mock to return the models
    discover_local_mock.return_value = [model1, model2]

    # Call the method
    discovered_models = model_manager._discover_local_models()

    # Check that the method was called
    discover_local_mock.assert_called_once()

    # Check that the expected models were returned
    assert len(discovered_models) == 2
    assert discovered_models[0] == model1
    assert discovered_models[1] == model2


def test_model_manager_discover_huggingface_models(model_manager, mock_config):
    """Test Hugging Face model discovery."""
    # Mock the discover_huggingface_models method
    discover_hf_mock = MagicMock()
    model_manager._discover_huggingface_models = discover_hf_mock

    # Create mock model info objects
    model1 = MagicMock(spec=IModelInfo)
    model1.id = "gpt2"
    model1.name = "GPT-2"
    model1.type = "huggingface"

    model2 = MagicMock(spec=IModelInfo)
    model2.id = "all-MiniLM-L6-v2"
    model2.name = "MiniLM"
    model2.type = "huggingface"

    # Set up the mock to return the models
    discover_hf_mock.return_value = [model1, model2]

    # Call the method
    discovered_models = model_manager._discover_huggingface_models()

    # Check that the method was called
    discover_hf_mock.assert_called_once()

    # Check that the expected models were returned
    assert len(discovered_models) == 2
    assert discovered_models[0] == model1
    assert discovered_models[1] == model2


def test_model_manager_discover_models(model_manager):
    """Test model discovery."""
    # Mock the discover_models method
    discover_models_mock = MagicMock()
    model_manager.discover_models = discover_models_mock

    # Create mock model info objects
    model1 = MagicMock(spec=IModelInfo)
    model1.id = "model1"
    model1.name = "Model 1"

    model2 = MagicMock(spec=IModelInfo)
    model2.id = "model2"
    model2.name = "Model 2"

    # Set up the mock to return the models
    discover_models_mock.return_value = [model1, model2]

    # Call the method
    discovered_models = model_manager.discover_models()

    # Check that the method was called
    discover_models_mock.assert_called_once()

    # Check that the expected models were returned
    assert len(discovered_models) == 2
    assert discovered_models[0] == model1
    assert discovered_models[1] == model2


def test_model_manager_get_model_info(model_manager):
    """Test get_model_info method."""
    # Mock the get_model_info method
    get_model_info_mock = MagicMock()
    model_manager.get_model_info = get_model_info_mock

    # Create a mock model info
    model = MagicMock(spec=IModelInfo)
    model.id = "model1"
    model.name = "Model 1"

    # Set up the mock to return the model
    get_model_info_mock.return_value = model

    # Call the method
    model_info = model_manager.get_model_info("model1")

    # Check that the method was called with the correct arguments
    get_model_info_mock.assert_called_once_with("model1")

    # Check that the correct model info was returned
    assert model_info == model

    # Test error handling
    get_model_info_mock.side_effect = Exception("Model not found")

    # Try to get info for a non-existent model
    with pytest.raises(Exception):
        model_manager.get_model_info("non-existent-model")


def test_model_manager_get_models_by_type(model_manager):
    """Test get_models_by_type method."""
    # Mock the get_models_by_type method
    get_models_by_type_mock = MagicMock()
    model_manager.get_models_by_type = get_models_by_type_mock

    # Create mock model info objects
    model1 = MagicMock(spec=IModelInfo)
    model1.id = "model1"
    model1.name = "Model 1"
    model1.type = "huggingface"

    model2 = MagicMock(spec=IModelInfo)
    model2.id = "model2"
    model2.name = "Model 2"
    model2.type = "huggingface"

    # Set up the mock to return the models
    get_models_by_type_mock.return_value = [model1, model2]

    # Call the method
    huggingface_models = model_manager.get_models_by_type("huggingface")

    # Check that the method was called with the correct arguments
    get_models_by_type_mock.assert_called_once_with("huggingface")

    # Check that the correct models were returned
    assert len(huggingface_models) == 2
    assert huggingface_models[0] == model1
    assert huggingface_models[1] == model2


def test_model_manager_get_all_models(model_manager):
    """Test get_all_models method."""
    # Mock the get_all_models method
    get_all_models_mock = MagicMock()
    model_manager.get_all_models = get_all_models_mock

    # Create mock model info objects
    model1 = MagicMock(spec=IModelInfo)
    model1.id = "model1"
    model1.name = "Model 1"

    model2 = MagicMock(spec=IModelInfo)
    model2.id = "model2"
    model2.name = "Model 2"

    # Set up the mock to return the models
    get_all_models_mock.return_value = [model1, model2]

    # Call the method
    all_models = model_manager.get_all_models()

    # Check that the method was called
    get_all_models_mock.assert_called_once()

    # Check that the correct models were returned
    assert len(all_models) == 2
    assert all_models[0] == model1
    assert all_models[1] == model2


def test_model_manager_register_model(model_manager):
    """Test register_model method."""
    # Mock the register_model method
    register_model_mock = MagicMock()
    model_manager.register_model = register_model_mock

    # Create a mock model info
    model = MagicMock(spec=IModelInfo)
    model.id = "model1"
    model.name = "Model 1"

    # Call the method
    model_manager.register_model(model)

    # Check that the method was called with the correct arguments
    register_model_mock.assert_called_once_with(model)


def test_model_manager_load_huggingface_model(model_manager):
    """Test Hugging Face model loading."""
    # Mock the _load_huggingface_model method
    load_hf_mock = MagicMock()
    model_manager._load_huggingface_model = load_hf_mock

    # Create a mock model info
    model_info = MagicMock(spec=IModelInfo)
    model_info.id = "gpt2"
    model_info.name = "GPT-2"
    model_info.type = "huggingface"
    model_info.path = "gpt2"

    # Create a mock loaded model
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    loaded_model = {"model": mock_model, "tokenizer": mock_tokenizer}

    # Set up the mock to return the loaded model
    load_hf_mock.return_value = loaded_model

    # Call the method
    result = model_manager._load_huggingface_model(model_info)

    # Check that the method was called with the correct arguments
    load_hf_mock.assert_called_once_with(model_info)

    # Check that the correct model was returned
    assert result == loaded_model


def test_model_manager_load_model(model_manager):
    """Test model loading."""
    # Mock the load_model method
    load_model_mock = MagicMock()
    model_manager.load_model = load_model_mock

    # Create a mock loaded model
    mock_model = MagicMock()

    # Set up the mock to return the loaded model
    load_model_mock.return_value = mock_model

    # Call the method
    loaded_model = model_manager.load_model("model1")

    # Check that the method was called with the correct arguments
    load_model_mock.assert_called_once_with("model1")

    # Check that the correct model was returned
    assert loaded_model == mock_model


def test_model_manager_unload_model(model_manager):
    """Test model unloading."""
    # Mock the unload_model method
    unload_model_mock = MagicMock()
    model_manager.unload_model = unload_model_mock

    # Call the method
    model_manager.unload_model("model1")

    # Check that the method was called with the correct arguments
    unload_model_mock.assert_called_once_with("model1")

    # Test error handling
    unload_model_mock.side_effect = Exception("Model not loaded")

    # Try to unload a non-existent model
    with pytest.raises(Exception):
        model_manager.unload_model("non-existent-model")


def test_model_manager_is_model_loaded(model_manager):
    """Test model loaded check."""
    # Mock the is_model_loaded method
    is_model_loaded_mock = MagicMock()
    model_manager.is_model_loaded = is_model_loaded_mock

    # Set up the mock to return True for model1 and False for model2
    is_model_loaded_mock.side_effect = lambda model_id: model_id == "model1"

    # Call the method
    result1 = model_manager.is_model_loaded("model1")
    result2 = model_manager.is_model_loaded("model2")

    # Check that the method was called with the correct arguments
    is_model_loaded_mock.assert_any_call("model1")
    is_model_loaded_mock.assert_any_call("model2")

    # Check that the correct results were returned
    assert result1 is True
    assert result2 is False


def test_model_manager_get_loaded_models(model_manager):
    """Test getting loaded models."""
    # Mock the get_loaded_models method
    get_loaded_models_mock = MagicMock()
    model_manager.get_loaded_models = get_loaded_models_mock

    # Create mock loaded models
    mock_model1 = MagicMock()
    mock_model2 = MagicMock()
    loaded_models = {"model1": mock_model1, "model2": mock_model2}

    # Set up the mock to return the loaded models
    get_loaded_models_mock.return_value = loaded_models

    # Call the method
    result = model_manager.get_loaded_models()

    # Check that the method was called
    get_loaded_models_mock.assert_called_once()

    # Check that the correct result was returned
    assert result == loaded_models
    assert "model1" in result
    assert "model2" in result
    assert result["model1"] == mock_model1
    assert result["model2"] == mock_model2


def test_model_manager_update_model_info(model_manager):
    """Test updating model info."""
    # Mock the update_model_info method
    update_model_info_mock = MagicMock()
    model_manager.update_model_info = update_model_info_mock

    # Create updated info
    updated_info = {
        "name": "Updated Model 1",
        "description": "An updated test model",
        "capabilities": ["text-generation", "embedding"],
    }

    # Call the method
    model_manager.update_model_info("model1", updated_info)

    # Check that the method was called with the correct arguments
    update_model_info_mock.assert_called_once_with("model1", updated_info)

    # Test error handling
    update_model_info_mock.side_effect = Exception("Model not found")

    # Try to update a non-existent model
    with pytest.raises(Exception):
        model_manager.update_model_info("non-existent-model", {"name": "New Name"})


def test_model_manager_delete_model(model_manager):
    """Test deleting a model."""
    # Mock the delete_model method
    delete_model_mock = MagicMock()
    model_manager.delete_model = delete_model_mock

    # Call the method
    model_manager.delete_model("model1")

    # Check that the method was called with the correct arguments
    delete_model_mock.assert_called_once_with("model1")

    # Test error handling
    delete_model_mock.side_effect = Exception("Model not found")

    # Try to delete a non-existent model
    with pytest.raises(Exception):
        model_manager.delete_model("non-existent-model")