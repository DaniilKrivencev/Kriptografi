# -*- coding: utf-8 -*-
"""
Шифр Тритемия.
Формула: Yj = X(i+j-1) mod n
"""

RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def _norm_text(text: str, alphabet: str) -> str:
    """Оставляет в тексте только символы из алфавита."""
    return "".join(c.upper() for c in text if c.upper() in alphabet)


def trithemius_encrypt(plaintext: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Шифрование по методу Тритемия.
    Формула: Yj = X(i+j-1) mod n
    """
    n = len(alphabet)
    text = _norm_text(plaintext, alphabet)
    result = []
    
    for j, char in enumerate(text, 1):  # j начинается с 1 для формулы
        i = alphabet.index(char) + 1  # i в формуле тоже с 1
        new_pos = (i + j - 1) % n
        if new_pos == 0:  # если 0, берем последнюю букву
            new_pos = n
        new_idx = new_pos - 1  # обратно в 0-based индекс
        result.append(alphabet[new_idx])
    
    return "".join(result)


def trithemius_decrypt(ciphertext: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Расшифрование по методу Тритемия.
    Обратная формула: Xi = Yj - j + 1 mod n
    """
    n = len(alphabet)
    text = _norm_text(ciphertext, alphabet)
    result = []
    
    for j, char in enumerate(text, 1):  # j начинается с 1
        y_pos = alphabet.index(char) + 1  # Yj позиция в алфавите (с 1)
        original_pos = (y_pos - j + 1) % n
        if original_pos == 0:
            original_pos = n
        original_idx = original_pos - 1
        result.append(alphabet[original_idx])
    
    return "".join(result)


def main():
    print("ШИФР ТРИТЕМИЯ")
    
    text = input("Введите текст: ")
    
    encrypted = trithemius_encrypt(text)
    print(f"Зашифровано: {encrypted}")
    
    decrypted = trithemius_decrypt(encrypted)
    print(f"Расшифровано: {decrypted}")


if __name__ == "__main__":
    main()