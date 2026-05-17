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


# Module-level default service instance for backward compatibility.
community_service = CommunityService()


# Backwards-compatible function wrappers (keep existing imports working)
async def create_community(request: schema.CommunityCreate, creator_id: int) -> models.Community:
    return await community_service.create_community(request, creator_id)


async def get_community(community_id: int) -> Optional[models.Community]:
    return await community_service.get_community(community_id)


async def list_communities() -> List[models.Community]:
    return await community_service.list_communities()
