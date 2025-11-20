import urllib.parse
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# 1. Головна клавіатура (ReplyKeyboardMarkup)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏆 Топ-5"), KeyboardButton(text="🔥 Новинки")],
        [KeyboardButton(text="🔍 Пошук за назвою"), KeyboardButton(text="🎭 Пошук за жанром")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть дію з меню..."
)

# 2. Вбудована клавіатура для меню "Топ-5"
top_rated_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎬 Найкращі фільми", callback_data="top_movie")],
    [InlineKeyboardButton(text="📺 Найкращі серіали", callback_data="top_tv")],
    [InlineKeyboardButton(text="🧸 Найкращі мультфільми", callback_data="top_cartoon")],
])

# 3. Вбудована клавіатура для меню "Новинки"
new_releases_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎬 Нові фільми (в кіно)", callback_data="new_movie")],
    [InlineKeyboardButton(text="📺 Нові серіали (в ефірі)", callback_data="new_tv")],
])


# 4. Функція для створення клавіатури зі списком результатів пошуку
def create_results_keyboard(results: list, media_type_prefix: str) -> InlineKeyboardMarkup:
    buttons = []
    for item in results:
        # Обробка результатів змішаного пошуку ('search')
        if media_type_prefix == 'search':
            media_type = item.get('media_type')
            if media_type == 'movie':
                title = item.get('title', 'Невідомо')
                callback_data = f"detail_movie_{item['id']}"
            elif media_type == 'tv':
                title = item.get('name', 'Невідомо')
                callback_data = f"detail_tv_{item['id']}"
            else:
                continue # Пропускаємо невідомі типи (наприклад, акторів)
        # Обробка результатів списків (top, new, genre)
        else:
            media_type = media_type_prefix
            # Отримуємо назву залежно від типу
            title = item.get('title') if media_type == 'movie' else item.get('name')
            callback_data = f"detail_{media_type}_{item['id']}" # Формат detail_type_id
        buttons.append([InlineKeyboardButton(text=title, callback_data=callback_data)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 5. Функція для створення клавіатури "Де дивитись" під карткою з деталями
def create_watch_keyboard(title: str, media_type: str, tmdb_id: int) -> InlineKeyboardMarkup:

    search_query = f"{title} дивитись онлайн"
    # Створення посилання на Google Search з закодованим запитом
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

    # Створення посилання на сторінку TMDB
    tmdb_url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}"

    buttons = [
        [InlineKeyboardButton(text="🔍 Знайти, де дивитись (Google)", url=google_url)],
        [InlineKeyboardButton(text="ℹ️ Більше інформації на TMDB", url=tmdb_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)