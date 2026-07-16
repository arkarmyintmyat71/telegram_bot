"""
Handles plain-text messages from customers:
- Reply-keyboard button presses (FAQ / Order Status / Contact Us)
- Everything else: try an FAQ auto-reply, otherwise forward to admins
"""

from aiogram import F, Router
from aiogram.types import Message

from keyboards.customer import faq_list_keyboard
from services.message_service import (
    find_faq_match,
    forward_to_admins,
    get_or_create_user,
    is_banned,
    list_faqs,
)
from utils.filters import IsCustomer

router = Router(name="customer")
router.message.filter(IsCustomer())


@router.message(F.text == "📖 FAQ")
async def reply_kb_faq(message: Message) -> None:
    faqs = await list_faqs()
    if not faqs:
        await message.answer("No FAQ entries yet.")
        return
    await message.answer("Frequently asked questions:", reply_markup=faq_list_keyboard(faqs))


@router.message(F.text == "📦 Order Status")
async def reply_kb_order_status(message: Message) -> None:
    await message.answer(
        "Please send your order number and an admin will check the status for you."
    )


@router.message(F.text == "✉️ Contact Us")
async def reply_kb_contact(message: Message) -> None:
    await message.answer("Type your message here and an admin will get back to you shortly.")


@router.message(F.text)
async def handle_customer_text(message: Message) -> None:
    """Catch-all for any other text: FAQ match first, then forward to admin."""
    user_tg = message.from_user

    if await is_banned(user_tg.id):
        await message.answer("You've been restricted from using this bot. Contact support elsewhere.")
        return

    user = await get_or_create_user(user_tg.id, user_tg.username, user_tg.first_name)

    faq = await find_faq_match(message.text)
    if faq is not None:
        await message.answer(f"❓ {faq.question}\n\n{faq.answer}")
        return

    await forward_to_admins(message.bot, user, message.text)
    await message.answer("Thanks for contacting us. An admin will reply shortly.")
