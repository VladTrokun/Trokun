from aiogram.fsm.state import StatesGroup, State

# Клас для керування станами користувача (FSM)
class SearchState(StatesGroup):
    # Стан очікування введення назви
    waiting_for_title = State()
    # Стан очікування введення жанру
    waiting_for_genre = State()