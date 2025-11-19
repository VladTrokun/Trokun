import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, TMDB_API_KEY
from handlers.main_handlers import router as main_router


async def main():
    if not BOT_TOKEN:
        logging.critical("Не знайдено BOT_TOKEN. Переконайтеся, що він є у .env")
        sys.exit(1)
    if not TMDB_API_KEY:
        logging.critical("Не знайдено TMDB_API_KEY. Переконайтеся, що він є у .env")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(main_router)

    print("Бот запускається...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинено.")