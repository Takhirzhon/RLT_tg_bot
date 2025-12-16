# Telegram Analytics Bot (RLT Test Task)

A Telegram bot that provides natural language analytics for video data using PostgreSQL and OpenRouter (LLM).

## Features
- **Natural Language Interface**: Ask questions like "How many videos got views yesterday?"
- **SQL Generation**: Uses an LLM to convert text to SQL queries.
- **Analytics**: Tracks views, likes, comments, and reports for videos and their hourly snapshots.

## Architecture
- **Language**: Python 3.11+
- **Bot Framework**: `aiogram`
- **Database**: PostgreSQL (via Docker)
- **ORM**: `SQLAlchemy` (Async)
- **LLM Integration**: OpenRouter API (Supports DeepSeek, Gemini, GPT-4). Configurable via `.env`.

## Setup & Launch

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+ (Tested on 3.14 via `psycopg` driver)

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```
Required variables:
- `BOT_TOKEN`: Your Telegram Bot Token
- `OPENROUTER_API_KEY`: Key from OpenRouter
- `DATABASE_URL`: `postgresql+psycopg://postgres:postgres@localhost:5432/rlt_bot` (Note: `psycopg` driver used for better compatibility)
- `LLM_MODEL`: e.g. `google/gemini-2.0-flash-exp:free` or `deepseek/deepseek-chat`

### 3. Start Database
```bash
docker-compose up -d
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Ingest Data
Place your `videos.json` in the root directory and run:
```bash
python scripts/ingest.py
```

### 6. Run the Bot
```bash
python main.py
```

## How It Works
1. User sends a text message.
2. `LLMService` constructs a prompt with the database schema and the user's query.
3. The LLM returns a SQL query.
4. The bot executes the SQL against PostgreSQL and returns the result number.

## Checker Instructions
To run the checker:
1. Ensure the bot is running (`python main.py`).
2. Send `/check @YourBotName https://github.com/your-repo` to `@rlt_test_checker_bot`.
