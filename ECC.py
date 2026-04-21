"""
ПРОСТАЯ ПРОГРАММА ДЛЯ ECC ШИФРОВАНИЯ
С поддержкой:
 Ручного ввода параметров
 Тестирования
"""

import random

#  ОСНОВНЫЕ ФУНКЦИИ 

def mod_inverse(n, p):
    """Находит обратный элемент числа n по модулю p"""
    try:
        return pow(n, p - 2, p)
    except ValueError:
        return 0

def point_double(P, a, p):
    """Удвоение точки P"""
    if P is None:
        return None
    x, y = P
    if y == 0:
        return None
    lambd = (3 * x * x + a) * mod_inverse(2 * y, p) % p
    x3 = (lambd * lambd - 2 * x) % p
    y3 = (lambd * (x - x3) - y) % p
    return (x3, y3)

def point_add(P, Q, a, p):
    """Сложение двух точек P и Q"""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        return point_double(P, a, p)
    lambd = (y2 - y1) * mod_inverse(x2 - x1, p) % p
    x3 = (lambd * lambd - x1 - x2) % p
    y3 = (lambd * (x1 - x3) - y1) % p
    return (x3, y3)

def multiply_point(k, P, a, p):
    """Умножение точки P на число k"""
    result = None
    current = P
    while k > 0:
        if k % 2 == 1:
            result = point_add(result, current, a, p)
        current = point_double(current, a, p)
        k = k // 2
    return result

def encrypt(message, public_key, G, a, p, k):
    """Шифрование сообщения"""
    R = multiply_point(k, G, a, p)
    P = multiply_point(k, public_key, a, p)
    if P is None:
        return (R, 0)
    e = (message * P[0]) % p
    return (R, e)

def decrypt(ciphertext, private_key, a, p):
    """Расшифрование сообщения"""
    R, e = ciphertext
    Q = multiply_point(private_key, R, a, p)
    if Q is None:
        return 0
    x_Q_inv = mod_inverse(Q[0], p)
    message = (e * x_Q_inv) % p
    return message

def find_order(G, a, p):
    """Находит порядок точки G (наименьшее q, при котором q*G O)"""
    point = G
    q = 1
    while point is not None:
        point = point_add(point, G, a, p)
        q += 1
        if q > p * 2:
            return None
    return q

def find_all_points(a, b, p):
    """Находит все точки на эллиптической кривой"""
    points = []
    for x in range(p):
        right = (x*x*x + a*x + b) % p
        for y in range(p):
            if (y*y) % p == right:
                points.append((x, y))
    return points

#  ФУНКЦИИ ДЛЯ РАБОТЫ С ТЕКСТОМ 

ALPHABET = {
    'А': 1, 'Б': 2, 'В': 3, 'Г': 4, 'Д': 5, 'Е': 6, 'Ж': 7, 'З': 8,
    'И': 9, 'К': 10, 'Л': 11, 'М': 12, 'Н': 13, 'О': 14, 'П': 15,
    'Р': 16, 'С': 17, 'Т': 18, 'У': 19, 'Ф': 20, 'Х': 21, 'Ц': 22,
    'Ч': 23, 'Ш': 24, 'Щ': 25, 'Ъ': 26, 'Ы': 27, 'Ь': 28, 'Э': 29,
    'Ю': 30, 'Я': 31, ' ': 32, ',': 33, '.': 34, '!': 35, '?': 36
}

REVERSE_ALPHABET = {v: k for k, v in ALPHABET.items()}

def text_to_numbers(text):
    numbers = []
    for char in text.upper():
        if char in ALPHABET:
            numbers.append(ALPHABET[char])
    return numbers

def numbers_to_text(numbers):
    text = []
    for num in numbers:
        if num in REVERSE_ALPHABET:
            text.append(REVERSE_ALPHABET[num])
    return ''.join(text)

#  ТЕСТЫ 

def run_test(params, use_random=False):
    print("\n ТЕСТИРОВАНИЕ ")
    
    a = params['a']
    b = params['b'] % params['p']
    p = params['p']
    G = params['G']
    
    print(f"\nПараметры кривой:")
    print(f"  y^2: x^3 + {a}x + {b} (mod {p})")
    print(f"  Базовая точка G: {G}")
    
    x, y = G
    left = (y*y) % p
    right = (x*x*x + a*x + b) % p
    if left != right:
        print(f"\n  ВНИМАНИЕ: Точка G: {G} НЕ лежит на кривой!")
        return
    
    print(f"\nВычисление порядка точки G")
    q = find_order(G, a, p)
    print(f"  Порядок точки G: q: {q}")
    
    if q is None or q < 3:
        print(f"\n ВНИМАНИЕ: Точка G имеет малый порядок {q}, не подходит для криптографии!")
        return
    
    if use_random:
        private_key = random.randint(1, q - 1)
        print(f"\n Рандомайзер сгенерировал Секретный ключ Cb: {private_key}")
    else:
        private_key = params['Cb']
        print(f"\n Заданный секретный ключ Cb: {private_key}")
    
    public_key = multiply_point(private_key, G, a, p)
    print(f"  Открытый ключ Db: {public_key}")
    
    message = params['message']
    print(f"\n Сообщение: m: {message}")
    if message >= p:
        print(f" ВНИМАНИЕ: m ({message}) не меньше p ({p}). Искажение данных при расшифровке!")
    
    if use_random:
        k = random.randint(1, q - 1)
        print(f"\n Рандомайзер сгенерировал случайное число k: {k}")
    else:
        k = params['k']
        print(f"\n Заданное число k: {k}")
    
    print(f"\n Шифрование")
    ciphertext = encrypt(message, public_key, G, a, p, k)
    print(f"  Шифртекст (R, e): {ciphertext}")
    
    print(f"\n Расшифрование")
    decrypted = decrypt(ciphertext, private_key, a, p)
    print(f"  Расшифрованное сообщение m': {decrypted}")

def run_text_test(params, text, use_random=False):
    print("\n ТЕСТИРОВАНИЕ НА ТЕКСТЕ ")

    p = params['p']
    if p < 36:
         print(f"\n ВНИМАНИЕ: Размер алфавита 36 символов, а модуль p: {p} ")
         print("Из за этого буквы с кодом >= 11 исказятся (x mod p)")
         print("Для работы с текстом используйте простые числа p > 36\n")
    
    a = params['a']
    b = params['b'] % params['p']
    G = params['G']
    q = find_order(G, a, p)
    
    if q is None or q < 3:
        print(f" Точка G не подходит!")
        return
        
    if use_random:
        private_key = random.randint(1, q - 1)
    else:
        private_key = params['Cb']
        
    public_key = multiply_point(private_key, G, a, p)
    numbers = text_to_numbers(text)
    
    print(f"Длина текста: {len(text)}. Преобразовано в {len(numbers)} чисел")
    
    ciphertexts = []
    print(f" Шифрование текста")
    for num in numbers:
        k = random.randint(1, q - 1) if use_random else params['k']
        ciphertexts.append(encrypt(num, public_key, G, a, p, k))
        
    decrypted_numbers = []
    print(f" Расшифрование текста")
    for ct in ciphertexts:
        decrypted_numbers.append(decrypt(ct, private_key, a, p))
        
    decrypted_text = numbers_to_text(decrypted_numbers)
    print(f"\n Расшифрованный текст: {decrypted_text[:50]}")

def manual_input():
    print("\n РУЧНОЙ ВВОД ПАРАМЕТРОВ ")
    params = {}
    print("\nВведите параметры эллиптической кривой:")
    params['a'] = int(input("  a: "))
    params['b'] = int(input("  b: "))
    params['p'] = int(input("  p (простое число): "))
    print("\nВведите базовую точку G:")
    params['G'] = (int(input("  x: ")), int(input("  y: ")))
    params['Cb'] = int(input("\nВведите секретный ключ Cb: "))
    params['k'] = int(input("Введите случайное число k: "))
    params['message'] = int(input("Введите сообщение m: "))
    return params

def random_mode():
    print("\n РЕЖИМ СЛУЧАЙНЫХ ЧИСЕЛ (РАНДОМАЙЗЕР) ")
    params = {}
    print("\nВведите параметры эллиптической кривой:")
    params['a'] = int(input("  a: "))
    params['b'] = int(input("  b: "))
    params['p'] = int(input("  p (простое число): "))
    print("\nВведите базовую точку G:")
    params['G'] = (int(input("  x: ")), int(input("  y: ")))
    params['message'] = int(input("\nВведите сообщение m: "))
    return params

def manual_decrypt():
    print("\n РУЧНОЙ ВВОД ДЛЯ РАСШИФРОВКИ ")
    print("\nВведите параметры эллиптической кривой:")
    a = int(input("  a: "))
    p = int(input("  p (простое число): "))
    
    Cb = int(input("\nВведите секретный ключ Cb: "))
    
    print("\nВведите составные части шифртекста (R, e):")
    Rx = int(input("  R (координата x): "))
    Ry = int(input("  R (координата y): "))
    e = int(input("  Значение e: "))
    
    ciphertext = ((Rx, Ry), e)
    
    print(f"\n Расшифрование")
    decrypted = decrypt(ciphertext, Cb, a, p)
    print(f"  Расшифрованное сообщение m': {decrypted}")

def variant_12():
    """Параметры из 12 го варианта задания"""
    return {
        'a': 4,
        'b': 3,
        'p': 11,
        'G': (0, 5),
        'Cb': 6,
        'k': 4,
        'message': 4
    }

def main():
    while True:
        print("\n ПРОГРАММА ECC ШИФРОВАНИЯ ")
        print("1. Вариант 12 (тестовый)")
        print("2. Ручной ввод параметров")
        print("3. Расшифрование вручную (ввод шифртекста)")
        print("0. Выход")
        
        choice = input("\nВаш выбор: ")
        
        if choice == '1':
            run_test(variant_12(), use_random=False)
        elif choice == '2':
            run_test(manual_input(), use_random=False)
        elif choice == '3':
            manual_decrypt()
        elif choice == '0':
            print("Выход")
            break
            
        again = input("Нажмите Enter для продолжения или введите 0 для выхода: ")
        if again == '0':
            break

if __name__ == "__main__":
    main()
