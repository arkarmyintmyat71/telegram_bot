"""
Handlers for inline keyboard button presses (menu:order, menu:faq, faq:<id>, ...).
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.customer import back_to_faq_keyboard, faq_list_keyboard, main_inline_menu
from services.message_service import get_faq_by_id, list_faqs

router = Router(name="callback")


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text("What would you like to do?", reply_markup=main_inline_menu())
    await callback.answer()


@router.callback_query(F.data == "menu:order")
async def cb_order(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🛒 To place an order, just tell me what you'd like and an admin will confirm "
        "the details with you shortly.",
        reply_markup=back_to_faq_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:contact")
async def cb_contact(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "✉️ Type your message here and an admin will reply as soon as possible.",
        reply_markup=back_to_faq_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:support")
async def cb_support(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🆘 Need help? Describe your issue and an admin will assist you.",
        reply_markup=back_to_faq_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:faq")
async def cb_faq(callback: CallbackQuery) -> None:
    faqs = await list_faqs()
    if not faqs:
        await callback.message.edit_text("No FAQ entries yet.", reply_markup=main_inline_menu())
    else:
        await callback.message.edit_text("📖 Frequently asked questions:", reply_markup=faq_list_keyboard(faqs))
    await callback.answer()


@router.callback_query(F.data.startswith("faq:"))
async def cb_faq_answer(callback: CallbackQuery) -> None:
    faq_id = int(callback.data.split(":", 1)[1])
    faq = await get_faq_by_id(faq_id)
    if faq is None:
        await callback.answer("That FAQ entry no longer exists.", show_alert=True)
        return
    await callback.message.edit_text(
        f"❓ {faq.question}\n\n{faq.answer}",
        reply_markup=back_to_faq_keyboard(),
    )
    await callback.answer()
