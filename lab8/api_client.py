import requests  # Імпорт синхронної бібліотеки для HTTP-запитів
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL, \
    PLACEHOLDER_IMAGE_URL  # Імпорт констант конфігурації
import random  # Додаємо для вибору випадкової сторінки для випадкового фільму

# Мапа українських жанрів до ID TMDB
GENRE_MAP = {
    'жахи': 27,  # ID жанру "жахи" на TMDB
    'комедія': 35,  # ID жанру "комедія" на TMDB
    'бойовик': 28,  # ID жанру "бойовик" на TMDB
    'фантастика': 878,  # ID жанру "фантастика" на TMDB
    'драма': 18,  # ID жанру "драма" на TMDB
    'трилер': 53,  # ID жанру "трилер" на TMDB
    'мультфільм': 16,  # ID жанру "мультфільм" на TMDB
    'пригоди': 12,  # ID жанру "пригоди" на TMDB
    'фентезі': 14,  # ID жанру "фентезі" на TMDB
    'детектив': 9648,  # ID жанру "детектив" на TMDB
    'сімейний': 10751,  # ID жанру "сімейний" на TMDB
}


# Приватна функція для виконання СИНХРОННИХ API-запитів
def _make_api_request(endpoint: str, params: dict = None) -> dict | None:
    if params is None:  # Перевірка, чи параметри не передано
        params = {}  # Створення пустого словника параметрів, якщо він None
    params['api_key'] = TMDB_API_KEY  # Додаємо ключ API до параметрів запиту
    params['language'] = 'uk-UA'  # Встановлюємо українську мову для відповідей API

    try:
        response = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=params,
                                timeout=10)  # Виконання GET-запиту з таймаутом
        response.raise_for_status()  # Викликає виняток, якщо HTTP-статус помилковий (4xx або 5xx)
        return response.json()  # Повернення відповіді у форматі словника Python
    except requests.RequestException as e:
        print(f"ПОМИЛКА API ЗАПИТУ: {e}")  # Логування помилки запиту
        return None  # Повернення None у разі помилки


# Приватна функція для форматування деталей
def _format_details(item: dict, media_type: str) -> str:
    # Визначаємо назву та дату залежно від типу медіа (movie/tv)
    if media_type == 'movie':
        title = item.get('title', 'Назва невідома')  # Отримання назви фільму
        release_date = item.get('release_date', 'Дата невідома')  # Отримання дати виходу фільму
    else:  # 'tv'
        title = item.get('name', 'Назва невідома')  # Отримання назви серіалу
        release_date = item.get('first_air_date', 'Дата невідома')  # Отримання дати виходу серіалу

    overview = item.get('overview', 'Опис відсутній.')  # Отримання опису
    genres = [g['name'] for g in item.get('genres', [])]  # Створення списку назв жанрів
    genre_str = ", ".join(genres) if genres else "Жанр невідомий"  # Форматування жанрів у рядок

    # Повертаємо відформатований текст з Markdown
    return (
        f"**{title}**\n\n"  # Форматування жирної назви
        f"**Дата виходу:** {release_date}\n"  # Дата виходу
        f"**Жанр:** {genre_str}\n\n"  # Жанри
        f"**Опис:**\n{overview}"  # Опис
    )


# Формує повний URL для постера
def get_poster_url(poster_path: str | None) -> str:
    # Повертає повний URL постера або URL-заглушку, якщо poster_path відсутній
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE_URL


# Отримати топ-5 найбільш рейтингових
def get_top_rated(media_type: str) -> list | None:
    if media_type == 'cartoon':  # Якщо шукаємо мультфільми
        # Запит для мультфільмів (discover, фільтр за жанром 16, сортування за рейтингом)
        data = _make_api_request("/discover/movie",
                                 {'sort_by': 'vote_average.desc', 'vote_count.gte': 500, 'with_genres': 16})
    else:
        # Стандартний запит для топ-рейтингових фільмів/серіалів
        data = _make_api_request(f"/{media_type}/top_rated")
    return data.get('results', [])[:5] if data else None  # Повертаємо перші 5 результатів


# Отримати деталі (повну інформацію) про медіа
def get_details(media_type: str, media_id: int) -> dict | None:
    # Запит деталей за типом та ID (наприклад, /movie/12345)
    return _make_api_request(f"/{media_type}/{media_id}")


# Отримати новинки (в кінотеатрах або в ефірі)
def get_new_releases(media_type: str) -> list | None:
    # Визначаємо ендпоінт для фільмів (now_playing) або серіалів (on_the_air)
    endpoint = "/movie/now_playing" if media_type == 'movie' else "/tv/on_the_air"
    data = _make_api_request(endpoint)  # Виконання запиту
    return data.get('results', [])[:5] if data else None  # Повертаємо топ-5


# Отримати випадковий популярний фільм
def get_random_movie() -> dict | None:
    # Обираємо випадкову сторінку (наприклад, з 1 до 50) для більшої рандомізації.
    random_page = random.randint(1, 50)

    # Запит до discover з сортуванням по популярності, високим рейтингом та випадковою сторінкою
    data = _make_api_request("/discover/movie", {
        'sort_by': 'popularity.desc',
        'vote_average.gte': 7.0,  # Фільтруємо фільми з високим рейтингом (>= 7.0)
        'vote_count.gte': 100,  # Фільтруємо з достатньою кількістю голосів
        'page': random_page  # Випадкова сторінка
    })

    if data and 'results' in data and data['results']:  # Якщо є результати
        # Вибираємо випадковий фільм зі списку на обраній сторінці
        movie = random.choice(data['results'])
        # Отримуємо повні деталі, щоб мати повний опис та жанри
        return get_details('movie', movie['id'])

    return None  # Повертаємо None, якщо результатів немає