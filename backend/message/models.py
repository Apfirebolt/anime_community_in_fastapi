from sqlalchemy import Column, Integer, String, Text, ForeignKey
from datetime import datetime
from backend.db import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Integer, default=0, nullable=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
