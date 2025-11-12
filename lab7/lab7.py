# Імпортуємо потрібні модулі
import os  # Для роботи з операційною системою
from dotenv import load_dotenv  # Для завантаження .env файлів
from telegram import Update  # Клас для представлення оновлень від Telegram
from telegram.ext import Application, MessageHandler, filters, ContextTypes  # Основні класи бібліотеки

# 1. Завантажуємо токен з .env файлу
load_dotenv()  # Завантажує змінні з файлу .env
TOKEN = os.getenv('TOKEN')  # Отримує токен зі змінних оточення

# Перевірка, чи токен знайдено
if not TOKEN:
    print("Помилка: Не знайдено TOKEN у .env.")  # Повідомлення про помилку
    exit(1)  # Завершуємо програму, якщо токена немає


# 2. Функція-обробник для ехо-відповіді
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Виводимо отриманий текст у консоль (для себе)
    print(f"Отримано: {update.message.text}")

    # Відправляємо користувачу той самий текст назад
    await update.message.reply_text(update.message.text)


# 3. Головна функція для налаштування та запуску бота
def main():
    print("Створюємо програму...")

    # Створюємо об'єкт Application з нашим токеном
    application = Application.builder().token(TOKEN).build()

    # Створюємо обробник повідомлень
    # Він реагує на звичайний текст (TEXT) і не реагує на команди (COMMAND)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # Реєструємо обробник в програмі
    application.add_handler(echo_handler)

    # Запускаємо бота в режимі опитування (polling)
    print("Бот запускається...")
    application.run_polling()


# 4. Стандартна конструкція для запуску скрипта
if __name__ == "__main__":
    main()  # Викликаємо головну функцію