import sys

ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя"

class LCG:
    def __init__(self, a, c, m, t0):
        self.a = a
        self.c = c
        self.m = m
        self.t = t0

    def next(self):
        self.t = (self.a * self.t + self.c) % self.m
        return self.t

def format_text(text):
    text = text.lower().replace('ё', 'е').replace(' ', '')
    return "".join([ch for ch in text if ch in ALPHABET])

def encrypt_shannon(text, a, c, t0):
    text = format_text(text)
    m = len(ALPHABET)
    rng = LCG(a, c, m, t0)
    
    res = ""
    for char in text:
        idx = ALPHABET.index(char)
        k = rng.next()
        res += ALPHABET[(idx + k) % m]
    return res

def decrypt_shannon(text, a, c, t0):
    text = format_text(text)
    m = len(ALPHABET)
    rng = LCG(a, c, m, t0)
    
    res = ""
    for char in text:
        idx = ALPHABET.index(char)
        k = rng.next()
        res += ALPHABET[(idx - k + m) % m]
    return res

if __name__ == "__main__":
    print("Одноразовый блокнот К.Шеннона")
    msg = input("Введите текст: ")
    a = int(input("Введите множитель a: "))
    c = int(input("Введите приращение c: "))
    t0 = int(input("Введите начальное значение T0: "))
    
    action = input("Что сделать? (1 зашифровать, 2 расшифровать): ")
    
    if action == "1":
        enc = encrypt_shannon(msg, a, c, t0)
        print("Зашифрованный текст:", enc)
    elif action == "2":
        dec = decrypt_shannon(msg, a, c, t0)
        print("Расшифрованный текст:", dec)
    else:
        print("Неизвестная команда")
