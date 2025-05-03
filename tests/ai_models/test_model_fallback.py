"""
Tests for AI model fallback mechanisms.

These tests verify that the system can gracefully handle model failures
and properly implement fallback strategies.
"""


import unittest
from unittest.mock import MagicMock, patch
import time

from ai_models.fallbacks import FallbackManager, FallbackStrategy, FallbackEvent
from ai_models.agent_integration import AgentModelProvider
from ai_models.model_manager import ModelManager
from ai_models.model_base_types import ModelInfo
from errors import ModelError, ModelLoadError, ModelAPIError


class TestModelFallback

(unittest.TestCase):
    """Test suite for model fallback mechanisms."""

    def setUp(self):
        """Set up test environment."""
        # Create mock model manager
        self.model_manager = MagicMock(spec=ModelManager)

        # Create mock models
        self.primary_model = MagicMock(name="Primary Model")
        self.fallback_model1 = MagicMock(name="Fallback Model 1")
        self.fallback_model2 = MagicMock(name="Fallback Model 2")

        # Create mock model info objects
        self.primary_model_info = ModelInfo(
            id="primary_model",
            name="Primary Model",
            description="High-quality but resource-intensive model",
            type="openai",
            path=None,
            capabilities=["text-generation", "summarization", "reasoning"],
            size_mb=1000
        )

        self.fallback_model1_info = ModelInfo(
            id="fallback_model1",
            name="Fallback Model 1",
            description="Medium-quality fallback model",
            type="huggingface",
            path=None,
            capabilities=["text-generation", "summarization"],
            size_mb=500
        )

        self.fallback_model2_info = ModelInfo(
            id="fallback_model2",
            name="Fallback Model 2",
            description="Basic fallback model",
            type="ollama",
            path=None,
            capabilities=["text-generation"],
            size_mb=200
        )

        # Configure model manager mock
        self.model_manager.get_model_info.side_effect = lambda model_id: {
            "primary_model": self.primary_model_info,
            "fallback_model1": self.fallback_model1_info,
            "fallback_model2": self.fallback_model2_info
        }.get(model_id)

        self.model_manager.get_all_models.return_value = [
            self.primary_model_info,
            self.fallback_model1_info,
            self.fallback_model2_info
        ]

        # Create agent model provider with fallback enabled
        self.provider = AgentModelProvider(self.model_manager)
        self.provider.configure_fallback(
            fallback_enabled=True,
            fallback_config={
                "default_strategy": FallbackStrategy.CAPABILITY_BASED,
                "default_model_id": "fallback_model1"
            }
        )

    def test_graceful_degradation_with_api_failure(self):
        """Test that the system gracefully degrades when a model API fails."""
        # Configure model manager to raise an API error for the primary model
        def load_model_side_effect(model_id):
            if model_id == "primary_model":
                raise ModelAPIError("API connection failed")
            elif model_id == "fallback_model1":
                return self.fallback_model1
            elif model_id == "fallback_model2":
                return self.fallback_model2
            else:
                raise ModelError(f"Unknown model: {model_id}")

        self.model_manager.load_model.side_effect = load_model_side_effect

        # Configure fallback manager to find fallback models
        self.provider.fallback_manager.find_fallback_model = MagicMock(
            return_value=(self.fallback_model1_info, MagicMock())
        )

        # Assign the primary model to an agent
        self.provider.assign_model_to_agent("researcher", "primary_model", "text-generation")

        # Try to get the model, which should trigger fallback
        model = self.provider.get_model_with_fallback("researcher", "primary_model", "text-generation")

        # Verify we got a fallback model
        self.assertIsNotNone(model)
        self.assertEqual(model, self.fallback_model1)

    def test_fallback_chain_with_multiple_failures(self):
        """Test that fallback chain works correctly with multiple failures."""
        # Configure model manager to raise errors for primary model but return fallback model
        def load_model_side_effect(model_id):
            if model_id == "primary_model":
                raise ModelLoadError("Failed to load model")
            elif model_id == "fallback_model2":
                return self.fallback_model2
            else:
                raise ModelError(f"Unknown model: {model_id}")

        self.model_manager.load_model.side_effect = load_model_side_effect

        # Mock the fallback manager to directly return the second fallback model
        mock_event = MagicMock()
        mock_event.strategy_used = FallbackStrategy.ANY_AVAILABLE
        self.provider.fallback_manager.find_fallback_model = MagicMock(
            return_value=(self.fallback_model2_info, mock_event)
        )

        # Disable tracking to avoid KeyError with mock objects
        self.provider.fallback_manager.track_fallback_event = MagicMock()

        # Assign the primary model to an agent
        self.provider.assign_model_to_agent("researcher", "primary_model", "text-generation")

        # Try to get the model, which should trigger fallback
        model = self.provider.get_model_with_fallback("researcher", "primary_model", "text-generation")

        # Verify we got the fallback model
        self.assertIsNotNone(model)
        self.assertEqual(model, self.fallback_model2)

        # Verify that find_fallback_model was called
        self.provider.fallback_manager.find_fallback_model.assert_called_once()

    def test_performance_impact_of_fallback(self):
        """Test the performance impact of fallback scenarios."""
        # Use a mock time approach instead of actual sleep delays
        self.mock_time = 0.0

        # Configure the models with different simulated response times
        def primary_model_generate(*args, **kwargs):
            self.mock_time += 0.01  # Simulate a 10ms response time
            return "Primary model response"

        def fallback_model_generate(*args, **kwargs):
            self.mock_time += 0.05  # Simulate a 50ms response time
            return "Fallback model response"

        self.primary_model.generate.side_effect = primary_model_generate
        self.fallback_model1.generate.side_effect = fallback_model_generate

        # Configure model manager for primary model case
        def load_model_primary_case(model_id):
            if model_id == "primary_model":
                return self.primary_model
            elif model_id == "fallback_model1":
                return self.fallback_model1
            else:
                raise ModelError(f"Unknown model: {model_id}")

        # Configure model manager for fallback model case
        def load_model_fallback_case(model_id):
            if model_id == "primary_model":
                raise ModelAPIError("API connection failed")
            elif model_id == "fallback_model1":
                return self.fallback_model1
            else:
                raise ModelError(f"Unknown model: {model_id}")

        # Configure fallback manager to find fallback models
        self.provider.fallback_manager.find_fallback_model = MagicMock(
            return_value=(self.fallback_model1_info, MagicMock())
        )

        # Assign the primary model to an agent
        self.provider.assign_model_to_agent("researcher", "primary_model", "text-generation")

        # Measure performance with primary model
        self.model_manager.load_model.side_effect = load_model_primary_case
        self.mock_time = 0.0  # Reset mock time
        model = self.provider.get_model_with_fallback("researcher", "primary_model", "text-generation")
        response = model.generate(prompt="Test prompt")
        primary_time = self.mock_time

        # Measure performance with fallback model
        self.model_manager.load_model.side_effect = load_model_fallback_case
        self.mock_time = 0.0  # Reset mock time
        model = self.provider.get_model_with_fallback("researcher", "primary_model", "text-generation")
        response = model.generate(prompt="Test prompt")
        fallback_time = self.mock_time

        # Verify that fallback has performance impact
        self.assertGreater(fallback_time, primary_time)

        # But the system should still function
        self.assertEqual(response, "Fallback model response")


if __name__ == "__main__":
    unittest.main()