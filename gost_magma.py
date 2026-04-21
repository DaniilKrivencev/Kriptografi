import os

S_BOX = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

def _substitute(val):
    res = 0
    for i in range(8):
        nibble = (val >> (4 * i)) & 0x0F
        res |= (S_BOX[i][nibble] << (4 * i))
    return res

def _f(R, K):
    t = (R + K) % (1 << 32)
    t = _substitute(t)
    return ((t << 11) & 0xFFFFFFFF) | (t >> 21)

def magma_encrypt_block(block, key):
    # key: 32 bytes, block: 8 bytes
    K = [int.from_bytes(key[i*4:i*4+4], "little") for i in range(8)]
    L = int.from_bytes(block[4:], "little")
    R = int.from_bytes(block[:4], "little")

    for i in range(32):
        if i < 24:
            k_idx = i % 8
        else:
            k_idx = 7 - (i % 8)
        
        tmp = L ^ _f(R, K[k_idx])
        L = R
        R = tmp

    return R.to_bytes(4, "little") + L.to_bytes(4, "little")

def magma_ctr(data: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Encrypts or decrypts using GOST Magma in CTR mode.
    key: 32 bytes (256 bits)
    iv: 4 bytes (32 bits) sync-parcel
    """
    out = bytearray()
    
    # IV in Magma CTR is usually 64 bit: IV(32 bit) || padding 0...0
    # Let's start counter from the first block
    # According to image, we do IV || 00 00 00 00, then increment
    ctr_val = iv + b'\x00\x00\x00\x00'
    ctr_int = int.from_bytes(ctr_val, "big")
    
    blocks = len(data) // 8 + (1 if len(data) % 8 else 0)
    for i in range(blocks):
        # We encrypt the counter
        ctr_bytes = ctr_int.to_bytes(8, "big")
        gamma_block = magma_encrypt_block(ctr_bytes, key)
        
        chunk = data[i*8:(i+1)*8]
        # XOR data with gamma
        for j in range(len(chunk)):
            out.append(chunk[j] ^ gamma_block[j])
            
        ctr_int = (ctr_int + 1) % (1 << 64)
        
    return bytes(out)

if __name__ == "__main__":
    import binascii

    print("ГОСТ Магма (Гаммирование CTR)")
    
    action = input("Что сделать? (1 зашифровать текст, 2 расшифровать HEX): ")

    key_hex = input("Введите ключ (64 HEX символа, 32 байта) [по умолчанию: 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff]: ").strip()
    if not key_hex:
        key_hex = "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff"
    
    iv_hex = input("Введите IV (8 HEX символов, 4 байта) [по умолчанию: 12345678]: ").strip()
    if not iv_hex:
        iv_hex = "12345678"

    try:
        key = bytes.fromhex(key_hex)
        iv = bytes.fromhex(iv_hex)

        if len(key) != 32:
            print("Ошибка: Ключ должен быть ровно 32 байта (64 символа)!")
            exit(1)
            
        if len(iv) != 4:
            print("Ошибка: IV должен быть ровно 4 байта (8 символов)!")
            exit(1)

        if action == "1":
            msg = input("Введите текст для шифрования: ")
            msg_bytes = msg.encode("utf-8")
            enc = magma_ctr(msg_bytes, key, iv)
            print("Зашифрованный текст (HEX):", enc.hex())
            
        elif action == "2":
            enc_hex = input("Введите зашифрованный текст в формате HEX: ")
            try:
                enc_bytes = bytes.fromhex(enc_hex)
                dec = magma_ctr(enc_bytes, key, iv)
                print("Расшифрованный текст:", dec.decode("utf-8"))
            except Exception as e:
                print("Ошибка при расшифровке:", e)
        else:
            print("Неизвестная команда")

    except Exception as e:
        print("Ошибка ввода данных:", e)
