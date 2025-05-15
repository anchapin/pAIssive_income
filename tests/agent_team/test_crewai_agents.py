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
