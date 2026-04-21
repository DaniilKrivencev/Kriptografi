import random

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y

def mod_inverse(e, phi):
    g, x, y = extended_gcd(e, phi)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    return x % phi

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def rsa_encrypt(message, e, n):
    """
    Шифрование: Ci = Mi^E MOD N
    """
    ciphertext = []
    for m in message:
        c = pow(m, e, n)
        ciphertext.append(c)
    return ciphertext

def rsa_decrypt(ciphertext, d, n):
    """
    Расшифрование: Mi = Ci^D MOD N
    """
    message = []
    for c in ciphertext:
        m = pow(c, d, n)
        message.append(m)
    return message

def main():
    print("--- 21. алгоритм RSA ---")
    # Генерация ключей
    p = 61
    q = 53
    print(f"Выбраны простые числа P={p}, Q={q}")
    
    n = p * q
    phi = (p - 1) * (q - 1)
    print(f"N = P*Q = {n}")
    print(f"Функция Эйлера phi(N) = {phi}")
    
    e = 17 # случайное целое число 1 < E < phi(N), взаимно простое с phi(N)
    while gcd(e, phi) != 1:
        e += 1
    print(f"Открытая экспонента E = {e}")
    
    d = mod_inverse(e, phi)
    print(f"Секретная экспонента D = {d}")
    
    print(f"Открытый ключ: (E={e}, N={n})")
    print(f"Секретный ключ: D={d}")
    
    m_text = "HELLO"
    M = [ord(char) for char in m_text]
    print(f"\nИсходное сообщение M: {m_text} -> {M}")
    
    # 1. Шифрование
    C = rsa_encrypt(M, e, n)
    print(f"Зашифрованное сообщение C: {C}")
    
    # 2. Расшифрование
    M_decrypted = rsa_decrypt(C, d, n)
    m_dec_text = "".join(chr(c) for c in M_decrypted)
    print(f"Расшифрованное сообщение: {M_decrypted} -> {m_dec_text}")

if __name__ == '__main__':
    main()
