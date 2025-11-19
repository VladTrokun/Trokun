import httpx
import random
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL, PLACEHOLDER_IMAGE_URL

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


async def _make_api_request(endpoint: str, params: dict = None) -> dict | None:
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY
    params['language'] = 'uk-UA'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TMDB_BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Помилка API запиту: {e}")
            return None


# НОВА ФУНКЦІЯ для надійного пошуку ID ключового слова
async def _find_keyword_id_in_english(query: str) -> int | None:
    """Шукає ID ключового слова в англійській базі (вона найнадійніша)."""
    params = {
        'api_key': TMDB_API_KEY,
        'query': query
        # 'language' НЕ вказано, щоб шукати у default (англійській) базі
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TMDB_BASE_URL}/search/keyword", params=params)
            response.raise_for_status()
            data = response.json()
            if data and data.get('results'):
                return data['results'][0]['id']  # Повертає ID
        except httpx.RequestError as e:
            print(f"Помилка пошуку ключового слова: {e}")
    return None


def _format_details(item: dict, media_type: str) -> str:
    if media_type == 'movie':
        title = item.get('title', 'Назва невідома')
        release_date = item.get('release_date', 'Дата невідома')
    else:
        title = item.get('name', 'Назва невідома')
        release_date = item.get('first_air_date', 'Дата невідома')

    overview = item.get('overview', 'Опис відсутній.')
    genres = [g['name'] for g in item.get('genres', [])]
    genre_str = ", ".join(genres) if genres else "Жанр невідомий"

    return (
        f"**{title}**\n\n"
        f"**Дата виходу:** {release_date}\n"
        f"**Жанр:** {genre_str}\n\n"
        f"**Опис:**\n{overview}"
    )


def get_poster_url(poster_path: str | None) -> str:
    return f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE_URL


async def get_top_rated(media_type: str) -> list | None:
    if media_type == 'cartoon':
        data = await _make_api_request("/discover/movie",
                                       {'sort_by': 'vote_average.desc', 'vote_count.gte': 500, 'with_genres': 16})
    else:
        data = await _make_api_request(f"/{media_type}/top_rated")
    return data.get('results', [])[:5] if data else None


async def search_by_title(query: str) -> list | None:
    data = await _make_api_request("/search/multi", {'query': query, 'include_adult': False})
    if data and 'results' in data:
        return [item for item in data['results'] if item.get('media_type') in ['movie', 'tv']][:5]
    return None


async def get_details(media_type: str, media_id: int) -> dict | None:
    return await _make_api_request(f"/{media_type}/{media_id}")


async def get_by_genre(genre_query: str) -> list | None:
    genre_id = GENRE_MAP.get(genre_query.lower().strip())
    if not genre_id:
        return None
    data = await _make_api_request("/discover/movie", {'sort_by': 'popularity.desc', 'with_genres': genre_id})
    return data.get('results', [])[:5] if data else None


async def get_new_releases(media_type: str) -> list | None:
    endpoint = "/movie/now_playing" if media_type == 'movie' else "/tv/on_the_air"
    data = await _make_api_request(endpoint)
    return data.get('results', [])[:5] if data else None


async def get_random() -> dict | None:
    random_page = random.randint(1, 500)
    data = await _make_api_request("/discover/movie", {'sort_by': 'popularity.desc', 'page': random_page})
    if data and data.get('results'):
        random_item = random.choice(data['results'])
        return await get_details('movie', random_item['id'])
    return None

async def get_by_keyword(keyword_query: str) -> list | None:

    keyword_id = await _find_keyword_id_in_english(keyword_query)

    if not keyword_id:
        return None

    data = await _make_api_request("/discover/movie", {'sort_by': 'popularity.desc', 'with_keywords': keyword_id})
    return data.get('results', [])[:5] if data else None