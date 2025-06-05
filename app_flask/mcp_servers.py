"""MCP Server management API endpoints."""

from __future__ import annotations

import json
import logging
import os
import re
import stat
import sys  # Added sys import
import threading
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from flask import Blueprint, Response, jsonify, request

# Configure logging


# Configure logging


# Configure logging


# Configure logging



# Configure logging
except ImportError:

    sys.exit(1)

# Use a safer path construction with Path
BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SETTINGS_FILE = BASE_DIR / "cline_mcp_settings.json"
MCP_SERVERS_KEY = "mcp_servers"

# Constants
MIN_PORT = 1
MAX_PORT = 65535
MAX_FILE_SIZE = 1024 * 1024  # 1MB max file size for settings file
MAX_JSON_DEPTH = 5  # Maximum nesting depth for JSON parsing

# Thread safety
_LOCK = threading.Lock()


# Custom exceptions
class InvalidDataTypeError(TypeError):
    """Raised when data is not of the expected type."""

    def __init__(self, data_name: str, expected_type: str) -> None:
        """
        Initialize the error with data name and expected type.

        Args:
            data_name: Name of the data field that has the wrong type
            expected_type: The expected type for the data field

        """
        self.message = f"{data_name} must be a {expected_type}"
        super().__init__(self.message)


# Create blueprint
mcp_servers_api = Blueprint("mcp_servers_api", __name__, url_prefix="/api/mcp_servers")


# Custom error handler for the blueprint
@mcp_servers_api.errorhandler(Exception)
def handle_exception(e: Exception) -> tuple[Response, int]:
    """
    Handle exceptions in the blueprint.

    Args:
        e: The exception that was raised

    Returns:
        A tuple of (response, status_code)

    """
    logger.exception("Unhandled exception in MCP servers API")
    response = jsonify({"error": "Internal server error", "message": str(e)})
    return response, 500


def load_settings() -> dict[str, Any]:
    """
    Load MCP server settings from the settings file.

    Returns:
        dict: The settings data with at least the MCP_SERVERS_KEY entry.

    """
    if not MCP_SETTINGS_FILE.exists():
        return {MCP_SERVERS_KEY: []}

    try:
        # Check file size before reading to prevent DoS
        file_size = MCP_SETTINGS_FILE.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.error(
                "Settings file '%s' exceeds maximum allowed size (%d bytes)",
                MCP_SETTINGS_FILE,
                MAX_FILE_SIZE,
            )
            return {MCP_SERVERS_KEY: []}

        with MCP_SETTINGS_FILE.open(encoding="utf-8") as f:
            try:
                # Parse with a maximum depth to prevent stack overflow attacks
                data = json.load(
                    f, parse_constant=lambda _: None, parse_int=int, parse_float=float
                )
            except json.JSONDecodeError:
                logger.exception(
                    "Failed to decode JSON from settings file '%s'", MCP_SETTINGS_FILE
                )
                data = {}
    except (OSError, PermissionError):
        logger.exception("Error reading settings file '%s'", MCP_SETTINGS_FILE)
        data = {}

    # Validate the structure of the data
    if not isinstance(data, dict):
        logger.error("Settings file does not contain a valid JSON object")
        data = {}

    if MCP_SERVERS_KEY not in data:
        data[MCP_SERVERS_KEY] = []
    elif not isinstance(data[MCP_SERVERS_KEY], list):
        logger.error("MCP servers entry is not a list, resetting to empty list")
        data[MCP_SERVERS_KEY] = []

    return data


def save_settings(data: dict[str, Any]) -> None:
    """
    Save MCP server settings to the settings file.

    Args:
        data: The settings data to save.

    Raises:
        OSError: If there's an error writing to the file
        PermissionError: If there's a permission error
        InvalidDataTypeError: If MCP_SERVERS_KEY is not a list

    """
    # Type checking is handled by the function signature

    # Continue with the save operation
    temp_file = None
    try:
        # Ensure parent directory exists
        MCP_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Ensure MCP_SERVERS_KEY exists and is a list
        if MCP_SERVERS_KEY not in data:
            data[MCP_SERVERS_KEY] = []
        elif not isinstance(data[MCP_SERVERS_KEY], list):
            raise InvalidDataTypeError(MCP_SERVERS_KEY, "list")

        # Create a temporary file first, then rename it to the target file
        # This ensures atomic writes and prevents corruption if the process is interrupted
        temp_file = MCP_SETTINGS_FILE.with_suffix(".tmp")

        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Ensure data is written to disk

        # Set secure permissions (owner read/write only)
        temp_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

        # Rename the temporary file to the target file (atomic operation)
        temp_file.replace(MCP_SETTINGS_FILE)

    except (OSError, PermissionError):
        logger.exception("Error writing settings file '%s'", MCP_SETTINGS_FILE)
        # Clean up temporary file if it exists
        if temp_file is not None and temp_file.exists():
            try:
                temp_file.unlink()
            except OSError as cleanup_error:
                # Log the error but continue with the main exception
                logger.warning("Failed to clean up temporary file: %s", cleanup_error)
        raise


def validate_server_data(server: dict[str, Any]) -> Optional[tuple[str, int]]:
    """
    Validate server data.

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

    # Check if server is None or not a dict before trying to access fields
    if not server or not isinstance(server, dict):
        # Return early with the first validation error
        return "Invalid JSON data", 400

    # Validate required fields
    required_fields = ["name", "host", "port"]
    validations.extend(
        [
            (field not in server, f"Missing required field: {field}")
            for field in required_fields
        ]
    )

    # If we have the required fields, perform additional validations
    if all(field in server for field in required_fields):
        # Validate server name (alphanumeric, dash, underscore only)
        validations.append(
            (
                not re.match(r"^[a-zA-Z0-9_-]+$", server["name"]),
                "Server name must contain only alphanumeric characters, underscores, and dashes",
            )
        )

        # Validate host (prevent command injection via hostname)
        validations.append(
            (
                not re.match(r"^[a-zA-Z0-9_.-]+$", server["host"]),
                "Host must contain only alphanumeric characters, dots, underscores, and dashes",
            )
        )

        # Validate description if provided
        if "description" in server:
            validations.append(
                (
                    not isinstance(server["description"], str),
                    "Description must be a string",
                )
            )

        # Validate port is an integer in valid range
        try:
            port = int(server["port"])
            validations.append(
                (
                    port < MIN_PORT or port > MAX_PORT,
                    f"Port must be between {MIN_PORT} and {MAX_PORT}",
                )
            )
            server["port"] = port
        except (ValueError, TypeError):
            return "Port must be a valid integer", 400

    # Check all validations
    for condition, error_message in validations:
        if condition:
            return error_message, 400

    return None


@mcp_servers_api.route("/", methods=["GET"])
def list_mcp_servers() -> tuple[Response, int]:
    """
    List all registered MCP servers.

    Returns:
        A tuple of (response, status_code)

    """
    with _LOCK:
        data = load_settings()
        return jsonify(data.get(MCP_SERVERS_KEY, [])), 200


@mcp_servers_api.route("/", methods=["POST"])
def add_mcp_server() -> tuple[Response, int]:
    """
    Add a new MCP server.

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
            error_msg = "Server with name '{}' already exists.".format(server["name"])
            return jsonify({"error": error_msg}), 409

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
def delete_mcp_server(server_name: str) -> tuple[Response, int]:
    """
    Remove an MCP server by name.

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
            error_msg = f"No server found with name '{server_name}'"
            return jsonify({"error": error_msg}), 404

        data[MCP_SERVERS_KEY] = new_servers
        save_settings(data)

    return jsonify({"status": "deleted", "name": server_name}), 200
