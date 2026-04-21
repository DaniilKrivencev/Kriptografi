# -*- coding: utf-8 -*-
"""
Шифр Виженера:
1) С самоключом
2) Ключом-шифртекстом
"""

RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def _norm_text(text: str, alphabet: str) -> str:
    """Оставляет в тексте только символы из алфавита."""
    return "".join(c.upper() for c in text if c.upper() in alphabet)


def vigenere_autokey_encrypt(plaintext: str, secret_letter: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Шифр Виженера с самоключом: гамма = секретная буква + открытый текст.
    """
    text = _norm_text(plaintext, alphabet)
    secret = _norm_text(secret_letter, alphabet)
    if not secret:
        secret = alphabet[0]
    
    t0 = secret[0]
    n = len(alphabet)
    gamma = [alphabet.index(t0)]
    for c in text:
        gamma.append(alphabet.index(c))
    
    result = []
    for i, c in enumerate(text):
        s_i = (gamma[i] + alphabet.index(c)) % n
        result.append(alphabet[s_i])
    
    return "".join(result)


def vigenere_autokey_decrypt(ciphertext: str, secret_letter: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Расшифрование шифра с самоключом.
    """
    text = _norm_text(ciphertext, alphabet)
    secret = _norm_text(secret_letter, alphabet)
    if not secret:
        secret = alphabet[0]
    
    n = len(alphabet)
    gamma = [alphabet.index(secret[0])]
    result = []
    
    for i, s_char in enumerate(text):
        t_i = (alphabet.index(s_char) - gamma[i]) % n
        result.append(alphabet[t_i])
        gamma.append(t_i)
    
    return "".join(result)


def vigenere_ciphertext_key_encrypt(plaintext: str, secret_letter: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Шифр Виженера с ключом-шифртекстом: гамма = секретная буква + шифртекст.
    """
    text = _norm_text(plaintext, alphabet)
    secret = _norm_text(secret_letter, alphabet)
    if not secret:
        secret = alphabet[0]
    
    n = len(alphabet)
    gamma = [alphabet.index(secret[0])]
    result = []
    
    for i, c in enumerate(text):
        s_i = (gamma[i] + alphabet.index(c)) % n
        result.append(alphabet[s_i])
        gamma.append(s_i)
    
    return "".join(result)


def vigenere_ciphertext_key_decrypt(ciphertext: str, secret_letter: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    """
    Расшифрование с ключом-шифртекстом.
    """
    text = _norm_text(ciphertext, alphabet)
    secret = _norm_text(secret_letter, alphabet)
    if not secret:
        secret = alphabet[0]
    
    n = len(alphabet)
    gamma = [alphabet.index(secret[0])]
    for c in text:
        gamma.append(alphabet.index(c))
    
    result = []
    for i, s_char in enumerate(text):
        t_i = (alphabet.index(s_char) - gamma[i]) % n
        result.append(alphabet[t_i])
    
    return "".join(result)


def main():
    print("ШИФР ВИЖЕНЕРА")
    print("=" * 50)
    
    text = input("Введите текст: ")
    secret = input("Введите одну секретную букву (ключ): ")
    
    print("\n1. Шифр с самоключом:")
    encrypted = vigenere_autokey_encrypt(text, secret)
    print(f"Зашифровано: {encrypted}")
    decrypted = vigenere_autokey_decrypt(encrypted, secret)
    print(f"Расшифровано: {decrypted}")
    
    print("\n2. Шифр с ключом-шифртекстом:")
    encrypted = vigenere_ciphertext_key_encrypt(text, secret)
    print(f"Зашифровано: {encrypted}")
    decrypted = vigenere_ciphertext_key_decrypt(encrypted, secret)
    print(f"Расшифровано: {decrypted}")


if __name__ == "__main__":
    main()