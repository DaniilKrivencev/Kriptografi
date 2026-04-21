import math

class MagmaCipher:
    def __init__(self):
        self.pi = [
            [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
            [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
            [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
            [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
            [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
            [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
            [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
            [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
        ]
        self.MASK32 = 0xFFFFFFFF
        self.round_keys = []

    def t_transform(self, x):
        result = 0
        for i in range(8):
            nibble = (x >> (4 * i)) & 0xF
            result |= self.pi[i][nibble] << (4 * i)
        return result & self.MASK32

    def rot11(self, x):
        return ((x << 11) | (x >> 21)) & self.MASK32

    def g(self, k, a):
        s = (a + k) & self.MASK32
        return self.rot11(self.t_transform(s))

    def encrypt_block(self, block):
        left = (block >> 32) & self.MASK32
        right = block & self.MASK32
        for i in range(31):
            left, right = right, self.g(self.round_keys[i], right) ^ left
        left, right = self.g(self.round_keys[31], right) ^ left, right
        return (left << 32) | right

    def decrypt_block(self, block):
        left = (block >> 32) & self.MASK32
        right = block & self.MASK32
        for i in range(31, 0, -1):
            left, right = right, self.g(self.round_keys[i], right) ^ left
        left, right = self.g(self.round_keys[0], right) ^ left, right
        return (left << 32) | right

    def set_key(self, key_hex):
        # В ГОСТ ключ читается слева направо: K1 K2 ... K8
        # Но при расчетах часто используют Little Endian для слов.
        # Для соответствия вектору A.7:
        # P = 92def06b 3c130a59, K = ffeeddcc...
        # K1 = ffeeddcc, K2 = bbaa9988 ... K8 = fcfdfeff
        K = []
        for i in range(8):
            K.append(int(key_hex[i * 8:(i + 1) * 8], 16))
        
        self.round_keys = []
        # K1...K8
        for i in range(8): self.round_keys.append(K[i])
        # K1...K8
        for i in range(8): self.round_keys.append(K[i])
        # K1...K8
        for i in range(8): self.round_keys.append(K[i])
        # K8...K1
        for i in range(7, -1, -1): self.round_keys.append(K[i])

class GOST_34_13_Modes:
    def __init__(self, magma_cipher):
        self.magma = magma_cipher
        self.n = 64

    def _xor(self, a_hex, b_hex):
        a = int(a_hex, 16)
        b = int(b_hex, 16)
        length = max(len(a_hex), len(b_hex))
        return f"{(a ^ b):0{length}x}"

    def ctr_process(self, text_hex, key_hex, iv_hex, mode="encrypt"):
        self.magma.set_key(key_hex)
        # В CTR счетчик: IV (32 бит) || 00000000
        ctr_val = int(iv_hex + "00000000", 16)
        
        blocks = [text_hex[i:i + 16] for i in range(0, len(text_hex), 16)]
        processed = []
        
        prefix = "C" if mode == "encrypt" else "P"
        
        for i, block in enumerate(blocks):
            gamma_int = self.magma.encrypt_block(ctr_val)
            gamma_hex = f"{gamma_int:016x}"
            
            res_hex = self._xor(block, gamma_hex[:len(block)])
            processed.append(res_hex)
            
            print(f"{prefix}{i+1} = {res_hex}")
            ctr_val = (ctr_val + 1) % (1 << 64)
            
        return "".join(processed)

def print_menu():
    print("ГОСТ Р 34.13 2015")
    print("1 Режим гаммирования")

def main():
    magma = MagmaCipher()
    modes = GOST_34_13_Modes(magma)

    while True:
        print_menu()
        choice = input("Ваш выбор: ").strip()

        # Ключ и данные со скрина №1
        default_key = "ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
        default_plain = "92def06b3c130a59db54c704f8189d204a98fb2e67a8024c8912409b17b57e41"
        default_iv = "12345678"

        if choice == "1":
            print("\n1 Шифрование")
            print("2 Расшифрование")
            subchoice = input("Выбор: ").strip()

            key = input("Введите ключ (128 hex символов): ").strip()
            if not key: key = default_key
            
            iv = input("Введите IV (8 hex символов): ").strip()
            if not iv: iv = default_iv
            
            if subchoice == "2":
                # Значения Ci со скрина как default для расшифровки
                default_cipher = "4e98110c97b7b93c3e250d93d6e85d69136d868807b2dbef568eb680ab52a12d"
                text = input("Введите зашифрованный текст (hex): ").strip()
                if not text: text = default_cipher
                print("\nРезультаты расшифрования:")
                modes.ctr_process(text, key, iv, mode="decrypt")
            else:
                text = input("Введите открытый текст (hex): ").strip()
                if not text: text = default_plain
                print("\nРезультаты вычислений:")
                modes.ctr_process(text, key, iv, mode="encrypt")
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()