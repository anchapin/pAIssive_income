"""
"""
Example usage of the AgentModelProvider.
Example usage of the AgentModelProvider.


This script demonstrates how to use the AgentModelProvider to assign
This script demonstrates how to use the AgentModelProvider to assign
and use AI models for different agents.
and use AI models for different agents.
"""
"""


import logging
import logging
import os
import os
import sys
import sys


from ai_models import AgentModelProvider, ModelInfo, ModelManager
from ai_models import AgentModelProvider, ModelInfo, ModelManager


# Add the parent directory to the path to import the ai_models module
# Add the parent directory to the path to import the ai_models module
sys.path.append(
sys.path.append(
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
)
# Set up logging
# Set up logging
logging.basicConfig(
logging.basicConfig(
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
)
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)




def main():
    def main():
    """
    """
    Main function to demonstrate the AgentModelProvider.
    Main function to demonstrate the AgentModelProvider.
    """
    """
    print("=" * 80)
    print("=" * 80)
    print("AgentModelProvider Example")
    print("AgentModelProvider Example")
    print("=" * 80)
    print("=" * 80)


    # Create a model manager
    # Create a model manager
    manager = ModelManager()
    manager = ModelManager()


    # Discover models
    # Discover models
    print("\nDiscovering models...")
    print("\nDiscovering models...")
    discovered_models = manager.discover_models()
    discovered_models = manager.discover_models()
    print(f"Discovered {len(discovered_models)} models")
    print(f"Discovered {len(discovered_models)} models")


    # Create an agent model provider
    # Create an agent model provider
    provider = AgentModelProvider(manager)
    provider = AgentModelProvider(manager)


    # Register some example models if none were discovered
    # Register some example models if none were discovered
    if not discovered_models:
    if not discovered_models:
    print("\nNo models discovered. Registering example models...")
    print("\nNo models discovered. Registering example models...")


    # Register a Hugging Face model
    # Register a Hugging Face model
    hf_model = ModelInfo(
    hf_model = ModelInfo(
    id="example-hf-model",
    id="example-hf-model",
    name="Example HF Model",
    name="Example HF Model",
    type="huggingface",
    type="huggingface",
    path="gpt2",  # This is a small model available on Hugging Face
    path="gpt2",  # This is a small model available on Hugging Face
    description="Example Hugging Face model for text generation",
    description="Example Hugging Face model for text generation",
    format="huggingface",
    format="huggingface",
    )
    )
    manager.register_model(hf_model)
    manager.register_model(hf_model)
    print(f"Registered example Hugging Face model: {hf_model.name}")
    print(f"Registered example Hugging Face model: {hf_model.name}")


    # Register an embedding model
    # Register an embedding model
    embedding_model = ModelInfo(
    embedding_model = ModelInfo(
    id="example-embedding-model",
    id="example-embedding-model",
    name="Example Embedding Model",
    name="Example Embedding Model",
    type="embedding",
    type="embedding",
    path="all-MiniLM-L6-v2",  # This is a small embedding model
    path="all-MiniLM-L6-v2",  # This is a small embedding model
    description="Example embedding model for text similarity",
    description="Example embedding model for text similarity",
    format="huggingface",
    format="huggingface",
    )
    )
    manager.register_model(embedding_model)
    manager.register_model(embedding_model)
    print(f"Registered example embedding model: {embedding_model.name}")
    print(f"Registered example embedding model: {embedding_model.name}")


    # Get all registered models
    # Get all registered models
    all_models = manager.get_all_models()
    all_models = manager.get_all_models()
    print(f"\nAll Registered Models ({len(all_models)}):")
    print(f"\nAll Registered Models ({len(all_models)}):")
    for model in all_models:
    for model in all_models:
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")


    # Try to get models for different agents
    # Try to get models for different agents
    agent_types = ["researcher", "developer", "monetization", "marketing", "feedback"]
    agent_types = ["researcher", "developer", "monetization", "marketing", "feedback"]


    print("\nTrying to get models for different agents...")
    print("\nTrying to get models for different agents...")
    for agent_type in agent_types:
    for agent_type in agent_types:
    try:
    try:
    model = provider.get_model_for_agent(agent_type)
    model = provider.get_model_for_agent(agent_type)
    model_info = manager.get_model_info(
    model_info = manager.get_model_info(
    provider.agent_models[agent_type]["default"]
    provider.agent_models[agent_type]["default"]
    )
    )
    print(f"Got model for {agent_type} agent: {model_info.name}")
    print(f"Got model for {agent_type} agent: {model_info.name}")
except ValueError as e:
except ValueError as e:
    print(f"Error getting model for {agent_type} agent: {e}")
    print(f"Error getting model for {agent_type} agent: {e}")


    # Try to get models for different tasks
    # Try to get models for different tasks
    task_types = ["text-generation", "embedding", "classification", "summarization"]
    task_types = ["text-generation", "embedding", "classification", "summarization"]


    print("\nTrying to get models for different tasks...")
    print("\nTrying to get models for different tasks...")
    for task_type in task_types:
    for task_type in task_types:
    try:
    try:
    model = provider.get_model_for_agent("researcher", task_type)
    model = provider.get_model_for_agent("researcher", task_type)
    model_info = manager.get_model_info(
    model_info = manager.get_model_info(
    provider.agent_models["researcher"][task_type]
    provider.agent_models["researcher"][task_type]
    )
    )
    print(
    print(
    f"Got model for researcher agent, task {task_type}: {model_info.name}"
    f"Got model for researcher agent, task {task_type}: {model_info.name}"
    )
    )
except ValueError as e:
except ValueError as e:
    print(f"Error getting model for researcher agent, task {task_type}: {e}")
    print(f"Error getting model for researcher agent, task {task_type}: {e}")


    # Print agent model assignments
    # Print agent model assignments
    assignments = provider.get_agent_model_assignments()
    assignments = provider.get_agent_model_assignments()
    print("\nAgent Model Assignments:")
    print("\nAgent Model Assignments:")
    for agent_type, tasks in assignments.items():
    for agent_type, tasks in assignments.items():
    for task_type, model_id in tasks.items():
    for task_type, model_id in tasks.items():
    model_info = manager.get_model_info(model_id)
    model_info = manager.get_model_info(model_id)
    print(
    print(
    f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}"
    f"Agent: {agent_type}, Task: {task_type}, Model: {model_info.name if model_info else model_id}"
    )
    )


    # Manually assign a model to an agent
    # Manually assign a model to an agent
    if all_models:
    if all_models:
    model_to_assign = all_models[0]
    model_to_assign = all_models[0]
    print(
    print(
    f"\nManually assigning model {model_to_assign.name} to developer agent..."
    f"\nManually assigning model {model_to_assign.name} to developer agent..."
    )
    )
    provider.assign_model_to_agent("developer", model_to_assign.id, "custom-task")
    provider.assign_model_to_agent("developer", model_to_assign.id, "custom-task")


    # Verify the assignment
    # Verify the assignment
    assignments = provider.get_agent_model_assignments()
    assignments = provider.get_agent_model_assignments()
    for agent_type, tasks in assignments.items():
    for agent_type, tasks in assignments.items():
    if agent_type == "developer" and "custom-task" in tasks:
    if agent_type == "developer" and "custom-task" in tasks:
    model_id = tasks["custom-task"]
    model_id = tasks["custom-task"]
    model_info = manager.get_model_info(model_id)
    model_info = manager.get_model_info(model_id)
    print(
    print(
    f"Verified assignment: Agent: developer, Task: custom-task, Model: {model_info.name if model_info else model_id}"
    f"Verified assignment: Agent: developer, Task: custom-task, Model: {model_info.name if model_info else model_id}"
    )
    )


    print("\nExample completed successfully!")
    print("\nExample completed successfully!")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()

