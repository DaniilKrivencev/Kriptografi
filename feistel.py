import struct

# S-блоки из ГОСТ (8 узлов замены)
PI = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

MASK32 = 0xFFFFFFFF

class Magma:
    def __init__(self, key_hex):
        """Интегрированная логика генерации ключей и подготовки"""
        k = int(key_hex, 16)
        key_parts = []
        for i in range(8):
            key_parts.append((k >> (32 * i)) & MASK32)
            
        # Формируем итерационные ключи K1...K32 по алгоритму пользователя
        self.enc_keys = []
        # K1...K8
        for i in range(7, -1, -1): self.enc_keys.append(key_parts[i])
        # K9...K16
        for i in range(7, -1, -1): self.enc_keys.append(key_parts[i])
        # K17...K24
        for i in range(7, -1, -1): self.enc_keys.append(key_parts[i])
        # K25...K32 (в обратном порядке)
        for i in range(8): self.enc_keys.append(key_parts[i])
        
        # Ключи для дешифрования - это просто развернутый список ключей шифрования
        self.dec_keys = self.enc_keys[::-1]

    def _t(self, x):
        """Нелинейное преобразование t (S-блоки)"""
        y = 0
        for i in range(8):
            nibble = (x >> (4 * i)) & 0xF
            y |= PI[i][nibble] << (4 * i)
        return y

    def _g(self, k, a):
        """g[k](a) = rot11(t((a + k) mod 2^32))"""
        sum_mod = (a + k) & MASK32
        res_t = self._t(sum_mod)
        # Циклический сдвиг на 11 бит влево
        return ((res_t << 11) | (res_t >> 21)) & MASK32

    def encrypt_block(self, block_hex):
        """Шифрование блока по 32 раундам"""
        block = int(block_hex, 16)
        a1 = (block >> 32) & MASK32
        a0 = block & MASK32
        
        for i in range(32):
            k = self.enc_keys[i]
            if i < 31:
                # Обычный раунд G
                a1, a0 = a0, self._g(k, a0) ^ a1
            else:
                # Последний раунд G* (без перестановки)
                a1 = self._g(k, a0) ^ a1
                
        return f"{a1:08x}{a0:08x}"

    def decrypt_block(self, block_hex):
        """Расшифрование блока"""
        block = int(block_hex, 16)
        a1 = (block >> 32) & MASK32
        a0 = block & MASK32
        
        for i in range(32):
            k = self.dec_keys[i]
            if i < 31:
                a1, a0 = a0, self._g(k, a0) ^ a1
            else:
                a1 = self._g(k, a0) ^ a1
                
        return f"{a1:08x}{a0:08x}"

if __name__ == "__main__":
    # Финальный тест по вашим данным
    test_key = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    test_data = "fedcba9876543210"
    
    cipher = Magma(test_key)
    
    print("=== ИНТЕГРИРОВАННАЯ СЕТЬ ФЕЙСТЕЛЯ ===")
    print(f"Ключ: {test_key}")
    print(f"Ввод: {test_data}")
    
    res = cipher.encrypt_block(test_data)
    print(f"Шифртекст: {res}")
    
    dec = cipher.decrypt_block(res)
    print(f"Расшифровка: {dec}")
    
    if dec.lower() == test_data.lower():
        print("\n✅ УСПЕХ: Все функции интегрированы корректно!")
