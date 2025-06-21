"""
Configuration utilities for agent_team.
"""

from typing import Optional
from agent_team.schemas import TeamConfigSchema

DEFAULT_TEAM_CONFIG = {
    "model": {
        "name": "gpt-3.5-turbo",
        "temperature": 0.2,
        "max_tokens": 2048,
    },
    "workflow": {
        "steps": ["research", "design", "monetize", "market", "feedback"]
    }
}

def load_config(path: Optional[str] = None) -> TeamConfigSchema:
    """
    Load a TeamConfigSchema from a file or defaults.

    If path is None, returns the default config.
    """
    if path is None:
        return TeamConfigSchema.model_validate(DEFAULT_TEAM_CONFIG)
    import json
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return TeamConfigSchema.model_validate(data)
    except Exception as exc:
        raise RuntimeError(f"Could not load config from {path}: {exc}")