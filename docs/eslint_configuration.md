# ESLint Configuration

This document provides an overview of the ESLint configuration for the pAIssive Income project.

## Overview

The project uses [ESLint](https://eslint.org/) version 9.x for JavaScript linting. ESLint helps maintain code quality and consistency across the JavaScript codebase.

## Configuration Files

- **.eslintrc.js**: Root configuration file for ESLint.
- **ui/react_frontend/tests/e2e/.eslintrc.js**: Configuration for E2E tests.

## ESLint Version

The project uses ESLint v9.x, which is the current supported version as of May 2024. ESLint v8.x reached End of Life (EOL) on October 5, 2024.

## Running ESLint

You can run ESLint from the command line:

```bash
# Run ESLint on all JavaScript files
pnpm lint

# Run ESLint in the JavaScript SDK
cd sdk/javascript
pnpm lint

# Run ESLint in the React frontend
cd ui/react_frontend
pnpm lint
```

## ESLint Rules

The project uses the recommended ESLint rules with some customizations:

- Base configuration extends `eslint:recommended`
- Test files have Jest environment enabled

## Integration with CI/CD

ESLint checks are part of the CI/CD pipeline to ensure code quality before merging.