import logging # Імпорт для логування
import sys # Імпорт для виходу з програми
import telebot # Імпорт головної бібліотеки Telegram бота
from telebot.storage import StateMemoryStorage # Імпорт сховища FSM

from config import BOT_TOKEN, TMDB_API_KEY # Імпорт токенів
from handlers.main_handlers import register_handlers # Імпорт функції реєстрації обробників


def main():
    # Перевірка наявності необхідних токенів
    if not BOT_TOKEN:
        logging.critical("Не знайдено BOT_TOKEN. Переконайтеся, що він є у .env")
        sys.exit(1) # Вихід з помилкою
    if not TMDB_API_KEY:
        logging.critical("Не знайдено TMDB_API_KEY. Переконайтеся, що він є у .env")
        sys.exit(1) # Вихід з помилкою

    logging.basicConfig(level=logging.INFO) # Налаштування рівня логування

    # Використовуємо StateMemoryStorage для FSM
    storage = StateMemoryStorage()
    bot = telebot.TeleBot(token=BOT_TOKEN, state_storage=storage) # Ініціалізація об'єкта Бота

    # Реєстрація обробників
    register_handlers(bot, storage)

    print("Бот запускається...")
    # Запуск процесу опитування (polling)
    try:
        bot.polling(none_stop=True) # Запуск бота, не зупиняючись на помилках
    except KeyboardInterrupt:
        print("Бот зупинено.")


if __name__ == "__main__":
    main() # Виклик головної функції