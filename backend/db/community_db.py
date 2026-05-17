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


async def create_community(name: str, description: str, anime: str, creator_id: int) -> models.Community:
    return await run_in_threadpool(_create_community_sync, name, description, anime, creator_id)


async def get_community(community_id: int) -> Optional[models.Community]:
    return await run_in_threadpool(_get_community_sync, community_id)


async def list_communities() -> List[models.Community]:
    return await run_in_threadpool(_list_communities_sync)
