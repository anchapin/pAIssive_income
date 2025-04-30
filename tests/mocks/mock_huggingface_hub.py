"""
Mock implementation of Hugging Face Hub API for testing.

This module mocks the huggingface_hub library to allow testing of code that interacts with
the Hugging Face Hub API without making actual API calls.
"""

import os
import shutil
import json
import tempfile
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class MockRepoInfo:
    """Mock repository information."""

    id: str
    sha: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    downloads: int = 0
    likes: int = 0
    private: bool = False
    author: str = ""
    tags: List[str] = None
    pipeline_tag: str = None
    card_data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.card_data is None:
            self.card_data = {}

        # Extract author from repo ID if not provided
        if not self.author and "/" in self.id:
            self.author = self.id.split("/")[0]

        # Set SHA if not provided
        if not self.sha:
            import hashlib

            self.sha = hashlib.sha256(self.id.encode()).hexdigest()


class MockHuggingFaceHub:
    """Mock implementation of Hugging Face Hub API."""

    def __init__(self):
        """Initialize the mock Hugging Face Hub API."""
        self.repos = {}
        self.files = {}
        self.models = {}
        self.datasets = {}
        self.authenticated = False
        self.token = None
        self.temp_dir = tempfile.mkdtemp(prefix="mock_hf_hub_")

    def reset(self):
        """Reset the mock Hugging Face Hub API."""
        self.repos = {}
        self.files = {}
        self.models = {}
        self.datasets = {}
        self.authenticated = False
        self.token = None

        # Clear temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = tempfile.mkdtemp(prefix="mock_hf_hub_")

    def add_repo(self, repo_info: Union[MockRepoInfo, Dict[str, Any]]) -> None:
        """
        Add a repository to the mock Hugging Face Hub.

        Args:
            repo_info: Repository information
        """
        if isinstance(repo_info, dict):
            repo_info = MockRepoInfo(**repo_info)

        self.repos[repo_info.id] = repo_info

        # Automatically add to models or datasets
        if repo_info.pipeline_tag or any(
            tag in repo_info.tags for tag in ["model", "text-generation", "fill-mask"]
        ):
            self.models[repo_info.id] = repo_info
        elif "dataset" in repo_info.tags:
            self.datasets[repo_info.id] = repo_info
        else:
            # Default to model
            self.models[repo_info.id] = repo_info

    def add_file(
        self,
        repo_id: str,
        file_path: str,
        content: Union[bytes, str, Dict[str, Any]],
        file_size: Optional[int] = None,
    ) -> None:
        """
        Add a file to a repository in the mock Hugging Face Hub.

        Args:
            repo_id: Repository ID
            file_path: Path of the file in the repository
            content: Content of the file
            file_size: Size of the file in bytes
        """
        # Ensure repo exists
        if repo_id not in self.repos:
            self.add_repo({"id": repo_id})

        # Convert content to bytes
        if isinstance(content, dict):
            content = json.dumps(content).encode("utf-8")
        elif isinstance(content, str):
            content = content.encode("utf-8")

        # Determine file size if not provided
        if file_size is None:
            file_size = len(content)

        # Store the file
        self.files[f"{repo_id}/{file_path}"] = {
            "content": content,
            "size": file_size,
            "last_modified": datetime.now(),
        }

        # Create the file in the temp directory
        repo_dir = os.path.join(self.temp_dir, repo_id.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)

        file_path_full = os.path.join(repo_dir, file_path)
        os.makedirs(os.path.dirname(file_path_full), exist_ok=True)

        with open(file_path_full, "wb") as f:
            f.write(content)

    def login(self, token: Optional[str] = None) -> None:
        """
        Mock login to Hugging Face Hub.

        Args:
            token: Authentication token

        Raises:
            ValueError: If token is invalid
        """
        if token == "invalid_token":
            raise ValueError("Invalid token")

        self.authenticated = token is not None
        self.token = token

    def hf_hub_download(
        self,
        repo_id: str,
        filename: str,
        revision: str = "main",
        cache_dir: Optional[str] = None,
        force_download: bool = False,
        proxies: Optional[Dict[str, str]] = None,
        etag_timeout: float = 10,
        resume_download: bool = False,
        use_auth_token: Optional[Union[bool, str]] = None,
        local_files_only: bool = False,
        legacy_cache_layout: bool = False,
        local_dir: Optional[str] = None,
        local_dir_use_symlinks: bool = True,
        **kwargs,
    ) -> str:
        """
        Mock downloading a file from Hugging Face Hub.

        Args:
            repo_id: Repository ID
            filename: Name of the file to download
            revision: Git revision
            cache_dir: Directory to cache files
            force_download: Whether to force download even if file exists
            proxies: Proxies to use
            etag_timeout: Timeout for ETag request
            resume_download: Whether to resume download if exists
            use_auth_token: Authentication token
            local_files_only: Whether to use local files only
            legacy_cache_layout: Whether to use legacy cache layout
            local_dir: Directory to download files to
            local_dir_use_symlinks: Whether to use symlinks
            **kwargs: Additional arguments

        Returns:
            Path to the downloaded file

        Raises:
            ValueError: If repository or file not found
            ValueError: If authentication required
        """
        # Check if repo exists
        if repo_id not in self.repos:
            raise ValueError(f"Repository {repo_id} not found")

        # Check if file exists
        file_key = f"{repo_id}/{filename}"
        if file_key not in self.files:
            raise ValueError(f"File {filename} not found in repository {repo_id}")

        # Check if authentication required
        if self.repos[repo_id].private and not (self.authenticated or use_auth_token):
            raise ValueError(f"Authentication required for repository {repo_id}")

        # Determine destination path
        dest_dir = local_dir or cache_dir or self.temp_dir
        os.makedirs(dest_dir, exist_ok=True)

        if local_dir:
            dest_path = os.path.join(dest_dir, filename)
        else:
            # Simulate cache structure
            repo_dir = repo_id.replace("/", "--")
            dest_path = os.path.join(dest_dir, repo_dir, revision, filename)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy the file
        file_info = self.files[file_key]

        with open(dest_path, "wb") as f:
            f.write(file_info["content"])

        # Simulate progress callback
        progress_callback = kwargs.get("progress_callback")
        if progress_callback:
            progress_callback(file_info["size"], file_info["size"])

        return dest_path

    def snapshot_download(
        self,
        repo_id: str,
        revision: str = "main",
        cache_dir: Optional[str] = None,
        force_download: bool = False,
        proxies: Optional[Dict[str, str]] = None,
        etag_timeout: float = 10,
        resume_download: bool = False,
        use_auth_token: Optional[Union[bool, str]] = None,
        local_files_only: bool = False,
        allow_patterns: Optional[Union[List[str], str]] = None,
        ignore_patterns: Optional[Union[List[str], str]] = None,
        local_dir: Optional[str] = None,
        local_dir_use_symlinks: bool = True,
        **kwargs,
    ) -> str:
        """
        Mock downloading a snapshot of a repository from Hugging Face Hub.

        Args:
            repo_id: Repository ID
            revision: Git revision
            cache_dir: Directory to cache files
            force_download: Whether to force download even if file exists
            proxies: Proxies to use
            etag_timeout: Timeout for ETag request
            resume_download: Whether to resume download if exists
            use_auth_token: Authentication token
            local_files_only: Whether to use local files only
            allow_patterns: Patterns to allow
            ignore_patterns: Patterns to ignore
            local_dir: Directory to download files to
            local_dir_use_symlinks: Whether to use symlinks
            **kwargs: Additional arguments

        Returns:
            Path to the downloaded repository

        Raises:
            ValueError: If repository not found
            ValueError: If authentication required
        """
        # Check if repo exists
        if repo_id not in self.repos:
            raise ValueError(f"Repository {repo_id} not found")

        # Check if authentication required
        if self.repos[repo_id].private and not (self.authenticated or use_auth_token):
            raise ValueError(f"Authentication required for repository {repo_id}")

        # Determine destination path
        dest_dir = local_dir or os.path.join(
            cache_dir or self.temp_dir, repo_id.replace("/", "--"), revision
        )
        os.makedirs(dest_dir, exist_ok=True)

        # Copy all files
        total_size = 0
        downloaded_size = 0

        # Calculate total size first
        for file_key, file_info in self.files.items():
            if file_key.startswith(repo_id + "/"):
                file_path = file_key[len(repo_id) + 1 :]

                # Check patterns
                if allow_patterns and not any(
                    self._match_pattern(file_path, pattern)
                    for pattern in allow_patterns
                ):
                    continue
                if ignore_patterns and any(
                    self._match_pattern(file_path, pattern)
                    for pattern in ignore_patterns
                ):
                    continue

                total_size += file_info["size"]

        # Now copy files
        for file_key, file_info in self.files.items():
            if file_key.startswith(repo_id + "/"):
                file_path = file_key[len(repo_id) + 1 :]

                # Check patterns
                if allow_patterns and not any(
                    self._match_pattern(file_path, pattern)
                    for pattern in allow_patterns
                ):
                    continue
                if ignore_patterns and any(
                    self._match_pattern(file_path, pattern)
                    for pattern in ignore_patterns
                ):
                    continue

                # Create destination file
                dest_path = os.path.join(dest_dir, file_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                with open(dest_path, "wb") as f:
                    f.write(file_info["content"])

                downloaded_size += file_info["size"]

                # Simulate progress callback
                progress_callback = kwargs.get("progress_callback")
                if progress_callback:
                    progress_callback(downloaded_size, total_size)

        return dest_dir

    def list_models(
        self,
        filter: str = None,
        author: str = None,
        search: str = None,
        tags: Union[str, List[str]] = None,
        language: str = None,
        library: str = None,
        task: str = None,
        limit: int = 10000,
        full: bool = True,
        **kwargs,
    ) -> List[MockRepoInfo]:
        """
        Mock listing models from Hugging Face Hub.

        Args:
            filter: Filter string
            author: Filter by author
            search: Search query
            tags: Filter by tags
            language: Filter by language
            library: Filter by library
            task: Filter by task
            limit: Maximum number of models to return
            full: Whether to return full model info
            **kwargs: Additional arguments

        Returns:
            List of model information
        """
        results = []

        for model_id, model_info in self.models.items():
            # Apply filters
            if author and (not model_info.author.lower() == author.lower()):
                continue

            if search:
                search_lower = search.lower()
                # More lenient search that checks if search term is in any part of the model ID
                if not (
                    search_lower in model_id.lower()
                    or search_lower in model_info.author.lower()
                    or any(search_lower in tag.lower() for tag in model_info.tags)
                ):
                    continue

            if tags:
                if isinstance(tags, str):
                    tags = [tags]
                if not all(tag in model_info.tags for tag in tags):
                    continue

            if task:
                if model_info.pipeline_tag != task:
                    continue

            results.append(model_info)

            if len(results) >= limit:
                break

        return results

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern.

        Args:
            path: Path to check
            pattern: Pattern to match against

        Returns:
            True if the path matches the pattern, False otherwise
        """
        import fnmatch

        return fnmatch.fnmatch(path, pattern)


class HfHubHTTPError(Exception):
    """Mock HTTP error from Hugging Face Hub."""

    def __init__(self, message: str, response=None):
        """Initialize the error."""
        self.message = message
        self.response = response or MockResponse()
        super().__init__(message)


class MockResponse:
    """Mock HTTP response for Hugging Face Hub errors."""

    def __init__(self, status_code: int = 404, json: Dict[str, Any] = None):
        """Initialize the response."""
        self.status_code = status_code
        self._json = json or {"error": "Not found"}

    def json(self) -> Dict[str, Any]:
        """Return the JSON content of the response."""
        return self._json


# Create a mock Hugging Face Hub
mock_huggingface_hub = MockHuggingFaceHub()


# Example usage
if __name__ == "__main__":
    # Add a repository
    mock_huggingface_hub.add_repo(
        {
            "id": "user/model",
            "downloads": 1000,
            "likes": 50,
            "tags": ["text-generation", "gpt"],
            "pipeline_tag": "text-generation",
        }
    )

    # Add a file
    mock_huggingface_hub.add_file(
        repo_id="user/model",
        file_path="config.json",
        content=json.dumps({"model_type": "gpt", "vocab_size": 50257}),
    )

    # Download a file
    try:
        file_path = mock_huggingface_hub.hf_hub_download(
            repo_id="user/model", filename="config.json"
        )
        print(f"Downloaded file to {file_path}")

        # Read the file
        with open(file_path, "r") as f:
            content = f.read()
        print(f"File content: {content}")

    except ValueError as e:
        print(f"Error: {e}")
