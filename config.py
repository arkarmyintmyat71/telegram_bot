"""
Central configuration, loaded from environment variables / .env file.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Fetch a required env var, or exit with a clear error instead of a
    confusing crash deep inside some other module."""
    value = os.getenv(name)
    if not value:
        sys.exit(
            f"Missing required environment variable: {name}\n"
            f"Set it in your local .env file, or in Railway's Variables tab for this service."
        )
    return value


# --- Telegram ---------------------------------------------------------
BOT_TOKEN: str = _require("BOT_TOKEN")

# Comma-separated list of admin Telegram user IDs, e.g. "123456789,987654321"
_admin_ids_raw = os.getenv("ADMIN_IDS", "1678659382")
ADMIN_IDS: list[int] = [
    int(x.strip())
    for x in _admin_ids_raw.split(",")
    if x.strip().isdigit()
]

# --- Database -----------------------------------------------------------
# Local default: SQLite file (zero setup, great for development/testing).
# Production: point this at a PostgreSQL instance (Neon, Supabase, Render, ...).
#
# Accepts the plain connection string your provider gives you, e.g.:
#   postgresql://user:pass@host/dbname?sslmode=require&channel_binding=require
# It will automatically be upgraded to use the async driver, and SSL (required
# by Neon) is configured separately in database.py via connect_args.
_raw_db_url = os.getenv("DATABASE_URL", "postgresql://postgres:uZhIZSITyBVzwQdevanPbwfSqmuYetGZ@postgres.railway.internal:5432/railway")

if _raw_db_url.startswith("postgres://"):
    _raw_db_url = _raw_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_db_url.startswith("postgresql://"):
    _raw_db_url = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg's connect() doesn't accept libpq-style query params like sslmode=
# or channel_binding= (both of which Neon's connection strings include) —
# passing them through raises a TypeError at connection time. Strip any
# query params here; SSL itself is re-enabled properly via connect_args in
# database.py, so this is safe for Neon and any other provider that requires it.
if "?" in _raw_db_url:
    _base, _, _query = _raw_db_url.partition("?")
    _kept = [
        p for p in _query.split("&")
        if p.split("=", 1)[0] not in {"sslmode", "channel_binding"}
    ]
    _raw_db_url = _base + ("?" + "&".join(_kept) if _kept else "")

DATABASE_URL = _raw_db_url
IS_POSTGRES = DATABASE_URL.startswith("postgresql+asyncpg://")

# --- Housekeeping -------------------------------------------------------
# How many days of message history to keep before auto-deleting.
MESSAGE_RETENTION_DAYS: int = int(os.getenv("MESSAGE_RETENTION_DAYS", "30"))

# How often (in hours) to run the cleanup job.
CLEANUP_INTERVAL_HOURS: int = int(os.getenv("CLEANUP_INTERVAL_HOURS", "24"))

# Links shown in the customer menu — edit these for your real business.
WEBSITE_URL: str = os.getenv("WEBSITE_URL", "https://example.com")
