# api_gateway

## Build and Run

```sh
docker build -t api-gateway .
docker run --env-file .env -p 8081:8081 api-gateway
```

## Development

- Entry point: `app.py`
- Config via environment variables (see `app.py`)
- Dependencies: `requirements.txt`