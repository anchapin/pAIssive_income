"""
Standalone test script for model fallback functionality.

This script directly imports the modules we need to test without
going through the package structure, avoiding circular imports.
"""

import os
import sys
import time
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple

# Define the fallback strategy enum directly instead of importing it
class FallbackStrategy(Enum):
    """Enumeration of fallback strategy types."""
    NONE = "none"                      # No fallback, just fail
    DEFAULT = "default"                # Use a default model
    SIMILAR_MODEL = "similar_model"    # Use a model with similar capabilities
    MODEL_TYPE = "model_type"          # Try other models of the same type
    ANY_AVAILABLE = "any_available"    # Use any available model
    SPECIFIED_LIST = "specified_list"  # Try models in a specified order
    SIZE_TIER = "size_tier"            # Try models of different size tiers
    CAPABILITY_BASED = "capability"    # Try models with required capabilities


class FallbackEvent:
    """Class representing a model fallback event."""
    
    def __init__(
        self, 
        original_model_id: Optional[str], 
        fallback_model_id: str,
        reason: str,
        agent_type: Optional[str] = None,
        task_type: Optional[str] = None,
        strategy_used: FallbackStrategy = FallbackStrategy.DEFAULT,
        timestamp: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize a fallback event."""
        self.original_model_id = original_model_id
        self.fallback_model_id = fallback_model_id
        self.reason = reason
        self.agent_type = agent_type
        self.task_type = task_type
        self.strategy_used = strategy_used
        self.timestamp = timestamp or time.time()
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the fallback event to a dictionary."""
        return {
            "original_model_id": self.original_model_id,
            "fallback_model_id": self.fallback_model_id,
            "reason": self.reason,
            "agent_type": self.agent_type,
            "task_type": self.task_type,
            "strategy_used": self.strategy_used.value,
            "timestamp": self.timestamp,
            "details": self.details
        }


class FallbackManager:
    """Manager class for handling model fallbacks."""
    
    def __init__(
        self, 
        model_manager,
        fallback_enabled: bool = True,
        default_strategy: FallbackStrategy = FallbackStrategy.DEFAULT,
        max_attempts: int = 3,
        default_model_id: Optional[str] = None,
        fallback_preferences: Optional[Dict[str, List[str]]] = None,
        logging_level: int = logging.INFO
    ):
        """Initialize the fallback manager."""
        self.model_manager = model_manager
        self.fallback_enabled = fallback_enabled
        self.default_strategy = default_strategy
        self.max_attempts = max_attempts
        self.default_model_id = default_model_id
        
        # Default fallback preferences if none provided
        self.fallback_preferences = fallback_preferences or {
            "researcher": ["huggingface", "llama", "general-purpose"],
            "developer": ["huggingface", "llama", "general-purpose"],
            "monetization": ["huggingface", "general-purpose"],
            "marketing": ["huggingface", "general-purpose"],
            "default": ["huggingface", "general-purpose"]
        }
        
        # History of fallback events for analysis
        self.fallback_history: List[FallbackEvent] = []
        
        # Fallback success metrics to track effectiveness
        self.fallback_metrics: Dict[FallbackStrategy, Dict[str, int]] = {
            strategy: {"success_count": 0, "total_count": 0} 
            for strategy in FallbackStrategy
        }
        
        # Set up dedicated logger for fallback events
        self.logger = logging.getLogger(__name__ + ".fallback")
        self.logger.setLevel(logging_level)
        
    def find_fallback_model(
        self, 
        original_model_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        task_type: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        strategy_override: Optional[FallbackStrategy] = None
    ):
        """Find a fallback model when the primary model is unavailable."""
        if not self.fallback_enabled:
            self.logger.info("Fallback is disabled, not attempting model fallback")
            return None, None
            
        # Select strategy to use
        strategy = strategy_override or self.default_strategy
        
        # Track the original model info if available
        original_model_info = None
        if original_model_id:
            original_model_info = self.model_manager.get_model_info(original_model_id)
            
        # Try to find a fallback model using the selected strategy
        self.logger.info(f"Finding fallback model using strategy: {strategy.value}")
        
        fallback_model = None
        reason = "Primary model selection failed"
        attempts = 0
        
        # Execute the selected fallback strategy
        if strategy == FallbackStrategy.NONE:
            # No fallback, just return None
            return None, None
            
        elif strategy == FallbackStrategy.DEFAULT:
            # Use the default model if specified
            fallback_model = self._apply_default_model_strategy()
            
        elif strategy == FallbackStrategy.SIMILAR_MODEL:
            # Find a model with similar capabilities
            fallback_model = self._apply_similar_model_strategy(original_model_info)
            
        elif strategy == FallbackStrategy.MODEL_TYPE:
            # Try other models of the same type
            fallback_model = self._apply_model_type_strategy(original_model_info, agent_type, task_type)
            
        elif strategy == FallbackStrategy.ANY_AVAILABLE:
            # Use any available model
            fallback_model = self._apply_any_available_strategy()
            
        elif strategy == FallbackStrategy.SPECIFIED_LIST:
            # Try models in a specified order based on agent type
            fallback_model = self._apply_specified_list_strategy(agent_type)
            
        elif strategy == FallbackStrategy.SIZE_TIER:
            # Try models of different size tiers
            fallback_model = self._apply_size_tier_strategy(original_model_info)
            
        elif strategy == FallbackStrategy.CAPABILITY_BASED:
            # Try models with required capabilities
            fallback_model = self._apply_capability_strategy(required_capabilities)
            
        # If we found a fallback model, record the event and return
        if fallback_model:
            event = FallbackEvent(
                original_model_id=original_model_id,
                fallback_model_id=fallback_model.id,
                reason=reason,
                agent_type=agent_type,
                task_type=task_type,
                strategy_used=strategy,
                details={
                    "attempts": attempts + 1,
                    "original_model_type": original_model_info.type if original_model_info else None,
                    "fallback_model_type": fallback_model.type
                }
            )
            
            self.track_fallback_event(event)
            return fallback_model, event
        
        self.logger.warning(f"No fallback model found after trying strategy: {strategy.value}")
        return None, None
        
    def track_fallback_event(self, event: FallbackEvent, was_successful: bool = True) -> None:
        """Track a fallback event and update metrics."""
        # Add to history
        self.fallback_history.append(event)
        
        # Update metrics
        strategy = event.strategy_used
        self.fallback_metrics[strategy]["total_count"] += 1
        if was_successful:
            self.fallback_metrics[strategy]["success_count"] += 1
            
        # Log the event
        if was_successful:
            self.logger.info(
                f"Fallback successful: {event.original_model_id or 'unknown'} -> {event.fallback_model_id} "
                f"using strategy {strategy.value}"
            )
        else:
            self.logger.warning(
                f"Fallback unsuccessful: {event.original_model_id or 'unknown'} -> {event.fallback_model_id} "
                f"using strategy {strategy.value}"
            )
            
    def get_fallback_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics about fallback effectiveness."""
        metrics = {}
        for strategy in FallbackStrategy:
            strategy_metrics = self.fallback_metrics[strategy]
            success_rate = 0
            if strategy_metrics["total_count"] > 0:
                success_rate = strategy_metrics["success_count"] / strategy_metrics["total_count"]
                
            metrics[strategy.value] = {
                "success_count": strategy_metrics["success_count"],
                "total_count": strategy_metrics["total_count"],
                "success_rate": success_rate
            }
            
        return metrics
        
    def get_fallback_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get history of fallback events."""
        return [event.to_dict() for event in self.fallback_history[-limit:]]
        
    def configure(self, **kwargs) -> None:
        """Configure the fallback manager."""
        if "fallback_enabled" in kwargs:
            self.fallback_enabled = kwargs["fallback_enabled"]
            
        if "default_strategy" in kwargs:
            strategy_value = kwargs["default_strategy"]
            if isinstance(strategy_value, str):
                try:
                    self.default_strategy = FallbackStrategy(strategy_value)
                except ValueError:
                    self.logger.warning(f"Invalid fallback strategy: {strategy_value}, using DEFAULT")
                    self.default_strategy = FallbackStrategy.DEFAULT
            elif isinstance(strategy_value, FallbackStrategy):
                self.default_strategy = strategy_value
                
        if "max_attempts" in kwargs:
            self.max_attempts = kwargs["max_attempts"]
            
        if "default_model_id" in kwargs:
            self.default_model_id = kwargs["default_model_id"]
            
        if "fallback_preferences" in kwargs:
            self.fallback_preferences = kwargs["fallback_preferences"]
            
        if "logging_level" in kwargs:
            self.logger.setLevel(kwargs["logging_level"])
            
        self.logger.info(f"Fallback manager configuration updated: enabled={self.fallback_enabled}, "
                         f"strategy={self.default_strategy.value}")
    
    def _apply_default_model_strategy(self):
        """Apply the default model fallback strategy."""
        if self.default_model_id:
            return self.model_manager.get_model_info(self.default_model_id)
        return None
        
    def _apply_similar_model_strategy(self, original_model):
        """Find a model with similar capabilities to the original model."""
        if not original_model:
            return None
            
        # Get all models
        all_models = self.model_manager.get_all_models()
        
        # Filter out the original model
        candidates = [m for m in all_models if m.id != original_model.id]
        
        # If no candidates, return None
        if not candidates:
            return None
            
        # If the original model has capabilities, try to find models with similar capabilities
        if hasattr(original_model, "capabilities") and original_model.capabilities:
            # For each model, calculate a similarity score based on shared capabilities
            scored_candidates = []
            for model in candidates:
                if not hasattr(model, "capabilities") or not model.capabilities:
                    scored_candidates.append((model, 0))
                    continue
                    
                # Count shared capabilities
                shared = len(set(original_model.capabilities) & set(model.capabilities))
                score = shared / len(original_model.capabilities) if original_model.capabilities else 0
                scored_candidates.append((model, score))
                
            # Sort by score (highest first)
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            
            # If we have a candidate with a score > 0, return it
            if scored_candidates and scored_candidates[0][1] > 0:
                return scored_candidates[0][0]
                
        # If no similarity-based match, fall back to same type
        same_type_models = [m for m in candidates if m.type == original_model.type]
        if same_type_models:
            return same_type_models[0]
            
        # If still no match, return any model
        return candidates[0] if candidates else None
        
    def _apply_model_type_strategy(self, original_model, agent_type, task_type):
        """Try other models of the same type as the original model."""
        # If we have an original model, try to find another of the same type
        if original_model:
            same_type_models = self.model_manager.get_models_by_type(original_model.type)
            filtered_models = [m for m in same_type_models if m.id != original_model.id]
            if filtered_models:
                return filtered_models[0]
                
        # If no original model or no other models of the same type, try using agent/task preferences
        if agent_type and agent_type in self.fallback_preferences:
            # Get preferred model types for this agent
            preferred_types = self.fallback_preferences[agent_type]
            
            # Try each preferred type
            for model_type in preferred_types:
                models = self.model_manager.get_models_by_type(model_type)
                if models:
                    return models[0]
                    
        # If all else fails, try default preferences
        if "default" in self.fallback_preferences:
            for model_type in self.fallback_preferences["default"]:
                models = self.model_manager.get_models_by_type(model_type)
                if models:
                    return models[0]
                    
        return None
        
    def _apply_any_available_strategy(self):
        """Use any available model as a fallback."""
        all_models = self.model_manager.get_all_models()
        return all_models[0] if all_models else None
        
    def _apply_specified_list_strategy(self, agent_type):
        """Try models in a specified order based on agent type."""
        # Get the list of preferred model types for this agent
        preferred_types = self.fallback_preferences.get(
            agent_type, self.fallback_preferences.get("default", [])
        )
        
        # Try each preferred type in order
        for model_type in preferred_types:
            models = self.model_manager.get_models_by_type(model_type)
            if models:
                return models[0]
                
        return None
        
    def _apply_size_tier_strategy(self, original_model):
        """Try models of different size tiers, preferring smaller models as fallbacks."""
        # This strategy works best when we have size information for models
        all_models = self.model_manager.get_all_models()
        
        # If no original model, just return any model
        if not original_model:
            return all_models[0] if all_models else None
            
        # Filter out the original model
        candidates = [m for m in all_models if m.id != original_model.id]
        if not candidates:
            return None
            
        # Get the original model's size if available
        original_size = getattr(original_model, "size_mb", 0)
        
        # If size is available, prefer smaller models
        if original_size > 0:
            # Get models with size info
            sized_models = [(m, getattr(m, "size_mb", float("inf"))) for m in candidates]
            
            # Sort by size (smallest first)
            sized_models.sort(key=lambda x: x[1])
            
            # Filter for models smaller than the original
            smaller_models = [m for m, size in sized_models if size < original_size]
            
            # If we have smaller models, return the largest of them
            if smaller_models:
                return smaller_models[-1]
                
        # If no size info or no smaller models, fall back to same type
        same_type_models = [m for m in candidates if m.type == original_model.type]
        if same_type_models:
            return same_type_models[0]
            
        # If still no match, return any model
        return candidates[0]
        
    def _apply_capability_strategy(self, required_capabilities):
        """Find a model that has all the required capabilities."""
        if not required_capabilities:
            return None
            
        all_models = self.model_manager.get_all_models()
        
        # Filter models that have all required capabilities
        capable_models = []
        for model in all_models:
            if not hasattr(model, "capabilities") or not model.capabilities:
                continue
                
            if all(cap in model.capabilities for cap in required_capabilities):
                capable_models.append(model)
                
        # Return the first capable model if any
        return capable_models[0] if capable_models else None


# Mock classes for testing
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
        MockModelInfo(id="model1", name="Primary Model", type="huggingface", path="/path/to/model1", 
                     capabilities=["text-generation", "classification"]),
        MockModelInfo(id="model2", name="Secondary Model", type="llama", path="/path/to/model2",
                     capabilities=["text-generation"]),
        MockModelInfo(id="model3", name="Embedding Model", type="embedding", path="/path/to/model3",
                     capabilities=["embedding"]),
        MockModelInfo(id="model4", name="Small Model", type="huggingface", path="/path/to/model4",
                     size_mb=100, capabilities=["text-generation"])
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
        default_model_id="model1"  # Set the default model to model1
    )
    
    strategies_to_test = [
        FallbackStrategy.DEFAULT,
        FallbackStrategy.SIMILAR_MODEL,
        FallbackStrategy.MODEL_TYPE,
        FallbackStrategy.ANY_AVAILABLE,
        FallbackStrategy.SPECIFIED_LIST,
        FallbackStrategy.SIZE_TIER,
        FallbackStrategy.CAPABILITY_BASED
    ]
    
    for strategy in strategies_to_test:
        # Try finding a fallback model with the strategy
        print(f"\nTesting strategy: {strategy.value}")
        
        fallback_model, event = fallback_manager.find_fallback_model(
            original_model_id="non_existent_model",
            agent_type="researcher",
            task_type="text-generation",
            strategy_override=strategy
        )
        
        if fallback_model:
            print(f"✅ Strategy {strategy.value} found fallback model: {fallback_model.name}")
        else:
            print(f"❌ Strategy {strategy.value} failed to find a fallback model")
    
    # Test capability-based strategy with specific capabilities
    print("\nTesting capability-based with specific requirements:")
    fallback_model, _ = fallback_manager.find_fallback_model(
        required_capabilities=["text-generation", "classification"],
        strategy_override=FallbackStrategy.CAPABILITY_BASED
    )
    
    if fallback_model:
        print(f"✅ Found model with required capabilities: {fallback_model.name}")
    else:
        print("❌ Failed to find model with required capabilities")


def test_fallback_metrics(manager):
    """Test fallback metrics tracking."""
    print("\n=== Test: Fallback Metrics ===")
    
    # Create a FallbackManager
    fallback_manager = FallbackManager(
        model_manager=manager,
        fallback_enabled=True
    )
    
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
                strategy_override=strategy
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
            print(f"  Success rate: {success_rate:.2f} ({stats['success_count']}/{stats['total_count']})")
    
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