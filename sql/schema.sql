-- Reference schema. You do NOT need to run this manually —
-- database.py automatically creates these tables on first run
-- via SQLAlchemy's Base.metadata.create_all().
-- This file is kept for documentation / manual inspection only.

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(64),
    first_name VARCHAR(128),
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    sender VARCHAR(16) NOT NULL, -- 'customer' or 'admin'
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS faq (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    answer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forward_map (
    id SERIAL PRIMARY KEY,
    admin_chat_id BIGINT NOT NULL,
    admin_message_id BIGINT NOT NULL,
    customer_telegram_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS broadcast_log (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    sent_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Suggested retention policy (run manually or rely on the bot's built-in
-- scheduled cleanup job instead):
-- DELETE FROM messages WHERE created_at < NOW() - INTERVAL '30 days';
-- DELETE FROM forward_map WHERE created_at < NOW() - INTERVAL '30 days';
-- DELETE FROM broadcast_log WHERE created_at < NOW() - INTERVAL '30 days';
