import random

def mod_inverse(k, p):
    """Модульная инверсия числа"""
    if k == 0:
        raise ZeroDivisionError('Деление на ноль в кольце вычетов.')
    return pow(k, p - 2, p)

def ec_add(p1, p2, a, p):
    """Сложение двух точек на эллиптической кривой y^2 = x^3 + a*x + b mod p"""
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    
    if x1 == x2 and y1 != y2:
        return None # Точка в бесконечности (O)
        
    if x1 == x2:
        # Касательная (удвоение точки)
        lam = ((3 * x1 * x1 + a) * mod_inverse(2 * y1, p)) % p
    else:
        # Хорда
        lam = ((y2 - y1) * mod_inverse(x2 - x1, p)) % p
        
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, pt, a, p):
    """Умножение точки на скаляр: k*G"""
    R = None
    addend = pt
    while k > 0:
        if k & 1:
            R = ec_add(R, addend, a, p)
        addend = ec_add(addend, addend, a, p)
        k >>= 1
    return R

def main():
    print("--- 23. ECC - С ИСПОЛЬЗОВАНИЕМ АБСЦИССЫ ТОЧКИ ---")
    
    print("Параметры кривой E_p(a,b): y^2 = x^3 + a*x + b (mod p)")
    try:
        p = int(input("Введите p (простое число, напр. 211): "))
        a = int(input("Введите a (напр. 0): "))
        b = int(input("Введите b (напр. -4): "))
        
        print("\nБазовая точка G(x, y)")
        gx = int(input("Введите абсциссу базовой точки G (x, напр. 2): "))
        gy = int(input("Введите ординату базовой точки G (y, напр. 2): "))
        G = (gx, gy)
        
        q = int(input("\nВведите порядок подгруппы q (напр. 241): "))
        
        print("\n--- Генерация ключей получателя (Боба) ---")
        c_B = int(input(f"Введите секретный ключ получателя c_B (0 < c_B < {q}, напр. 15): "))
        D_B = ec_mul(c_B, G, a, p)
        print(f"Открытый ключ получателя D_B вычислен: {D_B}")
        
        print("\n--- Отправитель (Алиса) ---")
        m = int(input(f"Введите сообщение m (число m < {p}, напр. 100): "))
        k = int(input(f"Введите случайное число k (0 < k < {q}, напр. 12): "))
        
        print("\n[Шифрование]")
        R = ec_mul(k, G, a, p)
        P = ec_mul(k, D_B, a, p)
        
        if P is None:
            print("Ошибка: Точка P в бесконечности")
            return
            
        x, y = P
        print(f"Вычислено R = [k]G = {R}")
        print(f"Вычислено P = [k]D_B = {P}, абсцисса x = {x}")
        
        e = (m * x) % p
        print(f"Сформирован шифртекст (R, e): {R}, {e}")
        
        print("\n--- Получатель (Боб) ---")
        print("[Расшифрование]")
        Q = ec_mul(c_B, R, a, p)
        
        if Q is None:
            print("Ошибка: Точка Q в бесконечности")
            return
            
        x_dec, y_dec = Q
        print(f"Боб вычислил Q = [c_B]R = {Q}, абсцисса x = {x_dec}")
        
        m_dec = (e * mod_inverse(x_dec, p)) % p
        print(f"Расшифрованное сообщение m': {m_dec}")
        
        if m == m_dec:
            print("\n✅ Успех: Первоначальное сообщение совпадает с расшифрованным!")
        else:
            print("\n❌ Ошибка: Расшифрованное сообщение не совпадает!")

    except ValueError:
        print("Пожалуйста, вводите только целые числа!")
    except Exception as ex:
        print(f"Произошла ошибка при вычислениях: {ex}")

if __name__ == '__main__':
    main()
