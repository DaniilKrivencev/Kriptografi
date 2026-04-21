# Шифр Цезаря с выбором ключа
A = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Вводим ключ
K = int(input("Введите ключ (число от 0 до 31): "))

# Вводим текст
t = input("Введите текст: ").upper()

# шифруем
e = "".join(A[(A.index(c) + K) % len(A)] if c in A else c for c in t)

# убираем пробелы для форматирования
e_no_spaces = e.replace(' ', '')

# форматируем по 5 символов 
formatted = []
for i in range(0, len(e_no_spaces), 5):
    formatted.append(e_no_spaces[i:i+5])

encrypted = ' '.join(formatted)
print(f"Зашифровано: {encrypted}")

# для дешифрования убираем пробелы между группами
e_for_decrypt = encrypted.replace(' ', '')

# расшифровываем
d = "".join(A[(A.index(c) - K) % len(A)] if c in A else c for c in e_for_decrypt)
print(f"Расшифровано: {d}")
