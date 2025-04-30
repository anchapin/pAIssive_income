# Test Coverage Plan

## Current Status

### Webhook Schema Tests
- **File**: `tests/api/test_webhook_schema.py`
- **Status**: ✅ All tests passing
- **Details**:
  - `test_webhook_request_schema_valid`: Validates the schema for a correct webhook request. **Passed**
  - `test_webhook_request_schema_invalid_url`: Ensures invalid URLs are rejected. **Passed**
  - `test_webhook_request_schema_missing_fields`: Verifies that missing required fields raise validation errors. **Passed**

### Notes
- The issue with the `HttpUrl` type comparison in `test_webhook_request_schema_valid` has been resolved by converting the `HttpUrl` object to a string for comparison.
- Deprecation warnings related to FastAPI's `on_event` handlers were observed but do not affect test outcomes. These should be addressed in the future.

## Next Steps
- Address FastAPI deprecation warnings in `api/routes/webhook_router.py`.
- Expand test coverage for edge cases in webhook schema validation.
