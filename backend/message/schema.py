from pydantic import BaseModel
from typing import Optional


class MessageCreate(BaseModel):
    receiver_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: int
    created_at: Optional[int]
    updated_at: Optional[int]
    is_active: Optional[int]

    class Config:
        from_attributes = True


class MessageUpdate(BaseModel):
    is_read: Optional[int] = None
