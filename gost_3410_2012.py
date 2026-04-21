import random
import math

# Проверка на простоту чисел
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    limit = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if n % i == 0: return False
    return True

# Упрощенная хэш-функция
def hash_function(message, p):
    alphabet = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    h = 0
    # Проход по символам с их возведением в квадрат и взятием по модулю p
    for ch in message.upper():
        if ch in alphabet:
            mi = alphabet.index(ch) + 1
            h = (h + mi) ** 2 % p
    return h

# Класс Эллиптической кривой (для ГОСТ 2012)
class EllipticCurve:
    def __init__(self, p, a, b):
        self.p = p # Модуль кривой
        self.a = a % p # Коэффициент a 
        self.b = b % p # Коэффициент b

    # Сложение двух точек P и Q на кривой
    def add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and y1 == (-y2) % self.p:
            return None # Точка уходит в бесконечность
        if x1 == x2 and y1 == y2:
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p # Удвоение
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p # Сложение различных
        x3 = (lam * lam - x1 - x2) % self.p
        y3 = (lam * (x1 - x3) - y1) % self.p
        return (x3, y3)

    # Скалярное умножение точки (Алгоритм double-and-add)
    def mul(self, k, P):
        res = None
        add = P
        while k:
            if k & 1:
                res = self.add(res, add)
            add = self.add(add, add)
            k >>= 1
        return res

    # Вычисление порядка точки G (q) путем сложения точки с собой
    def find_order(self, G, max_iter=200):
        if G is None: return 1
        P = G
        for q in range(1, max_iter + 1):
            if P is None:
                return q # Если P стало точкой O, значит это её порядок
            P = self.add(P, G)
        raise ValueError(f"Порядок точки не найден (лимит {max_iter})")
    
    def is_point_on_curve(self, P):
        """Проверяет, удовлетворяет ли точка P уравнению кривой"""
        if P is None: return True
        x, y = P
        left = (y * y) % self.p
        right = (x * x * x + self.a * x + self.b) % self.p
        return left == right

# Формирование цифровой подписи (Случайное k)
def gost2012_sign(message, curve, G, xA, k=None):
    if not curve.is_point_on_curve(G):
        raise ValueError(f"Точка G {G} не лежит на кривой!")
    
    q = curve.find_order(G)
    print(f"[Авто] Порядок точки G q {q}")

    h = hash_function(message, curve.p) % q
    if h == 0: h = 1 # Хэш должен быть ненулевым
    print(f"[Авто] Хэш h {h}")
    
    max_attempts = 100
    for attempt in range(max_attempts):
        if k is None or attempt > 0:
            k = random.randint(2, q - 1)
            print(f"Попытка {attempt + 1}: сгенерировано k = {k}")
        
        P = curve.mul(k, G) # Находим точку P = k * G
        if P is None:
            print(f"  P None (точка на бесконечности), перегенерируем k...")
            continue
            
        r = P[0] % q
        if r == 0:
            print(f"  r 0, перегенерируем k...") # r не должно быть 0
            continue
        
        s = (k * h + r * xA) % q
        if s == 0:
            print(f"  s 0, перегенерируем k...") # s не должно быть 0
            continue
        
        print(f"  Успех: r {r}, s {s}")
        return r, s, h, q, k
    
    raise ValueError(f"Не удалось сгенерировать корректную подпись за {max_attempts} попыток")

# Формирование цифровой подписи (Фиксированное k)
def gost2012_sign_fixed_k(message, curve, G, xA, k):
    if not curve.is_point_on_curve(G):
        raise ValueError(f"Точка G {G} не лежит на кривой!")
    
    q = curve.find_order(G)
    print(f"[Авто] Порядок точки G q {q}")

    h = hash_function(message, curve.p) % q
    if h == 0: h = 1
    print(f"[Авто] Хэш h {h}")
    
    if not (1 < k < q):
        raise ValueError(f"k должно быть в диапазоне (1, {q}), получено k {k}")
    
    print(f"Используется фиксированное k {k}")
    
    P = curve.mul(k, G)
    if P is None: raise ValueError("P None (точка на бесконечности)")
    
    r = P[0] % q
    if r == 0: raise ValueError(f"r 0, попробуйте другое k")
    
    s = (k * h + r * xA) % q
    if s == 0: raise ValueError(f"s 0, попробуйте другое k")
    
    print(f"  r {r}, s {s}")
    return r, s, h, q

# Проверка подписи по шагам
def gost2012_verify_steps(message, r, s, curve, q, G, YA):
    print("\n" + "=" * 50)
    print("ПРОВЕРКА ПОДПИСИ ГОСТ 2012 (пошагово)")
    print("=" * 50)

    # Шаг 1-2. Проверка интервалов (0, q)
    print(f"Шаг 1: 0 < r < q ? {0 < r < q} ({r} < {q})")
    print(f"Шаг 2: 0 < s < q ? {0 < s < q} ({s} < {q})")
    if not (0 < r < q and 0 < s < q): return False

    # Шаг 3. Хэширование
    h = hash_function(message, curve.p) % q
    if h == 0: h = 1
    print(f"Шаг 3: h hash(message) mod q {h}")

    # Шаг 4. Нахождение обратного элемента хэша
    try:
        h_inv = pow(h, -1, q)
        print(f"Шаг 4: h_inv h^( 1) mod q {h_inv}")
    except:
        print("Шаг 4: Ошибка — h не обратимо")
        return False

    # Шаг 5-6. Вычисление промежуточных значений u1 и u2
    u1 = (s * h_inv) % q
    u2 = (-r * h_inv) % q
    print(f"Шаг 5: u1 s * h_inv mod q {u1}")
    print(f"Шаг 6: u2  r * h_inv mod q {u2}")

    # Шаг 7. Сложение точек
    P1 = curve.mul(u1, G)
    P2 = curve.mul(u2, YA)
    P = curve.add(P1, P2)
    print(f"Шаг 7: P u1*G + u2*YA {P}")

    if P is None:
        print("Шаг 7: P O -> НЕВЕРНА")
        return False

    # Шаг 8. Взятие координаты X результирующей точки
    R = P[0] % q
    print(f"Шаг 8: R xP mod q {R}")

    # Шаг 9. Проверка R == r
    print(f"Шаг 9: R r ? {R} {r} -> {'ДА' if R == r else 'НЕТ'}")
    return R == r

# Основной цикл работы
def main():
    print("Выберите режим работы:")
    print("1   зашифровать")
    print("2   расшифровать")
    print("3   зашифровать текст 1000 символов")
    mode = input("Ваш выбор (1, 2 или 3): ")
    
    if mode not in ['1', '2', '3']:
        print("Неверный режим!")
        return

    print("\n Инициализация параметров ГОСТ Р 34.10 2012 ")
    while True:
        if mode == '3':
            p = int(input("p (модуль поля, простое число > 32): ")) # Ввод модуля
            if p <= 32:
                print("ОШИБКА: p должно быть больше 32!")
                continue
        else:
            p = int(input("p (модуль поля, простое число > 3): ")) # Ввод модуля
            if p <= 3:
                print("ОШИБКА: p должно быть больше 3!")
                continue
                
        if not is_prime(p):
            print(f"ОШИБКА: {p} не является простым числом!")
            continue
        break
    
    a = int(input("a (коэффициент кривой): "))
    b = int(input("b (коэффициент кривой): "))
    Gx = int(input("Gx: ")) # Координата X базовой точки
    Gy = int(input("Gy: ")) # Координата Y базовой точки
    
    curve = EllipticCurve(p, a, b)
    G = (Gx, Gy)
    
    print(f"\n[Проверка кривой]")
    print(f"Кривая: y^2 x^3 + {a}x + {b} mod {p}")
    if curve.is_point_on_curve(G):
        print(f"Точка G{G} лежит на кривой")
    else:
        x, y = G
        left = (y * y) % p
        right = (x * x * x + a * x + b) % p
        print(f"ОШИБКА: Точка G{G} НЕ лежит на кривой!")
        print(f"y^2 mod p {left}")
        print(f"x^3 + a*x + b mod p {right}")
        print("Проверьте правильность введенных параметров!")
        return

    # Режим "зашифровать"
    if mode in ['1', '3']:
        xA = int(input("Секретный ключ xA: ")) # Ввод секретного ключа
        
        print("\nВыберите режим генерации k:")
        print("1. Случайное k (с автоматической перегенерацией)")
        print("2. Фиксированное k (для тестирования)")
        k_mode = input("Ваш выбор (1 или 2): ")
        
        YA = curve.mul(xA, G) # Генерация открытого ключа
        print(f"Открытый ключ YA {YA}")
        
        if k_mode == "2":
            k = int(input("Введите k: "))
            msg = input("Сообщение: ")
            try:
                r, s, h, q = gost2012_sign_fixed_k(msg, curve, G, xA, k)
                print(f"\nХэш h {h}")
                print(f"Итоговая подпись: r {r}, s {s}")
            except ValueError as e:
                print(f"Ошибка: {e}")
                return
        else:
            msg = input("Сообщение: ")
            try:
                r, s, h, q, final_k = gost2012_sign(msg, curve, G, xA)
                print(f"\nХэш h {h}")
                print(f"Итоговая подпись: r {r}, s {s}")
                print(f"Использовано k {final_k}")
            except ValueError as e:
                print(f"Ошибка: {e}")
                return

    # Режим "расшифровать"
    elif mode == '2':
        YAx = int(input("Введите координату x открытого ключа YA: "))
        YAy = int(input("Введите координату y открытого ключа YA: "))
        YA = (YAx, YAy)
        
        msg = input("Сообщение: ")
        r = int(input("Введите координату r подписи: "))
        s = int(input("Введите координату s подписи: "))
        
        q = curve.find_order(G) # Определяем порядок точки для проверки
        valid = gost2012_verify_steps(msg, r, s, curve, q, G, YA)
        print("\n" + "=" * 50)
        print(f"ИТОГ: {'ПОДПИСЬ ВЕРНА' if valid else 'ПОДПИСЬ НЕВЕРНА'}")

if __name__ == "__main__":
    main()
