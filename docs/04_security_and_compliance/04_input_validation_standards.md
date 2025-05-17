# Input Validation Standards

- Validate all external input using Pydantic schemas and explicit type checks.
- Use FastAPI/Pydantic for request validation in APIs.
- For CLI and subprocesses, validate and sanitize inputs before command execution.
- Never use unchecked user input in subprocess commands or database queries.

For recent fixes, see [security_fixes.md](../../security_fixes.md).