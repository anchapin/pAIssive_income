# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the pAIssive Income project.

## Overview

The CI/CD pipeline automates the process of testing, building, and deploying the application. It is implemented using GitHub Actions and consists of the following stages:

1. **Lint**: Check code quality and style
2. **Test**: Run automated tests
3. **Security Scan**: Perform security analysis
4. **Build**: Build Docker image
5. **Deploy to Staging**: Deploy to staging environment (for develop branch)
6. **Deploy to Production**: Deploy to production environment (for main branch)

## Workflow File

The CI/CD pipeline is defined in the `.github/workflows/ci-cd.yml` file. This file contains the configuration for all stages of the pipeline.

## Stages

### Lint

The lint stage checks the code quality and style using the following tools:

- **fix_linting_issues.py**: Our custom script that automatically fixes common linting issues
- **flake8**: Checks for syntax errors and style issues
- **ruff**: Fast Python linter that finds and fixes issues (including formatting)
- **mypy**: Checks type annotations

The `fix_linting_issues.py` script is a comprehensive tool that uses Ruff to automatically fix common linting issues. It is run as part of the CI/CD pipeline to ensure code quality and consistency.

### Test

The test stage runs automated tests using pytest and generates a coverage report. The coverage report is uploaded to Codecov for tracking code coverage over time.

### Security Scan

The security scan stage performs security analysis using the following tools:

- **bandit**: Checks for common security issues in Python code
- **safety**: Checks for known vulnerabilities in dependencies

### Build

The build stage builds a Docker image for the application and pushes it to Docker Hub. This stage only runs on pushes to the main and develop branches.

### Deploy to Staging

The deploy to staging stage deploys the application to the staging environment. This stage only runs on pushes to the develop branch.

### Deploy to Production

The deploy to production stage deploys the application to the production environment. This stage only runs on pushes to the main branch.

## Environments

The CI/CD pipeline uses the following environments:

- **Staging**: Used for testing changes before they are deployed to production
- **Production**: The live environment used by end users

## Secrets

The CI/CD pipeline requires the following secrets to be configured in GitHub:

- **DOCKERHUB_USERNAME**: Docker Hub username
- **DOCKERHUB_TOKEN**: Docker Hub access token
- **STAGING_HOST**: Hostname of the staging server
- **STAGING_USERNAME**: Username for SSH access to the staging server
- **STAGING_SSH_KEY**: SSH private key for access to the staging server
- **PRODUCTION_HOST**: Hostname of the production server
- **PRODUCTION_USERNAME**: Username for SSH access to the production server
- **PRODUCTION_SSH_KEY**: SSH private key for access to the production server

## Branching Strategy

The CI/CD pipeline is designed to work with the following branching strategy:

- **main**: The production branch. Changes to this branch are deployed to the production environment.
- **develop**: The development branch. Changes to this branch are deployed to the staging environment.
- **feature/\***: Feature branches. These branches are used for developing new features and are merged into the develop branch when ready.
- **bugfix/\***: Bugfix branches. These branches are used for fixing bugs and are merged into the develop branch when ready.
- **hotfix/\***: Hotfix branches. These branches are used for critical fixes and are merged into both the main and develop branches when ready.

## Workflow

1. Developers create feature, bugfix, or hotfix branches from the develop branch
2. When changes are ready, a pull request is created to merge the branch into the develop branch
3. The CI/CD pipeline runs on the pull request to check code quality, run tests, and perform security analysis
4. If all checks pass, the pull request can be merged
5. When the changes are merged into the develop branch, the CI/CD pipeline builds a Docker image and deploys it to the staging environment
6. After testing in the staging environment, a pull request is created to merge the develop branch into the main branch
7. When the changes are merged into the main branch, the CI/CD pipeline builds a Docker image and deploys it to the production environment

## Monitoring

The CI/CD pipeline includes monitoring to ensure that deployments are successful:

- **GitHub Actions**: Provides logs and status for each stage of the pipeline
- **Docker Hub**: Stores and provides access to Docker images
- **Codecov**: Tracks code coverage over time
- **Server Logs**: Provide information about the deployment and running application

## Troubleshooting

If a stage of the CI/CD pipeline fails, check the logs in GitHub Actions for more information. Common issues include:

- **Lint Failures**: Code style or quality issues
- **Test Failures**: Failing tests
- **Security Scan Failures**: Security vulnerabilities
- **Build Failures**: Issues with building the Docker image
- **Deployment Failures**: Issues with deploying to the staging or production environment
