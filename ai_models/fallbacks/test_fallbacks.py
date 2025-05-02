"""
Test script for model fallback functionality.

This script demonstrates and tests the model fallback mechanisms to ensure
they work as expected under various scenarios.
"""

import logging
import os
import sys

# Add the project root to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ai_models.agent_integration import AgentModelProvider
from ai_models.fallbacks import FallbackManager, FallbackStrategy
from ai_models.model_manager import ModelInfo, ModelManager


def setup_test_environment():
    """Set up a test environment with a model manager and some test models."""
    print("\n=== Setting up test environment ===")

    # Create a model manager
    manager = ModelManager()

    # Clear any existing models for the test
    for model in list(manager.models.values()):
        manager.unregister_model(model.id)

    # Register some test models
    models = [
        ModelInfo(
            id="model1",
            name="Primary Model",
            type="huggingface",
            path="/path/to/model1",
            capabilities=["text-generation", "classification"],
        ),
        ModelInfo(
            id="model2",
            name="Secondary Model",
            type="llama",
            path="/path/to/model2",
            capabilities=["text-generation"],
        ),
        ModelInfo(
            id="model3",
            name="Embedding Model",
            type="embedding",
            path="/path/to/model3",
            capabilities=["embedding"],
        ),
        ModelInfo(
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


def test_basic_fallback(manager: ModelManager):
    """Test basic fallback functionality."""
    print("\n=== Test 1: Basic Fallback ===")

    # Create a provider with fallback enabled
    provider = AgentModelProvider(manager, fallback_enabled=True)

    # Configure fallback preferences
    provider.configure_fallback(
        fallback_enabled=True,
        fallback_config={
            "max_attempts": 3,
            "fallback_preferences": {
                "researcher": ["huggingface", "llama", "embedding"],
                "developer": ["llama", "huggingface", "embedding"],
                "default": ["huggingface", "llama"],
            },
        },
    )

    # Assign a non-existent model to the researcher agent
    try:
        # Force a fallback by trying to use a non-existent model
        provider.agent_models["researcher"] = {"text-generation": "non_existent_model"}

        # Try to get a model for the researcher agent
        model = provider.get_model_for_agent("researcher", "text-generation")

        # Check which model was used as fallback
        assignments = provider.get_agent_model_assignments()
        model_id = assignments["researcher"]["text-generation"]
        model_info = manager.get_model_info(model_id)

        print(
            f"Successfully fell back to model: {model_info.name} ({model_info.id}) - Type: {model_info.type}"
        )
        print("Basic fallback test PASSED")
    except ValueError as e:
        print(f"Basic fallback test FAILED: {e}")


def test_fallback_strategies(manager: ModelManager):
    """Test different fallback strategies."""
    print("\n=== Test 2: Fallback Strategies ===")

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
            print(f"✅ Strategy {strategy.value} found fallback model: {fallback_model.name}")
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


def test_fallback_metrics(manager: ModelManager):
    """Test fallback metrics tracking."""
    print("\n=== Test 3: Fallback Metrics ===")

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

            # Randomly mark some as unsuccessful
            if i == 0:
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


def test_agent_integration(manager: ModelManager):
    """Test integration with the AgentModelProvider."""
    print("\n=== Test 4: Agent Integration ===")

    # Create a provider with fallback enabled
    provider = AgentModelProvider(manager, fallback_enabled=True)

    # Set a default fallback model
    provider.set_default_fallback_model("model1")

    # Add preferences for different agent types
    provider.add_agent_fallback_preference("researcher", ["huggingface", "llama"])
    provider.add_agent_fallback_preference("developer", ["llama", "huggingface"])

    # Test model retrieval for different agent types
    agent_types = ["researcher", "developer", "marketing"]

    for agent_type in agent_types:
        try:
            model = provider.get_model_for_agent(agent_type, "text-generation")

            # Get the model info
            assignments = provider.get_agent_model_assignments()
            model_id = assignments[agent_type]["text-generation"]
            model_info = manager.get_model_info(model_id)

            print(f"Agent: {agent_type}, Assigned Model: {model_info.name}")
        except ValueError as e:
            print(f"Error getting model for {agent_type}: {e}")

    # Check fallback metrics
    metrics = provider.get_fallback_metrics()
    history = provider.get_fallback_history(limit=5)

    print("\nFallback events recorded:", len(history))


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Set up test environment
    manager = setup_test_environment()

    # Run tests
    test_basic_fallback(manager)
    test_fallback_strategies(manager)
    test_fallback_metrics(manager)
    test_agent_integration(manager)

    print("\n=== All tests completed ===")
