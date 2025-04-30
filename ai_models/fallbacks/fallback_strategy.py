"""
Fallback strategy for AI models.

This module provides classes and functions for implementing fallback mechanisms
when primary model selection fails. It includes configurable strategies for
selecting alternative models based on various criteria.
"""

import os
import sys
import time
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

# Add the project root to the Python path to import the errors module
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from errors import ModelNotFoundError, ModelLoadError
from interfaces.model_interfaces import IModelInfo, IModelManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        """
        Initialize a fallback event.
        
        Args:
            original_model_id: ID of the original model that failed (or None if no initial model)
            fallback_model_id: ID of the fallback model that was selected
            reason: Reason for the fallback
            agent_type: Optional type of agent using the model
            task_type: Optional type of task being performed
            strategy_used: The fallback strategy that was used
            timestamp: Optional timestamp of the fallback event (defaults to current time)
            details: Optional additional details about the fallback
        """
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
    """
    Manager class for handling model fallbacks.
    
    This class provides a comprehensive strategy for managing model fallbacks
    when the primary model selection fails, including:
    
    1. Configurable strategies for selecting fallback models
    2. Logging of fallback events for monitoring and analysis
    3. Performance tracking of fallback selections
    4. Dynamic adjustment of fallback preferences based on success rates
    """
    
    def __init__(
        self, 
        model_manager: IModelManager,
        fallback_enabled: bool = True,
        default_strategy: FallbackStrategy = FallbackStrategy.DEFAULT,
        max_attempts: int = 3,
        default_model_id: Optional[str] = None,
        fallback_preferences: Optional[Dict[str, List[str]]] = None,
        logging_level: int = logging.INFO
    ):
        """
        Initialize the fallback manager.
        
        Args:
            model_manager: The model manager to use for model operations
            fallback_enabled: Whether fallback mechanisms are enabled
            default_strategy: Default fallback strategy to use
            max_attempts: Maximum number of fallback attempts
            default_model_id: ID of the default fallback model
            fallback_preferences: Dictionary mapping agent types to lists of preferred model types
            logging_level: Logging level for fallback events
        """
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
        # Structure: {strategy: {success_count: int, total_count: int}}
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
    ) -> Tuple[Optional[IModelInfo], Optional[FallbackEvent]]:
        """
        Find a fallback model when the primary model is unavailable.
        
        This method implements the core fallback algorithm:
        1. If strategy_override is provided, use that strategy
        2. Otherwise, try strategies in order: DEFAULT -> SIMILAR_MODEL -> MODEL_TYPE -> ANY_AVAILABLE
        3. Execute each strategy until a fallback model is found
        4. Track the fallback event if successful
        
        Args:
            original_model_id: ID of the original model that failed (if any)
            agent_type: Type of agent requesting the model (for preference matching)
            task_type: Type of task the model will perform
            required_capabilities: List of required model capabilities
            strategy_override: Optional override for the fallback strategy
            
        Returns:
            Tuple containing:
              - ModelInfo of the fallback model or None if no fallback found
              - FallbackEvent describing the fallback or None if no fallback found
        """
        if not self.fallback_enabled:
            self.logger.info("Fallback is disabled, not attempting model fallback")
            return None, None
            
        # Track the original model info if available
        original_model_info = None
        if original_model_id:
            try:
                original_model_info = self.model_manager.get_model_info(original_model_id)
            except Exception:
                pass

        # If strategy override is provided, only try that strategy
        if strategy_override:
            return self._try_strategy(
                strategy_override,
                original_model_id,
                original_model_info,
                agent_type,
                task_type,
                required_capabilities
            )

        # Otherwise, try strategies in cascading order
        # The order matches test expectations: DEFAULT -> SIMILAR_MODEL -> MODEL_TYPE
        cascade_order = [
            FallbackStrategy.DEFAULT,
            FallbackStrategy.SIMILAR_MODEL,
            FallbackStrategy.MODEL_TYPE,
            FallbackStrategy.CAPABILITY_BASED,
            FallbackStrategy.SPECIFIED_LIST,
            FallbackStrategy.ANY_AVAILABLE
        ]

        last_event = None
        for strategy in cascade_order:
            fallback_model, event = self._try_strategy(
                strategy,
                original_model_id,
                original_model_info,
                agent_type,
                task_type,
                required_capabilities
            )
            if fallback_model:
                return fallback_model, event
            last_event = event

        self.logger.warning("No fallback model found after trying all strategies")
        return None, last_event

    def _try_strategy(
        self,
        strategy: FallbackStrategy,
        original_model_id: Optional[str],
        original_model_info: Optional[IModelInfo],
        agent_type: Optional[str],
        task_type: Optional[str],
        required_capabilities: Optional[List[str]]
    ) -> Tuple[Optional[IModelInfo], Optional[FallbackEvent]]:
        """Try a specific fallback strategy and return the result."""
        self.logger.info(f"Trying fallback strategy: {strategy.value}")
        
        fallback_model = None
        reason = "Primary model selection failed"
        
        # Execute the selected fallback strategy
        if strategy == FallbackStrategy.NONE:
            # No fallback, just return None
            return None, None
            
        elif strategy == FallbackStrategy.DEFAULT:
            # Use the default model if specified
            fallback_model = self._apply_default_model_strategy()
            reason = "Default model strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.SIMILAR_MODEL:
            # Find a model with similar capabilities
            fallback_model = self._apply_similar_model_strategy(original_model_info)
            reason = "Similar model strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.MODEL_TYPE:
            # Try other models of the same type
            fallback_model = self._apply_model_type_strategy(original_model_info, agent_type, task_type)
            reason = "Model type strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.ANY_AVAILABLE:
            # Use any available model
            fallback_model = self._apply_any_available_strategy()
            reason = "Any available strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.SPECIFIED_LIST:
            # Try models in a specified order based on agent type
            fallback_model = self._apply_specified_list_strategy(agent_type)
            reason = "Specified list strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.SIZE_TIER:
            # Try models of different size tiers
            fallback_model = self._apply_size_tier_strategy(original_model_info)
            reason = "Size tier strategy failed" if not fallback_model else reason
            
        elif strategy == FallbackStrategy.CAPABILITY_BASED:
            # Try models with required capabilities
            fallback_model = self._apply_capability_strategy(required_capabilities)
            reason = "Capability based strategy failed" if not fallback_model else reason
            
        # Create event to track this attempt
        event = FallbackEvent(
            original_model_id=original_model_id,
            fallback_model_id=fallback_model.id if fallback_model else "none",
            reason=reason,
            agent_type=agent_type,
            task_type=task_type,
            strategy_used=strategy,
            details={
                "original_model_type": original_model_info.type if original_model_info else None,
                "fallback_model_type": fallback_model.type if fallback_model else None
            }
        )
        
        # Track the event with appropriate success status
        self.track_fallback_event(event, was_successful=fallback_model is not None)
            
        return fallback_model, event  # Return event for both success and failure

    def track_fallback_event(self, event: FallbackEvent, was_successful: bool = True) -> None:
        """
        Track a fallback event and update metrics.
        
        Args:
            event: The fallback event to track
            was_successful: Whether the fallback was successful
        """
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
        """
        Get metrics about fallback effectiveness.
        
        Returns:
            Dictionary mapping strategy names to their metrics
        """
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
        """
        Get history of fallback events.
        
        Args:
            limit: Maximum number of events to return (most recent first)
            
        Returns:
            List of fallback events as dictionaries
        """
        return [event.to_dict() for event in self.fallback_history[-limit:]]
        
    def configure(self, **kwargs) -> None:
        """
        Configure the fallback manager.
        
        Args:
            **kwargs: Configuration parameters
                - fallback_enabled: Whether fallback is enabled
                - default_strategy: Default fallback strategy
                - max_attempts: Maximum number of fallback attempts
                - default_model_id: ID of the default fallback model
                - fallback_preferences: Mapping of agent types to model type preferences
                - logging_level: Logging level for fallback events
        """
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
    
    def _apply_default_model_strategy(self) -> Optional[IModelInfo]:
        """Apply the default model fallback strategy."""
        if self.default_model_id:
            return self.model_manager.get_model_info(self.default_model_id)
        return None
        
    def _apply_similar_model_strategy(self, original_model: Optional[IModelInfo]) -> Optional[IModelInfo]:
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
        
    def _apply_model_type_strategy(
        self, 
        original_model: Optional[IModelInfo], 
        agent_type: Optional[str], 
        task_type: Optional[str]
    ) -> Optional[IModelInfo]:
        """Try other models of the same type as the original model."""
        # Try each strategy in sequence:
        # 1. Same type as original model
        # 2. Agent preferences
        # 3. Default preferences
        
        # If we have an original model, try to find another of the same type
        if original_model and original_model.type:
            same_type_models = self.model_manager.get_models_by_type(original_model.type)
            # Ensure we don't return the original model
            filtered_models = [m for m in same_type_models if m.id != original_model.id]
            if filtered_models:
                return filtered_models[0]
                
        # If no match with original type or no original model, try agent preferences
        if agent_type and agent_type in self.fallback_preferences:
            # Get preferred model types for this agent
            preferred_types = self.fallback_preferences[agent_type]
            
            # Try each preferred type
            for model_type in preferred_types:
                models = self.model_manager.get_models_by_type(model_type)
                if models and (not original_model or models[0].id != original_model.id):
                    return models[0]
                    
        # If still no match or no agent preferences, try default preferences
        if "default" in self.fallback_preferences:
            for model_type in self.fallback_preferences["default"]:
                models = self.model_manager.get_models_by_type(model_type)
                if models and (not original_model or models[0].id != original_model.id):
                    return models[0]
                    
        # If all strategies fail, return None
        return None
        
    def _apply_any_available_strategy(self) -> Optional[IModelInfo]:
        """Use any available model as a fallback."""
        all_models = self.model_manager.get_all_models()
        return all_models[0] if all_models else None
        
    def _apply_specified_list_strategy(self, agent_type: Optional[str]) -> Optional[IModelInfo]:
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
        
    def _apply_size_tier_strategy(self, original_model: Optional[IModelInfo]) -> Optional[IModelInfo]:
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
        
    def _apply_capability_strategy(self, required_capabilities: Optional[List[str]]) -> Optional[IModelInfo]:
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