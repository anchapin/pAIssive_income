"""Flask application for UI backend exposing health, agent, and agent action endpoints."""

import os
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS

__all__ = ["create_app", "Agent"]

# In-memory storage for actions (as a placeholder)
_ACTIONS: List[Dict[str, Any]] = []
_ACTION_ID_COUNTER: int = 1

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
    CORS(app, resources={r"/*": {"origins": "*"}})

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
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

        # Basic validation: must have 'type' (and optionally agentId, payload)
        if not isinstance(data, dict) or "type" not in data:
            return jsonify({"error": "Missing required field 'type'"}), 400

        action = {
            "id": _ACTION_ID_COUNTER,
            "type": data["type"],
            "agentId": data.get("agentId", get_agent().id),
            "payload": data.get("payload"),
        }
        _ACTIONS.append(action)
        logger.info("Action received and stored: %s", action)
        resp = {"status": "success", "action_id": _ACTION_ID_COUNTER}
        _ACTION_ID_COUNTER += 1
        return jsonify(resp), 200

    return app