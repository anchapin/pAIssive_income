# pAIssive Income Tests

This directory contains tests for the pAIssive Income framework.

## Test Structure

The tests are organized into the following directories:

- `ai_models/`: Tests for the AI Models module
  - Tests for ModelConfig, ModelInfo, ModelManager, AgentModelProvider
  - Tests for ModelDownloader and DownloadTask
  - Tests for PerformanceMonitor and InferenceTracker
- `monetization/`: Tests for the Monetization module
  - Tests for SubscriptionModel and FreemiumModel
  - Tests for PricingCalculator and RevenueProjector
  - Tests for SubscriptionManager and subscription workflows
- `niche_analysis/`: Tests for the Niche Analysis module
  - Tests for MarketAnalyzer, ProblemIdentifier, OpportunityScorer
  - Tests for niche analysis workflows
- `agent_team/`: Tests for the Agent Team module
  - Tests for AgentTeam and agent profiles
  - Tests for team configuration and collaboration
- `marketing/`: Tests for the Marketing module
  - Tests for PersonaCreator, DemographicAnalyzer, PainPointIdentifier
  - Tests for MarketingStrategy, ContentMarketingStrategy, SocialMediaStrategy
  - Tests for ContentTemplate, BlogPostTemplate, SocialMediaTemplate
- `integration/`: Integration tests for the framework
  - Tests for niche-to-solution workflow
  - Tests for AI models integration with Agent Team
  - Tests for monetization end-to-end workflows

## Running Tests

To run all tests:

```bash
pytest
```

To run tests for a specific module:

```bash
pytest tests/ai_models
```

To run a specific test file:

```bash
pytest tests/ai_models/test_model_config.py
```

To run a specific test function:

```bash
pytest tests/ai_models/test_model_config.py::test_model_config_init
```

## Test Categories

Tests are categorized using markers:

- `unit`: Unit tests
- `integration`: Integration tests
- `slow`: Tests that take a long time to run
- `api`: Tests that require API access
- `model`: Tests that require AI models

To run tests with a specific marker:

```bash
pytest -m unit
```

To run tests excluding a specific marker:

```bash
pytest -m "not slow"
```

## Test Coverage

To run tests with coverage:

```bash
pytest --cov=.
```

To generate a coverage report:

```bash
pytest --cov=. --cov-report=html
```

The coverage report will be generated in the `htmlcov` directory.

## Test Fixtures

Common test fixtures are defined in `conftest.py`. These fixtures can be used across all tests.

## Test Data

Test data is stored in the `data` directory. This includes mock data for testing.

## Test Utilities

Utility functions for tests are defined in `utils.py`. These functions can be used across all tests.

## Test Coverage Summary

The tests cover the following key aspects of the framework:

1. **Core Functionality**
   - Configuration management
   - Model management and integration
   - Subscription and monetization workflows
   - Niche analysis and opportunity scoring
   - Agent team collaboration
   - Marketing strategy and content generation

2. **Edge Cases**
   - Error handling in model loading and downloading
   - Invalid inputs to subscription models
   - Unknown niches in market analysis
   - Subscription upgrades and downgrades
   - Feature access control

3. **Integration Points**
   - AI Models with Agent Team
   - Subscription Models with Subscription Manager
   - Niche Analysis with Agent Team
   - Monetization with Revenue Projection

## Continuous Integration

To set up continuous integration for these tests:

1. Add the following to your CI workflow:

```yaml
name: Run Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run tests
      run: |
        pytest --cov=.
    - name: Upload coverage report
      uses: codecov/codecov-action@v1
```

2. Add a `.coveragerc` file to configure coverage reporting:

```ini
[run]
source = .
omit =
    tests/*
    setup.py
    */examples/*
    */cli/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
```
