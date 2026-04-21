def matrix_cipher(text, key_matrix, encrypt=True):
    # Алфавит из 32 русских букв (без Ё)
    alphabet = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

    # Объявляем глобальные переменные
    global _last_max_digits
    global _last_original_length

    # Размерность матрицы
    n = len(key_matrix)

    # Определитель матрицы (для любой размерности)
    def determinant(matrix):
        size = len(matrix)
        if size == 1:
            return matrix[0][0]

        if size == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

        det = 0
        for j in range(size):
            minor = []
            for i in range(1, size):
                row = []
                for k in range(size):
                    if k != j:
                        row.append(matrix[i][k])
                minor.append(row)

            sign = 1 if j % 2 == 0 else -1
            det += sign * matrix[0][j] * determinant(minor)

        return det

    # Транспонирование матрицы
    def transpose(matrix):
        size = len(matrix)
        result = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                result[j][i] = matrix[i][j]
        return result

    # Вычисление присоединенной матрицы (матрицы алгебраических дополнений)
    def adjugate_matrix(matrix):
        size = len(matrix)
        adj = [[0 for _ in range(size)] for _ in range(size)]

        for i in range(size):
            for j in range(size):
                # Создаем минор (без i-й строки и j-го столбца)
                minor_matrix = []
                for r in range(size):
                    if r != i:
                        row = []
                        for c in range(size):
                            if c != j:
                                row.append(matrix[r][c])
                        minor_matrix.append(row)

                # Вычисляем определитель минора
                minor_det = determinant(minor_matrix)

                # Алгебраическое дополнение с учетом знака
                sign = 1 if (i + j) % 2 == 0 else -1
                adj[i][j] = sign * minor_det

        return adj

    # Создание обратной матрицы (в рациональных числах)
    def inverse_matrix(matrix):
        det = determinant(matrix)

import sys

# Алфавит
alp = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Глобальные переменные
_lmd = 0
_lol = 0

def det_val(m):
    sz = len(m)
    if sz == 1:
        return m[0][0]

    if sz == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]

    d = 0
    for j in range(sz):
        mnr = []
        for i in range(1, sz):
            row = []
            for k in range(sz):
                if k != j:
                    row.append(m[i][k])
            mnr.append(row)

        sign = 1 if j % 2 == 0 else -1
        d += sign * m[0][j] * det_val(mnr)

    return d

def trans(m):
    sz = len(m)
    res = [[0 for _ in range(sz)] for _ in range(sz)]
    for i in range(sz):
        for j in range(sz):
            res[j][i] = m[i][j]
    return res

def adj(m):
    sz = len(m)
    res = [[0 for _ in range(sz)] for _ in range(sz)]

    for i in range(sz):
        for j in range(sz):
            mnr_m = []
            for r in range(sz):
                if r != i:
                    row = []
                    for c in range(sz):
                        if c != j:
                            row.append(m[r][c])
                    mnr_m.append(row)

            mnr_d = det_val(mnr_m)
            sign = 1 if (i + j) % 2 == 0 else -1
            res[i][j] = sign * mnr_d

    return res

def inv(m):
    d = det_val(m)

    if d == 0:
        return None, 0

    a = adj(m)
    a_t = trans(a)

    return a_t, d

def mul(m, v):
    sz = len(m)
    res = [0] * sz
    for i in range(sz):
        for j in range(sz):
            res[i] += m[i][j] * v[j]
    return res

def mul_inv(a_m, d, v):
    sz = len(a_m)
    res = [0] * sz

    tmp = [0] * sz
    for i in range(sz):
        for j in range(sz):
            tmp[i] += a_m[i][j] * v[j]

    for i in range(sz):
        val = tmp[i] / d
        if abs(val - round(val)) > 1e-10:
            return None
        res[i] = round(val)

    return res

def proc(t, k, enc=True):
    global _lmd
    global _lol

    n = len(k)

    if enc:
        s = ""
        for c in t:
            if c == ' ':
                s += 'ПРБ'
            elif c == ',':
                s += 'ЗПТ'
            elif c == '.':
                s += 'ТЧК'
            elif c == ';':
                s += 'ТЧКЗПТ'
            elif c == '!':
                s += 'ВСКЛ'
            elif c == '?':
                s += 'ВОПР'
            else:
                s += c.upper()

        orig_len = len(s)

        n_arr = []
        for x in s:
            if x in alp:
                n_arr.append(alp.index(x))
            else:
                n_arr.append(0)

        while len(n_arr) % n != 0:
            n_arr.append(0)

        enc_n = []
        for i in range(0, len(n_arr), n):
            vec = n_arr[i:i + n]
            res_vec = mul(k, vec)
            enc_n.extend(res_vec)

        max_n = max(enc_n)
        max_d = len(str(abs(max_n)))

        f_nums = []
        for x in enc_n:
            f_nums.append(f"{x:0{max_d}d}")

        _lmd = max_d
        _lol = orig_len

        return ' '.join(f_nums)

    else:
        try:
            if ',' in t:
                s_nums = [x.strip() for x in t.split(',')]
            else:
                s_nums = [x for x in t.split()]

            nums = [int(x) for x in s_nums]

            if len(s_nums) > 0:
                _lmd = len(s_nums[0])

        except:
            return "Ошибка формата"

        a_m, d = inv(k)

        if a_m is None:
            return "Ошибка определителя"

        dec_n = []
        for i in range(0, len(nums), n):
            vec = nums[i:i + n]
            if len(vec) < n:
                break

            res_vec = mul_inv(a_m, d, vec)

            if res_vec is None:
                return "Ошибка целочисленности"

            dec_n.extend(res_vec)

        dec_t = ""
        for x in dec_n:
            if 0 <= x < len(alp):
                dec_t += alp[x]
            else:
                dec_t += '?'

        res = dec_t
        res = res.replace('ТЧКЗПТ', ';')
        res = res.replace('ВСКЛ', '!')
        res = res.replace('ВОПР', '?')
        res = res.replace('ПРБ', ' ')
        res = res.replace('ЗПТ', ',')
        res = res.replace('ТЧК', '.')

        if _lol > 0 and len(res) > _lol:
            res = res[:_lol]

        return res

def main():
    print("Матричный шифр")
    print("Используется алфавит из 32 русских букв")

    while True:
        print("\nВыбери:")
        print("1 - Зашифровать")
        print("2 - Расшифровать")
        print("0 - Выход")

        ch = input("Выбор: ").strip()

        if ch == '0':
            print("Завершение работы.")
            break

        if ch == '1' or ch == '2':
            while True:
                try:
                    n = int(input("Размерность матрицы: ").strip())
                    if n < 3:
                        print("Ошибка: размерность должна быть не меньше 3")
                        continue
                    break
                except ValueError:
                    print("Ошибка: введите целое число")

            mat = []
            print(f"\nВведите все элементы матрицы ({n*n} чисел) в одну строку через пробел:")
            
            while True:
                try:
                    inp = input("Ввод: ").strip()
                    els = [int(x) for x in inp.split()]
                    
                    if len(els) != n * n:
                        print(f"Ошибка: ожидалось {n*n} чисел, получено {len(els)}")
                        continue
                        
                    # Разбиваем на строки
                    for i in range(0, len(els), n):
                        mat.append(els[i:i + n])
                    break
                    
                except ValueError:
                    print("Ошибка: введите целые числа")

            d = det_val(mat)
            if d == 0:
                print("\nОшибка! Определитель матрицы равен 0. Матрица необратима.")
                continue

            if ch == '1':
                t = input("\nТекст для шифрования: ").strip()
                if not t:
                    print("Ошибка: пустой ввод")
                    continue

                res = proc(t, mat, enc=True)
                print(f"\nЗашифрованное слово: {res}")

            else:
                t = input("\nВведите числа: ").strip()
                if not t:
                    print("Ошибка: пустой ввод")
                    continue

                res = proc(t, mat, enc=False)
                print(f"\nРасшифрованное слово: {res}")

        else:
            print("Неверный выбор")



if __name__ == "__main__":
    main()