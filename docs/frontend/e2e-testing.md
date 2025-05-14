# Frontend End-to-End Testing

## Overview

This document describes the end-to-end (E2E) testing setup for the React frontend application. E2E tests verify that the application works correctly from a user's perspective by simulating user interactions with the application.

## Testing Framework

The project uses [Playwright](https://playwright.dev/) for E2E testing, which provides:

- Cross-browser testing (Chromium, Firefox, WebKit)
- Reliable auto-waiting for elements
- Strong isolation with browser contexts
- Powerful automation capabilities
- Screenshot and video capture

## Workflow Configuration

The E2E tests are run automatically using the GitHub Actions workflow defined in `.github/workflows/frontend-e2e.yml`. This workflow:

1. Runs on pull requests that modify files in the `ui/react_frontend` directory
2. Can be manually triggered with platform selection (Ubuntu, Windows, or both)
3. Sets up the necessary environment for running the tests
4. Runs the backend API server for the tests
5. Executes the Playwright tests
6. Uploads test reports as artifacts

## Key Features

### Cross-Platform Testing

The workflow supports testing on different platforms:

- **Ubuntu**: Default platform for testing
- **Windows**: Optional platform for testing
- **Both**: Can run tests on both platforms when manually triggered

### Backend API Integration

The workflow automatically:

1. Sets up a Python environment for the backend API
2. Installs backend dependencies
3. Starts the backend API server
4. Waits for the server to be ready before running tests
5. Verifies server health via the `/health` endpoint

### Robust Test Execution

The workflow includes:

- **Retry Mechanism**: Automatically retries failed tests
- **Artifact Collection**: Uploads test reports and screenshots
- **Error Handling**: Proper cleanup of processes even on failure

## Running Tests Locally

To run the E2E tests locally:

```bash
# Navigate to the React frontend directory
cd ui/react_frontend

# Install dependencies if needed
pnpm install

# Install Playwright browsers
npx playwright install --with-deps

# Start the backend API server in a separate terminal
cd ../..
python ui/api_server.py

# Run the tests
cd ui/react_frontend
npx playwright test
```

## Writing E2E Tests

E2E tests should be placed in the `ui/react_frontend/e2e` directory with a `.spec.ts` extension.

Example test:

```typescript
import { test, expect } from '@playwright/test';

test('basic navigation test', async ({ page }) => {
  // Navigate to the home page
  await page.goto('http://localhost:3000');
  
  // Verify the page title
  await expect(page).toHaveTitle(/pAIssive Income/);
  
  // Click on a navigation link
  await page.click('text=Dashboard');
  
  // Verify navigation was successful
  await expect(page).toHaveURL(/.*dashboard/);
});
```

## Test Reports

The workflow generates comprehensive test reports:

- **HTML Reports**: Interactive reports with screenshots and traces
- **JUnit Reports**: XML reports for CI integration
- **Artifacts**: Reports are uploaded as artifacts in GitHub Actions

## Troubleshooting

### Common Issues

1. **Backend API not starting**: Verify the API server is running and accessible at http://localhost:8000/health
2. **Browser installation issues**: Run `npx playwright install --with-deps` to ensure all browser dependencies are installed
3. **Test timeouts**: Increase timeouts in the Playwright configuration for slower environments

### Debugging Tests

To debug tests locally:

```bash
# Run tests in debug mode
npx playwright test --debug

# Run a specific test file
npx playwright test specific-test.spec.ts --debug
```

## Related Documentation

- [Vitest Framework](./vitest-framework.md) - Unit testing for the frontend
- [UI Components Guide](../ui_components_guide.md) - Documentation for UI components
- [UI Accessibility Guide](../ui_accessibility_guide.md) - Accessibility guidelines
