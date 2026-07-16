"""
Telegram Support Bot — entry point.

Run locally:      python bot.py
Deploy:            see README.md (Render / Railway)
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, CLEANUP_INTERVAL_HOURS, MESSAGE_RETENTION_DAYS
from database import init_db
from handlers import all_routers
from services.message_service import cleanup_old_data, seed_faqs_if_empty

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def scheduled_cleanup() -> None:
    try:
        await cleanup_old_data(MESSAGE_RETENTION_DAYS)
    except Exception:
        logger.exception("Scheduled cleanup failed.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Please check your .env file.")
    
    await init_db()
    await seed_faqs_if_empty()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_cleanup, "interval", hours=CLEANUP_INTERVAL_HOURS)
    scheduler.start()

    logger.info("Bot starting (polling mode)...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
