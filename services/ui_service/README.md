# ui_service

## Build and Run

```sh
docker build -t ui-service .
docker run --env-file .env -p 8080:8080 ui-service
```

## Development

- Entry point: `app.py`
- Config via environment variables (see `app.py`)
- Dependencies: `requirements.txt`