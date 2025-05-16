# Frontend Testing Guide

This document provides an overview of the frontend testing approach used in the pAIssive Income project, including the setup for end-to-end (e2e) tests and integration with the GitHub Actions CI/CD pipeline.

## Overview

The frontend tests are designed to verify that the UI components work correctly and interact properly with the backend API. We use Playwright for end-to-end testing of the React frontend.

## Test Types

### End-to-End (E2E) Tests

E2E tests simulate real user interactions with the application. They verify that:
- Components render correctly
- User interactions (clicks, form submissions, etc.) work as expected
- API integrations function properly

### Component Tests

Component tests focus on testing individual UI components in isolation. They verify that:
- Components render with the expected props
- State changes work correctly
- Event handlers are called appropriately

## Mock API Server

For testing purposes, we use a mock API server that simulates the backend API. This approach has several advantages:
- Tests are more reliable and don't depend on the actual backend
- Tests run faster since they don't need to wait for the backend to process requests
- Tests can be run in CI environments without setting up the full backend

### Mock API Server Implementation

The mock API server is implemented using Express.js and provides the following endpoints:
- `/api/agent` - Returns mock agent data
- `/api/agent/action` - Handles agent actions

To start the mock API server:

```bash
node tests/mock_api_server.js
```

The server runs on port 8000 by default.

## Test Files

### E2E Tests

- `tests/e2e/agent_ui_final.spec.ts` - Tests for the AgentUI component
- `tests/e2e/simple.spec.ts` - Basic tests for the homepage

### Mock API Server

- `tests/mock_api_server.js` - Implementation of the mock API server

## Running Tests Locally

To run the tests locally:

1. Start the mock API server:
   ```bash
   node tests/mock_api_server.js
   ```

2. Start the React development server:
   ```bash
   pnpm start
   ```

3. Run the tests:
   ```bash
   npx playwright test
   ```

## CI/CD Integration

The tests are integrated into the GitHub Actions CI/CD pipeline. The workflow file `.github/workflows/frontend-e2e-mock.yml` defines the steps to:
1. Set up the environment
2. Install dependencies
3. Start the mock API server
4. Start the React development server
5. Run the tests

## Troubleshooting

### Common Issues

1. **Tests fail with connection errors**
   - Make sure the React app is running on port 3000
   - Make sure the mock API server is running on port 8000

2. **Tests fail with timeout errors**
   - Increase the timeout values in the test files
   - Check if the selectors are correct

3. **Tests pass locally but fail in CI**
   - Check the CI logs for any environment-specific issues
   - Make sure all dependencies are installed in the CI environment

## Best Practices

1. **Use descriptive test names**
   - Test names should clearly describe what is being tested

2. **Keep tests independent**
   - Each test should be able to run independently of others

3. **Use appropriate selectors**
   - Prefer role-based selectors (e.g., `getByRole('button')`) over text-based selectors
   - Use data-testid attributes for elements that don't have semantic roles

4. **Handle asynchronous operations properly**
   - Use `await` for all asynchronous operations
   - Use appropriate timeouts for network requests

5. **Take screenshots on failure**
   - Configure tests to take screenshots when they fail for easier debugging
