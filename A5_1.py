import sys

# Алфавит: 32 русские буквы (без Ё), каждая кодируется 5 битами
RU_CHARS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def encode_char(ch):
    ch = ch.upper()
    if ch == "Ё":
        ch = "Е"
    if ch not in RU_CHARS:
        return []
    pos = RU_CHARS.index(ch)
    return [(pos >> (4 - b)) & 1 for b in range(5)]


def text_to_bitlist(text):
    result = []
    for ch in text:
        result += encode_char(ch)
    return result


def bitlist_to_text(bits):
    out = ""
    for i in range(0, len(bits) - 4, 5):
        val = 0
        for b in bits[i:i + 5]:
            val = (val << 1) | b
        out += RU_CHARS[val] if 0 <= val < len(RU_CHARS) else "?"
    return out


def apply_xor(seq_a, seq_b):
    return [a ^ b for a, b in zip(seq_a, seq_b)]


# Генератор ключевого потока A5/1
class StreamA5_1:
    """
    Потоковый шифр A5/1.
    Три регистра сдвига с линейной обратной связью (РСЛОС):
      R1 — 19 бит  полином X^19 + X^18 + X^17 + X^14 + 1  бит синхронизации: 8
      R2 — 22 бита полином X^22 + X^21 + 1               бит синхронизации: 10
      R3 — 23 бита полином X^23 + X^22 + X^21 + X^8 + 1  бит синхронизации: 10
    """

    def __init__(self, session_key_hex: str, frame_number: int):
        bits = ""
        for nibble in session_key_hex:
            bits += f"{int(nibble, 16):04b}"
        if len(bits) != 64:
            raise ValueError("Длина ключа должна быть ровно 64 бита (16 hex-символов).")
        # Биты читаются в обратном порядке (от LSB к MSB)
        self._key_bits = bits[::-1]
        self._frame   = frame_number

    # вспомогательные функции регистров

    @staticmethod
    def _next_bit_r1(r):
        return r[18] ^ r[17] ^ r[16] ^ r[13]

    @staticmethod
    def _next_bit_r2(r):
        return r[21] ^ r[20]

    @staticmethod
    def _next_bit_r3(r):
        return r[22] ^ r[21] ^ r[20] ^ r[7]

    @staticmethod
    def _majority(a, b, c):
        return (a & b) | (a & c) | (b & c)

    @staticmethod
    def _shift(reg, new_bit):
        reg.pop()
        reg.insert(0, new_bit)

    # основной цикл

    def keystream(self, length: int) -> list:
        stream = ""
        frames_needed = (length + 113) // 114

        for frame_idx in range(frames_needed):
            r1 = [0] * 19
            r2 = [0] * 22
            r3 = [0] * 23

            # Регистр 1: загрузка ключа (64 такта, все регистры тактируются)
            for bit_pos in range(64):
                k = int(self._key_bits[bit_pos])
                self._shift(r1, self._next_bit_r1(r1) ^ k)
                self._shift(r2, self._next_bit_r2(r2) ^ k)
                self._shift(r3, self._next_bit_r3(r3) ^ k)

            # Регистр 2: загрузка номера кадра (22 такта)
            frame_bits = f"{frame_idx:022b}"[::-1]
            for bit_pos in range(22):
                f = int(frame_bits[bit_pos])
                self._shift(r1, self._next_bit_r1(r1) ^ f)
                self._shift(r2, self._next_bit_r2(r2) ^ f)
                self._shift(r3, self._next_bit_r3(r3) ^ f)

            # Регистр 3: прогрев (100 тактов без выхода)
            for _ in range(100):
                maj = self._majority(r1[8], r2[10], r3[10])
                nb1, nb2, nb3 = self._next_bit_r1(r1), self._next_bit_r2(r2), self._next_bit_r3(r3)
                if r1[8] == maj: self._shift(r1, nb1)
                if r2[10] == maj: self._shift(r2, nb2)
                if r3[10] == maj: self._shift(r3, nb3)

        
            for _ in range(114):
                if len(stream) >= length:
                    break
                maj = self._majority(r1[8], r2[10], r3[10])
                nb1, nb2, nb3 = self._next_bit_r1(r1), self._next_bit_r2(r2), self._next_bit_r3(r3)
                if r1[8] == maj: self._shift(r1, nb1)
                if r2[10] == maj: self._shift(r2, nb2)
                if r3[10] == maj: self._shift(r3, nb3)
                stream += str(r1[18] ^ r2[21] ^ r3[22])

        return [int(b) for b in stream]


# ── Тест корректности ────────────────────────────────────────────────────────

def self_test():
    print("[ тест A5/1 ]")
    test_key  = "0123456789ABCDEF"
    test_msg  = "СЕКРЕТНОЕСООБЩЕНИЕ"
    frame_no  = 1024

    bits_msg = text_to_bitlist(test_msg)

    enc_gen = StreamA5_1(test_key, frame_no)
    encrypted = apply_xor(bits_msg, enc_gen.keystream(len(bits_msg)))

    dec_gen = StreamA5_1(test_key, frame_no)
    decrypted = bitlist_to_text(apply_xor(encrypted, dec_gen.keystream(len(encrypted))))

    if decrypted == test_msg:
        print("  результат: ПРОЙДЕН")
    else:
        print(f"  результат: ОШИБКА — ожидалось '{test_msg}', получено '{decrypted}'")
        sys.exit(1)


# ── Интерфейс командной строки ───────────────────────────────────────────────

def _ask_key():
    raw = input("Сеансовый ключ (16 hex-символов) [Enter = 0123456789ABCDEF]: ").strip()
    if not raw:
        raw = "0123456789ABCDEF"
        print(f"  используется: {raw}")
    return raw


def _ask_frame():
    while True:
        raw = input("Номер кадра [Enter = 1024]: ").strip()
        if not raw:
            raw = "1024"
            print(f"  используется: {raw}")
        try:
            return int(raw)
        except ValueError:
            print("  ошибка: введите целое число")


def _encrypt(cipher: StreamA5_1):
    raw = input("Открытый текст (русские буквы): ").strip().upper()
    if not raw:
        raw = "ПРИМЕРТЕКСТА"
        print(f"  используется: {raw}")

    plain_bits   = text_to_bitlist(raw)
    gamma_bits   = cipher.keystream(len(plain_bits))
    cipher_bits  = apply_xor(plain_bits, gamma_bits)

    plain_str    = "".join(map(str, plain_bits))
    gamma_str    = "".join(map(str, gamma_bits))
    cipher_str   = "".join(map(str, cipher_bits))
    hex_nibbles  = len(cipher_str) // 4
    cipher_hex   = f"{int(cipher_str, 2):0{hex_nibbles}X}" if cipher_str else ""
    cipher_chars = bitlist_to_text(cipher_bits)

    print()
    print("Открытый текст  :", plain_str)
    print("Гамма           :", gamma_str)
    print("Шифротекст (XOR):", cipher_str)
    print()
    print("Шифротекст (HEX):", cipher_hex)
    print("Шифротекст (рус):", cipher_chars)
    print()
    print("Сохраните BIN или HEX-строку для расшифровки.")


def _decrypt(cipher: StreamA5_1):
    print("Формат шифротекста:")
    print("  1 — двоичная строка (0 и 1)")
    print("  2 — шестнадцатеричная (HEX)")
    print("  3 — русские буквы")
    fmt = input("Выбор: ").strip()

    if fmt == "1":
        raw = input("Введите шифротекст (0/1): ").strip()
        if not all(c in "01" for c in raw):
            print("Ошибка: допустимы только символы 0 и 1.")
            return
        bits = [int(c) for c in raw]

    elif fmt == "2":
        raw = input("Введите шифротекст (HEX): ").strip()
        try:
            bits = []
            for h in raw:
                v = int(h, 16)
                for i in range(4):
                    bits.append((v >> (3 - i)) & 1)
        except ValueError:
            print("Ошибка: неверный HEX.")
            return

    elif fmt == "3":
        raw  = input("Введите шифротекст (буквы): ").strip()
        bits = text_to_bitlist(raw)

    else:
        print("Ошибка: неизвестный формат.")
        return

    gamma_bits     = cipher.keystream(len(bits))
    plain_bits     = apply_xor(bits, gamma_bits)
    gamma_str      = "".join(map(str, gamma_bits))
    plain_bin_str  = "".join(map(str, plain_bits))
    plain_text     = bitlist_to_text(plain_bits)

    print()
    print("Гамма           :", gamma_str)
    print("Открытый текст  :", plain_bin_str)
    print()
    print("Расшифрованный текст:", plain_text)


def main():
    if "--test" in sys.argv:
        self_test()
        return

    print("─" * 40)
    print("       Поточный шифр   A 5 / 1")
    print("─" * 40)
    print("  1  Зашифровать")
    print("  2  Расшифровать")
    print()

    try:
        action = input("Действие: ").strip()
        if action not in ("1", "2"):
            print("Выберите 1 или 2.")
            return

        key    = _ask_key()
        frame  = _ask_frame()
        gen    = StreamA5_1(key, frame)

        print()
        if action == "1":
            _encrypt(gen)
        else:
            _decrypt(gen)

    except EOFError:
        pass
    except Exception as exc:
        print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()
