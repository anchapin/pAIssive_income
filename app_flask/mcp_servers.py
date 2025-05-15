"""MCP Server management API endpoints."""

import json
import logging
import threading
import re
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from flask import Blueprint, request, jsonify, Response

# Use a safer path construction with Path
BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SETTINGS_FILE = BASE_DIR / "cline_mcp_settings.json"
MCP_SERVERS_KEY = "mcp_servers"

# Constants
MIN_PORT = 1
MAX_PORT = 65535

# Thread safety
_LOCK = threading.Lock()

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
mcp_servers_api = Blueprint("mcp_servers_api", __name__, url_prefix="/api/mcp_servers")


# Custom error handler for the blueprint
@mcp_servers_api.errorhandler(Exception)
def handle_exception(e: Exception) -> Tuple[Response, int]:
    """Handle exceptions in the blueprint.

    Args:
        e: The exception that was raised

    Returns:
        A tuple of (response, status_code)
    """
    logger.exception("Unhandled exception in MCP servers API")
    response = jsonify({"error": "Internal server error", "message": str(e)})
    return response, 500


def load_settings() -> Dict[str, Any]:
    """Load MCP server settings from the settings file.

    Returns:
        dict: The settings data with at least the MCP_SERVERS_KEY entry.
    """
    if not MCP_SETTINGS_FILE.exists():
        return {MCP_SERVERS_KEY: []}

    try:
        with open(MCP_SETTINGS_FILE, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logger.exception(
                    "Failed to decode JSON from settings file '%s'", MCP_SETTINGS_FILE
                )
                data = {}
    except (OSError, PermissionError):
        logger.exception("Error reading settings file '%s'", MCP_SETTINGS_FILE)
        data = {}

    if MCP_SERVERS_KEY not in data:
        data[MCP_SERVERS_KEY] = []
    return data


def save_settings(data: Dict[str, Any]) -> None:
    """Save MCP server settings to the settings file.

    Args:
        data: The settings data to save.
    """
    try:
        # Ensure parent directory exists
        MCP_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(MCP_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except (OSError, PermissionError):
        logger.exception("Error writing settings file '%s'", MCP_SETTINGS_FILE)
        raise


def validate_server_data(server: Dict[str, Any]) -> Optional[Tuple[str, int]]:
    """Validate server data.

    Args:
        server: Server data to validate

    Returns:
        None if validation passes, or (error_message, status_code) if validation fails
    """
    # Define validation checks
    validations = [
        # Check if server data is valid
        (not server or not isinstance(server, dict), "Invalid JSON data"),
    ]

    # Validate required fields
    required_fields = ["name", "host", "port"]
    for field in required_fields:
        validations.append((field not in server, f"Missing required field: {field}"))

    # If we have the required fields, perform additional validations
    if all(field in server for field in required_fields):
        # Validate server name (alphanumeric, dash, underscore only)
        validations.append((
            not re.match(r"^[a-zA-Z0-9_-]+$", server["name"]),
            "Server name must contain only alphanumeric characters, underscores, and dashes",
        ))

        # Validate host (prevent command injection via hostname)
        validations.append((
            not re.match(r"^[a-zA-Z0-9_.-]+$", server["host"]),
            "Host must contain only alphanumeric characters, dots, underscores, and dashes",
        ))

        # Validate description if provided
        if "description" in server:
            validations.append((
                not isinstance(server["description"], str),
                "Description must be a string",
            ))

        # Validate port is an integer in valid range
        try:
            port = int(server["port"])
            validations.append((
                port < MIN_PORT or port > MAX_PORT,
                f"Port must be between {MIN_PORT} and {MAX_PORT}",
            ))
            server["port"] = port
        except (ValueError, TypeError):
            return "Port must be a valid integer", 400

    # Check all validations
    for condition, error_message in validations:
        if condition:
            return error_message, 400

    return None


@mcp_servers_api.route("/", methods=["GET"])
def list_mcp_servers() -> Tuple[Response, int]:
    """List all registered MCP servers.

    Returns:
        A tuple of (response, status_code)
    """
    with _LOCK:
        data = load_settings()
        return jsonify(data.get(MCP_SERVERS_KEY, [])), 200


@mcp_servers_api.route("/", methods=["POST"])
def add_mcp_server() -> Tuple[Response, int]:
    """Add a new MCP server.

    Returns:
        A tuple of (response, status_code)
    """
    server = request.get_json()

    # Validate server data
    validation_error = validate_server_data(server)
    if validation_error:
        error_message, status_code = validation_error
        return jsonify({"error": error_message}), status_code

    with _LOCK:
        data = load_settings()
        servers = data.get(MCP_SERVERS_KEY, [])

        # Check for duplicate server name
        if any(s["name"] == server["name"] for s in servers):
            return jsonify({
                "error": f"Server with name '{server['name']}' already exists."
            }), 409

        # Create sanitized server entry
        sanitized_server = {
            "name": server["name"],
            "host": server["host"],
            "port": server["port"],
            "description": server.get("description", ""),
        }

        servers.append(sanitized_server)
        data[MCP_SERVERS_KEY] = servers
        save_settings(data)

    return jsonify({"status": "added", "server": sanitized_server}), 201


@mcp_servers_api.route("/<server_name>", methods=["DELETE"])
def delete_mcp_server(server_name: str) -> Tuple[Response, int]:
    """Remove an MCP server by name.

    Args:
        server_name: The name of the server to delete.

    Returns:
        A tuple of (response, status_code)
    """
    # Validate server name
    if not re.match(r"^[a-zA-Z0-9_-]+$", server_name):
        return jsonify({"error": "Invalid server name format"}), 400

    with _LOCK:
        data = load_settings()
        servers = data.get(MCP_SERVERS_KEY, [])

        # Find and remove the server by name
        new_servers = [s for s in servers if s["name"] != server_name]

        # Check if any server was removed
        if len(servers) == len(new_servers):
            return jsonify({"error": f"No server found with name '{server_name}'"}), 404

        data[MCP_SERVERS_KEY] = new_servers
        save_settings(data)

    return jsonify({"status": "deleted", "name": server_name}), 200
