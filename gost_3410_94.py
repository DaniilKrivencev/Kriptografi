import random
import math

# Проверка на простоту (Алгоритм перебора делителей до корня из n)
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    limit = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if n % i == 0: return False
    return True

# Упрощенная хэш-функция (квадратичная свертка)
def hash_function(message, p):
    alphabet = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    h = 0
    # Проходимся по всем символам сообщения и считаем хэш
    for ch in message.upper():
        if ch in alphabet:
            mi = alphabet.index(ch) + 1
            h = (h + mi) ** 2 % p
    return h

# Функция поиска подходящих значений открытого параметра 'a'
def generate_a_list(p, q, count=8):
    print(f"\n[Генерация параметров a]")
    print(f"Ищем a такие, что a^{q} mod {p} 1")
    
    a_list = []
    exp = (p - 1) // q
    
    # Пытаемся найти нужное количество a, перебирая d по порядку (не случайно),
    # чтобы список значений всегда был одинаковым для одних и тех же p и q.
    for d in range(2, p - 1):
        a = pow(d, exp, p)
        if a != 1 and a not in a_list:
            a_list.append(a)
            if len(a_list) >= count:
                break
    
    return sorted(a_list)

# Процесс генерации подписи для сообщения (Формирование)
def gost94_sign(message, p, q, a, x):
    h = hash_function(message, p) % q
    if h == 0:
        h = 1 # Значение хэша не должно быть нулевым
    
    max_attempts = 100
    for attempt in range(max_attempts):
        k = random.randint(2, q - 1) # Выбираем случайное k
        print(f"Попытка {attempt + 1}: сгенерировано k = {k}")
        
        r = pow(a, k, p) % q
        if r == 0:
            print(f"  r 0, перегенерируем k...") # r не должно равняться 0
            continue
        
        s = (x * r + k * h) % q
        if s == 0:
            print(f"  s 0, перегенерируем k...") # s не должно равняться 0
            continue
        
        print(f"  Успех r {r}, s {s}")
        return r, s, h, k
    
    raise ValueError(f"Не удалось сгенерировать подпись за {max_attempts} попыток")

# Пошаговая проверка подписанного сообщения
def gost94_verify_steps(message, r, s, p, q, a, y):
    print("\n" + "=" * 50)
    print("ПРОВЕРКА ПОДПИСИ ГОСТ 94 (пошагово)")
    print("=" * 50)

    # Проверяем диапазоны r и s
    print(f"Шаг 1: 0 < r < q ? {0 < r < q} ({r} < {q})")
    print(f"Шаг 2: 0 < s < q ? {0 < s < q} ({s} < {q})")
    if not (0 < r < q and 0 < s < q): return False

    # Считаем хэш от полученного сообщения
    h = hash_function(message, p) % q
    if h == 0: h = 1
    print(f"Шаг 3: h hash(message) mod q {h}")

    v = pow(h, q - 2, q) # Вычисляем обратный элемент
    print(f"Шаг 4: v h^(q 2) mod q {v}")

    # Высчитываем промежуточные значения z1 и z2
    z1 = (s * v) % q
    z2 = ((q - r) * v) % q
    print(f"Шаг 5: z1 s*v mod q {z1}")
    print(f"Шаг 6: z2 (q r)*v mod q {z2}")

    u = (pow(a, z1, p) * pow(y, z2, p)) % p % q
    print(f"Шаг 7: u (a^z1 * y^z2 mod p) mod q {u}")

    # Сравниваем вычисленное u с r
    print(f"Шаг 8: u r ? {u} {r} -> {'ДА' if u == r else 'НЕТ'}")
    return u == r

# Основной цикл программы
def main():
    print("Выберите режим работы:")
    print("1   зашифровать")
    print("2   расшифровать")
    mode = input("Ваш выбор (1 или 2): ")
    
    if mode not in ['1', '2']:
        print("Неверный режим!")
        return

    print("\n Инициализация параметров ГОСТ Р 34.10 94 ")
    # Ввод числа p
    while True:
        p = int(input("p (простое число > 32): "))
        if p <= 32:
            print("ОШИБКА: p должно быть больше 32!")
            continue
        if not is_prime(p):
            print(f"ОШИБКА: {p} не является простым числом!")
            continue
        break
    
    # Ввод числа q
    while True:
        q = int(input("q (простой делитель p 1): "))
        if not is_prime(q):
            print(f"ОШИБКА: {q} не является простым числом!")
            continue
        if (p - 1) % q != 0: # Проверка что q делитель p-1
            print(f"ОШИБКА: q {q} должен делить p 1 {p-1}!")
            continue
        break
    
    # Выбор параметра 'a'
    a_list = generate_a_list(p, q, count=8)
    if len(a_list) == 0:
        print("ОШИБКА: Не удалось сгенерировать подходящие a!")
        return
    
    print("\nВыберите параметр a из списка:")
    for i, val in enumerate(a_list):
        print(f"{i+1}. a = {val}")
    
    a_idx = int(input("Ваш выбор (1-{}): ".format(len(a_list)))) - 1
    if a_idx < 0 or a_idx >= len(a_list):
        print("ОШИБКА: Неверный выбор!")
        return
    a = a_list[a_idx]
    
    # Режим "зашифровать"
    if mode == '1':
        print(f"\nДопустимый диапазон: 1 < x < {q}")
        x = int(input("Введите секретный ключ x: ")) # Секретный ключ x
        if not (1 < x < q):
            print(f"ОШИБКА: x должен быть в диапазоне (1, {q})")
            return
            
        y = pow(a, x, p) # Вычисление открытого ключа y
        print(f"Открытый ключ y = {y}")
        
        msg = input("Сообщение: ")
        try:
            r, s, h, k = gost94_sign(msg, p, q, a, x)
            print(f"\nХэш h {h}")
            print(f"Итоговая подпись: r {r}, s {s}")
            print(f"Использовано k {k}")
        except ValueError as e:
            print(f"Ошибка: {e}")
            
    # Режим "расшифровать"
    elif mode == '2':
        y = int(input("Введите открытый ключ y: "))
        msg = input("Сообщение: ")
        r = int(input("Введите r: "))
        s = int(input("Введите s: "))
        
        valid = gost94_verify_steps(msg, r, s, p, q, a, y)
        print("\n" + "=" * 50)
        print(f"ИТОГ: {'ПОДПИСЬ ВЕРНА' if valid else 'ПОДПИСЬ НЕВЕРНА'}")

if __name__ == "__main__":
    main()
