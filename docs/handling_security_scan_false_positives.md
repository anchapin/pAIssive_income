# Handling Security Scan False Positives

This guide explains how to handle false positives in security scans and how to use the provided tools to fix them.

## Common False Positives

Security scanners often flag patterns that look like sensitive information but are actually safe. Common false positives include:

### 1. Test Files

Test files often contain example credentials, tokens, and other sensitive-looking data that are used for testing purposes only. These are not real credentials and do not pose a security risk.

Files include:
- `tests/api/test_token_management_api.py`
- `tests/api/test_user_api.py`
- `tests/api/test_rate_limiting_api.py`

**Solution**: 
- Add comments to indicate test data: `# Test credential only` or `# Test token only`
- Use the `fix_security_scan_issues.py` script to automatically add these comments
- Consider using dynamic generation of test credentials where possible

### 2. Authentication Code

Files that handle authentication, password resets, and token generation often contain variable names like `password`, `token`, and `secret`. These are not actual credentials but rather variable names used to handle authentication operations.

Files include:
- `users/password_reset.py`
- `users/services.py`
- `users/auth.py`
- `sdk/javascript/paissive_income_sdk/auth.js`

**Solution**: 
- Use clear variable names that indicate the purpose of the variable
- Add comments to explain the purpose of the code
- Consider using a dedicated authentication library

### 3. Validation Code

Client-side validation code often contains variable names and functions related to passwords and other sensitive data. These are not actual credentials but rather code to validate user input.

Files include:
- `ui/react_frontend/src/utils/validation/validators.js`

**Solution**: 
- Use clear variable names that indicate the purpose of the variable
- Add comments to explain the purpose of the code

### 4. Secrets Management Code

Code that manages secrets often contains variable names and functions related to sensitive data. These are not actual credentials but rather code to manage secrets securely.

Files include:
- `common_utils/secrets/cli.py`
- `common_utils/secrets/audit.py`

**Solution**: 
- Use clear variable names that indicate the purpose of the variable
- Add comments to explain the purpose of the code

### 5. Documentation and Examples

Documentation and example files often contain placeholder values for sensitive data. These are not actual credentials but rather examples for users.

Files include:
- `common_utils/secrets/README.md`
- `sdk/javascript/README.md`

**Solution**: 
- Use clearly marked example values
- Add comments to indicate that these are examples

### 6. Generated Files

Generated files like test reports may contain patterns that look like sensitive data but are actually part of the generated code.

Files include:
- `ui/react_frontend/playwright-report/index.html`

**Solution**: 
- Add these files to `.gitignore` if possible
- Otherwise, add them to the allowlist in `.gitleaks.toml`

## Using the Fix Security Scan Issues Script

The `fix_security_scan_issues.py` script helps fix security scan issues by:

1. Adding security scan exclusions to `.gitleaks.toml`
2. Renaming sensitive variable names
3. Adding comments to indicate test data

### Usage

```bash
# Update Gitleaks configuration
python fix_security_scan_issues.py --update-config

# Add comments to indicate test data
python fix_security_scan_issues.py --add-comments

# Rename sensitive variable names
python fix_security_scan_issues.py --rename-variables

# Process specific files
python fix_security_scan_issues.py --specific-files users/password_reset.py users/services.py

# Process scan results
python fix_security_scan_issues.py --scan-results security_scan_results.txt

# Combine options
python fix_security_scan_issues.py --update-config --add-comments --verbose
```

### Command-Line Options

- `--directory`, `-d`: Directory to process (default: current directory)
- `--add-comments`, `-c`: Add comments to indicate test data
- `--rename-variables`, `-r`: Rename sensitive variable names
- `--update-config`, `-u`: Update Gitleaks configuration
- `--verbose`, `-v`: Enable verbose output
- `--specific-files`, `-f`: Specific files to process
- `--scan-results`, `-s`: Path to a file containing security scan results

## Best Practices for Avoiding False Positives

1. **Use Obvious Placeholders**: When examples are needed, use values like `YOUR_API_KEY_HERE` or `example-password-123`
2. **Generate Test Reports in Ignored Directories**: Configure test tools to output reports to directories that are already excluded
3. **Add to .gitignore When Possible**: For build artifacts and generated files, consider adding them to `.gitignore` instead of just excluding them from secret scanning
4. **Regular Maintenance**: Periodically review and clean up exclusion lists to ensure they're not overly broad

## References

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Pre-commit Hooks Documentation](https://pre-commit.com/)
- [Project Security Policy](./secrets_management.md)
