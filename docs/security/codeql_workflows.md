# CodeQL Security Analysis Workflows

## Overview

This document describes the CodeQL security analysis workflows implemented in the project. CodeQL is a semantic code analysis engine that helps identify vulnerabilities and coding errors in your codebase. We have implemented platform-specific workflows to ensure comprehensive security analysis across different operating systems.

## Workflow Files

The project includes the following CodeQL workflow files:

1. **codeql.yml**: Base CodeQL workflow that runs on the default runner
2. **codeql-macos.yml**: macOS-specific CodeQL workflow
3. **codeql-ubuntu.yml**: Ubuntu-specific CodeQL workflow
4. **codeql-windows.yml**: Windows-specific CodeQL workflow

## Key Features

### Cross-Platform Analysis

The workflows are designed to run on different platforms to catch platform-specific security issues:

- **macOS**: Identifies security issues specific to macOS environments
- **Ubuntu**: Identifies security issues specific to Linux environments
- **Windows**: Identifies security issues specific to Windows environments

### Multi-Language Support

The workflows analyze both JavaScript/TypeScript and Python code:

- **JavaScript/TypeScript**: Analyzes frontend code and Node.js scripts
- **Python**: Analyzes backend code and utility scripts

### Robust Dependency Installation

The workflows include robust dependency installation with fallback mechanisms:

- **Python Dependencies**: Uses `uv pip` with fallback to regular `pip`
- **JavaScript Dependencies**: Uses `pnpm` for efficient package management

### Caching and Performance Optimization

To improve performance and reduce analysis time:

- **Database Caching**: Caches CodeQL databases between runs
- **Dependency Caching**: Caches dependencies to speed up installation

### Comprehensive Reporting

The workflows generate detailed reports in SARIF format:

- **SARIF Files**: Generated for each language and platform
- **Artifact Upload**: Reports are uploaded as artifacts for later analysis
- **GitHub Security Dashboard**: Results are integrated with GitHub's security dashboard

## Configuration

### CodeQL Configuration Files

The workflows use the following configuration files:

- **.github/codeql/security-os-config.yml**: OS-specific configuration
- **.github/codeql/security-os-macos.yml**: macOS-specific configuration

### Analysis Options

The workflows use the following analysis options:

- **Queries**: `security-and-quality` for comprehensive analysis
- **Languages**: JavaScript/TypeScript and Python
- **Category**: Platform-specific categories for better organization

## Workflow Triggers

The workflows are triggered by:

- **Push**: To main branches
- **Pull Request**: To main branches
- **Schedule**: Weekly for regular security checks
- **Manual**: Through workflow_dispatch for on-demand analysis

## Usage

### Running Manually

To run the CodeQL analysis manually:

1. Go to the Actions tab in the GitHub repository
2. Select the appropriate CodeQL workflow
3. Click "Run workflow"
4. Select the branch to analyze
5. Click "Run workflow"

### Viewing Results

To view the results of the CodeQL analysis:

1. Go to the Security tab in the GitHub repository
2. Select "Code scanning alerts"
3. Review the alerts and their details
4. Filter by language, severity, or other criteria

### Handling False Positives

For information on handling false positives, see [Security Scan False Positives](../security_scan_false_positives.md).

## Integration with CI/CD

The CodeQL workflows are integrated with the CI/CD pipeline:

- **Pre-Merge Checks**: Analysis runs before merging pull requests
- **Regular Scans**: Weekly scans of the main branches
- **Artifact Retention**: Reports are retained for 7 days

## Best Practices

When working with the CodeQL workflows:

1. **Review Alerts Promptly**: Address security alerts as soon as they are identified
2. **Update Dependencies**: Keep dependencies up to date to avoid known vulnerabilities
3. **Add Tests**: Add tests for security fixes to prevent regression
4. **Document Fixes**: Document security fixes in the appropriate documentation

## Related Documentation

- [Security Scanning](../security_scanning.md)
- [Security Scan Guide](../security_scan_guide.md)
- [Security Scan Fix Guide](../security_scan_fix_guide.md)
- [Handling Security Scan False Positives](../handling_security_scan_false_positives.md)
