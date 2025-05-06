# GitHub Actions Workflow Consolidation

## Overview

This document outlines the consolidation of GitHub Actions workflows to reduce redundancy and improve maintainability. The goal was to reduce the number of workflows while ensuring all functionality is preserved.

## Consolidated Workflow Structure

### Before Consolidation (7 workflows)

1. **ci.yml**: Comprehensive CI workflow with linting and testing
2. **lint-and-test.yml**: Similar to ci.yml but with fewer linting tools
3. **lint_and_quality.yml**: Similar to ci.yml but with additional type checking
4. **run_tests.yml**: Dedicated workflow for running tests only
5. **simple-lint.yml**: Simple linting workflow for manual triggering
6. **act-simple-lint.yml**: Similar to simple-lint.yml but optimized for Act
7. **security_scan.yml**: Specialized workflow for security scanning
8. **deploy.yml**: Workflow for deployment tasks

### After Consolidation (4 workflows)

1. **ci.yml**: Enhanced comprehensive CI workflow
   - Combines functionality from lint-and-test.yml, lint_and_quality.yml, and run_tests.yml
   - Added support for specific file and test path parameters
   - Configurable to run only linting or only tests

2. **local-testing.yml**: Unified local testing workflow
   - Combines functionality from simple-lint.yml and act-simple-lint.yml
   - Supports platform selection (Ubuntu/Windows)
   - Configurable for specific files and test paths

3. **security_scan.yml**: Kept as is (specialized purpose)
   - Maintained separately due to its specialized security scanning functionality

4. **deploy.yml**: Kept as is (specialized purpose)
   - Maintained separately due to its specialized deployment functionality

## Key Improvements

1. **Reduced Redundancy**: Eliminated overlapping workflows that performed similar functions
2. **Enhanced Configurability**: Added parameters to make workflows more flexible
   - Support for specific file testing/linting
   - Support for custom test paths
   - Options to run only linting or only tests
3. **Consistent Tooling**: Ensured all linting and testing tools are consistently applied
4. **Improved Maintainability**: Fewer workflows to maintain and update
5. **Better Documentation**: Added comments and echo statements to improve workflow readability

## Usage Examples

### Running the CI Workflow

```yaml
# Run full CI
name: CI - Lint and Test
on:
  workflow_dispatch:

# Run only linting
name: CI - Lint and Test
on:
  workflow_dispatch:
    inputs:
      lint_only: true

# Run only tests
name: CI - Lint and Test
on:
  workflow_dispatch:
    inputs:
      test_only: true

# Test a specific file
name: CI - Lint and Test
on:
  workflow_dispatch:
    inputs:
      specific_file: path/to/file.py

# Test a specific directory
name: CI - Lint and Test
on:
  workflow_dispatch:
    inputs:
      test_path: tests/specific_module/
```

### Running Local Testing

```yaml
# Run local tests on Ubuntu
name: Local Testing
on:
  workflow_dispatch:

# Run local tests on Windows
name: Local Testing
on:
  workflow_dispatch:
    inputs:
      platform: windows-latest

# Run only linting
name: Local Testing
on:
  workflow_dispatch:
    inputs:
      lint_only: true

# Test a specific file
name: Local Testing
on:
  workflow_dispatch:
    inputs:
      specific_file: path/to/file.py
```

## Workflows to Remove

The following workflows are now redundant and can be removed:

1. **lint-and-test.yml**: Functionality merged into ci.yml
2. **lint_and_quality.yml**: Functionality merged into ci.yml
3. **run_tests.yml**: Functionality merged into ci.yml
4. **simple-lint.yml**: Functionality merged into local-testing.yml
5. **act-simple-lint.yml**: Functionality merged into local-testing.yml
