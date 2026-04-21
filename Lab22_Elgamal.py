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

def mod_inverse(k, p):
    g, x, y = extended_gcd(k, p)
    if g != 1:
        raise Exception('Обратного элемента не существует')
    return x % p

def elgamal_encrypt(M, p, g, y):
    """
    Шифрование:
    ai = g^ki mod p
    bi = y^ki * Mi mod p
    """
    ciphertext = []
    for Mi in M:
        if Mi >= p:
            raise ValueError(f"Шифрвеличина Mi={Mi} должна быть меньше p={p}")
        
        # Выбирается случайное ki взаимно простое с p-1
        phi_p = p - 1
        ki = random.randint(2, phi_p - 1)
        while gcd(ki, phi_p) != 1:
            ki = random.randint(2, phi_p - 1)
            
        ai = pow(g, ki, p)
        bi = (pow(y, ki, p) * Mi) % p
        ciphertext.append((ai, bi))
        
    return ciphertext

def elgamal_decrypt(ciphertext, x, p):
    """
    Расшифрование:
    Mi = bi / ai^x (mod p) 
    т.е. Mi = bi * (ai^x)^-1 (mod p)
    """
    message = []
    for ai, bi in ciphertext:
        ax = pow(ai, x, p)
        ax_inv = mod_inverse(ax, p)
        Mi = (bi * ax_inv) % p
        message.append(Mi)
    return message

def main():
    print("--- 22. алгоритм Elgamal ---")
    
    # Большое простое число
    p = 227 
    # Выбор x и g
    x = 15 # Секретный ключ (1 < x < p)
    g = 2  # (1 < g < p)
    
    # Вычисляется y
    y = pow(g, x, p)
    
    print(f"Открытые ключи: p={p}, g={g}, y={y}")
    print(f"Секретный ключ: x={x}")
    
    m_text = "SECRET"
    M = [ord(char) for char in m_text]
    print(f"\nИсходное сообщение M: {m_text} -> {M}")
    
    # 1. Шифрование
    C = elgamal_encrypt(M, p, g, y)
    print(f"Зашифрованное сообщение C: {C}")
    
    # 2. Расшифрование
    M_decrypted = elgamal_decrypt(C, x, p)
    m_dec_text = "".join(chr(c) for c in M_decrypted)
    print(f"Расшифрованное сообщение: {M_decrypted} -> {m_dec_text}")

if __name__ == '__main__':
    main()
