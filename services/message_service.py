"""
Core business logic:
- registering users
- forwarding customer messages to all admins
- routing an admin's reply back to the correct customer
- FAQ lookup
- deleting old data (retention policy)
"""

import datetime as dt
import logging

from aiogram import Bot
from sqlalchemy import delete, func, select

from config import ADMIN_IDS, MESSAGE_RETENTION_DAYS
from database import get_session
from models import FAQ, BroadcastLog, ForwardMap, Message, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

async def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> User:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


async def is_banned(telegram_id: int) -> bool:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        return bool(user and user.is_banned)


async def set_banned(telegram_id: int, banned: bool) -> bool:
    """Returns True if a matching user was found and updated."""
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user is None:
            return False
        user.is_banned = banned
        await session.commit()
        return True


async def list_all_users() -> list[User]:
    async with get_session() as session:
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())


async def get_stats() -> dict:
    async with get_session() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar_one()
        banned_users = (
            await session.execute(select(func.count(User.id)).where(User.is_banned.is_(True)))
        ).scalar_one()
        total_messages = (await session.execute(select(func.count(Message.id)))).scalar_one()
        return {
            "total_users": total_users,
            "banned_users": banned_users,
            "total_messages": total_messages,
        }


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

DEFAULT_FAQS = [
    ("How do I place an order?", "Tap 'Order' in the menu, or just tell us what you'd like!"),
    ("What are your business hours?", "We're available 9am - 6pm, Monday to Saturday."),
    ("How can I contact a human?", "Tap 'Contact Us' or just type your question — an admin will reply shortly."),
]


async def seed_faqs_if_empty() -> None:
    async with get_session() as session:
        count = (await session.execute(select(func.count(FAQ.id)))).scalar_one()
        if count == 0:
            for q, a in DEFAULT_FAQS:
                session.add(FAQ(question=q, answer=a))
            await session.commit()
            logger.info("Seeded %d default FAQ entries.", len(DEFAULT_FAQS))


async def list_faqs() -> list[FAQ]:
    async with get_session() as session:
        result = await session.execute(select(FAQ).order_by(FAQ.id))
        return list(result.scalars().all())


async def get_faq_by_id(faq_id: int) -> FAQ | None:
    async with get_session() as session:
        return await session.get(FAQ, faq_id)


async def find_faq_match(text: str) -> FAQ | None:
    """Very simple keyword match: does the FAQ question share a word with the message?"""
    text_lower = text.lower()
    faqs = await list_faqs()
    for faq in faqs:
        if faq.question.lower() in text_lower or text_lower in faq.question.lower():
            return faq
    return None


# ---------------------------------------------------------------------------
# Message forwarding: customer -> admins, admin -> customer
# ---------------------------------------------------------------------------

async def save_message(user_id: int, sender: str, text: str) -> None:
    async with get_session() as session:
        session.add(Message(user_id=user_id, sender=sender, text=text))
        await session.commit()


async def forward_to_admins(bot: Bot, user: User, text: str) -> None:
    """
    Sends the customer's message to every configured admin and remembers
    the (admin_chat_id, admin_message_id) -> customer mapping so replies
    can be routed back correctly.
    """
    label = user.username and f"@{user.username}" or user.first_name or "Unknown"
    formatted = f"📩 Customer #{user.telegram_id} ({label})\n\n{text}"

    async with get_session() as session:
        for admin_id in ADMIN_IDS:
            try:
                sent = await bot.send_message(admin_id, formatted)
                session.add(
                    ForwardMap(
                        admin_chat_id=admin_id,
                        admin_message_id=sent.message_id,
                        customer_telegram_id=user.telegram_id,
                    )
                )
            except Exception:
                logger.exception("Failed to forward message to admin %s", admin_id)
        await session.commit()

    await save_message(user.id, "customer", text)


async def route_admin_reply(bot: Bot, admin_chat_id: int, reply_to_message_id: int, reply_text: str) -> bool:
    """
    Looks up which customer the admin is replying to (via ForwardMap) and
    sends the reply to them. Also notifies other admins that it's been answered.
    Returns True if a matching customer was found.
    """
    async with get_session() as session:
        result = await session.execute(
            select(ForwardMap).where(
                ForwardMap.admin_chat_id == admin_chat_id,
                ForwardMap.admin_message_id == reply_to_message_id,
            )
        )
        mapping = result.scalar_one_or_none()
        if mapping is None:
            return False
        customer_telegram_id = mapping.customer_telegram_id

    try:
        await bot.send_message(customer_telegram_id, reply_text)
    except Exception:
        logger.exception("Failed to deliver reply to customer %s", customer_telegram_id)
        return False

    # Log it against the user's message history
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == customer_telegram_id))
        user = result.scalar_one_or_none()
        if user:
            session.add(Message(user_id=user.id, sender="admin", text=reply_text))
            await session.commit()

    # Let other admins know it's handled
    for admin_id in ADMIN_IDS:
        if admin_id != admin_chat_id:
            try:
                await bot.send_message(
                    admin_id,
                    f"✅ Customer #{customer_telegram_id} was answered by another admin.",
                )
            except Exception:
                pass

    return True


# ---------------------------------------------------------------------------
# Broadcast
# ---------------------------------------------------------------------------

async def broadcast_message(bot: Bot, text: str) -> int:
    """Sends `text` to every non-banned user. Returns number of successful sends."""
    users = await list_all_users()
    sent = 0
    for user in users:
        if user.is_banned:
            continue
        try:
            await bot.send_message(user.telegram_id, text)
            sent += 1
        except Exception:
            logger.warning("Could not deliver broadcast to %s", user.telegram_id)

    async with get_session() as session:
        session.add(BroadcastLog(text=text, sent_count=sent))
        await session.commit()

    return sent


# ---------------------------------------------------------------------------
# Retention / cleanup
# ---------------------------------------------------------------------------

async def cleanup_old_data(retention_days: int = MESSAGE_RETENTION_DAYS) -> None:
    """Deletes messages, forward-map entries, and broadcast logs older than N days."""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=retention_days)

    async with get_session() as session:
        await session.execute(delete(Message).where(Message.created_at < cutoff))
        await session.execute(delete(ForwardMap).where(ForwardMap.created_at < cutoff))
        await session.execute(delete(BroadcastLog).where(BroadcastLog.created_at < cutoff))
        await session.commit()

    logger.info("Cleanup complete: removed data older than %d days.", retention_days)
