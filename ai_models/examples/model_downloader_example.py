"""
"""
Example usage of the ModelDownloader.
Example usage of the ModelDownloader.


This script demonstrates how to use the ModelDownloader to download
This script demonstrates how to use the ModelDownloader to download
models from various sources.
models from various sources.
"""
"""


import logging
import logging
import os
import os
import sys
import sys
import time
import time


from ai_models import DownloadProgress, ModelDownloader, ModelManager
from ai_models import DownloadProgress, ModelDownloader, ModelManager


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
    Main function to demonstrate the ModelDownloader.
    Main function to demonstrate the ModelDownloader.
    """
    """
    print("=" * 80)
    print("=" * 80)
    print("ModelDownloader Example")
    print("ModelDownloader Example")
    print("=" * 80)
    print("=" * 80)


    # Create a model manager
    # Create a model manager
    manager = ModelManager()
    manager = ModelManager()


    # Create a model downloader with the model manager
    # Create a model downloader with the model manager
    downloader = ModelDownloader(model_manager=manager)
    downloader = ModelDownloader(model_manager=manager)


    # Define a callback function for progress updates
    # Define a callback function for progress updates
    def progress_callback(progress: DownloadProgress):
    def progress_callback(progress: DownloadProgress):
    status_emoji = {
    status_emoji = {
    "pending": "⏳",
    "pending": "⏳",
    "downloading": "📥",
    "downloading": "📥",
    "completed": "✅",
    "completed": "✅",
    "failed": "❌",
    "failed": "❌",
    }
    }


    emoji = status_emoji.get(progress.status, "⏳")
    emoji = status_emoji.get(progress.status, "⏳")


    if progress.status == "downloading":
    if progress.status == "downloading":
    print(
    print(
    f"\r{emoji} Status: {progress.status}, Progress: {progress.percentage:.1f}%, "
    f"\r{emoji} Status: {progress.status}, Progress: {progress.percentage:.1f}%, "
    f"Speed: {progress.speed / 1024 / 1024:.2f} MB/s, "
    f"Speed: {progress.speed / 1024 / 1024:.2f} MB/s, "
    f"ETA: {progress.eta:.1f}s",
    f"ETA: {progress.eta:.1f}s",
    end="",
    end="",
    )
    )
    else:
    else:
    print(f"\n{emoji} Status: {progress.status}")
    print(f"\n{emoji} Status: {progress.status}")


    if progress.status == "failed" and progress.error:
    if progress.status == "failed" and progress.error:
    print(f"   Error: {progress.error}")
    print(f"   Error: {progress.error}")


    # Search for models on Hugging Face Hub
    # Search for models on Hugging Face Hub
    print("\nSearching for models on Hugging Face Hub...")
    print("\nSearching for models on Hugging Face Hub...")
    try:
    try:
    models = downloader.search_huggingface_models(query="gpt2", limit=5)
    models = downloader.search_huggingface_models(query="gpt2", limit=5)


    print("\nSearch Results:")
    print("\nSearch Results:")
    for i, model in enumerate(models):
    for i, model in enumerate(models):
    print(
    print(
    f"{i+1}. {model['id']} (Downloads: {model['downloads']}, Likes: {model['likes']})"
    f"{i+1}. {model['id']} (Downloads: {model['downloads']}, Likes: {model['likes']})"
    )
    )


    # Ask the user which model to download
    # Ask the user which model to download
    if models:
    if models:
    print(
    print(
    "\nDownloading a small file from the first model for demonstration..."
    "\nDownloading a small file from the first model for demonstration..."
    )
    )
    model_to_download = models[0]
    model_to_download = models[0]


    # Download just the config file for demonstration
    # Download just the config file for demonstration
    print(f"\nDownloading config.json from {model_to_download['id']}...")
    print(f"\nDownloading config.json from {model_to_download['id']}...")
    task = downloader.download_from_huggingface(
    task = downloader.download_from_huggingface(
    model_id=model_to_download["id"],
    model_id=model_to_download["id"],
    file_name="config.json",
    file_name="config.json",
    callback=progress_callback,
    callback=progress_callback,
    auto_register=True,
    auto_register=True,
    description=f"Model from {model_to_download['id']} (auto-registered)",
    description=f"Model from {model_to_download['id']} (auto-registered)",
    )
    )


    # Wait for the download to complete
    # Wait for the download to complete
    while task.is_running():
    while task.is_running():
    time.sleep(0.1)
    time.sleep(0.1)


    if task.progress.status == "completed":
    if task.progress.status == "completed":
    print(f"\nDownload completed: {task.destination}")
    print(f"\nDownload completed: {task.destination}")


    # Verify the model is registered (should happen automatically)
    # Verify the model is registered (should happen automatically)
    all_models = manager.get_all_models()
    all_models = manager.get_all_models()
    print(f"\nAll registered models after download ({len(all_models)}):")
    print(f"\nAll registered models after download ({len(all_models)}):")
    for model in all_models:
    for model in all_models:
    print(
    print(
    f"- {model.name} (Type: {model.type}, Format: {model.format})"
    f"- {model.name} (Type: {model.type}, Format: {model.format})"
    )
    )
    else:
    else:
    print(f"\nDownload failed: {task.progress.error}")
    print(f"\nDownload failed: {task.progress.error}")


except Exception as e:
except Exception as e:
    print(f"Error: {e}")
    print(f"Error: {e}")


    # Download a model from a URL
    # Download a model from a URL
    print("\nDownloading a file from a URL...")
    print("\nDownloading a file from a URL...")
    try:
    try:
    # Use a small file for demonstration
    # Use a small file for demonstration
    url = (
    url = (
    "https://raw.githubusercontent.com/huggingface/transformers/main/README.md"
    "https://raw.githubusercontent.com/huggingface/transformers/main/README.md"
    )
    )


    task = downloader.download_from_url(
    task = downloader.download_from_url(
    url=url,
    url=url,
    model_id="example-url-download",
    model_id="example-url-download",
    model_type="other",
    model_type="other",
    destination=os.path.join(
    destination=os.path.join(
    downloader.config.models_dir, "example-url-download.md"
    downloader.config.models_dir, "example-url-download.md"
    ),
    ),
    callback=progress_callback,
    callback=progress_callback,
    auto_register=True,
    auto_register=True,
    description="Example URL download (auto-registered)",
    description="Example URL download (auto-registered)",
    )
    )


    # Wait for the download to complete
    # Wait for the download to complete
    while task.is_running():
    while task.is_running():
    time.sleep(0.1)
    time.sleep(0.1)


    if task.progress.status == "completed":
    if task.progress.status == "completed":
    print(f"\nDownload completed: {task.destination}")
    print(f"\nDownload completed: {task.destination}")


    # Verify the model is registered (should happen automatically)
    # Verify the model is registered (should happen automatically)
    all_models = manager.get_all_models()
    all_models = manager.get_all_models()
    print(f"\nAll registered models after URL download ({len(all_models)}):")
    print(f"\nAll registered models after URL download ({len(all_models)}):")
    for model in all_models:
    for model in all_models:
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")
    print(f"- {model.name} (Type: {model.type}, Format: {model.format})")
    else:
    else:
    print(f"\nDownload failed: {task.progress.error}")
    print(f"\nDownload failed: {task.progress.error}")


except Exception as e:
except Exception as e:
    print(f"Error: {e}")
    print(f"Error: {e}")


    # Clean up completed tasks
    # Clean up completed tasks
    removed_tasks = downloader.clean_completed_tasks()
    removed_tasks = downloader.clean_completed_tasks()
    print(f"\nRemoved {removed_tasks} completed tasks")
    print(f"\nRemoved {removed_tasks} completed tasks")


    print("\nExample completed successfully!")
    print("\nExample completed successfully!")




    if __name__ == "__main__":
    if __name__ == "__main__":
    main()
    main()

