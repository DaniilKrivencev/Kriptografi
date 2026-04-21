def text_to_hex(text):
    """Преобразует обычный текст в шестнадцатеричную строку (UTF-8)"""
    return text.encode('utf-8').hex().upper()

def hex_to_text(hex_str):
    """Преобразует шестнадцатеричную строку обратно в текст"""
    try:
        return bytes.fromhex(hex_str).decode('utf-8')
    except ValueError:
        return bytes.fromhex(hex_str).decode('utf-8', errors='ignore')

def preprocess_text(text, encrypt_mode=True):
    """Предобработка: разбиение на блоки автоматически дополнит нулями"""
    return text

def postprocess_text(text):
    """Убираем нули (\x00), добавленные для добивки блока"""
    return text.rstrip('\x00')

#  Основной алгоритм шифрования 

# Таблица подстановки
PI = [
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    181, 112, 14, 86, 8, 12, 118, 18, 191, 114, 19, 71, 156, 183, 93, 135,
    21, 161, 150, 41, 16, 123, 154, 199, 243, 145, 120, 111, 157, 158, 178,
    177, 50, 117, 25, 61, 255, 53, 138, 126, 109, 84, 198, 128, 195, 189,
    13, 87, 223, 245, 36, 169, 62, 168, 67, 201, 215, 121, 214, 246, 124,
    34, 185, 3, 224, 15, 236, 222, 122, 148, 176, 188, 220, 232, 40, 80,
    78, 51, 10, 74, 167, 151, 96, 115, 30, 0, 98, 68, 26, 184, 56, 130,
    100, 159, 38, 65, 173, 69, 70, 146, 39, 94, 85, 47, 140, 163, 165, 125,
    105, 213, 149, 59, 7, 88, 179, 64, 134, 172, 29, 247, 48, 55, 107, 228,
    136, 217, 231, 137, 225, 27, 131, 73, 76, 63, 248, 254, 141, 83, 170, 144,
    202, 216, 133, 97, 32, 113, 103, 164, 45, 43, 9, 91, 203, 155, 37, 208,
    190, 229, 108, 82, 89, 166, 116, 210, 230, 244, 180, 192, 209, 102, 175,
    194, 57, 75, 99, 182
]

# Коэффициенты для линейного преобразования
R_coeffs = [148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1]

# Таблица обратной подстановки π'^-1
INV_PI = [0] * 256
for i, val in enumerate(PI):
    INV_PI[val] = i

# Преобразует hex-строку в список байт
def hex_to_bytes(hex_str):
    hex_str = hex_str.replace(' ', '')
    return [int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)]

# Преобразует список байт в hex-строку
def bytes_to_hex(bytes_list):
    return ''.join(f'{b:02x}' for b in bytes_list)

# Преобразует список байт в целое число
def bytes_to_int_be(bytes_list):
    result = 0
    for b in bytes_list:
        result = (result << 8) | b
    return result

# Преобразует целое число в список байт
def int_to_bytes_be(x, length=16):
    result = []
    for i in range(length - 1, -1, -1):
        result.append((x >> (i * 8)) & 0xFF)
    return result

# Умножение в поле GF(2^8) с образующим многочленом
def gf_mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit:
            a ^= 0xC3
        b >>= 1
    return p & 0xFF

# X[k](a) = k ⊕ a
def X(k, a): return k ^ a

# S(a) = π(a15)||...||π(a0) - a15 старший байт
def S(a):
    bytes_a = int_to_bytes_be(a, 16)
    transformed = [PI[b] for b in bytes_a]
    return bytes_to_int_be(transformed)

# S^{-1}(a) = π^{-1}(a15)||...||π^{-1}(a0)
def S_inv(a):
    bytes_a = int_to_bytes_be(a, 16)
    transformed = [INV_PI[b] for b in bytes_a]
    return bytes_to_int_be(transformed)

# R(a) = ℓ(a15,...,a0)||a15||...||a1
def R(a):
    bytes_a = int_to_bytes_be(a, 16)

    # Вычисляем ℓ(a15,...,a0) = Σ(coeffs[i] * a[i]) в GF(2^8)
    l_val = 0
    for i in range(16):
        term = gf_mul(R_coeffs[i], bytes_a[i])
        l_val ^= term

    # Формируем результат: ℓ(a) || a15 || a14 || ... || a1
    result_bytes = [l_val] + bytes_a[:-1]
    return bytes_to_int_be(result_bytes)

# R^{-1}(a) = a14||...||a0||ℓ(a14,...,a0,a15)
def R_inv(a):
    bytes_a = int_to_bytes_be(a, 16)

    # a14...a0
    a14_to_a0 = bytes_a[1:]
    a15 = bytes_a[0]


    # Вычисляем ℓ(a14,...,a0,a15)
    l_val = 0
    for i in range(16):
        # Используем a14...a0,a15 как входные данные
        if i < 15:
            val = bytes_a[i + 1]
        else:
            val = a15
        term = gf_mul(R_coeffs[i], val)
        l_val ^= term

    result_bytes = a14_to_a0 + [l_val]
    return bytes_to_int_be(result_bytes)

# L(a) = R^16(a)
def L(a):
    for _ in range(16):
        a = R(a)
    return a

# L^{-1}(a) = (R^{-1})^16(a)
def L_inv(a):
    for _ in range(16):
        a = R_inv(a)
    return a

# LSX[k](a) = L(S(X[k](a)))
def LSX(k, a):
    return L(S(X(k, a)))

# F[k](a1, a0) = (LSX[k](a1) ⊕ a0, a1)
def F(k, a1, a0):
    return (LSX(k, a1) ^ a0, a1)

# Возвращает константу C_i = L(Vec128(i))
def get_C(i):
    # Vec128(i) - представление числа i в виде 16-байтового вектора
    bytes_i = int_to_bytes_be(i, 16)
    val_i = bytes_to_int_be(bytes_i)
    return L(val_i)

# Развертывание ключа K (256 бит) в 10 итерационных ключей
def expand_key(key_hex):
    key_bytes = hex_to_bytes(key_hex)

    # K1 - первые 16 байт, K2 - последние 16 байт
    K1_bytes = key_bytes[:16]
    K2_bytes = key_bytes[16:]

    K1 = bytes_to_int_be(K1_bytes)
    K2 = bytes_to_int_be(K2_bytes)

    keys = [K1, K2]

    # Генерируем K3...K10
    for i in range(1, 5):  # i = 1,2,3,4
        a1, a0 = keys[2 * i - 2], keys[2 * i - 1]

        for j in range(1, 9):  # j = 1..8
            C = get_C(8 * (i - 1) + j)
            a1, a0 = F(C, a1, a0)

        keys.append(a1)
        keys.append(a0)

    return keys[:10]

# Зашифрование одного блока (128 бит)
def encrypt_block(plaintext_hex, keys):
    a = bytes_to_int_be(hex_to_bytes(plaintext_hex))

    state = a
    for i in range(9):
        # X[Ki]
        x_result = X(keys[i], state)
        # S
        s_result = S(x_result)
        # L
        state = L(s_result)

    # X[K10]
    state = X(keys[9], state)
    result_bytes = int_to_bytes_be(state, 16)
    return bytes_to_hex(result_bytes)

# Расшифрование одного блока (128 бит)
def decrypt_block(ciphertext_hex, keys):
    b = bytes_to_int_be(hex_to_bytes(ciphertext_hex))

    state = b
    # X[K10]
    state = X(keys[9], state)

    for i in range(8, -1, -1):
        # L^{-1}
        state = L_inv(state)
        # S^{-1}
        state = S_inv(state)
        # X[K_{i+1}]
        state = X(keys[i], state)

    result_bytes = int_to_bytes_be(state, 16)
    return bytes_to_hex(result_bytes)

# Разбивает hex-строку на блоки по block_size символов
def split_into_blocks(hex_string, block_size=32):
    blocks = []
    for i in range(0, len(hex_string), block_size):
        block = hex_string[i:i + block_size]
        if len(block) < block_size:
            block = block.ljust(block_size, '0')
        blocks.append(block)
    return blocks

# Шифрует текст (hex), разбивая на блоки
def encrypt_text(plain_hex, keys):
    blocks = split_into_blocks(plain_hex)
    encrypted_blocks = []
    for block in blocks:
        encrypted = encrypt_block(block, keys)
        encrypted_blocks.append(encrypted)
    return ''.join(encrypted_blocks).upper()

# Расшифровывает текст (hex), разбивая на блоки
def decrypt_text(cipher_hex, keys):
    blocks = split_into_blocks(cipher_hex)
    decrypted_blocks = []
    for block in blocks:
        decrypted = decrypt_block(block, keys)
        decrypted_blocks.append(decrypted)

    result = ''.join(decrypted_blocks)
    # Удаляем нулевое дополнение
    while len(result) > 0 and result.endswith('00'):
        result = result[:-2]
    return result.upper()

def main():
    print("\nВыберите действие:")
    print("1. Зашифровать")
    print("2. Расшифровать")

    action_choice = input("Ваш выбор: ").strip()

    encrypt_mode = (action_choice == '1')

    if encrypt_mode:
        print("\nВыберите формат ввода:")
        print("1. Текстовый формат")
        print("2. HEX формат")
        format_choice = input("Ваш выбор: ").strip()
        text_mode = (format_choice == '1')
    else:
        print("\nВыберите формат вывода:")
        print("1. Текстовый формат")
        print("2. HEX формат")
        format_choice = input("Ваш выбор: ").strip()
        text_mode = (format_choice == '1')


    key = input("Введите 256-битный ключ (64 шестнадцатеричных символа): ").strip().upper().replace(' ', '')

    if len(key) != 64:
        print(f"ОШИБКА: Ключ должен содержать 64 символа, получено {len(key)}")
        return

    if not all(c in '0123456789ABCDEF' for c in key):
        print("ОШИБКА: Ключ должен содержать только шестнадцатеричные символы (0-9, A-F)")
        return

    # Развертывание ключа
    keys = expand_key(key)

    try:
        text = input("Введите текст: ")

        if encrypt_mode:
            if text_mode:
                # Текстовый формат с предобработкой
                processed = preprocess_text(text, encrypt_mode=True)
                hex_text = text_to_hex(processed)
                result = encrypt_text(hex_text, keys)
                print(f"\nРезультат: {result}")
            else:
                # HEX формат без преобразований
                hex_input = text.strip().upper().replace(' ', '')
                if not all(c in '0123456789ABCDEF' for c in hex_input):
                    print("ОШИБКА: Входные данные должны содержать только шестнадцатеричные символы (0-9, A-F)")
                    return
                result = encrypt_text(hex_input, keys)
                print(f"\nРезультат: {result}")
        else:
            # Расшифрование (ввод всегда в hex)
            hex_input = text.strip().upper().replace(' ', '')
            if not all(c in '0123456789ABCDEF' for c in hex_input):
                print("ОШИБКА: Входные данные должны содержать только шестнадцатеричные символы (0-9, A-F)")
                return

            decrypted_hex = decrypt_text(hex_input, keys)

            if text_mode:
                # Текстовый формат с постобработкой
                decrypted_text = hex_to_text(decrypted_hex)
                result = postprocess_text(decrypted_text)
                print(f"\nРезультат: {result}")
            else:
                # HEX формат без преобразований
                print(f"\nРезультат: {decrypted_hex}")
    except Exception as e:
        print(f"ОШИБКА: {e}")

    return

if __name__ == "__main__":
    main()
