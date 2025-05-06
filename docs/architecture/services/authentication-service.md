# Authentication Service Design

## Overview

The Authentication Service handles user authentication, authorization, and identity management for the pAIssive income platform. It provides secure access control, manages user credentials, and issues tokens for authenticated sessions across all microservices.

## Responsibilities

- User registration and management
- Authentication and login processing
- Authorization and access control
- Token issuance and validation
- Password management and reset workflows
- Multi-factor authentication (MFA)
- Session management
- Role-based access control (RBAC)
- OAuth integration for third-party authentication
- Audit logging of security events

## API Design

### External API (Service-to-Service)

#### User Management
- `POST /api/auth/users` - Create a new user
- `GET /api/auth/users` - List all users (admin only)
- `GET /api/auth/users/{id}` - Get a specific user
- `PUT /api/auth/users/{id}` - Update a user
- `DELETE /api/auth/users/{id}` - Delete a user
- `GET /api/auth/users/me` - Get current user profile

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/token/refresh` - Refresh access token
- `POST /api/auth/password/reset-request` - Request a password reset
- `POST /api/auth/password/reset` - Reset password with token
- `POST /api/auth/mfa/enable` - Enable multi-factor authentication
- `POST /api/auth/mfa/verify` - Verify MFA code
- `POST /api/auth/oauth/{provider}` - Authenticate with OAuth provider

#### Authorization
- `POST /api/auth/token/validate` - Validate an access token
- `GET /api/auth/permissions/{resource}` - Get user permissions for a resource
- `GET /api/auth/roles` - List all roles
- `POST /api/auth/roles` - Create a new role
- `PUT /api/auth/roles/{role_id}` - Update a role
- `GET /api/auth/users/{id}/roles` - Get user roles
- `PUT /api/auth/users/{id}/roles` - Assign roles to user

#### Audit
- `GET /api/auth/audit-logs` - Get security audit logs
- `GET /api/auth/sessions` - List active sessions
- `DELETE /api/auth/sessions/{id}` - Terminate a session

## Technology Stack

- **Framework**: FastAPI
- **Authentication**: JWT tokens with refresh tokens
- **Password Security**: Argon2 for password hashing
- **Database**: PostgreSQL (via Database Service)
- **Caching**: Redis for token blacklisting
- **MFA**: TOTP for multi-factor authentication
- **Audit Logging**: Structured logging to database
- **OAuth**: OAuth2 clients for third-party authentication

## Service Dependencies

- **Database Service** - For storing user data and audit logs
- **Email Service** (future) - For sending password reset emails
- **API Gateway** - For routing requests

## Data Model

### User
```
{
  "id": "string",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "first_name": "string",
  "last_name": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime",
  "status": "active|inactive|suspended|pending",
  "mfa_enabled": boolean,
  "mfa_secret": "string",
  "verified": boolean,
  "verification_token": "string",
  "password_reset_token": "string",
  "password_reset_expires": "datetime",
  "preferences": {
    "language": "string",
    "timezone": "string",
    "notification_preferences": {}
  }
}
```

### Role
```
{
  "id": "string",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "permissions": [
    {
      "resource": "string",
      "actions": ["read", "write", "delete", "admin"]
    }
  ]
}
```

### User Role
```
{
  "user_id": "string",
  "role_id": "string",
  "assigned_at": "datetime",
  "assigned_by": "string"
}
```

### Session
```
{
  "id": "string",
  "user_id": "string",
  "created_at": "datetime",
  "expires_at": "datetime",
  "refresh_token_hash": "string",
  "ip_address": "string",
  "user_agent": "string",
  "last_active": "datetime",
  "status": "active|expired|revoked"
}
```

### Audit Log
```
{
  "id": "string",
  "timestamp": "datetime",
  "user_id": "string",
  "action": "string",
  "resource": "string",
  "resource_id": "string",
  "ip_address": "string",
  "user_agent": "string",
  "status": "success|failure",
  "details": "string"
}
```

## Sequence Diagrams

### Authentication Flow

```
┌──────┐          ┌────────────────┐          ┌─────────────────┐          ┌────────────────┐
│Client│          │API Gateway     │          │Auth Service     │          │Database Service│
└──┬───┘          └─────┬──────────┘          └────────┬────────┘          └───────┬────────┘
   │                    │                              │                           │
   │ Login Request      │                              │                           │
   │ (username/password)│                              │                           │
   │────────────────────>                              │                           │
   │                    │                              │                           │
   │                    │ Forward Login Request        │                           │
   │                    │─────────────────────────────>│                           │
   │                    │                              │                           │
   │                    │                              │ Lookup User               │
   │                    │                              │──────────────────────────>│
   │                    │                              │                           │
   │                    │                              │ Return User Data          │
   │                    │                              │<──────────────────────────│
   │                    │                              │                           │
   │                    │                              │ Verify Password           │
   │                    │                              │───────┐                   │
   │                    │                              │       │                   │
   │                    │                              │<──────┘                   │
   │                    │                              │                           │
   │                    │                              │ Generate JWT Token        │
   │                    │                              │───────┐                   │
   │                    │                              │       │                   │
   │                    │                              │<──────┘                   │
   │                    │                              │                           │
   │                    │                              │ Store Session Data        │
   │                    │                              │──────────────────────────>│
   │                    │                              │                           │
   │                    │                              │ Session Stored            │
   │                    │                              │<──────────────────────────│
   │                    │                              │                           │
   │                    │ Return JWT Token             │                           │
   │                    │<─────────────────────────────│                           │
   │                    │                              │                           │
   │ JWT Token          │                              │                           │
   │<────────────────────                              │                           │
   │                    │                              │                           │
   │ Request Resource   │                              │                           │
   │ with JWT Token     │                              │                           │
   │────────────────────>                              │                           │
   │                    │                              │                           │
   │                    │ Validate Token               │                           │
   │                    │─────────────────────────────>│                           │
   │                    │                              │                           │
   │                    │ Token Valid + User Info      │                           │
   │                    │<─────────────────────────────│                           │
   │                    │                              │                           │
   │                    │ Forward to Resource Service  │                           │
   │                    │───────┐                      │                           │
   │                    │       │                      │                           │
   │                    │<──────┘                      │                           │
   │                    │                              │                           │
   │ Resource Response  │                              │                           │
   │<────────────────────                              │                           │
   │                    │                              │                           │
```

### Password Reset Flow

```
┌──────┐          ┌────────────────┐          ┌─────────────────┐          ┌────────────────┐
│Client│          │Auth Service    │          │Database Service │          │Email Service   │
└──┬───┘          └─────┬──────────┘          └────────┬────────┘          └───────┬────────┘
   │                    │                              │                           │
   │ Password Reset Req │                              │                           │
   │────────────────────>                              │                           │
   │                    │                              │                           │
   │                    │ Lookup User                  │                           │
   │                    │─────────────────────────────>│                           │
   │                    │                              │                           │
   │                    │ User Found                   │                           │
   │                    │<─────────────────────────────│                           │
   │                    │                              │                           │
   │                    │ Generate Reset Token         │                           │
   │                    │───────┐                      │                           │
   │                    │       │                      │                           │
   │                    │<──────┘                      │                           │
   │                    │                              │                           │
   │                    │ Store Reset Token            │                           │
   │                    │─────────────────────────────>│                           │
   │                    │                              │                           │
   │                    │ Token Stored                 │                           │
   │                    │<─────────────────────────────│                           │
   │                    │                              │                           │
   │                    │ Send Reset Email             │                           │
   │                    │──────────────────────────────────────────────────────────>
   │                    │                              │                           │
   │                    │ Email Sent                   │                           │
   │                    │<──────────────────────────────────────────────────────────
   │                    │                              │                           │
   │ Request Sent       │                              │                           │
   │<────────────────────                              │                           │
   │                    │                              │                           │
```

## Scaling Considerations

- Horizontal scaling for high user concurrency
- Token validation caching for improved performance
- Stateless authentication for easier scaling
- Database sharding for large user bases
- Low latency token validation for all service requests
- Distributed session management
- Rate limiting for security endpoints

## Monitoring and Logging

- Authentication success/failure rates
- Token validation latency
- Active session counts
- Password reset request volumes
- Account lockout events
- MFA usage statistics
- OAuth provider usage
- Security event logging
- Login attempt patterns
- API usage by user/role

## Security Considerations

- Secure password storage with modern hashing
- Token expiration and rotation
- Protection against brute force attacks
- CSRF protection
- Rate limiting for sensitive endpoints
- Secure token storage on client
- Input validation for all parameters
- Audit logging for security events
- Session timeout and idle session management
- GDPR and privacy compliance

## Implementation Plan

1. Create core user management functionality
2. Implement JWT-based authentication
3. Add password management features
4. Implement role-based authorization
5. Add multi-factor authentication
6. Implement OAuth providers integration
7. Create audit logging system
8. Add session management
9. Implement security monitoring
10. Create user self-service features
