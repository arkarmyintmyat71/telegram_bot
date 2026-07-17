"""
Central configuration, loaded from environment variables / .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---------------------------------------------------------
BOT_TOKEN: str = os.getenv("BOT_TOKEN")

# Comma-separated list of admin Telegram user IDs, e.g. "123456789,987654321"
_admin_ids_raw = os.getenv("ADMIN_IDS", "")

ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in _admin_ids_raw.split(",")
    if x.strip().isdigit()
]

# --- Database -----------------------------------------------------------
# Local default: SQLite file (zero setup, great for development/testing).
# Production: point this at a free PostgreSQL instance (Neon, Supabase, Render).
#
# Accepts the plain connection string your provider gives you, e.g.:
#   postgresql://user:pass@host/dbname
# It will automatically be upgraded to use the async driver.
_raw_db_url = os.getenv("DATABASE_URL")

if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_db_url.startswith("postgresql://"):
    _raw_db_url = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Remove parameters that asyncpg doesn't accept in the URL
_raw_db_url = _raw_db_url.replace("?sslmode=require&channel_binding=require", "")

DATABASE_URL = _raw_db_url

# --- Housekeeping -------------------------------------------------------
# How many days of message history to keep before auto-deleting.
MESSAGE_RETENTION_DAYS: int = int(os.getenv("MESSAGE_RETENTION_DAYS"))

# How often (in hours) to run the cleanup job.
CLEANUP_INTERVAL_HOURS: int = int(os.getenv("CLEANUP_INTERVAL_HOURS"))

# Links shown in the customer menu — edit these for your real business.
WEBSITE_URL: str = os.getenv("WEBSITE_URL")
