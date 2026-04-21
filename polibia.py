# Квадрат Полибия
square = {
    'А': '11', 'Б': '12', 'В': '13', 'Г': '14', 'Д': '15', 'Е': '16',
    'Ж': '21', 'З': '22', 'И': '23', 'Й': '24', 'К': '25', 'Л': '26',
    'М': '31', 'Н': '32', 'О': '33', 'П': '34', 'Р': '35', 'С': '36',
    'Т': '41', 'У': '42', 'Ф': '43', 'Х': '44', 'Ц': '45', 'Ч': '46',
    'Ш': '51', 'Щ': '52', 'Ъ': '53', 'Ы': '54', 'Ь': '55', 'Э': '56',
    'Ю': '61', 'Я': '62'
}

text = input("Введите текст: ").upper()

# шифруем - получаем все коды подряд
codes_string = ''.join(square[char] if char in square else '' for char in text)

# разбиваем на группы по 5 цифр (5 символов)
formatted_codes = []
for i in range(0, len(codes_string), 5):
    formatted_codes.append(codes_string[i:i+5])

# соединяем группы пробелами
encrypted = ' '.join(formatted_codes)
print(f"Зашифровано: {encrypted}")

# расшифровываем
reverse = {v: k for k, v in square.items()}

# убираем пробелы и разбиваем по 2 цифры
codes_for_decryption = encrypted.replace(' ', '')
codes_list = [codes_for_decryption[i:i+2] for i in range(0, len(codes_for_decryption), 2)]

decrypted = ''.join(reverse[code] for code in codes_list)
print(f"Расшифровано: {decrypted}")