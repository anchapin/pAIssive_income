"""Flask application for UI backend exposing health, agent, and agent action endpoints."""

import os
import threading
import time
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib.parse import urlparse

app = Flask(__name__)

def _parse_allowed_origins():
    """Parse and validate allowed origins from the CORS_ALLOWED_ORIGINS environment variable."""
    origins_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    origins = []
    for origin in origins_raw.split(","):
        o = origin.strip()
        if not o:
            continue
        parsed = urlparse(o)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            origins.append(o)
        else:
            logging.warning(f"Ignoring malformed CORS origin: {o!r}")
    return origins

allowed_origins = _parse_allowed_origins()

CORS(app, origins=allowed_origins, supports_credentials=True)

# Simulated shared action storage (thread safe)
class ActionStore:
    """Thread-safe action store with id counter."""
    def __init__(self):
        self.actions = []
        self.lock = threading.Lock()
        self.counter = 0

    def add_action(self, data):
        with self.lock:
            self.counter += 1
            data["id"] = self.counter
            self.actions.append(data)
            return data

    def get_actions(self):
        with self.lock:
            return list(self.actions)

actions_store = ActionStore()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/actions", methods=["POST"])
def post_action():
    data = request.get_json(force=True)
    action = actions_store.add_action(data)
    return jsonify(action), 201

@app.route("/actions", methods=["GET"])
def get_actions():
    return jsonify(actions_store.get_actions())
import threading
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

__all__ = ["create_app", "Agent"]

# In-memory storage for actions (as a placeholder)
_ACTIONS: List[Dict[str, Any]] = []
_ACTION_ID_COUNTER: int = 1
_ACTION_LOCK = threading.Lock()

@dataclass
class Agent:
    """Dataclass representing an Agent."""
    id: str
    name: str
    description: Optional[str] = None
    # Add more fields as needed


DEFAULT_AGENT = Agent(
    id="default-agent",
    name="Default Agent",
    description="Fallback agent when DB unavailable.",
)


def get_agent() -> Agent:
    """Fetch agent object. Placeholder for DB integration."""
    # TODO: Integrate with real DB; fallback to default.
    return DEFAULT_AGENT


def create_app() -> Flask:
    """Create and configure Flask app with routes and CORS."""
    app = Flask(__name__)
    allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    CORS(app, resources={r"/*": {"origins": allowed_origins}})

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.route("/api/agent", methods=["GET"])
    def get_agent_route() -> Any:
        """Get agent object."""
        agent = get_agent()
        return jsonify(asdict(agent)), 200

    @app.route("/api/agent/action", methods=["POST"])
    def agent_action() -> Any:
        """Accept and store/log an agent action."""
        global _ACTION_ID_COUNTER, _ACTIONS
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400

        # Basic validation: must have 'type' (and optionally agentId, payload)
        if not isinstance(data, dict) or "type" not in data:
            return jsonify({"error": "Missing required field 'type'"}), 400

        with _ACTION_LOCK:
            action_id = _ACTION_ID_COUNTER
            _ACTION_ID_COUNTER += 1
            action = {
                "id": action_id,
                "type": data["type"],
                "agentId": data.get("agentId", get_agent().id),
                "payload": data.get("payload"),
            }
            _ACTIONS.append(action)
            logger.info("Action received and stored: %s", action)
        resp = {"status": "success", "action_id": action_id}
        return jsonify(resp), 200

    return app