"""
"""
Example usage of the ModelManager.
Example usage of the ModelManager.


This script demonstrates how to use the ModelManager to discover, register,
This script demonstrates how to use the ModelManager to discover, register,
and load AI models.
and load AI models.
"""
"""


import logging
import logging
import os
import os
import sys
import sys


from ai_models import ModelManager
from ai_models import ModelManager


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
    Main function to demonstrate the ModelManager.
    Main function to demonstrate the ModelManager.
    """
    """
    print("=" * 80)
    print("=" * 80)
    print("ModelManager Example")
    print("ModelManager Example")
    print("=" * 80)
    print("=" * 80)


    # Create a model manager with default configuration
    # Create a model manager with default configuration
    manager = ModelManager()
    manager = ModelManager()


    # Print system information
    # Print system information
    system_info = manager.get_system_info()
    system_info = manager.get_system_info()
    print("\nSystem Information:")
    print("\nSystem Information:")
    print(f"Platform: {system_info['platform']}")
    print(f"Platform: {system_info['platform']}")
    print(f"Python Version: {system_info['python_version']}")
    print(f"Python Version: {system_info['python_version']}")
    print(f"CPU Count: {system_info['cpu_count']}")
    print(f"CPU Count: {system_info['cpu_count']}")
    if system_info.get("memory_gb"):
    if system_info.get("memory_gb"):
    print(f"Memory: {system_info['memory_gb']} GB")
    print(f"Memory: {system_info['memory_gb']} GB")


    if system_info["gpu_available"]:
    if system_info["gpu_available"]:
    print("\nGPU Information:")
    print("\nGPU Information:")
    for i, gpu in enumerate(system_info["gpu_info"]):
    for i, gpu in enumerate(system_info["gpu_info"]):
    print(f"GPU {i}: {gpu['name']} ({gpu['memory_gb']} GB)")
    print(f"GPU {i}: {gpu['name']} ({gpu['memory_gb']} GB)")
    else:
    else:
    print("\nNo GPU detected")
    print("\nNo GPU detected")


    # Print dependency information
    # Print dependency information
    dependencies = manager.get_dependencies_info()
    dependencies = manager.get_dependencies_info()
    print("\nDependency Information:")
    print("\nDependency Information:")
    for name, info in dependencies.items():
    for name, info in dependencies.items():
    status = "Installed" if info["installed"] else "Not Installed"
    status = "Installed" if info["installed"] else "Not Installed"
    version = info.get("version", "N/A")
    version = info.get("version", "N/A")
    print(f"{name}: {status} (Version: {version})")
    print(f"{name}: {status} (Version: {version})")


    # Discover models
    # Discover models
    print("\nDiscovering models...")
    print("\nDiscovering models...")
    discovered_models = manager.discover_models()
    discovered_models = manager.discover_models()
    print(f"Discovered {len(discovered_models)} models")
    print(f"Discovered {len(discovered_models)} models")


    # Print all registered models
    # Print all registered models
    all_models = manager.get_all_models()
    all_models = manager.get_all_models()
    print(f"\nAll Registered Models ({len(all_models)}):")
    print(f"\nAll Registered Models ({len(all_models)}):")
    for model in all_models:
    for model in all_models:
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")


    # Try to load a model if available
    # Try to load a model if available
    if all_models:
    if all_models:
    model_to_load = all_models[0]
    model_to_load = all_models[0]
    print(f"\nTrying to load model: {model_to_load.name}")
    print(f"\nTrying to load model: {model_to_load.name}")


    try:
    try:
    manager.load_model(model_to_load.id)
    manager.load_model(model_to_load.id)
    print(f"Successfully loaded model: {model_to_load.name}")
    print(f"Successfully loaded model: {model_to_load.name}")


    # Unload the model
    # Unload the model
    manager.unload_model(model_to_load.id)
    manager.unload_model(model_to_load.id)
    print(f"Unloaded model: {model_to_load.name}")
    print(f"Unloaded model: {model_to_load.name}")


except Exception as e:
except Exception as e:
    print(f"Error loading model: {e}")
    print(f"Error loading model: {e}")


    print("\nExample completed successfully!")
    print("\nExample completed successfully!")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()

