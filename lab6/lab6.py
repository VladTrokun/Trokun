# Імпортуємо наш декоратор з іншого файлу
from decorators import require_nonempty

@require_nonempty
def print_info(name, city=""): # Додали city як ключовий аргумент
    print(f"Ім'я: {name}, Місто: {city}")


# Успішний виклик
print("Успішний виклик")
try:
    print_info("Влад", city="Луцьк")
except ValueError as e:
    print(f"Помилка: {e}")


# Невдалий виклик (порожнє ім'я)
print("\nНевдалий виклик (порожнє ім'я)")
try:
    print_info("", city="Київ") # name="" це порожній аргумент
except ValueError as e:
    print(f"Спіймали помилку: {e}")


# Невдалий виклик (порожнє місто)
print("\nНевдалий виклик (порожнє місто)")
try:
    print_info("Анна", city="") # city="" це порожній аргумент
except ValueError as e:
    print(f"Спіймали помилку: {e}")