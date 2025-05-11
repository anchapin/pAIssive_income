# Security Scan False Positives

This document explains the false positives identified in security scans and how they are being handled in the project.

## Common False Positives

### 1. Test Files

Test files often contain example credentials, tokens, and other sensitive-looking data that are used for testing purposes only. These are not real credentials and do not pose a security risk.

Files include:
- `tests/api/test_token_management_api.py`
- `tests/api/test_user_api.py`

**Solution**: These files are allowlisted in `.gitleaks.toml` and use dynamic generation of test credentials where possible.

### 2. Authentication Code

Files that handle authentication, password resets, and token generation often contain variable names like `password`, `token`, and `secret`. These are not actual credentials but rather variable names used to handle authentication operations.

Files include:
- `users/password_reset.py`
- `users/services.py`
- `users/auth.py`
- `sdk/javascript/paissive_income_sdk/auth.js`

**Solution**: These files are allowlisted in `.gitleaks.toml` and use secure coding practices to handle sensitive information.

### 3. Validation Code

Client-side validation code often contains variable names and functions related to passwords and other sensitive data. These are not actual credentials but rather code to validate user input.

Files include:
- `ui/react_frontend/src/utils/validation/validators.js`

**Solution**: These files are allowlisted in `.gitleaks.toml` and use secure coding practices.

### 4. Secrets Management Code

Code that manages secrets often contains variable names and functions related to sensitive data. These are not actual credentials but rather code to manage secrets securely.

Files include:
- `common_utils/secrets/cli.py`
- `common_utils/secrets/audit.py`

**Solution**: These files are allowlisted in `.gitleaks.toml` and use secure coding practices.

### 5. Documentation and Examples

Documentation and example files often contain placeholder values for sensitive data. These are not actual credentials but rather examples for users.

Files include:
- `common_utils/secrets/README.md`
- `sdk/javascript/README.md`

**Solution**: These files are allowlisted in `.gitleaks.toml` and use clearly marked example values.

### 6. Generated Files

Generated files like test reports may contain patterns that look like sensitive data but are actually part of the generated code.

Files include:
- `ui/react_frontend/playwright-report/index.html`

**Solution**: These files are allowlisted in `.gitleaks.toml` and excluded from security scans.

## Handling False Positives

To handle false positives in security scans, we use the following approaches:

1. **Allowlisting**: Files and patterns that are known to be false positives are allowlisted in `.gitleaks.toml`.

2. **Dynamic Generation**: Where possible, we use dynamic generation of test credentials instead of hardcoded values.

3. **Secure Coding Practices**: We use secure coding practices to handle sensitive information, such as:
   - Not logging sensitive information
   - Using environment variables for secrets
   - Using secure storage for secrets
   - Using proper authentication and authorization

4. **Documentation**: We document false positives and how they are being handled.

## Reporting Real Security Issues

If you discover a real security issue in the codebase, please follow the guidelines in `SECURITY.md` to report it responsibly.
