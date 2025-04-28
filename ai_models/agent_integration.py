"""
Integration with the agent team for the AI Models module.

This module provides functions and classes for integrating the AI Models module
with the agent team, allowing agents to use local AI models for their tasks.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interfaces.model_interfaces import IModelManager, IModelInfo
from .model_manager import ModelManager, ModelInfo
from .model_config import ModelConfig
from dependency_container import get_container

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

    def __init__(self, model_manager: Optional[IModelManager] = None, 
                fallback_enabled: bool = True, 
                fallback_config: Optional[Dict] = None):
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
        
        # Fallback configuration
        self.fallback_enabled = fallback_enabled
        self.fallback_config = fallback_config or {
            "max_attempts": 3,                 # Maximum number of fallback attempts
            "default_model_id": None,          # Global fallback model ID
            "logging_level": logging.INFO,     # Logging level for fallback events
            "use_general_purpose_fallback": True,  # Use general purpose models as fallbacks
            "fallback_preferences": {          # Fallback preferences for different agent types
                "researcher": ["huggingface", "llama", "general-purpose"],
                "developer": ["huggingface", "llama", "general-purpose"],
                "monetization": ["huggingface", "general-purpose"],
                "marketing": ["huggingface", "general-purpose"],
                "default": ["huggingface", "general-purpose"]
            }
        }
        
        # Set up logging for fallback events
        self.logger = logging.getLogger(__name__ + ".fallback")
        self.logger.setLevel(self.fallback_config["logging_level"])

    def get_model_for_agent(self, agent_type: str, task_type: Optional[str] = None) -> Any:
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
        if agent_type in self.agent_models and (task_type is None or task_type in self.agent_models[agent_type]):
            model_id = self.agent_models[agent_type].get(task_type) if task_type else list(self.agent_models[agent_type].values())[0]
            try:
                return self.model_manager.load_model(model_id)
            except Exception as e:
                if not self.fallback_enabled:
                    raise e
                # Log the failure and continue to fallback mechanisms
                self.logger.warning(
                    f"Failed to load assigned model {model_id} for agent {agent_type}, task {task_type}: {str(e)}. "
                    f"Attempting fallback."
                )

        # Attempt to find a suitable model with fallback support
        model_info, fallback_used = self._find_model_with_fallback(agent_type, task_type)

        if not model_info:
            raise ValueError(f"No suitable model found for agent type {agent_type} and task type {task_type} "
                           f"after exhausting all fallback options.")

        # Load the model
        try:
            model = self.model_manager.load_model(model_info.id)
        except Exception as e:
            # If we can't load the model even after fallback, we give up
            raise ValueError(f"Failed to load model {model_info.id} for agent {agent_type}, task {task_type}: {str(e)}") from e

        # Store the model assignment
        if agent_type not in self.agent_models:
            self.agent_models[agent_type] = {}

        self.agent_models[agent_type][task_type or "default"] = model_info.id

        # Log successful model assignment
        if fallback_used:
            self.logger.info(f"Successfully assigned fallback model {model_info.id} to agent {agent_type}, task {task_type}")
        else:
            logger.info(f"Assigned model {model_info.id} to agent {agent_type}, task {task_type}")

        return model

    def _find_model_with_fallback(self, agent_type: str, task_type: Optional[str] = None) -> Tuple[Optional[IModelInfo], bool]:
        """
        Find a suitable model with fallback support.
        
        This method tries to find a suitable model for the agent and task type.
        If fallback is enabled and the initial search fails, it will try fallback options.

        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)
            
        Returns:
            Tuple containing:
              - IModelInfo instance or None if no suitable model is found
              - Boolean indicating whether a fallback was used
        """
        # First try the normal model selection logic
        model_info = self._find_suitable_model(agent_type, task_type)
        
        # If we found a model, return it with fallback=False
        if model_info:
            return model_info, False
            
        # If fallback is disabled or we have no fallback config, just return None
        if not self.fallback_enabled or not self.fallback_config:
            return None, False
        
        self.logger.info(f"No primary model found for agent {agent_type}, task {task_type}. Trying fallback options.")
        
        # Try fallback options
        max_attempts = self.fallback_config.get("max_attempts", 3)
        attempts = 0
        
        # 1. Try the default model for this agent type if specified in fallback config
        agent_fallback_prefs = self.fallback_config.get("fallback_preferences", {}).get(
            agent_type, self.fallback_config.get("fallback_preferences", {}).get("default", [])
        )
        
        for model_type in agent_fallback_prefs:
            if attempts >= max_attempts:
                break
                
            self.logger.info(f"Trying fallback model type '{model_type}' for agent {agent_type}, task {task_type}")
            models = self.model_manager.get_models_by_type(model_type)
            
            if models:
                self.logger.info(f"Found fallback model {models[0].id} of type '{model_type}'")
                return models[0], True
                
            attempts += 1
        
        # 2. Try the global default model if specified
        default_model_id = self.fallback_config.get("default_model_id")
        if default_model_id:
            self.logger.info(f"Trying global default model {default_model_id}")
            model_info = self.model_manager.get_model_info(default_model_id)
            if model_info:
                return model_info, True
        
        # 3. Last resort: any available model
        if self.fallback_config.get("use_general_purpose_fallback", True):
            self.logger.warning(f"No specific fallbacks available for {agent_type}/{task_type}. Trying any available model.")
            all_models = self.model_manager.get_all_models()
            if all_models:
                self.logger.info(f"Using general purpose fallback model {all_models[0].id}")
                return all_models[0], True
                
        # No models found even with fallbacks
        self.logger.error(f"Failed to find any model for agent {agent_type}, task {task_type} after trying fallbacks")
        return None, False

    def _find_suitable_model(self, agent_type: str, task_type: Optional[str] = None) -> Optional[IModelInfo]:
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

        # Define model preferences for different agent types
        # This maps agent types to a prioritized list of model types they prefer
        agent_preferences = {
            "researcher": ["huggingface", "llama"],
            "developer": ["huggingface", "llama"],
            "monetization": ["huggingface", "llama"],
            "marketing": ["huggingface", "llama"],
            "feedback": ["huggingface", "llama"]
        }

        # Define model preferences for different task types
        # This maps task types to a prioritized list of model types best suited for them
        task_preferences = {
            "text-generation": ["huggingface", "llama"],
            "embedding": ["embedding"],
            "classification": ["huggingface"],
            "summarization": ["huggingface", "llama"],
            "translation": ["huggingface"]
        }

        # Get preferences for the specified agent type
        # Use default preferences if agent_type is not found in the mapping
        agent_prefs = agent_preferences.get(agent_type, ["huggingface", "llama"])

        # Get preferences for the specified task type
        # Only consider task preferences if a task_type was provided
        task_prefs = task_preferences.get(task_type, ["huggingface", "llama"]) if task_type else []

        # Combine preferences
        # If task_prefs is not empty, find the intersection (preferences that satisfy both)
        # Otherwise, just use the agent preferences
        combined_prefs = list(set(agent_prefs) & set(task_prefs)) if task_prefs else agent_prefs

        # Find a model that matches the preferences
        # Try each preferred model type in order until a match is found
        for model_type in combined_prefs:
            models = self.model_manager.get_models_by_type(model_type)
            if models:
                return models[0]  # Return the first model of the preferred type

        # If no model matches the preferences, return any available model as fallback
        return all_models[0] if all_models else None

    def assign_model_to_agent(self, agent_type: str, model_id: str, task_type: Optional[str] = None) -> None:
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
        logger.info(f"Assigned model {model_id} to agent {agent_type}, task {task_type or 'default'}")

    def unassign_model_from_agent(self, agent_type: str, task_type: Optional[str] = None) -> bool:
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
                    logger.info(f"Unassigned model from agent {agent_type}, task {task_type}")
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
        
    def configure_fallback(self, fallback_enabled: bool = True, fallback_config: Optional[Dict] = None) -> None:
        """
        Configure the fallback behavior.
        
        Args:
            fallback_enabled: Whether fallback should be enabled
            fallback_config: Configuration options for fallback behavior
        """
        self.fallback_enabled = fallback_enabled
        
        if fallback_config:
            # Update the fallback configuration, preserving any missing values
            for key, value in fallback_config.items():
                self.fallback_config[key] = value
                
        # Update logger level if specified in the config
        if "logging_level" in self.fallback_config:
            self.logger.setLevel(self.fallback_config["logging_level"])
            
        logger.info(f"Fallback configuration updated. Enabled: {fallback_enabled}")
        
    def set_default_fallback_model(self, model_id: str) -> None:
        """
        Set the default model to use as a fallback when no suitable models are found.
        
        Args:
            model_id: ID of the model to use as default fallback
            
        Raises:
            ValueError: If the model is not found
        """
        # Check if the model exists
        model_info = self.model_manager.get_model_info(model_id)
        if not model_info:
            raise ValueError(f"Model with ID {model_id} not found")
            
        self.fallback_config["default_model_id"] = model_id
        logger.info(f"Set default fallback model to {model_id}")
        
    def add_agent_fallback_preference(self, agent_type: str, model_types: List[str]) -> None:
        """
        Add fallback preferences for a specific agent type.
        
        Args:
            agent_type: Type of agent to set preferences for
            model_types: List of model types in order of preference for fallbacks
        """
        if "fallback_preferences" not in self.fallback_config:
            self.fallback_config["fallback_preferences"] = {}
            
        self.fallback_config["fallback_preferences"][agent_type] = model_types
        logger.info(f"Set fallback preferences for agent {agent_type}: {model_types}")


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
            print(f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}")

    # Configure fallback behavior
    provider.configure_fallback(
        fallback_enabled=True,
        fallback_config={
            "max_attempts": 5,
            "logging_level": logging.DEBUG,
            "use_general_purpose_fallback": True
        }
    )
    
    # Set a default fallback model
    try:
        model = manager.get_all_models()[0]
        if model:
            provider.set_default_fallback_model(model.id)
    except (IndexError, ValueError) as e:
        print(f"Couldn't set default fallback model: {e}")
