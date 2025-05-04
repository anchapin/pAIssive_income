"""
Agent Team service for the pAIssive Income API.

This module provides a service for interacting with the agent team endpoints.
"""

from typing import Any, Dict

from .base import BaseService

class AgentTeamService(BaseService):
    """
    Agent Team service.
    """

    def create_team(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an agent team.

        Args:
            data: Team creation data
                - name: Team name
                - description: Team description
                - agents: List of agent IDs or configurations

        Returns:
            Created team
        """
        return self._post("agent - team / teams", data)

    def get_teams(self) -> Dict[str, Any]:
        """
        Get all agent teams.

        Returns:
            List of agent teams
        """
        return self._get("agent - team / teams")

    def get_team(self, team_id: str) -> Dict[str, Any]:
        """
        Get details for a specific agent team.

        Args:
            team_id: Team ID

        Returns:
            Team details
        """
        return self._get(f"agent - team / teams/{team_id}")

    def update_team(self, team_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an agent team.

        Args:
            team_id: Team ID
            data: Updated team data

        Returns:
            Updated team
        """
        return self._put(f"agent - team / teams/{team_id}", data)

    def delete_team(self, team_id: str) -> Dict[str, Any]:
        """
        Delete an agent team.

        Args:
            team_id: Team ID

        Returns:
            Result of the deletion
        """
        return self._delete(f"agent - team / teams/{team_id}")

    def get_agents(self) -> Dict[str, Any]:
        """
        Get all available agents.

        Returns:
            List of agents
        """
        return self._get("agent - team / agents")

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get details for a specific agent.

        Args:
            agent_id: Agent ID

        Returns:
            Agent details
        """
        return self._get(f"agent - team / agents/{agent_id}")

    def get_workflows(self) -> Dict[str, Any]:
        """
        Get all available workflows.

        Returns:
            List of workflows
        """
        return self._get("agent - team / workflows")

    def run_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a workflow with an agent team.

        Args:
            data: Workflow execution data
                - team_id: Team ID
                - workflow_id: Workflow ID
                - inputs: Workflow inputs

        Returns:
            Workflow execution results
        """
        return self._post("agent - team / workflows / run", data)
