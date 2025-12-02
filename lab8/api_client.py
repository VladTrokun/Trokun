import requests # Імпорт синхронної бібліотеки для HTTP-запитів
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL, PLACEHOLDER_IMAGE_URL # Імпорт констант з config.py

# Мапа українських жанрів до ID TMDB
GENRE_MAP = {
    'жахи': 27, # ID жанру "жахи"
    'комедія': 35, # ID жанру "комедія"
    'бойовик': 28, # ID жанру "бойовик"
    'фантастика': 878, # ID жанру "фантастика"
    'драма': 18, # ID жанру "драма"
    'трилер': 53, # ID жанру "трилер"
    'мультфільм': 16, # ID жанру "мультфільм"
    'пригоди': 12, # ID жанру "пригоди"
    'фентезі': 14, # ID жанру "фентезі"
    'детектив': 9648, # ID жанру "детектив"
    'сімейний': 10751, # ID жанру "сімейний"
}


# Приватна функція для виконання СИНХРОННИХ API-запитів
def _make_api_request(endpoint: str, params: dict = None) -> dict | None:
    if params is None: # Перевірка, чи параметри не передано
        params = {} # Створення пустого словника параметрів
    params['api_key'] = TMDB_API_KEY # Додаємо ключ API до параметрів
    params['language'] = 'uk-UA'    # Встановлюємо українську мову

    try:
        # Виконуємо GET-запит до TMDB API
        response = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=params)
        response.raise_for_status() # Викликає помилку для 4xx/5xx статусів
        return response.json() # Повертаємо дані у форматі JSON
    except requests.RequestException as e: # Обробка помилок запиту
        print(f"Помилка API запиту: {e}") # Вивід помилки в консоль
        return None # Повертаємо None у разі помилки


# Приватна функція для форматування деталей
def _format_details(item: dict, media_type: str) -> str:
    # Визначаємо назву та дату залежно від типу медіа (movie/tv)
    if media_type == 'movie':
        title = item.get('title', 'Назва невідома') # Отримання назви фільму
        release_date = item.get('release_date', 'Дата невідома') # Отримання дати виходу фільму
    else: # 'tv'
        title = item.get('name', 'Назва невідома') # Отримання назви серіалу
        release_date = item.get('first_air_date', 'Дата невідома') # Отримання дати виходу серіалу

    overview = item.get('overview', 'Опис відсутній.') # Отримання опису
    genres = [g['name'] for g in item.get('genres', [])] # Створення списку назв жанрів
    genre_str = ", ".join(genres) if genres else "Жанр невідомий" # Форматування жанрів у рядок

    # Повертаємо відформатований текст з Markdown
    return (
        f"**{title}**\n\n" # Жирна назва
        f"**Дата виходу:** {release_date}\n" # Дата виходу
        f"**Жанр:** {genre_str}\n\n" # Жанри
        f"**Опис:**\n{overview}" # Опис
    )


# Формує повний URL для постера
def get_poster_url(poster_path: str | None) -> str:
    # Повертає повний URL постера або URL-заглушку
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE_URL


# Отримати топ-5 найбільш рейтингових
def get_top_rated(media_type: str) -> list | None:
    if media_type == 'cartoon': # Якщо шукаємо мультфільми
        # Запит для мультфільмів (фільтр за жанром 16)
        data = _make_api_request("/discover/movie",
                                       {'sort_by': 'vote_average.desc', 'vote_count.gte': 500, 'with_genres': 16})
    else:
        # Стандартний запит для фільмів/серіалів
        data = _make_api_request(f"/{media_type}/top_rated")
    return data.get('results', [])[:5] if data else None # Повертаємо перші 5 результатів


# Пошук за назвою (фільми та серіали)
def search_by_title(query: str) -> list | None:
    data = _make_api_request("/search/multi", {'query': query, 'include_adult': False}) # Запит змішаного пошуку
    if data and 'results' in data: # Перевірка наявності результатів
        # Фільтруємо лише фільми ('movie') та серіали ('tv'), повертаємо топ-5
        return [item for item in data['results'] if item.get('media_type') in ['movie', 'tv']][:5]
    return None # Повертаємо None, якщо результатів немає


# Отримати деталі (повну інформацію) про медіа
def get_details(media_type: str, media_id: int) -> dict | None:
    # Запит деталей за типом та ID
    return _make_api_request(f"/{media_type}/{media_id}")


# Отримати список фільмів за жанром
def get_by_genre(genre_query: str) -> list | None:
    genre_id = GENRE_MAP.get(genre_query.lower().strip()) # Отримуємо ID жанру за назвою
    if not genre_id: # Якщо ID жанру не знайдено
        return None # Повертаємо None
    # Запит до discover з фільтром по жанру та сортуванням по популярності
    data = _make_api_request("/discover/movie", {'sort_by': 'popularity.desc', 'with_genres': genre_id})
    return data.get('results', [])[:5] if data else None # Повертаємо топ-5


# Отримати новинки (в кінотеатрах або в ефірі)
def get_new_releases(media_type: str) -> list | None:
    # Визначаємо ендпоінт для фільмів (now_playing) або серіалів (on_the_air)
    endpoint = "/movie/now_playing" if media_type == 'movie' else "/tv/on_the_air"
    data = _make_api_request(endpoint) # Виконання запиту
    return data.get('results', [])[:5] if data else None # Повертаємо топ-5