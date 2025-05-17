"""Test module for mock_crewai module."""

import logging
import pytest
import importlib
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module under test
import mock_crewai


class TestMockCrewAI:
    """Test suite for mock_crewai module."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        assert hasattr(mock_crewai, "__version__")
        assert isinstance(mock_crewai.__version__, str)
        assert mock_crewai.__version__ == "0.120.0"

    def test_agent_class(self):
        """Test the Agent class."""
        # Create an agent
        agent = mock_crewai.Agent(
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

    def test_task_class(self):
        """Test the Task class."""
        # Create an agent
        agent = mock_crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = mock_crewai.Task(
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
        agent1 = mock_crewai.Agent(
            role="Agent 1",
            goal="Goal 1",
            backstory="Backstory 1",
        )
        agent2 = mock_crewai.Agent(
            role="Agent 2",
            goal="Goal 2",
            backstory="Backstory 2",
        )

        # Create tasks
        task1 = mock_crewai.Task(
            description="Task 1",
            agent=agent1,
        )
        task2 = mock_crewai.Task(
            description="Task 2",
            agent=agent2,
        )

        # Create a crew
        crew = mock_crewai.Crew(
            agents=[agent1, agent2],
            tasks=[task1, task2],
            verbose=True,
        )

        # Verify the crew attributes
        assert len(crew.agents) == 2
        assert agent1 in crew.agents
        assert agent2 in crew.agents
        assert len(crew.tasks) == 2
        assert task1 in crew.tasks
        assert task2 in crew.tasks
        assert "verbose" in crew.kwargs
        assert crew.kwargs["verbose"] is True

    def test_crew_kickoff(self):
        """Test the Crew.kickoff method."""
        # Create a crew
        crew = mock_crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Kickoff the crew
        result = crew.kickoff()

        # Verify the result
        assert result == "Mock crew output"

    def test_crew_kickoff_with_inputs(self):
        """Test the Crew.kickoff method with inputs."""
        # Create a crew
        crew = mock_crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Kickoff the crew with inputs
        inputs = {"key": "value"}
        result = crew.kickoff(inputs=inputs)

        # Verify the result includes the inputs
        assert result == f"Mock crew output with inputs: {inputs}"

    def test_module_reload(self):
        """Test that the module can be reloaded without errors."""
        # Reload the module
        importlib.reload(mock_crewai)

        # Verify the version attribute is still defined
        assert hasattr(mock_crewai, "__version__")
        assert mock_crewai.__version__ == "0.120.0"

    def test_import_all_classes(self):
        """Test that all classes can be imported without errors."""
        # Import all classes
        from mock_crewai import Agent, Task, Crew, tools

        # Verify the imports
        assert Agent.__name__ == "Agent"
        assert Task.__name__ == "Task"
        assert Crew.__name__ == "Crew"
        assert hasattr(tools, "BaseTool")

    def test_agent_str_repr(self):
        """Test the Agent __str__ and __repr__ methods."""
        # Create an agent
        agent = mock_crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Test __str__
        assert "Agent" in str(agent)
        assert "Test Agent" in str(agent)

        # Test __repr__
        assert "Agent" in repr(agent)
        assert "Test Agent" in repr(agent)
        assert "Test goal" in repr(agent)

        # Test execute_task with a task that has no description attribute
        class FakeTask:
            pass

        fake_task = FakeTask()
        result = agent.execute_task(fake_task)
        assert "Unknown task" in result

        # Test execute_task with context
        result_with_context = agent.execute_task(fake_task, context={"key": "value"})
        assert "Unknown task" in result_with_context
        assert "context" in result_with_context

    def test_task_str_repr(self):
        """Test the Task __str__ and __repr__ methods."""
        # Create an agent
        agent = mock_crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Create a task
        task = mock_crewai.Task(
            description="Test task",
            agent=agent,
        )

        # Test __str__
        assert "Task" in str(task)
        assert "Test task" in str(task)

        # Test __repr__
        assert "Task" in repr(task)
        assert "Test task" in repr(task)
        assert "Agent" in repr(task)

    def test_crew_str_repr(self):
        """Test the Crew __str__ and __repr__ methods."""
        # Create a crew
        crew = mock_crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Test __str__
        assert "Crew" in str(crew)
        assert "agents" in str(crew)
        assert "tasks" in str(crew)

    def test_tools_base_tool(self):
        """Test the BaseTool class."""
        # Create a base tool
        tool = mock_crewai.tools.BaseTool(name="Test Tool")

        # Test attributes
        assert tool.name == "Test Tool"

        # Test __str__
        assert "BaseTool" in str(tool)

        # Test execute method
        result = tool.execute("test input")
        assert "test input" in result
