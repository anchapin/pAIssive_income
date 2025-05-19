# message_queue_service

## Build and Run

```sh
docker build -t message-queue-service .
docker run --env-file .env -p 9000:9000 message-queue-service
```

## Development

- Entry point: `app.py`
- Config via environment variables (see `app.py`)
- Dependencies: `requirements.txt`
