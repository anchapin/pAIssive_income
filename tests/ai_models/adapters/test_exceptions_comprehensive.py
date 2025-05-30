"""Comprehensive tests for the ai_models.adapters.exceptions module."""

import pytest

from ai_models.adapters.exceptions import (
    AdapterError,
    ModelContextProtocolError,
)


class TestExceptionsComprehensive:
    """Comprehensive test suite for the exceptions module."""

    def test_adapter_error_base_class(self):
        """Test that AdapterError is a subclass of Exception."""
        assert issubclass(AdapterError, Exception)

    def test_adapter_error_instantiation(self):
        """Test that AdapterError can be instantiated with a message."""
        # Create an instance with a custom message
        error = AdapterError("Custom error message")

        # Verify the error message
        assert str(error) == "Custom error message"

    def test_adapter_error_inheritance(self):
        """Test that AdapterError can be subclassed."""
        # Create a custom subclass of AdapterError
        class CustomAdapterError(AdapterError):
            pass

        # Verify the inheritance
        assert issubclass(CustomAdapterError, AdapterError)
        assert issubclass(CustomAdapterError, Exception)

        # Create an instance of the custom error
        error = CustomAdapterError("Custom subclass error")

        # Verify the error message
        assert str(error) == "Custom subclass error"

    def test_model_context_protocol_error(self):
        """Test ModelContextProtocolError class."""
        # Verify that ModelContextProtocolError is a subclass of AdapterError
        assert issubclass(ModelContextProtocolError, AdapterError)

        # Create an instance of ModelContextProtocolError
        error = ModelContextProtocolError()

        # Verify the error message
        assert "modelcontextprotocol-python-sdk is not installed" in str(error)
        assert "uv pip install modelcontextprotocol-python-sdk" in str(error)

    def test_model_context_protocol_error_standard_message(self):
        """Test that ModelContextProtocolError uses a standard message."""
        # Create two instances of ModelContextProtocolError
        error1 = ModelContextProtocolError()
        error2 = ModelContextProtocolError()

        # Verify that both instances have the same error message
        assert str(error1) == str(error2)
        assert str(error1) == ModelContextProtocolError.MESSAGE

    def test_exception_handling(self):
        """Test handling of adapter exceptions."""
        # Test catching AdapterError
        try:
            raise AdapterError("Test error")
        except AdapterError as e:
            assert str(e) == "Test error"

        # Test catching ModelContextProtocolError
        try:
            raise ModelContextProtocolError()
        except ModelContextProtocolError as e:
            assert "modelcontextprotocol-python-sdk is not installed" in str(e)

        # Test catching ModelContextProtocolError as AdapterError
        try:
            raise ModelContextProtocolError()
        except AdapterError as e:
            assert "modelcontextprotocol-python-sdk is not installed" in str(e)

    def test_custom_adapter_error_with_attributes(self):
        """Test creating a custom AdapterError with additional attributes."""
        # Create a custom AdapterError subclass with additional attributes
        class CustomAttributeError(AdapterError):
            def __init__(self, message, code, details=None):
                super().__init__(message)
                self.code = code
                self.details = details

        # Create an instance with custom attributes
        error = CustomAttributeError("Custom error", 404, {"reason": "Not found"})

        # Verify the error message and attributes
        assert str(error) == "Custom error"
        assert error.code == 404
        assert error.details == {"reason": "Not found"}

    def test_adapter_error_in_exception_chain(self):
        """Test using AdapterError in an exception chain."""
        try:
            try:
                # Raise a built-in exception
                raise ValueError("Original error")
            except ValueError as original_error:
                # Wrap it in an AdapterError
                raise AdapterError("Wrapped error") from original_error
        except AdapterError as adapter_error:
            # Verify the exception chain
            assert str(adapter_error) == "Wrapped error"
            assert isinstance(adapter_error.__cause__, ValueError)
            assert str(adapter_error.__cause__) == "Original error"
