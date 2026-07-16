"""
Reply and inline keyboards shown to customers.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import WEBSITE_URL


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent keyboard shown under the text input box."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 FAQ"), KeyboardButton(text="📦 Order Status")],
            [KeyboardButton(text="✉️ Contact Us")],
        ],
        resize_keyboard=True,
    )


def main_inline_menu() -> InlineKeyboardMarkup:
    """Inline menu sent right after /start."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛒 Order", callback_data="menu:order"),
                InlineKeyboardButton(text="✉️ Contact", callback_data="menu:contact"),
            ],
            [
                InlineKeyboardButton(text="📖 FAQ", callback_data="menu:faq"),
                InlineKeyboardButton(text="🆘 Support", callback_data="menu:support"),
            ],
            [InlineKeyboardButton(text="🌐 Website", url=WEBSITE_URL)],
        ]
    )


def faq_list_keyboard(faqs: list) -> InlineKeyboardMarkup:
    """One button per FAQ entry, plus a Back button."""
    rows = [
        [InlineKeyboardButton(text=faq.question, callback_data=f"faq:{faq.id}")]
        for faq in faqs
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Back", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_faq_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Back to FAQ", callback_data="menu:faq")]
        ]
    )
