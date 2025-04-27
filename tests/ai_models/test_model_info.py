"""
Tests for the ModelInfo class.
"""
import pytest
from unittest.mock import patch
from datetime import datetime
import json

from ai_models.model_manager import ModelInfo


def test_model_info_init():
    """Test ModelInfo initialization."""
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation", "embedding"]
    )
    
    # Check that the model info has the expected attributes
    assert model_info.id == "test-model"
    assert model_info.name == "Test Model"
    assert model_info.description == "A test model"
    assert model_info.type == "huggingface"
    assert model_info.path == "/path/to/model"
    assert model_info.capabilities == ["text-generation", "embedding"]
    assert isinstance(model_info.metadata, dict)
    assert isinstance(model_info.performance, dict)
    assert isinstance(model_info.created_at, str)
    assert isinstance(model_info.updated_at, str)


def test_model_info_with_metadata():
    """Test ModelInfo initialization with metadata."""
    metadata = {
        "model_size": "7B",
        "context_length": 2048,
        "quantization": None,
        "license": "MIT",
    }
    
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"],
        metadata=metadata
    )
    
    # Check that the metadata was set
    assert model_info.metadata == metadata
    assert model_info.metadata["model_size"] == "7B"
    assert model_info.metadata["context_length"] == 2048
    assert model_info.metadata["quantization"] is None
    assert model_info.metadata["license"] == "MIT"


def test_model_info_with_performance():
    """Test ModelInfo initialization with performance metrics."""
    performance = {
        "latency_ms": 100,
        "throughput": 10,
        "memory_usage_mb": 1000,
    }
    
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"],
        performance=performance
    )
    
    # Check that the performance metrics were set
    assert model_info.performance == performance
    assert model_info.performance["latency_ms"] == 100
    assert model_info.performance["throughput"] == 10
    assert model_info.performance["memory_usage_mb"] == 1000


def test_model_info_to_dict():
    """Test to_dict method."""
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"]
    )
    
    # Convert to dictionary
    model_dict = model_info.to_dict()
    
    # Check that the dictionary has the expected keys
    assert "id" in model_dict
    assert "name" in model_dict
    assert "description" in model_dict
    assert "type" in model_dict
    assert "path" in model_dict
    assert "capabilities" in model_dict
    assert "metadata" in model_dict
    assert "performance" in model_dict
    assert "created_at" in model_dict
    assert "updated_at" in model_dict
    
    # Check that the values are correct
    assert model_dict["id"] == "test-model"
    assert model_dict["name"] == "Test Model"
    assert model_dict["description"] == "A test model"
    assert model_dict["type"] == "huggingface"
    assert model_dict["path"] == "/path/to/model"
    assert model_dict["capabilities"] == ["text-generation"]


def test_model_info_to_json():
    """Test to_json method."""
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"]
    )
    
    # Convert to JSON
    model_json = model_info.to_json()
    
    # Check that the JSON is valid
    model_dict = json.loads(model_json)
    assert "id" in model_dict
    assert "name" in model_dict
    assert model_dict["id"] == "test-model"
    assert model_dict["name"] == "Test Model"


def test_model_info_from_dict():
    """Test from_dict method."""
    model_dict = {
        "id": "test-model",
        "name": "Test Model",
        "description": "A test model",
        "type": "huggingface",
        "path": "/path/to/model",
        "capabilities": ["text-generation"],
        "metadata": {
            "model_size": "7B",
            "context_length": 2048,
        },
        "performance": {
            "latency_ms": 100,
            "throughput": 10,
        },
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00",
    }
    
    # Create ModelInfo from dictionary
    model_info = ModelInfo.from_dict(model_dict)
    
    # Check that the ModelInfo has the expected attributes
    assert model_info.id == "test-model"
    assert model_info.name == "Test Model"
    assert model_info.description == "A test model"
    assert model_info.type == "huggingface"
    assert model_info.path == "/path/to/model"
    assert model_info.capabilities == ["text-generation"]
    assert model_info.metadata["model_size"] == "7B"
    assert model_info.metadata["context_length"] == 2048
    assert model_info.performance["latency_ms"] == 100
    assert model_info.performance["throughput"] == 10
    assert model_info.created_at == "2023-01-01T12:00:00"
    assert model_info.updated_at == "2023-01-01T12:00:00"


def test_model_info_update_performance():
    """Test update_performance method."""
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"]
    )
    
    # Initial performance should be empty
    assert model_info.performance == {}
    
    # Update performance
    model_info.update_performance({
        "latency_ms": 100,
        "throughput": 10,
        "memory_usage_mb": 1000,
    })
    
    # Check that the performance was updated
    assert model_info.performance["latency_ms"] == 100
    assert model_info.performance["throughput"] == 10
    assert model_info.performance["memory_usage_mb"] == 1000
    
    # Update performance again
    model_info.update_performance({
        "latency_ms": 50,  # Changed
        "throughput": 20,  # Changed
        "accuracy": 0.95,  # New
    })
    
    # Check that the performance was updated and merged
    assert model_info.performance["latency_ms"] == 50
    assert model_info.performance["throughput"] == 20
    assert model_info.performance["memory_usage_mb"] == 1000
    assert model_info.performance["accuracy"] == 0.95


@patch('ai_models.model_manager.datetime')
def test_model_info_update_timestamp(mock_datetime):
    """Test that update_performance updates the timestamp."""
    # Mock datetime.now() to return a fixed datetime
    mock_now = datetime(2023, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_now
    
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation"]
    )
    
    # Set initial updated_at to a different value
    model_info.updated_at = "2022-01-01T12:00:00"
    
    # Update performance
    model_info.update_performance({"latency_ms": 100})
    
    # Check that updated_at was updated to the mocked datetime
    assert model_info.updated_at == mock_now.isoformat()


def test_model_info_has_capability():
    """Test has_capability method."""
    model_info = ModelInfo(
        id="test-model",
        name="Test Model",
        description="A test model",
        type="huggingface",
        path="/path/to/model",
        capabilities=["text-generation", "embedding"]
    )
    
    # Check capabilities
    assert model_info.has_capability("text-generation") is True
    assert model_info.has_capability("embedding") is True
    assert model_info.has_capability("classification") is False
    assert model_info.has_capability("summarization") is False
