# UI Flask Backend

This directory contains the Flask-based backend for the UI MVP.

## Quickstart

1. Install dependencies (using `uv`):
    ```bash
    uv pip install -r requirements.txt
    ```

2. Run the server:
    ```bash
    python -m ui.run_ui
    ```
    - Or set custom port:
    ```bash
    PORT=8080 python -m ui.run_ui
    ```

### Production Deployment

For production, use Gunicorn (recommended):

```bash
gunicorn ui.app:create_app --bind 0.0.0.0:8000
```

Set the `CORS_ALLOWED_ORIGINS` environment variable to restrict allowed origins for security (comma-separated if multiple):

```bash
export CORS_ALLOWED_ORIGINS="https://yourdomain.com"
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

## CORS

CORS is enabled for all origins (`*`).  
See `app.py` for implementation.

## Tests

To run tests (from repo root):

```bash
pytest tests/ui/test_app.py
```

## Notes

- Code is modular, `create_app()` can be used for testing.
- Uses an in-memory list for agent actions (see TODO for DB integration).
- Logging is configured, type hints and docstrings included.