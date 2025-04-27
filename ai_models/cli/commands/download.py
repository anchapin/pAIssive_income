"""
Download command for the command-line interface.

This module provides a command for downloading models.
"""

import os
import argparse
import logging
from typing import Dict, Any, Optional, List

from ..base import BaseCommand

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DownloadCommand(BaseCommand):
    """
    Command for downloading models.
    """
    
    description = "Download a model"
    
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Add command-specific arguments to the parser.
        
        Args:
            parser: Argument parser
        """
        parser.add_argument(
            "--model-id",
            type=str,
            required=True,
            help="Model ID or URL to download"
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default="models",
            help="Directory to save the model"
        )
        parser.add_argument(
            "--revision",
            type=str,
            default="main",
            help="Model revision to download"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force download even if the model already exists"
        )
        parser.add_argument(
            "--cache-dir",
            type=str,
            help="Cache directory for downloaded models"
        )
        parser.add_argument(
            "--auth-token",
            type=str,
            help="Authentication token for private models"
        )
        parser.add_argument(
            "--use-auth-token",
            action="store_true",
            help="Use the Hugging Face token from the environment"
        )
        parser.add_argument(
            "--local-files-only",
            action="store_true",
            help="Use only local files (no downloads)"
        )
        parser.add_argument(
            "--resume-download",
            action="store_true",
            help="Resume incomplete downloads"
        )
        parser.add_argument(
            "--proxies",
            type=str,
            help="Dictionary of proxies for HTTP/HTTPS connections"
        )
        parser.add_argument(
            "--max-workers",
            type=int,
            default=8,
            help="Maximum number of workers for parallel downloads"
        )
    
    def run(self) -> int:
        """
        Run the command.
        
        Returns:
            Exit code
        """
        # Validate arguments
        if not self._validate_args(["model_id", "output_dir"]):
            return 1
        
        try:
            # Import required modules
            from ...core import ModelDownloader
            
            # Create output directory if it doesn't exist
            os.makedirs(self.args.output_dir, exist_ok=True)
            
            # Create downloader
            downloader = ModelDownloader(
                cache_dir=self.args.cache_dir,
                max_workers=self.args.max_workers
            )
            
            # Prepare download parameters
            params = {
                "revision": self.args.revision,
                "force": self.args.force,
                "local_files_only": self.args.local_files_only,
                "resume_download": self.args.resume_download
            }
            
            # Add authentication token if provided
            if self.args.auth_token:
                params["auth_token"] = self.args.auth_token
            elif self.args.use_auth_token:
                params["use_auth_token"] = True
            
            # Add proxies if provided
            if self.args.proxies:
                import json
                params["proxies"] = json.loads(self.args.proxies)
            
            # Download model
            logger.info(f"Downloading model {self.args.model_id} to {self.args.output_dir}")
            
            # Create download task
            task = downloader.download(
                model_id=self.args.model_id,
                output_dir=self.args.output_dir,
                **params
            )
            
            # Wait for download to complete
            task.wait()
            
            # Check if download was successful
            if task.is_completed():
                logger.info(f"Model downloaded successfully to {task.output_dir}")
                return 0
            else:
                logger.error(f"Failed to download model: {task.error}")
                return 1
        
        except Exception as e:
            logger.error(f"Error downloading model: {e}", exc_info=True)
            return 1
