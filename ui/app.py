"""Flask backend for UI MVP."""

import os
import threading
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from flask_cors import CORS

__all__ = ["create_app", "Agent"]

def _parse_allowed_origins() -> list[str]:
    """Parse and validate allowed origins from the CORS_ALLOWED_ORIGINS environment variable."""
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    origins: list[str] = []
    for origin in raw.split(","):
        o = origin.strip()
        if not o:
            continue
        parsed = urlparse(o)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            origins.append(o)
        else:
            logging.warning("Ignoring malformed CORS origin: %r", o)
    return origins

class ActionStore:
    """Thread-safe in-memory action store."""
    def __init__(self) -> None:
        self.actions: List[Dict[str, Any]] = []
        self.counter: int = 1
        self.lock = threading.Lock()

    def add_action(self, action: Dict[str, Any]) -> int:
        with self.lock:
            action_id = self.counter
            self.counter += 1
            action["id"] = action_id
            self.actions.append(action)
            return action_id

    def reset(self) -> None:
        with self.lock:
            self.actions.clear()
            self.counter = 1

    def all(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.actions)

@dataclass
class Agent:
    """Dataclass representing an Agent."""
    id: str
    name: str
    description: Optional[str] = None
    # Add more fields as needed.

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
    CORS(app, resources={r"/*": {"origins": _parse_allowed_origins()}})
    logger = logging.getLogger(__name__)

    action_store = ActionStore()

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
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON"}), 400

        # Basic validation: must have 'type' (and optionally agentId, payload)
        if not isinstance(data, dict) or "type" not in data:
            return jsonify({"error": "Missing required field 'type'"}), 400

        # Fetch agent_id outside the lock to avoid holding it during potential I/O.
        agent_id = data.get("agentId", get_agent().id)
        action = {
            "type": data["type"],
            "agentId": agent_id,
            "payload": data.get("payload"),
        }
        action_id = action_store.add_action(action)
        logger.info("Action received and stored: %s", action)
        resp = {"status": "success", "action_id": action_id}
        return jsonify(resp), 200

    # For test reset: attach store for monkeypatching
    app._action_store = action_store  # type: ignore

    return app