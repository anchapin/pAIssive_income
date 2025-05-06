# Security Policy

## Supported Versions

The following versions of pAIssive_income are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of pAIssive_income seriously. If you believe you've found a security vulnerability, please follow these steps:

### For Non-Critical Issues

1. **Open a GitHub Issue**: For non-sensitive security issues, you can open a regular GitHub issue with the "security" label.

### For Critical or Sensitive Issues

1. **Do Not Open a Public Issue**: Please do not disclose critical vulnerabilities in public GitHub issues.
2. **Email the Project Maintainer**: Send an email to a.n.chapin@gmail.com with details about the vulnerability.
3. **Include the Following Information**:
   - Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
   - Full paths of source file(s) related to the manifestation of the issue
   - The location of the affected source code (tag/branch/commit or direct URL)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit the issue

## Security Response Process

1. Your report will be acknowledged within 48 hours.
2. We will confirm the vulnerability and determine its impact.
3. We will release a fix as soon as possible, depending on complexity.
4. We will notify you when the fix is released.

## Security Updates

Security updates will be released as part of our regular release cycle or as emergency patches, depending on severity.

## Security-Related Configuration

This project uses several tools to ensure security:

1. **CodeQL Analysis**: Automated code scanning to detect common vulnerabilities.
2. **Bandit**: Python-specific security linter.
3. **Safety**: Checks for known vulnerabilities in dependencies.
4. **Trivy**: Vulnerability scanner for containers and file systems.
5. **Gitleaks**: Secret scanning to prevent credential leaks.

## Best Practices for Contributors

1. **Dependency Management**: Always use the latest stable versions of dependencies.
2. **Code Review**: All code changes undergo security review before merging.
3. **Authentication**: Use strong authentication methods and avoid hardcoding credentials.
4. **Input Validation**: Validate all user inputs to prevent injection attacks.
5. **Error Handling**: Implement proper error handling without exposing sensitive information.

## Security Advisories

We publish security advisories for significant vulnerabilities. You can view them in the "Security" tab of our GitHub repository.

## Acknowledgments

We would like to thank the following individuals who have reported security issues:

(This section will be updated as security researchers contribute)

## Contact

For any questions about this security policy, please contact a.n.chapin@gmail.com.
