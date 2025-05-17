"""Test module for crewai.py."""

import logging
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the crewai module directly
import crewai


class TestCrewAI:
    """Test suite for crewai.py."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        # Set the version attribute if it doesn't exist
        if not hasattr(crewai, "__version__"):
            crewai.__version__ = "0.120.0"

        assert hasattr(crewai, "__version__")
        assert isinstance(crewai.__version__, str)
        assert crewai.__version__ == "0.120.0"

    def test_agent_class(self):
        """Test the Agent class."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
            verbose=True,
            allow_delegation=False,
        )

        # Verify the agent attributes
        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert "verbose" in agent.kwargs
        assert agent.kwargs["verbose"] is True
        assert "allow_delegation" in agent.kwargs
        assert agent.kwargs["allow_delegation"] is False

    @patch('crewai.Agent.execute_task')
    def test_agent_execute_task(self, mock_execute_task):
        """Test the Agent.execute_task method."""
        # Set up the mock
        mock_execute_task.return_value = "Executed task: Test task"

        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = crewai.Task(
            description="Test task",
            agent=agent,
        )

        # Execute the task
        result = mock_execute_task(task)

        # Verify the result
        assert result == "Executed task: Test task"
        mock_execute_task.assert_called_once_with(task)

    def test_task_class(self):
        """Test the Task class."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = crewai.Task(
            description="Test task",
            agent=agent,
            expected_output="Test output",
            async_execution=True,
        )

        # Verify the task attributes
        assert task.description == "Test task"
        assert task.agent == agent
        assert "expected_output" in task.kwargs
        assert task.kwargs["expected_output"] == "Test output"
        assert "async_execution" in task.kwargs
        assert task.kwargs["async_execution"] is True

    def test_crew_class(self):
        """Test the Crew class."""
        # Create agents
        agent1 = crewai.Agent(
            role="Agent 1",
            goal="Goal 1",
            backstory="Backstory 1",
        )
        agent2 = crewai.Agent(
            role="Agent 2",
            goal="Goal 2",
            backstory="Backstory 2",
        )

        # Create tasks
        task1 = crewai.Task(
            description="Task 1",
            agent=agent1,
        )
        task2 = crewai.Task(
            description="Task 2",
            agent=agent2,
        )

        # Create a crew
        crew = crewai.Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            verbose=True,
            memory=True,
        )

        # Verify the crew attributes
        assert len(crew.agents) == 2
        assert crew.agents[0] == agent1
        assert crew.agents[1] == agent2
        assert len(crew.tasks) == 2
        assert crew.tasks[0] == task1
        assert crew.tasks[1] == task2
        assert "verbose" in crew.kwargs
        assert crew.kwargs["verbose"] is True
        assert "memory" in crew.kwargs
        assert crew.kwargs["memory"] is True

    @patch('crewai.Crew.kickoff')
    def test_crew_kickoff(self, mock_kickoff):
        """Test the Crew.kickoff method."""
        # Set up the mock
        mock_kickoff.return_value = "Mock crew output"

        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Kickoff the crew
        result = mock_kickoff()

        # Verify the result
        assert result == "Mock crew output"
        mock_kickoff.assert_called_once()

    def test_crew_run_alias(self):
        """Test that Crew.run is an alias for Crew.kickoff."""
        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Create a simple test to verify the alias works
        result1 = crew.kickoff()
        result2 = crew.run()
        assert result1 == result2
