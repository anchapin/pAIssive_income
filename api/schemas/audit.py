"""
"""
Audit schemas for the API server.
Audit schemas for the API server.
"""
"""


import time
import time
from datetime import datetime
from datetime import datetime
from enum import Enum
from enum import Enum
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List, Optional


from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, ConfigDict, Field




class AuditEventType
class AuditEventType


(str, Enum):
    (str, Enum):
    """Types of audit events."""

    # Webhook events
    WEBHOOK_CREATED = "webhook.created"
    WEBHOOK_UPDATED = "webhook.updated"
    WEBHOOK_DELETED = "webhook.deleted"
    WEBHOOK_DELIVERY_SENT = "webhook.delivery.sent"
    WEBHOOK_DELIVERY_FAILED = "webhook.delivery.failed"
    WEBHOOK_DELIVERY_RETRIED = "webhook.delivery.retried"
    WEBHOOK_SIGNATURE_FAILED = "webhook.signature.failed"
    WEBHOOK_IP_BLOCKED = "webhook.ip.blocked"
    WEBHOOK_RATE_LIMITED = "webhook.rate_limited"

    # API key events
    API_KEY_CREATED = "api_key.created"
    API_KEY_UPDATED = "api_key.updated"
    API_KEY_DELETED = "api_key.deleted"
    API_KEY_EXPIRED = "api_key.expired"
    API_KEY_REVOKED = "api_key.revoked"

    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_LOGIN_FAILED = "user.login.failed"

    # Security events
    AUTH_FAILED = "auth.failed"
    AUTH_SUCCESS = "auth.success"
    PERMISSION_DENIED = "permission.denied"


    class AuditResourceType(str, Enum):

    WEBHOOK = "webhook"
    WEBHOOK_DELIVERY = "webhook_delivery"
    API_KEY = "api_key"
    USER = "user"
    SYSTEM = "system"


    class AuditAction(str, Enum):

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEND = "send"
    RETRY = "retry"
    BLOCK = "block"
    LIMIT = "limit"
    LOGIN = "login"
    LOGOUT = "logout"
    VERIFY = "verify"
    REVOKE = "revoke"


    class AuditStatus(str, Enum):

    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"


    class AuditActorType(str, Enum):


    USER = "user"
    USER = "user"
    SYSTEM = "system"
    SYSTEM = "system"
    API_KEY = "api_key"
    API_KEY = "api_key"
    SERVICE = "service"
    SERVICE = "service"




    class AuditEventBase(BaseModel):
    class AuditEventBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    model_config = ConfigDict(protected_namespaces=()))
    """Base schema for audit events."""
    event_type: AuditEventType = Field(..., description="Type of event")
    resource_type: AuditResourceType = Field(..., description="Type of resource")
    action: AuditAction = Field(..., description="Action performed")
    resource_id: Optional[str] = Field(None, description="ID of the resource")
    actor_id: Optional[str] = Field(None, description="ID of the actor")
    actor_type: AuditActorType = Field(AuditActorType.USER, description="Type of actor")
    status: AuditStatus = Field(AuditStatus.SUCCESS, description="Status of the event")
    details: Dict[str, Any] = Field(
    default_factory=dict, description="Additional details"
    )
    ip_address: Optional[str] = Field(None, description="IP address of the actor")
    user_agent: Optional[str] = Field(None, description="User agent of the actor")


    class AuditEventCreate(AuditEventBase):

    pass


    class AuditEventResponse(AuditEventBase):

    id: str = Field(..., description="Event ID")
    timestamp: datetime = Field(..., description="When the event occurred")

    class Config:

    orm_mode = True


    class AuditEventList(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for listing audit events."""
    items: List[AuditEventResponse] = Field(..., description="List of audit events")
    total: int = Field(..., description="Total number of audit events")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(..., description="Number of audit events per page")
    pages: int = Field(..., description="Total number of pages")


    class AuditEventFilter(BaseModel):
    model_config = ConfigDict(protected_namespaces=()))
    """Schema for filtering audit events."""
    event_type: Optional[AuditEventType] = Field(
    None, description="Filter by event type"
    )
    resource_type: Optional[AuditResourceType] = Field(
    None, description="Filter by resource type"
    )
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    action: Optional[AuditAction] = Field(None, description="Filter by action")
    actor_id: Optional[str] = Field(None, description="Filter by actor ID")
    status: Optional[AuditStatus] = Field(None, description="Filter by status")
    start_time: Optional[datetime] = Field(None, description="Filter by start time"
    end_time: Optional[datetime] = Field(None, description="Filter by end time"