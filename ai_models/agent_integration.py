"""Agent integration module for MCP servers."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Optional

from ai_models.adapters.adapter_factory import AdapterError, get_adapter

# Use a safer path construction with Path
BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SETTINGS_FILE = BASE_DIR / "cline_mcp_settings.json"
MCP_SERVERS_KEY = "mcp_servers"

# Constants
MIN_PORT = 1
MAX_PORT = 65535
MAX_FILE_SIZE = 1024 * 1024  # 1MB max file size for settings file
MAX_JSON_DEPTH = 5  # Maximum nesting depth for JSON parsing

# Configure logging
logger = logging.getLogger(__name__)


def load_mcp_server_configs() -> list[dict[str, Any]]:
    """
    Load MCP server configurations from the settings JSON file.

    Returns:
        A list of dicts with at least: name, host, port.

    """
    # Initialize empty list for validated servers
    validated_servers: list[dict[str, Any]] = []

    # Early return if file doesn't exist
    if not MCP_SETTINGS_FILE.exists():
        return validated_servers

    # Process the settings file
    data = _load_settings_file()

    # Process server configurations if data is valid
    if data and MCP_SERVERS_KEY in data and isinstance(data[MCP_SERVERS_KEY], list):
        validated_servers = _process_server_configs(data[MCP_SERVERS_KEY])

    return validated_servers


def _load_settings_file() -> Optional[dict[str, Any]]:
    """
    Load and parse the settings file with security checks.

    Returns:
        The parsed data as a dictionary, or None if loading failed

    """
    try:
        # Check file size before reading to prevent DoS
        file_size = MCP_SETTINGS_FILE.stat().st_size
        if file_size > MAX_FILE_SIZE:
            logger.error(
                "Settings file '%s' exceeds maximum allowed size (%d bytes)",
                MCP_SETTINGS_FILE,
                MAX_FILE_SIZE,
            )
            return None

        with MCP_SETTINGS_FILE.open(encoding="utf-8") as f:
            # Try to parse JSON content with security measures
            try:
                # Use safe parsing options to prevent attacks
                data = json.load(
                    f,
                    parse_constant=lambda _: None,  # Prevent code execution via special constants
                    parse_int=int,  # Ensure integers are parsed as integers
                    parse_float=float,  # Ensure floats are parsed as floats
                )
            except json.JSONDecodeError:
                logger.exception("Failed to decode JSON from settings file")
                return None
            except RecursionError:
                logger.exception("JSON parsing failed due to excessive nesting")
                return None

            # Validate the structure of the data
            if not isinstance(data, dict):
                logger.error("Settings file does not contain a valid JSON object")
                return None

            return data

    # Handle file access errors
    except (OSError, PermissionError):
        logger.exception("Error reading settings file")
        return None


def _process_server_configs(servers: list[Any]) -> list[dict[str, Any]]:
    """
    Process and validate server configurations.

    Args:
        servers: List of server configurations to process

    Returns:
        List of validated server configurations

    """
    validated_servers = []

    # Validate each server entry
    for server in servers:
        if not isinstance(server, dict):
            logger.warning("Skipping invalid server entry (not a dictionary)")
            continue

        if _validate_server_config(server):
            # Create a sanitized copy with only the expected fields
            sanitized_server = {
                "name": server["name"],
                "host": server["host"],
                "port": server["port"],
                "description": server.get("description", ""),
            }
            validated_servers.append(sanitized_server)

    return validated_servers


def _validate_server_config(server: dict[str, Any]) -> bool:
    """
    Validate a server configuration.

    Args:
        server: Server configuration dictionary

    Returns:
        True if the server configuration is valid, False otherwise

    """
    # Check required fields
    if not all(k in server for k in ["name", "host", "port"]):
        logger.warning(
            "Skipping invalid server config missing required fields: %s", server
        )
        return False

    # Validate server name
    if not re.match(r"^[a-zA-Z0-9_-]+$", server["name"]):
        logger.warning("Skipping server with invalid name format: %s", server["name"])
        return False

    # Validate host
    if not re.match(r"^[a-zA-Z0-9_.-]+$", server["host"]):
        logger.warning("Skipping server with invalid host format: %s", server["host"])
        return False

    # Validate port
    try:
        port = int(server["port"])
        if port < MIN_PORT or port > MAX_PORT:
            logger.warning("Skipping server with invalid port range: %s", port)
            return False
        server["port"] = port
    except (ValueError, TypeError):
        logger.warning("Skipping server with invalid port: %s", server["port"])
        return False

    return True


def get_mcp_adapters() -> dict[str, Any]:
    """
    Get a dict mapping MCP server name to its instantiated MCPAdapter.

    Returns:
        A dictionary with server names as keys and MCPAdapter instances as values.

    """
    servers = load_mcp_server_configs()
    adapters = {}

    for server in servers:
        name, host, port = server.get("name"), server.get("host"), server.get("port")

        # These should already be validated by load_mcp_server_configs, but check again
        if not name or not host or not port:
            continue

        try:
            adapters[name] = get_adapter("mcp", host, port)
        except AdapterError:
            logger.exception("Adapter error for server '%s'", name)
            continue
        except Exception:
            logger.exception("Failed to instantiate adapter for server '%s'", name)
            continue

    return adapters


def list_available_agent_backends() -> list[dict[str, Any]]:
    """
    List all available agent backends, including MCP servers.

    Returns:
        A list of dicts with keys: name, type, host, port, description.

    """
    # Add built-in or statically-configured servers here if needed
    mcp_servers = load_mcp_server_configs()

    # Add type field to each server
    for server in mcp_servers:
        server["type"] = "mcp"

    return mcp_servers


"""
Usage example for agent code:

To enumerate all available backends (including MCP servers):
    from ai_models.agent_integration import list_available_agent_backends, get_mcp_adapters
    backends = list_available_agent_backends()
    mcp_adapters = get_mcp_adapters()

To use a registered MCP server by name:
    mcp = mcp_adapters.get("my-github-server")
    if mcp:
        response = mcp.send_message("my request")
"""
