"""MCP Server management API endpoints."""

import os
import json
import threading
from flask import Blueprint, request, jsonify, abort

MCP_SETTINGS_FILE = os.path.abspath("cline_mcp_settings.json")
MCP_SERVERS_KEY = "mcp_servers"
_LOCK = threading.Lock()

mcp_servers_api = Blueprint("mcp_servers_api", __name__, url_prefix="/api/mcp_servers")


def load_settings():
    if not os.path.exists(MCP_SETTINGS_FILE):
        return {MCP_SERVERS_KEY: []}
    with open(MCP_SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = {}
    if MCP_SERVERS_KEY not in data:
        data[MCP_SERVERS_KEY] = []
    return data


def save_settings(data):
    with open(MCP_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@mcp_servers_api.route("/", methods=["GET"])
def list_mcp_servers():
    """List all registered MCP servers."""
    with _LOCK:
        data = load_settings()
        return jsonify(data.get(MCP_SERVERS_KEY, [])), 200


@mcp_servers_api.route("/", methods=["POST"])
def add_mcp_server():
    """Add a new MCP server."""
    server = request.get_json()
    required_fields = ["name", "host", "port"]
    for field in required_fields:
        if field not in server:
            abort(400, f"Missing required field: {field}")
    with _LOCK:
        data = load_settings()
        servers = data.get(MCP_SERVERS_KEY, [])
        if any(s["name"] == server["name"] for s in servers):
            abort(409, f"Server with name '{server['name']}' already exists.")
        servers.append({
            "name": server["name"],
            "host": server["host"],
            "port": server["port"],
            "description": server.get("description", "")
        })
        data[MCP_SERVERS_KEY] = servers
        save_settings(data)
    return jsonify({"status": "added", "server": server}), 201


@mcp_servers_api.route("/<name>", methods=["DELETE"])
def delete_mcp_server(name):
    """Remove an MCP server by name."""
    with _LOCK:
        data = load_settings()
        servers = data.get(MCP_SERVERS_KEY, [])
        new_servers = [s for s in servers if s["name"] != name]
        if len(servers) == len(new_servers):
            abort(404, f"No server found with name '{name}'.")
        data[MCP_SERVERS_KEY] = new_servers
        save_settings(data)
    return jsonify({"status": "deleted", "name": name}), 200