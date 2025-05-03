"""
Tests for Celery integration with Flask and Socket.IO.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from celery import states

from flask import Flask
from ui.celery_app import (
    create_celery_app,
    emit_task_event,
    task_failure_handler,
    task_prerun_handler,
    task_sent_handler,
    task_success_handler,
)


@pytest.fixture
def mock_app():
    """Create a mock Flask app with Celery configuration."""
    app = Flask(__name__)
    app.config.update(
        CELERY_BROKER_URL="redis://localhost:6379 / 0",
        CELERY_RESULT_BACKEND="redis://localhost:6379 / 0",
    )
    return app


@pytest.fixture
def mock_celery(mock_app):
    """Create a mock Celery instance."""
    return create_celery_app(mock_app)


@pytest.fixture
def mock_task():
    """Create a mock Celery task."""
    task = MagicMock()
    task.request.id = "test_task_id"
    return task


@pytest.fixture
def mock_headers():
    """Create mock task headers."""
    return {"id": "test_task_id"}


class TestCeleryIntegration:
    """Test Celery integration with Flask and Socket.IO."""

    def test_create_celery_app(self, mock_app):
        """Test Celery app creation and configuration."""
        celery = create_celery_app(mock_app)

        # Check basic configuration
        assert celery.main == mock_app.import_name
        assert celery.conf["broker_url"] == "redis://localhost:6379 / 0"
        assert celery.conf["result_backend"] == "redis://localhost:6379 / 0"

        # Check task configuration
        assert celery.conf["task_serializer"] == "json"
        assert celery.conf["result_serializer"] == "json"
        assert celery.conf["accept_content"] == ["json"]
        assert celery.conf["timezone"] == "UTC"
        assert celery.conf["enable_utc"] is True
        assert celery.conf["task_track_started"] is True

    @patch("ui.celery_app.socketio")
    def test_emit_task_event(self, mock_socketio):
        """Test Socket.IO event emission for tasks."""
        task_id = "test_task_id"
        event_name = "task_progress"
        data = {"status": "RUNNING", "progress": 50, "message": "Processing..."}

        # Test event emission
        emit_task_event(event_name, task_id, data)

        # Verify Socket.IO emit was called correctly
        mock_socketio.emit.assert_called_once_with(
            event_name, {"task_id": task_id, **data}, room=task_id
        )

    @patch("ui.celery_app.emit_task_event")
    def test_task_sent_handler(self, mock_emit, mock_headers):
        """Test task sent event handling."""
        task_sent_handler(headers=mock_headers)

        # Verify event emission
        mock_emit.assert_called_once_with(
            "task_progress",
            "test_task_id",
            {"status": "PENDING", "message": "Task queued", "progress": 0},
        )

    @patch("ui.celery_app.emit_task_event")
    def test_task_prerun_handler(self, mock_emit):
        """Test task pre - run event handling."""
        task_id = "test_task_id"
        task = MagicMock()

        task_prerun_handler(task_id=task_id, task=task)

        # Verify event emission
        mock_emit.assert_called_once_with(
            "task_progress",
            task_id,
            {"status": "STARTED", "message": "Task started", "progress": 0},
        )

    @patch("ui.celery_app.emit_task_event")
    def test_task_success_handler(self, mock_emit, mock_task):
        """Test task success event handling."""
        result = {"key": "value"}

        task_success_handler(sender=mock_task, result=result)

        # Verify event emission
        mock_emit.assert_called_once_with(
            "task_progress",
            "test_task_id",
            {
                "status": "SUCCESS",
                "message": "Task completed successfully",
                "progress": 100,
                "result": result,
            },
        )

    @patch("ui.celery_app.emit_task_event")
    def test_task_failure_handler(self, mock_emit, mock_task):
        """Test task failure event handling."""
        exception = ValueError("Test error")
        traceback = "Test traceback"

        task_failure_handler(sender=mock_task, exception=exception, traceback=traceback)

        # Verify event emission
        mock_emit.assert_called_once_with(
            "error",
            "test_task_id",
            {
                "status": "FAILURE",
                "message": "Task failed: Test error",
                "error": "Test error",
                "traceback": traceback,
            },
        )

    def test_task_context(self, mock_celery):
        """Test task execution with Flask application context."""

        @mock_celery.task
        def test_task():
            from flask import current_app

            return current_app.name

        # Execute task (should maintain app context)
        with mock_celery.app.app_context():
            result = test_task.apply().get()
            assert result == mock_celery.app.name

    @patch("ui.celery_app.socketio")
    def test_task_retry(self, mock_socketio, mock_celery):
        """Test task retry behavior."""
        retry_count = 0

        @mock_celery.task(bind=True, max_retries=3)
        def failing_task(self):
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                self.retry(countdown=0)
            return "Success"

        # Execute task
        result = failing_task.apply()
        assert result.get() == "Success"
        assert retry_count == 3

    @patch("ui.celery_app.socketio")
    def test_task_progress_updates(self, mock_socketio, mock_celery):
        """Test task progress updates via Socket.IO."""

        @mock_celery.task(bind=True)
        def progress_task(self):
            # Simulate progress updates
            self.update_state(state="PROGRESS", meta={"progress": 50, 
                "message": "Halfway done"})
            return "Completed"

        # Execute task
        result = progress_task.apply()
        assert result.get() == "Completed"

        # Verify Socket.IO events
        progress_call = mock_socketio.emit.call_args_list[0]
        assert progress_call[0][0] == "task_progress"
        assert progress_call[0][1]["progress"] == 50

    @patch("ui.celery_app.socketio")
    def test_error_handling(self, mock_socketio, mock_celery):
        """Test error handling in tasks."""

        @mock_celery.task
        def error_task():
            raise ValueError("Test error")

        # Execute task (should fail)
        result = error_task.apply()
        assert result.status == states.FAILURE

        # Verify error event
        error_call = mock_socketio.emit.call_args_list[-1]
        assert error_call[0][0] == "error"
        assert "Test error" in error_call[0][1]["message"]
