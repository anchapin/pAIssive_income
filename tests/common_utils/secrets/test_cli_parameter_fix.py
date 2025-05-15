"""Tests for the parameter name fix in common_utils/secrets/cli.py."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

from common_utils.secrets.cli import handle_audit
from common_utils.secrets.audit import SecretsAuditor


class TestCliParameterFix(unittest.TestCase):
    """Test cases for the parameter name fix in cli.py."""

    @patch('common_utils.secrets.cli.SecretsAuditor')
    def test_audit_uses_correct_parameter_name(self, mock_auditor_class):
        """Test that handle_audit uses the correct parameter name 'format' instead of 'output_format'."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor
        
        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = True
        mock_args.exclude = None
        mock_args.backend = "env"
        
        # Call handle_audit
        handle_audit(mock_args)
        
        # Verify that audit was called with the correct parameter name 'format'
        mock_auditor.audit.assert_called_once()
        call_kwargs = mock_auditor.audit.call_args[1]
        
        # Check that 'format' is in the kwargs and 'output_format' is not
        assert 'format' in call_kwargs
        assert 'output_format' not in call_kwargs
        
        # Check that the format value is correct
        assert call_kwargs['format'] == 'json'

    @patch('common_utils.secrets.cli.SecretsAuditor')
    def test_audit_with_text_format(self, mock_auditor_class):
        """Test that handle_audit uses 'text' format when json is False."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor
        
        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = False
        mock_args.exclude = None
        mock_args.backend = "env"
        
        # Call handle_audit
        handle_audit(mock_args)
        
        # Verify that audit was called with the correct parameter name 'format'
        mock_auditor.audit.assert_called_once()
        call_kwargs = mock_auditor.audit.call_args[1]
        
        # Check that 'format' is in the kwargs and has the correct value
        assert 'format' in call_kwargs
        assert call_kwargs['format'] == 'text'

    @patch('common_utils.secrets.cli.SecretsAuditor')
    def test_audit_with_output_file(self, mock_auditor_class):
        """Test that handle_audit correctly passes the output_file parameter."""
        # Create a mock auditor instance
        mock_auditor = MagicMock()
        mock_auditor_class.return_value = mock_auditor
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            
            try:
                # Create mock args
                mock_args = MagicMock()
                mock_args.directory = "test_dir"
                mock_args.output = temp_path
                mock_args.json = True
                mock_args.exclude = None
                mock_args.backend = "env"
                
                # Call handle_audit
                handle_audit(mock_args)
                
                # Verify that audit was called with the correct parameters
                mock_auditor.audit.assert_called_once()
                call_kwargs = mock_auditor.audit.call_args[1]
                
                # Check that both 'format' and 'output_file' are in the kwargs
                assert 'format' in call_kwargs
                assert 'output_file' in call_kwargs
                
                # Check that the values are correct
                assert call_kwargs['format'] == 'json'
                assert call_kwargs['output_file'] == temp_path
                
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    @patch('common_utils.secrets.cli.SecretsAuditor')
    @patch('common_utils.secrets.cli.logger')
    def test_audit_exception_handling(self, mock_logger, mock_auditor_class):
        """Test that handle_audit properly handles exceptions."""
        # Create a mock auditor instance that raises an exception
        mock_auditor = MagicMock()
        mock_auditor.audit.side_effect = Exception("Test exception")
        mock_auditor_class.return_value = mock_auditor
        
        # Create mock args
        mock_args = MagicMock()
        mock_args.directory = "test_dir"
        mock_args.output = None
        mock_args.json = True
        mock_args.exclude = None
        mock_args.backend = "env"
        
        # Call handle_audit and expect it to handle the exception
        with pytest.raises(SystemExit):
            handle_audit(mock_args)
        
        # Verify that the exception was logged
        mock_logger.exception.assert_called()


if __name__ == "__main__":
    unittest.main()
