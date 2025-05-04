"""
Integration with external collaboration tools.

This module provides classes for integrating with external collaboration tools
such as GitHub, Slack, Microsoft Teams, and others.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

# Set up logging
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    """Types of external integrations supported."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    TRELLO = "trello"
    JIRA = "jira"
    ASANA = "asana"
    NOTION = "notion"
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    DROPBOX = "dropbox"
    CUSTOM = "custom"

class CollaborationIntegration:
    """
    Manages integrations with external collaboration tools.

    This class provides functionality for connecting to and interacting with
    external tools to enhance collaboration capabilities.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the integration manager.

        Args:
            storage_path: Path where integration data will be stored
        """
        self.storage_path = storage_path or "integrations"
        os.makedirs(self.storage_path, exist_ok=True)

        self.integrations: Dict[str, Dict[str, Any]] = {}
        self.workspace_integrations: Dict[str, List[str]] = {}

        self._load_integration_data()

    def _load_integration_data(self):
        """Load integration data from disk."""
        integrations_file = os.path.join(self.storage_path, "integrations.json")
        workspace_integrations_file = os.path.join(self.storage_path, 
            "workspace_integrations.json")

        if os.path.exists(integrations_file):
            try:
                with open(integrations_file, "r") as f:
                    self.integrations = json.load(f)
                logger.info(f"Loaded {len(self.integrations)} integrations")
            except Exception as e:
                logger.error(f"Failed to load integrations: {e}")
                self.integrations = {}

        if os.path.exists(workspace_integrations_file):
            try:
                with open(workspace_integrations_file, "r") as f:
                    self.workspace_integrations = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load workspace integrations: {e}")
                self.workspace_integrations = {}

    def _save_integration_data(self):
        """Save integration data to disk."""
        integrations_file = os.path.join(self.storage_path, "integrations.json")
        workspace_integrations_file = os.path.join(self.storage_path, 
            "workspace_integrations.json")

        with open(integrations_file, "w") as f:
            json.dump(self.integrations, f, indent=2)

        with open(workspace_integrations_file, "w") as f:
            json.dump(self.workspace_integrations, f, indent=2)

    def add_integration(self,
                       workspace_id: str,
                       integration_type: IntegrationType,
                       name: str,
                       config: Dict[str, Any],
                       created_by: str) -> Dict[str, Any]:
        """
        Add an integration to a workspace.

        Args:
            workspace_id: ID of the workspace
            integration_type: Type of integration
            name: Name of the integration
            config: Configuration for the integration
            created_by: ID of the user creating the integration

        Returns:
            Integration information
        """
        integration_id = str(uuid.uuid4())

        # Create integration information
        integration = {
            "integration_id": integration_id,
            "workspace_id": workspace_id,
            "integration_type": integration_type.value,
            "name": name,
            "config": config,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "last_sync": None,
            "metadata": {}
        }

        # Store integration
        self.integrations[integration_id] = integration

        # Update workspace integrations
        if workspace_id not in self.workspace_integrations:
            self.workspace_integrations[workspace_id] = []
        self.workspace_integrations[workspace_id].append(integration_id)

        self._save_integration_data()

        logger.info(
            f"Added {integration_type.value} integration '{name}' to workspace" \
             + "{workspace_id}")
        return integration

    def update_integration(self,
                          integration_id: str,
                          updated_by: str,
                          name: Optional[str] = None,
                          config: Optional[
    Dict[str,Any]
]] = None) -> Optional[Dict[str, 
                              Any]]:
        """
        Update an integration.

        Args:
            integration_id: ID of the integration
            name: Optional new name for the integration
            config: Optional new configuration for the integration
            updated_by: ID of the user updating the integration

        Returns:
            Updated integration information or None if not found
        """
        if integration_id not in self.integrations:
            logger.error(f"Integration {integration_id} not found")
            return None

        integration = self.integrations[integration_id]

        if name:
            integration["name"] = name

        if config:
            integration["config"] = config

        integration["updated_at"] = datetime.now().isoformat()
        integration["updated_by"] = updated_by

        self._save_integration_data()

        logger.info(f"Updated integration {integration_id}")
        return integration

    def delete_integration(self, integration_id: str, deleted_by: str) -> bool:
        """
        Delete an integration.

        Args:
            integration_id: ID of the integration
            deleted_by: ID of the user deleting the integration

        Returns:
            True if the integration was deleted, False otherwise
        """
        if integration_id not in self.integrations:
            logger.error(f"Integration {integration_id} not found")
            return False

        integration = self.integrations[integration_id]
        workspace_id = integration["workspace_id"]

        # Remove integration from workspace integrations
        if workspace_id in self.workspace_integrations and \
            integration_id in self.workspace_integrations[workspace_id]:
            self.workspace_integrations[workspace_id].remove(integration_id)

        # Remove integration
        del self.integrations[integration_id]

        self._save_integration_data()

        logger.info(f"Deleted integration {integration_id}")
        return True

    def get_integration(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an integration by ID.

        Args:
            integration_id: ID of the integration

        Returns:
            Integration information or None if not found
        """
        return self.integrations.get(integration_id)

    def get_workspace_integrations(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Get all integrations for a workspace.

        Args:
            workspace_id: ID of the workspace

        Returns:
            List of integration information
        """
        if workspace_id not in self.workspace_integrations:
            return []

        integrations = []
        for integration_id in self.workspace_integrations[workspace_id]:
            integration = self.get_integration(integration_id)
            if integration:
                integrations.append(integration)

        return integrations

    def get_integrations_by_type(self, workspace_id: str, 
        integration_type: IntegrationType) -> List[Dict[str, Any]]:
        """
        Get integrations of a specific type for a workspace.

        Args:
            workspace_id: ID of the workspace
            integration_type: Type of integration

        Returns:
            List of integration information
        """
        integrations = self.get_workspace_integrations(workspace_id)
        return [i for i in integrations if i["integration_type"] == \
            integration_type.value]

    def sync_integration(self, integration_id: str) -> Dict[str, Any]:
        """
        Synchronize an integration with the external service.

        Args:
            integration_id: ID of the integration

        Returns:
            Sync result information

        Raises:
            ValueError: If the integration does not exist
        """
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")

        integration = self.integrations[integration_id]
        integration_type = integration["integration_type"]

        # Perform sync based on integration type
        result = {
            "integration_id": integration_id,
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "",
            "data": {}
        }

        try:
            if integration_type == IntegrationType.GITHUB.value:
                result = self._sync_github(integration)
            elif integration_type == IntegrationType.GITLAB.value:
                result = self._sync_gitlab(integration)
            elif integration_type == IntegrationType.SLACK.value:
                result = self._sync_slack(integration)
            elif integration_type == IntegrationType.TEAMS.value:
                result = self._sync_teams(integration)
            elif integration_type == IntegrationType.JIRA.value:
                result = self._sync_jira(integration)
            elif integration_type == IntegrationType.TRELLO.value:
                result = self._sync_trello(integration)
            else:
                result["message"] = f"Sync not implemented for {integration_type}"
                logger.warning(result["message"])
        except Exception as e:
            result["message"] = f"Sync failed: {str(e)}"
            logger.error(f"Sync failed for integration {integration_id}: {e}")

        # Update integration with sync result
        integration["last_sync"] = result["sync_time"]
        integration["last_sync_status"] = "success" if result["success"] else "failed"
        integration["last_sync_message"] = result["message"]

        self._save_integration_data()

        return result

    def _sync_github(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with GitHub.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        config = integration["config"]
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "",
            "data": {}
        }

        # Check for required configuration
        if "token" not in config or "repository" not in config:
            result["message"] = "Missing required configuration: token and repository"
            return result

        # Make API request to GitHub
        token = config["token"]
        repo = config["repository"]
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application / vnd.github.v3 + json"
        }

        try:
            # Get repository information
            repo_url = f"https://api.github.com / repos/{repo}"
            repo_response = requests.get(repo_url, headers=headers)
            repo_response.raise_for_status()

            # Get recent commits
            commits_url = f"{repo_url}/commits"
            commits_response = requests.get(commits_url, headers=headers)
            commits_response.raise_for_status()

            # Get issues
            issues_url = f"{repo_url}/issues"
            issues_response = requests.get(issues_url, headers=headers)
            issues_response.raise_for_status()

            # Store data
            result["data"] = {
                "repository": repo_response.json(),
                "commits": commits_response.json()[:10],  # Last 10 commits
                "issues": issues_response.json()
            }

            result["success"] = True
            result["message"] = "Successfully synchronized with GitHub"

        except requests.exceptions.RequestException as e:
            result["message"] = f"GitHub API request failed: {str(e)}"

        return result

    def _sync_gitlab(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with GitLab.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        # Implementation similar to GitHub sync
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "GitLab sync not fully implemented",
            "data": {}
        }
        return result

    def _sync_slack(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Slack.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        # Implementation for Slack sync
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "Slack sync not fully implemented",
            "data": {}
        }
        return result

    def _sync_teams(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Microsoft Teams.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        # Implementation for Teams sync
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "Microsoft Teams sync not fully implemented",
            "data": {}
        }
        return result

    def _sync_jira(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Jira.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        # Implementation for Jira sync
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "Jira sync not fully implemented",
            "data": {}
        }
        return result

    def _sync_trello(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize with Trello.

        Args:
            integration: Integration information

        Returns:
            Sync result information
        """
        # Implementation for Trello sync
        result = {
            "integration_id": integration["integration_id"],
            "sync_time": datetime.now().isoformat(),
            "success": False,
            "message": "Trello sync not fully implemented",
            "data": {}
        }
        return result

    def send_notification(self,
                         integration_id: str,
                         message: str,
                         channel: Optional[str] = None,
                         title: Optional[str] = None,
                         link: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification through an integration.

        Args:
            integration_id: ID of the integration
            message: Message to send
            channel: Optional channel or destination
            title: Optional title for the message
            link: Optional link to include

        Returns:
            Notification result information

        Raises:
            ValueError: If the integration does not exist
        """
        if integration_id not in self.integrations:
            raise ValueError(f"Integration {integration_id} not found")

        integration = self.integrations[integration_id]
        integration_type = integration["integration_type"]

        # Send notification based on integration type
        result = {
            "integration_id": integration_id,
            "time": datetime.now().isoformat(),
            "success": False,
            "message": "",
            "data": {}
        }

        try:
            if integration_type == IntegrationType.SLACK.value:
                result = self._send_slack_notification(integration, message, channel, 
                    title, link)
            elif integration_type == IntegrationType.TEAMS.value:
                result = self._send_teams_notification(integration, message, channel, 
                    title, link)
            elif integration_type == IntegrationType.DISCORD.value:
                result = self._send_discord_notification(integration, message, channel, 
                    title, link)
            else:
                result["message"] = \
                    f"Notifications not implemented for {integration_type}"
                logger.warning(result["message"])
        except Exception as e:
            result["message"] = f"Notification failed: {str(e)}"
            logger.error(f"Notification failed for integration {integration_id}: {e}")

        return result

    def _send_slack_notification(self,
                               integration: Dict[str, Any],
                               message: str,
                               channel: Optional[str] = None,
                               title: Optional[str] = None,
                               link: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to Slack.

        Args:
            integration: Integration information
            message: Message to send
            channel: Optional channel
            title: Optional title for the message
            link: Optional link to include

        Returns:
            Notification result information
        """
        config = integration["config"]
        result = {
            "integration_id": integration["integration_id"],
            "time": datetime.now().isoformat(),
            "success": False,
            "message": "",
            "data": {}
        }

        # Check for required configuration
        if "webhook_url" not in config:
            result["message"] = "Missing required configuration: webhook_url"
            return result

        webhook_url = config["webhook_url"]

        # Prepare payload
        payload = {
            "text": message
        }

        if channel:
            payload["channel"] = channel

        if title or link:
            payload["attachments"] = [{
                "title": title or "Notification",
                "text": message,
                "title_link": link
            }]

        try:
            # Send to Slack
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()

            result["success"] = True
            result["message"] = "Successfully sent notification to Slack"
            result["data"] = {"response": response.text}

        except requests.exceptions.RequestException as e:
            result["message"] = f"Slack API request failed: {str(e)}"

        return result

    def _send_teams_notification(self,
                               integration: Dict[str, Any],
                               message: str,
                               channel: Optional[str] = None,
                               title: Optional[str] = None,
                               link: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to Microsoft Teams.

        Args:
            integration: Integration information
            message: Message to send
            channel: Optional channel
            title: Optional title for the message
            link: Optional link to include

        Returns:
            Notification result information
        """
        # Implementation for Teams notification
        result = {
            "integration_id": integration["integration_id"],
            "time": datetime.now().isoformat(),
            "success": False,
            "message": "Microsoft Teams notifications not fully implemented",
            "data": {}
        }
        return result

    def _send_discord_notification(self,
                                 integration: Dict[str, Any],
                                 message: str,
                                 channel: Optional[str] = None,
                                 title: Optional[str] = None,
                                 link: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a notification to Discord.

        Args:
            integration: Integration information
            message: Message to send
            channel: Optional channel
            title: Optional title for the message
            link: Optional link to include

        Returns:
            Notification result information
        """
        # Implementation for Discord notification
        result = {
            "integration_id": integration["integration_id"],
            "time": datetime.now().isoformat(),
            "success": False,
            "message": "Discord notifications not fully implemented",
            "data": {}
        }
        return result
