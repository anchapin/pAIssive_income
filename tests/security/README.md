# Security Tests

This directory contains advanced security tests for the pAIssive income platform, focusing on edge cases and complex scenarios that are critical for production readiness.

## Test Categories

### Advanced Authentication Tests

Located in `test_advanced_authentication.py`, these tests cover:

1. **Token Refresh Scenarios**
   - Basic token refresh
   - Refreshing with expired access token but valid refresh token
   - Refreshing with expired refresh token
   - Chaining multiple token refreshes

2. **Concurrent Authentication Attempts**
   - Multiple simultaneous authentication attempts
   - Rate limiting of concurrent authentication attempts

3. **Session Invalidation Propagation**
   - Single session invalidation
   - Invalidation of all user sessions
   - Propagation of session invalidation across services
   - Session invalidation after password change

### Authorization Edge Cases

Located in `test_authorization_edge_cases.py`, these tests cover:

1. **Resource Access During Role Transitions**
   - Basic role transition
   - Role transition with active sessions
   - Access control during role transition process

2. **Inherited Permissions Scenarios**
   - Basic inherited permissions
   - Inherited permissions with overrides
   - Deep role hierarchy inheritance

3. **Temporary Permission Elevation**
   - Basic temporary permission elevation
   - Expiration of temporary elevated permissions
   - Permission elevation with approval workflow

## Running the Tests

You can run these tests using the `run_security_tests_advanced.py` script:

```bash
python run_security_tests_advanced.py
```

## Integration with CI/CD

These tests should be integrated into your CI/CD pipeline to ensure security features are working correctly before deployment. They are particularly important for production readiness as they test edge cases that might not be covered by basic unit tests.

## Extending the Tests

When adding new security features, consider adding corresponding tests in this directory. Focus on edge cases and scenarios that might occur in production environments, especially those related to:

- Authentication and authorization
- Session management
- Permission handling
- Role transitions
- Concurrent access patterns
