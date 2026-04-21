import sys


def encrypt_atbash(text):
    ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    
    # Шифруем каждый символ
    encrypted_chars = []
    for char in text:
        char_lower = char.lower()
        if char_lower in ALPHABET:
            idx = ALPHABET.index(char_lower)
            new_char = ALPHABET[len(ALPHABET) - 1 - idx]
            # Сохраняем регистр
            if char.isupper():
                new_char = new_char.upper()
            encrypted_chars.append(new_char)
        else:
            # Сохраняем пробелы и другие символы
            encrypted_chars.append(char)
    
    encrypted_text = ''.join(encrypted_chars)
    
    # Убираем пробелы для группировки по 5 символов
    text_no_spaces = encrypted_text.replace(' ', '').replace('\n', '')
    
    # Разбиваем на группы по 5 символов
    groups = []
    for i in range(0, len(text_no_spaces), 5):
        groups.append(text_no_spaces[i:i+5])
    
    return ' '.join(groups)

def decrypt_atbash(text):
    ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    
    # Убираем пробелы между группами
    text_no_spaces = text.replace(' ', '')
    
    # Дешифруем
    decrypted_chars = []
    for char in text_no_spaces:
        char_lower = char.lower()
        if char_lower in ALPHABET:
            idx = ALPHABET.index(char_lower)
            new_char = ALPHABET[len(ALPHABET) - 1 - idx]
            if char.isupper():
                new_char = new_char.upper()
            decrypted_chars.append(new_char)
        else:
            decrypted_chars.append(char)
    
    return ''.join(decrypted_chars)


def encrypt_polybius(text):
    square = {
        'А': '11', 'Б': '12', 'В': '13', 'Г': '14', 'Д': '15', 'Е': '16',
        'Ж': '21', 'З': '22', 'И': '23', 'Й': '24', 'К': '25', 'Л': '26',
        'М': '31', 'Н': '32', 'О': '33', 'П': '34', 'Р': '35', 'С': '36',
        'Т': '41', 'У': '42', 'Ф': '43', 'Х': '44', 'Ц': '45', 'Ч': '46',
        'Ш': '51', 'Щ': '52', 'Ъ': '53', 'Ы': '54', 'Ь': '55', 'Э': '56',
        'Ю': '61', 'Я': '62'
    }
    
    # Преобразуем текст в цифры
    codes = []
    for char in text.upper():
        if char in square:
            codes.append(square[char])
        else:
            # Пропускаем все остальные символы
            continue
    
    # Объединяем все цифры
    all_digits = ''.join(codes)
    
    # Разбиваем на группы по 5 цифр
    groups = []
    for i in range(0, len(all_digits), 5):
        groups.append(all_digits[i:i+5])
    
    return ' '.join(groups)

def decrypt_polybius(text):
    square = {
        'А': '11', 'Б': '12', 'В': '13', 'Г': '14', 'Д': '15', 'Е': '16',
        'Ж': '21', 'З': '22', 'И': '23', 'Й': '24', 'К': '25', 'Л': '26',
        'М': '31', 'Н': '32', 'О': '33', 'П': '34', 'Р': '35', 'С': '36',
        'Т': '41', 'У': '42', 'Ф': '43', 'Х': '44', 'Ц': '45', 'Ч': '46',
        'Ш': '51', 'Щ': '52', 'Ъ': '53', 'Ы': '54', 'Ь': '55', 'Э': '56',
        'Ю': '61', 'Я': '62'
    }
    
    # Создаем обратный словарь
    reverse = {v: k for k, v in square.items()}
    
    # Убираем пробелы
    text_no_spaces = text.replace(' ', '')
    
    # Разбиваем по 2 цифры и дешифруем
    decrypted_chars = []
    for i in range(0, len(text_no_spaces), 2):
        code = text_no_spaces[i:i+2]
        if code in reverse:
            decrypted_chars.append(reverse[code])
    
    return ''.join(decrypted_chars)


def encrypt_caesar(text, key=3):
    A = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    
    # Шифруем
    encrypted_chars = []
    for char in text:
        if char.upper() in A:
            idx = A.index(char.upper())
            new_idx = (idx + key) % len(A)
            new_char = A[new_idx]
            # Сохраняем регистр
            if char.islower():
                new_char = new_char.lower()
            encrypted_chars.append(new_char)
        else:
            # Пропускаем все остальные символы
            continue
    
    encrypted_text = ''.join(encrypted_chars)
    
    # Разбиваем на группы по 5 символов
    groups = []
    for i in range(0, len(encrypted_text), 5):
        groups.append(encrypted_text[i:i+5])
    
    return ' '.join(groups)

def decrypt_caesar(text, key=3):
    A = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    
    # Убираем пробелы
    text_no_spaces = text.replace(' ', '')
    
    # Дешифруем
    decrypted_chars = []
    for char in text_no_spaces:
        if char.upper() in A:
            idx = A.index(char.upper())
            new_idx = (idx - key) % len(A)
            new_char = A[new_idx]
            if char.islower():
                new_char = new_char.lower()
            decrypted_chars.append(new_char)
        else:
            decrypted_chars.append(char)
    
    return ''.join(decrypted_chars)

# ============================================
# ОСНОВНАЯ ПРОГРАММА
# ============================================

def main():
    print("Введите текст для шифрования:")
    lines = []
    while True:
        try:
            line = input()
            if line == "" and len(lines) > 0:
                # Проверяем, если ввод завершен (две пустые строки подряд)
                if lines[-1] == "":
                    lines.pop()
                    break
            lines.append(line)
        except EOFError:
            break
    
    original_text = "\n".join(lines)
    
    print(f"\nДлина текста: {len(original_text)} символов")
    
    # Получаем ключ для Цезаря
    while True:
        try:
            key_input = input("\nВведите ключ для шифра Цезаря (от 1 до 31, по умолчанию 3): ").strip()
            if key_input == "":
                caesar_key = 3
                break
                
            caesar_key = int(key_input)
            if caesar_key == 0:
                print("Ошибка: ключ не может быть 0. Введите ключ от 1 до 31.")
                continue
            if 1 <= caesar_key <= 31:
                break
            else:
                print("Ключ должен быть от 1 до 31. Попробуйте снова.")
        except ValueError:
            print("Введите целое число!")

    # ============================================
    # АТБАШ
    # ============================================
    print("\n" + "=" * 60)
    print("ШИФР АТБАШ")
    print("=" * 60)
    
    encrypted_atbash = encrypt_atbash(original_text)
    print("\nЗашифровано (группы по 5 символов):")
    print(encrypted_atbash)
    
    decrypted_atbash = decrypt_atbash(encrypted_atbash)
    print("\nРасшифровано (читаемый текст):")
    print(decrypted_atbash)
    
    # ============================================
    # ПОЛИБИЙ
    # ============================================
    print("\n" + "=" * 60)
    print("КВАДРАТ ПОЛИБИЯ")
    print("=" * 60)
    
    encrypted_polybius = encrypt_polybius(original_text)
    print("\nЗашифровано (группы по 5 цифр):")
    print(encrypted_polybius)
    
    decrypted_polybius = decrypt_polybius(encrypted_polybius)
    print("\nРасшифровано (читаемый текст):")
    print(decrypted_polybius)
    
    # ============================================
    # ЦЕЗАРЬ
    # ============================================
    print("\n" + "=" * 60)
    print(f"ШИФР ЦЕЗАРЯ (ключ = {caesar_key})")
    print("=" * 60)
    
    encrypted_caesar = encrypt_caesar(original_text, caesar_key)
    print("\nЗашифровано (группы по 5 символов):")
    print(encrypted_caesar)
    
    decrypted_caesar = decrypt_caesar(encrypted_caesar, caesar_key)
    print("\nРасшифровано (читаемый текст):")
    print(decrypted_caesar)
    
    # ============================================
    # ПРОВЕРКА КОРРЕКТНОСТИ
    # ============================================
    print("\n" + "=" * 60)
    print("ПРОВЕРКА КОРРЕКТНОСТИ РАСШИФРОВКИ")
    print("=" * 60)
    
    # Подготовим тексты для сравнения
    # Для сравнения уберем пробелы, переносы строк и приведем к верхнему регистру
    def prepare_for_comparison(text):
        # Оставляем только русские буквы
        russian_letters = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя"
        result = []
        for char in text:
            if char in russian_letters:
                result.append(char.upper())
        return ''.join(result)
    
    original_clean = prepare_for_comparison(original_text)
    atbash_clean = prepare_for_comparison(decrypted_atbash)
    polybius_clean = prepare_for_comparison(decrypted_polybius)
    caesar_clean = prepare_for_comparison(decrypted_caesar)
    
    print(f"\nСравнение (только русские буквы):")
    print(f"Исходный текст: {len(original_clean)} букв")
    print(f"Атбаш: {len(atbash_clean)} букв - {'СОВПАДАЕТ' if original_clean == atbash_clean else 'НЕ СОВПАДАЕТ'}")
    print(f"Полибий: {len(polybius_clean)} букв - {'СОВПАДАЕТ' if original_clean == polybius_clean else 'НЕ СОВПАДАЕТ'}")
    print(f"Цезарь: {len(caesar_clean)} букв - {'СОВПАДАЕТ' if original_clean == caesar_clean else 'НЕ СОВПАДАЕТ'}")

if __name__ == "__main__":
    main()