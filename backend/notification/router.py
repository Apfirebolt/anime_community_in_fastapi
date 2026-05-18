from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Optional

from backend.auth.jwt import get_current_user
from backend.auth import schema as auth_schema
from backend.notification import schema
from backend.notification import services
router = APIRouter(tags=["Notifications"], prefix="/api/notifications")


@router.get("/", response_model=schema.NotificationListOut)
async def list_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: Optional[bool] = False,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    notifications = await services.list_notifications(current_user.id, unread_only, limit, offset)
    unread_count = await services.count_unread_notifications(current_user.id)
    return schema.NotificationListOut(
        total=len(notifications),
        unread_count=unread_count,
        notifications=notifications,
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.NotificationOut)
async def create_notification(
    request: schema.NotificationCreate,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    if request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create notifications for other users")
    notification = await services.create_notification(
        user_id=request.user_id,
        event_type=request.event_type,
        title=request.title,
        message=request.message,
        actor_id=request.actor_id,
        related_entity_type=request.related_entity_type,
        related_entity_id=request.related_entity_id,
    )
    return notification


@router.put("/{notification_id}/read", response_model=schema.NotificationOut)
async def mark_notification_read(
    notification_id: int,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    notification = await services.get_notification(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    updated = await services.mark_notification_read(notification_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return updated


@router.put("/read_all", response_model=int)
async def mark_all_notifications_read(
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    return await services.mark_all_notifications_read(current_user.id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: auth_schema.TokenData = Depends(get_current_user),
):
    notification = await services.get_notification(notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    success = await services.delete_notification(notification_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete notification")
