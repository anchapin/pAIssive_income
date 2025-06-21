"""
Unit tests for agent_team config utilities.
"""

import tempfile
import json
import os

from agent_team.team_config import load_config, DEFAULT_TEAM_CONFIG

def test_load_default_config():
    config = load_config()
    assert config.model["name"] == "gpt-3.5-turbo"
    assert "steps" in config.workflow
    assert config.workflow["steps"] == ["research", "design", "monetize", "market", "feedback"]

def test_load_config_from_file():
    cfg = {
        "model": {"name": "custom-model", "temperature": 0.42, "max_tokens": 123},
        "workflow": {"steps": ["a", "b", "c"]}
    }
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump(cfg, f)
        f.flush()
        path = f.name

    try:
        loaded = load_config(path)
        assert loaded.model["name"] == "custom-model"
        assert loaded.workflow["steps"] == ["a", "b", "c"]
    finally:
        os.remove(path)