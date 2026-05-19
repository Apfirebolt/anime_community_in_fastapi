from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from backend.message import schema
from backend.message import services
from backend.auth.jwt import get_current_user
from backend.auth import schema as auth_schema


router = APIRouter(tags=["Messages"], prefix="/api/messages")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.MessageOut)
async def send_message(
    request: schema.MessageCreate,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        message = await services.send_message(current_user.id, request)
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send message")


@router.get("/", response_model=List[schema.MessageOut])
async def list_messages(current_user: auth_schema.TokenData = Depends(get_current_user)):
    return await services.list_user_messages(current_user.id)


@router.get("/{other_user_id}", response_model=List[schema.MessageOut])
async def list_conversation(
    other_user_id: int,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        return await services.list_conversation(current_user.id, other_user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{message_id}/read", response_model=schema.MessageOut)
async def mark_message_as_read(
    message_id: int,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        message = await services.mark_as_read(message_id, current_user.id)
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mark message as read")


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    try:
        await services.delete_message(message_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete message")
