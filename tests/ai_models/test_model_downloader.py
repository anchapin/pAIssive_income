"""
Tests for the ModelDownloader class.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import os
import tempfile
import shutil

from ai_models.model_downloader import ModelDownloader, DownloadTask, DownloadProgress


def test_download_progress_init():
    """Test DownloadProgress initialization."""
    progress = DownloadProgress(
        total_size=1000,
        downloaded_size=500,
        percentage=50.0,
        speed=1024,
        eta=30
    )
    
    # Check that the progress has the expected attributes
    assert progress.total_size == 1000
    assert progress.downloaded_size == 500
    assert progress.percentage == 50.0
    assert progress.speed == 1024
    assert progress.eta == 30


def test_download_progress_to_dict():
    """Test to_dict method of DownloadProgress."""
    progress = DownloadProgress(
        total_size=1000,
        downloaded_size=500,
        percentage=50.0,
        speed=1024,
        eta=30
    )
    
    # Convert to dictionary
    progress_dict = progress.to_dict()
    
    # Check that the dictionary has the expected keys
    assert "total_size" in progress_dict
    assert "downloaded_size" in progress_dict
    assert "percentage" in progress_dict
    assert "speed" in progress_dict
    assert "eta" in progress_dict
    
    # Check that the values are correct
    assert progress_dict["total_size"] == 1000
    assert progress_dict["downloaded_size"] == 500
    assert progress_dict["percentage"] == 50.0
    assert progress_dict["speed"] == 1024
    assert progress_dict["eta"] == 30


def test_download_task_init():
    """Test DownloadTask initialization."""
    task = DownloadTask(
        model_id="test-model",
        source="huggingface",
        url="https://huggingface.co/test-model",
        destination="/path/to/model",
        status="pending"
    )
    
    # Check that the task has the expected attributes
    assert task.model_id == "test-model"
    assert task.source == "huggingface"
    assert task.url == "https://huggingface.co/test-model"
    assert task.destination == "/path/to/model"
    assert task.status == "pending"
    assert task.progress is None
    assert task.error is None
    assert isinstance(task.created_at, str)
    assert isinstance(task.updated_at, str)


def test_download_task_to_dict():
    """Test to_dict method of DownloadTask."""
    task = DownloadTask(
        model_id="test-model",
        source="huggingface",
        url="https://huggingface.co/test-model",
        destination="/path/to/model",
        status="pending"
    )
    
    # Convert to dictionary
    task_dict = task.to_dict()
    
    # Check that the dictionary has the expected keys
    assert "model_id" in task_dict
    assert "source" in task_dict
    assert "url" in task_dict
    assert "destination" in task_dict
    assert "status" in task_dict
    assert "progress" in task_dict
    assert "error" in task_dict
    assert "created_at" in task_dict
    assert "updated_at" in task_dict
    
    # Check that the values are correct
    assert task_dict["model_id"] == "test-model"
    assert task_dict["source"] == "huggingface"
    assert task_dict["url"] == "https://huggingface.co/test-model"
    assert task_dict["destination"] == "/path/to/model"
    assert task_dict["status"] == "pending"
    assert task_dict["progress"] is None
    assert task_dict["error"] is None


def test_download_task_update_progress():
    """Test update_progress method of DownloadTask."""
    task = DownloadTask(
        model_id="test-model",
        source="huggingface",
        url="https://huggingface.co/test-model",
        destination="/path/to/model",
        status="downloading"
    )
    
    # Update progress
    progress = DownloadProgress(
        total_size=1000,
        downloaded_size=500,
        percentage=50.0,
        speed=1024,
        eta=30
    )
    
    task.update_progress(progress)
    
    # Check that the progress was updated
    assert task.progress == progress
    assert task.status == "downloading"


def test_download_task_complete():
    """Test complete method of DownloadTask."""
    task = DownloadTask(
        model_id="test-model",
        source="huggingface",
        url="https://huggingface.co/test-model",
        destination="/path/to/model",
        status="downloading"
    )
    
    # Complete the task
    task.complete()
    
    # Check that the status was updated
    assert task.status == "completed"


def test_download_task_fail():
    """Test fail method of DownloadTask."""
    task = DownloadTask(
        model_id="test-model",
        source="huggingface",
        url="https://huggingface.co/test-model",
        destination="/path/to/model",
        status="downloading"
    )
    
    # Fail the task
    task.fail("Download failed")
    
    # Check that the status and error were updated
    assert task.status == "failed"
    assert task.error == "Download failed"


@pytest.fixture
def temp_models_dir():
    """Create a temporary directory for models."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@patch('ai_models.model_downloader.requests.get')
def test_model_downloader_download_from_url(mock_get, temp_models_dir):
    """Test download_from_url method of ModelDownloader."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2", b"chunk3"]
    mock_response.headers = {"Content-Length": "15"}  # 3 chunks of 5 bytes each
    mock_get.return_value = mock_response
    
    # Create a downloader
    downloader = ModelDownloader(models_dir=temp_models_dir)
    
    # Create a callback to track progress
    progress_updates = []
    def progress_callback(progress):
        progress_updates.append(progress)
    
    # Download from URL
    destination = os.path.join(temp_models_dir, "test-model.bin")
    result = downloader.download_from_url(
        url="https://example.com/test-model.bin",
        destination=destination,
        progress_callback=progress_callback
    )
    
    # Check that the file was downloaded
    assert result is True
    assert os.path.exists(destination)
    
    # Check that progress was reported
    assert len(progress_updates) > 0
    assert isinstance(progress_updates[0], DownloadProgress)
    
    # Check that the mock was called correctly
    mock_get.assert_called_once_with(
        "https://example.com/test-model.bin",
        stream=True,
        timeout=30
    )
    mock_response.iter_content.assert_called_once_with(chunk_size=1024)


@patch('ai_models.model_downloader.ModelDownloader.download_from_url')
def test_model_downloader_download_model(mock_download_from_url, temp_models_dir):
    """Test download_model method of ModelDownloader."""
    # Mock the download_from_url method
    mock_download_from_url.return_value = True
    
    # Create a downloader
    downloader = ModelDownloader(models_dir=temp_models_dir)
    
    # Create a callback to track progress
    progress_updates = []
    def progress_callback(progress):
        progress_updates.append(progress)
    
    # Download a model
    task = downloader.download_model(
        model_id="test-model",
        source="direct",
        url="https://example.com/test-model.bin",
        progress_callback=progress_callback
    )
    
    # Check that a task was returned
    assert isinstance(task, DownloadTask)
    assert task.model_id == "test-model"
    assert task.source == "direct"
    assert task.url == "https://example.com/test-model.bin"
    assert task.destination.startswith(temp_models_dir)
    assert task.status == "completed"
    
    # Check that the mock was called correctly
    mock_download_from_url.assert_called_once_with(
        url="https://example.com/test-model.bin",
        destination=task.destination,
        progress_callback=progress_callback
    )


@patch('ai_models.model_downloader.ModelDownloader.download_from_url')
def test_model_downloader_download_model_failure(mock_download_from_url, temp_models_dir):
    """Test download_model method of ModelDownloader with a failure."""
    # Mock the download_from_url method to fail
    mock_download_from_url.side_effect = Exception("Download failed")
    
    # Create a downloader
    downloader = ModelDownloader(models_dir=temp_models_dir)
    
    # Download a model
    task = downloader.download_model(
        model_id="test-model",
        source="direct",
        url="https://example.com/test-model.bin"
    )
    
    # Check that a task was returned with failure status
    assert isinstance(task, DownloadTask)
    assert task.model_id == "test-model"
    assert task.status == "failed"
    assert task.error == "Download failed"


@patch('ai_models.model_downloader.ModelDownloader.download_from_url')
def test_model_downloader_get_task(mock_download_from_url, temp_models_dir):
    """Test get_task method of ModelDownloader."""
    # Mock the download_from_url method
    mock_download_from_url.return_value = True
    
    # Create a downloader
    downloader = ModelDownloader(models_dir=temp_models_dir)
    
    # Download a model
    task = downloader.download_model(
        model_id="test-model",
        source="direct",
        url="https://example.com/test-model.bin"
    )
    
    # Get the task
    retrieved_task = downloader.get_task(task.id)
    
    # Check that the task was retrieved
    assert retrieved_task == task
    
    # Try to get a non-existent task
    assert downloader.get_task("non-existent-id") is None


@patch('ai_models.model_downloader.ModelDownloader.download_from_url')
def test_model_downloader_get_tasks(mock_download_from_url, temp_models_dir):
    """Test get_tasks method of ModelDownloader."""
    # Mock the download_from_url method
    mock_download_from_url.return_value = True
    
    # Create a downloader
    downloader = ModelDownloader(models_dir=temp_models_dir)
    
    # Download multiple models
    task1 = downloader.download_model(
        model_id="test-model-1",
        source="direct",
        url="https://example.com/test-model-1.bin"
    )
    
    task2 = downloader.download_model(
        model_id="test-model-2",
        source="direct",
        url="https://example.com/test-model-2.bin"
    )
    
    # Get all tasks
    tasks = downloader.get_tasks()
    
    # Check that all tasks were retrieved
    assert len(tasks) == 2
    assert task1 in tasks
    assert task2 in tasks
    
    # Get tasks by status
    completed_tasks = downloader.get_tasks(status="completed")
    assert len(completed_tasks) == 2
    assert task1 in completed_tasks
    assert task2 in completed_tasks
    
    # Get tasks by model ID
    model1_tasks = downloader.get_tasks(model_id="test-model-1")
    assert len(model1_tasks) == 1
    assert task1 in model1_tasks
    assert task2 not in model1_tasks
