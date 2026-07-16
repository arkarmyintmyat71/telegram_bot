# Telegram Support Bot

A customer-support Telegram bot with:

- `/start` welcome menu with buttons (Order, Contact, FAQ, Support)
- Automatic FAQ replies
- Forwarding of unknown customer messages to **all admins**
- Admins reply by simply **replying** to the forwarded message — the bot routes it back to the right customer automatically
- Admin-only commands: `/users`, `/stats`, `/ban`, `/unban`, `/broadcast`
- PostgreSQL (or SQLite for local testing) storage of users & message history
- Automatic daily cleanup of old messages (configurable retention)
- Ready to deploy on Render or Railway, connected to GitHub

---

## Project structure

```
telegram-support-bot/
├── bot.py                     # Entry point
├── config.py                  # Loads settings from .env
├── database.py                # Async SQLAlchemy engine/session
├── models.py                  # User, Message, FAQ, ForwardMap, BroadcastLog
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile                   # For Render/Railway
├── handlers/
│   ├── start.py                # /start /help /menu /contact
│   ├── customer.py             # FAQ auto-reply + forward-to-admin logic
│   ├── admin.py                # Admin commands + reply routing
│   └── callback.py             # Inline button presses
├── keyboards/
│   └── customer.py             # Reply & inline keyboards
├── services/
│   └── message_service.py      # All business logic (DB reads/writes)
├── utils/
│   └── filters.py               # IsAdmin / IsCustomer filters
├── sql/
│   └── schema.sql               # Reference schema (auto-created by SQLAlchemy)
└── README.md
```

---

## 1. Create your bot on Telegram

1. Open Telegram, search **@BotFather**.
2. Send `/newbot`, choose a display name and a username ending in `bot`.
3. Copy the token BotFather gives you, e.g. `123456789:AAExampleToken...`.
4. Find your own Telegram numeric ID by messaging **@userinfobot** — you'll need this for `ADMIN_IDS`. Do the same for your second admin's account if you have one.

---

## 2. Local setup

### Prerequisites
- Python 3.11+ (3.12 recommended)
- pip

### Steps

```bash
cd telegram-support-bot

# Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your real .env file
cp .env.example .env
```

Now edit `.env`:

```
BOT_TOKEN=123456789:AAExampleToken...
ADMIN_IDS=111111111,222222222
DATABASE_URL=sqlite+aiosqlite:///bot.db     # fine for local testing
```

### Run it

```bash
python bot.py
```

You should see `Bot starting (polling mode)...`. A local `bot.db` SQLite file
will be created automatically with all tables and default FAQ entries.

---

## 3. Try it out

**As a customer** (any other Telegram account):
- Send `/start` → you'll see a welcome message + inline menu (Order / Contact / FAQ / Support) plus a persistent keyboard below the text box.
- Tap **FAQ** → pick a question → get an instant automatic answer.
- Type something not in the FAQ, e.g. "Can someone help me?" → the bot forwards it to **every admin** and tells the customer "An admin will reply shortly."

**As an admin** (an account whose ID is in `ADMIN_IDS`):
- You'll receive a message like:
  ```
  📩 Customer #123456 (john_doe)

  Can someone help me?
  ```
- **Reply directly to that message** (use Telegram's reply feature, not a new message) with your answer, e.g. "Yes, how can I help?"
- The bot delivers your reply straight to that customer, and lets any other admin know it's been handled.

**Admin commands** (type these in your DM with the bot):
| Command | What it does |
|---|---|
| `/users` | Lists registered users |
| `/stats` | Shows total users, banned users, total messages |
| `/ban <telegram_id>` | Prevents a user from messaging the bot |
| `/unban <telegram_id>` | Restores access |
| `/broadcast <text>` | Sends `<text>` to every non-banned user |

---

## 4. Switching to PostgreSQL (recommended for production)

Free options: [Neon](https://neon.tech), [Supabase](https://supabase.com), or Render's own PostgreSQL add-on.

1. Create a free Postgres database with one of the providers above.
2. Copy the connection string they give you (usually starts with `postgresql://`).
3. Paste it into `.env` as `DATABASE_URL` — the bot automatically converts it to use the async driver:
   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   ```
4. Restart the bot — tables are created automatically on first run, no manual migration needed.

---

## 5. Deployment (Render or Railway)

### Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/telegram-support-bot.git
git push -u origin main
```

`.env` is excluded via `.gitignore` — never commit real secrets.

### Option A: Render

1. Go to [render.com](https://render.com) → **New** → **Background Worker** (not a Web Service — this bot uses polling, not a public HTTP endpoint).
2. Connect your GitHub repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python bot.py`
5. Under **Environment**, add each variable from `.env.example` with your real values (`BOT_TOKEN`, `ADMIN_IDS`, `DATABASE_URL`, etc.).
6. Deploy. Render keeps the worker running continuously — pushing to `main` triggers automatic redeploys.

### Option B: Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
2. Railway detects the `Procfile` and runs `python bot.py` as a worker.
3. Add the same environment variables in the **Variables** tab.
4. Optionally add Railway's own PostgreSQL plugin and copy its connection string into `DATABASE_URL`.
5. Deploy. Future pushes to GitHub auto-redeploy.

Either way, once deployed your laptop can be off — the bot keeps running on the host, customers keep chatting, and admins keep receiving forwarded messages.

---

## 6. Data retention (staying within free-tier limits)

By default the bot automatically deletes:
- `messages` older than `MESSAGE_RETENTION_DAYS` (default 30)
- `forward_map` entries and `broadcast_log` entries of the same age

...once every `CLEANUP_INTERVAL_HOURS` (default 24), via an internal scheduler — no manual steps needed. Users, admins, and FAQ entries are never deleted by this job.

Adjust both values in `.env` to taste.

---

## 7. Extending

- Add more FAQ entries directly in the database, or add an admin command (`/addfaq`) if you want to manage them without touching the DB.
- Add ticket numbers, file/photo forwarding, or an admin web dashboard later — the project structure (`handlers/`, `services/`, `keyboards/`) is set up to make that straightforward.

---

## 8. Troubleshooting

| Problem | Likely cause |
|---|---|
| Bot doesn't respond at all | Wrong/placeholder `BOT_TOKEN`, or process not running |
| Admin commands say nothing happens | Your Telegram ID isn't in `ADMIN_IDS` |
| Admin reply not delivered to customer | You replied to the wrong message, or replied in a different admin chat than the one that received the forward |
| Works locally, not on Render/Railway | Environment variables not set on the platform, or `DATABASE_URL` still pointing at local SQLite |
| Database grows too large on free tier | Lower `MESSAGE_RETENTION_DAYS` / `CLEANUP_INTERVAL_HOURS` |
