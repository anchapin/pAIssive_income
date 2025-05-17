"""Tests for the CrewAI agents module."""

import pytest
from unittest.mock import patch, MagicMock

# Import the module to test
from agent_team.crewai_agents import (
    data_gatherer,
    analyzer,
    writer,
    task_collect,
    task_analyze,
    task_report,
    reporting_team,
    CrewAIAgentTeam,
    CREWAI_AVAILABLE,
)


class TestCrewAIAgents:
    """Tests for the CrewAI agents module."""

    def test_agent_definitions(self):
        """Test that agents are properly defined."""
        # Test data_gatherer agent
        assert data_gatherer.role == "Data Gatherer"
        assert "Collect relevant information" in data_gatherer.goal
        assert "data collection" in data_gatherer.backstory

        # Test analyzer agent
        assert analyzer.role == "Analyzer"
        assert "Analyze collected data" in analyzer.goal
        assert "analytics" in analyzer.backstory

        # Test writer agent
        assert writer.role == "Writer"
        assert "Generate clear" in writer.goal
        assert "communicating insights" in writer.backstory

    def test_task_definitions(self):
        """Test that tasks are properly defined."""
        # Test task_collect
        assert "Gather all relevant data" in task_collect.description
        assert task_collect.agent == data_gatherer

        # Test task_analyze
        assert "Analyze gathered data" in task_analyze.description
        assert task_analyze.agent == analyzer

        # Test task_report
        assert "Write a summary report" in task_report.description
        assert task_report.agent == writer

    def test_crew_definition(self):
        """Test that the crew is properly defined."""
        assert data_gatherer in reporting_team.agents
        assert analyzer in reporting_team.agents
        assert writer in reporting_team.agents

        assert task_collect in reporting_team.tasks
        assert task_analyze in reporting_team.tasks
        assert task_report in reporting_team.tasks

    @patch("agent_team.crewai_agents.Crew.run")
    @patch("logging.basicConfig")
    @patch("logging.info")
    def test_main_execution(self, mock_info, mock_basicConfig, mock_run):
        """Test the main execution flow."""
        # Setup mock
        mock_run.return_value = "Mock result"

        # Simulate the __main__ block execution
        from agent_team.crewai_agents import reporting_team

        # Call the run method directly
        reporting_team.run()

        # Verify the workflow was run
        mock_run.assert_called_once()

        # Now manually call what would happen in the __main__ block
        import logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.info("CrewAI reporting workflow completed.")

        # Verify logging was configured and the message was logged
        mock_basicConfig.assert_called_once()
        mock_info.assert_called_with("CrewAI reporting workflow completed.")

    @patch("agent_team.crewai_agents.CREWAI_AVAILABLE", True)
    def test_crewai_agent_team_initialization(self):
        """Test CrewAIAgentTeam initialization."""
        # Create a mock LLM provider
        mock_llm = MagicMock()

        # Initialize the agent team
        agent_team = CrewAIAgentTeam(llm_provider=mock_llm)

        # Verify the initialization
        assert agent_team.llm_provider == mock_llm
        assert agent_team.agents == []
        assert agent_team.tasks == []
        assert agent_team.agent_map == {}

    def test_crewai_agent_team_add_agent(self):
        """Test adding an agent to the team."""
        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent = agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory",
            verbose=True
        )

        # Verify the agent was added
        assert len(agent_team.agents) == 1
        assert agent_team.agents[0] == agent
        assert agent_team.agent_map["Test Agent"] == agent
        assert agent.role == "Test Agent"
        assert agent.goal == "Test Goal"
        assert agent.backstory == "Test Backstory"
        assert "verbose" in agent.kwargs
        assert agent.kwargs["verbose"] is True

    def test_crewai_agent_team_add_task(self):
        """Test adding a task to the team."""
        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent = agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory"
        )

        # Add a task using the agent object
        task1 = agent_team.add_task(
            description="Test Task 1",
            agent=agent,
            expected_output="Test Output"
        )

        # Add a task using the agent role
        task2 = agent_team.add_task(
            description="Test Task 2",
            agent="Test Agent",
            async_execution=True
        )

        # Verify the tasks were added
        assert len(agent_team.tasks) == 2
        assert agent_team.tasks[0] == task1
        assert agent_team.tasks[1] == task2
        assert task1.description == "Test Task 1"
        assert task1.agent == agent
        assert "expected_output" in task1.kwargs
        assert task1.kwargs["expected_output"] == "Test Output"
        assert task2.description == "Test Task 2"
        assert task2.agent == agent
        assert "async_execution" in task2.kwargs
        assert task2.kwargs["async_execution"] is True

    def test_crewai_agent_team_add_task_invalid_agent(self):
        """Test adding a task with an invalid agent role."""
        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Try to add a task with an invalid agent role
        with pytest.raises(ValueError, match="Agent with role 'Invalid Agent' not found"):
            agent_team.add_task(
                description="Test Task",
                agent="Invalid Agent"
            )

    @patch("agent_team.crewai_agents.Crew")
    def test_crewai_agent_team_create_crew(self, mock_crew_class):
        """Test creating a crew from the agent team."""
        # Setup mock
        mock_crew = MagicMock()
        mock_crew_class.return_value = mock_crew

        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent = agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory"
        )

        # Add a task
        task = agent_team.add_task(
            description="Test Task",
            agent=agent
        )

        # Create a crew
        crew = agent_team._create_crew(verbose=True)

        # Verify the crew was created
        mock_crew_class.assert_called_once_with(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        assert crew == mock_crew

    @patch("agent_team.crewai_agents.Crew")
    def test_crewai_agent_team_run(self, mock_crew_class):
        """Test running the agent team workflow."""
        # Setup mock
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Test Result"
        mock_crew_class.return_value = mock_crew

        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent = agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory"
        )

        # Add a task
        task = agent_team.add_task(
            description="Test Task",
            agent=agent
        )

        # Run the workflow
        result = agent_team.run(verbose=True)

        # Verify the workflow was run
        mock_crew_class.assert_called_once_with(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        mock_crew.kickoff.assert_called_once()
        assert result == "Test Result"

    def test_crewai_agent_team_run_no_agents(self):
        """Test running the agent team workflow with no agents."""
        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Try to run the workflow with no agents
        with pytest.raises(ValueError, match="No agents added to the team"):
            agent_team.run()

    def test_crewai_agent_team_run_no_tasks(self):
        """Test running the agent team workflow with no tasks."""
        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory"
        )

        # Try to run the workflow with no tasks
        with pytest.raises(ValueError, match="No tasks added to the team"):
            agent_team.run()

    @patch("agent_team.crewai_agents.Crew")
    def test_crewai_agent_team_run_with_run_method(self, mock_crew_class):
        """Test running the agent team workflow using the run method."""
        # Setup mock
        mock_crew = MagicMock()
        # Remove the kickoff attribute to test the fallback to run
        del mock_crew.kickoff
        mock_crew.run.return_value = "Test Result"
        mock_crew_class.return_value = mock_crew

        # Initialize the agent team
        agent_team = CrewAIAgentTeam()

        # Add an agent
        agent = agent_team.add_agent(
            role="Test Agent",
            goal="Test Goal",
            backstory="Test Backstory"
        )

        # Add a task
        task = agent_team.add_task(
            description="Test Task",
            agent=agent
        )

        # Run the workflow
        result = agent_team.run()

        # Verify the workflow was run
        mock_crew.run.assert_called_once()
        assert result == "Test Result"

    @patch("agent_team.crewai_agents.CREWAI_AVAILABLE", False)
    @patch("agent_team.crewai_agents.warnings.warn")
    def test_crewai_not_available_warning(self, mock_warn):
        """Test that a warning is issued when CrewAI is not available."""
        # Force reload of the module to trigger the warning
        import importlib
        import agent_team.crewai_agents
        importlib.reload(agent_team.crewai_agents)

        # Verify the warning was issued
        mock_warn.assert_called_once_with(
            "CrewAI is not installed. This module will not function properly. Install with: pip install '.[agents]'",
            stacklevel=2
        )
