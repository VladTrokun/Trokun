import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, TMDB_API_KEY
from handlers.main_handlers import router as main_router # Імпортуємо головний роутер обробників


async def main():
    # Перевірка наявності необхідних токенів
    if not BOT_TOKEN:
        logging.critical("Не знайдено BOT_TOKEN. Переконайтеся, що він є у .env")
        sys.exit(1)
    if not TMDB_API_KEY:
        logging.critical("Не знайдено TMDB_API_KEY. Переконайтеся, що він є у .env")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO) # Налаштування логування

    bot = Bot(token=BOT_TOKEN) # Ініціалізація об'єкта Бота

    storage = MemoryStorage() # Сховище для FSM (Finite State Machine)

    dp = Dispatcher(storage=storage) # Ініціалізація Диспетчера

    dp.include_router(main_router) # Реєстрація роутера з обробниками

    print("Бот запускається...")
    await dp.start_polling(bot) # Запуск процесу опитування (polling)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот зупинено.")