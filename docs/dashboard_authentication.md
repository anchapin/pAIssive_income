# Dashboard Authentication System

The logging dashboard includes a comprehensive authentication and authorization system to secure access to sensitive log data and dashboard features. This document provides an overview of the authentication system and how to use it.

## Features

- **User Authentication**: Secure login with username and password
- **Role-Based Access Control**: Assign roles to users with specific permissions
- **Permission System**: Fine-grained control over dashboard features
- **CSRF Protection**: Protection against cross-site request forgery attacks
- **Rate Limiting**: Protection against brute force attacks
- **Audit Logging**: Comprehensive logging of security events
- **Session Management**: Secure session handling with expiration

## Configuration

The authentication system can be configured when starting the dashboard using the following command-line arguments:

```bash
python tools/log_dashboard.py --enable-auth [OPTIONS]
```

### Authentication Options

| Option | Description | Default |
|--------|-------------|---------|
| `--enable-auth` | Enable authentication | Disabled |
| `--secret-key` | Secret key for session signing | Random generated |
| `--session-expiry` | Session expiry time in seconds | 3600 (1 hour) |
| `--disable-csrf` | Disable CSRF protection | CSRF enabled |
| `--disable-rate-limit` | Disable rate limiting | Rate limiting enabled |
| `--max-auth-attempts` | Maximum failed authentication attempts | 5 |
| `--lockout-time` | Lockout time in seconds after max failed attempts | 300 (5 minutes) |
| `--disable-audit-logging` | Disable audit logging | Audit logging enabled |

## Default Users and Roles

When authentication is enabled, the following default users are created:

| Username | Password | Role |
|----------|----------|------|
| admin | admin | admin |
| user | user | viewer |

The following default roles are available:

| Role | Description | Permissions |
|------|-------------|------------|
| admin | Administrator role | All permissions |
| viewer | Viewer role | view_logs, view_analytics, view_alerts, view_ml_analysis |
| analyst | Analyst role | view_logs, view_analytics, view_alerts, view_ml_analysis, run_ml_analysis |

## Permissions

The following permissions are available:

| Permission | Description |
|------------|-------------|
| view_logs | View logs |
| view_analytics | View analytics |
| view_alerts | View alerts |
| manage_alerts | Manage alerts |
| view_ml_analysis | View machine learning analysis |
| run_ml_analysis | Run machine learning analysis |
| view_settings | View settings |
| manage_settings | Manage settings |
| manage_users | Manage users |
| manage_roles | Manage roles |

## User Management

The dashboard includes a user management interface that allows administrators to:

- View existing users
- Add new users
- Edit user roles
- Activate/deactivate users
- Delete users

To access the user management interface, click on the "Users" tab in the dashboard navigation.

### Adding a New User

1. Navigate to the "Users" tab
2. Fill in the username and password fields
3. Select one or more roles for the user
4. Click "Add User"

### Managing Roles

The dashboard also includes a role management interface that allows administrators to:

- View existing roles
- Add new roles
- Edit role permissions
- Delete roles

### Audit Logs

The audit logging system records security-related events such as:

- Login attempts (successful and failed)
- Permission checks
- User management actions
- Rate limiting events
- CSRF validation failures

Administrators can view the audit logs in the "Users" tab under the "Audit Logs" section.

## Security Considerations

- Change the default passwords for the admin and user accounts
- Use a strong secret key for session signing
- Consider using HTTPS for production deployments
- Regularly review audit logs for suspicious activity
- Implement proper backup and recovery procedures for user data

## Programmatic Usage

The authentication system can also be used programmatically:

```python
from common_utils.logging.dashboard_auth import (
    DashboardAuth,
    User,
    Role,
    Permission,
    require_auth,
    require_permission,
)

# Create dashboard auth
auth = DashboardAuth(secret_key="your-secret-key")

# Add users
auth.add_user(
    User(
        username="admin",
        password_hash=auth.hash_password("admin_password"),
        roles=["admin"],
    )
)

# Add roles
auth.add_role(
    Role(
        name="admin",
        permissions=["view_logs", "manage_alerts"],
        description="Administrator role",
    )
)

# Protect routes
@app.callback(...)
@require_auth
def protected_callback(...):
    ...

@app.callback(...)
@require_permission("manage_alerts")
def permission_protected_callback(...):
    ...
```

## Troubleshooting

### User Lockout

If a user is locked out due to too many failed authentication attempts, the lockout will automatically expire after the configured lockout time (default: 5 minutes). Alternatively, an administrator can reset the lockout by restarting the dashboard.

### Session Expiry

If a session expires, the user will be redirected to the login page. Sessions expire after the configured session expiry time (default: 1 hour).

### CSRF Validation Failures

If a CSRF validation failure occurs, the user will see an error message. This can happen if the session has expired or if the CSRF token is invalid. The user should refresh the page and try again.
