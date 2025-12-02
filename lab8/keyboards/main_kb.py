import urllib.parse # Імпорт для кодування URL-запитів
from telebot.types import ( # Імпорт класів клавіатур з telebot
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# 1. Головна клавіатура (ReplyKeyboardMarkup) - звичайне меню
main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) # Створення об'єкта
main_menu_kb.row(KeyboardButton(text="🏆 Топ-5"), KeyboardButton(text="🔥 Новинки")) # Додавання першого рядка кнопок
main_menu_kb.row(KeyboardButton(text="🔍 Пошук за назвою"), KeyboardButton(text="🎭 Пошук за жанром")) # Додавання другого рядка кнопок


# 2. Вбудована клавіатура для меню "Топ-5" (InlineKeyboardMarkup)
top_rated_menu = InlineKeyboardMarkup(keyboard=[ # Створення об'єкта з кнопками
    [InlineKeyboardButton(text="🎬 Найкращі фільми", callback_data="top_movie")], # Кнопка для фільмів
    [InlineKeyboardButton(text="📺 Найкращі серіали", callback_data="top_tv")], # Кнопка для серіалів
    [InlineKeyboardButton(text="🧸 Найкращі мультфільми", callback_data="top_cartoon")], # Кнопка для мультфільмів
])

# 3. Вбудована клавіатура для меню "Новинки"
new_releases_menu = InlineKeyboardMarkup(keyboard=[ # Створення об'єкта з кнопками
    [InlineKeyboardButton(text="🎬 Нові фільми (в кіно)", callback_data="new_movie")], # Кнопка для нових фільмів
    [InlineKeyboardButton(text="📺 Нові серіали (в ефірі)", callback_data="new_tv")], # Кнопка для нових серіалів
])


# 4. Функція для створення клавіатури зі списком результатів пошуку
def create_results_keyboard(results: list, media_type_prefix: str) -> InlineKeyboardMarkup:
    buttons = [] # Список для рядків кнопок
    for item in results: # Прохід по кожному результату
        # Обробка результатів змішаного пошуку ('search')
        if media_type_prefix == 'search':
            media_type = item.get('media_type') # Визначення фактичного типу медіа
            if media_type == 'movie':
                title = item.get('title', 'Невідомо') # Отримання назви фільму
                callback_data = f"detail_movie_{item['id']}" # Формування callback_data для фільму
            elif media_type == 'tv':
                title = item.get('name', 'Невідомо') # Отримання назви серіалу
                callback_data = f"detail_tv_{item['id']}" # Формування callback_data для серіалу
            else:
                continue # Пропускаємо невідомі типи
        # Обробка результатів списків (top, new, genre)
        else:
            media_type = media_type_prefix # Тип медіа відомий
            title = item.get('title') if media_type == 'movie' else item.get('name') # Отримання назви
            callback_data = f"detail_{media_type}_{item['id']}" # Формування callback_data
        buttons.append([InlineKeyboardButton(text=title, callback_data=callback_data)]) # Додавання кнопки
    return InlineKeyboardMarkup(buttons) # Повертаємо об'єкт клавіатури


# 5. Функція для створення клавіатури "Де дивитись"
def create_watch_keyboard(title: str, media_type: str, tmdb_id: int) -> InlineKeyboardMarkup:
    search_query = f"{title} дивитись онлайн" # Формування пошукового запиту
    # Створення посилання на Google Search з закодованим запитом
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

    # Створення посилання на сторінку TMDB
    tmdb_url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}"

    buttons = [ # Список кнопок
        [InlineKeyboardButton(text="🔍 Знайти, де дивитись (Google)", url=google_url)], # Кнопка Google
        [InlineKeyboardButton(text="ℹ️ Більше інформації на TMDB", url=tmdb_url)] # Кнопка TMDB
    ]
    return InlineKeyboardMarkup(buttons) # Повертаємо об'єкт клавіатури