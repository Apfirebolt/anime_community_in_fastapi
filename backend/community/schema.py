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

    class Config:
        from_attributes = True
