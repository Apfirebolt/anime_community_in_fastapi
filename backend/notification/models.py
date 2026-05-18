"""Notification models for the anime community app."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.db import Base


class NotificationEventType(str, Enum):
    """Event types that can trigger notifications."""
    THREAD_REPLY = "thread_reply"  # Someone replied to a thread user created
    COMMENT_REPLY = "comment_reply"  # Someone replied to a comment user made
    THREAD_MENTION = "thread_mention"  # User mentioned in a thread
    COMMENT_MENTION = "comment_mention"  # User mentioned in a comment
    NEW_MESSAGE = "new_message"  # User received a new DM
    MODERATOR_ASSIGNED = "moderator_assigned"  # User assigned as moderator
    COMMUNITY_UPDATE = "community_update"  # Community update notification
    THREAD_PINNED = "thread_pinned"  # Thread was pinned
    CUSTOM = "custom"  # Custom event type


class Notification(Base):
    """Notification model for user notifications."""
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event type
    event_type = Column(SQLEnum(NotificationEventType), nullable=False, index=True)
    
    # Flexible payload to store event-specific data
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    actor_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True, index=True)  # Who triggered it
    related_entity_type = Column(String(50), nullable=True)  # "thread", "comment", "message", "community", etc.
    related_entity_id = Column(Integer, nullable=True, index=True)  # ID of the related entity
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    actor = relationship("User", foreign_keys=[actor_id], backref="notifications_triggered")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, event_type={self.event_type})>"
