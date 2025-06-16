# GitHub Workflows

This document provides an overview of the GitHub Actions workflows used in the pAIssive_income project.

## Overview

GitHub Actions workflows automate various aspects of the development lifecycle, including testing, security scanning, and deployment. The workflows are defined in YAML files in the `.github/workflows/` directory.

## Workflow Files

### CodeQL Analysis

The following workflows are used for CodeQL security analysis:

1. **codeql.yml**: Main CodeQL workflow for security analysis
2. **codeql-ubuntu.yml**: CodeQL workflow for Ubuntu environments
3. **codeql-macos.yml**: CodeQL workflow for macOS environments
4. **codeql-windows.yml**: CodeQL workflow for Windows environments

These workflows scan the codebase for security vulnerabilities using GitHub's CodeQL analysis engine. They run on different operating systems to ensure comprehensive coverage.

#### Configuration

The CodeQL workflows are configured using the `.github/scripts/ensure_codeql_configs.py` script, which ensures that the CodeQL configuration is consistent across all workflows.

### CI/CD Pipeline

1. **consolidated-ci-cd.yml**: Main CI/CD workflow that runs tests, linting, and other checks

This workflow is triggered on push and pull request events and runs a series of jobs to validate the codebase, including:

- Running tests
- Linting code
- Checking documentation
- Building and testing Docker images

### Docker Compose Workflows

1. **docker-compose-workflow.yml**: Workflow for testing Docker Compose setup
2. **docker-compose.yml**: Workflow for building and testing Docker Compose services

These workflows ensure that the Docker Compose configuration works correctly across different environments and that all services can be built and run successfully.

## Recent Updates

### PR #193 (mem0 Integration)

As part of PR #193, the following workflow files were updated:

1. **codeql.yml**: Updated to include mem0-related files in security scanning
2. **codeql-ubuntu.yml**, **codeql-macos.yml**, **codeql-windows.yml**: Updated for consistency
3. **consolidated-ci-cd.yml**: Added mem0 integration tests
4. **docker-compose-workflow.yml**, **docker-compose.yml**: Updated to include mem0 services

These updates ensure that the mem0 integration is properly tested and secured as part of the CI/CD pipeline.

## Running Workflows Locally

You can run GitHub Actions workflows locally using [act](https://github.com/nektos/act):

```bash
# Run the entire CI/CD workflow
act

# Run a specific job
act -j lint

# Run a specific workflow
act -W .github/workflows/consolidated-ci-cd.yml
```

## Troubleshooting

If a workflow fails, check the following:

1. **Workflow Logs**: Review the logs in the GitHub Actions tab
2. **Local Testing**: Run the workflow locally using act
3. **Configuration**: Verify that the workflow configuration is correct
4. **Dependencies**: Ensure that all dependencies are installed and up to date

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [act Documentation](https://github.com/nektos/act)
