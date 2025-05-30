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
        self.assertEqual(mock_crewai.__version__, "0.120.0")

    def test_version_import(self):
        """Test that __version__ is imported correctly."""
        self.assertEqual(__version__, "0.120.0")

    def test_agent_class(self):
        """Test that Agent class is available."""
        self.assertTrue(hasattr(mock_crewai, "Agent"))
        self.assertEqual(Agent.__name__, "MockAgent")

    def test_crew_class(self):
        """Test that Crew class is available."""
        self.assertTrue(hasattr(mock_crewai, "Crew"))
        self.assertEqual(Crew.__name__, "MockCrew")

    def test_task_class(self):
        """Test that Task class is available."""
        self.assertTrue(hasattr(mock_crewai, "Task"))
        self.assertEqual(Task.__name__, "MockTask")

    def test_agent_creation(self):
        """Test that Agent can be created."""
        agent = Agent(name="Test Agent", role="Test Role")
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.role, "Test Role")

    def test_task_creation(self):
        """Test that Task can be created."""
        task = Task(description="Test Task")
        self.assertEqual(task.description, "Test Task")

    def test_crew_creation(self):
        """Test that Crew can be created."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task")
        crew = Crew(agents=[agent], tasks=[task])
        self.assertEqual(len(crew.agents), 1)
        self.assertEqual(len(crew.tasks), 1)

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
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.role, "Test Role")
        self.assertEqual(agent.goal, "Test Goal")
        self.assertEqual(agent.backstory, "Test Backstory")
        self.assertTrue(agent.verbose)
        self.assertTrue(agent.allow_delegation)
        self.assertEqual(agent.tools, ["tool1", "tool2"])
        self.assertIsNotNone(agent.llm)

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
        self.assertEqual(task.description, "Test Task")
        self.assertEqual(task.expected_output, "Test Output")
        self.assertIsNotNone(task.agent)
        self.assertTrue(task.async_execution)
        self.assertEqual(task.context, ["context1", "context2"])
        self.assertEqual(task.tools, ["tool1", "tool2"])

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
        self.assertEqual(len(crew.agents), 1)
        self.assertEqual(len(crew.tasks), 1)
        self.assertEqual(crew.process, "sequential")
        self.assertTrue(crew.verbose)
        self.assertIsNotNone(crew.memory)
        self.assertTrue(crew.cache)

    def test_agent_execute(self):
        """Test that Agent can execute a task."""
        agent = Agent(name="Test Agent", role="Test Role")
        result = agent.execute("Test Task")
        self.assertEqual(result, "Executed: Test Task by Test Agent (Test Role)")

    def test_task_execute(self):
        """Test that Task can be executed."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        result = task.execute()
        self.assertEqual(result, "Executed: Test Task by Test Agent (Test Role)")

    def test_crew_kickoff(self):
        """Test that Crew can kickoff tasks."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.kickoff()
        self.assertEqual(result, ["Executed: Test Task by Test Agent (Test Role)"])

    def test_crew_run(self):
        """Test that Crew can run tasks."""
        agent = Agent(name="Test Agent", role="Test Role")
        task = Task(description="Test Task", agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        result = crew.run()
        self.assertEqual(result, ["Executed: Test Task by Test Agent (Test Role)"])
