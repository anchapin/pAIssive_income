"""
Integration with the agent team for the AI Models module.

This module provides functions and classes for integrating the AI Models module
with the agent team, allowing agents to use local AI models for their tasks.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dependency_container import get_container
from errors import ModelError, ModelLoadError
from interfaces.model_interfaces import IModelInfo, IModelManager

from .fallbacks import FallbackEvent, FallbackManager, FallbackStrategy
from .model_config import ModelConfig
from .model_manager import ModelManager

# Set up logging with secure defaults
logging.basicConfig(
    level=logging.INFO,
    format=" % (asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), "logs", "agent_integration.log"),
            mode="a",
            encoding="utf - 8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AgentModelProvider:
    """
    Provider for AI models used by agents.

    This class serves as a bridge between the Agent Team module and the AI Models module,
        
    providing a way for different agent types (researcher, developer, etc.) to access
    appropriate AI models for their specific tasks.
    """

    def __init__(
        self,
        model_manager: Optional[IModelManager] = None,
        fallback_enabled: bool = True,
        fallback_config: Optional[Dict] = None,
    ):
        """Initialize the agent model provider."""
        # Use dependency injection to get the model manager if not provided
        if model_manager is None:
            container = get_container()
            try:
                self.model_manager = container.resolve(IModelManager)
            except ValueError:
                # If not registered in the container, create a new instance
                self.model_manager = ModelManager()
        else:
            self.model_manager = model_manager

        # Dictionary to store agent model assignments
        self.agent_models: Dict[str, Dict[str, Any]] = {}

        # Default fallback configuration with secure defaults
        default_fallback_config = {
            "max_attempts": 3,  # Maximum number of fallback attempts
            "default_model_id": None,  # Global fallback model ID
            "logging_level": logging.INFO,  # Logging level for fallback events
            "use_general_purpose_fallback": True,  
                # Use general purpose models as fallbacks
            "fallback_preferences": {  # Fallback preferences for different agent types
                "researcher": ["huggingface", "llama", "general - purpose"],
                "developer": ["huggingface", "llama", "general - purpose"],
                "monetization": ["huggingface", "general - purpose"],
                "marketing": ["huggingface", "general - purpose"],
                "default": ["huggingface", "general - purpose"],
            },
            "secure_mode": True,  # Enable additional security checks
            "allowed_model_types": {  # Restrict model types per agent type
                "researcher": ["huggingface", "llama"],
                "developer": ["huggingface", "llama"],
                "monetization": ["huggingface"],
                "marketing": ["huggingface"],
                "default": ["huggingface"],
            },
        }

        # Apply any custom fallback configuration
        if fallback_config:
            # Only update allowed keys to prevent injection of malicious config
            allowed_keys = set(default_fallback_config.keys())
            sanitized_config = {k: v for k, 
                v in fallback_config.items() if k in allowed_keys}
            for key, value in sanitized_config.items():
                default_fallback_config[key] = value

        # Initialize the fallback manager
        self.fallback_manager = FallbackManager(
            model_manager=self.model_manager,
            fallback_enabled=fallback_enabled,
            default_strategy=FallbackStrategy.SPECIFIED_LIST,
            max_attempts=default_fallback_config["max_attempts"],
            default_model_id=default_fallback_config["default_model_id"],
            fallback_preferences=default_fallback_config["fallback_preferences"],
            logging_level=default_fallback_config["logging_level"],
        )

    def get_model_for_agent(self, agent_type: str, 
        task_type: Optional[str] = None) -> Any:
        """Get a model for a specific agent and task."""
        try:
            # Validate agent type
            if not isinstance(agent_type, str) or not agent_type.isalnum():
                raise ValueError("Invalid agent type")

            # Check existing assignment
            if agent_type in self.agent_models and (
                task_type is None or task_type in self.agent_models[agent_type]
            ):
                model_id = (
                    self.agent_models[agent_type].get(task_type)
                    if task_type
                    else list(self.agent_models[agent_type].values())[0]
                )
                try:
                    return self.model_manager.load_model(model_id)
                except ModelLoadError as e:
                    if not self.fallback_manager.fallback_enabled:
                        raise e
                    # Try fallback
                    return self._handle_fallback(model_id, agent_type, task_type, e)
                except Exception as e:
                    logger.error(f"Unexpected error loading model {model_id}: {e}")
                    raise

            # Find suitable model
            model_info = self._find_suitable_model(agent_type, task_type)
            if not model_info and self.fallback_manager.fallback_enabled:
                # Try fallback
                fallback_model_info, event = self.fallback_manager.find_fallback_model(
                    agent_type=agent_type, task_type=task_type
                )
                model_info = fallback_model_info

            if not model_info:
                raise ValueError(
                    f"No suitable model found for agent type {agent_type} and \
                        task type {task_type}"
                )

            # Load and register model
            try:
                model = self.model_manager.load_model(model_info.id)
                self._register_model_assignment(agent_type, model_info.id, task_type)
                return model
            except Exception as e:
                return self._handle_fallback(model_info.id, agent_type, task_type, e)

        except Exception as e:
            logger.error(f"Error in get_model_for_agent: {e}")
            raise

    def _handle_fallback(
        self,
        failed_model_id: str,
        agent_type: str,
        task_type: Optional[str],
        original_error: Exception,
    ) -> Any:
        """Handle model fallback when primary model fails."""
        logger.warning(
            f"Failed to load model {failed_model_id} for agent {agent_type}: {original_error}"
        )

        try:
            # Try to find a fallback model
            fallback_info, event = self.fallback_manager.find_fallback_model(
                original_model_id=failed_model_id,
                agent_type=agent_type,
                task_type=task_type,
            )

            if fallback_info:
                try:
                    model = self.model_manager.load_model(fallback_info.id)
                    # Update assignment
                    self._register_model_assignment(agent_type, fallback_info.id, 
                        task_type)
                    return model
                except Exception as e:
                    if event:
                        self.fallback_manager.track_fallback_event(event, False)
                    raise ModelLoadError(
                        f"Failed to load fallback model {fallback_info.id}: {e}"
                    ) from e

            raise ValueError("No fallback models available")

        except Exception as e:
            logger.error(f"Error in fallback handling: {e}")
            raise ModelError(
                f"Failed to get model for agent {agent_type} after fallback attempts"
            ) from e

    def _register_model_assignment(
        self, agent_type: str, model_id: str, task_type: Optional[str] = None
    ) -> None:
        """Register a model assignment securely."""
        if agent_type not in self.agent_models:
            self.agent_models[agent_type] = {}

        self.agent_models[agent_type][task_type or "default"] = model_id
        logger.info(
            f"Assigned model {model_id} to agent {agent_type}, 
                task {task_type or 'default'}"
        )

    def configure_fallback(
        self, fallback_enabled: bool = True, fallback_config: Optional[Dict] = None
    ) -> None:
        """Configure fallback behavior securely."""
        try:
            # Validate and sanitize configuration
            if fallback_config:
                # Validate configuration structure
                allowed_keys = {
                    "max_attempts",
                    "default_model_id",
                    "logging_level",
                    "use_general_purpose_fallback",
                    "fallback_preferences",
                    "secure_mode",
                    "allowed_model_types",
                }
                invalid_keys = set(fallback_config.keys()) - allowed_keys
                if invalid_keys:
                    raise ValueError(f"Invalid configuration keys: {invalid_keys}")

            # Default configuration with secure defaults
            default_config = {
                "max_attempts": 3,
                "logging_level": logging.INFO,
                "use_general_purpose_fallback": True,
                "secure_mode": True,
            }

            # Apply custom configuration
            if fallback_config:
                for key, value in fallback_config.items():
                    if key in allowed_keys:
                        default_config[key] = value

            # Update the fallback manager
            self.fallback_manager.fallback_enabled = fallback_enabled
            self.fallback_manager.max_attempts = default_config["max_attempts"]
            if "default_model_id" in default_config:
                self.fallback_manager.default_model_id = \
                    default_config["default_model_id"]
            if "fallback_preferences" in default_config:
                self.fallback_manager.fallback_preferences = \
                    default_config["fallback_preferences"]
            self.fallback_manager.logging_level = default_config["logging_level"]

            logger.info(f"Updated fallback configuration. Enabled: {fallback_enabled}")

        except Exception as e:
            logger.error(f"Error configuring fallback: {e}")
            raise

    def get_fallback_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics about fallback effectiveness securely."""
        try:
            metrics = self.fallback_manager.get_fallback_metrics()
            # Sanitize metrics before returning
            sanitized_metrics = {}
            for strategy, data in metrics.items():
                sanitized_metrics[str(strategy)] = {
                    "success_rate": float(data.get("success_rate", 0.0)),
                    "total_attempts": int(data.get("total_attempts", 0)),
                    "successful_attempts": int(data.get("successful_attempts", 0)),
                }
            return sanitized_metrics
        except Exception as e:
            logger.error(f"Error getting fallback metrics: {e}")
            return {}

    def get_fallback_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get sanitized history of fallback events."""
        try:
            # Validate limit
            limit = max(1, min(1000, limit))  # Constrain between 1 and 1000
            history = self.fallback_manager.get_fallback_history(limit)

            # Sanitize history entries
            sanitized_history = []
            for entry in history:
                sanitized_entry = {
                    "timestamp": str(entry.get("timestamp", "")),
                    "model_id": str(entry.get("model_id", "")),
                    "status": str(entry.get("status", "")),
                    "error": str(entry.get("error", "")),
                }
                sanitized_history.append(sanitized_entry)

            return sanitized_history
        except Exception as e:
            logger.error(f"Error getting fallback history: {e}")
            return []


class AgentModelIntegration:
    """Secure integration between AI models and agents."""

    def __init__(
        self,
        model_manager: ModelManager,
        model_config: Optional[ModelConfig] = None,
        fallback_preferences: Optional[Dict[str, List[str]]] = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize secure agent - model integration."""
        self.model_manager = model_manager
        self.model_config = model_config or ModelConfig.get_default()
        self._fallback_manager = FallbackManager(
            max_attempts=max_retries,
            fallback_preferences=fallback_preferences,
            secure_mode=True,  # Enable secure mode by default
        )

    async def get_completion(self, prompt: str, model_id: Optional[str] = None, 
        **kwargs) -> str:
        """Get a secure text completion from an AI model."""
        try:
            # Validate prompt
            if not isinstance(prompt, str):
                raise ValueError("Prompt must be a string")

            # Limit prompt length for security
            max_prompt_length = 4096  # Reasonable limit
            if len(prompt) > max_prompt_length:
                raise ValueError(
                    f"Prompt exceeds maximum length of {max_prompt_length}")

            # Sanitize kwargs
            allowed_kwargs = {"temperature", "max_tokens", "top_p", "top_k"}
            sanitized_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}

            # Use fallback manager to handle retries and model switching
            async def completion_attempt(current_model_id: str) -> str:
                model = await self.model_manager.load_model_async(current_model_id)
                return await model.generate_text(prompt, **sanitized_kwargs)

            return await self._fallback_manager.execute_with_fallbacks(
                completion_attempt,
                model_id or self.model_config.default_text_model,
                capability="text - generation",
            )

        except Exception as e:
            logger.error(f"Error in get_completion: {e}")
            raise ModelError("Failed to generate completion") from e

    async def get_embedding(
        self, text: str, model_id: Optional[str] = None, **kwargs
    ) -> List[float]:
        """Get secure embeddings from an AI model."""
        try:
            # Validate input
            if not isinstance(text, str):
                raise ValueError("Text must be a string")

            # Limit input length for security
            max_text_length = 4096  # Reasonable limit
            if len(text) > max_text_length:
                raise ValueError(f"Text exceeds maximum length of {max_text_length}")

            # Sanitize kwargs
            allowed_kwargs = {"pooling", "normalize"}
            sanitized_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}

            async def embedding_attempt(current_model_id: str) -> List[float]:
                model = await self.model_manager.load_model_async(current_model_id)
                embeddings = await model.generate_embeddings(text, **sanitized_kwargs)

                # Validate embeddings
                if not isinstance(embeddings, list) or not all(
                    isinstance(x, float) for x in embeddings
                ):
                    raise ValueError("Invalid embedding format")

                return embeddings

            return await self._fallback_manager.execute_with_fallbacks(
                embedding_attempt,
                model_id or self.model_config.default_embedding_model,
                capability="embedding",
            )

        except Exception as e:
            logger.error(f"Error in get_embedding: {e}")
            raise ModelError("Failed to generate embeddings") from e
