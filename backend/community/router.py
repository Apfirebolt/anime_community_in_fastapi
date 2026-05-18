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


@router.post("/{community_id}/threads", status_code=status.HTTP_201_CREATED, response_model=schema.ThreadOut)
async def create_thread(
    community_id: int,
    request: schema.ThreadCreate,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        thread = await services.create_thread(community_id, request, current_user.id)
        return thread
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create thread")


@router.get("/{community_id}/threads", response_model=List[schema.ThreadOut])
async def list_threads_for_community(community_id: int):
    return await services.list_threads(community_id)


@router.get("/threads/{thread_id}", response_model=schema.ThreadOut)
async def read_thread(thread_id: int):
    thread = await services.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return thread


@router.put("/threads/{thread_id}", response_model=schema.ThreadOut)
async def update_thread(
    thread_id: int,
    request: schema.ThreadUpdate,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        thread = await services.update_thread(thread_id, request, current_user.id)
        return thread
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update thread")


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: int, current_user: auth_schema.TokenData = Depends(get_current_user)):
    try:
        await services.delete_thread(thread_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete thread")
