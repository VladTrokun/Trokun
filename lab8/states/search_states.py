from telebot.handler_backends import StatesGroup, State # Імпорт класів станів для telebot

# Клас для керування станами користувача (FSM)
class SearchState(StatesGroup):
    # Стан очікування введення назви
    waiting_for_title = State()
    # Стан очікування введення жанру
    waiting_for_genre = State()