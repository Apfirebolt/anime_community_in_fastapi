"""Pydantic schemas for notification API."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from backend.notification.models import NotificationEventType


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    user_id: int
    event_type: NotificationEventType
    title: str
    message: Optional[str] = None
    actor_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    """Schema for updating notification (mark as read)."""
    is_read: bool


class NotificationOut(BaseModel):
    """Schema for notification output."""
    id: int
    user_id: int
    event_type: NotificationEventType
    title: str
    message: Optional[str]
    actor_id: Optional[int]
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class NotificationListOut(BaseModel):
    """Schema for notification list with metadata."""
    total: int
    unread_count: int
    notifications: list[NotificationOut]
