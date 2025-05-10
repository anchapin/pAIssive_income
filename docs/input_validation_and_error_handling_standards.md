# Input Validation and Error Handling Standards

## Purpose

This document defines the standards for input validation and error handling across the pAIssive_income project. All contributors must adhere to these guidelines to ensure security, data integrity, and a consistent user experience.

---

## 1. Input Validation

### 1.1 Use of Validation Libraries

- **Pydantic** is the standard library for input validation for Python code (APIs, CLI, config, etc.).
- All user, API, and configuration inputs must be validated using Pydantic models or equivalent schemas.
- For client-side validation (UI), use appropriate JavaScript validation libraries that mirror backend constraints.

### 1.2 Validation Coverage

- Validate all external inputs, including:
  - API requests (body, query, headers)
  - Web form submissions
  - CLI arguments
  - Configuration files
  - File uploads

### 1.3 Validation Rules

- Use strict typing (e.g., int, float, str, UUID).
- Enforce min/max lengths, value ranges, regex/patterns as appropriate.
- Use Pydantic's `forbid` option to reject unknown/extra fields.
- Apply cross-field validation using Pydantic validators where needed.
- Validate content types (e.g., Content-Type: application/json).
- Enforce request size limits to mitigate DoS risks.
- For file uploads, validate type, size, and content.

### 1.4 Input Sanitization

- Sanitize all string inputs for XSS and injection risks.
- Use the centralized sanitization utility for all input points.
- For HTML/JS contexts, escape user-provided values.
- Sanitize filenames for uploads.

### 1.5 Security Considerations

- Implement rate limiting and CSRF protection on all form/API endpoints.
- Validate API keys or auth tokens for API endpoints.

---

## 2. Error Handling

### 2.1 Consistency

- Raise a `ValidationError` (custom exception) for all validation failures.
- Return consistent error responses for validation errors:
  - HTTP APIs: JSON error response with code, message, and details.
  - Web UI: User-friendly error message.
  - CLI: Descriptive error output.

### 2.2 Error Response Format

- For APIs, error responses **must** include:
  - error_code (string)
  - message (human-readable)
  - details (optional, for validation errors)
- Avoid leaking internal stack traces or sensitive info in error responses.

### 2.3 Logging

- Log all validation and error events at appropriate levels (warning/error).
- Log validation errors with context about the input that failed.

### 2.4 Documentation

- Document expected error responses for every API endpoint and CLI command.
- Document all custom exceptions and error handlers in code.

---

## 3. Testing

### 3.1 Invalid and Malicious Input

- Every input validation function and endpoint must have tests for:
  - Invalid types, missing/extra fields, out-of-range values.
  - Malicious inputs (e.g., SQL injection, XSS strings, very large payloads).
  - Invalid/malformed files for uploads.

### 3.2 Error Handling

- Test that validation and error handlers return the correct error codes and formats.
- Test that no sensitive/internal details are leaked in error responses.

---

## 4. References and Resources

- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
