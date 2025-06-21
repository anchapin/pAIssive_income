# UI Flask Backend

This is a minimal Flask REST API for storing UI actions and providing CORS.

## CORS

CORS is enabled via Flask-CORS. By default, only `http://localhost:3000` is allowed for CORS requests. You can override this with the `CORS_ALLOWED_ORIGINS` environment variable (comma-separated list of allowed origins):

```bash
export CORS_ALLOWED_ORIGINS="http://localhost:3000,https://yourdomain.com"
```

Set the `CORS_ALLOWED_ORIGINS` environment variable to restrict allowed origins for security (comma-separated if multiple). Only valid `http`/`https` origins are accepted.

### Production Deployment

For production, use Gunicorn (recommended):

```bash
gunicorn ui.app:create_app --bind 0.0.0.0:8000
```

## Endpoints

- `GET /health`  
  Health check. Returns: `{"status": "ok"}`

- `GET /api/agent`  
  Returns agent object (id, name, description).

- `POST /api/agent/action`  
  Accepts JSON: `{type: str, agentId?: str, payload?: any}`  
  Stores/logs action in memory, returns incremental `action_id`.  
  Returns 400 for invalid JSON or missing `type`.

## Tests

To run tests (from repo root):

```bash
pytest tests/ui/test_app.py
```

## Notes

- Code is modular, `create_app()` can be used for testing.
- Uses an in-memory list for agent actions (see TODO for DB integration).
- Logging is configured, type hints and docstrings included.