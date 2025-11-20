import httpx
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL, PLACEHOLDER_IMAGE_URL

# Мапа українських жанрів до ID TMDB
GENRE_MAP = {
    'жахи': 27,
    'комедія': 35,
    'бойовик': 28,
    'фантастика': 878,
    'драма': 18,
    'трилер': 53,
    'мультфільм': 16,
    'пригоди': 12,
    'фентезі': 14,
    'детектив': 9648,
    'сімейний': 10751,
}


# Приватна функція для виконання асинхронних API-запитів
async def _make_api_request(endpoint: str, params: dict = None) -> dict | None:
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY # Додаємо ключ API
    params['language'] = 'uk-UA'    # Встановлюємо українську мову

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TMDB_BASE_URL}{endpoint}", params=params)
            response.raise_for_status() # Викликає помилку, якщо статус 4xx/5xx
            return response.json()
        except httpx.RequestError as e:
            print(f"Помилка API запиту: {e}")
            return None


# Приватна функція для форматування деталей у рядок (caption для фото)
def _format_details(item: dict, media_type: str) -> str:
    # Визначаємо назву та дату залежно від типу медіа
    if media_type == 'movie':
        title = item.get('title', 'Назва невідома')
        release_date = item.get('release_date', 'Дата невідома')
    else: # 'tv'
        title = item.get('name', 'Назва невідома')
        release_date = item.get('first_air_date', 'Дата невідома')

    overview = item.get('overview', 'Опис відсутній.')
    genres = [g['name'] for g in item.get('genres', [])]
    genre_str = ", ".join(genres) if genres else "Жанр невідомий"

    # Повертаємо відформатований текст з Markdown
    return (
        f"**{title}**\n\n"
        f"**Дата виходу:** {release_date}\n"
        f"**Жанр:** {genre_str}\n\n"
        f"**Опис:**\n{overview}"
    )


# Формує повний URL для постера
def get_poster_url(poster_path: str | None) -> str:
    # Повертає URL постера або заглушку
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE_URL


# Отримати топ-5 найбільш рейтингових
async def get_top_rated(media_type: str) -> list | None:
    if media_type == 'cartoon':
        # Спеціальний запит для мультфільмів (фільтр за жанром 16)
        data = await _make_api_request("/discover/movie",
                                       {'sort_by': 'vote_average.desc', 'vote_count.gte': 500, 'with_genres': 16})
    else:
        # Стандартний запит для фільмів/серіалів
        data = await _make_api_request(f"/{media_type}/top_rated")
    return data.get('results', [])[:5] if data else None # Повертаємо перші 5


# Пошук за назвою (фільми та серіали)
async def search_by_title(query: str) -> list | None:
    data = await _make_api_request("/search/multi", {'query': query, 'include_adult': False})
    if data and 'results' in data:
        # Фільтруємо лише фільми та серіали, повертаємо топ-5
        return [item for item in data['results'] if item.get('media_type') in ['movie', 'tv']][:5]
    return None


# Отримати деталі (повну інформацію) про медіа
async def get_details(media_type: str, media_id: int) -> dict | None:
    return await _make_api_request(f"/{media_type}/{media_id}")


# Отримати список фільмів за жанром
async def get_by_genre(genre_query: str) -> list | None:
    genre_id = GENRE_MAP.get(genre_query.lower().strip()) # Отримуємо ID жанру
    if not genre_id:
        return None
    # Запит до discover з фільтром по жанру
    data = await _make_api_request("/discover/movie", {'sort_by': 'popularity.desc', 'with_genres': genre_id})
    return data.get('results', [])[:5] if data else None # Повертаємо топ-5


# Отримати новинки (в кінотеатрах або в ефірі)
async def get_new_releases(media_type: str) -> list | None:
    # Визначаємо ендпоінт для фільмів або серіалів
    endpoint = "/movie/now_playing" if media_type == 'movie' else "/tv/on_the_air"
    data = await _make_api_request(endpoint)
    return data.get('results', [])[:5] if data else None