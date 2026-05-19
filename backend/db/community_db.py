from typing import List, Optional

from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import select
from fastapi.concurrency import run_in_threadpool

from backend import db as sync_db
from backend.community import models


def _create_community_sync(name: str, description: str, anime: str, creator_id: int) -> models.Community:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        community = models.Community(
            name=name,
            description=description,
            anime=anime,
            creator_id=creator_id,
            created_at=now,
            updated_at=now,
        )
        db.add(community)
        db.commit()
        db.refresh(community)
        return community
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_community_sync(community_id: int) -> Optional[models.Community]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Community).where(models.Community.id == community_id)
        result = db.execute(stmt).scalars().first()
        return result
    finally:
        db.close()


def _list_communities_sync() -> List[models.Community]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Community)
        result = db.execute(stmt).scalars().all()
        return result
    finally:
        db.close()


def _create_thread_sync(title: str, description: str, community_id: int, creator_id: int) -> models.Thread:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        thread = models.Thread(
            title=title,
            description=description,
            community_id=community_id,
            creator_id=creator_id,
            created_at=now,
            updated_at=now,
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)
        return thread
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_thread_sync(thread_id: int) -> Optional[models.Thread]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Thread).where(models.Thread.id == thread_id)
        result = db.execute(stmt).scalars().first()
        return result
    finally:
        db.close()


def _list_threads_sync() -> List[models.Thread]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Thread)
        result = db.execute(stmt).scalars().all()
        return result
    finally:
        db.close()


def _list_threads_by_community_sync(community_id: int) -> List[models.Thread]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Thread).where(models.Thread.community_id == community_id)
        result = db.execute(stmt).scalars().all()
        return result
    finally:
        db.close()


def _create_thread_comment_sync(thread_id: int, user_id: int, content: str) -> models.ThreadComment:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        comment = models.ThreadComment(
            thread_id=thread_id,
            user_id=user_id,
            content=content,
            created_at=now,
            updated_at=now,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_thread_comment_sync(comment_id: int) -> Optional[models.ThreadComment]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.ThreadComment).where(models.ThreadComment.id == comment_id)
        return db.execute(stmt).scalars().first()
    finally:
        db.close()


def _list_thread_comments_sync(thread_id: int) -> List[models.ThreadComment]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.ThreadComment).where(models.ThreadComment.thread_id == thread_id)
        return db.execute(stmt).scalars().all()
    finally:
        db.close()


def _get_thread_like_sync(thread_id: int, user_id: int) -> Optional[models.ThreadLike]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.ThreadLike).where(
            models.ThreadLike.thread_id == thread_id,
            models.ThreadLike.user_id == user_id,
        )
        return db.execute(stmt).scalars().first()
    finally:
        db.close()


def _set_thread_like_sync(thread_id: int, user_id: int, is_liked: int) -> models.ThreadLike:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        stmt = select(models.ThreadLike).where(
            models.ThreadLike.thread_id == thread_id,
            models.ThreadLike.user_id == user_id,
        )
        thread_like = db.execute(stmt).scalars().first()
        if thread_like:
            thread_like.is_liked = is_liked
            thread_like.updated_at = now
        else:
            thread_like = models.ThreadLike(
                thread_id=thread_id,
                user_id=user_id,
                is_liked=is_liked,
                created_at=now,
                updated_at=now,
            )
            db.add(thread_like)
        db.commit()
        db.refresh(thread_like)
        return thread_like
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_thread_comment_like_sync(comment_id: int, user_id: int) -> Optional[models.ThreadCommentLike]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.ThreadCommentLike).where(
            models.ThreadCommentLike.comment_id == comment_id,
            models.ThreadCommentLike.user_id == user_id,
        )
        return db.execute(stmt).scalars().first()
    finally:
        db.close()


def _set_thread_comment_like_sync(comment_id: int, user_id: int, is_liked: int) -> models.ThreadCommentLike:
    db: Session = sync_db.SessionLocal()
    try:
        now = int(datetime.utcnow().timestamp())
        stmt = select(models.ThreadCommentLike).where(
            models.ThreadCommentLike.comment_id == comment_id,
            models.ThreadCommentLike.user_id == user_id,
        )
        comment_like = db.execute(stmt).scalars().first()
        if comment_like:
            comment_like.is_liked = is_liked
            comment_like.updated_at = now
        else:
            comment_like = models.ThreadCommentLike(
                comment_id=comment_id,
                user_id=user_id,
                is_liked=is_liked,
                created_at=now,
                updated_at=now,
            )
            db.add(comment_like)
        db.commit()
        db.refresh(comment_like)
        return comment_like
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_community_moderator_by_id_sync(moderator_id: int) -> Optional[models.CommunityModerator]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.CommunityModerator).where(models.CommunityModerator.id == moderator_id)
        return db.execute(stmt).scalars().first()
    finally:
        db.close()


def _list_community_moderators_sync(community_id: int) -> List[models.CommunityModerator]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.CommunityModerator).where(models.CommunityModerator.community_id == community_id)
        return db.execute(stmt).scalars().all()
    finally:
        db.close()


def _create_community_moderator_sync(community_id: int, user_id: int) -> models.CommunityModerator:
    db: Session = sync_db.SessionLocal()
    try:
        existing = db.execute(
            select(models.CommunityModerator).where(
                models.CommunityModerator.community_id == community_id,
                models.CommunityModerator.user_id == user_id,
            )
        ).scalars().first()
        if existing:
            return existing
        now = int(datetime.utcnow().timestamp())
        moderator = models.CommunityModerator(
            community_id=community_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        db.add(moderator)
        db.commit()
        db.refresh(moderator)
        return moderator
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _delete_community_moderator_sync(moderator_id: int) -> bool:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.CommunityModerator).where(models.CommunityModerator.id == moderator_id)
        moderator = db.execute(stmt).scalars().first()
        if not moderator:
            return False
        db.delete(moderator)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _is_user_moderator_sync(user_id: int, community_id: int) -> bool:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.CommunityModerator).where(
            models.CommunityModerator.user_id == user_id,
            models.CommunityModerator.community_id == community_id,
            models.CommunityModerator.is_active == 1,
        )
        return db.execute(stmt).scalars().first() is not None
    finally:
        db.close()


def _update_thread_sync(thread_id: int, title: Optional[str], description: Optional[str], is_active: Optional[int]) -> Optional[models.Thread]:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Thread).where(models.Thread.id == thread_id)
        thread = db.execute(stmt).scalars().first()
        if not thread:
            return None
        if title is not None:
            thread.title = title
        if description is not None:
            thread.description = description
        if is_active is not None:
            thread.is_active = is_active
        thread.updated_at = int(datetime.utcnow().timestamp())
        db.commit()
        db.refresh(thread)
        return thread
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _delete_thread_sync(thread_id: int) -> bool:
    db: Session = sync_db.SessionLocal()
    try:
        stmt = select(models.Thread).where(models.Thread.id == thread_id)
        thread = db.execute(stmt).scalars().first()
        if not thread:
            return False
        db.delete(thread)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def create_community(name: str, description: str, anime: str, creator_id: int) -> models.Community:
    return await run_in_threadpool(_create_community_sync, name, description, anime, creator_id)


async def get_community(community_id: int) -> Optional[models.Community]:
    return await run_in_threadpool(_get_community_sync, community_id)


async def list_communities() -> List[models.Community]:
    return await run_in_threadpool(_list_communities_sync)


async def create_thread(title: str, description: str, community_id: int, creator_id: int) -> models.Thread:
    return await run_in_threadpool(_create_thread_sync, title, description, community_id, creator_id)


async def get_thread(thread_id: int) -> Optional[models.Thread]:
    return await run_in_threadpool(_get_thread_sync, thread_id)


async def list_threads() -> List[models.Thread]:
    return await run_in_threadpool(_list_threads_sync)


async def update_thread(thread_id: int, title: Optional[str], description: Optional[str], is_active: Optional[int]) -> Optional[models.Thread]:
    return await run_in_threadpool(_update_thread_sync, thread_id, title, description, is_active)


async def delete_thread(thread_id: int) -> bool:
    return await run_in_threadpool(_delete_thread_sync, thread_id)


async def list_threads_by_community(community_id: int) -> List[models.Thread]:
    return await run_in_threadpool(_list_threads_by_community_sync, community_id)


async def create_thread_comment(thread_id: int, user_id: int, content: str) -> models.ThreadComment:
    return await run_in_threadpool(_create_thread_comment_sync, thread_id, user_id, content)


async def get_thread_comment(comment_id: int) -> Optional[models.ThreadComment]:
    return await run_in_threadpool(_get_thread_comment_sync, comment_id)


async def list_thread_comments(thread_id: int) -> List[models.ThreadComment]:
    return await run_in_threadpool(_list_thread_comments_sync, thread_id)


async def get_thread_like(thread_id: int, user_id: int) -> Optional[models.ThreadLike]:
    return await run_in_threadpool(_get_thread_like_sync, thread_id, user_id)


async def set_thread_like(thread_id: int, user_id: int, is_liked: int) -> models.ThreadLike:
    return await run_in_threadpool(_set_thread_like_sync, thread_id, user_id, is_liked)


async def get_thread_comment_like(comment_id: int, user_id: int) -> Optional[models.ThreadCommentLike]:
    return await run_in_threadpool(_get_thread_comment_like_sync, comment_id, user_id)


async def set_thread_comment_like(comment_id: int, user_id: int, is_liked: int) -> models.ThreadCommentLike:
    return await run_in_threadpool(_set_thread_comment_like_sync, comment_id, user_id, is_liked)


async def get_community_moderator_by_id(moderator_id: int) -> Optional[models.CommunityModerator]:
    return await run_in_threadpool(_get_community_moderator_by_id_sync, moderator_id)


async def list_community_moderators(community_id: int) -> List[models.CommunityModerator]:
    return await run_in_threadpool(_list_community_moderators_sync, community_id)


async def create_community_moderator(community_id: int, user_id: int) -> models.CommunityModerator:
    return await run_in_threadpool(_create_community_moderator_sync, community_id, user_id)


async def delete_community_moderator(moderator_id: int) -> bool:
    return await run_in_threadpool(_delete_community_moderator_sync, moderator_id)


async def is_user_moderator(user_id: int, community_id: int) -> bool:
    return await run_in_threadpool(_is_user_moderator_sync, user_id, community_id)
