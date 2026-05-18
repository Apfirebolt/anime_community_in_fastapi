from typing import List, Optional

from . import schema
from . import models
from backend.db import message_db
from backend.db import auth_db


class MessageService:
    """Service layer for direct message operations."""

    async def send_message(self, sender_id: int, request: schema.MessageCreate) -> models.Message:
        if not request.content or not request.content.strip():
            raise ValueError("Message content is required")
        receiver = await auth_db.get_user_by_id(request.receiver_id)
        if not receiver:
            raise ValueError("Receiver not found")
        if sender_id == request.receiver_id:
            raise ValueError("Cannot send message to yourself")
        message = await message_db.create_message(
            sender_id, request.receiver_id, request.content.strip()
        )
        return message

    async def get_message(self, message_id: int) -> Optional[models.Message]:
        return await message_db.get_message(message_id)

    async def list_user_messages(self, user_id: int) -> List[models.Message]:
        return await message_db.list_user_messages(user_id)

    async def list_conversation(self, user_id: int, other_user_id: int) -> List[models.Message]:
        other_user = await auth_db.get_user_by_id(other_user_id)
        if not other_user:
            raise ValueError("Other user not found")
        return await message_db.list_conversation(user_id, other_user_id)

    async def mark_as_read(self, message_id: int, current_user_id: int) -> models.Message:
        message = await message_db.get_message(message_id)
        if not message:
            raise ValueError("Message not found")
        if message.receiver_id != current_user_id:
            raise PermissionError("Only receiver can mark message as read")
        updated = await message_db.update_message(message_id, is_read=1)
        if not updated:
            raise ValueError("Message not found")
        return updated

    async def delete_message(self, message_id: int, current_user_id: int) -> None:
        message = await message_db.get_message(message_id)
        if not message:
            raise ValueError("Message not found")
        if message.sender_id != current_user_id and message.receiver_id != current_user_id:
            raise PermissionError("Not authorized to delete this message")
        deleted = await message_db.delete_message(message_id)
        if not deleted:
            raise ValueError("Message not found")


# Module-level default service instance
message_service = MessageService()


# Backwards-compatible function wrappers
async def send_message(sender_id: int, request: schema.MessageCreate) -> models.Message:
    return await message_service.send_message(sender_id, request)


async def get_message(message_id: int) -> Optional[models.Message]:
    return await message_service.get_message(message_id)


async def list_user_messages(user_id: int) -> List[models.Message]:
    return await message_service.list_user_messages(user_id)


async def list_conversation(user_id: int, other_user_id: int) -> List[models.Message]:
    return await message_service.list_conversation(user_id, other_user_id)


async def mark_as_read(message_id: int, current_user_id: int) -> models.Message:
    return await message_service.mark_as_read(message_id, current_user_id)


async def delete_message(message_id: int, current_user_id: int) -> None:
    return await message_service.delete_message(message_id, current_user_id)
