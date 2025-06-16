# Developer Security Guide

## Quick Security Checklist for Developers

This guide provides essential security patterns and practices to follow when contributing to the codebase.

## 🔒 Logging Security

### ✅ DO: Use Generic Error Messages
```python
# Good - No sensitive information exposed
logger.exception("Invalid backend specified")
logger.error("Authentication failed")
logger.warning("Configuration error detected")
```

### ❌ DON'T: Log Sensitive Information
```python
# Bad - Exposes sensitive data
logger.exception(f"Invalid backend specified: {backend}")
logger.error(f"Authentication failed for user: {username}")
logger.warning(f"API key invalid: {api_key}")
```

### Pattern: Secure Error Logging
```python
try:
    # Some operation with sensitive data
    result = process_sensitive_data(secret_value)
except Exception:
    # Don't log the actual sensitive value
    logger.exception("Error processing sensitive data")
    # Add comment explaining security consideration
    # Don't log the actual value as it might contain sensitive information
```

## 🔐 Secrets Management

### ✅ DO: Use Environment Variables
```python
import os
api_key = os.getenv("API_KEY")
if not api_key:
    logger.error("API key not configured")
    return None
```

### ❌ DON'T: Hardcode Secrets
```python
# Bad - Never hardcode secrets
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:password@host/db"
```

### Pattern: Safe Secret Handling
```python
from common_utils.secrets.secrets_manager import get_secret

def get_api_credentials():
    """Get API credentials safely."""
    try:
        api_key = get_secret("API_KEY")
        if not api_key:
            logger.warning("API key not found in secrets manager")
            return None
        return api_key
    except Exception:
        # Don't log the actual error details that might contain sensitive info
        logger.exception("Failed to retrieve API credentials")
        return None
```

## 🛡️ Input Validation

### ✅ DO: Validate All External Input
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    username: str
    email: str
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v.strip()
```

### ❌ DON'T: Trust External Input
```python
# Bad - No validation
def process_user_data(data):
    username = data['username']  # Could be None, empty, or malicious
    return f"Hello {username}"   # Potential injection risk
```

## 🔍 CodeQL Best Practices

### Configuration Guidelines
- Always use `.codeqlignore` to exclude third-party code
- Use `security-and-quality` query suites for comprehensive coverage
- Maintain consistent category naming across workflows
- Document any query exclusions with clear reasoning

### Security Patterns
- Generic error messages for security-sensitive operations
- No sensitive data in log statements
- Proper exception handling without information leakage
- Clear comments explaining security considerations

## 📝 Documentation Requirements

### Security Comments
Always add comments explaining security decisions:
```python
# Don't log the actual backend value as it might contain sensitive information
logger.exception("Invalid backend specified")

# Use generic message to avoid exposing system internals
logger.error("Authentication failed")
```

### Change Documentation
When making security-related changes:
1. Document the security rationale
2. Update relevant security documentation
3. Add comments in the code explaining the approach
4. Include security considerations in PR descriptions

## 🚀 Pre-Commit Checklist

Before submitting a PR, verify:
- [ ] No hardcoded secrets or credentials
- [ ] All logging uses generic, security-safe messages
- [ ] Input validation implemented for external data
- [ ] Security comments added where appropriate
- [ ] No sensitive information in error messages
- [ ] Configuration files follow established patterns

## 🔧 Tools and Validation

### Local Security Checks
```bash
# Check for potential secrets
git secrets --scan

# Validate YAML configuration
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/codeql.yml'))"

# Run security linting
bandit -r . -f json -o bandit-results.json
```

### CodeQL Local Testing
```bash
# Install CodeQL CLI (if available)
codeql database create --language=python python-db
codeql database analyze python-db --format=sarif-latest --output=results.sarif
```

## 📚 Additional Resources

- [Security Overview](01_security_overview.md)
- [Secrets Management](03_secrets_management.md)
- [Input Validation Standards](04_input_validation_standards.md)
- [PR #243 CodeQL Fixes](../../PR243_CODEQL_FIXES_SUMMARY.md)

## 🆘 Getting Help

If you're unsure about security implications:
1. Review existing security patterns in the codebase
2. Check the security documentation
3. Ask for security review in your PR
4. Consult the security team for complex scenarios

Remember: **When in doubt, err on the side of caution and use generic messages.**
