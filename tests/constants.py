"""
constants - Module for tests/constants.

This module provides constants for use in tests.
"""

# Standard library imports

# Third-party imports

# Local imports

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503

# Common test constants
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_COUNT = 3
DEFAULT_BATCH_SIZE = 100
DEFAULT_PAGE_SIZE = 20
DEFAULT_LIMIT = 10

# Test data constants
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test-password-123"
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "Admin-password-123"

# Test model constants
TEST_MODEL_NAME = "test-model"
TEST_MODEL_VERSION = "1.0.0"
TEST_MODEL_DESCRIPTION = "Test model for unit tests"

# Test agent constants
TEST_AGENT_NAME = "test-agent"
TEST_AGENT_DESCRIPTION = "Test agent for unit tests"
TEST_AGENT_TYPE = "assistant"

# Test team constants
TEST_TEAM_NAME = "test-team"
TEST_TEAM_DESCRIPTION = "Test team for unit tests"
AGENT_COUNT = 2
