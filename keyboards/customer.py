"""
Reply and inline keyboards shown to customers.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

#from config import WEBSITE_URL


def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Persistent keyboard shown under the text input box."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 CV ရေးသားရန်"), KeyboardButton(text="🎫 လက်မှတ် (ကား/ရထား)")],
            [KeyboardButton(text="🎓 တက္ကသိုလ်ဝင်တန်း ရလဒ်"), KeyboardButton(text="📖 မေးလေ့ရှိသောမေးခွန်း")],
            [KeyboardButton(text="✉️ ဆက်သွယ်ရန်")],
        ],
        resize_keyboard=True,
    )


def main_inline_menu() -> InlineKeyboardMarkup:
    """Inline menu sent right after /start."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 CV ရေးသားရန်", callback_data="menu:cv"),
                InlineKeyboardButton(text="🎫 လက်မှတ် (ကား/ရထား)", callback_data="menu:ticket"),
            ],
            [
                InlineKeyboardButton(text="🎓 တက္ကသိုလ်ဝင်တန်း ရလဒ်", callback_data="menu:grade12"),
                InlineKeyboardButton(text="✉️ ဆက်သွယ်ရန်", callback_data="menu:contact"),
            ],
            [
                InlineKeyboardButton(text="📖 FAQ", callback_data="menu:faq")
            ],
        ]
    )


def faq_category_keyboard(categories: list[str]) -> InlineKeyboardMarkup:
    """One button per FAQ category (CV / Ticket / General), plus a Back button."""
    from services.message_service import FAQ_CATEGORY_LABELS

    rows = [
        [InlineKeyboardButton(text=FAQ_CATEGORY_LABELS.get(cat, cat), callback_data=f"faqcat:{cat}")]
        for cat in categories
    ]
    rows.append([InlineKeyboardButton(text="⬅️ နောက်သို့", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def faq_list_keyboard(faqs: list, category: str | None = None) -> InlineKeyboardMarkup:
    """One button per FAQ entry within a category, plus a Back button to the category list."""
    rows = [
        [InlineKeyboardButton(text=faq.question, callback_data=f"faq:{faq.id}")]
        for faq in faqs
    ]
    back_target = f"faqcat:{category}" if category else "menu:faq"
    rows.append([InlineKeyboardButton(text="⬅️ နောက်သို့", callback_data=back_target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_faq_keyboard(category: str | None = None) -> InlineKeyboardMarkup:
    """Back button that returns to the FAQ list for `category` (or the category menu if omitted)."""
    target = f"faqcat:{category}" if category else "menu:faq"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ FAQ သို့ပြန်သွားရန်", callback_data=target)]
        ]
    )
