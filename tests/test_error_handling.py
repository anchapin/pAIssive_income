"""
Tests for error handling functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from api.errors import (
    ErrorDetail,
    ErrorResponse,
    HTTPStatus,
    create_error_response,
    get_status_code_for_exception,
)
from errors import (
    BaseError,
    ConfigurationError,
    MarketingError,
    ModelError,
    MonetizationError,
    NicheAnalysisError,
    UIError,
    ValidationError,
)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""

    def test_base_error(self):
        """Test base error functionality."""
        # Test basic error creation
        error = BaseError(
            message="Test error",
            code="test_error",
            details={"key": "value"},
            http_status=400,
        )

        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, "test_error")
        self.assertEqual(error.details["key"], "value")
        self.assertEqual(error.http_status, 400)

        # Test error serialization
        error_dict = error.to_dict()
        self.assertEqual(error_dict["message"], "Test error")
        self.assertEqual(error_dict["code"], "test_error")
        self.assertEqual(error_dict["details"]["key"], "value")

        # Test error with original exception
        original_exc = ValueError("Original error")
        error = BaseError(message="Wrapper error", original_exception=original_exc)
        self.assertEqual(error.details["original_error_type"], "ValueError")

    def test_validation_error(self):
        """Test validation error handling."""
        # Test validation error with field
        error = ValidationError(
            message="Invalid input",
            field="username",
            validation_errors=[{"field": "username", "error": "Field is required"}],
        )

        self.assertEqual(error.http_status, 400)
        self.assertEqual(error.code, "validation_error")
        self.assertEqual(error.details["field"], "username")
        self.assertTrue("validation_errors" in error.details)

    def test_error_response_format(self):
        """Test error response formatting."""
        # Create a test request mock
        request = MagicMock()
        request.url = "/test/endpoint"

        # Test basic error response
        exc = ValueError("Test error")
        response = create_error_response(exc, request)

        self.assertEqual(response.message, "Test error")
        self.assertEqual(response.code, "ValueError")
        self.assertEqual(response.path, "/test/endpoint")
        self.assertTrue(response.timestamp)

        # Test error response with details
        error = ValidationError(
            message="Validation failed",
            field="email",
            validation_errors=[{"field": "email", "error": "Invalid email format"}],
        )
        response = create_error_response(error, request)

        self.assertEqual(response.message, "Validation failed")
        self.assertEqual(response.code, "validation_error")
        self.assertTrue(len(response.details) > 0)

    def test_http_status_mapping(self):
        """Test HTTP status code mapping for exceptions."""
        # Test standard exceptions
        self.assertEqual(
            get_status_code_for_exception(ValueError()), HTTPStatus.BAD_REQUEST
        )
        self.assertEqual(
            get_status_code_for_exception(FileNotFoundError()), HTTPStatus.NOT_FOUND
        )
        self.assertEqual(
            get_status_code_for_exception(PermissionError()), HTTPStatus.FORBIDDEN
        )
        self.assertEqual(
            get_status_code_for_exception(NotImplementedError()),
            HTTPStatus.NOT_IMPLEMENTED,
        )

        # Test custom exceptions
        validation_error = ValidationError("Invalid input")
        self.assertEqual(
            get_status_code_for_exception(validation_error), HTTPStatus.BAD_REQUEST
        )

        config_error = ConfigurationError("Config error")
        self.assertEqual(
            get_status_code_for_exception(config_error),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def test_error_inheritance(self):
        """Test error class inheritance and specialization."""
        # Test model errors
        model_error = ModelError("Model failed", model_id="model123")
        self.assertEqual(model_error.details["model_id"], "model123")

        # Test monetization errors
        monetization_error = MonetizationError("Payment failed")
        self.assertEqual(monetization_error.code, "monetization_error")

        # Test niche analysis errors
        niche_error = NicheAnalysisError("Analysis failed")
        self.assertEqual(niche_error.code, "niche_analysis_error")

        # Test marketing errors
        marketing_error = MarketingError("Campaign failed")
        self.assertEqual(marketing_error.code, "marketing_error")

        # Test UI errors
        ui_error = UIError("UI error")
        self.assertEqual(ui_error.code, "ui_error")

    def test_error_detail_formatting(self):
        """Test error detail formatting."""
        detail = ErrorDetail(
            message="Field is required",
            code="missing_field",
            field="username",
            params={"min_length": 3},
        )

        detail_dict = detail.to_dict()
        self.assertEqual(detail_dict["message"], "Field is required")
        self.assertEqual(detail_dict["code"], "missing_field")
        self.assertEqual(detail_dict["field"], "username")
        self.assertEqual(detail_dict["params"]["min_length"], 3)

    @patch("logging.Logger.error")
    def test_error_logging(self, mock_logger):
        """Test error logging functionality."""
        error = BaseError(
            message="Test error", code="test_error", details={"key": "value"}
        )

        # Test error logging
        error.log()
        mock_logger.assert_called_once()

        # Verify log message contains error details
        log_message = mock_logger.call_args[0][0]
        self.assertIn("Test error", log_message)
        self.assertIn("test_error", log_message)

    def test_error_response_serialization(self):
        """Test error response serialization."""
        response = ErrorResponse(
            message="Test error",
            code="test_error",
            details=[
                ErrorDetail(
                    message="Detail message", code="detail_code", field="test_field"
                )
            ],
            path="/test/path",
        )

        response_dict = response.to_dict()
        self.assertTrue("error" in response_dict)
        self.assertEqual(response_dict["error"]["message"], "Test error")
        self.assertEqual(response_dict["error"]["code"], "test_error")
        self.assertEqual(response_dict["error"]["path"], "/test/path")
        self.assertTrue(len(response_dict["error"]["details"]) > 0)


if __name__ == "__main__":
    unittest.main()
