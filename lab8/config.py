import os
from dotenv import load_dotenv

# Завантажуємо змінні оточення з файлу .env
load_dotenv()

# Ключі та токени
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен Telegram-бота
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Ключ доступу до TMDB API

# Базові URL-адреси TMDB
TMDB_BASE_URL = "https://api.themoviedb.org/3" # основна адреса сайту
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500" # постери

# URL для постера-заглушки
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/500x750.png?text=Poster+Not+Found"