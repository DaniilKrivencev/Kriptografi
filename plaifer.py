#Удаляет служебные символы из расшифрованного текста
def clean_decrypted_text(text):
    result = ""
    i = 0
    while i < len(text):
        if i < len(text) - 1:
            # Проверяем, не является ли текущий символ служебной вставкой
            # Если после символа идет 'ф' или 'я', которые были вставлены для разделения одинаковых букв
            if text[i + 1] in ['ф', 'я'] and i + 2 < len(text) and text[i] == text[i + 2]:
                # Пропускаем служебный символ
                result += text[i]
                i += 2
            else:
                result += text[i]
                i += 1
        else:
            result += text[i]
            i += 1

    # Удаляем последний символ, если это служебная вставка для четности
    if len(result) > 0:
        # Если заканчивается на 'я', удаляем только если перед ней 'ф' (ситуация 'фя')
        if result[-1] == 'я':
            if len(result) > 1 and result[-2] == 'ф':
                result = result[:-1]
        # Если заканчивается на 'ф', считаем это паддингом 
        elif result[-1] == 'ф':
            # Оставляем стандартное удаление паддинга 'ф'
            result = result[:-1]

    return result


def playfer(text, is_text_mode, is_encrypt, shift):
    alphabet_change = {
        'а': 'а', 'б': 'б', 'в': 'в', 'г': 'г', 'д': 'д',
        'е': 'е', 'ё': 'е', 'ж': 'ж', 'з': 'з', 'и': 'и',
        'й': 'и', 'к': 'к', 'л': 'л', 'м': 'м', 'н': 'н',
        'о': 'о', 'п': 'п', 'р': 'р', 'с': 'с', 'т': 'т',
        'у': 'у', 'ф': 'ф', 'х': 'х', 'ц': 'ц', 'ч': 'ч',
        'ш': 'ш', 'щ': 'щ', 'ъ': 'ь', 'ы': 'ы', 'ь': 'ь',
        'э': 'э', 'ю': 'ю', 'я': 'я'
    }

    shift = replace_letters(shift.lower(), alphabet_change)
    print(f"Введенный ключ: {shift}")

    # Проверка на повторяющиеся буквы в ключе
    if not has_unique_letters(shift):
        print("ОШИБКА: Ключ содержит повторяющиеся буквы!")
        return None

    shift = remove_duplicate_letters(shift)

    processed_text = ""
    alphabet = "абвгдежзиклмнопрстуфхцчшщьыэюя"

    if is_text_mode:
        pass
    else:
        import re
        processed_text = re.sub(r'\s', '', text).lower()
        processed_text = replace_letters(processed_text, alphabet_change)
        print(f"Введенный текст: {processed_text}")

        result = ""
        main_string = ""

        # Удаляем из алфавита буквы, которые есть в ключе
        main_string = remove_letters_from_string(shift, alphabet)
        main_string = shift + main_string

        # Создаем матрицу 5x6
        losung_arr = []
        index = 0
        for i in range(5):
            row = []
            for j in range(6):
                if index < len(main_string):
                    row.append(main_string[index])
                else:
                    row.append('')
                index += 1
            losung_arr.append(row)

        print("Таблица 5x6:")
        for row in losung_arr:
            print(' '.join(row))

        if is_encrypt:
            processed_text = prepare_text(processed_text)

            count = 0
            while count < len(processed_text) - 1:
                char1 = processed_text[count]
                char2 = processed_text[count + 1]

                a1 = find_element_index(losung_arr, char1)
                a2 = find_element_index(losung_arr, char2)

                if a1 is None or a2 is None:
                    missing = char1 if a1 is None else char2
                    print(f"Ошибка: символ '{missing}' не найден в матрице!")
                    # Пропускаем эту пару
                    count += 2
                    continue

                if a1['row'] == a2['row']:
                    result += (losung_arr[a1['row']][(a1['col'] + 1) % 6] +
                               losung_arr[a2['row']][(a2['col'] + 1) % 6])
                elif a1['col'] == a2['col']:
                    result += (losung_arr[(a1['row'] + 1) % 5][a1['col']] +
                               losung_arr[(a2['row'] + 1) % 5][a2['col']])
                else:
                    result += (losung_arr[a1['row']][a2['col']] +
                               losung_arr[a2['row']][a1['col']])




                count += 2
        else:
            # Расшифровка
            count = 0
            while count < len(processed_text) - 1:
                char1 = processed_text[count]
                char2 = processed_text[count + 1]

                a1 = find_element_index(losung_arr, char1)
                a2 = find_element_index(losung_arr, char2)

                if a1 is None or a2 is None:
                    missing = char1 if a1 is None else char2
                    print(f"Ошибка: символ '{missing}' не найден в матрице!")
                    count += 2
                    continue

                if a1['row'] == a2['row']:
                    # Сдвиг влево по строке
                    new_col1 = (a1['col'] - 1) % 6
                    new_col2 = (a2['col'] - 1) % 6
                    result += losung_arr[a1['row']][new_col1] + losung_arr[a2['row']][new_col2]
                elif a1['col'] == a2['col']:
                    # Сдвиг вверх по столбцу
                    new_row1 = (a1['row'] - 1) % 5
                    new_row2 = (a2['row'] - 1) % 5
                    result += losung_arr[new_row1][a1['col']] + losung_arr[new_row2][a2['col']]
                else:
                    # Прямоугольное правило
                    result += losung_arr[a1['row']][a2['col']] + losung_arr[a2['row']][a1['col']]

                count += 2

            # Очищаем расшифрованный текст от служебных символов
            result = clean_decrypted_text(result)

        return result

def replace_letters(text, mapping):
    result = ""
    for char in text:
        if char in mapping:
            result += mapping[char]
        else:
            result += char
    return result


def remove_duplicate_letters(text):
    result = ""
    seen = set()
    for char in text:
        if char not in seen:
            seen.add(char)
            result += char
    return result


def remove_letters_from_string(letters, alphabet):
    result = ""
    for char in alphabet:
        if char not in letters:
            result += char
    return result


def find_element_index(matrix, element):
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == element:
                return {'row': i, 'col': j}
    return None


def prepare_text(text):
    """Подготавливает текст для шифрования: вставляет разделители между одинаковыми буквами"""
    result = ""
    i = 0
    while i < len(text):
        result += text[i]
        if i + 1 < len(text):
            # Проверяем, будут ли следующие две буквы одинаковыми
            if text[i] == text[i + 1]:
                if text[i] == 'ф':
                    result += 'я'
                else:
                    result += 'ф'
        i += 1

    # Если после обработки длина нечетная, добавляем разделитель
    if len(result) % 2 != 0:
        # Проверяем последний символ, чтобы не создать две одинаковые буквы
        if result and result[-1] == 'ф':
            result += 'я'
        else:
            result += 'ф'

    return result


def has_unique_letters(text):
    seen = set()
    for char in text:
        if char in seen:
            print(f"Найдена повторяющаяся буква: '{char}'")
            return False
        seen.add(char)
    return True


def replace(text):
    replacements = {
        '.': 'тчк',
        '—': 'тире',
        '-': 'тире',
        ',': 'зпт',
        '!': 'вскл',
        '?': 'впрс',
        '«': 'квчл',
        '»': 'квчп',
        ' ': 'прб'
    }
    result = ""
    for i in text.lower():
        result += replacements.get(i, i)
    return result


def restore(text):
    replacements = {
        'тчк': '.',
        'тире': '—',
        'зпт': ',',
        'вскл': '!',
        'впрс': '?',
        'квчл': '«',
        'квчп': '»',
        'прб': ' '
    }
    result = text
    for code, symbol in replacements.items():
        result = result.replace(code, symbol)
    return result


def format5(text):
    text = str(text).replace(' ', '')
    return ' '.join(text[i:i + 5] for i in range(0, len(text), 5))




def main():
    key = None

    while True:
        print("Введите ключевое слово для шифра Плейфера")
        key = input("Введите ключ: ").strip()
        if not key:
            print("Ключ не может быть пустым!")
            continue

        # Проверка на повторяющиеся буквы в ключе
        alphabet_change = {
            'а': 'а', 'б': 'б', 'в': 'в', 'г': 'г', 'д': 'д',
            'е': 'е', 'ё': 'е', 'ж': 'ж', 'з': 'з', 'и': 'и',
            'й': 'и', 'к': 'к', 'л': 'л', 'м': 'м', 'н': 'н',
            'о': 'о', 'п': 'п', 'р': 'р', 'с': 'с', 'т': 'т',
            'у': 'у', 'ф': 'ф', 'х': 'х', 'ц': 'ц', 'ч': 'ч',
            'ш': 'ш', 'щ': 'щ', 'ъ': 'ь', 'ы': 'ы', 'ь': 'ь',
            'э': 'э', 'ю': 'ю', 'я': 'я'
        }
        processed_key = replace_letters(key.lower(), alphabet_change)

        if not has_unique_letters(processed_key):
            print("ОШИБКА: Ключ не должен содержать повторяющиеся буквы!")
            print("Пожалуйста, введите ключ без повторяющихся букв.")
            continue
        break

    while True:
        print("\nВыберите действие:")
        print("1 - Зашифровать сообщение")
        print("2 - Расшифровать сообщение")
        print("3 - Выход")

        choice = input("Ввод: ").strip()

        if choice == '1':
            text = input("Введите текст для зашифровки: ").strip()
            if not text:
                print("Текст не может быть пустым!")
                continue

            try:
                replaced_text = replace(text)
                encrypted = playfer(replaced_text, False, True, key)
                
                if encrypted is not None:
                    formatted = format5(encrypted)
                    print(f"Зашифрованный текст: {formatted}")

            except Exception as e:
                print(f"Ошибка при шифровании: {e}")
                import traceback
                traceback.print_exc()

        elif choice == '2':
            text = input("Введите текст для расшифровки: ").strip()
            if not text:
                print("Текст не может быть пустым!")
                continue

            try:
                text_without_spaces = text.replace(' ', '')
                decrypted = playfer(text_without_spaces, False, False, key)

                if decrypted is not None:
                    restored = restore(decrypted)
                    print(f"Расшифрованный текст: {restored}")

            except Exception as e:
                print(f"Ошибка при расшифровании: {e}")
                import traceback
                traceback.print_exc()

        elif choice == '3':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 3.")


if __name__ == "__main__":
    main()