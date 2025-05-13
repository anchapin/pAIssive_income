# DevOps & CI/CD Workflow

This document provides an overview of the DevOps and CI/CD workflows used in the pAIssive Income project.

## Overview

Our DevOps workflow is designed to automate the development, testing, and deployment processes, ensuring consistent quality and reliability. We use GitHub Actions for continuous integration and continuous deployment, with a focus on code quality, testing, and security.

## CI/CD Pipeline

Our CI/CD pipeline automates the process of testing, building, and deploying the application. It consists of the following stages:

1. **Lint**: Check code quality and style
2. **Test**: Run automated tests
3. **Security Scan**: Perform security analysis
4. **Documentation Check**: Ensure code changes are accompanied by documentation updates
5. **Build**: Build Docker image
6. **Deploy to Staging**: Deploy to staging environment (for develop branch)
7. **Deploy to Production**: Deploy to production environment (for main branch)

For detailed information about our CI/CD pipeline, see [CI/CD Pipeline](ci_cd_pipeline.md).

## Docker Compose Workflows

We use Docker Compose for local development and testing, as well as in our CI/CD pipeline. Our Docker Compose workflows are designed to be robust and reliable, with comprehensive error handling, health checks, and resource management.

### Docker Compose in GitHub Actions

We have two main Docker Compose workflows:

1. **docker-compose-integration.yml**: A comprehensive workflow for Docker Compose integration testing with robust error handling, health checks, and disk space management.
2. **docker-compose-alternative.yml**: An alternative approach using Docker's official GitHub Action with improved health checks.

For detailed information about using Docker Compose in GitHub Actions, see:

- [Docker Compose in GitHub Actions](github-actions-docker-compose.md)
- [Docker Compose Workflows](docker-compose-workflows.md)
- [Docker Build and Push Action Update](docker-build-push-action-update.md)

## Setup Workflows

We have several workflows for setting up development environments and dependencies:

### PNPM Setup

We use PNPM as our package manager for JavaScript dependencies. Our PNPM setup workflow is designed to be reusable across multiple workflows, providing consistent setup across different environments.

For detailed information about our PNPM setup workflow, see [Setup PNPM Workflow](ci_cd/setup-pnpm.md).

### Development Environment Setup

We have a workflow for testing our development environment setup scripts, ensuring they work correctly across different platforms and configurations.

For detailed information about our development environment setup workflow, see [Test Setup Script Workflow](ci_cd/test-setup-script.md).

## Security Scanning

We have a comprehensive security scanning workflow that includes:

1. **CodeQL Analysis**: Static code analysis to find security vulnerabilities
2. **Trivy**: Scanning for vulnerabilities in dependencies and container images
3. **Gitleaks**: Detecting secrets in the codebase
4. **Bandit**: Python-specific security scanning
5. **Pylint**: Security-specific linting

For detailed information about our security scanning workflows, see:

- [Security Overview](security.md)
- [CodeQL Workflows](security/codeql_workflows.md)
- [Security Scanning](security_scanning.md)
- [Security Scan Guide](security_scan_guide.md)

## Best Practices

Based on our experience with DevOps and CI/CD workflows, we recommend the following best practices:

1. **Automate Everything**: Automate as much of the development, testing, and deployment process as possible
2. **Use Reusable Workflows**: Create reusable workflows for common tasks to reduce duplication
3. **Implement Robust Error Handling**: Include comprehensive error handling and fallback mechanisms
4. **Monitor Resources**: Proactively monitor and manage resources throughout the workflow
5. **Provide Detailed Diagnostics**: Include comprehensive logging and diagnostics for troubleshooting
6. **Implement Health Checks**: Use comprehensive health checks with multiple verification methods
7. **Clean Up Resources**: Ensure resources are cleaned up even if the workflow fails
8. **Use Official Actions**: Leverage official GitHub Actions for the most reliable setup
9. **Pin Action Versions**: Pin action versions to ensure consistent behavior
10. **Document Everything**: Provide detailed documentation for all workflows and processes

## Troubleshooting

If you encounter issues with our DevOps or CI/CD workflows, check the following:

1. **GitHub Actions Logs**: Check the logs in GitHub Actions for detailed information about the failure
2. **Resource Constraints**: Check if the workflow is failing due to resource constraints (e.g., disk space, memory)
3. **Network Issues**: Check if the workflow is failing due to network issues (e.g., timeouts, connection failures)
4. **Configuration Issues**: Check if the workflow is failing due to configuration issues (e.g., missing secrets, incorrect paths)
5. **Dependency Issues**: Check if the workflow is failing due to dependency issues (e.g., version conflicts, missing dependencies)

For more detailed troubleshooting information, see [Troubleshooting](troubleshooting.md).

## Related Documentation

- [CI/CD Pipeline](ci_cd_pipeline.md)
- [Documentation Check Workflow](documentation-check-workflow.md)
- [Docker Compose in GitHub Actions](github-actions-docker-compose.md)
- [Docker Compose Workflows](docker-compose-workflows.md)
- [Docker Build and Push Action Update](docker-build-push-action-update.md)
- [Setup PNPM Workflow](ci_cd/setup-pnpm.md)
- [Test Setup Script Workflow](ci_cd/test-setup-script.md)
- [Security Overview](security.md)
- [CodeQL Workflows](security/codeql_workflows.md)
- [Security Scanning](security_scanning.md)
- [Security Scan Guide](security_scan_guide.md)
- [Troubleshooting](troubleshooting.md)
- [Containerization Guide](containerization.md)
- [Container Deployment Guide](container-deployment.md)
- [Deployment Architecture](deployment-architecture.md)
