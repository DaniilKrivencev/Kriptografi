# -*- coding: utf-8 -*-
"""
ГОСТ 28147-89 (Магма)
Режим простой замены (ECB)
"""

# Узлы замены (S-блоки) по ГОСТ Р 34.12-2015 (Магма)
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

class Gost28147_89:
    def __init__(self, key_bytes: bytes):
        if len(key_bytes) != 32:
            raise ValueError("Ключ должен быть ровно 32 байта (256 бит)")
        
        # Разделение ключа на 8 частей по 32 бита (little-endian)
        self.key_parts = []
        for i in range(8):
            part = int.from_bytes(key_bytes[i*4:(i+1)*4], byteorder='little')
            self.key_parts.append(part)
            
        # Формируем итерационные ключи
        self.enc_keys = []
        # Шаги 1-24: K1..K8, K1..K8, K1..K8 (прямой порядок)
        for _ in range(3):
            self.enc_keys.extend(self.key_parts)
        # Шаги 25-32: K8..K1 (обратный порядок)
        self.enc_keys.extend(self.key_parts[::-1])
        
        self.dec_keys = self.enc_keys[::-1]

    def _t(self, x):
        """Нелинейное преобразование t (S-блоки)"""
        y = 0
        for i in range(8):
            nibble = (x >> (4 * i)) & 0xF
            y |= PI[i][nibble] << (4 * i)
        return y

    def _g(self, k, a):
        """Функция раунда"""
        sum_mod = (a + k) & MASK32
        res_t = self._t(sum_mod)
        # Циклический сдвиг на 11 бит влево
        return ((res_t << 11) | (res_t >> 21)) & MASK32

    def _process_block(self, block: bytes, keys) -> bytes:
        if len(block) != 8:
            raise ValueError("Блок должен быть 8 байт (64 бита)")
            
        a0 = int.from_bytes(block[:4], byteorder='little')
        a1 = int.from_bytes(block[4:], byteorder='little')
        
        for i in range(32):
            k = keys[i]
            if i < 31:
                a1, a0 = a0, self._g(k, a0) ^ a1
            else:
                a1 = self._g(k, a0) ^ a1  # В последнем раунде нет перестановки
                
        # Формируем результат также в little-endian
        return a0.to_bytes(4, byteorder='little') + a1.to_bytes(4, byteorder='little')

    def encrypt_block(self, block: bytes) -> bytes:
        return self._process_block(block, self.enc_keys)

    def decrypt_block(self, block: bytes) -> bytes:
        return self._process_block(block, self.dec_keys)
        
    def encrypt_ecb(self, data: bytes) -> bytes:
        """Режим простой замены (ECB)"""
        # Padding (дополнение до размера блока)
        padding_len = 8 - (len(data) % 8)
        data = data + bytes([padding_len] * padding_len)
        
        result = b''
        for i in range(0, len(data), 8):
            result += self.encrypt_block(data[i:i+8])
        return result

    def decrypt_ecb(self, data: bytes) -> bytes:
        """Дешифрование в режиме простой замены (ECB)"""
        if len(data) % 8 != 0:
            raise ValueError("Размер зашифрованных данных должен быть кратен 8")
            
        result = b''
        for i in range(0, len(data), 8):
            result += self.decrypt_block(data[i:i+8])
            
        # Удаляем padding
        padding_len = result[-1]
        return result[:-padding_len]

if __name__ == "__main__":
    import binascii
    
    print("=== ГОСТ 28147-89 (Магма) - Режим простой замены (ECB) ===\n")
    
    # Ключ по ГОСТ Р 34.12-2015 (256 бит)
    # Тестовый ключ "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    test_key_hex = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
    test_key = bytes.fromhex(test_key_hex)
    
    cipher = Gost28147_89(test_key)
    
    # Тестирование на тексте 1000+ символов
    # Создаем длинный текст:
    long_text = "Это тестовое сообщение для алгоритма ГОСТ 28147-89 в режиме простой замены (ECB). " * 20
    print(f"Длина сгенерированного открытого текста: {len(long_text)} символов.")
    
    plaintext_bytes = long_text.encode('utf-8')
    print(f"Размер в байтах: {len(plaintext_bytes)} байт.\n")
    
    # Шифруем
    ciphertext = cipher.encrypt_ecb(plaintext_bytes)
    print("Шифрование выполнено успешно.")
    print(f"Первые 32 байта шифртекста (hex): {binascii.hexlify(ciphertext[:32]).decode('utf-8')}")
    
    # Расшифровываем
    decrypted_bytes = cipher.decrypt_ecb(ciphertext)
    decrypted_text = decrypted_bytes.decode('utf-8')
    print("\nДешифрование выполнено успешно.")
    
    # Проверка
    if decrypted_text == long_text:
        print("\n✅ УСПЕХ: Исходный и расшифрованный тексты полностью совпадают!")
    else:
        print("\n❌ ОШИБКА: Тексты не совпадают.")
