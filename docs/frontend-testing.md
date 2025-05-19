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

### Unit Tests

Unit tests focus on testing individual functions and methods in isolation. We use Vitest for unit testing React components and JavaScript/TypeScript code. These tests verify that:
- Components render correctly with different props
- State updates work as expected
- Event handlers behave correctly
- Utility functions return the expected results

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

### Unit Tests

We have comprehensive unit tests for various components:

#### UI Components
- `src/components/UI/Notifications.test.jsx` - Tests for the Notifications component
- `src/components/Layout/Layout.test.jsx` - Tests for the Layout component
- `src/components/auth/LoginForm.test.jsx` - Tests for the LoginForm component

#### Visualization Components
- `src/components/Visualizations/ApiEndpointBarChart.test.js` - Tests for the ApiEndpointBarChart component
- `src/components/Visualizations/ApiStatusPieChart.test.js` - Tests for the ApiStatusPieChart component
- `src/components/Visualizations/ApiUsageLineChart.test.js` - Tests for the ApiUsageLineChart component
- `src/components/Visualizations/CohortRetentionChart.test.js` - Tests for the CohortRetentionChart component
- `src/components/Visualizations/ConversionFunnelChart.test.js` - Tests for the ConversionFunnelChart component
- `src/components/Visualizations/CustomerLifetimeValueGauge.test.js` - Tests for the CustomerLifetimeValueGauge component
- `src/components/Visualizations/MultiMetricLineChart.test.js` - Tests for the MultiMetricLineChart component
- `src/components/Visualizations/OpportunityBarChart.test.js` - Tests for the OpportunityBarChart component
- `src/components/Visualizations/OpportunityRadarChart.test.js` - Tests for the OpportunityRadarChart component
- `src/components/Visualizations/RevenueAreaChart.test.js` - Tests for the RevenueAreaChart component
- `src/components/Visualizations/RevenueProjectionChart.test.js` - Tests for the RevenueProjectionChart component
- `src/components/Visualizations/ScoreDistributionPieChart.test.js` - Tests for the ScoreDistributionPieChart component
- `src/components/Visualizations/TierRevenueStackedBarChart.test.js` - Tests for the TierRevenueStackedBarChart component
- `src/components/Visualizations/UserActivityChart.test.js` - Tests for the UserActivityChart component
- `src/components/Visualizations/UserGrowthLineChart.test.js` - Tests for the UserGrowthLineChart component

#### Analytics Components
- `src/components/ApiAnalytics/ApiAnalyticsDashboard.test.js` - Tests for the ApiAnalyticsDashboard component

#### Integration Tests
- `src/__tests__/AgentUI.test.ts` - Integration tests for the AgentUI component

### Mock API Server

- `tests/mock_api_server.js` - Implementation of the mock API server
- `tests/mock_api_server.test.js` - Tests for the mock API server

## Running Tests Locally

### Running E2E Tests

To run the end-to-end tests locally:

1. Start the mock API server:
   ```bash
   node tests/mock_api_server.js
   ```

2. Start the React development server:
   ```bash
   pnpm start
   ```

3. Run the E2E tests:
   ```bash
   npx playwright test
   ```

### Running Unit Tests

To run the unit tests locally:

1. Navigate to the React frontend directory:
   ```bash
   cd ui/react_frontend
   ```

2. Run the unit tests using Vitest:
   ```bash
   pnpm test
   ```

3. To run tests with coverage:
   ```bash
   pnpm test:coverage
   ```

4. To run a specific test file:
   ```bash
   pnpm test src/components/UI/Notifications.test.jsx
   ```

## CI/CD Integration

### E2E Tests

The end-to-end tests are integrated into the GitHub Actions CI/CD pipeline. The workflow file `.github/workflows/frontend-e2e-mock.yml` defines the steps to:
1. Set up the environment
2. Install dependencies
3. Start the mock API server
4. Start the React development server
5. Run the E2E tests

### Unit Tests

The unit tests are integrated into the GitHub Actions CI/CD pipeline. The workflow file `.github/workflows/frontend-vitest.yml` defines the steps to:
1. Set up the environment
2. Install dependencies
3. Run the unit tests
4. Generate and upload test coverage reports

### Mock API Server Tests

The mock API server tests are integrated into the GitHub Actions CI/CD pipeline. The workflow file `.github/workflows/mock-api-server.yml` defines the steps to:
1. Set up the environment
2. Install dependencies
3. Run the mock API server tests
4. Verify that the mock API server works correctly with the frontend tests

## Troubleshooting

### Common Issues with E2E Tests

1. **Tests fail with connection errors**
   - Make sure the React app is running on port 3000
   - Make sure the mock API server is running on port 8000

2. **Tests fail with timeout errors**
   - Increase the timeout values in the test files
   - Check if the selectors are correct

3. **Tests pass locally but fail in CI**
   - Check the CI logs for any environment-specific issues
   - Make sure all dependencies are installed in the CI environment

### Common Issues with Unit Tests

1. **Tests fail with module import errors**
   - Make sure all dependencies are installed
   - Check for circular dependencies
   - Verify that the import paths are correct

2. **Tests fail with React rendering errors**
   - Make sure the component is properly mocked
   - Check if all required props are provided
   - Verify that the component's dependencies are properly mocked

3. **Tests fail with path-to-regexp errors**
   - This is a known issue in CI environments
   - Use the fix-codeql-issues.sh script to create a mock implementation of path-to-regexp
   - Alternatively, mock the path-to-regexp module in your tests

4. **Tests fail with timeout errors**
   - Increase the timeout values in the test configuration
   - Check for asynchronous operations that might be taking too long
   - Verify that all promises are properly awaited

## Best Practices

### E2E Testing Best Practices

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

### Unit Testing Best Practices

1. **Follow the AAA pattern (Arrange-Act-Assert)**
   - Arrange: Set up the test data and conditions
   - Act: Perform the action being tested
   - Assert: Verify the results

2. **Test one thing at a time**
   - Each test should focus on a single behavior or functionality
   - Avoid testing multiple behaviors in a single test

3. **Use mocks appropriately**
   - Mock external dependencies to isolate the component being tested
   - Use Jest's mock functions to verify function calls and arguments

4. **Test edge cases**
   - Test boundary conditions and error cases
   - Verify that components handle unexpected inputs gracefully

5. **Keep tests fast**
   - Unit tests should run quickly to provide fast feedback
   - Avoid unnecessary setup and teardown operations

6. **Use test coverage reports**
   - Monitor test coverage to identify untested code
   - Aim for high coverage but prioritize meaningful tests over coverage percentage

## Recent Improvements

The frontend tests have been recently improved to:

1. **Fix path-to-regexp error in mock API server**
   - Added a mock implementation of path-to-regexp for CI compatibility
   - Fixed issues with URL parsing in the mock API server

2. **Update error handling in mock API server tests**
   - Improved error handling and logging for better debugging
   - Added more robust error recovery mechanisms

3. **Fix catch method usage in tests**
   - Updated tests to use proper error handling with try/catch
   - Fixed issues with promise rejection handling

4. **Add better logging for CI environments**
   - Enhanced logging for better visibility in CI environments
   - Added more detailed error messages for easier troubleshooting

5. **Improve error handling for URL parsing**
   - Added more robust URL parsing with better error handling
   - Fixed issues with malformed URLs in tests

These improvements have made the frontend tests more reliable and easier to maintain, especially in CI environments.
