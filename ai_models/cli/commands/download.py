"""
"""
Download command for the command-line interface.
Download command for the command-line interface.


This module provides a command for downloading models.
This module provides a command for downloading models.
"""
"""




import argparse
import argparse
import json
import json
import logging
import logging
import os
import os


from ...core import ModelDownloader
from ...core import ModelDownloader
from ..base import BaseCommand
from ..base import BaseCommand


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




class DownloadCommand(BaseCommand):
    class DownloadCommand(BaseCommand):
    """
    """
    Command for downloading models.
    Command for downloading models.
    """
    """


    description = "Download a model"
    description = "Download a model"


    @classmethod
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
    """
    """
    Add command-specific arguments to the parser.
    Add command-specific arguments to the parser.


    Args:
    Args:
    parser: Argument parser
    parser: Argument parser
    """
    """
    parser.add_argument(
    parser.add_argument(
    "--model-id", type=str, required=True, help="Model ID or URL to download"
    "--model-id", type=str, required=True, help="Model ID or URL to download"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--output-dir",
    "--output-dir",
    type=str,
    type=str,
    default="models",
    default="models",
    help="Directory to save the model",
    help="Directory to save the model",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--revision", type=str, default="main", help="Model revision to download"
    "--revision", type=str, default="main", help="Model revision to download"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--force",
    "--force",
    action="store_true",
    action="store_true",
    help="Force download even if the model already exists",
    help="Force download even if the model already exists",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--cache-dir", type=str, help="Cache directory for downloaded models"
    "--cache-dir", type=str, help="Cache directory for downloaded models"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--auth-token", type=str, help="Authentication token for private models"
    "--auth-token", type=str, help="Authentication token for private models"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--use-auth-token",
    "--use-auth-token",
    action="store_true",
    action="store_true",
    help="Use the Hugging Face token from the environment",
    help="Use the Hugging Face token from the environment",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--local-files-only",
    "--local-files-only",
    action="store_true",
    action="store_true",
    help="Use only local files (no downloads)",
    help="Use only local files (no downloads)",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--resume-download", action="store_true", help="Resume incomplete downloads"
    "--resume-download", action="store_true", help="Resume incomplete downloads"
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--proxies",
    "--proxies",
    type=str,
    type=str,
    help="Dictionary of proxies for HTTP/HTTPS connections",
    help="Dictionary of proxies for HTTP/HTTPS connections",
    )
    )
    parser.add_argument(
    parser.add_argument(
    "--max-workers",
    "--max-workers",
    type=int,
    type=int,
    default=8,
    default=8,
    help="Maximum number of workers for parallel downloads",
    help="Maximum number of workers for parallel downloads",
    )
    )


    def run(self) -> int:
    def run(self) -> int:
    """
    """
    Run the command.
    Run the command.


    Returns:
    Returns:
    Exit code
    Exit code
    """
    """
    # Validate arguments
    # Validate arguments
    if not self._validate_args(["model_id", "output_dir"]):
    if not self._validate_args(["model_id", "output_dir"]):
    return 1
    return 1


    try:
    try:
    # Import required modules
    # Import required modules
    # Create output directory if it doesn't exist
    # Create output directory if it doesn't exist
    os.makedirs(self.args.output_dir, exist_ok=True)
    os.makedirs(self.args.output_dir, exist_ok=True)


    # Create downloader
    # Create downloader
    downloader = ModelDownloader(
    downloader = ModelDownloader(
    cache_dir=self.args.cache_dir, max_workers=self.args.max_workers
    cache_dir=self.args.cache_dir, max_workers=self.args.max_workers
    )
    )


    # Prepare download parameters
    # Prepare download parameters
    params = {
    params = {
    "revision": self.args.revision,
    "revision": self.args.revision,
    "force": self.args.force,
    "force": self.args.force,
    "local_files_only": self.args.local_files_only,
    "local_files_only": self.args.local_files_only,
    "resume_download": self.args.resume_download,
    "resume_download": self.args.resume_download,
    }
    }


    # Add authentication token if provided
    # Add authentication token if provided
    if self.args.auth_token:
    if self.args.auth_token:
    params["auth_token"] = self.args.auth_token
    params["auth_token"] = self.args.auth_token
    elif self.args.use_auth_token:
    elif self.args.use_auth_token:
    params["use_auth_token"] = True
    params["use_auth_token"] = True


    # Add proxies if provided
    # Add proxies if provided
    if self.args.proxies:
    if self.args.proxies:




    params["proxies"] = json.loads(self.args.proxies)
    params["proxies"] = json.loads(self.args.proxies)


    # Download model
    # Download model
    logger.info(
    logger.info(
    f"Downloading model {self.args.model_id} to {self.args.output_dir}"
    f"Downloading model {self.args.model_id} to {self.args.output_dir}"
    )
    )


    # Create download task
    # Create download task
    task = downloader.download(
    task = downloader.download(
    model_id=self.args.model_id, output_dir=self.args.output_dir, **params
    model_id=self.args.model_id, output_dir=self.args.output_dir, **params
    )
    )


    # Wait for download to complete
    # Wait for download to complete
    task.wait()
    task.wait()


    # Check if download was successful
    # Check if download was successful
    if task.is_completed():
    if task.is_completed():
    logger.info(f"Model downloaded successfully to {task.output_dir}")
    logger.info(f"Model downloaded successfully to {task.output_dir}")
    return 0
    return 0
    else:
    else:
    logger.error(f"Failed to download model: {task.error}")
    logger.error(f"Failed to download model: {task.error}")
    return 1
    return 1


except Exception as e:
except Exception as e:
    logger.error(f"Error downloading model: {e}", exc_info=True)
    logger.error(f"Error downloading model: {e}", exc_info=True)
    return 1
    return 1