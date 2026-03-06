class Human:
    def __init__(self, name, age):
        self.name = name          # Публічний атрибут
        self.__age = age          # Приватний атрибут (інкапсуляція)

    # Getter для доступу до приватного атрибуту
    def get_age(self):
        return self.__age

    # Метод, який буде перевизначено (поліморфізм)
    def introduce(self):
        return f"Я людина. Мене звати {self.name}."

    def breathe(self):
        return f"{self.name} дихає повітрям."


# Наслідування від класу Human
class Student(Human):
    def __init__(self, name, age, course, college_name):
        super().__init__(name, age)   # Виклик конструктора батьківського класу
        self.course = course
        self.college_name = college_name

    # Поліморфізм — перевизначення методу introduce
    def introduce(self):
        return (
            f"Я студент {self.course}-го курсу коледжу {self.college_name}. "
            f"Мене звати {self.name}, мені {self.get_age()} років."
        )

    def study(self):
        return f"{self.name} готується до сесії."


# Точка входу
if __name__ == "__main__":
    # Створюємо об'єкти
    person = Human("Толік", 35)
    student = Student("Влад", 17, 2, "ТФК Луцьк")

    # Демонстрація роботи
    print(person.introduce())  # Базовий метод
    print(student.introduce()) # Перевизначений метод (поліморфізм)
    print(student.breathe())   # Успадкований метод
    print(student.study())     # Власний метод дитини