from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import api_client
import keyboards.main_kb as keyboards
from states.search_states import SearchState

router = Router()


async def send_details_card(message: Message, media_type: str, details: dict):
    title = details.get('title') if media_type == 'movie' else details.get('name', 'Фільм')
    media_id = details.get('id')
    watch_keyboard = keyboards.create_watch_keyboard(title, media_type, media_id)

    caption = api_client._format_details(details, media_type)
    poster_url = api_client.get_poster_url(details.get('poster_path'))

    await message.answer_photo(
        photo=poster_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=watch_keyboard
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Я твій особистий помічник у світі кіно.\n"
        "Я допоможу знайти фільми, серіали та мультфільми.\n\n"
        "Оберіть дію з меню:",
        reply_markup=keyboards.main_menu_kb
    )


@router.message(F.text == "🏆 Топ-5")
async def show_top_rated_menu(message: Message):
    await message.answer("Оберіть категорію:", reply_markup=keyboards.top_rated_menu)


@router.message(F.text == "🔥 Новинки")
async def show_new_releases_menu(message: Message):
    await message.answer("Що шукаємо?", reply_markup=keyboards.new_releases_menu)


@router.message(F.text == "🎲 Випадкова порада")
async def show_random(message: Message):
    await message.answer("🔮 Шукаю щось цікавеньке для вас...")
    random_item = await api_client.get_random()
    if random_item:
        await send_details_card(message, 'movie', random_item)
    else:
        await message.answer("😥 На жаль, не вдалося нічого знайти.")


@router.message(F.text == "🔍 Пошук за назвою")
async def start_title_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_title)
    await message.answer("Введіть назву фільму, серіалу або мультфільму:")


@router.message(SearchState.waiting_for_title)
async def process_title_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text
    await message.answer(f"🔍 Шукаю за запитом: \"{query}\"...")

    results = await api_client.search_by_title(query)

    if results:
        keyboard = keyboards.create_results_keyboard(results, 'search')
        await message.answer("Ось, що я знайшов (топ-5 результатів):", reply_markup=keyboard)
    else:
        await message.answer("На жаль, за вашим запитом нічого не знайдено.")


@router.message(F.text == "🎭 Пошук за жанром")
async def start_genre_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_genre)
    genres_list = ", ".join(api_client.GENRE_MAP.keys())

    await message.answer(
        "Введіть жанр (наприклад: комедія, жахи...)\n\n"
        f"Доступні жанри: {genres_list}"
    )


@router.message(SearchState.waiting_for_genre)
async def process_genre_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.lower().strip()

    results = await api_client.get_by_genre(query)

    if results:
        keyboard = keyboards.create_results_keyboard(results, 'movie')
        await message.answer(f"Ось 5 популярних фільмів у жанрі '{query}':", reply_markup=keyboard)
    else:
        await message.answer(f"Не можу знайти такий жанр '{query}'. Спробуйте ще раз.")


@router.message(F.text == "💬 Пошук за побажаннями")
async def start_keyword_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_keyword)
    await message.answer(
        "Опишіть ключове слово (наприклад: 'army', 'space', 'vampire').\n\n"
        "**Увага:** База даних TMDB найкраще розуміє **англійські** ключові слова."
    )


@router.message(SearchState.waiting_for_keyword)
async def process_keyword_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.lower().strip()

    results = await api_client.get_by_keyword(query)

    if results:
        keyboard = keyboards.create_results_keyboard(results, 'movie')
        await message.answer(f"Ось 5 фільмів за ключовим словом '{query}':", reply_markup=keyboard)
    else:
        await message.answer(
            f"На жаль, нічого не знайдено за ключовим словом '{query}'.\n\n"
            "Спробуйте інше слово (бажано англійською)."
        )


@router.callback_query(F.data.startswith('top_') | F.data.startswith('new_'))
async def process_list_callback(callback: CallbackQuery):
    await callback.answer()

    action, media_type = callback.data.split('_')

    if action == 'top':
        results = await api_client.get_top_rated(media_type)
        if media_type == 'movie':
            title = "Топ-5 фільмів"
        elif media_type == 'tv':
            title = "Топ-5 серіалів"
        else:
            title = "Топ-5 мультфільмів"
    else:
        results = await api_client.get_new_releases(media_type)
        if media_type == 'movie':
            title = "Новинки в кіно"
        else:
            title = "Новинки серіалів в ефірі"

    if results:
        list_media_type = 'movie' if media_type == 'cartoon' else media_type
        keyboard = keyboards.create_results_keyboard(results, list_media_type)
        await callback.message.edit_text(f"**{title}**\n\nОберіть зі списку нижче:", reply_markup=keyboard,
                                         parse_mode="Markdown")
    else:
        await callback.message.edit_text("😥 Не вдалося завантажити список.")


@router.callback_query(F.data.startswith('detail_'))
async def process_detail_callback(callback: CallbackQuery):
    await callback.answer()

    try:
        _, media_type, media_id = callback.data.split('_')
        media_id = int(media_id)
    except ValueError:
        await callback.message.answer("Помилка обробки запиту.")
        return

    details = await api_client.get_details(media_type, media_id)

    if details:
        await send_details_card(callback.message, media_type, details)
    else:
        await callback.message.answer("Не вдалося завантажити деталі.")