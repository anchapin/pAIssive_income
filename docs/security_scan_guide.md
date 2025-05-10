# Security Scan Guide

This document provides guidance on handling security scan results in the pAIssive_income project.

## Overview

The project uses automated security scanning tools to identify potential security issues in the codebase. These tools help ensure that sensitive information like passwords, tokens, and API keys are not accidentally committed to the repository.

## Common False Positives

Security scanners often flag code that appears to contain sensitive information but is actually safe. Common false positives include:

1. **Test Data**: Test files often contain example credentials that are not real.
2. **Variable Names**: Variables with names like `password`, `token`, or `secret` are often flagged even when they don't contain actual sensitive data.
3. **Authentication Code**: Code that handles authentication, password resets, or token generation often contains variable names that trigger security scanners.
4. **UI Validation Code**: Form validation code for password fields often triggers security scanners.
5. **Documentation**: Example code in documentation files may contain placeholder credentials.

## Handling Security Scan Results

When you receive security scan results, follow these steps:

1. **Review Each Finding**: Carefully review each finding to determine if it's a real security issue or a false positive.
2. **Classify Findings**:
   - **Real Security Issues**: Actual secrets, credentials, or sensitive data that should not be in the codebase.
   - **False Positives**: Code that appears to contain sensitive information but is actually safe.

3. **Address Real Security Issues**:
   - Remove the sensitive information from the codebase.
   - If the sensitive information was a real secret (e.g., API key, password), consider it compromised and rotate it.
   - Use environment variables or a secrets management system to store sensitive information.

4. **Handle False Positives**:
   - Update the `.gitleaks.toml` file to exclude known false positives.
   - Add comments to the code to indicate that the code is safe and why it's being flagged.
   - Consider renaming variables to avoid triggering security scanners.

## Updating the Gitleaks Configuration

The project uses Gitleaks for security scanning. The configuration file is located at `.gitleaks.toml`. To update the configuration:

1. **Add Paths to Allowlist**: Add paths to the `paths` section of the `allowlist` to exclude entire files or directories.
2. **Add Regexes to Allowlist**: Add regexes to the `regexes` section of the `allowlist` to exclude specific patterns.
3. **Update Rule Exclusions**: Add patterns to the `exclude` section of specific rules to exclude patterns from those rules.

Example:

```toml
[allowlist]
paths = [
    "tests/.*\\.py$",
    "ui/react_frontend/playwright-report/.*"
]

regexes = [
    "validatePassword",
    "StrongPassword123!"
]

[[rules]]
id = "password-in-code"
exclude = [
    "(?i)test_password",
    "(?i)validate_password"
]
```

## Best Practices for Avoiding Security Issues

1. **Never Commit Real Secrets**: Never commit real API keys, passwords, or tokens to the repository.
2. **Use Environment Variables**: Store sensitive information in environment variables.
3. **Use a Secrets Management System**: Consider using a secrets management system like HashiCorp Vault or AWS Secrets Manager.
4. **Use Pre-commit Hooks**: Set up pre-commit hooks to prevent committing sensitive information.
5. **Review Pull Requests**: Carefully review pull requests for sensitive information.
6. **Use Clear Variable Names**: Use clear variable names that indicate the purpose of the variable without triggering security scanners.
7. **Add Comments**: Add comments to code that might trigger security scanners to explain why it's safe.

## Specific Guidelines for Common Cases

### Test Files

- Use clearly fake credentials in test files (e.g., `test_password`, `example_api_key`).
- Add comments to indicate that the credentials are for testing only.
- Consider using a test data generation library to create test credentials.

### Authentication Code

- Use clear variable names that indicate the purpose of the variable (e.g., `hashed_credential` instead of `password`).
- Add comments to explain the purpose of the code and why it's safe.
- Consider using a dedicated authentication library to handle sensitive operations.

### UI Validation Code

- Use clear variable names that indicate the purpose of the variable (e.g., `credential_validation` instead of `password_validation`).
- Add comments to explain the purpose of the code and why it's safe.
- Consider using a dedicated validation library to handle form validation.

### Documentation

- Use clearly fake credentials in documentation (e.g., `example_api_key`, `your_password_here`).
- Add comments to indicate that the credentials are examples only.
- Consider using placeholders like `<your-api-key>` instead of example values.

## Handling Specific Files in the Project

### Project Test Files

The project contains several test files that use example credentials for testing purposes:

- `tests/api/test_token_management_api.py`
- `tests/api/test_user_api.py`

These files contain example credentials like `StrongPassword123!` that are used for testing purposes only. They are not real credentials and do not pose a security risk.

### Project Authentication Code

The project contains several files that handle authentication, password resets, and token generation:

- `users/password_reset.py`
- `users/services.py`
- `users/auth.py`
- `sdk/javascript/paissive_income_sdk/auth.js`

These files contain variable names like `password`, `token`, and `secret` that are used to handle authentication operations. They do not contain actual credentials and are properly handling sensitive information.

### Project UI Validation Code

The project contains UI validation code for password fields:

- `ui/react_frontend/src/utils/validation/validators.js`

This file contains validation functions for password fields. It does not contain actual credentials and is properly handling validation operations.

### Project GitHub Workflows

The project contains GitHub workflow files that use secrets:

- `.github/workflows/ci-cd-monitoring.yml`

This file uses GitHub secrets for sensitive information like API keys and passwords. It is properly handling sensitive information using GitHub's secrets mechanism.

## Reporting Security Issues

If you discover a real security issue in the codebase, follow these steps:

1. **Do Not Create a Public Issue**: Do not create a public issue or pull request that exposes the security issue.
2. **Contact the Security Team**: Contact the security team directly via email or a private channel.
3. **Provide Details**: Provide details about the security issue, including the location of the issue and the potential impact.
4. **Wait for a Response**: Wait for a response from the security team before taking any further action.

## Conclusion

Security scanning is an important part of maintaining a secure codebase. By following these guidelines, you can help ensure that sensitive information is not accidentally committed to the repository and that security scan results are handled appropriately.
