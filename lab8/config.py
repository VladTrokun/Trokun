import os # Імпорт модуля для взаємодії з операційною системою (для змінних оточення)
from dotenv import load_dotenv # Імпорт функції для завантаження файлу .env

# Завантажуємо змінні оточення з файлу .env
load_dotenv()

# Ключі та токени
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Отримання токена Telegram-бота зі змінних оточення
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Отримання ключа доступу до TMDB API зі змінних оточення

# Базові URL-адреси TMDB
TMDB_BASE_URL = "https://api.themoviedb.org/3" # Основна адреса TMDB API
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500" # Базова адреса для отримання постерів (розмір w500)

# URL для постера-заглушки
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/500x750.png?text=Poster+Not+Found" # Посилання на заглушку, якщо постер відсутній