# API Testing Suite

This directory contains tests for the pAIssive Income API. The tests are organized by API module and include both unit tests for individual endpoints and integration tests that span multiple endpoints.

## Test Structure

- `conftest.py`: Contains pytest fixtures for API tests
- `utils/`: Contains utilities for API testing
  - `test_client.py`: Test client for making API requests
  - `test_data.py`: Utilities for generating test data
  - `test_validators.py`: Utilities for validating API responses
  - `test_query_params.py`: Tests for query parameter utilities
- `test_niche_analysis_api.py`: Tests for the niche analysis API
- `test_monetization_api.py`: Tests for the monetization API
- `test_marketing_api.py`: Tests for the marketing API
- `test_ai_models_api.py`: Tests for the AI models API
- `test_agent_team_api.py`: Tests for the agent team API
- `test_user_api.py`: Tests for the user API
- `test_dashboard_api.py`: Tests for the dashboard API
- `test_api_key_api.py`: Tests for the API key API
- `test_analytics_api.py`: Tests for the analytics API
- `test_webhook_api.py`: Tests for the webhook API
- `test_api_integration.py`: Integration tests that span multiple API endpoints

## Running the Tests

To run all API tests:

```bash
pytest tests/api
```

To run tests for a specific API module:

```bash
pytest tests/api/test_niche_analysis_api.py
```

To run a specific test:

```bash
pytest tests/api/test_niche_analysis_api.py:TestNicheAnalysisAPI:test_analyze_niche
```

## Test Categories

The tests are categorized using markers:

- `unit`: Unit tests for individual endpoints
- `integration`: Integration tests that span multiple endpoints
- `api`: Tests that require API access

To run tests with a specific marker:

```bash
pytest -m api
```

## Test Coverage

To run tests with coverage:

```bash
pytest --cov=api tests/api
```

## Adding New Tests

To add tests for a new API endpoint:

1. Identify the appropriate test file for the API module
2. Add a new test method to the test class
3. Use the `api_test_client` or `auth_api_test_client` fixture to make API requests
4. Use the validation utilities to validate the response

Example:

```python
def test_new_endpoint(self, api_test_client: APITestClient):
    """Test a new endpoint."""
    # Generate test data
    data = {"key": "value"}
    
    # Make request
    response = api_test_client.post("module/endpoint", data)
    
    # Validate response
    result = validate_success_response(response, 201)  # Created
    
    # Validate fields
    validate_field_exists(result, "id")
    validate_field_type(result, "id", str)
    validate_field_not_empty(result, "id")
```

## Test Utilities

The test utilities provide a consistent way to make API requests and validate responses:

- `APITestClient`: A wrapper around the FastAPI test client that provides methods for making API requests
- `generate_*_data()`: Functions for generating test data for different API modules
- `validate_*()`: Functions for validating API responses

## Mocking

The tests use pytest fixtures to mock external dependencies:

- `api_client`: A FastAPI test client for making API requests
- `api_test_client`: A wrapper around the FastAPI test client that provides methods for making API requests
- `auth_api_test_client`: A wrapper around the FastAPI test client that includes authentication headers

## Test Data

The tests use generated test data to avoid hardcoding values:

- `generate_id()`: Generates a random ID
- `generate_niche_analysis_data()`: Generates test data for niche analysis
- `generate_monetization_data()`: Generates test data for monetization
- `generate_marketing_strategy_data()`: Generates test data for marketing strategies
- `generate_ai_model_data()`: Generates test data for AI models
- `generate_agent_team_data()`: Generates test data for agent teams
- `generate_user_data()`: Generates test data for users
- `generate_api_key_data()`: Generates test data for API keys
- `generate_webhook_data()`: Generates test data for webhooks

## Validation

The tests use validation utilities to ensure that API responses are correct:

- `validate_status_code()`: Validates the status code of a response
- `validate_json_response()`: Validates that a response is JSON and returns the parsed JSON
- `validate_error_response()`: Validates an error response
- `validate_success_response()`: Validates a success response
- `validate_paginated_response()`: Validates a paginated response
- `validate_bulk_response()`: Validates a bulk operation response
- `validate_field_*()`: Functions for validating fields in a response
- `validate_list_*()`: Functions for validating lists in a response
