"""
Collaboration module for the pAIssive Income project.

This module provides functionality for team collaboration, project sharing,
and other collaborative features to enable teams to work together effectively
on AI solutions.
"""

from .workspace import TeamWorkspace, WorkspaceManager
from .sharing import ProjectSharing, SharingPermission
from .access_control import RoleManager, Role, Permission
from .version_control import VersionControl, VersionInfo
from .activity import ActivityTracker, ActivityLog, NotificationManager
from .comments import CommentSystem, Comment, Reaction
from .integration import CollaborationIntegration, IntegrationType

__all__ = [
    # Workspace management
    'TeamWorkspace',
    'WorkspaceManager',
    
    # Project sharing
    'ProjectSharing',
    'SharingPermission',
    
    # Access control
    'RoleManager',
    'Role',
    'Permission',
    
    # Version control
    'VersionControl',
    'VersionInfo',
    
    # Activity tracking
    'ActivityTracker',
    'ActivityLog',
    'NotificationManager',
    
    # Comments and feedback
    'CommentSystem',
    'Comment',
    'Reaction',
    
    # External integrations
    'CollaborationIntegration',
    'IntegrationType'
]
