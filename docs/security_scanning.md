# Security Scanning Workflow

This document provides an overview of the security scanning workflow in the CI/CD pipeline and how to troubleshoot common issues.

## Overview

The security scanning workflow is part of the consolidated CI/CD pipeline and is defined in the `.github/workflows/consolidated-ci-cd.yml` file. It includes several security scanning tools to identify vulnerabilities in the codebase and dependencies.

## Security Scanning Tools

The workflow uses the following security scanning tools:

1. **pip-audit**: Scans Python dependencies for known vulnerabilities.
2. **Safety**: Another tool for scanning Python dependencies for vulnerabilities.
3. **Bandit**: Static analysis tool designed to find common security issues in Python code.
4. **Trivy**: Comprehensive vulnerability scanner for containers and file systems.
5. **Semgrep**: Static analysis tool that can find security issues using pattern matching.
6. **Pylint**: Used with security-focused rules to identify security issues in Python code.
7. **Gitleaks**: Scans for secrets and credentials in the codebase.

## Workflow Steps

The security scanning workflow consists of the following steps:

1. **Setup**: Checkout code, set up Python, and create a virtual environment.
2. **Install Security Tools**: Install all security scanning tools using uv or pip.
3. **Run Security Scans**: Run each security scanning tool and generate reports.
4. **Upload Reports**: Upload security reports as artifacts and to GitHub Security.

## Troubleshooting

### Common Issues

#### 1. Tool Installation Failures

If security tools fail to install, the workflow includes fallback mechanisms:

- First, it tries to install tools using `uv pip`.
- If that fails, it falls back to using `python -m pip`.
- For each tool, it verifies the installation and tries alternative methods if needed.

#### 2. pip-audit Command Not Found

If the `pip-audit` command is not found, the workflow:

1. Checks for the command in various locations.
2. Tries to locate the `pip_audit` module and create a wrapper script.
3. Falls back to running `python -m pip_audit` if possible.
4. Creates an empty results file if all methods fail.

#### 3. Invalid SARIF Files

If SARIF files are invalid or missing, the workflow:

1. Checks if the file exists and has the required "version" property.
2. Verifies that the file is valid JSON.
3. Creates a valid empty SARIF file if needed.

### Manual Verification

To manually verify that security tools are installed and working:

```bash
# Verify pip-audit installation
which pip-audit
python -c "import pip_audit"

# Verify safety installation
which safety
safety check --help

# Verify bandit installation
which bandit
bandit --help

# Verify semgrep installation
which semgrep
semgrep --help

# Verify pylint installation
which pylint
pylint --help
```

### Running Security Scans Locally

You can run security scans locally to troubleshoot issues:

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install security tools
pip install pip-audit safety bandit semgrep pylint

# Run pip-audit
pip-audit

# Run safety
safety check

# Run bandit
bandit -r .

# Run semgrep
semgrep scan --config=auto

# Run pylint security checks
pylint --disable=all --enable=security .
```

## Customizing Security Scans

### Adding New Security Tools

To add a new security tool to the workflow:

1. Add the tool to the installation step in the workflow.
2. Add a new step to run the tool and generate a report.
3. Update the upload steps to include the new report.

### Configuring Existing Tools

Each security tool can be configured to meet the specific needs of the project:

- **pip-audit**: Configure with command-line options like `--format`, `--output`, etc.
- **Safety**: Configure with command-line options like `--full-report`, `--ignore`, etc.
- **Bandit**: Configure with command-line options or a `.bandit` configuration file.
- **Semgrep**: Configure with command-line options or a `.semgrep.yml` configuration file.
- **Pylint**: Configure with command-line options or a `.pylintrc` configuration file.

## Interpreting Security Reports

The security reports are uploaded as artifacts and can be downloaded from the GitHub Actions workflow run. They provide information about vulnerabilities found in the codebase and dependencies.

### SARIF Reports

SARIF (Static Analysis Results Interchange Format) reports are used by GitHub Security to display security issues in the Security tab. They include:

- **Rule ID**: Identifier for the rule that was violated.
- **Message**: Description of the vulnerability.
- **Location**: File and line number where the vulnerability was found.
- **Severity**: Severity level of the vulnerability (Critical, High, Medium, Low).

### JSON Reports

JSON reports from tools like pip-audit and safety include:

- **Package Name**: Name of the vulnerable package.
- **Installed Version**: Currently installed version of the package.
- **Vulnerable Version**: Version range that is vulnerable.
- **Description**: Description of the vulnerability.
- **Fix Version**: Version that fixes the vulnerability.

## Conclusion

The security scanning workflow is designed to be robust and handle failures gracefully. It includes fallback mechanisms for tool installation and execution, ensuring that the workflow can complete even if some tools fail.

If you encounter issues with the security scanning workflow, please refer to the troubleshooting section or open an issue in the GitHub repository.
