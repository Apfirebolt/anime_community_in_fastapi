from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from backend.community import schema
from backend.community import services
from backend.auth.jwt import get_current_user
from backend.auth import schema as auth_schema


router = APIRouter(tags=["Community"], prefix="/api/community")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.CommunityOut)
async def create_community(request: schema.CommunityCreate, current_user: auth_schema.TokenData = Depends(get_current_user)):
    try:
        community = await services.create_community(request, current_user.id)
        return community
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create community")


@router.get("/{community_id}", response_model=schema.CommunityOut)
async def read_community(community_id: int):
    community = await services.get_community(community_id)
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")
    return community


@router.get("/", response_model=List[schema.CommunityOut])
async def list_all_communities():
    return await services.list_communities()
