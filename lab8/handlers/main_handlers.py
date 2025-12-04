import telebot  # Імпорт головної бібліотеки telebot
from telebot import types  # Імпорт типів для обробників (Message, CallbackQuery)
from lab8 import api_client  # Імпорт модуля api_client для роботи з TMDB
import keyboards.main_kb as keyboards  # Імпорт клавіатур
import logging  # Додаємо імпорт для логування

# Налаштування логування для кращого виводу
logging.basicConfig(level=logging.INFO)


# Утиліта для надсилання картки з деталями (постер + опис + кнопки)
def send_details_card(bot: telebot.TeleBot, chat_id: int, media_type: str, details: dict):
    # Перевірка наявності деталей
    if not details:
        bot.send_message(chat_id, "Не вдалося завантажити деталі для картки.") # Повідомлення про помилку
        return

    # Визначення назви (залежно від типу медіа)
    title = details.get('title') if media_type == 'movie' else details.get('name', 'Фільм')
    media_id = details.get('id')  # Отримання ID медіа

    # Перевірка, що media_id існує
    if not media_id:
        bot.send_message(chat_id, "Помилка: не знайдено ID медіа для створення посилань.") # Повідомлення про помилку ID
        return

    # Створення клавіатури "Знайти, де дивитись"
    watch_keyboard = keyboards.create_watch_keyboard(title, media_type, media_id)

    caption = api_client._format_details(details, media_type)  # Форматування опису для підпису
    poster_url = api_client.get_poster_url(details.get('poster_path'))  # Отримання URL постера

    # Надсилання фото з підписом та клавіатурою
    bot.send_photo(
        chat_id=chat_id,  # ID чату
        photo=poster_url,  # URL постера
        caption=caption,  # Опис (підпис)
        parse_mode="Markdown",  # Режим парсингу тексту для форматування (жирний текст, тощо)
        reply_markup=watch_keyboard  # Inline-клавіатура
    )


# Реєстрація всіх обробників
def register_handlers(bot: telebot.TeleBot):
    # Обробник команди /start
    @bot.message_handler(commands=['start'])
    def cmd_start(message: types.Message):
        # Надсилання вітального повідомлення з головним меню
        bot.send_message(
            message.chat.id,
            f"Привіт, {message.from_user.first_name}! 👋\n\n"
            "Я твій особистий помічник у світі кіно.\n"
            "Я допоможу знайти фільми, серіали та мультфільми.\n\n"
            "Оберіть дію з меню:",
            reply_markup=keyboards.main_menu_kb  # Reply-клавіатура
        )

    # Обробник кнопки "🏆 Топ-5" (використовує regexp для точної відповідності)
    @bot.message_handler(regexp="^🏆 Топ-5$")
    def show_top_rated_menu(message: types.Message):
        # Надсилання Inline-меню з опціями "Фільми", "Серіали", "Мультфільми"
        bot.send_message(message.chat.id, "Оберіть категорію:", reply_markup=keyboards.top_rated_menu)

    # Обробник кнопки "🔥 Новинки"
    @bot.message_handler(regexp="^🔥 Новинки$")
    def show_new_releases_menu(message: types.Message):
        # Надсилання Inline-меню з опціями "Нові фільми", "Нові серіали"
        bot.send_message(message.chat.id, "Що шукаємо?", reply_markup=keyboards.new_releases_menu)

    # Обробник кнопки "🎲 Випадковий фільм"
    @bot.message_handler(regexp="^🎲 Випадковий фільм$")
    def get_random_movie_handler(message: types.Message):
        sent_message = bot.send_message(message.chat.id, "Шукаю випадковий популярний фільм... 🍿") # Повідомлення-заглушка

        try:
            random_movie_details = api_client.get_random_movie() # Виклик функції для отримання випадкового фільму

            # Видаляємо повідомлення-заглушку перед відправленням картки
            bot.delete_message(message.chat.id, sent_message.message_id)

            if random_movie_details:
                # Надсилання картки з деталями для випадкового фільму
                send_details_card(bot, message.chat.id, 'movie', random_movie_details)
            else:
                bot.send_message(message.chat.id, "На жаль, не вдалося знайти випадковий фільм.")

        except Exception as e:
            logging.error(f"Помилка отримання випадкового фільму: {e}") # Логування помилки
            bot.send_message(message.chat.id, "Виникла помилка під час пошуку випадкового фільму. Спробуйте пізніше.")


    # Обробник inline-кнопок для списків ("top_" та "new_")
    @bot.callback_query_handler(func=lambda call: call.data.startswith('top_') or call.data.startswith('new_'))
    def process_list_callback(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)  # Зняття стану "завантаження" з кнопки

        try:
            action, media_type = call.data.split('_')  # Розбір "top_movie" або "new_tv"
        except ValueError:
            bot.edit_message_text("Помилка обробки запиту.", call.message.chat.id, call.message.message_id)
            return

        results = None  # Ініціалізація змінної для результатів
        title = ""  # Ініціалізація змінної для заголовка

        # Визначення, які дані завантажувати
        try:
            if action == 'top':
                results = api_client.get_top_rated(media_type)  # Отримання топ-рейтингу
                if media_type == 'movie':
                    title = "Топ-5 фільмів"
                elif media_type == 'tv':
                    title = "Топ-5 серіалів"
                else:  # 'cartoon'
                    title = "Топ-5 мультфільмів"
            else:  # action == 'new'
                results = api_client.get_new_releases(media_type)  # Отримання новинок
                if media_type == 'movie':
                    title = "Новинки в кіно"
                else:
                    title = "Новинки серіалів в ефірі"

            if results:
                # Визначення типу для клавіатури
                keyboard_media_type = 'movie' if media_type == 'cartoon' else media_type
                keyboard = keyboards.create_results_keyboard(results, keyboard_media_type) # Створення клавіатури результатів

                # Редагування повідомлення
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"**{title}**\n\nОберіть зі списку нижче:",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text("😥 Не вдалося завантажити список.", call.message.chat.id, call.message.message_id)

        except Exception as e:
            logging.error(f"Помилка завантаження списку ({action}_{media_type}): {e}") # Логування помилки
            bot.edit_message_text("Виникла помилка під час завантаження даних.", call.message.chat.id,
                                  call.message.message_id)

    # Обробник inline-кнопок для деталей (вибір елемента зі списку: "detail_")
    @bot.callback_query_handler(func=lambda call: call.data.startswith('detail_'))
    def process_detail_callback(call: types.CallbackQuery):
        bot.answer_callback_query(call.id)  # Зняття стану "завантаження"

        try:
            _, media_type, media_id = call.data.split('_')  # Розбір detail_type_id
            media_id = int(media_id)
        except ValueError:
            bot.send_message(call.message.chat.id, "Помилка обробки запиту.")
            return

        try:
            details = api_client.get_details(media_type, media_id)  # Отримання деталей

            if details:
                # Надсилання нової картки з деталями
                send_details_card(bot, call.message.chat.id, media_type, details)
            else:
                bot.send_message(call.message.chat.id, "Не вдалося завантажити деталі.")
        except Exception as e:
            logging.error(f"Помилка завантаження деталей ({media_type}_{media_id}): {e}") # Логування помилки
            bot.send_message(call.message.chat.id, "Виникла помилка під час завантаження деталей.")