# -*- coding: utf-8 -*-
"""
Преобразование t алгоритма Магма (ГОСТ Р 34.12-2015)
А.2.1 Преобразование t

Примеры из стандарта:
t(fdb97531) = 2a196f34,
t(2a196f34) = ebd9f03a,
t(ebd9f03a) = b039bb3d,
t(b039bb3d) = 68695433.
"""

def magma_t_transform(hex_input: str) -> str:
    """
    Преобразование t алгоритма Магма.
    
    32-битное слово разбивается на 8 групп по 4 бита,
    каждая проходит через свой S-блок, результаты объединяются.
    
    Аргументы:
        hex_input: строка с 8 шестнадцатеричными символами (например, "fdb97531")
    
    Возвращает:
        Строку с 8 шестнадцатеричными символами - результат преобразования
    """
    # S-блоки из ГОСТ Р 34.12-2015 (Магма)
    s_boxes = [
        [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],   # S1
        [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],  # S2
        [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],  # S3
        [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],  # S4
        [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],  # S5
        [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],  # S6
        [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],  # S7
        [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]   # S8
    ]
    
    # Проверяем и подготавливаем входные данные
    hex_input = hex_input.strip().replace(" ", "").lower()
    
    if len(hex_input) != 8:
        raise ValueError(f"Нужно ввести 8 шестнадцатеричных символов, получено {len(hex_input)}: '{hex_input}'")
    
    if not all(c in '0123456789abcdef' for c in hex_input):
        raise ValueError(f"Некорректные символы в шестнадцатеричном числе: '{hex_input}'")
    
    # Преобразуем строку в 32-битное число
    value_32 = int(hex_input, 16)
    
    result = 0
    
    # Обрабатываем 8 групп по 4 бита (младшие 4 бита - группа 0)
    for i in range(8):
        # Извлекаем 4-битную подпоследовательность
        # Группа 0: биты 0-3 (младшие)
        # Группа 1: биты 4-7
        # ...
        # Группа 7: биты 28-31 (старшие)
        sub_value = (value_32 >> (4 * i)) & 0xF
        
        # Применяем соответствующий S-блок
        s_box = s_boxes[i]
        substituted = s_box[sub_value]
        
        # Помещаем результат в соответствующую позицию
        result |= (substituted << (4 * i))
    
    # Приводим к 32-битному виду и преобразуем обратно в hex строку
    result = result & 0xFFFFFFFF
    return f"{result:08x}"

def magma_t_with_shift(hex_input: str) -> str:
    """
    Преобразование t с циклическим сдвигом на 11 бит влево.
    То же самое, что и magma_t_transform, но с дополнительным сдвигом.
    
    Аргументы:
        hex_input: строка с 8 шестнадцатеричными символами
    
    Возвращает:
        Строку с 8 шестнадцатеричными символами - результат преобразования со сдвигом
    """
    # Сначала применяем преобразование t
    t_result = int(magma_t_transform(hex_input), 16)
    
    # Циклический сдвиг влево на 11 бит
    high_bits = t_result >> (32 - 11)
    shifted = (t_result << 11) & 0xFFFFFFFF
    result = (shifted | high_bits) & 0xFFFFFFFF
    
    return f"{result:08x}"

def test_magma_t():
    """Тестирование преобразования t на примерах из ГОСТ"""
    print("Тестирование преобразования t из ГОСТ Р 34.12-2015 (А.2.1)")
    print("=" * 60)
    
    # Примеры из стандарта
    test_cases = [
        ("fdb97531", "2a196f34"),
        ("2a196f34", "ebd9f03a"),
        ("ebd9f03a", "b039bb3d"),
        ("b039bb3d", "68695433")
    ]
    
    for input_hex, expected_hex in test_cases:
        try:
            result = magma_t_transform(input_hex)
            print(f"t({input_hex}) = {result}")
            print(f"Ожидается:   {expected_hex}")
            print(f"Совпадение:  {'✓' if result == expected_hex else '✗'}")
            print("-" * 40)
        except ValueError as e:
            print(f"Ошибка для входного значения {input_hex}: {e}")
            print("-" * 40)
    
    # Дополнительные тесты со сдвигом
    print("\nТестирование преобразования t со сдвигом на 11 бит:")
    print("=" * 60)
    
    test_with_shift = [
        ("00000001", magma_t_with_shift("00000001")),
        ("ffffffff", magma_t_with_shift("ffffffff")),
        ("12345678", magma_t_with_shift("12345678")),
    ]
    
    for input_hex, result in test_with_shift:
        print(f"t_shift({input_hex}) = {result}")

def interactive_mode():
    """Интерактивный режим для преобразования t"""
    print("=" * 60)
    print("ПРЕОБРАЗОВАНИЕ t алгоритма Магма (ГОСТ Р 34.12-2015)")
    print("=" * 60)
    print("Примеры из стандарта (А.2.1):")
    print("  t(fdb97531) = 2a196f34")
    print("  t(2a196f34) = ebd9f03a")
    print("  t(ebd9f03a) = b039bb3d")
    print("  t(b039bb3d) = 68695433")
    print("=" * 60)
    
    while True:
        print("\nВыберите режим:")
        print("  1. Просто преобразование t (как в А.2.1)")
        
        choice = input("Ваш выбор: ").strip()
        
        if choice == "0":
            print("Выход из программы.")
            break
        
        elif choice == "1":
            hex_input = input("Введите 8 шестнадцатеричных символов (например, fdb97531): ").strip()
            try:
                result = magma_t_transform(hex_input)
                print(f"\nРезультат преобразования t:")
                print(f"t({hex_input}) = {result}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        
        elif choice == "2":
            hex_input = input("Введите 8 шестнадцатеричных символов (например, fdb97531): ").strip()
            try:
                result = magma_t_with_shift(hex_input)
                print(f"\nРезультат преобразования t со сдвигом:")
                print(f"t_shift({hex_input}) = {result}")
                
                # Покажем промежуточные шаги
                t_result = magma_t_transform(hex_input)
                print(f"  t({hex_input}) = {t_result}")
                t_val = int(t_result, 16)
                print(f"  В двоичном: {t_val:032b}")
                print(f"  Сдвиг влево на 11 бит...")
                result_val = int(result, 16)
                print(f"  Результат: {result_val:032b}")
                print(f"  В hex: {result}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        
        elif choice == "3":
            test_magma_t()
        
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    # Можно запустить в интерактивном режиме
    interactive_mode()
    
