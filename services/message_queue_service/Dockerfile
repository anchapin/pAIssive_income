FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install uv and use it exclusively for environment and dependency management
RUN apt-get update && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && export PATH="$HOME/.cargo/bin:$PATH" \
    && ~/.cargo/bin/uv --version \
    && ~/.cargo/bin/uv venv .venv \
    && . .venv/bin/activate \
    && ~/.cargo/bin/uv pip install -r requirements.txt

# Use the virtual environment's Python to run the app
CMD [".venv/bin/python", "app.py"]
