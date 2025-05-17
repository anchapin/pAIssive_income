# ui_service

## Build and Run

```sh
docker build -t ui-service .
docker run --env-file .env -p 8080:8080 ui-service
```

## Development

- Entry point: `ui_app.py`
- Config via environment variables (see `ui_app.py`)
- Dependencies: `requirements.txt`