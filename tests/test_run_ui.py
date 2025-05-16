"""Tests for the run_ui module."""

import os
import unittest
from unittest.mock import patch, MagicMock

import run_ui


class TestRunUI(unittest.TestCase):
    """Test cases for the run_ui module."""

    @patch("run_ui.create_app")
    def test_app_creation(self, mock_create_app):
        """Test that the Flask app is created correctly."""
        # Setup mock
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        # Import the module again to trigger app creation
        import importlib
        importlib.reload(run_ui)

        # Verify create_app was called
        mock_create_app.assert_called_once()

    @patch("run_ui.create_app")
    def test_app_creation_error(self, mock_create_app):
        """Test error handling during app creation."""
        # Setup mock to raise an exception
        mock_create_app.side_effect = Exception("Test error")

        # Test with development environment
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            with self.assertRaises(Exception):
                importlib.reload(run_ui)

        # Test with production environment
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(Exception):
                importlib.reload(run_ui)

    @patch("run_ui.app")
    @patch("run_ui.db")
    def test_health_check_success(self, mock_db, mock_app):
        """Test health check endpoint with successful database connection."""
        # Setup mocks
        mock_session = MagicMock()
        mock_db.session = mock_session
        
        # Import the module to get the health_check function
        import importlib
        importlib.reload(run_ui)
        
        # Call the health check function
        response, status_code = run_ui.health_check()
        
        # Verify response
        self.assertEqual(status_code, 200)
        self.assertEqual(response.json["status"], "healthy")
        self.assertEqual(response.json["components"]["app"], "running")
        self.assertEqual(response.json["components"]["database"], "connected")

    @patch("run_ui.app")
    @patch("run_ui.db")
    def test_health_check_db_error(self, mock_db, mock_app):
        """Test health check endpoint with database connection error."""
        # Setup mocks
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("DB Error")
        mock_db.session = mock_session
        
        # Test with development environment
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            # Import the module to get the health_check function
            import importlib
            importlib.reload(run_ui)
            
            # Call the health check function
            response, status_code = run_ui.health_check()
            
            # Verify response
            self.assertEqual(status_code, 200)
            self.assertEqual(response.json["status"], "healthy")
            self.assertEqual(response.json["components"]["app"], "running")
            self.assertEqual(response.json["components"]["database"], "error")

        # Test with production environment
        with patch.dict(os.environ, {}, clear=True):
            # Import the module to get the health_check function
            importlib.reload(run_ui)
            
            # Call the health check function
            response, status_code = run_ui.health_check()
            
            # Verify response
            self.assertEqual(status_code, 200)
            self.assertEqual(response.json["status"], "healthy")
            self.assertEqual(response.json["components"]["app"], "running")
            self.assertEqual(response.json["components"]["database"], "error")


if __name__ == "__main__":
    unittest.main()
