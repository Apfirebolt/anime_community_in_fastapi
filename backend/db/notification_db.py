import os
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from backend import db as sync_db
from backend.notification import models


def _create_notification_sync(
    user_id: int,
    event_type: models.NotificationEventType,
    title: str,
    message: Optional[str] = None,
    actor_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
) -> models.Notification:
    db: Session = sync_db.SessionLocal()
    try:
        notification = models.Notification(
            user_id=user_id,
            event_type=event_type,
            title=title,
            message=message,
            actor_id=actor_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_notification_sync(notification_id: int) -> Optional[models.Notification]:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.Notification).get(notification_id)
    finally:
        db.close()


def _list_notifications_sync(user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0) -> List[models.Notification]:
    db: Session = sync_db.SessionLocal()
    try:
        query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
        if unread_only:
            query = query.filter(models.Notification.is_read == False)
        return query.order_by(models.Notification.created_at.desc()).offset(offset).limit(limit).all()
    finally:
        db.close()


def _count_unread_notifications_sync(user_id: int) -> int:
    db: Session = sync_db.SessionLocal()
    try:
        return db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.is_read == False).count()
    finally:
        db.close()


def _mark_notification_read_sync(notification_id: int) -> Optional[models.Notification]:
    db: Session = sync_db.SessionLocal()
    try:
        notification = db.query(models.Notification).get(notification_id)
        if not notification:
            return None
        notification.is_read = True
        notification.read_at = models.datetime.utcnow() if notification.read_at is None else notification.read_at
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _mark_all_notifications_read_sync(user_id: int) -> int:
    db: Session = sync_db.SessionLocal()
    try:
        notifications = db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.is_read == False).all()
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = models.datetime.utcnow()
            db.add(notification)
            count += 1
        db.commit()
        return count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _delete_notification_sync(notification_id: int) -> bool:
    db: Session = sync_db.SessionLocal()
    try:
        notification = db.query(models.Notification).get(notification_id)
        if not notification:
            return False
        db.delete(notification)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_notification(
    user_id: int,
    event_type: models.NotificationEventType,
    title: str,
    message: Optional[str] = None,
    actor_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
) -> models.Notification:
    return await run_in_threadpool(
        _create_notification_sync,
        user_id,
        event_type,
        title,
        message,
        actor_id,
        related_entity_type,
        related_entity_id,
    )


async def get_notification(notification_id: int) -> Optional[models.Notification]:
    return await run_in_threadpool(_get_notification_sync, notification_id)


async def list_notifications(user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0) -> List[models.Notification]:
    return await run_in_threadpool(_list_notifications_sync, user_id, unread_only, limit, offset)


async def count_unread_notifications(user_id: int) -> int:
    return await run_in_threadpool(_count_unread_notifications_sync, user_id)


async def mark_notification_read(notification_id: int) -> Optional[models.Notification]:
    return await run_in_threadpool(_mark_notification_read_sync, notification_id)


async def mark_all_notifications_read(user_id: int) -> int:
    return await run_in_threadpool(_mark_all_notifications_read_sync, user_id)


async def delete_notification(notification_id: int) -> bool:
    return await run_in_threadpool(_delete_notification_sync, notification_id)
