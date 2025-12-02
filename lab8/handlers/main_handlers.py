import telebot # Імпорт головної бібліотеки
from telebot import types # Імпорт типів для обробників
import api_client # Імпорт клієнта API
import keyboards.main_kb as keyboards # Імпорт клавіатур
from states.search_states import SearchState # Імпорт класів станів
from telebot.storage import StateMemoryStorage # Імпорт сховища FSM


# Утиліта для надсилання картки з деталями (постер + опис + кнопки)
def send_details_card(bot: telebot.TeleBot, chat_id: int, media_type: str, details: dict):
    # Перевірка наявності деталей
    if not details:
        bot.send_message(chat_id, "Не вдалося завантажити деталі для картки.")
        return

    title = details.get('title') if media_type == 'movie' else details.get('name', 'Фільм') # Визначення назви
    media_id = details.get('id') # Отримання ID

    # Перевірка, що media_id існує
    if not media_id:
        bot.send_message(chat_id, "Помилка: не знайдено ID медіа для створення посилань.")
        return

    # Створення клавіатури "Знайти, де дивитись"
    watch_keyboard = keyboards.create_watch_keyboard(title, media_type, media_id)

    caption = api_client._format_details(details, media_type)  # Форматування опису
    poster_url = api_client.get_poster_url(details.get('poster_path'))  # Отримання URL постера

    # Надсилання фото з підписом та клавіатурою
    bot.send_photo(
        chat_id=chat_id, # ID чату
        photo=poster_url, # URL постера
        caption=caption, # Опис (підпис)
        parse_mode="Markdown", # Режим парсингу тексту
        reply_markup=watch_keyboard # Inline-клавіатура
    )


def register_handlers(bot: telebot.TeleBot, state_storage: StateMemoryStorage):

    # Обробник команди /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: types.Message):
        # Очищаємо стан користувача
        bot.delete_state(message.from_user.id, message.chat.id)
        # Надсилання вітального повідомлення з головним меню
        bot.send_message(
            message.chat.id,
            f"Привіт, {message.from_user.first_name}! 👋\n\n"
            "Я твій особистий помічник у світі кіно.\n"
            "Я допоможу знайти фільми, серіали та мультфільми.\n\n"
            "Оберіть дію з меню:",
            reply_markup=keyboards.main_menu_kb # Reply-клавіатура
        )

    # Обробник кнопки "🏆 Топ-5"
    @bot.message_handler(regexp="^🏆 Топ-5$")
    def show_top_rated_menu(message: types.Message):
        bot.send_message(message.chat.id, "Оберіть категорію:", reply_markup=keyboards.top_rated_menu) # Надсилання Inline-меню

    # Обробник кнопки "🔥 Новинки"
    @bot.message_handler(regexp="^🔥 Новинки$")
    def show_new_releases_menu(message: types.Message):
        bot.send_message(message.chat.id, "Що шукаємо?", reply_markup=keyboards.new_releases_menu) # Надсилання Inline-меню

    # Обробник кнопки "🔍 Пошук за назвою"
    @bot.message_handler(regexp="^🔍 Пошук за назвою$")
    def start_title_search(message: types.Message):
        # Встановлюємо стан очікування назви
        bot.set_state(message.from_user.id, SearchState.waiting_for_title, message.chat.id)
        bot.send_message(message.chat.id, "Введіть назву фільму, серіалу або мультфільму:")

    # Обробник стану SearchState.waiting_for_title (отримання назви)
    @bot.message_handler(state=SearchState.waiting_for_title)
    def process_title_search(message: types.Message):
        # Очищаємо стан
        bot.delete_state(message.from_user.id, message.chat.id)
        query = message.text
        # Надсилання повідомлення "шукаю..."
        sent_message = bot.send_message(message.chat.id, f"🔍 Шукаю за запитом: \"{query}\"...")

        try:
            results = api_client.search_by_title(query)  # Виконання синхронного пошуку

            if results:
                keyboard = keyboards.create_results_keyboard(results, 'search') # Створення клавіатури результатів
                # Редагування повідомлення з результатами
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text="Ось, що я знайшов (топ-5 результатів):",
                    reply_markup=keyboard
                )
            else:
                # Редагування повідомлення про відсутність результатів
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text="На жаль, за вашим запитом нічого не знайдено."
                )
        except Exception: # Обробка помилок
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_message.message_id,
                text="Виникла помилка під час пошуку. Спробуйте пізніше."
            )

    # Обробник кнопки "🎭 Пошук за жанром"
    @bot.message_handler(regexp="^🎭 Пошук за жанром$")
    def start_genre_search(message: types.Message):
        # Встановлюємо стан очікування жанру
        bot.set_state(message.from_user.id, SearchState.waiting_for_genre, message.chat.id)
        genres_list = ", ".join(api_client.GENRE_MAP.keys()) # Отримання списку жанрів

        bot.send_message(
            message.chat.id,
            "Введіть жанр (наприклад: комедія, жахи...)\n\n"
            f"Доступні жанри: {genres_list}"
        )

    # Обробник стану SearchState.waiting_for_genre (отримання жанру)
    @bot.message_handler(state=SearchState.waiting_for_genre)
    def process_genre_search(message: types.Message):
        # Очищаємо стан
        bot.delete_state(message.from_user.id, message.chat.id)
        query = message.text.lower().strip() # Отримання та очищення запиту

        sent_message = bot.send_message(message.chat.id, f"🔍 Шукаю 5 популярних фільмів у жанрі '{query}'...")

        try:
            results = api_client.get_by_genre(query)  # Виконання синхронного пошуку за жанром

            if results:
                keyboard = keyboards.create_results_keyboard(results, 'movie')
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=f"Ось 5 популярних фільмів у жанрі '{query}':",
                    reply_markup=keyboard
                )
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=f"Не можу знайти такий жанр '{query}' або результатів не знайдено."
                )
        except Exception:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_message.message_id,
                text="Виникла помилка під час пошуку. Спробуйте пізніше."
            )

    # Обробник inline-кнопок для списків ("top_" та "new_")
    @bot.callback_query_handler(func=lambda call: call.data.startswith('top_') or call.data.startswith('new_'))
    def process_list_callback(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)  # Зняття стану "завантаження" з кнопки

        # Безпечний розбір callback_data
        try:
            action, media_type = call.data.split('_')
        except ValueError:
            bot.edit_message_text("Помилка обробки запиту.", call.message.chat.id, call.message.message_id)
            return

        # Визначення, які дані завантажувати
        if action == 'top':
            results = api_client.get_top_rated(media_type) # Отримання топ-рейтингу
            if media_type == 'movie':
                title = "Топ-5 фільмів"
            elif media_type == 'tv':
                title = "Топ-5 серіалів"
            else:
                title = "Топ-5 мультфільмів"
        else:  # action == 'new'
            results = api_client.get_new_releases(media_type) # Отримання новинок
            if media_type == 'movie':
                title = "Новинки в кіно"
            else:
                title = "Новинки серіалів в ефірі"

        if results:
            # Визначення типу для клавіатури
            keyboard_media_type = 'movie' if media_type == 'cartoon' else media_type
            keyboard = keyboards.create_results_keyboard(results, keyboard_media_type)

            # Редагування повідомлення
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"**{title}**\n\nОберіть зі списку нижче:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            except Exception:
                # Надсилання нового повідомлення, якщо редагування неможливе
                bot.send_message(
                    call.message.chat.id,
                    f"**{title}**\n\nОберіть зі списку нижче:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        else:
            bot.edit_message_text("😥 Не вдалося завантажити список.", call.message.chat.id, call.message.message_id)

    # Обробник inline-кнопок для деталей (вибір елемента зі списку: "detail_")
    @bot.callback_query_handler(func=lambda call: call.data.startswith('detail_'))
    def process_detail_callback(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)  # Зняття стану "завантаження"

        # Безпечний розбір detail_type_id
        try:
            _, media_type, media_id = call.data.split('_')
            media_id = int(media_id)
        except ValueError:
            bot.send_message(call.message.chat.id, "Помилка обробки запиту.")
            return

        details = api_client.get_details(media_type, media_id)  # Отримання деталей

        if details:
            # Надсилання нової картки з деталями
            send_details_card(bot, call.message.chat.id, media_type, details)
        else:
            bot.send_message(call.message.chat.id, "Не вдалося завантажити деталі.")