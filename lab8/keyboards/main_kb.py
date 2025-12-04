import urllib.parse # Імпорт для кодування URL-запитів, наприклад, для Google Search
from telebot.types import ( # Імпорт необхідних класів клавіатур з telebot
    ReplyKeyboardMarkup, KeyboardButton, # Класи для звичайних клавіатур (під полем вводу)
    InlineKeyboardMarkup, InlineKeyboardButton # Класи для вбудованих (inline) клавіатур
)

# 1. Головна клавіатура (ReplyKeyboardMarkup) - звичайне меню
main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False) # Створення об'єкта Reply-клавіатури (головне меню)
main_menu_kb.row(KeyboardButton(text="🏆 Топ-5"), KeyboardButton(text="🔥 Новинки")) # Додавання першого рядка кнопок: "Топ-5" та "Новинки"
main_menu_kb.row(KeyboardButton(text="🎲 Випадковий фільм")) # Додавання другого рядка: "Випадковий фільм"


# 2. Вбудована клавіатура для меню "Топ-5" (InlineKeyboardMarkup)
top_rated_menu = InlineKeyboardMarkup(keyboard=[ # Створення об'єкта Inline-клавіатури для меню "Топ-5"
    [InlineKeyboardButton(text="🎬 Найкращі фільми", callback_data="top_movie")], # Кнопка для топ-фільмів
    [InlineKeyboardButton(text="📺 Найкращі серіали", callback_data="top_tv")], # Кнопка для топ-серіалів
    [InlineKeyboardButton(text="🧸 Найкращі мультфільми", callback_data="top_cartoon")], # Кнопка для топ-мультфільмів
])

# 3. Вбудована клавіатура для меню "Новинки"
new_releases_menu = InlineKeyboardMarkup(keyboard=[ # Створення об'єкта Inline-клавіатури для меню "Новинки"
    [InlineKeyboardButton(text="🎬 Нові фільми (в кіно)", callback_data="new_movie")], # Кнопка для нових фільмів
    [InlineKeyboardButton(text="📺 Нові серіали (в ефірі)", callback_data="new_tv")], # Кнопка для нових серіалів
])


# 4. Функція для створення клавіатури зі списком результатів пошуку
def create_results_keyboard(results: list, media_type_prefix: str) -> InlineKeyboardMarkup:
    buttons = [] # Список для зберігання рядків кнопок
    for item in results: # Прохід по кожному елементу (фільму/серіалу) у списку результатів
        # Обробка результатів змішаного пошуку ('search')
        if media_type_prefix == 'search':
            media_type = item.get('media_type') # Визначення фактичного типу медіа (movie або tv)
            if media_type == 'movie':
                title = item.get('title', 'Невідомо') # Отримання назви фільму
                callback_data = f"detail_movie_{item['id']}" # Формування даних для колбеку (деталі фільму)
            elif media_type == 'tv':
                title = item.get('name', 'Невідомо') # Отримання назви серіалу
                callback_data = f"detail_tv_{item['id']}" # Формування даних для колбеку (деталі серіалу)
            else:
                continue # Пропускаємо невідомі типи
        # Обробка результатів списків (top, new, genre)
        else:
            media_type = media_type_prefix # Тип медіа відомий
            title = item.get('title') if media_type == 'movie' else item.get('name') # Отримання назви (різна логіка для movie/tv)
            callback_data = f"detail_{media_type}_{item['id']}" # Формування даних для колбеку
        buttons.append([InlineKeyboardButton(text=title, callback_data=callback_data)]) # Додавання кнопки до списку рядків
    return InlineKeyboardMarkup(buttons) # Повертаємо об'єкт Inline-клавіатури


# 5. Функція для створення клавіатури "Де дивитись"
def create_watch_keyboard(title: str, media_type: str, tmdb_id: int) -> InlineKeyboardMarkup:
    search_query = f"{title} дивитись онлайн" # Формування пошукового запиту для Google
    # Створення посилання на Google Search з закодованим запитом (безпечне для URL)
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

    # Створення посилання на сторінку TMDB
    tmdb_url = f"https://www.themoviedb.org/{media_type}/{tmdb_id}"

    buttons = [ # Список кнопок
        [InlineKeyboardButton(text="🔍 Знайти, де дивитись (Google)", url=google_url)], # Кнопка з посиланням на Google
        [InlineKeyboardButton(text="ℹ️ Більше інформації на TMDB", url=tmdb_url)] # Кнопка з посиланням на сторінку TMDB
    ]
    return InlineKeyboardMarkup(buttons) # Повертаємо об'єкт Inline-клавіатури