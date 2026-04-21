import random

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def diffie_hellman():
    print("=== ОБМЕН КЛЮЧАМИ ПО ДИФФИ-ХЕЛЛМАНУ ===")
    
    # 0. Исходные параметры n и a
    try:
        n = int(input("Введите большое простое число n: "))
        if not is_prime(n):
            print("Предупреждение: n должно быть простым числом согласно методичке.")
            
        a = int(input(f"Введите число a (1 < a < {n}): "))
        if not (1 < a < n):
            print(f"Ошибка: a должно быть в интервале (1, {n})")
            return
    except ValueError:
        print("Ошибка: введите целое число")
        return

    print(f"\nПубличные параметры: n = {n}, a = {a}")

    # 1-2. Определение секретных ключей KA и KB
    # В методичке KA и KB - это секретные ключи (часто обозначаются xA, xB)
    # Выбираются из интервала [2, n-1]
    
    use_random = input("Сгенерировать секретные ключи автоматически? (y/n): ").lower() == 'y'
    
    if use_random:
        priv_A = random.randint(2, n - 1)
        priv_B = random.randint(2, n - 1)
        print(f"Секретный ключ А (KA): {priv_A}")
        print(f"Секретный ключ B (KB): {priv_B}")
    else:
        priv_A = int(input("Введите секретный ключ А (KA): "))
        priv_B = int(input("Введите секретный ключ B (KB): "))

    # 3. Вычислить открытые ключи YA и YB
    # Y = a^K mod n
    YA = pow(a, priv_A, n)
    YB = pow(a, priv_B, n)
    
    print(f"\n3. Вычисленные открытые ключи:")
    print(f"YA = {a}^{priv_A} mod {n} = {YA}")
    print(f"YB = {a}^{priv_B} mod {n} = {YB}")

    # 4. Обмен ключами (имитация)
    print("\n4. Пользователи обмениваются открытыми ключами YA и YB...")

    # 5. Независимо определить общий секретный ключ K
    # KA_final = YB^KA mod n
    # KB_final = YA^KB mod n
    K_A = pow(YB, priv_A, n)
    K_B = pow(YA, priv_B, n)

    print(f"\n5. Определение общего секретного ключа K:")
    print(f"Для A: K = YB^KA mod n = {YB}^{priv_A} mod {n} = {K_A}")
    print(f"Для B: K = YA^KB mod n = {YA}^{priv_B} mod {n} = {K_B}")

    # Проверка
    print(f"\nПроверка: KA = KB = K")
    if K_A == K_B:
        K = K_A
        print(f"Успех! Общий секретный ключ K = {K}")
        
        # Специальная проверка по вашему требованию
        if K == 1:
            print("ВНИМАНИЕ: Общий ключ равен 1. Это небезопасно!")
        if K == YA or K == YB:
            print(f"ВНИМАНИЕ: Общий ключ совпадает с одним из открытых ключей (YA или YB)!")
            
        print("Задача решена.")
    else:
        print("Ошибка! Ключи не совпадают.")

if __name__ == "__main__":
    diffie_hellman()
