import urllib.parse
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏆 Топ-5"), KeyboardButton(text="🔥 Новинки")],
        [KeyboardButton(text="🔍 Пошук за назвою"), KeyboardButton(text="🎭 Пошук за жанром")],
        [KeyboardButton(text="💬 Пошук за побажаннями"), KeyboardButton(text="🎲 Випадкова порада")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть дію з меню..."
)

top_rated_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎬 Найкращі фільми", callback_data="top_movie")],
    [InlineKeyboardButton(text="📺 Найкращі серіали", callback_data="top_tv")],
    [InlineKeyboardButton(text="🧸 Найкращі мультфільми", callback_data="top_cartoon")],
])

new_releases_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎬 Нові фільми (в кіно)", callback_data="new_movie")],
    [InlineKeyboardButton(text="📺 Нові серіали (в ефірі)", callback_data="new_tv")],
])


def create_results_keyboard(results: list, media_type_prefix: str) -> InlineKeyboardMarkup:
    buttons = []
    for item in results:
        if media_type_prefix == 'search':
            media_type = item.get('media_type')
            if media_type == 'movie':
                title = item.get('title', 'Невідомо')
                callback_data = f"detail_movie_{item['id']}"
            elif media_type == 'tv':
                title = item.get('name', 'Невідомо')
                callback_data = f"detail_tv_{item['id']}"
            else:
                continue
        else:
            media_type = media_type_prefix
            title = item.get('title') if media_type == 'movie' else item.get('name')
            callback_data = f"detail_{media_type}_{item['id']}"
        buttons.append([InlineKeyboardButton(text=title, callback_data=callback_data)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_watch_keyboard(title: str, media_type: str, tmdb_id: int) -> InlineKeyboardMarkup:

    search_query = f"{title} дивитись онлайн"
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

    tmdb_url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}"

    buttons = [
        [InlineKeyboardButton(text="🔍 Знайти, де дивитись (Google)", url=google_url)],
        [InlineKeyboardButton(text="ℹ️ Більше інформації на TMDB", url=tmdb_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)