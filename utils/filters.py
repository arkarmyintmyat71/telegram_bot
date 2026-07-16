"""
Reusable aiogram filters.
"""

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import ADMIN_IDS


class IsAdmin(BaseFilter):
    """True if the message comes from one of the configured admin IDs."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user is not None and message.from_user.id in ADMIN_IDS


class IsCustomer(BaseFilter):
    """True if the message does NOT come from an admin (i.e. a regular customer)."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user is not None and message.from_user.id not in ADMIN_IDS
