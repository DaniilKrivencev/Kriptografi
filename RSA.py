import random
from math import gcd

alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# Расширенный алгоритм Евклида
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd_val, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return gcd_val, x, y


# Правильный обратный элемент
def mod_inverse(e, phi):
    gcd_val, x, _ = extended_gcd(e, phi)

    if gcd_val != 1:
        return None

    return x % phi


def input_keys():
    while True:
        try:
            p = int(input("Введите простое число P: "))
            q = int(input("Введите простое число Q: "))

            if not is_prime(p) or not is_prime(q):
                print("P и Q должны быть простыми числами\n")
                continue

            if p == q:
                print("P и Q не должны совпадать\n")
                continue

            n = p * q
            if n <= 32:
                print("Ошибка: N должно быть больше 32 (иначе нарушится шифрование текста)\n")
                continue

            phi = (p - 1) * (q - 1)

            print(f"N: {n}")
            print(f"φ(N): {phi}")

            e = int(input("Введите E (1 < E < φ(N) и взаимно просто с φ(N)): "))

            if not (1 < e < phi):
                print("E должно быть в диапазоне (1, φ(N))\n")
                continue

            if gcd(e, phi) != 1:
                print("E не взаимно просто с φ(N)\n")
                continue

            # защита от d = e
            if (e * e) % phi == 1:
                print("Плохое E (даёт D равное E), выберите другое\n")
                continue

            d = mod_inverse(e, phi)

            if d is None:
                print("Не удалось найти D\n")
                continue

            print(f"D: {d}")

            return (e, n), (d, n)

        except ValueError:
            print("Введите корректные числа\n")


def text_to_numbers(text):
    numbers = []

    for char in text:
        if char == 'ё':
            char = 'е'

        if char in alphabet:
            numbers.append(alphabet.index(char) + 1)

    return numbers


def numbers_to_text(numbers):
    text = ""
    for num in numbers:
        if 1 <= num <= 32:
            text += alphabet[num - 1]
        else:
            text += "?"
    return text


def encrypt(message, public_key, block_size):
    e, n = public_key
    numbers = text_to_numbers(message)

    encrypted_blocks = []
    for m in numbers:
        c = pow(m, e, n)
        encrypted_blocks.append(str(c).zfill(block_size))

    return "".join(encrypted_blocks)


def parse_cipher_fixed(data, block_size):
    if len(data) % block_size != 0:
        print("Ошибка: длина шифртекста некорректна")
        return None

    cipher = []
    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]
        cipher.append(int(block))

    return cipher


def decrypt(cipher, private_key):
    d, n = private_key

    decrypted = []
    for c in cipher:
        m = pow(c, d, n)
        decrypted.append(m)

    return numbers_to_text(decrypted)


def decrypt_from_string(data, private_key, block_size):
    cipher = parse_cipher_fixed(data, block_size)
    if cipher is None:
        return None

    return decrypt(cipher, private_key)


def validate_keys(public_key, private_key):
    e, n1 = public_key
    d, n2 = private_key

    if n1 != n2:
        print("Ошибка: N в ключах не совпадает")
        return False

    if e == d:
        print("Ошибка: открытый и закрытый ключ совпадают")
        return False

    return True


def main():
    print("\n ПРОГРАММА RSA ШИФРОВАНИЯ ")
    while True:
        print("\n1. Сгенерировать ключи (нужны P и Q)")
        print("2. Зашифровать сообщение (нужны открытые E и N)")
        print("3. Расшифровать шифртекст (нужны секретные D и N)")
        print("0. Выход")

        choice = input("\nВыбор: ").strip()

        if choice == "1":
            print("\n ГЕНЕРАЦИЯ КЛЮЧЕЙ ")
            res = input_keys()
            if res:
                public_key, private_key = res
                if validate_keys(public_key, private_key):
                    print("Ключи успешно созданы! Сохраните D и N для расшифровки.")

        elif choice == "2":
            print("\n ЗАШИФРОВАНИЕ ")
            try:
                e = int(input("Введите открытый ключ (E): "))
                n = int(input("Введите модуль (N): "))
            except ValueError:
                print("Ошибка ввода. Ожидаются числа!\n")
                continue
            
            block_size = len(str(n))
            text = input("Введите исходный текст: ").lower()
            encrypted = encrypt(text, (e, n), block_size)

            print("\nЗашифрованное сообщение:")
            print(encrypted)

        elif choice == "3":
            print("\n РАСШИФРОВАНИЕ ")
            try:
                d = int(input("Введите секретный ключ (D): "))
                n = int(input("Введите модуль (N): "))
            except ValueError:
                print("Ошибка ввода. Ожидаются числа!\n")
                continue
                
            block_size = len(str(n))
            data = input("Введите шифртекст (строка из цифр): ").strip()

            decrypted = decrypt_from_string(data, (d, n), block_size)

            if decrypted is not None:
                print("\nРасшифрованный текст:")
                print(decrypted)

        elif choice == "0":
            print("Выход")
            break
        else:
            print("Неверный выбор!\n")


if __name__ == "__main__":
    main()
