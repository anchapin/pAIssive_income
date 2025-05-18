# Secrets Management

All secrets are managed via secure environment variables or encrypted backends.

- Never log or store secrets in plaintext.
- Use the provided `mask_sensitive_data` utilities.
- SecureLogger automatically masks all known secret fields.
- When listing secrets, only show masked values.

For secret rotation, encrypted storage, and audit recommendations, see [security_fixes_summary.md](../../security_fixes_summary.md).