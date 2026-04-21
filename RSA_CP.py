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
    
    # Тест Миллера-Рабина
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

def generate_prime(bits):
    while True:
        p = random.getrandbits(bits)
        # Устанавливаем старший и младший биты, чтобы число имело нужную длину и было нечетным
        p |= (1 << (bits - 1)) | 1
        if is_prime(p):
            return p

def hash_message(message, mod_p):
    """
    Упрощенная хеш-функция квадратичной свертки: h_i = (h_{i-1} + M_i)^2 mod p
    """
    ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    h = 0
    for char in message.upper():
        if char in ALPHABET:
            m_i = ALPHABET.index(char) + 1
        else:
            m_i = ord(char)
        h = ((h + m_i) ** 2) % mod_p
    
    # Чтобы хэш находился строго в интервале (1, N) как по методичке
    if h <= 1:
        h += 2
    if h >= mod_p - 1:
        h = mod_p - 2
    return h

def generate_keys(bits=256):
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    
    e = 65537
    if gcd(e, phi) != 1:
        while True:
            e = random.randrange(2, phi)
            if gcd(e, phi) == 1:
                break
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def sign(message, d, n):
    m = hash_message(message, n)
    s = pow(m, d, n) # S = m^D MOD N
    return s, m

def verify(message, s, e, n):
    m_calc = hash_message(message, n)
    m_dec = pow(s, e, n) # m = S^E MOD N
    return m_calc == m_dec, m_calc, m_dec

def main():
    print("Алгоритм RSA (Подпись)")
    print("1. Сгенерировать ключи")
    print("2. Подписать сообщение")
    print("3. Проверить ЭЦП")
    print("0. Выход")
    
    while True:
        choice = input("\nВыберите действие: ")
        if choice == '1':
            try:
                bits = int(input("Введите размер простых чисел P и Q (бит, например 256): "))
            except ValueError:
                bits = 256
            pub, priv = generate_keys(bits)
            print(f"\n[+] Ключи сгенерированы!")
            print(f"Открытый ключ (E, N):\n  E \n= {pub[0]}\n  N \n= {pub[1]}")
            print(f"\nСекретный ключ (D, N):\n  D \n= {priv[0]}\n  N \n= {priv[1]}")
            
        elif choice == '2':
            msg = input("Введите сообщение M для подписи: ")
            d = int(input("Введите секретный ключ D: "))
            n = int(input("Введите модуль N: "))
                
            sig, m = sign(msg, d, n)
            print(f"\n[i] Хэш-код сообщения m = h(M): {m}")
            print(f"[✓] Получена цифровая подпись S:\n{sig}")
            
        elif choice == '3':
            msg = input("Введите полученное сообщение M: ")
            s = int(input("Введите цифровую подпись S: "))
            e = int(input("Введите открытый ключ E: "))
            n = int(input("Введите модуль N: "))
                
            valid, m_calc, m_dec = verify(msg, s, e, n)
            print(f"\n[i] Вычисленный хэш-код m' = h(M): {m_calc}")
            print(f"[i] Расшифрованный хэш-код m = S^E mod N: {m_dec}")
            if valid:
                print("\n[✓] ПОДПИСЬ ВЕРНА (m == m'). Сообщение подлинное.")
            else:
                print("\n[✗] ПОДПИСЬ НЕВЕРНА (m != m'). Сообщение искажено или подпись подделана.")
                
        elif choice == '0':
            break

if __name__ == '__main__':
    main()
