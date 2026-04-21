import math

class RouteShuffle:
    @staticmethod
    def encrypt(text, rows, cols):
        # Заполнение матрицы змейкой (маршрут: по строкам)
        matrix = [['' for _ in range(cols)] for _ in range(rows)]
        text = text.replace(" ", "")
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx < len(text):
                    matrix[r][c] = text[idx]
                    idx += 1
                else:
                    matrix[r][c] = 'х' # заполнитель
        
        # Чтение по столбцам
        result = ""
        for c in range(cols):
            for r in range(rows):
                result += matrix[r][c]
        return result

    @staticmethod
    def decrypt(ciphertext, rows, cols):
        matrix = [['' for _ in range(cols)] for _ in range(rows)]
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx < len(ciphertext):
                    matrix[r][c] = ciphertext[idx]
                    idx += 1
        
        result = ""
        for r in range(rows):
            for c in range(cols):
                result += matrix[r][c]
        return result.rstrip('х')

def main():
    print("Маршрутная перестановка")
    print("1. Шифрование")
    print("2. Расшифрование")
    choice = input("Выбор: ")
    
    text = input("Введите текст: ")
    rows = int(input("Введите количество строк: "))
    cols = int(input("Введите количество столбцов: "))
    
    cipher = RouteShuffle()
    if choice == "1":
        print("Результат:", cipher.encrypt(text, rows, cols))
    else:
        print("Результат:", cipher.decrypt(text, rows, cols))

if __name__ == "__main__":
    main()
