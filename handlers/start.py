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
        f"👋 မင်္ဂလာပါ။, {user.first_name or 'there'}!\n\n"
        "CV Myanmar မှကူညီပေးရန် အသင့်ရှိပါတယ်။"

        "အောက်မှာရှိတဲ့ ရွေးချယ်စရာများထဲမှ တစ်ခုကို ရွေးချယ်နိုင်ပါတယ်၊"
        "သို့မဟုတ် သင့်မေးခွန်းကို တိုက်ရိုက်ရိုက်ပို့နိုင်ပါတယ်။"

        "တာဝန်ခံ Admin တစ်ဦးက အမြန်ဆုံး ပြန်လည်ဖြေကြားပေးပါမည်။",
        reply_markup=main_reply_keyboard(),
    )
    await message.answer("ဘာများအလိုရှိပါသလဲခင်ဗျာ။", reply_markup=main_inline_menu())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📋 <b>အသုံးပြုနိုင်သော command များ</b>\n"
        "/start — Welcome menu ကို ပြပါမည်\n"
        "/help — ဒီစာကို ပြပါမည်\n"
        "/menu — Menu ကို ထပ်ပြပါမည်\n"
        "/contact — Admin နှင့် ဆက်သွယ်ရန်\n\n"
        "📝 CV ရေးသားရန်၊ 🎫 လက်မှတ် (ရထား/ဘတ်စ်ကား) ဝယ်ယူရန်၊ 🎓 တက္ကသိုလ်ဝင်တန်း ရလဒ် စစ်ဆေးရန် — "
        "အောက်ကမီနူးထဲက ရွေးချယ်နိုင်ပါတယ်၊ သို့မဟုတ် သင့်မေးခွန်းကို တိုက်ရိုက်ရိုက်ပို့လိုက်ရုံနဲ့ ရပါတယ်။ "
        "Admin က အမြန်ဆုံး ပြန်လည်ဆက်သွယ်ပေးပါမယ်။"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("အောက်မှာ Menu ကို ရွေးချယ်နိုင်ပါတယ်။", reply_markup=main_inline_menu())


@router.message(Command("contact"))
async def cmd_contact(message: Message) -> None:
    await message.answer(
        "✉️ သင့်မေးခွန်း သို့မဟုတ် မက်ဆေ့ချ်ကို ဒီမှာ တိုက်ရိုက်ရိုက်ပို့နိုင်ပါတယ်။ Admin က အမြန်ဆုံး ပြန်လည်ကူညီဖြေကြားပေးပါမယ်။"
    )
