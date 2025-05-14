"""Test scaffold for CrewAI agent integration."""

import pytest

def test_crewai_import_and_agent():
    try:
        from crewai import Agent
        # Minimal agent instantiation check
        agent = Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory"
        )
    except ImportError:
        pytest.fail("CrewAI is not installed or cannot be imported.")

    assert agent.role == "Test Agent"
    assert agent.goal == "Test goal"
    assert agent.backstory == "Test backstory"
