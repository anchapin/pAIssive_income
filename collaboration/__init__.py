"""
Collaboration module for the pAIssive Income project.

This module provides functionality for team collaboration, project sharing,
and other collaborative features to enable teams to work together effectively
on AI solutions.
"""


from .access_control import Permission, Role, RoleManager
from .activity import ActivityLog, ActivityTracker, NotificationManager
from .comments import Comment, CommentSystem, Reaction
from .integration import CollaborationIntegration, IntegrationType
from .sharing import ProjectSharing, SharingPermission
from .version_control import VersionControl, VersionInfo
from .workspace import TeamWorkspace, WorkspaceManager

__all__

= [
# Workspace management
"TeamWorkspace",
"WorkspaceManager",
# Project sharing
"ProjectSharing",
"SharingPermission",
# Access control
"RoleManager",
"Role",
"Permission",
# Version control
"VersionControl",
"VersionInfo",
# Activity tracking
"ActivityTracker",
"ActivityLog",
"NotificationManager",
# Comments and feedback
"CommentSystem",
"Comment",
"Reaction",
# External integrations
"CollaborationIntegration",
"IntegrationType",
]