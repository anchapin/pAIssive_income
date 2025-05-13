# Setup PNPM Reusable Workflow

## Overview

This document describes the reusable GitHub Actions workflow for setting up PNPM in CI/CD pipelines. PNPM is a fast, disk space efficient package manager that is used for managing JavaScript dependencies in the project.

## Workflow File

The workflow is defined in `.github/workflows/setup-pnpm.yml` and is designed to be reused across multiple workflows that require PNPM.

## Key Features

### Reusable Design

The workflow is designed as a reusable workflow that can be called from other workflows using the `workflow_call` trigger. This allows for consistent PNPM setup across different workflows without duplicating code.

### Cross-Platform Support

The workflow runs on both Ubuntu and Windows platforms, ensuring that PNPM is properly set up regardless of the operating system.

### Configurable Options

The workflow accepts several input parameters to customize its behavior:

- **node-version**: The Node.js version to use (default: '18')
- **pnpm-version**: The PNPM version to use (default: '8')
- **working-directory**: The directory containing the package.json file (default: '.')
- **install-dependencies**: Whether to install dependencies (default: true)
- **verify-package-json**: Whether to verify the package.json file exists (default: true)
- **create-if-missing**: Whether to create a minimal package.json if missing (default: true)

### Platform-Specific Setup

The workflow includes platform-specific steps for setting up PNPM:

- **Linux**: Adds PNPM to the PATH environment variable using bash
- **Windows**: Adds PNPM to the PATH environment variable using PowerShell

### Robust Error Handling

The workflow includes verification steps to ensure PNPM is properly installed and accessible:

- Verifies PNPM is in the PATH
- Checks PNPM version
- Validates package.json existence

### Fallback Mechanisms

If `create-if-missing` is enabled and no package.json is found, the workflow creates a minimal package.json file for testing purposes.

## Usage

To use this reusable workflow in another workflow:

```yaml
jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup PNPM
        uses: ./.github/workflows/setup-pnpm.yml
        with:
          node-version: '20'
          pnpm-version: '8'
          working-directory: 'ui/react_frontend'
          install-dependencies: true
```

## Input Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| node-version | Node.js version to use | '18' | No |
| pnpm-version | PNPM version to use | '8' | No |
| working-directory | Directory containing package.json | '.' | No |
| install-dependencies | Whether to install dependencies | true | No |
| verify-package-json | Whether to verify package.json exists | true | No |
| create-if-missing | Whether to create package.json if missing | true | No |

## Example Scenarios

### Basic Setup

```yaml
- name: Setup PNPM
  uses: ./.github/workflows/setup-pnpm.yml
```

### Custom Node.js and PNPM Versions

```yaml
- name: Setup PNPM
  uses: ./.github/workflows/setup-pnpm.yml
  with:
    node-version: '20'
    pnpm-version: '8.1.0'
```

### Custom Working Directory

```yaml
- name: Setup PNPM
  uses: ./.github/workflows/setup-pnpm.yml
  with:
    working-directory: 'ui/react_frontend'
```

### Skip Dependency Installation

```yaml
- name: Setup PNPM
  uses: ./.github/workflows/setup-pnpm.yml
  with:
    install-dependencies: false
```

## Best Practices

When using the setup-pnpm workflow:

1. **Specify Versions**: Always specify the Node.js and PNPM versions to ensure consistency
2. **Cache Dependencies**: Use the cache parameter of the actions/setup-node action to cache dependencies
3. **Verify Installation**: Add a step to verify that PNPM is working correctly after setup
4. **Handle Errors**: Add error handling for cases where PNPM setup fails

## Related Documentation

- [Frontend Vitest Testing](../frontend/vitest-framework.md)
- [Frontend E2E Testing](../frontend/e2e-testing.md)
- [CI/CD Pipeline](../ci_cd_pipeline.md)
