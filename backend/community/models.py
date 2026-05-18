from sqlalchemy import Column, Integer, String, Text, ForeignKey
from datetime import datetime
from backend.db import Base


class Community(Base):
    __tablename__ = "community"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    anime = Column(String(100), nullable=True)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    

class Thread(Base):
    __tablename__ = "thread"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    community_id = Column(Integer, ForeignKey("community.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)


class CommunityModerator(Base):
    __tablename__ = "community_moderator"

    id = Column(Integer, primary_key=True, autoincrement=True)
    community_id = Column(Integer, ForeignKey("community.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)


class ThreadComment(Base):
    __tablename__ = "thread_comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, ForeignKey("thread.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
        