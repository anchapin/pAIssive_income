"""agent_integration - Module for ai_models.agent_integration."""

import os
import json

from .adapters import adapter_factory

MCP_SETTINGS_FILE = os.path.abspath("cline_mcp_settings.json")
MCP_SERVERS_KEY = "mcp_servers"

def load_mcp_server_configs():
    """Load MCP server configurations from the config file."""
    if not os.path.exists(MCP_SETTINGS_FILE):
        return []
    with open(MCP_SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            return []
    return data.get(MCP_SERVERS_KEY, [])

def get_mcp_server_adapters():
    """
    Instantiate MCPAdapter objects for all user-configured MCP servers.
    Returns a dict mapping server name to adapter instance.
    """
    servers = load_mcp_server_configs()
    adapters = {}
    for server in servers:
        try:
            adapter = adapter_factory.get_adapter(
                server_type="mcp",
                host=server["host"],
                port=server["port"],
            )
            adapters[server["name"]] = adapter
        except Exception as e:
            # Optionally log or handle errors
            continue
    return adapters
