import math

alphabet_ru32 = "абвгдежзийклмнопрстуфхцчшщьыэюя"

def get_key_sequence(key_str):
    """
    Преобразует строку-ключ в последовательность чисел, 
    основанную на алфавитном порядке букв.
    """
    if not key_str:
        return []
    
    # Очистка ключа
    clean_key = key_str.replace(" ", "").upper()
    
    # Создаем пары (буква, оригинальный индекс)
    key_chars = [(c, i) for i, c in enumerate(clean_key)]
    
    # Сортируем по букве (устойчивая сортировка)
    sorted_key = sorted(key_chars, key=lambda x: x[0])
    
    # Присваиваем ранги (1..N)
    ranks = [0] * len(clean_key)
    for rank, (char, original_idx) in enumerate(sorted_key):
        ranks[original_idx] = rank + 1
        
    return ranks

def encrypt(text, key):
    if not key:
        return "Ошибка: пустой ключ"
        
    key_seq = get_key_sequence(key)
    cols = len(key_seq)
    
    clean_text = text.replace(" ", "").lower()
    clean_text = "".join(c for c in clean_text if c in alphabet_ru32)
    
    rows = math.ceil(len(clean_text) / cols)
    
    # Матрица
    matrix = [['' for _ in range(cols)] for _ in range(rows)]
    
    # Записываем построчно
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx < len(clean_text):
                matrix[r][c] = clean_text[idx]
                idx += 1
            else:
                matrix[r][c] = '' # Пустая клетка
    
    # Считываем по столбцам в порядке ключа (1, 2, 3...)
    encrypted_text = ""
    for r in range(1, cols + 1):
        try:
            col_idx = key_seq.index(r)
        except ValueError:
            continue
        
        for row_idx in range(rows):
            val = matrix[row_idx][col_idx]
            if val != '':
                encrypted_text += val
                
    # Форматируем по 5 символов
    return " ".join(encrypted_text[i:i+5] for i in range(0, len(encrypted_text), 5))

def decrypt(ciphertext, key):
    if not key:
        return "Ошибка: пустой ключ"
        
    key_seq = get_key_sequence(key)
    cols = len(key_seq)
    
    clean_text = ciphertext.replace(" ", "")
    total_len = len(clean_text)
    
    rows = math.ceil(total_len / cols)
    
    # Количество полных (длинных) столбцов
    # Это количество символов в последней строке
    items_in_last_row = total_len % cols
    if items_in_last_row == 0:
        items_in_last_row = cols
        
    # Длинные столбцы - это первые items_in_last_row столбцов МАТРИЦЫ (0..k-1)
    
    matrix = [['' for _ in range(cols)] for _ in range(rows)]
    current_text_idx = 0
    
    # Заполняем матрицу по столбцам В ПОРЯДКЕ КЛЮЧА
    for r in range(1, cols + 1):
        col_idx = key_seq.index(r)
        
        # Высота этого столбца?
        # Если индекс столбца (при записи) < items_in_last_row, то он длинный (rows)
        # Иначе короткий (rows - 1)
        col_height = rows if col_idx < items_in_last_row else rows - 1
        
        for row_idx in range(col_height):
            if current_text_idx < total_len:
                matrix[row_idx][col_idx] = clean_text[current_text_idx]
                current_text_idx += 1
                
    # Считываем по строкам
    decrypted = ""
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c]:
                decrypted += matrix[r][c]
                
    return decrypted

if __name__ == "__main__":
    t = input("Введите фразу для шифрования: ")
    k = input("Введите ключ (слово или цифры): ")
    
    print(f"\nТекст: {t}")
    print(f"Ключ: {k}")
    
    enc = encrypt(t, k)
    print(f"Зашифровано: {enc}")
    
    dec = decrypt(enc, k)
    print(f"Расшифровано: {dec}")
