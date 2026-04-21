import sys
import binascii

class A5_Y:
    """
    Класс, реализующий генератор гаммы по учебному алгоритму А5/У.
    Состоит из трех регистров сдвига с линейной обратной связью (РСЛОС):
    R1 (6 бит), R2 (7 бит), R3 (11 бит).
    Кадры обрабатываются блоками по 32 бита.
    """
    def __init__(self, key: int, frame: int):
        # Инициализация регистров нулевыми значениями
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        
        self.key = key
        self.frame = frame
        
        # Вызов процедуры начальной загрузки (инициализации) регистров
        self._init_registers()

    def _get_majority(self):
        """
        Вычисляет мажоритарную функцию (F = x1*x2 + x1*x3 + x2*x3).
        Биты синхронизации: C1=третий разряд (бит 2) для R1, 
        C2=пятый разряд (бит 4) для R2, C3=пятый разряд (бит 4) для R3.
        (индексация с нуля, начиная с младшего бита)
        """
        b1 = (self.r1 >> 2) & 1
        b2 = (self.r2 >> 4) & 1
        b3 = (self.r3 >> 4) & 1
        return (b1 & b2) | (b1 & b3) | (b2 & b3)

    def _clock_r1(self, force=False, mix_bit=0):
        """
        Сдвиг регистра R1.
        Многочлен: X^6 + X + 1 -> отводы с 5 и 0 бит.
        """
        if not force:
            maj = self._get_majority()
            sync_bit = (self.r1 >> 2) & 1
            if maj != sync_bit:
                return
        
        feedback = ((self.r1 >> 5) ^ (self.r1 >> 0)) & 1
        feedback ^= mix_bit
        self.r1 = ((self.r1 << 1) | feedback) & 0x3F

    def _clock_r2(self, force=False, mix_bit=0):
        """
        Сдвиг регистра R2.
        Многочлен: X^7 + X^3 + 1 -> отводы с 6 и 2 бит.
        """
        if not force:
            maj = self._get_majority()
            sync_bit = (self.r2 >> 4) & 1
            if maj != sync_bit:
                return
        
        feedback = ((self.r2 >> 6) ^ (self.r2 >> 2)) & 1
        feedback ^= mix_bit
        self.r2 = ((self.r2 << 1) | feedback) & 0x7F

    def _clock_r3(self, force=False, mix_bit=0):
        """
        Сдвиг регистра R3.
        Многочлен: X^11 + X^2 + 1 -> отводы с 10 и 1 бит.
        """
        if not force:
            maj = self._get_majority()
            sync_bit = (self.r3 >> 4) & 1
            if maj != sync_bit:
                return
        
        feedback = ((self.r3 >> 10) ^ (self.r3 >> 1)) & 1
        feedback ^= mix_bit
        self.r3 = ((self.r3 << 1) | feedback) & 0x7FF

    def _clock_all_force(self, mix_bit=0):
        """Принудительно сдвигает все три регистра (без stop-and-go)."""
        self._clock_r1(force=True, mix_bit=mix_bit)
        self._clock_r2(force=True, mix_bit=mix_bit)
        self._clock_r3(force=True, mix_bit=mix_bit)

    def _clock(self):
        """
        Обычный такт работы по принципу stop-and-go.
        """
        maj = self._get_majority()
        b1 = (self.r1 >> 2) & 1
        b2 = (self.r2 >> 4) & 1
        b3 = (self.r3 >> 4) & 1
        
        if maj == b1:
            self._clock_r1(force=True)
        if maj == b2:
            self._clock_r2(force=True)
        if maj == b3:
            self._clock_r3(force=True)

    def _init_registers(self):
        """
        Процедура инициализации ключа и вектора IV:
        1. 24 такта с принудительным сдвигом и XOR битами ключа.
        2. 8 тактов с принудительным сдвигом и XOR битами номера кадра.
        3. 32 такта в режиме stop-and-go (холостой прогон для перемешивания).
        """
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        
        # 1. 24 раза тактируются все три, добавляется ключ
        for i in range(24):
            key_bit = (self.key >> i) & 1
            self._clock_all_force(key_bit)
            
        # 2. 8 раз тактируются все три, добавляется номер кадра (IV)
        for i in range(8):
            frame_bit = (self.frame >> i) & 1
            self._clock_all_force(frame_bit)
            
        # 3. 32 такта работы с режимом stop-and-go (перемешивание)
        for i in range(32):
            self._clock()

    def get_bit(self):
        """
        Генерация 1 бита гаммы с использованием режима stop-and-go.
        Выходной бит снимается с самых старших разрядов (5, 6, 10).
        """
        self._clock()
        out1 = (self.r1 >> 5) & 1
        out2 = (self.r2 >> 6) & 1
        out3 = (self.r3 >> 10) & 1
        return out1 ^ out2 ^ out3

def a5_y_encrypt(data_bits: list[int], key: int, start_frame: int):
    """
    Шифрует/расшифровывает данные блоками (кадрами) по 32 бита.
    """
    output_bits = []
    frame = start_frame
    
    for i in range(0, len(data_bits), 32):
        chunk = data_bits[i:i+32]
        cipher = A5_Y(key, frame)
        
        # 4. Формирование гаммы и шифрование кадра
        for bit in chunk:
            gamma_bit = cipher.get_bit()
            output_bits.append(bit ^ gamma_bit)
            
        frame = (frame + 1) & 0xFF # номер кадра 8-битный
        
    return output_bits

def bytes_to_bits(data: bytes) -> list[int]:
    """Перевод байтов в массив битов."""
    bits = []
    for b in data:
        for i in range(8):
            bits.append((b >> (7 - i)) & 1)
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    """Перевод массива битов обратно в байты."""
    res = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        chunk = bits[i:i+8]
        for j, bit in enumerate(chunk):
            b |= (bit << (7 - j))
        res.append(b)
    return bytes(res)

if __name__ == "__main__":
    print("Учебная модель алгоритма А5/У")
    
    action = input("Что сделать? (1 зашифровать текст, 2 расшифровать HEX): ")
    
    key_hex = input("Введите ключ (24 бита / 6 HEX символов) [по умолчанию: 1A2B3C]: ").strip()
    if not key_hex:
        key_hex = "1A2B3C"
        
    frame_str = input("Введите стартовый номер кадра (до 8 бит, число) [по умолчанию: 0]: ").strip()
    if not frame_str:
        frame_str = "0"
        
    try:
        key_int = int(key_hex, 16)
        frame_int = int(frame_str) & 0xFF
        
        if action == "1":
            msg = input("Введите текст для шифрования: ")
            msg_bytes = msg.encode('utf-8')
            msg_bits = bytes_to_bits(msg_bytes)
            
            enc_bits = a5_y_encrypt(msg_bits, key_int, frame_int)
            enc_bytes = bits_to_bytes(enc_bits)
            print("Зашифрованный текст (HEX):", enc_bytes.hex())
            
        elif action == "2":
            enc_hex = input("Введите зашифрованный текст (HEX): ").strip()
            enc_bytes = bytes.fromhex(enc_hex)
            enc_bits = bytes_to_bits(enc_bytes)
            
            dec_bits = a5_y_encrypt(enc_bits, key_int, frame_int)
            dec_bytes = bits_to_bytes(dec_bits)
            print("Расшифрованный текст:", dec_bytes.decode('utf-8'))
            
        else:
            print("Неизвестная команда")
            
    except Exception as e:
        print("Ошибка:", e)
