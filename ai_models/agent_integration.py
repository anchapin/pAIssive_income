"""Agent integration module for MCP servers."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any

from ai_models.adapters.adapter_factory import get_adapter, AdapterError

# Use a safer path construction with Path
BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SETTINGS_FILE = BASE_DIR / "cline_mcp_settings.json"
MCP_SERVERS_KEY = "mcp_servers"

# Constants
MIN_PORT = 1
MAX_PORT = 65535

# Configure logging
logger = logging.getLogger(__name__)


def load_mcp_server_configs() -> List[Dict[str, Any]]:
    """Load MCP server configurations from the settings JSON file.

    Returns:
        A list of dicts with at least: name, host, port.
    """
    if not MCP_SETTINGS_FILE.exists():
        return []

    # Initialize empty list for validated servers
    validated_servers = []

    # Try to open and read the settings file
    try:
        with open(MCP_SETTINGS_FILE, encoding="utf-8") as f:
            # Try to parse JSON content
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                logger.exception("Failed to decode JSON from settings file")
                return []

            # Get server configurations
            servers = data.get(MCP_SERVERS_KEY, [])

            # Validate each server entry
            for server in servers:
                if _validate_server_config(server):
                    validated_servers.append(server)

    # Handle file access errors
    except (OSError, PermissionError):
        logger.exception("Error reading settings file")
        return []

    # Return the list of validated servers
    return validated_servers


def _validate_server_config(server: Dict[str, Any]) -> bool:
    """Validate a server configuration.

    Args:
        server: Server configuration dictionary

    Returns:
        True if the server configuration is valid, False otherwise
    """
    # Check required fields
    if not all(k in server for k in ["name", "host", "port"]):
        logger.warning(
            f"Skipping invalid server config missing required fields: {server}"
        )
        return False

    # Validate server name
    if not re.match(r"^[a-zA-Z0-9_-]+$", server["name"]):
        logger.warning(f"Skipping server with invalid name format: {server['name']}")
        return False

    # Validate host
    if not re.match(r"^[a-zA-Z0-9_.-]+$", server["host"]):
        logger.warning(f"Skipping server with invalid host format: {server['host']}")
        return False

    # Validate port
    try:
        port = int(server["port"])
        if port < MIN_PORT or port > MAX_PORT:
            logger.warning(f"Skipping server with invalid port range: {port}")
            return False
        server["port"] = port
    except (ValueError, TypeError):
        logger.warning(f"Skipping server with invalid port: {server['port']}")
        return False

    return True


def get_mcp_adapters() -> Dict[str, Any]:
    """Returns a dict mapping MCP server name to its instantiated MCPAdapter.

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
            logger.exception(f"Adapter error for server '{name}'")
            continue
        except Exception:
            logger.exception(f"Failed to instantiate adapter for server '{name}'")
            continue

    return adapters


def list_available_agent_backends() -> List[Dict[str, Any]]:
    """List all available agent backends, including MCP servers.

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
