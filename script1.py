a = [21, 2, 31, 42, 53, 67, 72, 18, 93, 11,
     'яблуко', 'вишня', 'груша', 'апельсин',
     'слива', 'виноград', 'ананас', 'ківі',
     'манго', 'персик']

nums = sorted([el for el in a if isinstance(el, int)])
words = sorted([el for el in a if isinstance(el, str)])

sorted_list = nums + words

even_list = [n for n in nums if n % 2 == 0]

caps_list = [w.upper() for w in words]

print("Перший список:", a)
print("Відсортований список:", sorted_list)
print("Парні числа:", even_list)
print("Капс:", caps_list)
