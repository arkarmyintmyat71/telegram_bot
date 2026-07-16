"""
Admin-only commands and reply routing.

Only Telegram user IDs listed in ADMIN_IDS (see config.py / .env) can use these.
"""

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from services.message_service import (
    broadcast_message,
    get_stats,
    list_all_users,
    route_admin_reply,
    set_banned,
)
from utils.filters import IsAdmin

router = Router(name="admin")
router.message.filter(IsAdmin())


@router.message(Command("users"))
async def cmd_users(message: Message) -> None:
    users = await list_all_users()
    if not users:
        await message.answer("No users yet.")
        return
    lines = [
        f"#{u.telegram_id} — {u.first_name or 'Unknown'} "
        f"(@{u.username})" if u.username else f"#{u.telegram_id} — {u.first_name or 'Unknown'}"
        for u in users[:50]
    ]
    header = f"👥 {len(users)} total user(s). Showing up to 50:\n\n"
    await message.answer(header + "\n".join(lines))


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    stats = await get_stats()
    await message.answer(
        "📊 Bot stats\n"
        f"Total users: {stats['total_users']}\n"
        f"Banned users: {stats['banned_users']}\n"
        f"Total messages: {stats['total_messages']}"
    )


@router.message(Command("ban"))
async def cmd_ban(message: Message, command: CommandObject) -> None:
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: /ban <telegram_id>")
        return
    telegram_id = int(command.args.strip())
    ok = await set_banned(telegram_id, True)
    await message.answer(f"🚫 User #{telegram_id} banned." if ok else "User not found.")


@router.message(Command("unban"))
async def cmd_unban(message: Message, command: CommandObject) -> None:
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Usage: /unban <telegram_id>")
        return
    telegram_id = int(command.args.strip())
    ok = await set_banned(telegram_id, False)
    await message.answer(f"✅ User #{telegram_id} unbanned." if ok else "User not found.")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer("Usage: /broadcast <message text>")
        return
    sent = await broadcast_message(message.bot, command.args)
    await message.answer(f"📣 Broadcast sent to {sent} user(s).")


@router.message(F.reply_to_message)
async def handle_admin_reply(message: Message) -> None:
    """
    When an admin replies (Telegram 'reply') to a forwarded customer message,
    route that reply back to the correct customer automatically.
    """
    if not message.text:
        await message.answer("Only text replies are supported right now.")
        return

    handled = await route_admin_reply(
        bot=message.bot,
        admin_chat_id=message.chat.id,
        reply_to_message_id=message.reply_to_message.message_id,
        reply_text=message.text,
    )
    if handled:
        await message.answer("✅ Reply sent to customer.")
    else:
        await message.answer(
            "⚠️ Couldn't find which customer this reply belongs to. "
            "Make sure you're replying directly to the forwarded message."
        )
