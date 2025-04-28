"""
Session management functionality for the pAIssive_income project.

This module provides functions for managing user sessions,
including tracking active sessions and session termination.
"""

import uuid
import time
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from .models import User, UserPublic
from .token_refresh import blacklist_token

# Configure logger
logger = logging.getLogger(__name__)

# In-memory storage for active sessions
# In a production environment, this would be stored in a database
ACTIVE_SESSIONS: Dict[str, Dict] = {}  # session_id -> session_data


class Session:
    """
    Class representing a user session.
    """
    def __init__(self, user_id: str, token: str, device_info: Dict = None):
        """
        Initialize a new session.
        
        Args:
            user_id: ID of the user
            token: Authentication token
            device_info: Information about the device/browser
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.token = token
        self.created_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(days=1)  # Default 1 day expiry
        self.device_info = device_info or {}
        self.ip_address = None
        self.is_active = True
    
    def to_dict(self) -> Dict:
        """
        Convert session to dictionary.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "expires_at": self.expires_at,
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """
        Create a session from a dictionary.
        
        Args:
            data: Dictionary representation of a session
            
        Returns:
            Session object
        """
        session = cls(
            user_id=data["user_id"],
            token=data.get("token", ""),
            device_info=data.get("device_info", {})
        )
        session.id = data["id"]
        session.created_at = data["created_at"]
        session.last_active = data["last_active"]
        session.expires_at = data["expires_at"]
        session.ip_address = data.get("ip_address")
        session.is_active = data.get("is_active", True)
        return session


def create_session(user_id: str, token: str, device_info: Dict = None, ip_address: str = None) -> Session:
    """
    Create a new session for a user.
    
    Args:
        user_id: ID of the user
        token: Authentication token
        device_info: Information about the device/browser
        ip_address: IP address of the client
        
    Returns:
        New session object
    """
    session = Session(user_id, token, device_info)
    session.ip_address = ip_address
    
    # Store session
    ACTIVE_SESSIONS[session.id] = session.to_dict()
    
    logger.info(f"Created new session {session.id} for user {user_id}")
    return session


def get_session(session_id: str) -> Optional[Session]:
    """
    Get a session by ID.
    
    Args:
        session_id: ID of the session
        
    Returns:
        Session object if found, None otherwise
    """
    session_data = ACTIVE_SESSIONS.get(session_id)
    if not session_data:
        return None
    
    return Session.from_dict(session_data)


def get_user_sessions(user_id: str) -> List[Session]:
    """
    Get all active sessions for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of session objects
    """
    sessions = []
    for session_id, session_data in ACTIVE_SESSIONS.items():
        if session_data["user_id"] == user_id and session_data.get("is_active", True):
            sessions.append(Session.from_dict(session_data))
    
    return sessions


def update_session_activity(session_id: str) -> bool:
    """
    Update the last active time for a session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        True if session was updated, False otherwise
    """
    session_data = ACTIVE_SESSIONS.get(session_id)
    if not session_data:
        return False
    
    session_data["last_active"] = datetime.utcnow()
    ACTIVE_SESSIONS[session_id] = session_data
    
    return True


def terminate_session(session_id: str) -> bool:
    """
    Terminate a session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        True if session was terminated, False otherwise
    """
    session_data = ACTIVE_SESSIONS.get(session_id)
    if not session_data:
        return False
    
    # Mark session as inactive
    session_data["is_active"] = False
    ACTIVE_SESSIONS[session_id] = session_data
    
    # Blacklist the token
    token = session_data.get("token")
    if token:
        blacklist_token(token)
    
    logger.info(f"Terminated session {session_id} for user {session_data['user_id']}")
    return True


def terminate_all_user_sessions(user_id: str, except_session_id: str = None) -> int:
    """
    Terminate all sessions for a user, optionally except one.
    
    Args:
        user_id: ID of the user
        except_session_id: ID of session to keep active
        
    Returns:
        Number of sessions terminated
    """
    terminated_count = 0
    
    for session_id, session_data in ACTIVE_SESSIONS.items():
        if session_data["user_id"] == user_id and session_data.get("is_active", True):
            if except_session_id and session_id == except_session_id:
                continue
                
            if terminate_session(session_id):
                terminated_count += 1
    
    logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
    return terminated_count


def cleanup_expired_sessions() -> int:
    """
    Clean up expired sessions.
    
    Returns:
        Number of sessions removed
    """
    now = datetime.utcnow()
    expired_sessions = []
    
    for session_id, session_data in ACTIVE_SESSIONS.items():
        # Check if session is expired
        expires_at = session_data["expires_at"]
        if expires_at < now:
            expired_sessions.append(session_id)
        
        # Also check for inactive sessions older than 30 days
        if not session_data.get("is_active", True):
            created_at = session_data["created_at"]
            if created_at < now - timedelta(days=30):
                expired_sessions.append(session_id)
    
    # Remove expired sessions
    for session_id in expired_sessions:
        del ACTIVE_SESSIONS[session_id]
    
    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    return len(expired_sessions)
