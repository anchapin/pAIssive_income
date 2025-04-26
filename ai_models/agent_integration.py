"""
Integration with the agent team for the AI Models module.

This module provides functions and classes for integrating the AI Models module
with the agent team, allowing agents to use local AI models for their tasks.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union

from .model_manager import ModelManager, ModelInfo
from .model_config import ModelConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentModelProvider:
    """
    Provider for AI models used by agents.
    """
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        """
        Initialize the agent model provider.
        
        Args:
            model_manager: Optional model manager instance
        """
        self.model_manager = model_manager or ModelManager()
        self.agent_models: Dict[str, Dict[str, Any]] = {}
    
    def get_model_for_agent(self, agent_type: str, task_type: Optional[str] = None) -> Any:
        """
        Get a model for a specific agent and task.
        
        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)
            
        Returns:
            Model instance
            
        Raises:
            ValueError: If no suitable model is found
        """
        # Check if the agent already has a model assigned
        if agent_type in self.agent_models and (task_type is None or task_type in self.agent_models[agent_type]):
            model_id = self.agent_models[agent_type].get(task_type) if task_type else list(self.agent_models[agent_type].values())[0]
            return self.model_manager.load_model(model_id)
        
        # Find a suitable model based on agent type and task type
        model_info = self._find_suitable_model(agent_type, task_type)
        
        if not model_info:
            raise ValueError(f"No suitable model found for agent type {agent_type} and task type {task_type}")
        
        # Load the model
        model = self.model_manager.load_model(model_info.id)
        
        # Store the model assignment
        if agent_type not in self.agent_models:
            self.agent_models[agent_type] = {}
        
        self.agent_models[agent_type][task_type or "default"] = model_info.id
        
        return model
    
    def _find_suitable_model(self, agent_type: str, task_type: Optional[str] = None) -> Optional[ModelInfo]:
        """
        Find a suitable model for a specific agent and task.
        
        Args:
            agent_type: Type of agent (researcher, developer, etc.)
            task_type: Optional type of task (text-generation, embedding, etc.)
            
        Returns:
            ModelInfo instance or None if no suitable model is found
        """
        # Get all available models
        all_models = self.model_manager.get_all_models()
        
        # Define model preferences for different agent types
        agent_preferences = {
            "researcher": ["huggingface", "llama"],
            "developer": ["huggingface", "llama"],
            "monetization": ["huggingface", "llama"],
            "marketing": ["huggingface", "llama"],
            "feedback": ["huggingface", "llama"]
        }
        
        # Define model preferences for different task types
        task_preferences = {
            "text-generation": ["huggingface", "llama"],
            "embedding": ["embedding"],
            "classification": ["huggingface"],
            "summarization": ["huggingface", "llama"],
            "translation": ["huggingface"]
        }
        
        # Get preferences for the specified agent type
        agent_prefs = agent_preferences.get(agent_type, ["huggingface", "llama"])
        
        # Get preferences for the specified task type
        task_prefs = task_preferences.get(task_type, ["huggingface", "llama"]) if task_type else []
        
        # Combine preferences
        combined_prefs = list(set(agent_prefs) & set(task_prefs)) if task_prefs else agent_prefs
        
        # Find a model that matches the preferences
        for model_type in combined_prefs:
            models = self.model_manager.get_models_by_type(model_type)
            if models:
                return models[0]
        
        # If no model matches the preferences, return any available model
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
                    return True
            else:
                del self.agent_models[agent_type]
                return True
        
        return False
    
    def get_agent_model_assignments(self) -> Dict[str, Dict[str, str]]:
        """
        Get all agent model assignments.
        
        Returns:
            Dictionary of agent model assignments
        """
        return self.agent_models


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
