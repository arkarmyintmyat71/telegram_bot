"""
/start, /help, /menu, /contact — basic commands available to everyone.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.customer import main_inline_menu, main_reply_keyboard
from services.message_service import get_or_create_user

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    user = message.from_user
    await get_or_create_user(user.id, user.username, user.first_name)

    await message.answer(
        f"👋 Welcome, {user.first_name or 'there'}!\n\n"
        "I'm here to help. Choose an option below, or just type your question "
        "and an admin will get back to you.",
        reply_markup=main_reply_keyboard(),
    )
    await message.answer("What would you like to do?", reply_markup=main_inline_menu())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Available commands:\n"
        "/start — show the welcome menu\n"
        "/help — show this message\n"
        "/menu — show the menu again\n"
        "/contact — get in touch with an admin\n\n"
        "You can also just type your question directly — I'll try to answer it, "
        "and if I can't, an admin will."
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Here's the menu:", reply_markup=main_inline_menu())


@router.message(Command("contact"))
async def cmd_contact(message: Message) -> None:
    await message.answer(
        "✉️ Just type your message here and an admin will reply as soon as possible."
    )
