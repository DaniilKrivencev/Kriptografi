import random
import os

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def ext_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = ext_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def mod_inverse(a, m):
    g, x, y = ext_gcd(a, m)
    if g != 1:
        raise Exception('Определитель модульного инвертирования не равен 1 (числа не взаимно простые)')
    return x % m

def is_prime(n, k=10):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_safe_prime(bits):
    while True:
        q = random.getrandbits(bits - 1)
        q |= (1 << (bits - 2)) | 1
        if is_prime(q):
            p = 2 * q + 1
            if is_prime(p):
                return p, q

def get_primitive_root(p, q):
    while True:
        g = random.randrange(2, p - 1)
        if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
            return g

def hash_message(message, mod_p):
    ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    h = 0
    for char in message.upper():
        if char in ALPHABET:
            m_i = ALPHABET.index(char) + 1
        else:
            m_i = ord(char)
        h = ((h + m_i) ** 2) % mod_p
    
    if h <= 1:
        h += 2
    if h >= mod_p - 1:
        h = mod_p - 2
    return h

def generate_keys(bits=256):
    p, q = generate_safe_prime(bits)
    g = get_primitive_root(p, q)
    x = random.randrange(2, p - 1)
    y = pow(g, x, p)
    return (p, g, y), (p, g, x)

def sign_elgamal(text, p, g, x, y=0):
    if p <= 32: return "Ошибка: p должно быть > 32"
    if not is_prime(p): return "Ошибка: p должно быть простым числом"
    if x is not None:
        if x <= 1: return "Ошибка: секретный ключ x должен быть > 1"
        if x == y and y != 0: return "Ошибка: секретный ключ x не должен быть равен y"
        if x >= p: return "Ошибка: X должен быть меньше P"
    if g >= p: return "Ошибка: G должен быть меньше P"
    if g <= 1: return "Ошибка: g должен быть > 1"
    
    p_minus_1 = p - 1
    
    # 1. Хэширование текста -> m
    m = hash_message(text, p)
    
    # 2. Генерация случайного К (взаимно простого с P-1)
    k = random.randint(2, p_minus_1 - 1)
    while gcd(k, p_minus_1) != 1:
        k += 1
        if k >= p_minus_1:
            k = 2
            
    # Подписание (п.3):
    # Вычисляем a = G^K mod P
    a = pow(g, k, p)
    
    # Вычисляем b из уравнения: m = X*a + K*b (mod P-1)
    # b = (m - X*a) * K^(-1) mod (P-1)
    k_inv = mod_inverse(k, p_minus_1)
    b = ((m - (x * a % p_minus_1)) * k_inv) % p_minus_1
    
    if b < 0:
        b += p_minus_1
        
    pad_len = len(str(p))
    # Пара (a, b) образует подпись S с нулями вначале (паддинг)
    signature_s = str(a).zfill(pad_len) + str(b).zfill(pad_len)
    
    return f"{text}    ЦП {signature_s}"


def verify_elgamal(m_text, signature_s, p, g, y):
    if not p or not g or not y:
        return "Ошибка: заполните P, G и Y"
        
    pad_len = len(str(p))
    signature_s = str(signature_s).strip()
    
    if len(signature_s) < 2 * pad_len:
         return "Ошибка: длина подписи меньше ожидаемой"
    
    # Извлекаем a и b из подписи S
    a = int(signature_s[:pad_len])
    b = int(signature_s[pad_len:])
    
    # Проверка условий 1 < a < P
    if a <= 0 or a >= p:
        return "Подпись неверна (а вне диапазона)"
        
    # 1. Вычисляем хеш m = h(M)
    m = hash_message(m_text, p)
    
    # 2. Проверка уравнения: G^m mod P == (Y^a * a^b) mod P
    left_part = pow(g, m, p)
    right_part = (pow(y, a, p) * pow(a, b, p)) % p
    
    if left_part == right_part:
        return f"Цифровая подпись верна: G^m ({left_part}) = Y^a * a^b ({right_part})"
    else:
        return f"Цифровая подпись НЕВЕРНА: {left_part} != {right_part}"


def main():
    print("Алгоритм ElGamal (Подпись)")
    print("1. Сгенерировать ключи")
    print("2. Подписать сообщение")
    print("3. Проверить ЭЦП")
    print("0. Выход")
    
    while True:
        choice = input("\nВыберите действие: ")
        if choice == '1':
            try:
                bits = int(input("Введите размер простого числа P (бит, например 256): "))
            except ValueError:
                bits = 256
            pub, priv = generate_keys(bits)
            print(f"\n[+] Ключи сгенерированы!")
            print(f"Открытый ключ (P, G, Y):\n  P \n= {pub[0]}\n  G \n= {pub[1]}\n  Y \n= {pub[2]}")
            print(f"\nСекретный ключ (X):\n  X \n= {priv[2]}")
            
        elif choice == '2':
            p = int(input("Введите модуль P: "))
            g = int(input("Введите G: "))
            x = int(input("Введите секретный ключ X: "))
            msg = input("Введите сообщение M для подписи: ")
                
            res = sign_elgamal(msg, p, g, x)
            print(f"\n[✓] Результат подписания:\n{res}")
            
        elif choice == '3':
            p = int(input("Введите модуль P: "))
            g = int(input("Введите G: "))
            y = int(input("Введите открытый ключ Y: "))
            msg = input("Введите текст сообщения: ")
            sig = input("Введите значение ЦП: ")
                
            res = verify_elgamal(msg, sig, p, g, y)
            print(f"\n[i] Результат проверки:\n{res}")
                
        elif choice == '0':
            break

if __name__ == '__main__':
    main()
