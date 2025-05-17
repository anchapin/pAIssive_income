# pAIssive_income

Framework for generating passive income by utilizing a team of AI agents to generate niche software and AI bots for customers.

## Features

- **AI Agent Team**: Utilize a team of AI agents to generate niche software and AI bots
- **CrewAI Integration**: Use CrewAI to create and manage AI agent teams
- **CopilotKit Integration**: Add AI copilot features to the React frontend
- **Multi-Chain Protocol (MCP) Support**: Connect to various AI providers through a unified interface

> **Note:** Documentation for this project has been centralized. Please see the [docs/](docs/) directory for additional onboarding, development, deployment, security, contribution information, and UI architecture ([docs/ui-architecture.md](docs/ui-architecture.md)).

## 1. Install Dev Dependencies (including pytest-xdist)

To enable parallel test execution and all developer/testing features, install the dev dependencies using [uv](https://github.com/astral-sh/uv):

```sh
uv pip install -e .[dev]
```
This will install `pytest`, `pytest-xdist`, and all plugins required for advanced testing.

## 2. Run Tests in Parallel (recommended)

We use [pytest-xdist](https://pypi.org/project/pytest-xdist/) to run tests in parallel across all available CPU cores:

```sh
pytest -n auto
```
By default, `-n auto` uses all available CPU cores. You can override with e.g. `pytest -n 4` to use 4 workers.

## 3. Skip Slow Tests During Development

Tests that take a long time to run are marked with `@pytest.mark.slow`. You can skip these tests during development to speed up your test runs:

```sh
pytest -m "not slow"
```

To run only the slow tests:

```sh
pytest -m "slow"
```

See `tests/examples/test_slow_test_example.py` for examples of how to mark slow tests.

## 4. Profile Slow Tests

Find the slowest tests to identify candidates for optimization or marking as slow:

```sh
pytest --durations=10
```

## 5. Only Collect Tests from `tests/`

Test collection is limited to the `tests/` directory for speed.

## Docker Compose Integration

**Start PostgreSQL database, application, and frontend with Docker Compose:**
```bash
# Using Docker Compose plugin
docker compose up --build

# Or using standalone Docker Compose
docker-compose up --build
```
This will launch the Flask backend, React frontend with ag-ui integration, and PostgreSQL database.

For more details on the Docker Compose integration, see [DOCKER_COMPOSE.md](DOCKER_COMPOSE.md).

## CrewAI + CopilotKit Integration

This project includes integration with CrewAI and CopilotKit to enable powerful multi-agent AI features in the React frontend.

### Features

- **Agentic Chat**: Chat with AI copilots and call frontend tools
- **Human-in-the-Loop**: Collaborate with the AI, plan tasks, and decide actions interactively
- **Agentic/Generative UI**: Assign long-running tasks to agents and see real-time progress

### Usage

To use the CrewAI + CopilotKit integration:

1. Install the required dependencies:
   ```bash
   # Backend (CrewAI)
   pip install '.[agents]'

   # Frontend (CopilotKit)
   cd ui/react_frontend
   npm install
   ```

2. Start the application:
   ```bash
   # Using Docker Compose
   docker compose up --build

   # Or manually
   python app.py
   ```

For more details on the CrewAI + CopilotKit integration, see:
- [docs/CrewAI_CopilotKit_Integration.md](docs/CrewAI_CopilotKit_Integration.md) - Main integration guide
- [ui/react_frontend/CopilotKit_CrewAI.md](ui/react_frontend/CopilotKit_CrewAI.md) - Frontend implementation details
- [docs/examples/CrewAI_CopilotKit_Advanced_Examples.md](docs/examples/CrewAI_CopilotKit_Advanced_Examples.md) - Advanced usage examples

## 6. Mock External Calls for Speed

Mock out network/database/API calls in your tests to keep them fast and reliable. This avoids actual external calls during testing, which can significantly speed up your test suite.

Example:
```python
@patch("requests.get")
def test_api_call(mock_get):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response

    # Test your function that uses requests.get
    result = my_function()
    assert result == expected_result
```

See `tests/examples/test_mocking_example.py` for more detailed examples of mocking.

## 7. Using Test Markers Effectively

The project uses various pytest markers to categorize tests:

- `@pytest.mark.unit`: Unit tests for individual components
- `@pytest.mark.integration`: Tests for interactions between components
- `@pytest.mark.slow`: Tests that take more than 1 second to run
- `@pytest.mark.api`: Tests related to API functionality
- `@pytest.mark.webhook`: Tests related to webhook functionality
- `@pytest.mark.security`: Tests related to security features
- `@pytest.mark.model`: Tests related to AI model functionality
- `@pytest.mark.performance`: Performance-sensitive tests

Run tests with specific markers:

```sh
# Run only unit tests
pytest -m unit

# Run tests that are both API-related and slow
pytest -m "api and slow"

# Run API tests that are not slow
pytest -m "api and not slow"
```

