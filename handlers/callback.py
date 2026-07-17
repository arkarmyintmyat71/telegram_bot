"""
Handlers for inline keyboard button presses (menu:cv, menu:ticket, menu:grade12, ...).
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.customer import (
    back_to_faq_keyboard,
    faq_category_keyboard,
    faq_list_keyboard,
    main_inline_menu,
)
from services.message_service import (
    FAQ_CATEGORY_LABELS,
    faq_category,
    get_faq_by_id,
    list_faq_categories,
    list_faqs_by_category,
)

router = Router(name="callback")

CV_PROMPT = (
    "📝 <b>CV ရေးသားခြင်း ဝန်ဆောင်မှု</b>\n\n"
    "အောက်ပါ အချက်အလက်များကို ပေးပို့ပေးပါ —\n"
    "• အမည်\n"
    "• အသက်\n"
    "• ပညာအရည်အချင်း\n"
    "• အလုပ်အတွေ့အကြုံ (ရှိပါက)\n"
    "• ဖုန်းနံပါတ်\n"
    "• လျှောက်ထားလိုသော ရာထူး/အလုပ်အမျိုးအစား\n\n"
    "အချက်အလက်များ ရရှိပါက Admin မှ CV ကို စတင်ရေးသားပေးပါမည်။"
)

TICKET_PROMPT = (
    "🎫 <b>လက်မှတ် (ရထား/ဘတ်စ်ကား) ဝန်ဆောင်မှု</b>\n\n"
    "အောက်ပါ အချက်အလက်များကို ပေးပို့ပေးပါ —\n"
    "• ခရီးစဉ် (ထွက်မည့်မြို့ → သွားမည့်မြို့)\n"
    "• ခရီးသွားမည့် ရက်စွဲ\n"
    "• ခရီးသည် အမည်\n"
    "• ဖုန်းနံပါတ်\n"
    "• လက်မှတ်အမျိုးအစား (ရထား သို့မဟုတ် ဘတ်စ်ကား)\n\n"
    "အချက်အလက်များ ရရှိပါက Admin မှ စျေးနှုန်းနှင့် အသေးစိတ်ကို ပြန်လည်ဆက်သွယ်ပေးပါမည်။"
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
    "စာဖြေခုနှစ် — ၂၀၂၅\n"
    "စာစစ်ဌာန — ......\n"
    "အဖအမည် — ......\n\n"
    "ပြည့်စုံစွာ ပေးပို့ပြီးပါက Admin မှ ရလဒ်ကို စစ်ဆေးပြီး ပြန်လည်အကြောင်းကြားပေးပါမည်။"
)

CONTACT_PROMPT = (
    "✉️ သင့်စကား သို့မဟုတ် မေးခွန်းကို ဒီမှာတိုက်ရိုက် ရိုက်ပို့နိုင်ပါတယ်။ "
    "Admin က အမြန်ဆုံး ပြန်လည်ဆက်သွယ်ပေးပါမယ်။"
)


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text("ဘာများ လိုအပ်ပါသလဲခင်ဗျာ။", reply_markup=main_inline_menu())
    await callback.answer()


@router.callback_query(F.data == "menu:cv")
async def cb_cv(callback: CallbackQuery) -> None:
    await callback.message.edit_text(CV_PROMPT, reply_markup=back_to_faq_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:ticket")
async def cb_ticket(callback: CallbackQuery) -> None:
    await callback.message.edit_text(TICKET_PROMPT, reply_markup=back_to_faq_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:grade12")
async def cb_grade12(callback: CallbackQuery) -> None:
    await callback.message.edit_text(GRADE12_PROMPT, reply_markup=back_to_faq_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:contact")
async def cb_contact(callback: CallbackQuery) -> None:
    await callback.message.edit_text(CONTACT_PROMPT, reply_markup=back_to_faq_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:faq")
async def cb_faq(callback: CallbackQuery) -> None:
    categories = await list_faq_categories()
    if not categories:
        await callback.message.edit_text("အမေးများသောမေးခွန်းများ မရှိသေးပါ။", reply_markup=main_inline_menu())
    else:
        await callback.message.edit_text(
            "📖 မေးလိုသော အမျိုးအစားကို ရွေးချယ်ပါ", reply_markup=faq_category_keyboard(categories)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("faqcat:"))
async def cb_faq_category(callback: CallbackQuery) -> None:
    category = callback.data.split(":", 1)[1]
    faqs = await list_faqs_by_category(category)
    if not faqs:
        await callback.answer("ဤအမျိုးအစားတွင် မေးခွန်းများ မရှိသေးပါ။", show_alert=True)
        return
    label = FAQ_CATEGORY_LABELS.get(category, category)
    await callback.message.edit_text(f"📖 {label}", reply_markup=faq_list_keyboard(faqs, category))
    await callback.answer()


@router.callback_query(F.data.startswith("faq:"))
async def cb_faq_answer(callback: CallbackQuery) -> None:
    faq_id = int(callback.data.split(":", 1)[1])
    faq = await get_faq_by_id(faq_id)
    if faq is None:
        await callback.answer("ဤ FAQ အကြောင်းအရာကို ရှာမတွေ့တော့ပါ။", show_alert=True)
        return
    await callback.message.edit_text(
        f"❓ {faq.question}\n\n{faq.answer}",
        reply_markup=back_to_faq_keyboard(faq_category(faq.question)),
    )
    await callback.answer()
