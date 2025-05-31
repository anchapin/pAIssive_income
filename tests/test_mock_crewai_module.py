"""test_mock_crewai_module - Test for mock_crewai module coverage."""

# Standard library imports
import sys
import unittest
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local imports
import mock_crewai
from mock_crewai import Agent, Crew, Task, __version__


class TestMockCrewAIModule(unittest.TestCase):
    """Test case for mock_crewai module."""

    def test_mock_crewai_version(self):
        """Test that the mock_crewai version is correct."""
        assert mock_crewai.__version__ == "0.120.0"

    def test_version_import(self):
        """Test that __version__ is imported correctly."""
        assert __version__ == "0.120.0"

    def test_agent_class(self):
        """Test that Agent class is available."""
        assert hasattr(mock_crewai, "Agent")
        assert Agent.__name__ == "MockAgent"

    def test_crew_class(self):
        """Test that Crew class is available."""
        assert hasattr(mock_crewai, "Crew")
        assert Crew.__name__ == "MockCrew"

    def test_task_class(self):
        """Test that Task class is available."""
        assert hasattr(mock_crewai, "Task")
        assert Task.__name__ == "MockTask"

    def test_agent_creation(self):
        """Test that Agent can be created."""
        agent = Agent(name="Test Agent", role="Test Role")
        assert agent.name == "Test Agent"
        assert agent.role == "Test Role"

    def test_task_creation(self):
        """Test that Task can be created."""
        task = Task(description="Test Task")
        assert task.description == "Test Task"

    def test_crew_creation(self):
        """Test that Crew can be created."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task")
        crew = Crew(agents=[agent], tasks=[task])
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1

    def test_agent_kwargs(self):
        """Test that Agent can be created with kwargs."""
        agent = Agent(
            name="Test Agent",
            role="Test Role",
            goal="Test Goal",
            backstory="Test Backstory",
            verbose=True,
            allow_delegation=True,
            tools=["tool1", "tool2"],
            llm=MagicMock(),
        )
        assert agent.name == "Test Agent"
        assert agent.role == "Test Role"
        assert agent.goal == "Test Goal"
        assert agent.backstory == "Test Backstory"
        assert agent.verbose
        assert agent.allow_delegation
        assert agent.tools == ["tool1", "tool2"]
        assert agent.llm is not None

    def test_task_kwargs(self):
        """Test that Task can be created with kwargs."""
        task = Task(
            description="Test Task",
            expected_output="Test Output",
            agent=MagicMock(),
            async_execution=True,
            context=["context1", "context2"],
            tools=["tool1", "tool2"],
        )
        assert task.description == "Test Task"
        assert task.expected_output == "Test Output"
        assert task.agent is not None
        assert task.async_execution
        assert task.context == ["context1", "context2"]
        assert task.tools == ["tool1", "tool2"]

    def test_crew_kwargs(self):
        """Test that Crew can be created with kwargs."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process="sequential",
            verbose=True,
            memory=MagicMock(),
            cache=True,
        )
        assert len(crew.agents) == 1
        assert len(crew.tasks) == 1
        assert crew.process == "sequential"
        assert crew.verbose
        assert crew.memory is not None
        assert crew.cache

    def test_agent_execute(self):
        """Test that Agent can execute a task."""
        agent = Agent(name="Test Agent", role="Test Role")
        result = agent.execute("Test Task")
        assert result == "Executed: Test Task by Test Agent (Test Role)"

    def test_task_execute(self):
        """Test that Task can be executed."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        result = task.execute()
        assert result == "Executed: Test Task by Test Agent (Test Role)"

    def test_crew_kickoff(self):
        """Test that Crew can kickoff tasks."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()
        assert result == ["Executed: Test Task by Test Agent (Test Role)"]

    def test_crew_run(self):
        """Test that Crew can run tasks."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.run()
        assert result == ["Executed: Test Task by Test Agent (Test Role)"]
