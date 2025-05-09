# GitHub Actions Artifact Upload Issue Resolution

## Issue Description

The GitHub Actions workflow was encountering an error during the artifact upload process:
```
Missing download info for actions/upload-artifact@v3
```

This error typically occurs when:
- The artifact upload action is unable to locate or access the specified directory
- There are version compatibility issues with the actions/upload-artifact action
- The target directory for artifacts doesn't exist when the upload is attempted

## Solution Steps

### 1. Version Update
Updated the actions/upload-artifact version from v3 to v3.1.1 to resolve potential version-specific issues.

### 2. Directory Verification
Added explicit directory creation step before the artifact upload to ensure the target directory exists:

```yaml
- name: Create playwright-report directory
  if: always()
  run: mkdir -p playwright-report

- name: Upload Playwright report
  if: always()
  uses: actions/upload-artifact@v3.1.1
  with:
    name: playwright-report
    path: playwright-report/
    retention-days: 30
```

## Recommended Implementation

Complete workflow snippet with all fixes applied:

```yaml
name: Frontend E2E Tests

on:
  push:
    paths:
      - 'ui/react_frontend/**'
  pull_request:
    paths:
      - 'ui/react_frontend/**'

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci
        working-directory: ./ui/react_frontend

      - name: Install Playwright browsers
        run: npx playwright install --with-deps
        working-directory: ./ui/react_frontend

      - name: Run Playwright tests
        run: npx playwright test
        working-directory: ./ui/react_frontend

      - name: Create playwright-report directory
        if: always()
        run: mkdir -p playwright-report
        working-directory: ./ui/react_frontend

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3.1.1
        with:
          name: playwright-report
          path: ui/react_frontend/playwright-report/
          retention-days: 30
```

Key implementation points:
1. Always create the report directory before upload attempt
2. Use latest patch version (v3.1.1) of upload-artifact action
3. Ensure proper path mapping between working directory and artifact upload path
4. Include directory creation and upload steps in `if: always()` block to capture reports even on test failure
