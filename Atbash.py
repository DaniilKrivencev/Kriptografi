ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

phrase = input("Введите фразу: ")

# Очищаем фразу: нижний регистр, убираем пробелы, заменяем пунктуацию
phrase_clean = phrase.lower().replace(' ', '').replace(',', 'зпт').replace('.', 'тчк')

# Шифруем
encrypted = "".join(ALPHABET[len(ALPHABET)-1-ALPHABET.index(c)] 
                    if c in ALPHABET else c for c in phrase_clean)

# разбиваем на группы по 5 символов
formatted = " ".join(encrypted[i:i+5] for i in range(0, len(encrypted), 5))
print(f"Зашифровано: {formatted}")

# Расшифровываем (убираем пробелы для дешифрования)
decrypted = "".join(ALPHABET[len(ALPHABET)-1-ALPHABET.index(c)] 
                    if c in ALPHABET else c for c in formatted.replace(" ", "").lower())
decrypted = decrypted.replace('зпт', ',').replace('тчк', '.')
print(f"Расшифровано: {decrypted}")


