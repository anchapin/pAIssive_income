"""
Agent Team Service for the pAIssive Income UI.

This service provides methods for interacting with the Agent Team module.
"""

import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from common_utils import format_datetime
from interfaces.ui_interfaces import IAgentTeamService

from .base_service import BaseService

# Set up logging
logger = logging.getLogger(__name__)


class AgentTeamService(BaseService, IAgentTeamService):
    """
    Service for interacting with the Agent Team module.
    """

    def __init__(self):
        """Initialize the Agent Team service."""
        super().__init__()
        self.projects_file = "projects.json"

        # Import the AgentTeam class
        try:
            from agent_team import AgentTeam

            self.agent_team_available = True
        except ImportError:
            logger.warning("Agent Team module not available. Using mock data.")
            self.agent_team_available = False

    def create_project(
        self, project_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new project with an agent team.

        Args:
            project_name: Name of the project
            config: Optional configuration for the agent team

        Returns:
            Project data
        """
        if self.agent_team_available:
            try:
                from agent_team import AgentTeam

                team = AgentTeam(project_name, config_path=None)

                from datetime import datetime

                now = datetime.now()
                project = {
                    "id": str(uuid.uuid4()),
                    "name": project_name,
                    "created_at": format_datetime(now, "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "updated_at": format_datetime(now, "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "status": "active",
                    "team_id": team.id if hasattr(team, "id") else str(uuid.uuid4()),
                    "config": config or {},
                }
            except Exception as e:
                logger.error(f"Error creating agent team: {e}")
                project = self._create_mock_project(project_name, config)
        else:
            project = self._create_mock_project(project_name, config)

        # Save the project
        projects = self.get_projects()
        projects.append(project)
        self.save_data(self.projects_file, projects)

        return project

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.

        Returns:
            List of projects
        """
        projects = self.load_data(self.projects_file)
        if projects is None:
            projects = []
            self.save_data(self.projects_file, projects)
        return projects

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID.

        Args:
            project_id: ID of the project

        Returns:
            Project data, or None if not found
        """
        projects = self.get_projects()
        for project in projects:
            if project["id"] == project_id:
                return project
        return None

    def update_project(
        self, project_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a project.

        Args:
            project_id: ID of the project
            updates: Updates to apply to the project

        Returns:
            Updated project data, or None if not found
        """
        projects = self.get_projects()
        for i, project in enumerate(projects):
            if project["id"] == project_id:
                project.update(updates)
                from datetime import datetime

                project["updated_at"] = format_datetime(
                    datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                projects[i] = project
                self.save_data(self.projects_file, projects)
                return project
        return None

    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.

        Args:
            project_id: ID of the project

        Returns:
            True if successful, False otherwise
        """
        projects = self.get_projects()
        for i, project in enumerate(projects):
            if project["id"] == project_id:
                del projects[i]
                self.save_data(self.projects_file, projects)
                return True
        return False

    def _create_mock_project(
        self, project_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a mock project for testing.

        Args:
            project_name: Name of the project
            config: Optional configuration for the agent team

        Returns:
            Mock project data
        """
        from datetime import datetime

        now = datetime.now()
        return {
            "id": str(uuid.uuid4()),
            "name": project_name,
            "created_at": format_datetime(now, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated_at": format_datetime(now, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "status": "active",
            "team_id": str(uuid.uuid4()),
            "config": config or {},
            "is_mock": True,
        }
