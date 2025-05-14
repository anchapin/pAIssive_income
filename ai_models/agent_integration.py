import os
import json
import logging
from ai_models.adapters.adapter_factory import get_adapter

MCP_SETTINGS_FILE = os.path.abspath("cline_mcp_settings.json")
MCP_SERVERS_KEY = "mcp_servers"

def load_mcp_server_configs():
    """
    Load MCP server configurations from the settings JSON file.
    Returns a list of dicts with at least: name, host, port.
    """
    if not os.path.exists(MCP_SETTINGS_FILE):
        return []
    with open(MCP_SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get(MCP_SERVERS_KEY, [])
        except Exception:
            return []

def get_mcp_adapters():
    """
    Returns a dict mapping MCP server name to its instantiated MCPAdapter.
    """
    servers = load_mcp_server_configs()
    adapters = {}
    for server in servers:
        name, host, port = server.get("name"), server.get("host"), server.get("port")
        if not name or not host or not port:
            continue
        try:
            adapters[name] = get_adapter("mcp", host, port)
        except Exception as e:
            logging.error(f"Failed to instantiate adapter for server '{name}' with host '{host}' and port '{port}': {e}")
            continue
    return adapters

def list_available_agent_backends():
    """
    List all available agent backends, including MCP servers.
    Returns a list of dicts with keys: name, type, host, port, description.
    """
    # Add built-in or statically-configured servers here if needed
    mcp_servers = load_mcp_server_configs()
    for s in mcp_servers:
        s["type"] = "mcp"
    return mcp_servers

# === Usage example for agent code ===
# To enumerate all available backends (including MCP servers):
#   from ai_models.agent_integration import list_available_agent_backends, get_mcp_adapters
#   backends = list_available_agent_backends()
#   mcp_adapters = get_mcp_adapters()
#
# To use a registered MCP server by name:
#   mcp = mcp_adapters["my-github-server"]
#   response = mcp.send_message("my request")
