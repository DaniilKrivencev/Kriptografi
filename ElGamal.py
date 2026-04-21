from math import gcd

# Только русский алфавит без ё (32 символа)
alphabet = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

# Нумерация от 1 до 32
char_to_num = {c: i + 1 for i, c in enumerate(alphabet)}
num_to_char = {i + 1: c for i, c in enumerate(alphabet)}


def is_prime(n):
    """Проверка числа на простоту"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def mod_inverse(a, m):
    """Обратный элемент по модулю"""
    a %= m
    if a == 0:
        return None

    t, new_t = 0, 1
    r, new_r = m, a

    while new_r != 0:
        q = r // new_r
        t, new_t = new_t, t - q * new_t
        r, new_r = new_r, r - q * new_r

    if r > 1:
        return None
    if t < 0:
        t += m

    return t


def preprocess_text(text, encrypt_mode=True):
    """Приводим к нижнему регистру, ё заменяем на е, игнорируем пробелы"""
    return text.lower().replace('ё', 'е').replace(' ', '')


def postprocess_text(text):
    return text


def compute_x_from_y(p, g, y):
    """Вычисляет секретный ключ x из уравнения y = g^x mod p"""
    for x in range(1, p):
        if pow(g, x, p) == y:
            return x
    return None


def generate_keys(need_x=True):
    """Ввод параметров ключа"""
    while True:
        try:
            p = int(input("Введите простое число p >= 32: "))
            if not is_prime(p):
                print("Ошибка: p должно быть простым числом!")
                continue
            if p < 32:
                print("Ошибка: p должно быть >= 32")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    while True:
        try:
            g = int(input(f"Введите число g (1 < g < {p}): "))
            if g <= 1 or g >= p:
                print(f"Ошибка: g должно быть в диапазоне 1 < g < {p}")
                continue
            break
        except ValueError:
            print("Ошибка: введите целое число")

    if need_x:
        while True:
            try:
                x = int(input(f"Введите секретный ключ x (1 < x < {p}): "))
                if x <= 1 or x >= p:
                    print(f"Ошибка: x должно быть в диапазоне 1 < x < {p}")
                    continue
                break
            except ValueError:
                print("Ошибка: введите целое число")

        y = pow(g, x, p)
        print(f"Открытый ключ: (p: {p}, g: {g}, y: {y})")
        print(f"Секретный ключ: x: {x}")
        return p, g, y, x
    else:
        while True:
            try:
                y = int(input(f"Введите открытый ключ y: "))
                if y <= 1 or y >= p:
                    print(f"Ошибка: y должно быть в диапазоне 1 < y < {p}")
                    continue
                break
            except ValueError:
                print("Ошибка: введите целое число")

        print(f"Открытый ключ: (p: {p}, g: {g}, y: {y})")
        return p, g, y, None


def encrypt_elgamal(message, p, g, y, k_values):
    """Шифрование с использованием списка k"""
    numbers = []
    valid_chars = []

    for char in message:
        if char in char_to_num:
            numbers.append(char_to_num[char])
            valid_chars.append(char)
        else:
            print(f"Предупреждение: символ '{char}' не найден в алфавите и будет пропущен")

    if len(numbers) == 0:
        print("Ошибка: нет допустимых символов для шифрования")
        return None, None, None

    cipher_pairs = []
    for i, m in enumerate(numbers):
        # Циклично выбираем k из списка k_values
        k = k_values[i % len(k_values)]
        a = pow(g, k, p)
        b = (pow(y, k, p) * m) % p
        cipher_pairs.append((a, b))

    return cipher_pairs, numbers, valid_chars


def decrypt_elgamal(cipher_pairs, p, x):
    decrypted_numbers = []

    for i, (a, b) in enumerate(cipher_pairs):
        ax = pow(a, x, p)
        ax_inv = mod_inverse(ax, p)

        if ax_inv is None:
            print(f"Ошибка: не удалось найти обратный элемент для блока {i + 1}")
            return None

        m = (b * ax_inv) % p
        decrypted_numbers.append(m)

    return decrypted_numbers


def parse_cipher_input(cipher_text):
    cipher_pairs = []
    parts = cipher_text.replace(',', ' ').split()

    if len(parts) % 2 != 0:
        print("Ошибка: количество чисел должно быть четным (пары a и b)")
        return None

    for i in range(0, len(parts), 2):
        try:
            a = int(parts[i])
            b = int(parts[i + 1])
            cipher_pairs.append((a, b))
        except ValueError:
            print(f"Ошибка: неверный формат числа в паре ({parts[i]}, {parts[i + 1]})")
            return None

    return cipher_pairs


def numbers_to_text(numbers):
    text = ''
    for num in numbers:
        if num in num_to_char:
            text += num_to_char[num]
        else:
            text += '?'
    return text


def main():
    while True:
        print("\n ПРОГРАММА ШИФРОВАНИЯ ЭЛЬ-ГАМАЛЯ ")
        print("1. Зашифровать")
        print("2. Расшифровать")
        print("0. Выход")

        action_choice = input("\nВаш выбор: ").strip()

        if action_choice == '0':
            print("Выход")
            break

        elif action_choice == '1':
            p, g, y, x = generate_keys(need_x=True)
            message = input("Введите сообщение: ")
            processed = preprocess_text(message, encrypt_mode=True)

            phi = p - 1

            # Находим и выводим подходящие значения k
            valid_k_list = [str(k) for k in range(2, phi) if gcd(k, phi) == 1]

            print(f"\Значения k ):")
            if len(valid_k_list) > 50:
                print(", ".join(valid_k_list[:50]) + f" ... и еще {len(valid_k_list) - 50} вариантов.")
            else:
                print(", ".join(valid_k_list))

            # Ввод 3 рандомизаторов вручную через пробел
            while True:
                try:
                    k_input = input(f"\nВыберите и введите 3 значения k через пробел: ")
                    k_str_list = k_input.strip().split()

                    if len(k_str_list) != 3:
                        print(f"Ошибка: необходимо ввести ровно 3 числа, вы ввели {len(k_str_list)}")
                        continue

                    k_values = [int(k) for k in k_str_list]

                    valid = True
                    for i, k in enumerate(k_values):
                        if k <= 1 or k >= phi:
                            print(f"Ошибка: k{i + 1}: {k} вне диапазона 1 < k < {phi}")
                            valid = False
                            break
                        if gcd(k, phi) != 1:
                            print(
                                f"Ошибка: k{i + 1}: {k} и φ(p): {phi} не взаимно простые (их НОД: {gcd(k, phi)}). Выберите другое число из списка.")
                            valid = False
                            break

                    if valid:
                        break

                except ValueError:
                    print("Ошибка: введите целые числа через пробел")

            result = encrypt_elgamal(processed, p, g, y, k_values)
            if result[0] is None:
                continue

            cipher_pairs, original_numbers, valid_chars = result

            print("\nРезультат:")
            for i, (a, b) in enumerate(cipher_pairs):
                print(f"  Блок {i + 1} (буква '{valid_chars[i]}'): a: {a}, b: {b}")

            print("\nРезультат в одну строку:")
            cipher_str = ' '.join([f"{a} {b}" for a, b in cipher_pairs])
            print(cipher_str)

        elif action_choice == '2':
            p, g, y, _ = generate_keys(need_x=False)
            x = compute_x_from_y(p, g, y)

            if x is None:
                print("Ошибка: не удалось вычислить секретный ключ x по заданным p, g, y")
                continue

            cipher_input = input("\nВведите шифротекст: ")
            cipher_pairs = parse_cipher_input(cipher_input)

            if cipher_pairs is None:
                continue

            decrypted_numbers = decrypt_elgamal(cipher_pairs, p, x)
            if decrypted_numbers is None:
                continue

            decrypted_text = numbers_to_text(decrypted_numbers)
            result = postprocess_text(decrypted_text)
            print(f"\nРезультат: {result}")
        else:
            print("Неверный выбор. Пожалуйста, введите 1, 2 или 0.")

if __name__ == "__main__":
    main()
