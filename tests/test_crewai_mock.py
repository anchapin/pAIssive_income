"""Test module for mock_crewai module."""

import os
import sys
import importlib
from unittest.mock import patch, MagicMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the mock_crewai module directly
mock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_crewai")
if os.path.exists(mock_dir):
    sys.path.insert(0, os.path.dirname(mock_dir))

import mock_crewai as crewai


class TestCrewAIMock:
    """Test suite for mock_crewai module."""

    def test_version_attribute(self):
        """Test that the __version__ attribute is defined."""
        assert hasattr(crewai, "__version__")
        assert isinstance(crewai.__version__, str)
        assert crewai.__version__ == "0.120.0"

    def test_version_attribute_in_init(self):
        """Test that the __version__ attribute is defined in __init__.py."""
        # Import the module directly to check its attributes
        import mock_crewai
        assert hasattr(mock_crewai, "__version__")
        assert isinstance(mock_crewai.__version__, str)
        assert mock_crewai.__version__ == "0.120.0"

    def test_version_attribute_import(self):
        """Test that the __version__ attribute can be imported directly."""
        # Test direct import of __version__
        from mock_crewai import __version__
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

    def test_agent_str_representation(self):
        """Test the string representation of the Agent class."""
        # Create an agent
        agent = crewai.Agent(
            role="Test Agent",
            goal="Test goal",
            backstory="Test backstory",
        )

        # Verify the string representation
        assert str(agent) == "Agent(role='Test Agent')"
        assert repr(agent) == "Agent(role='Test Agent', goal='Test goal', backstory='Test backstory')"

    def test_agent_execute_task(self):
        """Test the Agent.execute_task method."""
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
        result = agent.execute_task(task)

        # Verify the result
        assert result == "Executed task: Test task"

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

        # Execute the task with context
        context = "Additional context"
        result = agent.execute_task(task, context=context)

        # Verify the result includes the context
        assert result == f"Executed task: Test task with context: {context}"

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

    def test_task_str_representation(self):
        """Test the string representation of the Task class."""
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

        # Verify the string representation
        assert str(task) == "Task(description='Test task')"
        assert repr(task) == "Task(description='Test task', agent=Agent(role='Test Agent'))"

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

    def test_crew_str_representation(self):
        """Test the string representation of the Crew class."""
        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Verify the string representation
        assert str(crew) == "Crew(agents=0, tasks=0)"
        assert repr(crew) == "Crew(agents=[], tasks=[])"

    def test_crew_kickoff(self):
        """Test the Crew.kickoff method."""
        # Create a crew
        crew = crewai.Crew(
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
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Kickoff the crew with inputs
        inputs = {"key": "value"}
        result = crew.kickoff(inputs=inputs)

        # Verify the result includes the inputs
        assert result == f"Mock crew output with inputs: {inputs}"

    def test_crew_run_alias(self):
        """Test that Crew.run is an alias for Crew.kickoff."""
        # Create a crew
        crew = crewai.Crew(
            agents=[],
            tasks=[],
        )

        # Verify that run is an alias for kickoff
        assert crew.run == crew.kickoff

        # Create a simple test to verify the alias works
        original_kickoff = crew.kickoff
        result1 = original_kickoff()
        result2 = crew.run()
        assert result1 == result2

    def test_tools_module(self):
        """Test the tools module."""
        # Import the tools module
        from mock_crewai import tools

        # Verify the module exists
        assert hasattr(tools, "BaseTool")

    def test_base_tool_class(self):
        """Test the BaseTool class."""
        # Import the BaseTool class
        from mock_crewai.tools import BaseTool

        # Create a tool
        tool = BaseTool(name="Test Tool", description="Test description")

        # Verify the tool attributes
        assert tool.name == "Test Tool"
        assert tool.description == "Test description"

    def test_base_tool_execute(self):
        """Test the BaseTool.execute method."""
        # Import the BaseTool class
        from mock_crewai.tools import BaseTool

        # Create a tool
        tool = BaseTool(name="Test Tool", description="Test description")

        # Execute the tool
        result = tool.execute("Test input")

        # Verify the result
        assert result == "Executed tool: Test Tool with input: Test input"

    def test_module_reload(self):
        """Test that the module can be reloaded without errors."""
        # Import the module
        import mock_crewai

        # Reload the module
        importlib.reload(mock_crewai)

        # Verify the version attribute is still defined
        assert hasattr(mock_crewai, "__version__")
        assert mock_crewai.__version__ == "0.120.0"

    def test_import_all_modules(self):
        """Test that all modules can be imported without errors."""
        # Import all modules
        from mock_crewai import Agent, Task, Crew, tools

        # Verify the imports
        assert Agent.__name__ == "Agent"
        assert Task.__name__ == "Task"
        assert Crew.__name__ == "Crew"
        assert hasattr(tools, "BaseTool")
