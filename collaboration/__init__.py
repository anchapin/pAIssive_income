"""
"""
Collaboration module for the pAIssive Income project.
Collaboration module for the pAIssive Income project.


This module provides functionality for team collaboration, project sharing,
This module provides functionality for team collaboration, project sharing,
and other collaborative features to enable teams to work together effectively
and other collaborative features to enable teams to work together effectively
on AI solutions.
on AI solutions.
"""
"""




from .access_control import Permission, Role, RoleManager
from .access_control import Permission, Role, RoleManager
from .activity import ActivityLog, ActivityTracker, NotificationManager
from .activity import ActivityLog, ActivityTracker, NotificationManager
from .comments import Comment, CommentSystem, Reaction
from .comments import Comment, CommentSystem, Reaction
from .integration import CollaborationIntegration, IntegrationType
from .integration import CollaborationIntegration, IntegrationType
from .sharing import ProjectSharing, SharingPermission
from .sharing import ProjectSharing, SharingPermission
from .version_control import VersionControl, VersionInfo
from .version_control import VersionControl, VersionInfo
from .workspace import TeamWorkspace, WorkspaceManager
from .workspace import TeamWorkspace, WorkspaceManager


__all__
__all__


= [
= [
# Workspace management
# Workspace management
"TeamWorkspace",
"TeamWorkspace",
"WorkspaceManager",
"WorkspaceManager",
# Project sharing
# Project sharing
"ProjectSharing",
"ProjectSharing",
"SharingPermission",
"SharingPermission",
# Access control
# Access control
"RoleManager",
"RoleManager",
"Role",
"Role",
"Permission",
"Permission",
# Version control
# Version control
"VersionControl",
"VersionControl",
"VersionInfo",
"VersionInfo",
# Activity tracking
# Activity tracking
"ActivityTracker",
"ActivityTracker",
"ActivityLog",
"ActivityLog",
"NotificationManager",
"NotificationManager",
# Comments and feedback
# Comments and feedback
"CommentSystem",
"CommentSystem",
"Comment",
"Comment",
"Reaction",
"Reaction",
# External integrations
# External integrations
"CollaborationIntegration",
"CollaborationIntegration",
"IntegrationType",
"IntegrationType",
]
]