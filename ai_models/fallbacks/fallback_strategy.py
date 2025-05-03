"""
Fallback strategy for AI models.

This module provides classes and functions for implementing fallback mechanisms
when primary model selection fails. It includes configurable strategies for
selecting alternative models based on various criteria.
"""

import logging
import os
import sys
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Add the project root to the Python path to import the errors module
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from errors import ModelError, ModelNotFoundError, SecurityError
from interfaces.model_interfaces import IModelInfo, IModelManager

# Set up logging with secure defaults
logging.basicConfig(
    level=logging.INFO,
    format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "logs", "fallback.log"),
            mode="a",
            encoding="utf - 8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class FallbackStrategy(Enum):
    """Enumeration of fallback strategy types."""

    NONE = "none"  # No fallback, just fail
    DEFAULT = "default"  # Use a default model
    SIMILAR_MODEL = "similar_model"  # Use a model with similar capabilities
    MODEL_TYPE = "model_type"  # Try other models of the same type
    ANY_AVAILABLE = "any_available"  # Use any available model
    SPECIFIED_LIST = "specified_list"  # Try models in a specified order
    SIZE_TIER = "size_tier"  # Try models of different size tiers
    CAPABILITY_BASED = "capability"  # Try models with required capabilities


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
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a fallback event with input validation."""
        # Validate model IDs
        if original_model_id and not self._is_safe_model_id(original_model_id):
            raise SecurityError("Invalid original model ID format")
        if not self._is_safe_model_id(fallback_model_id):
            raise SecurityError("Invalid fallback model ID format")

        # Validate agent and task types
        if agent_type and not self._is_safe_type_name(agent_type):
            raise SecurityError("Invalid agent type format")
        if task_type and not self._is_safe_type_name(task_type):
            raise SecurityError("Invalid task type format")

        self.original_model_id = original_model_id
        self.fallback_model_id = fallback_model_id
        self.reason = str(reason)[:1000]  # Limit reason length
        self.agent_type = agent_type
        self.task_type = task_type
        self.strategy_used = strategy_used
        self.timestamp = timestamp or time.time()
        self.details = self._sanitize_details(details or {})

    @staticmethod
    def _is_safe_model_id(model_id: str) -> bool:
        """Validate model ID format."""
        import re

        return bool(re.match(r"^[a - zA - Z0 - 9][a - zA - Z0 - 9_\-\.]+$", model_id))

    @staticmethod
    def _is_safe_type_name(type_name: str) -> bool:
        """Validate type name format."""
        import re

        return bool(re.match(r"^[a - zA - Z0 - 9_\-]+$", type_name))

    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize details dictionary."""
        sanitized = {}
        for key, value in details.items():
            # Only allow alphanumeric keys with underscores
            import re
            if not re.match(r"^[a - zA - Z0 - 9_]+$", key):
                continue
            # Convert values to strings and limit length
            sanitized[key] = str(value)[:500]
        return sanitized

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
            "details": self.details,
        }


class FallbackManager:
    """Manager class for handling model fallbacks securely."""

    def __init__(
        self,
        model_manager: IModelManager,
        fallback_enabled: bool = True,
        default_strategy: FallbackStrategy = FallbackStrategy.DEFAULT,
        max_attempts: int = 3,
        default_model_id: Optional[str] = None,
        fallback_preferences: Optional[Dict[str, List[str]]] = None,
        logging_level: int = logging.INFO,
        secure_mode: bool = True,  # Enable additional security features
    ):
        """Initialize the fallback manager with security features."""
        self.model_manager = model_manager
        self.fallback_enabled = fallback_enabled
        self.default_strategy = default_strategy
        self.max_attempts = min(max_attempts, 10)  # Limit maximum attempts
        self.secure_mode = secure_mode

        # Validate default model ID if provided
        if default_model_id and not self._is_safe_model_id(default_model_id):
            raise SecurityError("Invalid default model ID format")
        self.default_model_id = default_model_id

        # Default fallback preferences with secure defaults
        default_preferences = {
            "researcher": ["huggingface", "llama", "general - purpose"],
            "developer": ["huggingface", "llama", "general - purpose"],
            "monetization": ["huggingface", "general - purpose"],
            "marketing": ["huggingface", "general - purpose"],
            "default": ["huggingface", "general - purpose"],
        }

        # Validate and merge provided preferences
        self.fallback_preferences = self._validate_preferences(
            fallback_preferences or default_preferences
        )

        # Set up secure logging
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, mode=0o750, exist_ok=True)

        self.logger = logging.getLogger(__name__ + ".fallback")
        self.logger.setLevel(logging_level)

        # Initialize metrics with thread safety
        self._init_metrics()

    def _init_metrics(self) -> None:
        """Initialize metrics securely."""
        self.fallback_history: List[FallbackEvent] = []
        self.fallback_metrics: Dict[FallbackStrategy, Dict[str, int]] = {
            strategy: {"success_count": 0, 
                "total_count": 0} for strategy in FallbackStrategy
        }

    def _validate_preferences(self, preferences: Dict[str, List[str]]) -> Dict[str, 
        List[str]]:
        """Validate fallback preferences."""
        validated = {}
        allowed_types = {"huggingface", "llama", "openai", "general - purpose"}

        for agent_type, model_types in preferences.items():
            # Validate agent type
            if not self._is_safe_type_name(agent_type):
                continue

            # Validate and filter model types
            safe_types = [
                mt for mt in model_types if isinstance(mt, 
                    str) and mt.lower() in allowed_types
            ]
            if safe_types:
                validated[agent_type] = safe_types

        return validated

    @staticmethod
    def _is_safe_model_id(model_id: str) -> bool:
        """Validate model ID format."""
        import re

        return bool(re.match(r"^[a - zA - Z0 - 9][a - zA - Z0 - 9_\-\.]+$", model_id))

    @staticmethod
    def _is_safe_type_name(type_name: str) -> bool:
        """Validate type name format."""
        import re

        return bool(re.match(r"^[a - zA - Z0 - 9_\-]+$", type_name))

    def find_fallback_model(
        self,
        original_model_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        task_type: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        strategy_override: Optional[FallbackStrategy] = None,
    ) -> Tuple[Optional[IModelInfo], Optional[FallbackEvent]]:
        """Find a fallback model securely with cascading strategies."""
        if not self.fallback_enabled:
            self.logger.info("Fallback is disabled")
            return None, None

        try:
            # Validate inputs
            if original_model_id and not self._is_safe_model_id(original_model_id):
                raise SecurityError("Invalid original model ID format")
            if agent_type and not self._is_safe_type_name(agent_type):
                raise SecurityError("Invalid agent type format")
            if task_type and not self._is_safe_type_name(task_type):
                raise SecurityError("Invalid task type format")
            if required_capabilities:
                self._validate_capabilities(required_capabilities)

            # Track the original model info if available
            original_model_info = None
            if original_model_id:
                try:
                    original_model_info = \
                        self.model_manager.get_model_info(original_model_id)
                except ModelNotFoundError:
                    pass

            # Define cascade order for strategies
            cascade_order = [
                FallbackStrategy.DEFAULT,
                FallbackStrategy.SIMILAR_MODEL,
                FallbackStrategy.MODEL_TYPE,
                FallbackStrategy.CAPABILITY_BASED,
                FallbackStrategy.SPECIFIED_LIST,
                FallbackStrategy.ANY_AVAILABLE,
            ]

            # Use override or cascade
            strategies_to_try = \
                [strategy_override] if strategy_override else cascade_order

            reason = "Primary model selection failed"
            attempts = 0

            # Try each strategy in sequence
            for strategy in strategies_to_try:
                if attempts >= self.max_attempts:
                    break

                attempts += 1
                self.logger.info(
                    f"Trying fallback strategy: {strategy.value} (attempt {attempts})")

                fallback_model = None
                try:
                    if strategy == FallbackStrategy.NONE:
                        continue
                    elif strategy == FallbackStrategy.DEFAULT:
                        fallback_model = self._apply_default_model_strategy()
                    elif strategy == FallbackStrategy.SIMILAR_MODEL:
                        fallback_model = \
                            self._apply_similar_model_strategy(original_model_info)
                    elif strategy == FallbackStrategy.MODEL_TYPE:
                        fallback_model = self._apply_model_type_strategy(
                            original_model_info, agent_type, task_type
                        )
                    elif strategy == FallbackStrategy.ANY_AVAILABLE:
                        fallback_model = self._apply_any_available_strategy()
                    elif strategy == FallbackStrategy.SPECIFIED_LIST:
                        fallback_model = self._apply_specified_list_strategy(agent_type)
                    elif strategy == FallbackStrategy.SIZE_TIER:
                        fallback_model = \
                            self._apply_size_tier_strategy(original_model_info)
                    elif strategy == FallbackStrategy.CAPABILITY_BASED:
                        fallback_model = \
                            self._apply_capability_strategy(required_capabilities)

                except Exception as e:
                    self.logger.error(f"Error in strategy {strategy.value}: {e}")
                    continue

                # If we found a fallback model, validate and return
                if fallback_model:
                    try:
                        self._validate_fallback_model(fallback_model)
                    except SecurityError as e:
                        self.logger.error(
                            f"Security validation failed for fallback model: {e}")
                        continue

                    event = FallbackEvent(
                        original_model_id=original_model_id,
                        fallback_model_id=fallback_model.id,
                        reason=reason,
                        agent_type=agent_type,
                        task_type=task_type,
                        strategy_used=strategy,
                        details={
                            "attempts": attempts,
                            "original_model_type": (
                                original_model_info.type if original_model_info else None
                            ),
                            "fallback_model_type": fallback_model.type,
                        },
                    )

                    self.track_fallback_event(event, was_successful=True)
                    return fallback_model, event

            # No fallback found after all attempts
            event = FallbackEvent(
                original_model_id=original_model_id,
                fallback_model_id="none",
                reason=f"No fallback found after {attempts} attempts",
                agent_type=agent_type,
                task_type=task_type,
                strategy_used=strategies_to_try[-1],
                details={
                    "attempts": attempts,
                    "original_model_type": (
                        original_model_info.type if original_model_info else None
                    ),
                },
            )
            self.track_fallback_event(event, was_successful=False)
            return None, event

        except Exception as e:
            self.logger.error(f"Error in fallback process: {e}")
            raise ModelError(f"Fallback process failed: {e}")

    def _validate_capabilities(self, capabilities: List[str]) -> None:
        """Validate capability names."""
        for cap in capabilities:
            if not isinstance(cap, str) or not self._is_safe_type_name(cap):
                raise SecurityError(f"Invalid capability name: {cap}")

    def _validate_fallback_model(self, model: IModelInfo) -> None:
        """Validate fallback model security requirements."""
        if not model or not hasattr(model, 
            "id") or not self._is_safe_model_id(model.id):
            raise SecurityError("Invalid fallback model ID")

        if not hasattr(model, "type") or not self._is_safe_type_name(model.type):
            raise SecurityError("Invalid fallback model type")

    # ... (rest of the FallbackManager implementation remains the same,
    # including _apply_ * _strategy methods and other utility methods)
