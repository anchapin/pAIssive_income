"""
Integration with the agent team for the AI Models module.

This module provides functions and classes for integrating the AI Models module
with the agent team, allowing agents to use local AI models for their tasks.
"""


import logging
import os
import sys
from typing import Any, Dict, Optional

sys.path.insert
from dependency_container import get_container
from interfaces.model_interfaces import IModelInfo, IModelManager


from .fallbacks import FallbackManager, FallbackStrategy
from .model_manager import ModelManager



(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Import the fallback manager classes
# Import specific error types

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentModelProvider:
    """
    Provider for AI models used by agents.

    This class serves as a bridge between the Agent Team module and the AI Models module,
    providing a way for different agent types (researcher, developer, etc.) to access
    appropriate AI models for their specific tasks. It implements a sophisticated model
    selection algorithm that considers both the agent type and task type when finding
    the most suitable model.

    The provider maintains a mapping of agent-to-model assignments and can dynamically
    find models based on predefined preferences when no explicit assignment exists.

    It also implements a robust fallback strategy to ensure that agents always have
    a model to use, even if their preferred models are not available.
    """

    def __init__(
        self,
        model_manager: Optional[IModelManager] = None,
        fallback_enabled: bool = True,
        fallback_config: Optional[Dict] = None,
    ):
        """
        Initialize the agent model provider.

        Args:
            model_manager: Optional model manager instance
            fallback_enabled: Whether fallback mechanisms should be enabled
            fallback_config: Optional configuration for fallback behavior
        """
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
        # Structure: {agent_type: {task_type: model_id}}
        self.agent_models: Dict[str, Dict[str, Any]] = {}

        # Default fallback configuration if none provided
        default_fallback_config = {
            "max_attempts": 3,  # Maximum number of fallback attempts
            "default_model_id": None,  # Global fallback model ID
            "logging_level": logging.INFO,  # Logging level for fallback events
            "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
            "fallback_preferences": {  # Fallback preferences for different agent types
                "researcher": ["huggingface", "llama", "general-purpose"],
                "developer": ["huggingface", "llama", "general-purpose"],
                "monetization": ["huggingface", "general-purpose"],
                "marketing": ["huggingface", "general-purpose"],
                "default": ["huggingface", "general-purpose"],
            },
        }

        # Apply any custom fallback configuration
        if fallback_config:
            for key, value in fallback_config.items():
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

    def get_model_for_agent(
        self, agent_type: str, task_type: Optional[str] = None
    ) -> Any:
        """
        Get a model for a specific agent and task.

        This method implements a multi-step model selection process:
        1. Check if there's an explicit assignment for this agent and task
        2. If not, find a suitable model based on agent and task preferences
        3. Load the selected model
        4. Record the assignment for future use

        If fallback is enabled and initial model selection fails, the method will
        attempt to find alternative models based on the fallback configuration.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)

        Returns:
            Model instance

        Raises:
            ValueError: If no suitable model is found after exhausting all fallbacks
        """
        # Check if the agent already has a model assigned
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
            except Exception as e:
                if not self.fallback_manager.fallback_enabled:
                    raise e
                # Log the failure and continue to fallback mechanisms
                logger.warning(
                    f"Failed to load assigned model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
                    "Attempting fallback."
                )
                # Try to find a fallback model
                fallback_model_info, event = self.fallback_manager.find_fallback_model(
                    original_model_id=model_id,
                    agent_type=agent_type,
                    task_type=task_type,
                )

                if fallback_model_info:
                    # Try to load the fallback model
                    try:
                        model = self.model_manager.load_model(fallback_model_info.id)
                        # Update the agent's model assignment to use the fallback model
                        self.agent_models[agent_type][
                            task_type or "default"
                        ] = fallback_model_info.id
                        return model
                    except Exception as load_error:
                        # Mark the fallback as unsuccessful
                        if event:
                            self.fallback_manager.track_fallback_event(
                                event, was_successful=False
                            )
                        # Re-raise with additional context
                        raise ValueError(
                            f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
                        ) from load_error

        # If we don't have a model assignment, find a suitable model
        model_info = self._find_suitable_model(agent_type, task_type)

        # If no suitable model found, try fallback
        if not model_info and self.fallback_manager.fallback_enabled:
            logger.info(
                f"No suitable model found for agent {agent_type}, task {task_type}. Attempting fallback."
            )
            fallback_model_info, _ = self.fallback_manager.find_fallback_model(
                agent_type=agent_type, task_type=task_type
            )
            model_info = fallback_model_info

        if not model_info:
            raise ValueError(
                f"No suitable model found for agent type {agent_type} and task type {task_type} "
                "after exhausting all fallback options."
            )

        # Load the model
        try:
            model = self.model_manager.load_model(model_info.id)
        except Exception as e:
            # If we can't load the model, try one last fallback to ANY_AVAILABLE strategy
            if self.fallback_manager.fallback_enabled:
                logger.warning(
                    f"Failed to load model {model_info.id}. Trying last-resort fallback."
                )
                fallback_model_info, _ = self.fallback_manager.find_fallback_model(
                    original_model_id=model_info.id,
                    agent_type=agent_type,
                    task_type=task_type,
                    strategy_override=FallbackStrategy.ANY_AVAILABLE,
                )

                if fallback_model_info:
                    try:
                        model = self.model_manager.load_model(fallback_model_info.id)
                        model_info = fallback_model_info
                    except Exception as fallback_error:
                        raise ValueError(
                            f"Failed to load model for agent {agent_type}, task {task_type} "
                            f"after exhausting all fallbacks: {str(fallback_error)}"
                        ) from fallback_error
                else:
                    raise ValueError(
                        f"Failed to load model for agent {agent_type}, task {task_type}. "
                        "No fallback models available."
                    ) from e
            else:
                raise ValueError(
                    f"Failed to load model {model_info.id} for agent {agent_type}, task {task_type}: {str(e)}"
                ) from e

        # Store the model assignment
        if agent_type not in self.agent_models:
            self.agent_models[agent_type] = {}

        self.agent_models[agent_type][task_type or "default"] = model_info.id
        logger.info(
            f"Assigned model {model_info.id} to agent {agent_type}, task {task_type or 'default'}"
        )

        return model

    def _find_suitable_model(
        self, agent_type: str, task_type: Optional[str] = None
    ) -> Optional[IModelInfo]:
        """
        Find a suitable model for a specific agent and task.

        This algorithm implements a preference-based model selection strategy:

        1. Define preference lists for both agent types and task types
        2. For the given agent_type and task_type, retrieve their specific preferences
        3. Find the intersection of preferences if both are provided (agent AND task preferences)
        4. Try to find models matching the combined preferences in order of priority
        5. Fall back to any available model if no matches found

        This approach ensures that each agent gets a model that is optimized for both
        its general role (agent_type) and specific current task (task_type).

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)

        Returns:
            IModelInfo instance or None if no suitable model is found
        """
        # Get all available models
        all_models = self.model_manager.get_all_models()
        if not all_models:
            return None

        # Define model preferences for different agent types
        # This maps agent types to a prioritized list of model types they prefer
        agent_preferences = {
            "researcher": ["huggingface", "llama"],
            "developer": ["huggingface", "llama"],
            "monetization": ["huggingface", "llama"],
            "marketing": ["huggingface", "llama"],
            "feedback": ["huggingface", "llama"],
        }

        # Define model preferences for different task types
        # This maps task types to a prioritized list of model types best suited for them
        task_preferences = {
            "text-generation": ["huggingface", "llama"],
            "embedding": ["embedding"],
            "classification": ["huggingface"],
            "summarization": ["huggingface", "llama"],
            "translation": ["huggingface"],
        }

        # Get preferences for the specified agent type
        # Use default preferences if agent_type is not found in the mapping
        agent_prefs = agent_preferences.get(agent_type, ["huggingface", "llama"])

        # Get preferences for the specified task type
        # Only consider task preferences if a task_type was provided
        task_prefs = (
            task_preferences.get(task_type, ["huggingface", "llama"])
            if task_type
            else []
        )

        # Combine preferences
        # If task_prefs is not empty, find the intersection (preferences that satisfy both)
        # Otherwise, just use the agent preferences
        combined_prefs = (
            list(set(agent_prefs) & set(task_prefs)) if task_prefs else agent_prefs
        )

        # Find a model that matches the preferences
        # Try each preferred model type in order until a match is found
        for model_type in combined_prefs:
            models = self.model_manager.get_models_by_type(model_type)
            if models:
                return models[0]  # Return the first model of the preferred type

        # If no model matches the preferences, return None and let the caller decide what to do
        return None

    def assign_model_to_agent(
        self, agent_type: str, model_id: str, task_type: Optional[str] = None
    ) -> None:
        """
        Assign a specific model to an agent.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            model_id: ID of the model to assign
            task_type: Optional type of task (text-generation, embedding, etc.)

        Raises:
            ValueError: If the model is not found
        """
        # Check if the model exists
        model_info = self.model_manager.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model with ID {model_id} not found")

        # Store the model assignment
        if agent_type not in self.agent_models:
            self.agent_models[agent_type] = {}

        self.agent_models[agent_type][task_type or "default"] = model_id
        logger.info(
            f"Assigned model {model_id} to agent {agent_type}, task {task_type or 'default'}"
        )

    def unassign_model_from_agent(
        self, agent_type: str, task_type: Optional[str] = None
    ) -> bool:
        """
        Unassign a model from an agent.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)

        Returns:
            True if the model was unassigned, False otherwise
        """
        if agent_type in self.agent_models:
            if task_type:
                if task_type in self.agent_models[agent_type]:
                    del self.agent_models[agent_type][task_type]
                    logger.info(
                        f"Unassigned model from agent {agent_type}, task {task_type}"
                    )
                    return True
            else:
                del self.agent_models[agent_type]
                logger.info(f"Unassigned all models from agent {agent_type}")
                return True

        return False

    def get_agent_model_assignments(self) -> Dict[str, Dict[str, str]]:
        """
        Get all agent model assignments.

        Returns:
            Dictionary of agent model assignments
        """
        return self.agent_models

    def get_model_with_fallback(
        self, agent_type: str, model_id: str, task_type: Optional[str] = None
    ) -> Any:
        """
        Get a model with fallback support.

        This method attempts to load the specified model, and if that fails,
        it will try to find a fallback model based on the configured fallback strategy.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            model_id: ID of the model to load
            task_type: Optional type of task (text-generation, embedding, etc.)

        Returns:
            Model instance

        Raises:
            ValueError: If no suitable model is found after exhausting all fallbacks
        """
        try:
            # First try to load the specified model
            return self.model_manager.load_model(model_id)
        except Exception as e:
            if not self.fallback_manager.fallback_enabled:
                raise e

            # Log the failure and continue to fallback mechanisms
            logger.warning(
                f"Failed to load model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
                "Attempting fallback."
            )

            # Try to find a fallback model
            fallback_model_info, event = self.fallback_manager.find_fallback_model(
                original_model_id=model_id, agent_type=agent_type, task_type=task_type
            )

            if fallback_model_info:
                # Try to load the fallback model
                try:
                    model = self.model_manager.load_model(fallback_model_info.id)
                    # Update the agent's model assignment to use the fallback model
                    if agent_type not in self.agent_models:
                        self.agent_models[agent_type] = {}
                    self.agent_models[agent_type][
                        task_type or "default"
                    ] = fallback_model_info.id
                    return model
                except Exception as load_error:
                    # Mark the fallback as unsuccessful
                    if event:
                        self.fallback_manager.track_fallback_event(
                            event, was_successful=False
                        )
                    # Re-raise with additional context
                    raise ValueError(
                        f"Failed to load fallback model {fallback_model_info.id}: {str(load_error)}"
                    ) from load_error

            # If no fallback model found, raise an error
            raise ValueError(
                f"No fallback model found for {model_id} after exhausting all options"
            )

    def configure_fallback(
        self, fallback_enabled: bool = True, fallback_config: Optional[Dict] = None
    ) -> None:
        """
        Configure fallback behavior.

        Args:
            fallback_enabled: Whether fallback mechanisms should be enabled
            fallback_config: Optional configuration for fallback behavior
        """
        # Default fallback configuration if none provided
        default_fallback_config = {
            "max_attempts": 3,  # Maximum number of fallback attempts
            "default_model_id": None,  # Global fallback model ID
            "logging_level": logging.INFO,  # Logging level for fallback events
            "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
            "fallback_preferences": {  # Fallback preferences for different agent types
                "researcher": ["huggingface", "llama", "general-purpose"],
                "developer": ["huggingface", "llama", "general-purpose"],
                "monetization": ["huggingface", "general-purpose"],
                "marketing": ["huggingface", "general-purpose"],
                "default": ["huggingface", "general-purpose"],
            },
        }

        # Apply any custom fallback configuration
        if fallback_config:
            for key, value in fallback_config.items():
                default_fallback_config[key] = value

        # Update the fallback manager
        self.fallback_manager.fallback_enabled = fallback_enabled
        self.fallback_manager.max_attempts = default_fallback_config["max_attempts"]
        self.fallback_manager.default_model_id = default_fallback_config[
            "default_model_id"
        ]
        self.fallback_manager.fallback_preferences = default_fallback_config[
            "fallback_preferences"
        ]
        self.fallback_manager.logging_level = default_fallback_config["logging_level"]

        logger.info(f"Updated fallback configuration. Enabled: {fallback_enabled}")

    def model_has_capability(self, model_id: str, capability: str) -> bool:
        """
        Check if a model has a specific capability.

        Args:
            model_id: ID of the model to check
            capability: Capability to check for

        Returns:
            True if the model has the capability, False otherwise
        """
        model_info = self.model_manager.get_model_info(model_id)
        if not model_info:
            return False

        return capability in model_info.capabilities

    def get_assigned_model_id(
        self, agent_type: str, task_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the currently assigned model ID for an agent and task type.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)

        Returns:
            Assigned model ID or None if no model is assigned
        """
        if agent_type not in self.agent_models:
            return None

        return self.agent_models[agent_type].get(task_type or "default")


# Example usage
if __name__ == "__main__":
    # Create a model manager
    manager = ModelManager()

    # Create an agent model provider
    provider = AgentModelProvider(manager)

    # Get a model for the researcher agent
    try:
        researcher_model = provider.get_model_for_agent("researcher", "text-generation")
        print(f"Got model for researcher agent: {researcher_model}")
    except ValueError as e:
        print(f"Error getting model for researcher agent: {e}")

    # Get a model for the developer agent
    try:
        developer_model = provider.get_model_for_agent("developer")
        print(f"Got model for developer agent: {developer_model}")
    except ValueError as e:
        print(f"Error getting model for developer agent: {e}")

    # Print agent model assignments
    assignments = provider.get_agent_model_assignments()
    print("\nAgent Model Assignments:")
    for agent_type, tasks in assignments.items():
        for task_type, model_id in tasks.items():
            model_info = manager.get_model_info(model_id)
            print(
                f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}"
            )

    # Configure fallback behavior
    provider.configure_fallback(
        fallback_enabled=True,
        fallback_config={
            "max_attempts": 5,
            "logging_level": logging.DEBUG,
            "use_general_purpose_fallback": True,
        },
    )

    # Set a default fallback model
    try:
        all_models = manager.get_all_models()
        if all_models:
            provider.set_default_fallback_model(all_models[0].id)
    except (IndexError, ValueError) as e:
        print(f"Couldn't set default fallback model: {e}")

    # Print fallback metrics after some usage
    metrics = provider.get_fallback_metrics()
    print("\nFallback Metrics:")
    for strategy, stats in metrics.items():
        print(f"Strategy: {strategy}, Success Rate: {stats['success_rate']:.2f}")