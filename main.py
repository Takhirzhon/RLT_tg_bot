import asyncio
import logging
import os
import sys

# Ensure bot package is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

from bot.services.llm_service import LLMService

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN is not set")
    sys.exit(1)

# Initialize
dp = Dispatcher()
llm_service = None

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Я аналитический бот.\n"
        "Спроси меня о чем-нибудь, например: 'Сколько видео вышло 28 ноября 2025?'"
    )

@dp.message()
async def query_handler(message: Message) -> None:
    if not message.text:
        return

    # Notify user we are thinking
    status_msg = await message.answer("Думаю...")
    
    try:
        # 1. Generate SQL
        user_query = message.text
        logger.info(f"User Query: {user_query}")
        
        sql_query = await llm_service.generate_sql(user_query)
        logger.info(f"Generated SQL: {sql_query}")
        
        # 2. Execute SQL
        result = await llm_service.execute_sql(sql_query)
        logger.info(f"Result: {result}")
        
        # 3. Reply
        await status_msg.edit_text(str(result))
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        await status_msg.edit_text("Произошла ошибка при обработке запроса.")

async def main() -> None:
    global llm_service
    # Initialize service
    try:
        llm_service = LLMService()
    except Exception as e:
        logger.error(f"Failed to init LLMService: {e}")
        return

    bot = Bot(token=TOKEN)
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
