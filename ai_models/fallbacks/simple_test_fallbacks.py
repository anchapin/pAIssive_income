
import logging
import os
import sys
from ai_models.fallbacks import FallbackManager, FallbackStrategy

"""
Simplified test script for model fallback functionality.

This script tests the model fallback mechanisms using mock objects
to avoid circular import issues.
"""

import logging
import os
import sys

# Add the project root to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import only what we need from our fallbacks module
from ai_models.fallbacks import FallbackManager, FallbackStrategy


# Create mock classes to avoid circular imports
class MockModelInfo:
    """Mock model info class for testing purposes."""

    def __init__(self, id, name, type, path, capabilities=None, size_mb=0):
        self.id = id
        self.name = name
        self.type = type
        self.path = path
        self.capabilities = capabilities or []
        self.size_mb = size_mb

    def __str__(self):
        return f"{self.name} ({self.type})"


class MockModelManager:
    """Mock model manager class for testing purposes."""

    def __init__(self):
        self.models = {}

    def register_model(self, model):
        """Register a mock model."""
        self.models[model.id] = model
        return model

    def get_model_info(self, model_id):
        """Get mock model info."""
        return self.models.get(model_id)

    def get_models_by_type(self, model_type):
        """Get mock models by type."""
        return [m for m in self.models.values() if m.type == model_type]

    def get_all_models(self):
        """Get all mock models."""
        return list(self.models.values())


def setup_test_environment():
    """Set up a test environment with mock models."""
    print("\n=== Setting up mock test environment ===")

    # Create a mock model manager
    manager = MockModelManager()

    # Register some test models
    models = [
        MockModelInfo(
            id="model1",
            name="Primary Model",
            type="huggingface",
            path="/path/to/model1",
            capabilities=["text-generation", "classification"],
        ),
        MockModelInfo(
            id="model2",
            name="Secondary Model",
            type="llama",
            path="/path/to/model2",
            capabilities=["text-generation"],
        ),
        MockModelInfo(
            id="model3",
            name="Embedding Model",
            type="embedding",
            path="/path/to/model3",
            capabilities=["embedding"],
        ),
        MockModelInfo(
            id="model4",
            name="Small Model",
            type="huggingface",
            path="/path/to/model4",
            size_mb=100,
            capabilities=["text-generation"],
        ),
    ]

    for model in models:
        manager.register_model(model)
        print(f"Registered test model: {model.name} ({model.id}) - Type: {model.type}")

    return manager


def test_fallback_strategies(manager):
    """Test different fallback strategies."""
    print("\n=== Test: Fallback Strategies ===")

    # Create a FallbackManager directly
    fallback_manager = FallbackManager(
        model_manager=manager,
        fallback_enabled=True,
        default_strategy=FallbackStrategy.DEFAULT,
        default_model_id="model1",  # Set the default model to model1
    )

    strategies_to_test = [
        FallbackStrategy.DEFAULT,
        FallbackStrategy.SIMILAR_MODEL,
        FallbackStrategy.MODEL_TYPE,
        FallbackStrategy.ANY_AVAILABLE,
        FallbackStrategy.SPECIFIED_LIST,
        FallbackStrategy.SIZE_TIER,
        FallbackStrategy.CAPABILITY_BASED,
    ]

    for strategy in strategies_to_test:
        # Try finding a fallback model with the strategy
        print(f"\nTesting strategy: {strategy.value}")

        fallback_model, event = fallback_manager.find_fallback_model(
            original_model_id="non_existent_model",
            agent_type="researcher",
            task_type="text-generation",
            strategy_override=strategy,
        )

        if fallback_model:
            print(
                f"✅ Strategy {strategy.value} found fallback model: {fallback_model.name}"
            )
        else:
            print(f"❌ Strategy {strategy.value} failed to find a fallback model")

    # Test capability-based strategy with specific capabilities
    print("\nTesting capability-based with specific requirements:")
    fallback_model, _ = fallback_manager.find_fallback_model(
        required_capabilities=["text-generation", "classification"],
        strategy_override=FallbackStrategy.CAPABILITY_BASED,
    )

    if fallback_model:
        print(f"✅ Found model with required capabilities: {fallback_model.name}")
    else:
        print("❌ Failed to find model with required capabilities")


def test_fallback_metrics(manager):
    """Test fallback metrics tracking."""
    print("\n=== Test: Fallback Metrics ===")

    # Create a FallbackManager
    fallback_manager = FallbackManager(model_manager=manager, fallback_enabled=True)

    # Generate some fallback events
    strategies = [
        FallbackStrategy.DEFAULT,
        FallbackStrategy.SIMILAR_MODEL,
        FallbackStrategy.MODEL_TYPE,
        FallbackStrategy.ANY_AVAILABLE,
    ]

    # Create several fallback events with different strategies
    for strategy in strategies:
        for i in range(3):  # Create 3 events per strategy
            fallback_model, event = fallback_manager.find_fallback_model(
                original_model_id=f"non_existent_model_{i}",
                agent_type="tester",
                strategy_override=strategy,
            )

            if event and i == 0:  # Mark some as unsuccessful for testing
                fallback_manager.track_fallback_event(event, was_successful=False)

    # Get and display metrics
    metrics = fallback_manager.get_fallback_metrics()

    print("\nFallback Metrics:")
    for strategy, stats in metrics.items():
        if stats["total_count"] > 0:
            success_rate = stats["success_count"] / stats["total_count"]
            print(f"Strategy: {strategy}")
            print(
                f"  Success rate: {success_rate:.2f} ({stats['success_count']}/{stats['total_count']})"
            )

    # Get fallback history
    history = fallback_manager.get_fallback_history(limit=5)
    print(f"\nRecent fallback events: {len(history)}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Set up test environment
    manager = setup_test_environment()

    # Run tests
    test_fallback_strategies(manager)
    test_fallback_metrics(manager)

    print("\n=== All tests completed ===")
