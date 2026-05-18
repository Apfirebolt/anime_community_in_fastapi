from typing import List, Optional

from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select
from fastapi.concurrency import run_in_threadpool

from backend import db as sync_db
from backend.message import models


def _create_message_sync(sender_id: int, receiver_id: int, content: str) -> models.Message:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        message = models.Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            created_at=now,
            updated_at=now,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_message_sync(message_id: int) -> Optional[models.Message]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Message).where(models.Message.id == message_id)
        return db.execute(stmt).scalars().first()
    finally:
        db.close()


def _list_user_messages_sync(user_id: int) -> List[models.Message]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Message).where(
            (models.Message.receiver_id == user_id) | (models.Message.sender_id == user_id)
        )
        return db.execute(stmt).scalars().all()
    finally:
        db.close()


def _list_conversation_sync(user_id: int, other_user_id: int) -> List[models.Message]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Message).where(
            ((models.Message.sender_id == user_id) & (models.Message.receiver_id == other_user_id)) |
            ((models.Message.sender_id == other_user_id) & (models.Message.receiver_id == user_id))
        ).order_by(models.Message.created_at)
        return db.execute(stmt).scalars().all()
    finally:
        db.close()


def _update_message_sync(message_id: int, is_read: Optional[int]) -> Optional[models.Message]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Message).where(models.Message.id == message_id)
        message = db.execute(stmt).scalars().first()
        if not message:
            return None
        if is_read is not None:
            message.is_read = is_read
        message.updated_at = int(datetime.utcnow().timestamp())
        db.commit()
        db.refresh(message)
        return message
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _delete_message_sync(message_id: int) -> bool:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Message).where(models.Message.id == message_id)
        message = db.execute(stmt).scalars().first()
        if not message:
            return False
        db.delete(message)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_message(sender_id: int, receiver_id: int, content: str) -> models.Message:
    return await run_in_threadpool(_create_message_sync, sender_id, receiver_id, content)


async def get_message(message_id: int) -> Optional[models.Message]:
    return await run_in_threadpool(_get_message_sync, message_id)


async def list_user_messages(user_id: int) -> List[models.Message]:
    return await run_in_threadpool(_list_user_messages_sync, user_id)


async def list_conversation(user_id: int, other_user_id: int) -> List[models.Message]:
    return await run_in_threadpool(_list_conversation_sync, user_id, other_user_id)


async def update_message(message_id: int, is_read: Optional[int]) -> Optional[models.Message]:
    return await run_in_threadpool(_update_message_sync, message_id, is_read)


async def delete_message(message_id: int) -> bool:
    return await run_in_threadpool(_delete_message_sync, message_id)
