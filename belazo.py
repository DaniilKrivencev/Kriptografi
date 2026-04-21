# -*- coding: utf-8 -*-
"""
Шифр Белазо.
Матрица замены: строка задаётся ключом, столбец — открытым текстом.
"""

RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def _norm_text(text: str, alphabet: str) -> str:
    """Оставляет в тексте только символы из алфавита."""
    return "".join(c.upper() for c in text if c.upper() in alphabet)


def _build_belazo_matrix(alphabet: str, key: str) -> list:
    """Строит матрицу замены Белазо."""
    key_chars = _norm_text(key, alphabet)
    if not key_chars:
        key_chars = alphabet[0]
    n = len(alphabet)
    matrix = [list(alphabet)]
    for k in key_chars:
        start = alphabet.index(k)
        row = [alphabet[(start + i) % n] for i in range(n)]
        matrix.append(row)
    return matrix


def belazo_encrypt(plaintext: str, key: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Шифрование Белазо.
    """
    text = _norm_text(plaintext, alphabet)
    key_norm = _norm_text(key, alphabet)
    if not key_norm:
        key_norm = alphabet[0]
    
    matrix = _build_belazo_matrix(alphabet, key_norm)
    result = []
    
    for pos, char in enumerate(text):
        col = alphabet.index(char)
        key_char = key_norm[pos % len(key_norm)]
        row_idx = 1 + key_norm.index(key_char)
        row = matrix[row_idx]
        result.append(row[col])
    
    return "".join(result)


def belazo_decrypt(ciphertext: str, key: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Расшифрование Белазо.
    """
    text = _norm_text(ciphertext, alphabet)
    key_norm = _norm_text(key, alphabet)
    if not key_norm:
        key_norm = alphabet[0]
    
    matrix = _build_belazo_matrix(alphabet, key_norm)
    result = []
    
    for pos, char in enumerate(text):
        key_char = key_norm[pos % len(key_norm)]
        row_idx = 1 + key_norm.index(key_char)
        row = matrix[row_idx]
        col = row.index(char)
        result.append(alphabet[col])
    
    return "".join(result)


def main():
    print("ШИФР БЕЛАЗО")
    print("=" * 50)
    
    text = input("Введите текст: ")
    key = input("Введите ключ (слово-пароль): ")
    
    encrypted = belazo_encrypt(text, key)
    print(f"Зашифровано: {encrypted}")
    
    decrypted = belazo_decrypt(encrypted, key)
    print(f"Расшифровано: {decrypted}")


if __name__ == "__main__":
    main()