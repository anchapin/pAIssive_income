# Vitest Testing Framework

This document provides information about the Vitest testing framework integration in the frontend application.

## Overview

Vitest is a fast and lightweight testing framework for JavaScript and TypeScript projects, designed as a Vite-native alternative to Jest. It provides a modern testing experience with features like:

- Fast execution through Vite's native ESM-based transformation
- Watch mode for rapid development
- Compatible with Jest's API for easy migration
- Built-in code coverage reporting
- UI for visualizing test results

## Recent Improvements (req-28)

The Vitest framework has been significantly improved with recent workflow fixes:

### Fixed Issues
- **Dependency Caching**: Fixed missing pnpm-lock.yaml file causing cache failures
- **Node.js Setup**: Corrected cache-dependency-path configuration in GitHub Actions
- **PATH Configuration**: Added proper pnpm PATH setup for reliable test execution
- **Error Handling**: Enhanced error handling with fallback coverage report generation

### Workflow Enhancements
- Improved dependency installation process
- Added fallback mechanisms for test failures
- Enhanced coverage reporting reliability
- Better error messages for debugging

## Setup

The Vitest framework has been integrated into our React frontend with the following components:

1. **Configuration**: `vitest.config.ts` in the `ui/react_frontend` directory configures the testing environment.
2. **Test Setup**: `tests/setup.ts` provides global setup for React Testing Library integration.
3. **Sample Tests**: A basic test structure in `src/__tests__/` demonstrates how to write tests.
4. **Package Dependencies**: Added Vitest and related testing libraries to `package.json`.
5. **CI Integration**: Added a GitHub Actions workflow (`.github/workflows/frontend-vitest.yml`) to run tests on pull requests.

## Running Tests

To run the Vitest tests locally:

```bash
# Navigate to the React frontend directory
cd ui/react_frontend

# Install dependencies if needed
pnpm install

# Run tests
pnpm run test:unit

# Run tests with UI
pnpm run test:unit:ui
```

## Writing Tests

Tests should be placed in the `src/__tests__/` directory or alongside the components they test with a `.test.ts` or `.test.tsx` extension.

Example test:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
});
```

## CI Workflow

The GitHub Actions workflow (`.github/workflows/frontend-vitest.yml`) automatically runs Vitest tests when changes are made to the React frontend code. The workflow:

1. Sets up the Node.js environment with Node.js 20.x
2. Configures pnpm using the pnpm/action-setup@v4 action
3. Adds pnpm to the PATH environment variable
4. Verifies pnpm installation with version checks
5. Installs dependencies using pnpm
6. Runs the tests with proper error handling
7. Uploads coverage reports as artifacts

## Coverage Reports

Test coverage reports are generated in HTML, JSON, and text formats and are available as artifacts in the GitHub Actions workflow runs.
