import requests                 # Для запитів в інтернет
import numpy as np              # Для роботи з масивами (математика)
import pandas as pd             # Для роботи з таблицями даних
import matplotlib.pyplot as plt # Для створення графіків
from PIL import Image           # Для роботи з зображеннями
from bs4 import BeautifulSoup   # Для парсингу (читання) HTML-сторінок
import pyjokes                  # Для генерації жартів
from termcolor import colored   # Для кольорового тексту в терміналі
from faker import Faker         # Для створення фейкових (несправжніх) даних
import arrow                    # Для зручної роботи з датою та часом

#Блок 1: requests
try:
    print("1. Тестуємо 'requests'")
    # Робимо запит на сайт
    response = requests.get('https://api.github.com')
    # Перевіряємо, чи запит успішний (статус 200)
    response.raise_for_status()
    # Якщо все добре, друкуємо статус
    print(f"requests: Успішно, статус: {response.status_code}")
# Ловимо помилки, пов'язані з запитом (наприклад, немає інтернету)
except requests.exceptions.RequestException as e:
    print(f"requests: Помилка: {e}")

#Блок 2: pyjokes
try:
    print("\n2. Тестуємо 'pyjokes'")
    # Отримуємо та одразу друкуємо жарт
    print(f"pyjokes: {pyjokes.get_joke(language='en', category='neutral')}")
# 'Exception as e' ловить будь-яку можливу помилку
except Exception as e:
    print(f"pyjokes: Помилка: {e}")

#Блок 3: termcolor
try:
    print("\n3. Тестуємо 'termcolor'")
    # "Фарбуємо" текст у зелений колір
    print(colored("termcolor: Цей текст зелений.", 'green'))
except Exception as e:
    print(f"termcolor: Помилка: {e}")

#Блок 4: numpy
try:
    print("\n4. Тестуємо 'numpy'")
    # Створюємо numpy-масив і множимо кожен елемент на 3
    result = np.array([1, 5, 10]) * 3
    # Друкуємо результат (має бути [3 15 30])
    print(f"numpy: Результат [1, 5, 10] * 3 = {result}")
except Exception as e:
    print(f"numpy: Помилка: {e}")

#Блок 5: faker
try:
    print("\n5. Тестуємо 'faker'")
    # Створюємо генератор даних ('uk_UA' - для української мови)
    fake = Faker('uk_UA')
    # Генеруємо та друкуємо фейкові ім'я та адресу
    print(f"faker: {fake.name()}, {fake.address()}")
except Exception as e:
    print(f"faker: Помилка: {e}")