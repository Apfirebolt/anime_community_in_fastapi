from typing import List, Optional

from . import schema
from . import models
from backend.db import community_db
from backend.db import auth_db
from backend.notification import services as notification_services


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

    async def create_thread_comment(self, thread_id: int, request: schema.ThreadCommentCreate, user_id: int) -> models.ThreadComment:
        if not request.content or not request.content.strip():
            raise ValueError("Comment content is required")
        thread = await community_db.get_thread(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        comment = await community_db.create_thread_comment(thread_id, user_id, request.content.strip())
        if thread.creator_id != user_id:
            actor = await auth_db.get_user_by_id(user_id)
            actor_name = actor.username if actor else "Someone"
            await notification_services.notify_thread_owner_of_new_comment(
                thread_owner_id=thread.creator_id,
                actor_id=user_id,
                thread_id=thread_id,
                actor_name=actor_name,
                comment_content=request.content.strip(),
            )
        return comment

    async def like_thread(self, thread_id: int, user_id: int) -> models.ThreadLike:
        thread = await community_db.get_thread(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        return await community_db.set_thread_like(thread_id, user_id, 1)

    async def unlike_thread(self, thread_id: int, user_id: int) -> None:
        thread = await community_db.get_thread(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        await community_db.set_thread_like(thread_id, user_id, 0)

    async def like_thread_comment(self, thread_id: int, comment_id: int, user_id: int) -> models.ThreadCommentLike:
        comment = await community_db.get_thread_comment(comment_id)
        if not comment or comment.thread_id != thread_id:
            raise ValueError("Comment not found")
        return await community_db.set_thread_comment_like(comment_id, user_id, 1)

    async def unlike_thread_comment(self, thread_id: int, comment_id: int, user_id: int) -> None:
        comment = await community_db.get_thread_comment(comment_id)
        if not comment or comment.thread_id != thread_id:
            raise ValueError("Comment not found")
        await community_db.set_thread_comment_like(comment_id, user_id, 0)

    async def get_thread_comment(self, comment_id: int) -> Optional[models.ThreadComment]:
        return await community_db.get_thread_comment(comment_id)

    async def list_thread_comments(self, thread_id: int) -> List[models.ThreadComment]:
        return await community_db.list_thread_comments(thread_id)

    async def update_thread(self, thread_id: int, request: schema.ThreadUpdate, current_user_id: int) -> models.Thread:
        thread = await community_db.get_thread(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        is_moderator = await community_db.is_user_moderator(current_user_id, thread.community_id)
        if thread.creator_id != current_user_id and not is_moderator:
            raise PermissionError("Not authorized to update thread")
        if request.title is not None and not request.title.strip():
            raise ValueError("Thread title cannot be empty")
        updated_thread = await community_db.update_thread(
            thread_id,
            title=request.title.strip() if request.title is not None else None,
            description=request.description,
            is_active=request.is_active,
        )
        return updated_thread

    async def delete_thread(self, thread_id: int, current_user_id: int) -> None:
        thread = await community_db.get_thread(thread_id)
        if not thread:
            raise ValueError("Thread not found")
        is_moderator = await community_db.is_user_moderator(current_user_id, thread.community_id)
        if thread.creator_id != current_user_id and not is_moderator:
            raise PermissionError("Not authorized to delete thread")
        await community_db.delete_thread(thread_id)

    async def assign_moderator(self, community_id: int, user_id: int, current_user_id: int) -> models.CommunityModerator:
        community = await community_db.get_community(community_id)
        if not community:
            raise ValueError("Community not found")
        if community.creator_id != current_user_id:
            raise PermissionError("Only community creator can assign moderators")
        user = await auth_db.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        moderator = await community_db.create_community_moderator(community_id, user_id)
        return moderator

    async def list_moderators(self, community_id: int) -> List[models.CommunityModerator]:
        return await community_db.list_community_moderators(community_id)

    async def remove_moderator(self, community_id: int, moderator_id: int, current_user_id: int) -> None:
        community = await community_db.get_community(community_id)
        if not community:
            raise ValueError("Community not found")
        if community.creator_id != current_user_id:
            raise PermissionError("Only community creator can remove moderators")
        moderator = await community_db.get_community_moderator_by_id(moderator_id)
        if not moderator or moderator.community_id != community_id:
            raise ValueError("Moderator assignment not found")
        await community_db.delete_community_moderator(moderator_id)

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


async def create_thread_comment(thread_id: int, request: schema.ThreadCommentCreate, user_id: int) -> models.ThreadComment:
    return await community_service.create_thread_comment(thread_id, request, user_id)


async def get_thread_comment(comment_id: int) -> Optional[models.ThreadComment]:
    return await community_service.get_thread_comment(comment_id)


async def list_thread_comments(thread_id: int) -> List[models.ThreadComment]:
    return await community_service.list_thread_comments(thread_id)


async def like_thread(thread_id: int, user_id: int) -> models.ThreadLike:
    return await community_service.like_thread(thread_id, user_id)


async def unlike_thread(thread_id: int, user_id: int) -> None:
    return await community_service.unlike_thread(thread_id, user_id)


async def like_thread_comment(thread_id: int, comment_id: int, user_id: int) -> models.ThreadCommentLike:
    return await community_service.like_thread_comment(thread_id, comment_id, user_id)


async def unlike_thread_comment(thread_id: int, comment_id: int, user_id: int) -> None:
    return await community_service.unlike_thread_comment(thread_id, comment_id, user_id)


async def update_thread(thread_id: int, request: schema.ThreadUpdate, current_user_id: int) -> models.Thread:
    return await community_service.update_thread(thread_id, request, current_user_id)


async def delete_thread(thread_id: int, current_user_id: int) -> None:
    return await community_service.delete_thread(thread_id, current_user_id)


async def assign_moderator(community_id: int, user_id: int, current_user_id: int) -> models.CommunityModerator:
    return await community_service.assign_moderator(community_id, user_id, current_user_id)


async def list_moderators(community_id: int) -> List[models.CommunityModerator]:
    return await community_service.list_moderators(community_id)


async def remove_moderator(community_id: int, moderator_id: int, current_user_id: int) -> None:
    return await community_service.remove_moderator(community_id, moderator_id, current_user_id)


async def list_threads(community_id: Optional[int] = None) -> List[models.Thread]:
    return await community_service.list_threads(community_id)


async def list_communities() -> List[models.Community]:
    return await community_service.list_communities()
