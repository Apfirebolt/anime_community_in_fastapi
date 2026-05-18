from typing import List, Optional

from . import schema
from . import models
from backend.db import community_db


class CommunityService:
    """Service layer for community operations.

    Methods are async and delegate to `community_db` functions. Creating
    this class makes it easier to inject dependencies or state later.
    """

    async def create_community(self, request: schema.CommunityCreate, creator_id: int) -> models.Community:
        # Basic validation: name must be provided
        if not request.name or not request.name.strip():
            raise ValueError("Community name is required")
        community = await community_db.create_community(
            request.name.strip(), request.description, request.anime, creator_id
        )
        return community

    async def get_community(self, community_id: int) -> Optional[models.Community]:
        return await community_db.get_community(community_id)

    async def list_communities(self) -> List[models.Community]:
        return await community_db.list_communities()


    async def create_thread(self, community_id: int, request: schema.ThreadCreate, creator_id: int) -> models.Thread:
        if not request.title or not request.title.strip():
            raise ValueError("Thread title is required")
        community = await community_db.get_community(community_id)
        if not community:
            raise ValueError("Community not found")
        thread = await community_db.create_thread(
            request.title.strip(), request.description, community_id, creator_id
        )
        return thread

    async def get_thread(self, thread_id: int) -> Optional[models.Thread]:
        return await community_db.get_thread(thread_id)

    async def list_threads(self, community_id: Optional[int] = None) -> List[models.Thread]:
        if community_id is None:
            return await community_db.list_threads()
        return await community_db.list_threads_by_community(community_id)


# Module-level default service instance for backward compatibility.
community_service = CommunityService()


# Backwards-compatible function wrappers (keep existing imports working)
async def create_community(request: schema.CommunityCreate, creator_id: int) -> models.Community:
    return await community_service.create_community(request, creator_id)


async def get_community(community_id: int) -> Optional[models.Community]:
    return await community_service.get_community(community_id)


async def create_thread(community_id: int, request: schema.ThreadCreate, creator_id: int) -> models.Thread:
    return await community_service.create_thread(community_id, request, creator_id)


async def get_thread(thread_id: int) -> Optional[models.Thread]:
    return await community_service.get_thread(thread_id)


async def list_threads(community_id: Optional[int] = None) -> List[models.Thread]:
    return await community_service.list_threads(community_id)


async def list_communities() -> List[models.Community]:
    return await community_service.list_communities()
