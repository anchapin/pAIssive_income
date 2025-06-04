# GitHub Actions Workflow Documentation

## Overview

The consolidated CI/CD pipeline provides comprehensive testing, security scanning, and deployment capabilities across multiple platforms.

## Workflow Jobs

### 1. Lint, Type Check, and Test (`lint-test`)
- **Runs on**: Ubuntu, Windows, MacOS
- **Key Steps**:
  - Python setup with version 3.12
  - Dependency caching using uv
  - Virtual environment creation and verification
  - Linting with Ruff
  - Type checking with mypy
  - Testing with pytest (parallel execution)
  - Coverage reporting to Codecov

### 2. Security & SAST (`security`)
- **Runs on**: Ubuntu, Windows, MacOS
- **Tools Used**:
  - Safety: Python package vulnerability scanning
  - Bandit: Python security linting
  - Trivy: Comprehensive vulnerability scanner
  - Semgrep: Pattern-based security analysis
  - pip-audit: Supply chain security
  - Gitleaks: Secrets scanning
  - CodeQL: Advanced security analysis

### 3. Build & Deploy (`build-deploy`)
- **Runs on**: Ubuntu only (for Docker compatibility)
- **Triggers on**:
  - Pushes to main/dev branches
  - Version tags (v*.*.*)
  - Workflow dispatch
- **Features**:
  - Docker layer caching
  - Multi-stage builds
  - Automated version tagging
  - Docker Hub publishing

## Required Secrets

- `DOCKERHUB_USERNAME`: Docker Hub account username
- `DOCKERHUB_TOKEN`: Docker Hub access token (from Docker Hub > Account Settings > Security)

## Permissions

Default permissions are minimal (`contents: read`), with elevated permissions granted only where needed:
- `security-events: write`: For SARIF uploads
- `packages: write`: For Docker publishing
- `id-token: write`: For OIDC cloud authentication

## Key Features

1. **Enhanced Dependency Management**:
   - Uses uv for faster, more reliable dependency installation
   - Implements robust caching strategy
   - Fallback mechanisms for dependency installation

2. **Cross-Platform Testing**:
   - Comprehensive testing across all major operating systems
   - Platform-specific script adaptations
   - Parallel test execution for speed

3. **Security Scanning**:
   - Multiple scanning tools for comprehensive coverage
   - SARIF report generation and upload
   - Automated secret detection and prevention

4. **Deployment Automation**:
   - Automated Docker image building and tagging
   - Conditional deployment based on branch/tag
   - Layer caching for faster builds

## Best Practices

1. **Branch Protection**:
   - Enable branch protection for main/dev branches
   - Require status checks to pass
   - Enforce PR reviews
   - Restrict who can push directly

2. **Secret Management**:
   - Store all credentials as encrypted GitHub secrets
   - Use OIDC where possible for cloud authentication
   - Regular rotation of access tokens

3. **File Management**:
   - .gitignore properly configured
   - Build artifacts excluded from repository
   - Respect file patterns in scan configurations

## Error Handling

- Continues on error for non-critical steps
- Provides detailed logs for debugging
- Uses fallback mechanisms where appropriate
- Implements retry logic for transient failures

## Related Documentation

- [PR #139 Final Summary](PR_139_FINAL_SUMMARY.md) - Complete workflow resolution documentation
- [Workflow Maintenance Guide](WORKFLOW_MAINTENANCE_GUIDE.md) - Ongoing maintenance procedures
- [Workflow Fixes Summary](pr_139_workflow_fixes_summary.md) - Technical implementation details
- [CI Workflow Consolidation](ci_workflow_consolidation.md) - Workflow architecture changes

## Troubleshooting

For common issues and solutions, refer to:
1. **Workflow Maintenance Guide** - Daily monitoring and routine maintenance
2. **PR #139 Final Summary** - Comprehensive fix documentation
3. **GitHub Actions Logs** - Real-time debugging information
4. **Local Testing with Act** - `act -j lint-test --dryrun` for validation
