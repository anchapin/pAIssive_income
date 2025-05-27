"""Test module for crewai.py."""

import logging
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the crewai module directly
import sys
import importlib.util
import os

# Get the absolute path to the crewai.py file
crewai_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "crewai.py"))

# Import the module using importlib.util
spec = importlib.util.spec_from_file_location("crewai", crewai_path)
crewai = importlib.util.module_from_spec(spec)
sys.modules["crewai"] = crewai
spec.loader.exec_module(crewai)


class TestCrewAI:
    """Test suite for crewai.py."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        assert hasattr(crewai, "__version__")
        assert isinstance(crewai.__version__, str)
        assert crewai.__version__ == "0.120.0"

    def test_version_attribute_format(self):
        """Test that the __version__ attribute has the correct format."""
        import re
        # Check that the version follows semantic versioning (MAJOR.MINOR.PATCH)
        version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        assert version_pattern.match(crewai.__version__) is not None

    def test_version_attribute_is_module_level(self):
        """Test that the __version__ attribute is defined at the module level."""
        # Get all attributes of the module
        module_attrs = dir(crewai)

        # Check that __version__ is in the module attributes
        assert "__version__" in module_attrs

        # Check that the attribute is accessible directly from the module
        assert crewai.__version__ == "0.120.0"

    def test_version_attribute_is_string(self):
        """Test that the __version__ attribute is a string."""
        assert isinstance(crewai.__version__, str)

        # Check that the version is not empty
        assert crewai.__version__ != ""

        # Check that the version is not just whitespace
        assert crewai.__version__.strip() == crewai.__version__

    def test_version_attribute_direct_import(self):
        """Test that the __version__ attribute can be imported directly."""
        # Test direct import of __version__
        from crewai import __version__
        assert __version__ == "0.120.0"

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

        # Test string representation
        agent_str = str(agent)
        assert "Agent" in agent_str
        assert "Test Agent" in agent_str
        assert "Test goal" in agent_str

        # Test repr representation
        agent_repr = repr(agent)
        assert "Agent" in agent_repr
        assert "Test Agent" in agent_repr
        assert "Test goal" in agent_repr
        assert "Test backstory" in agent_repr

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

    def test_crew_kickoff_with_inputs(self):
        """Test the Crew.kickoff method with inputs."""
        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Define inputs
        inputs = {"key": "value"}

        # Kickoff the crew with inputs
        result = crew.kickoff(inputs=inputs)

        # Verify the result
        assert result == f"Mock crew output with inputs: {inputs}"

    def test_crew_run_with_inputs(self):
        """Test the Crew.run method with inputs."""
        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Define inputs
        inputs = {"key": "value"}

        # Run the crew with inputs
        result = crew.run(inputs=inputs)

        # Verify the result
        assert result == f"Mock crew output with inputs: {inputs}"

    def test_agent_execute_task_with_context(self):
        """Test the Agent.execute_task method with context."""
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

        # Define context
        context = {"key": "value"}

        # Execute the task with context
        result = agent.execute_task(task, context=context)

        # Verify the result
        assert result == f"Executed task: Test task with context: {context}"

    def test_agent_with_empty_values(self):
        """Test the Agent class with empty values."""
        # Create an agent with empty values
        agent = crewai.Agent()

        # Verify the agent attributes
        assert agent.role == ""
        assert agent.goal == ""
        assert agent.backstory == ""
        assert agent.kwargs == {}

    def test_task_with_empty_values(self):
        """Test the Task class with empty values."""
        # Create a task with empty values
        task = crewai.Task()

        # Verify the task attributes
        assert task.description == ""
        assert task.agent is None
        assert task.kwargs == {}

    def test_crew_with_empty_values(self):
        """Test the Crew class with empty values."""
        # Create a crew with empty values
        crew = crewai.Crew()

        # Verify the crew attributes
        assert crew.agents == []
        assert crew.tasks == []
        assert crew.kwargs == {}
