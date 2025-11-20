from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import api_client
import keyboards.main_kb as keyboards
from states.search_states import SearchState

router = Router()  # Створення роутера


# Утиліта для надсилання картки з деталями (постер + опис + кнопки)
async def send_details_card(message: Message, media_type: str, details: dict):
    # Додано перевірку на наявність деталей
    if not details:
        await message.answer("Не вдалося завантажити деталі для картки.")
        return

    title = details.get('title') if media_type == 'movie' else details.get('name', 'Фільм')
    media_id = details.get('id')

    # Додано перевірку, що media_id існує
    if not media_id:
        await message.answer("Помилка: не знайдено ID медіа для створення посилань.")
        return

    # Створюємо клавіатуру "Знайти, де дивитись"
    watch_keyboard = keyboards.create_watch_keyboard(title, media_type, media_id)

    caption = api_client._format_details(details, media_type)  # Форматування опису
    poster_url = api_client.get_poster_url(details.get('poster_path'))  # Отримання URL постера

    # Надсилаємо фото з підписом та клавіатурою
    await message.answer_photo(
        photo=poster_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=watch_keyboard
    )


# Обробник команди /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()  # Очищаємо стан користувача
    # Надсилаємо вітальне повідомлення з головним меню
    await message.answer(
        f"Привіт, {message.from_user.first_name}! 👋\n\n"
        "Я твій особистий помічник у світі кіно.\n"
        "Я допоможу знайти фільми, серіали та мультфільми.\n\n"
        "Оберіть дію з меню:",
        reply_markup=keyboards.main_menu_kb
    )


# Обробник кнопки "🏆 Топ-5"
@router.message(F.text == "🏆 Топ-5")
async def show_top_rated_menu(message: Message):
    await message.answer("Оберіть категорію:", reply_markup=keyboards.top_rated_menu)


# Обробник кнопки "🔥 Новинки"
@router.message(F.text == "🔥 Новинки")
async def show_new_releases_menu(message: Message):
    await message.answer("Що шукаємо?", reply_markup=keyboards.new_releases_menu)


# Обробник кнопки "🔍 Пошук за назвою"
@router.message(F.text == "🔍 Пошук за назвою")
async def start_title_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_title)  # Встановлюємо стан очікування назви
    await message.answer("Введіть назву фільму, серіалу або мультфільму:")


# Обробник стану SearchState.waiting_for_title (отримання назви)
@router.message(SearchState.waiting_for_title)
async def process_title_search(message: Message, state: FSMContext):
    await state.clear()  # Очищаємо стан
    query = message.text
    # Надсилаємо "шукаю..." для кращого UX
    sent_message = await message.answer(f"🔍 Шукаю за запитом: \"{query}\"...")

    try:
        results = await api_client.search_by_title(query)  # Виконуємо пошук

        if results:
            keyboard = keyboards.create_results_keyboard(results, 'search')
            # Редагуємо повідомлення з результатами
            await sent_message.edit_text("Ось, що я знайшов (топ-5 результатів):", reply_markup=keyboard)
        else:
            await sent_message.edit_text("На жаль, за вашим запитом нічого не знайдено.")
    except Exception:
        await sent_message.edit_text("Виникла помилка під час пошуку. Спробуйте пізніше.")


# Обробник кнопки "🎭 Пошук за жанром"
@router.message(F.text == "🎭 Пошук за жанром")
async def start_genre_search(message: Message, state: FSMContext):
    await state.set_state(SearchState.waiting_for_genre)  # Встановлюємо стан очікування жанру
    genres_list = ", ".join(api_client.GENRE_MAP.keys())

    await message.answer(
        "Введіть жанр (наприклад: комедія, жахи...)\n\n"
        f"Доступні жанри: {genres_list}"
    )


# Обробник стану SearchState.waiting_for_genre (отримання жанру)
@router.message(SearchState.waiting_for_genre)
async def process_genre_search(message: Message, state: FSMContext):
    await state.clear()  # Очищаємо стан
    query = message.text.lower().strip()

    sent_message = await message.answer(f"🔍 Шукаю 5 популярних фільмів у жанрі '{query}'...")

    try:
        results = await api_client.get_by_genre(query)  # Виконуємо пошук за жанром

        if results:
            keyboard = keyboards.create_results_keyboard(results, 'movie')
            await sent_message.edit_text(f"Ось 5 популярних фільмів у жанрі '{query}':", reply_markup=keyboard)
        else:
            await sent_message.edit_text(f"Не можу знайти такий жанр '{query}' або результатів не знайдено.")
    except Exception:
        await sent_message.edit_text("Виникла помилка під час пошуку. Спробуйте пізніше.")


# Обробник inline-кнопок для списків ("top_" та "new_")
@router.callback_query(F.data.startswith('top_') | F.data.startswith('new_'))
async def process_list_callback(callback: CallbackQuery):
    await callback.answer()  # Прибираємо "годинник" з кнопки

    # Безпечний розбір callback_data
    try:
        action, media_type = callback.data.split('_')
    except ValueError:
        await callback.message.edit_text("Помилка обробки запиту.")
        return

    # Визначаємо, які дані завантажувати (топ чи новинки)
    if action == 'top':
        results = await api_client.get_top_rated(media_type)
        if media_type == 'movie':
            title = "Топ-5 фільмів"
        elif media_type == 'tv':
            title = "Топ-5 серіалів"
        else:
            title = "Топ-5 мультфільмів"
    else:  # action == 'new'
        results = await api_client.get_new_releases(media_type)
        if media_type == 'movie':
            title = "Новинки в кіно"
        else:
            title = "Новинки серіалів в ефірі"

    if results:
        # Визначаємо тип для клавіатури
        keyboard_media_type = 'movie' if media_type == 'cartoon' else media_type
        keyboard = keyboards.create_results_keyboard(results, keyboard_media_type)

        # Редагуємо повідомлення
        try:
            await callback.message.edit_text(f"**{title}**\n\nОберіть зі списку нижче:", reply_markup=keyboard,
                                             parse_mode="Markdown")
        except Exception:  # Обробка помилки, якщо повідомлення не можна редагувати
            await callback.message.answer(f"**{title}**\n\nОберіть зі списку нижче:", reply_markup=keyboard,
                                          parse_mode="Markdown")
    else:
        await callback.message.edit_text("😥 Не вдалося завантажити список.")


# Обробник inline-кнопок для деталей (вибір елемента зі списку: "detail_")
@router.callback_query(F.data.startswith('detail_'))
async def process_detail_callback(callback: CallbackQuery):
    await callback.answer()  # Прибираємо "годинник"

    # Безпечний розбір detail_type_id
    try:
        _, media_type, media_id = callback.data.split('_')
        media_id = int(media_id)
    except ValueError:
        await callback.message.answer("Помилка обробки запиту.")
        return

    details = await api_client.get_details(media_type, media_id)  # Отримуємо деталі

    if details:
        # Надсилаємо нову картку з деталями
        await send_details_card(callback.message, media_type, details)
    else:
        await callback.message.answer("Не вдалося завантажити деталі.")