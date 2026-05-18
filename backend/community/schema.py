from pydantic import BaseModel
from typing import Optional


class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    anime: Optional[str] = None


class CommunityOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    anime: Optional[str]
    creator_id: int
    created_at: Optional[int]
    updated_at: Optional[int]
    is_active: Optional[int]

    class Config:
        from_attributes = True


class ThreadCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ThreadOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    community_id: int
    creator_id: int
    created_at: Optional[int]
    updated_at: Optional[int]
    is_active: Optional[int]

    class Config:
        from_attributes = True


class ThreadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None


class ModeratorAssign(BaseModel):
    user_id: int


class ModeratorOut(BaseModel):
    id: int
    community_id: int
    user_id: int
    created_at: Optional[int]
    updated_at: Optional[int]
    is_active: Optional[int]

    class Config:
        from_attributes = True
