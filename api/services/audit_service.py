"""
Audit service for tracking security-related events.

This module provides services for recording and retrieving audit logs.
"""

import time


import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4



# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditEvent:
    """Audit event model."""

    def __init__(
        self,
        id: Optional[str] = None,
        event_type: str = "",
        resource_type: str = "",
        resource_id: Optional[str] = None,
        action: str = "",
        actor_id: Optional[str] = None,
        actor_type: str = "user",
        timestamp: Optional[datetime] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Initialize an audit event.

        Args:
            id: Event ID
            event_type: Type of event (e.g., "webhook.created")
            resource_type: Type of resource (e.g., "webhook")
            resource_id: ID of the resource
            action: Action performed (e.g., "create", "update", "delete")
            actor_id: ID of the actor who performed the action
            actor_type: Type of actor (e.g., "user", "system")
            timestamp: When the event occurred
            status: Status of the event (e.g., "success", "failure")
            details: Additional details about the event
            ip_address: IP address of the actor
            user_agent: User agent of the actor
        """
        self.id = id or str(uuid4())
        self.event_type = event_type
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.status = status
        self.details = details or {}
        self.ip_address = ip_address
        self.user_agent = user_agent

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the audit event to a dictionary.

        Returns:
            Dictionary representation of the audit event
        """
                return {
            "id": self.id,
            "event_type": self.event_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """
        Create an audit event from a dictionary.

        Args:
            data: Dictionary representation of the audit event

        Returns:
            Audit event instance
        """
        # Convert ISO format string to datetime object
        timestamp = (
            datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )

                return cls(
            id=data.get("id"),
            event_type=data.get("event_type", ""),
            resource_type=data.get("resource_type", ""),
            resource_id=data.get("resource_id"),
            action=data.get("action", ""),
            actor_id=data.get("actor_id"),
            actor_type=data.get("actor_type", "user"),
            timestamp=timestamp,
            status=data.get("status", "success"),
            details=data.get("details", {}),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
        )


class AuditService:
    """Service for recording and retrieving audit logs."""

    def __init__(self, storage_path: str = None):
        """
        Initialize the audit service.

        Args:
            storage_path: Path to the storage file
        """
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "../data/audit_logs.json"
        )
        self.audit_events: List[AuditEvent] = []

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # Load audit events from storage
        self._load()

    def _load(self) -> None:
        """Load audit events from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    data = json.load(f)

                for event_data in data:
                    event = AuditEvent.from_dict(event_data)
                    self.audit_events.append(event)
        except Exception as e:
            logger.error(f"Error loading audit events: {str(e)}")

    def _save(self) -> None:
        """Save audit events to storage."""
        try:
            data = [event.to_dict() for event in self.audit_events]

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving audit events: {str(e)}")

    def record_event(self, event: AuditEvent) -> AuditEvent:
        """
        Record an audit event.

        Args:
            event: Audit event to record

        Returns:
            Recorded audit event
        """
        # Add event to list
        self.audit_events.append(event)

        # Save to storage
        self._save()

        # Log the event
        logger.info(
            f"Audit event recorded: {event.event_type} - {event.action} - {event.resource_type}/{event.resource_id}"
        )

                return event

    def create_event(
        self,
        event_type: str,
        resource_type: str,
        action: str,
        resource_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        actor_type: str = "user",
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditEvent:
        """
        Create and record an audit event.

        Args:
            event_type: Type of event
            resource_type: Type of resource
            action: Action performed
            resource_id: ID of the resource
            actor_id: ID of the actor
            actor_type: Type of actor
            status: Status of the event
            details: Additional details
            ip_address: IP address of the actor
            user_agent: User agent of the actor

        Returns:
            Recorded audit event
        """
        # Create event
        event = AuditEvent(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            status=status,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Record event
                return self.record_event(event)

    def get_events(
        self,
        event_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """
        Get audit events matching the specified criteria.

        Args:
            event_type: Filter by event type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            action: Filter by action
            actor_id: Filter by actor ID
            status: Filter by status
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events to return
            offset: Number of events to skip

        Returns:
            List of matching audit events
        """
        # Filter events
        filtered_events = self.audit_events

        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]

        if resource_type:
            filtered_events = [
                e for e in filtered_events if e.resource_type == resource_type
            ]

        if resource_id:
            filtered_events = [
                e for e in filtered_events if e.resource_id == resource_id
            ]

        if action:
            filtered_events = [e for e in filtered_events if e.action == action]

        if actor_id:
            filtered_events = [e for e in filtered_events if e.actor_id == actor_id]

        if status:
            filtered_events = [e for e in filtered_events if e.status == status]

        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]

        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]

        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit and offset
                return filtered_events[offset : offset + limit]

    def get_event_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get an audit event by ID.

        Args:
            event_id: Event ID

        Returns:
            Audit event if found, None otherwise
        """
        for event in self.audit_events:
            if event.id == event_id:
                        return event

                return None