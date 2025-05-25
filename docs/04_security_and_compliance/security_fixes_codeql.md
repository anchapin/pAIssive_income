# Security Fixes for CodeQL Alerts

## Issues Identified

The CodeQL security scan identified 5 high severity security vulnerabilities related to clear-text logging of sensitive information in `common_utils/secrets/secrets_manager.py`:

1. Line 238: `logger.exception(f"Invalid backend specified: {backend}")`
2. Line 307: `logger.error(f"Unsupported backend type: {backend_type}")`
3. Line 341: `logger.exception(f"Invalid backend specified: {backend}")`
4. Line 407: `logger.error(f"Unsupported backend type: {backend_type}")`
5. Line 438: `logger.exception(f"Invalid backend specified: {backend}")`

## Fixes Applied

### 1. Removed sensitive data from error logging

Changed all instances where backend or backend_type values were being logged directly in error messages to use generic messages instead:

```python
# Before
logger.exception(f"Invalid backend specified: {backend}")

# After
# Don't log the actual backend value as it might contain sensitive information
logger.exception("Invalid backend specified")
```

```python
# Before
logger.error(f"Unsupported backend type: {backend_type}")

# After
# Don't log the actual backend type as it might contain sensitive information
logger.error("Unsupported backend type")
```

### 2. Removed sensitive data from debug logging

Changed all instances where backend_str values were being logged in debug messages:

```python
# Before
backend_str: str = backend_enum.value
logger.debug(f"Getting secret from {backend_str} backend")

# After
# Don't log the actual backend as it might reveal sensitive information
logger.debug("Getting secret from backend")
```

### 3. Fixed other potential leaks

Also fixed similar issues in other logging statements:

```python
# Before
logger.warning(f"{backend_type.value} backend not yet fully implemented")

# After
# Don't log the actual backend type value as it might contain sensitive information
logger.warning("Backend not yet fully implemented")
```

```python
# Before
logger.exception(f"Error setting secret in {backend_type.value} backend")

# After
# Don't log the actual backend type value as it might contain sensitive information
logger.exception("Error setting secret in backend")
```

## Conclusion

These changes ensure that sensitive information is not logged in clear text. The fixes include:

1. Removing potentially sensitive backend identifiers from log messages
2. Using generic messages instead of including sensitive data
3. Adding clear comments explaining the security considerations

These changes should resolve the CodeQL security vulnerabilities identified in the scan.
