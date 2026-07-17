"""
Handles plain-text messages from customers:
- Reply-keyboard button presses (CV / Ticket / Grade 12 Result / FAQ / Contact Us)
- Everything else: try an FAQ auto-reply, otherwise forward to admins
"""

from aiogram import F, Router
from aiogram.types import Message

from keyboards.customer import faq_category_keyboard
from services.message_service import (
    find_faq_match,
    forward_to_admins,
    get_or_create_user,
    is_banned,
    list_faq_categories,
)
from utils.filters import IsCustomer

router = Router(name="customer")
router.message.filter(IsCustomer())

CV_PROMPT = (
    "📝 <b>CV ရေးသားခြင်း ဝန်ဆောင်မှု</b>\n\n"
    "💰 CV တစ်စောင် — 10,000 ကျပ်\n"
    "⏱ Service အပ်ပြီး 24 hr အတွင်း ရရှိမည်\n"
    "🌐 မြန်မာလို / English လို နှစ်မျိုးလုံး ရေးပေးပါသည်\n\n"
    "အောက်ပါ အချက်အလက်များကို ပေးပို့ပေးပါ —\n"
    "• အမည်၊ အသက်၊ ပညာအရည်အချင်း\n"
    "• ဖုန်းနံပါတ် / Gmail / လိပ်စာ\n"
    "• အလုပ်အတွေ့အကြုံ / တက်ရောက်ခဲ့သော သင်တန်းများ (မရှိလည်း ရေးပေးပါသည်)\n"
    "• လျှောက်ထားလိုသော ရာထူး/အလုပ်အမျိုးအစား\n\n"
    "အချက်အလက်များ ရရှိပါက Admin မှ CV ကို စတင်ရေးသားပေးပါမည်။ CV ပြီးစီးပါက PDF / PNG / JPG "
    "ဖြင့်ပေးပို့ပြီး၊ Payment ကို KBZPay/Wave — 09956413316 သို့ လွှဲပေးရပါမည်။"
)

TICKET_PROMPT = (
    "🎫 <b>ရထားလက်မှတ် ဝန်ဆောင်မှု</b>\n\n"
    "🚆 ခရီးစဉ်များ — ရန်ကုန်-နေပြည်တော်-မန္တလေး / ရန်ကုန်-မော်လမြိုင်\n"
    "📅 (၇) ရက်ကြိုတင်ဝယ်ယူရပါမည် (ကြားဘူတာဆိုပါက ၅ ရက်ကြို)\n\n"
    "အောက်ပါ အချက်အလက်များကို ပေးပို့ပေးပါ —\n"
    "• သွားမည့်သူများ၏ မှတ်ပုံတင်အမည်\n"
    "• မှတ်ပုံတင်အမှတ် (NRC Smart Card မူရင်း / Passport လည်း ရပါသည်)\n"
    "• ခရီးစဉ် (ထွက်မည့်မြို့ → သွားမည့်မြို့) နှင့် သွားမည့်ရက်စွဲ\n"
    "• ဖုန်းနံပါတ်\n\n"
    "အချက်အလက်များ ရရှိပါက Admin မှ စျေးနှုန်းနှင့် အသေးစိတ်ကို ပြန်လည်ဆက်သွယ်ပေးပါမည်။ ဝယ်ယူမည့်နေ့တွင် "
    "လက်မှတ်ခကို KBZPay — 09956413316 (Nay Linn Htet) သို့ လွှဲပေးရပါမည်။ ဝယ်ယူပြီးသည်နှင့် E-ticket (PDF) ကို "
    "ချက်ချင်း ပေးပို့ပေးပါမည်။ Cancel/Refund နှင့် ရက်စွဲပြောင်းခြင်း မပြုလုပ်နိုင်ပါ။"
)

GRADE12_PROMPT = (
    "🎓 <b>တက္ကသိုလ်ဝင်တန်း (Grade 12) ရလဒ် စစ်ဆေးခြင်း</b>\n\n"
    "အောက်ပါ အချက်အလက် (၄) ခုကို အတိအကျ ပေးပို့ပေးပါ —\n"
    "• အမည်\n"
    "• ခုံအမှတ်\n"
    "• စာဖြေခုနှစ်\n"
    "• စာစစ်ဌာန\n"
    "• အဖအမည်\n\n"
    "ဥပမာ —\n"
    "အမည် — ......\n"
    "ခုံအမှတ် — ......\n"
    "စာဖြေခုနှစ် — ၂၀၂၆\n"
    "စာစစ်ဌာန- ......\n"
    "အဖအမည် — ......\n\n"
    "ပြည့်စုံစွာ ပေးပို့ပြီးပါက Admin မှ ရလဒ်ကို စစ်ဆေးပြီး ပြန်လည်အကြောင်းကြားပေးပါမည်။"
)

CONTACT_PROMPT = (
    "✉️ သင့်စကား သို့မဟုတ် မေးခွန်းကို ဒီမှာတိုက်ရိုက် ရိုက်ပို့နိုင်ပါတယ်။ "
    "Admin က အမြန်ဆုံး ပြန်လည်ဆက်သွယ်ပေးပါမယ်။"
)


@router.message(F.text == "📝 CV ရေးသားရန်")
async def reply_kb_cv(message: Message) -> None:
    await message.answer(CV_PROMPT)


@router.message(F.text == "🎫 လက်မှတ် (ကား/ရထား)")
async def reply_kb_ticket(message: Message) -> None:
    await message.answer(TICKET_PROMPT)


@router.message(F.text == "🎓 တက္ကသိုလ်ဝင်တန်း ရလဒ်")
async def reply_kb_grade12(message: Message) -> None:
    await message.answer(GRADE12_PROMPT)


@router.message(F.text == "📖 မေးလေ့ရှိသောမေးခွန်း")
async def reply_kb_faq(message: Message) -> None:
    categories = await list_faq_categories()
    if not categories:
        await message.answer("အမေးများသောမေးခွန်းများ မရှိသေးပါ။")
        return
    await message.answer("📖 မေးလိုသော အမျိုးအစားကို ရွေးချယ်ပါ", reply_markup=faq_category_keyboard(categories))


@router.message(F.text == "✉️ ဆက်သွယ်ရန်")
async def reply_kb_contact(message: Message) -> None:
    await message.answer(CONTACT_PROMPT)


@router.message(F.text)
async def handle_customer_text(message: Message) -> None:
    """Catch-all for any other text: FAQ match first, then forward to admin."""
    user_tg = message.from_user

    if await is_banned(user_tg.id):
        await message.answer(
            "⛔️ သင့်အား ဤဘော့ကို အသုံးပြုခွင့် ကန့်သတ်ထားပါသည်။ "
            "အခြားနည်းလမ်းဖြင့် ဆက်သွယ်ပေးပါ။"
        )
        return

    user = await get_or_create_user(user_tg.id, user_tg.username, user_tg.first_name)

    faq = await find_faq_match(message.text)
    if faq is not None:
        await message.answer(f"❓ {faq.question}\n\n{faq.answer}")
        return

    await forward_to_admins(message.bot, user, message.text)
    await message.answer(
        "✅ ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။ သင့်စာကို လက်ခံရရှိပါပြီ။ Admin မှ အမြန်ဆုံး ပြန်လည်ဆက်သွယ်ပေးပါမယ်။"
    )
