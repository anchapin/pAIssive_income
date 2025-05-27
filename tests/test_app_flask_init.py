"""Tests for the app_flask/__init__.py module."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app_flask import create_app, db, migrate


class TestAppFlaskInit(unittest.TestCase):
    """Test cases for the app_flask/__init__.py module."""

    @patch('app_flask.db.init_app')
    @patch('app_flask.migrate.init_app')
    @patch('app_flask.db.create_all')
    @patch('app_flask.models')
    def test_create_app_basic(self, mock_models, mock_create_all, mock_migrate_init, mock_db_init):
        """Test basic app creation without test config."""
        app = create_app()
        
        # Check that the app was created
        self.assertIsNotNone(app)
        
        # Check that the app has the expected name
        self.assertEqual(app.name, 'app_flask')
        
        # Check that the database was initialized
        mock_db_init.assert_called_once_with(app)
        
        # Check that migrations were initialized
        mock_migrate_init.assert_called_once_with(app, db)
        
        # Check that models were imported
        self.assertTrue(mock_models is not None)
        
        # Check that tables were created
        self.assertTrue(mock_create_all.called)

    @patch('app_flask.db.init_app')
    @patch('app_flask.migrate.init_app')
    @patch('app_flask.db.create_all')
    @patch('app_flask.models')
    def test_create_app_with_test_config(self, mock_models, mock_create_all, mock_migrate_init, mock_db_init):
        """Test app creation with test config."""
        test_config = {'TESTING': True, 'DEBUG': True}
        app = create_app(test_config)
        
        # Check that the app was created
        self.assertIsNotNone(app)
        
        # Check that the test config was applied
        self.assertTrue(app.config['TESTING'])
        self.assertTrue(app.config['DEBUG'])
        
        # Check that the database was initialized
        mock_db_init.assert_called_once_with(app)
        
        # Check that migrations were initialized
        mock_migrate_init.assert_called_once_with(app, db)

    @patch('app_flask.db.init_app')
    @patch('app_flask.migrate.init_app')
    @patch('app_flask.db.create_all')
    @patch('app_flask.models')
    @patch('app_flask.user_bp', create=True)
    def test_create_app_with_blueprint(self, mock_user_bp, mock_models, mock_create_all, 
                                      mock_migrate_init, mock_db_init):
        """Test app creation with blueprint registration."""
        # Mock the import of user_bp
        with patch('app_flask.importlib.import_module') as mock_import:
            mock_import.return_value = MagicMock()
            
            app = create_app()
            
            # Check that the app was created
            self.assertIsNotNone(app)
            
            # Check that the blueprint was registered
            self.assertTrue(hasattr(app, 'blueprints'))


if __name__ == "__main__":
    unittest.main()
