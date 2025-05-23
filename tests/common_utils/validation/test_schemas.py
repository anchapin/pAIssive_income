"""Test module for common_utils.validation.schemas."""

import logging
import pytest
from pydantic import ValidationError

from common_utils.validation.schemas import (
    ErrorDetail,
    ErrorResponse,
    PaginationParams,
    SuccessResponse,
)


class TestErrorDetail:
    """Test suite for ErrorDetail schema."""

    def test_error_detail_with_field(self):
        """Test ErrorDetail with field."""
        error = ErrorDetail(field="name", message="Field required")
        assert error.field == "name"
        assert error.message == "Field required"

    def test_error_detail_without_field(self):
        """Test ErrorDetail without field."""
        error = ErrorDetail(message="General error")
        assert error.field is None
        assert error.message == "General error"

    def test_error_detail_model_dump(self):
        """Test ErrorDetail model_dump method."""
        error = ErrorDetail(field="name", message="Field required")
        error_dict = error.model_dump()
        assert error_dict["field"] == "name"
        assert error_dict["message"] == "Field required"


class TestErrorResponse:
    """Test suite for ErrorResponse schema."""

    def test_error_response_single_error(self):
        """Test ErrorResponse with a single error."""
        error = ErrorDetail(field="name", message="Field required")
        response = ErrorResponse(errors=[error])
        assert len(response.errors) == 1
        assert response.errors[0].field == "name"
        assert response.errors[0].message == "Field required"

    def test_error_response_multiple_errors(self):
        """Test ErrorResponse with multiple errors."""
        errors = [
            ErrorDetail(field="name", message="Field required"),
            ErrorDetail(field="age", message="Must be an integer"),
        ]
        response = ErrorResponse(errors=errors)
        assert len(response.errors) == 2
        fields = {error.field for error in response.errors}
        assert "name" in fields
        assert "age" in fields

    def test_error_response_model_dump(self):
        """Test ErrorResponse model_dump method."""
        error = ErrorDetail(field="name", message="Field required")
        response = ErrorResponse(errors=[error])
        response_dict = response.model_dump()
        assert "errors" in response_dict
        assert len(response_dict["errors"]) == 1
        assert response_dict["errors"][0]["field"] == "name"
        assert response_dict["errors"][0]["message"] == "Field required"


class TestSuccessResponse:
    """Test suite for SuccessResponse schema."""

    def test_success_response_with_data(self):
        """Test SuccessResponse with data."""
        data = {"name": "Test User", "age": 30}
        response = SuccessResponse(data=data)
        assert response.status == "success"
        assert response.data == data

    def test_success_response_with_message(self):
        """Test SuccessResponse with message."""
        response = SuccessResponse(data={}, message="Operation successful")
        assert response.status == "success"
        assert response.message == "Operation successful"

    def test_success_response_model_dump(self):
        """Test SuccessResponse model_dump method."""
        data = {"name": "Test User", "age": 30}
        response = SuccessResponse(data=data, message="Operation successful")
        response_dict = response.model_dump()
        assert response_dict["status"] == "success"
        assert response_dict["data"] == data
        assert response_dict["message"] == "Operation successful"


class TestPaginationParams:
    """Test suite for PaginationParams schema."""

    def test_pagination_params_defaults(self):
        """Test PaginationParams with default values."""
        params = PaginationParams()
        assert params.page == 1
        assert params.limit == 10

    def test_pagination_params_custom_values(self):
        """Test PaginationParams with custom values."""
        params = PaginationParams(page=2, limit=20)
        assert params.page == 2
        assert params.limit == 20

    def test_pagination_params_validation(self):
        """Test PaginationParams validation."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)  # page must be >= 1

        with pytest.raises(ValidationError):
            PaginationParams(limit=0)  # limit must be >= 1

        with pytest.raises(ValidationError):
            PaginationParams(limit=101)  # limit must be <= 100

    def test_pagination_params_model_dump(self):
        """Test PaginationParams model_dump method."""
        params = PaginationParams(page=2, limit=20)
        params_dict = params.model_dump()
        assert params_dict["page"] == 2
        assert params_dict["limit"] == 20
