# pAIssive Income Testing Framework

This document provides a comprehensive guide to the testing infrastructure for the pAIssive Income project.

## Table of Contents

1. [Test Structure](#test-structure)
2. [Test Categories](#test-categories)
3. [Test Fixtures](#test-fixtures)
4. [Running Tests](#running-tests)
5. [Test Coverage](#test-coverage)
6. [Writing New Tests](#writing-new-tests)
7. [CI/CD Integration](#cicd-integration)

## Test Structure

The test suite is organized as follows:

```
tests/
├── api/              # API-level tests
├── conftest.py       # Shared fixtures for all tests
├── integration/      # Integration tests
├── models/           # Model tests
├── performance/      # Performance and load tests
├── schemas/          # Schema validation tests
├── security/         # Security tests
└── unit/             # Unit tests
```

## Test Categories

Tests are categorized using pytest markers to allow selective test execution:

- **unit**: Unit tests for individual components
- **integration**: Tests for interactions between components
- **webhook**: Tests related to webhook functionality
- **api**: Tests for API endpoints
- **payment**: Tests for payment functionality
- **security**: Tests for security features
- **model**: Tests for AI model functionality
- **performance**: Performance-sensitive tests
- **slow**: Tests that take more than 1 second to run
- **smoke**: Critical functionality tests
- **flaky**: Tests that occasionally fail
- **dependency**: Tests requiring external dependencies
- **asyncio**: Asynchronous tests

## Test Fixtures

Common test fixtures are defined in `tests/conftest.py` to promote code reuse and simplify test setup.

### Key Fixtures

#### Webhook Testing Fixtures

```python
@pytest.fixture(scope="function")
def webhook_service() -> WebhookService:
    """Returns a WebhookService instance."""
    return WebhookService()

@pytest.fixture(scope="function")
async def running_webhook_service() -> Generator[WebhookService, None, None]:
    """Returns a running WebhookService and cleans up after tests."""
    service = WebhookService()
    await service.start()
    yield service
    await service.stop()

@pytest.fixture(scope="function")
async def registered_webhook(running_webhook_service) -> Dict[str, Any]:
    """Returns a registered test webhook."""
    webhook_data = {
        "url": "https://example.com/test-webhook",
        "events": [WebhookEventType.USER_CREATED, WebhookEventType.PAYMENT_RECEIVED],
        "description": "Test webhook for automated tests",
        "headers": {"Authorization": "Bearer test-token"},
        "is_active": True,
    }

    webhook = await running_webhook_service.register_webhook(webhook_data)
    return webhook
```

#### Mock Fixtures

```python
@pytest.fixture(scope="function")
def mock_http_client(monkeypatch):
    """Mocks HTTP client to avoid real HTTP requests during tests."""
    # Mock implementation details in conftest.py

@pytest.fixture(scope="function")
def mock_audit_service(monkeypatch):
    """Mocks the AuditService to avoid side effects during tests."""
    # Mock implementation details in conftest.py
```

## Running Tests

### Using the Enhanced Test Runner

The project provides `run_tests.py` with multiple options for running tests:

```bash
# Run all tests
python run_tests.py

# Run tests with specific marker
python run_tests.py --unit       # Run only unit tests
python run_tests.py --integration # Run only integration tests
python run_tests.py --webhook    # Run only webhook tests

# Run tests with coverage reporting
python run_tests.py --coverage

# Run tests with HTML report generation
python run_tests.py --html

# Run tests in parallel
python run_tests.py --parallel

# Run only previously failed tests
python run_tests.py --failed-only

# Run tests matching specific pattern
python run_tests.py --pattern "webhook"

# Combine options
python run_tests.py --webhook --coverage --verbose
```

### Using the Webhook-Specific Test Runner

For webhook-specific testing, use `run_webhook_tests.py`:

```bash
# Run standalone webhook test
python run_webhook_tests.py

# Run only webhook unit tests
python run_webhook_tests.py --unit

# Run only webhook integration tests
python run_webhook_tests.py --integration

# Run all webhook tests (unit and integration)
python run_webhook_tests.py --all

# Run with coverage reporting
python run_webhook_tests.py --coverage

# Run with verbose output
python run_webhook_tests.py --verbose

# Combine options
python run_webhook_tests.py --all --coverage --verbose
```

### Using pytest Directly

You can also use pytest commands directly:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/api/test_webhook_service.py

# Run tests with specific marker
python -m pytest -m webhook

# Run specific test function
python -m pytest tests/api/test_webhook_service.py:TestWebhookService:test_register_webhook
```

### Async Test Support

For asynchronous tests, pytest-asyncio is configured in the pytest.ini file. Mark async tests with `@pytest.mark.asyncio`. Example:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

## Test Coverage

Coverage reports are generated using pytest-cov when running tests with the `--coverage` option.

```bash
# Run tests with coverage reporting
python run_tests.py --coverage
```

The coverage report will be available in:
- Terminal output (summary)
- HTML report: `coverage_html/index.html`
- XML report: `coverage-{python-version}.xml`

The HTML report will be automatically opened in your browser after test execution.

## Writing New Tests

### Test Class Structure

Organize tests in classes for related functionality. Use descriptive test function names starting with `test_`:

```python
class TestWebhookService:
    """Test suite for the WebhookService class."""

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_register_webhook(self, webhook_service, mock_audit_service):
        """Test registering a webhook."""
        # Test implementation

    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.webhook
    async def test_list_webhooks(self, running_webhook_service):
        """Test listing webhooks."""
        # Test implementation
```

### Using Markers

Add appropriate markers to your tests to help with categorization and selective execution:

```python
@pytest.mark.unit          # Unit test
@pytest.mark.webhook       # Webhook-related test
@pytest.mark.asyncio       # Asynchronous test
@pytest.mark.slow          # Slow test (>1 second)
@pytest.mark.flaky         # Occasionally failing test
@pytest.mark.security      # Security-related test
@pytest.mark.performance   # Performance-sensitive test
```

### Using Fixtures

Use fixtures to set up test dependencies and promote code reuse:

```python
async def test_update_webhook(self, registered_webhook, running_webhook_service):
    """Test updating a webhook."""
    # registered_webhook and running_webhook_service are provided by fixtures
    # Test implementation
```

## CI/CD Integration

The testing framework is designed to integrate with CI/CD pipelines:

- **GitHub Actions**: The test suite runs on PRs and merges to main
- **Test Reports**: HTML and XML reports are generated for integration with CI tools
- **Coverage Requirements**: 80% minimum coverage required for PRs to be merged

### GitHub Actions Workflow

The test runner is integrated with GitHub Actions to run tests automatically:

```yaml
# In .github/workflows/test.yml
- name: Run Tests
  run: python run_tests.py --coverage --html
```

## Troubleshooting

### Common Issues

1. **Test Discovery Fails**:
   - Ensure test file names start with `test_`
   - Ensure test function names start with `test_`
   - Ensure test classes start with `Test`

2. **Asynchronous Tests Not Running**:
   - Ensure tests are marked with `@pytest.mark.asyncio`
   - Check pytest-asyncio is installed and configured

3. **Coverage Reports Not Generated**:
   - Ensure pytest-cov is installed
   - Check coverage configuration in pytest.ini

## Getting Help

For questions about the testing framework, contact the development team or refer to the project documentation.
