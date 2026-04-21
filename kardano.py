import random
import math

alphabet_ru32 = "абвгдежзийклмнопрстуфхцчшщьыэюя"

def create_grille(size, seed_val):
    if size % 2 != 0:
        size += 1
    
    n = size // 2
    random.seed(seed_val)
    holes = [[0] * size for _ in range(size)]
    
    for r in range(n):
        for c in range(n):
            choice = random.randint(0, 3)
            
            if choice == 0:
                holes[r][c] = 1
            elif choice == 1:
                holes[c][size-1-r] = 1
            elif choice == 2:
                holes[size-1-r][size-1-c] = 1
            else:
                holes[size-1-c][r] = 1
                
    return holes

def encrypt(message, key="secret"):
    text = message.replace(" ", "").lower()
    l = len(text)
    
    size = 2
    while size * size < l:
        size += 2
        
    padding_len = size * size - l
    pad = "".join(random.choice(alphabet_ru32) for _ in range(padding_len))
    full_text = text + pad
    
    grille = create_grille(size, key)
    grid = [['' for _ in range(size)] for _ in range(size)]
    current_grille = [row[:] for row in grille]
    text_idx = 0
    
    for _ in range(4):
        for r in range(size):
            for c in range(size):
                if current_grille[r][c] == 1:
                    if text_idx < len(full_text):
                        grid[r][c] = full_text[text_idx]
                        text_idx += 1
        
        # Rotate 90 deg positive
        new_grille = [[0] * size for _ in range(size)]
        for r in range(size):
            for c in range(size):
                if current_grille[r][c] == 1:
                    new_grille[c][size-1-r] = 1
        current_grille = new_grille
        
    res = ""
    for r in range(size):
        for c in range(size):
            res += grid[r][c]
            
    return " ".join(res[i:i+5] for i in range(0, len(res), 5))

def decrypt(ciphertext, key="secret"):
    clean_text = ciphertext.replace(" ", "")
    l = len(clean_text)
    size = int(math.sqrt(l))
    
    if size * size != l or size % 2 != 0:
        return "Ошибка: Длина текста не соответствует квадрату четного размера (возможно, текст обрезан или добавлен мусор)."
        
    grille = create_grille(size, key)
    
    grid = [['' for _ in range(size)] for _ in range(size)]
    idx = 0
    for r in range(size):
        for c in range(size):
            grid[r][c] = clean_text[idx]
            idx += 1
            
    decrypted = ""
    current_grille = [row[:] for row in grille]
    
    for _ in range(4):
        for r in range(size):
            for c in range(size):
                if current_grille[r][c] == 1:
                    decrypted += grid[r][c]
                    
        new_grille = [[0] * size for _ in range(size)]
        for r in range(size):
            for c in range(size):
                if current_grille[r][c] == 1:
                    new_grille[c][size-1-r] = 1
        current_grille = new_grille
            
    return decrypted

if __name__ == "__main__":
    t = input("Введите фразу для шифрования: ")
    k = input("Введите ключ (слово или число): ")
    
    print(f"\nТекст: {t}")
    print(f"Ключ: {k}")
    
    enc = encrypt(t, k)
    print(f"Зашифровано: {enc}")
    
    dec = decrypt(enc, k)
    print(f"Расшифровано: {dec}")
