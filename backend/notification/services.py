from typing import List, Optional

from . import schema
from . import models
from backend.db import notification_db
from backend.db import auth_db


class NotificationService:
    async def create_notification(
        self,
        user_id: int,
        event_type: models.NotificationEventType,
        title: str,
        message: Optional[str] = None,
        actor_id: Optional[int] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
    ) -> models.Notification:
        return await notification_db.create_notification(
            user_id=user_id,
            event_type=event_type,
            title=title,
            message=message,
            actor_id=actor_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )

    async def get_notification(self, notification_id: int) -> Optional[models.Notification]:
        return await notification_db.get_notification(notification_id)

    async def list_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[models.Notification]:
        return await notification_db.list_notifications(user_id, unread_only, limit, offset)

    async def count_unread_notifications(self, user_id: int) -> int:
        return await notification_db.count_unread_notifications(user_id)

    async def mark_notification_read(self, notification_id: int) -> Optional[models.Notification]:
        return await notification_db.mark_notification_read(notification_id)

    async def mark_all_notifications_read(self, user_id: int) -> int:
        return await notification_db.mark_all_notifications_read(user_id)

    async def delete_notification(self, notification_id: int) -> bool:
        return await notification_db.delete_notification(notification_id)

    async def notify_thread_owner_of_new_comment(self, thread_owner_id: int, actor_id: int, thread_id: int, actor_name: str, comment_content: str) -> models.Notification:
        title = f"{actor_name} replied to your thread"
        message = comment_content.strip()[:255]
        return await self.create_notification(
            user_id=thread_owner_id,
            event_type=models.NotificationEventType.THREAD_REPLY,
            title=title,
            message=message,
            actor_id=actor_id,
            related_entity_type="thread",
            related_entity_id=thread_id,
        )


notification_service = NotificationService()


async def create_notification(
    user_id: int,
    event_type: models.NotificationEventType,
    title: str,
    message: Optional[str] = None,
    actor_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
) -> models.Notification:
    return await notification_service.create_notification(
        user_id,
        event_type,
        title,
        message,
        actor_id,
        related_entity_type,
        related_entity_id,
    )


async def list_notifications(user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0) -> list[models.Notification]:
    return await notification_service.list_notifications(user_id, unread_only, limit, offset)


async def count_unread_notifications(user_id: int) -> int:
    return await notification_service.count_unread_notifications(user_id)


async def mark_notification_read(notification_id: int) -> Optional[models.Notification]:
    return await notification_service.mark_notification_read(notification_id)


async def mark_all_notifications_read(user_id: int) -> int:
    return await notification_service.mark_all_notifications_read(user_id)


async def delete_notification(notification_id: int) -> bool:
    return await notification_service.delete_notification(notification_id)


async def notify_thread_owner_of_new_comment(thread_owner_id: int, actor_id: int, thread_id: int, actor_name: str, comment_content: str) -> models.Notification:
    return await notification_service.notify_thread_owner_of_new_comment(
        thread_owner_id,
        actor_id,
        thread_id,
        actor_name,
        comment_content,
    )
