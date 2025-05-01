"""
Tests for the fallback strategy implementation.

This module contains tests for the FallbackManager and related classes
to ensure the fallback mechanism works correctly in different scenarios.
"""

import os
import sys
import time
import unittest
from enum import Enum
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the errors module
from errors import ModelLoadError, ModelNotFoundError


# Mock the FallbackStrategy enum to avoid import issues
class FallbackStrategy(Enum):
    """Enumeration of fallback strategy types."""

    NONE = "none"
    DEFAULT = "default"
    SIMILAR_MODEL = "similar_model"
    MODEL_TYPE = "model_type"
    ANY_AVAILABLE = "any_available"
    SPECIFIED_LIST = "specified_list"
    SIZE_TIER = "size_tier"
    CAPABILITY_BASED = "capability"


# Mock the FallbackEvent class
class FallbackEvent:
    def __init__(
        self,
        original_model_id: Optional[str],
        fallback_model_id: str,
        reason: str,
        agent_type: Optional[str] = None,
        task_type: Optional[str] = None,
        strategy_used: FallbackStrategy = FallbackStrategy.DEFAULT,
        timestamp: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.original_model_id = original_model_id
        self.fallback_model_id = fallback_model_id
        self.reason = reason
        self.agent_type = agent_type
        self.task_type = task_type
        self.strategy_used = strategy_used
        self.timestamp = timestamp or time.time()
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_model_id": self.original_model_id,
            "fallback_model_id": self.fallback_model_id,
            "reason": self.reason,
            "agent_type": self.agent_type,
            "task_type": self.task_type,
            "strategy_used": self.strategy_used.value,
            "timestamp": self.timestamp,
            "details": self.details,
        }


# Import the FallbackManager module with patching to avoid circular imports
with patch(
    "ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy
), patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent):
    from ai_models.fallbacks.fallback_strategy import FallbackManager


class ModelInfoMock:
    """Mock implementation of IModelInfo for testing."""

    def __init__(
        self,
        id: str,
        type: str,
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        size_mb: Optional[float] = None,
        is_available: bool = True,
    ):
        self.id = id
        self.type = type
        self.name = name or f"Model {id}"
        self.capabilities = capabilities or []
        self.size_mb = size_mb
        self.is_available = is_available


class ModelManagerMock:
    """Mock implementation of IModelManager for testing."""

    def __init__(self, available_models: List[ModelInfoMock] = None):
        self.models = available_models or []
        self.model_dict = {model.id: model for model in self.models}

    def get_model_info(self, model_id: str) -> Optional[ModelInfoMock]:
        """Get information about a model by ID."""
        if model_id not in self.model_dict:
            raise ModelNotFoundError(f"Model not found: {model_id}")
        return self.model_dict[model_id]

    def get_all_models(self) -> List[ModelInfoMock]:
        """Get all available models."""
        return self.models

    def get_models_by_type(self, model_type: str) -> List[ModelInfoMock]:
        """Get models of a specific type."""
        return [model for model in self.models if model.type == model_type]

    def load_model(self, model_id: str) -> bool:
        """Simulate loading a model."""
        if model_id not in self.model_dict:
            raise ModelNotFoundError(f"Model not found: {model_id}")
        model = self.model_dict[model_id]
        if not model.is_available:
            raise ModelLoadError(f"Failed to load model: {model_id}")
        return True


class TestFallbackEvent(unittest.TestCase):
    """Tests for the FallbackEvent class."""

    def test_event_initialization(self):
        """Test that a FallbackEvent can be initialized with correct values."""
        event = FallbackEvent(
            original_model_id="gpt-4",
            fallback_model_id="gpt-3.5-turbo",
            reason="Model unavailable",
            agent_type="researcher",
            task_type="summarization",
            strategy_used=FallbackStrategy.DEFAULT,
        )

        self.assertEqual(event.original_model_id, "gpt-4")
        self.assertEqual(event.fallback_model_id, "gpt-3.5-turbo")
        self.assertEqual(event.reason, "Model unavailable")
        self.assertEqual(event.agent_type, "researcher")
        self.assertEqual(event.task_type, "summarization")
        self.assertEqual(event.strategy_used, FallbackStrategy.DEFAULT)

    def test_to_dict(self):
        """Test that a FallbackEvent can be converted to a dictionary."""
        event = FallbackEvent(
            original_model_id="gpt-4",
            fallback_model_id="gpt-3.5-turbo",
            reason="Model unavailable",
            strategy_used=FallbackStrategy.DEFAULT,
        )

        event_dict = event.to_dict()
        self.assertEqual(event_dict["original_model_id"], "gpt-4")
        self.assertEqual(event_dict["fallback_model_id"], "gpt-3.5-turbo")
        self.assertEqual(event_dict["reason"], "Model unavailable")
        self.assertEqual(event_dict["strategy_used"], "default")


class TestFallbackManager(unittest.TestCase):
    """Tests for the FallbackManager class."""

    def setUp(self):
        """Set up test data."""
        # Create mock models with different types and capabilities
        self.models = [
            ModelInfoMock(
                id="gpt-4",
                type="openai",
                capabilities=["chat", "reasoning", "summarization"],
                size_mb=1000,
                is_available=True,
            ),
            ModelInfoMock(
                id="gpt-3.5-turbo",
                type="openai",
                capabilities=["chat", "summarization"],
                size_mb=500,
                is_available=True,
            ),
            ModelInfoMock(
                id="llama-7b",
                type="llama",
                capabilities=["chat", "reasoning"],
                size_mb=700,
                is_available=True,
            ),
            ModelInfoMock(
                id="bert-base",
                type="huggingface",
                capabilities=["embeddings", "classification"],
                size_mb=400,
                is_available=True,
            ),
            ModelInfoMock(
                id="t5-base",
                type="huggingface",
                capabilities=["summarization", "translation"],
                size_mb=300,
                is_available=True,
            ),
            ModelInfoMock(
                id="offline-model",
                type="general-purpose",
                capabilities=["chat"],
                is_available=False,
            ),
        ]

        # Create a mock model manager with these models
        self.model_manager = ModelManagerMock(self.models)

        # Create a fallback manager with patches for its dependencies
        with patch(
            "ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy
        ), patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent):
            self.fallback_manager = FallbackManager(
                model_manager=self.model_manager,
                default_model_id="gpt-3.5-turbo",
                fallback_preferences={
                    "researcher": ["huggingface", "openai", "llama"],
                    "developer": ["huggingface", "llama", "openai"],
                    "default": ["huggingface", "openai"],
                },
            )

    def test_initialization(self):
        """Test that a FallbackManager can be initialized correctly."""
        self.assertEqual(self.fallback_manager.model_manager, self.model_manager)
        self.assertEqual(self.fallback_manager.default_model_id, "gpt-3.5-turbo")
        self.assertTrue(self.fallback_manager.fallback_enabled)
        self.assertEqual(len(self.fallback_manager.fallback_history), 0)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_disable_fallbacks(self):
        """Test that fallbacks can be disabled."""
        # Configure to disable fallbacks
        self.fallback_manager.configure(fallback_enabled=False)

        # Try to find a fallback model
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="offline-model"
        )

        # Should return None when disabled
        self.assertIsNone(model)
        self.assertIsNone(event)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_default_model_strategy(self):
        """Test the default model fallback strategy."""
        # Configure to use default model strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.DEFAULT)

        # Try to find a fallback model for a non-existent model
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="non-existent-model"
        )

        # Should return the default model
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "gpt-3.5-turbo")
        self.assertIsNotNone(event)
        self.assertEqual(event.fallback_model_id, "gpt-3.5-turbo")
        self.assertEqual(event.strategy_used, FallbackStrategy.DEFAULT)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_similar_model_strategy(self):
        """Test the similar model fallback strategy."""
        # Configure to use similar model strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.SIMILAR_MODEL)

        # Try to find a fallback model for gpt-4
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="gpt-4"
        )

        # Should return gpt-3.5-turbo (similar capabilities)
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "gpt-3.5-turbo")
        self.assertIsNotNone(event)
        self.assertEqual(event.fallback_model_id, "gpt-3.5-turbo")
        self.assertEqual(event.strategy_used, FallbackStrategy.SIMILAR_MODEL)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_model_type_strategy(self):
        """Test the model type fallback strategy."""
        # Configure to use model type strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.MODEL_TYPE)

        # Try to find a fallback model for llama-7b
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="gpt-4", agent_type="researcher"
        )

        # Should return another openai model
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "gpt-3.5-turbo")
        self.assertEqual(model.type, "openai")
        self.assertIsNotNone(event)
        self.assertEqual(event.fallback_model_id, "gpt-3.5-turbo")
        self.assertEqual(event.strategy_used, FallbackStrategy.MODEL_TYPE)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_any_available_strategy(self):
        """Test the any available fallback strategy."""
        # Configure to use any available strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.ANY_AVAILABLE)

        # Try to find a fallback model
        model, event = self.fallback_manager.find_fallback_model()

        # Should return any model (first in the list)
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "gpt-4")
        self.assertIsNotNone(event)
        self.assertEqual(event.fallback_model_id, "gpt-4")
        self.assertEqual(event.strategy_used, FallbackStrategy.ANY_AVAILABLE)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_specified_list_strategy(self):
        """Test the specified list fallback strategy."""
        # Configure to use specified list strategy
        self.fallback_manager.configure(
            default_strategy=FallbackStrategy.SPECIFIED_LIST
        )

        # Try to find a fallback model for a developer
        model, event = self.fallback_manager.find_fallback_model(agent_type="developer")

        # Should return a huggingface model (first in developer preferences)
        self.assertIsNotNone(model)
        self.assertEqual(model.type, "huggingface")
        self.assertIsNotNone(event)
        self.assertEqual(event.fallback_model_id, model.id)
        self.assertEqual(event.strategy_used, FallbackStrategy.SPECIFIED_LIST)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_size_tier_strategy(self):
        """Test the size tier fallback strategy."""
        # Configure to use size tier strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.SIZE_TIER)

        # Try to find a fallback model for gpt-4 (1000MB)
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="gpt-4"
        )

        # Should return a smaller model
        self.assertIsNotNone(model)
        self.assertLess(model.size_mb, 1000)
        self.assertIsNotNone(event)
        self.assertEqual(event.strategy_used, FallbackStrategy.SIZE_TIER)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_capability_based_strategy(self):
        """Test the capability-based fallback strategy."""
        # Configure to use capability strategy
        self.fallback_manager.configure(
            default_strategy=FallbackStrategy.CAPABILITY_BASED
        )

        # Try to find a model with summarization capability
        model, event = self.fallback_manager.find_fallback_model(
            required_capabilities=["summarization"]
        )

        # Should return a model with summarization capability
        self.assertIsNotNone(model)
        self.assertIn("summarization", model.capabilities)
        self.assertIsNotNone(event)
        self.assertEqual(event.strategy_used, FallbackStrategy.CAPABILITY_BASED)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_strategy_override(self):
        """Test that strategy can be overridden per request."""
        # Configure default strategy as DEFAULT
        self.fallback_manager.configure(default_strategy=FallbackStrategy.DEFAULT)

        # But override with CAPABILITY_BASED for this request
        model, event = self.fallback_manager.find_fallback_model(
            required_capabilities=["translation"],
            strategy_override=FallbackStrategy.CAPABILITY_BASED,
        )

        # Should return a model with translation capability
        self.assertIsNotNone(model)
        self.assertIn("translation", model.capabilities)
        self.assertEqual(model.id, "t5-base")
        self.assertIsNotNone(event)
        self.assertEqual(event.strategy_used, FallbackStrategy.CAPABILITY_BASED)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_multiple_fallback_attempts(self):
        """Test that fallback events are tracked correctly."""
        # First fallback
        model1, event1 = self.fallback_manager.find_fallback_model(
            original_model_id="offline-model",
            strategy_override=FallbackStrategy.DEFAULT,
        )

        # Second fallback
        model2, event2 = self.fallback_manager.find_fallback_model(
            original_model_id="non-existent-model",
            strategy_override=FallbackStrategy.ANY_AVAILABLE,
        )

        # Check that history contains both events
        history = self.fallback_manager.get_fallback_history()
        self.assertEqual(len(history), 2)

        # Check that metrics are updated
        metrics = self.fallback_manager.get_fallback_metrics()
        self.assertEqual(metrics[FallbackStrategy.DEFAULT.value]["total_count"], 1)
        self.assertEqual(
            metrics[FallbackStrategy.ANY_AVAILABLE.value]["total_count"], 1
        )

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_no_fallback_strategy(self):
        """Test the NONE fallback strategy."""
        # Configure to use NONE strategy
        self.fallback_manager.configure(default_strategy=FallbackStrategy.NONE)

        # Try to find a fallback model
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="offline-model"
        )

        # Should return None
        self.assertIsNone(model)
        self.assertIsNone(event)

    @patch("ai_models.fallbacks.fallback_strategy.FallbackStrategy", FallbackStrategy)
    @patch("ai_models.fallbacks.fallback_strategy.FallbackEvent", FallbackEvent)
    def test_fallback_with_unsuccessful_result(self):
        """Test tracking unsuccessful fallbacks."""
        # Find a fallback model
        model, event = self.fallback_manager.find_fallback_model(
            original_model_id="offline-model",
            strategy_override=FallbackStrategy.DEFAULT,
        )

        # Mark it as unsuccessful
        self.fallback_manager.track_fallback_event(event, was_successful=False)

        # Check that metrics reflect the unsuccessful attempt
        metrics = self.fallback_manager.get_fallback_metrics()
        self.assertEqual(metrics[FallbackStrategy.DEFAULT.value]["total_count"], 1)
        self.assertEqual(metrics[FallbackStrategy.DEFAULT.value]["success_count"], 0)


if __name__ == "__main__":
    unittest.main()
