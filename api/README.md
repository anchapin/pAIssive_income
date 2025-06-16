# API Service

See the full documentation for API endpoints, authentication, and usage in
[docs/02_developer_guide/06_module_deep_dives/api_gateway.md](../../docs/02_developer_guide/06_module_deep_dives/api_gateway.md).

This module provides RESTful API endpoints for all core services.

## Password Reset Endpoints

The API exposes endpoints for password reset as part of the authentication flow:

- `POST /api/auth/forgot-password`
    - **Body:** `{ "email": "user@example.com" }`
    - Always returns 200 and a generic message, whether or not the email exists.
    - If the email is registered, a password reset token is generated (in-memory for demo) and a reset link would be sent (simulated).

- `POST /api/auth/reset-password`
    - **Body:** `{ "token": "...", "new_password": "..." }`
    - Sets the new password if the token is valid and unexpired.
    - Returns 200 on success, 400 if the token is invalid/expired.

### Testing

These endpoints are covered by `tests/test_auth_reset.py` using pytest.
To run the tests:

```sh
cd api
pytest
```

Tokens and users are in-memory for demonstration; integrate with your database and email system for production.
