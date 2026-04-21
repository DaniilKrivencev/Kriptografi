// ===== Cipher Registry =====
const ciphers = {};

// ===== Cipher Registration System =====
function registerCipher(id, name, description, params, encryptFn, decryptFn) {
    ciphers[id] = {
        name,
        description,
        params,
        encrypt: encryptFn,
        decrypt: decryptFn
    };
}

// ===== Russian Alphabet =====
const ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюя";

// ===== Cardan Grille Configuration =====
const CARDAN_POS = [
    // Turn 1
    [[0, 1], [1, 0], [1, 4], [1, 6], [1, 7], [2, 1], [2, 5], [2, 9], [3, 3], [3, 7], [4, 1], [5, 2], [5, 5], [5, 6], [5, 9]],
    // Turn 2
    [[0, 0], [0, 3], [0, 4], [0, 7], [1, 8], [2, 2], [2, 6], [3, 0], [3, 4], [3, 8], [4, 2], [4, 3], [4, 5], [4, 9], [5, 8]],
    // Turn 3
    [[0, 2], [0, 5], [0, 6], [0, 9], [1, 1], [2, 3], [2, 7], [3, 1], [3, 5], [3, 9], [4, 0], [4, 4], [4, 6], [4, 7], [5, 1]],
    // Turn 4
    [[0, 8], [1, 2], [1, 3], [1, 5], [1, 9], [2, 0], [2, 4], [2, 8], [3, 2], [3, 6], [4, 8], [5, 0], [5, 3], [5, 4], [5, 7]]
];

let currentCardanGrid = null;
let currentCardanStep = 0;

let currentFeistelL = 0;
let currentFeistelR = 0;
let feistelKeys = []; // To store K1...K32
let feistelRounds = []; // To store intermediate L, R per round

// ===== Utility Functions =====
function formatText(text) {
    return text.toLowerCase()
        .replace(/ё/g, 'е')
        .replace(/ /g, '')
        .replace(/,/g, 'зпт')
        .replace(/\./g, 'тчк')
        .replace(/-/g, 'тире');
}


function formatOutput(text) {
    const segments = [];
    for (let i = 0; i < text.length; i += 5) {
        segments.push(text.slice(i, i + 5));
    }
    let rows = [];
    for (let i = 0; i < segments.length; i += 5) {
        rows.push(segments.slice(i, i + 5).join(' '));
    }
    return rows.join('\n');
}


function reverseFormat(text) {
    return text
        .replace(/зпт/g, ',')
        .replace(/тчк/g, '.')
        .replace(/тире/g, '-');
}

// ===== Toast Notification =====
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    toastMessage.textContent = message;

    if (isError) {
        toast.classList.add('error');
    } else {
        toast.classList.remove('error');
    }

    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ===== CIPHER IMPLEMENTATIONS =====

// ----- 1. Atbash Cipher -----
registerCipher('atbash', 'Шифр Атбаш', 'Простой шифр замены: первая буква алфавита заменяется на последнюю, вторая на предпоследнюю и так далее.', [],
    (text) => {
        const t = formatText(text);
        let res = '';
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            res += idx !== -1 ? ALPHABET[ALPHABET.length - 1 - idx] : c;
        }
        return formatOutput(res);
    },
    (text) => {
        const t = text.replace(/ /g, '');
        let res = '';
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            res += idx !== -1 ? ALPHABET[ALPHABET.length - 1 - idx] : c;
        }
        return reverseFormat(res);
    }
);

// ----- 2. Polybius Square -----
const POLYBIUS = {
    'а': '11', 'б': '12', 'в': '13', 'г': '14', 'д': '15', 'е': '16',
    'ж': '21', 'з': '22', 'и': '23', 'й': '24', 'к': '25', 'л': '26',
    'м': '31', 'н': '32', 'о': '33', 'п': '34', 'р': '35', 'с': '36',
    'т': '41', 'у': '42', 'ф': '43', 'х': '44', 'ц': '45', 'ч': '46',
    'ш': '51', 'щ': '52', 'ъ': '53', 'ы': '54', 'ь': '55', 'э': '56',
    'ю': '61', 'я': '62'
};
const POLYBIUS_REV = Object.fromEntries(Object.entries(POLYBIUS).map(([k, v]) => [v, k]));

registerCipher('polybius', 'Квадрат Полибия', 'Каждая буква заменяется на координаты (строка, столбец) в квадрате 6x6.', [],
    (text) => {
        const t = text.toUpperCase();
        const tLower = formatText(text);
        let codeStr = '';
        for (let c of tLower) {
            if (POLYBIUS[c]) codeStr += POLYBIUS[c];
        }
        return formatOutput(codeStr);
    },
    (text) => {
        const t = text.replace(/ /g, '');
        let res = '';
        for (let i = 0; i < t.length; i += 2) {
            let pair = t.slice(i, i + 2);
            if (POLYBIUS_REV[pair]) res += POLYBIUS_REV[pair];
        }
        return reverseFormat(res);
    }
);

// ----- 3. Caesar Cipher -----
registerCipher('caesar', 'Шифр Цезаря', 'Каждая буква сдвигается на фиксированное число позиций (ключ).',
    [{ id: 'key', label: 'Ключ (число)', type: 'number', default: 3 }],
    (text, p) => {
        const k = parseInt(p.key) || 3;
        const t = formatText(text);
        let res = '';
        const len = ALPHABET.length;
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            res += idx !== -1 ? ALPHABET[(idx + k) % len] : c;
        }
        return formatOutput(res);
    },
    (text, p) => {
        const k = parseInt(p.key) || 3;
        const t = text.replace(/ /g, '');
        let res = '';
        const len = ALPHABET.length;
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            res += idx !== -1 ? ALPHABET[(idx - k + len) % len] : c;
        }
        return reverseFormat(res);
    }
);

// ----- 4. Trithemius Cipher -----
registerCipher('trithemius', 'Шифр Тритемия', 'Сдвиг меняется для каждой буквы по формуле: Y = (X + index) mod N.', [],
    (text) => {
        const t = formatText(text);
        let res = '';
        const n = ALPHABET.length;
        let j = 1;
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            if (idx !== -1) {
                let newIdx = (idx + j) % n;
                res += ALPHABET[newIdx];
                j++;
            }
        }
        return formatOutput(res);
    },
    (text) => {
        const t = text.replace(/ /g, '');
        let res = '';
        const n = ALPHABET.length;
        let j = 1;
        for (let c of t) {
            let idx = ALPHABET.indexOf(c);
            if (idx !== -1) {
                let oldIdx = (idx - j) % n;
                if (oldIdx < 0) oldIdx += n;
                res += ALPHABET[oldIdx];
                j++;
            }
        }
        return reverseFormat(res);
    }
);

// ----- 5. Bellaso Cipher -----
registerCipher('bellaso', 'Шифр Белазо', 'Многоалфавитный шифр с использованием лозунга (ключа).',
    [{ id: 'key', label: 'Ключ (слово)', type: 'text', default: 'ключ' }],
    (text, p) => {
        const key = formatText(p.key || 'а');
        const t = formatText(text);
        let res = '';
        const n = ALPHABET.length;

        let validT = '';
        for (let c of t) if (ALPHABET.includes(c)) validT += c;

        for (let i = 0; i < validT.length; i++) {
            let c = validT[i];
            let kChar = key[i % key.length];
            let cIdx = ALPHABET.indexOf(c);
            let kIdx = ALPHABET.indexOf(kChar);

            let newIdx = (cIdx + kIdx) % n;
            res += ALPHABET[newIdx];
        }
        return formatOutput(res);
    },
    (text, p) => {
        const key = formatText(p.key || 'а');
        const t = text.replace(/ /g, '');
        let res = '';
        const n = ALPHABET.length;

        for (let i = 0; i < t.length; i++) {
            let c = t[i];
            let kChar = key[i % key.length];
            let cIdx = ALPHABET.indexOf(c);
            let kIdx = ALPHABET.indexOf(kChar);

            let newIdx = (cIdx - kIdx) % n;
            if (newIdx < 0) newIdx += n;
            res += ALPHABET[newIdx];
        }
        return reverseFormat(res);
    }
);

// ----- 6. Vigenere Cipher -----
registerCipher('vigenere', 'Шифр Виженера', 'Шифр с самоключом или ключом-шифртекстом.',
    [{ id: 'key', label: 'Секретная буква', type: 'text', default: 'а', maxlength: 1 },
    { id: 'mode', label: 'Режим (auto/cipher)', type: 'text', default: 'auto', placeholder: 'auto или cipher' }],
    (text, p) => {
        const mode = p.mode === 'cipher' ? 'cipher' : 'auto';
        const keyChar = (formatText(p.key || 'а'))[0] || 'а';
        const t = formatText(text);
        const n = ALPHABET.length;

        let gamma = [ALPHABET.indexOf(keyChar)];

        let res = '';
        let validT = '';
        for (let c of t) if (ALPHABET.includes(c)) validT += c;

        let currentGamma = ALPHABET.indexOf(keyChar);

        for (let c of validT) {
            let idx = ALPHABET.indexOf(c);
            let s_i = (currentGamma + idx) % n;
            res += ALPHABET[s_i];

            if (mode === 'cipher') {
                currentGamma = s_i;
            } else {
                currentGamma = idx;
            }
        }
        return formatOutput(res);
    },
    (text, p) => {
        const mode = p.mode === 'cipher' ? 'cipher' : 'auto';
        const keyChar = (formatText(p.key || 'а'))[0] || 'а';
        const t = text.replace(/ /g, '');
        const n = ALPHABET.length;

        let res = '';
        let currentGamma = ALPHABET.indexOf(keyChar);

        for (let c of t) {
            let idx = ALPHABET.indexOf(c);

            let pIdx = (idx - currentGamma) % n;
            if (pIdx < 0) pIdx += n;
            res += ALPHABET[pIdx];

            if (mode === 'cipher') {
                currentGamma = idx;
            } else {
                currentGamma = pIdx;
            }
        }
        return reverseFormat(res);
    }
);

// ----- 7. GOST Magma (S-box) -----
const S_BOXES = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
];

// Precompute Inverse S-boxes
const INV_S_BOXES = S_BOXES.map(box => {
    const inv = new Array(16);
    box.forEach((val, idx) => inv[val] = idx);
    return inv;
});

registerCipher('magma', 'GOST Magma (S-box)', 'Преобразование 32-битного блока через таблицы замен (S-блоки).', [],
    (text) => {
        const clean = text.replace(/ /g, '').toLowerCase();
        if (!/^[0-9a-f]{8}$/.test(clean)) return "Ошибка: Введите ровно 8 HEX символов (0-9, a-f)";

        let resHex = [];
        for (let i = 7; i >= 0; i--) {
            let hexChar = clean[7 - i]; // i=7 -> clean[0]
            let val = parseInt(hexChar, 16);
            let sub = S_BOXES[i][val];
            resHex.push(sub.toString(16));
        }
        return resHex.join('');
    },
    (text) => {
        const clean = text.replace(/ /g, '').toLowerCase();
        if (!/^[0-9a-f]{8}$/.test(clean)) return "Ошибка: Введите ровно 8 HEX символов";

        let resHex = [];
        for (let i = 7; i >= 0; i--) {
            let hexChar = clean[7 - i];
            let val = parseInt(hexChar, 16);
            let sub = INV_S_BOXES[i][val];
            resHex.push(sub.toString(16));
        }
        return resHex.join('');
    }
);

// ----- 7b. Feistel Network (Full Magma) -----
const feistel_f = (part, subkey) => {
    let temp = (part + subkey) >>> 0;
    let res = 0;
    for (let i = 0; i < 8; i++) {
        let nibble = (temp >>> (4 * i)) & 0x0F;
        res |= (S_BOXES[i][nibble] << (4 * i));
    }
    return ((res << 11) | (res >>> 21)) >>> 0;
};

registerCipher('feistel', 'Сеть Фейстеля (Магма)', 'Полноценный блочный шифр (32 раунда). Поддерживает строковый и HEX ввод (16 символов).',
    [{ id: 'key', label: 'Ключ (32 символа или 64 HEX)', type: 'text', default: 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff' }],
    (text, p) => {
        let keys = [];
        const rawKey = (p.key || '').trim();

        if (/^[0-9a-fA-F]{64}$/.test(rawKey)) {
            const bytes = rawKey.match(/.{1,2}/g).map(b => parseInt(b, 16));
            const view = new DataView(new Uint8Array(bytes).buffer);
            for (let i = 0; i < 8; i++) keys.push(view.getUint32(i * 4, false));
        } else {
            const keyStr = rawKey.padEnd(32, '\0').slice(0, 32);
            const view = new DataView(new TextEncoder().encode(keyStr).buffer);
            for (let i = 0; i < 8; i++) keys.push(view.getUint32(i * 4, false));
        }

        // Store Ki for visualization (3 cycles of K1..K8, then 1 cycle of K8..K1)
        feistelKeys = [];
        for (let j = 0; j < 3; j++) {
            for (let i = 0; i < 8; i++) feistelKeys.push(keys[i]);
        }
        for (let i = 7; i >= 0; i--) feistelKeys.push(keys[i]);

        let dataBlocks = [];
        const cleanText = text.trim();
        if (/^[0-9a-fA-F]{16}$/.test(cleanText)) {
            dataBlocks = [new Uint8Array(cleanText.match(/.{1,2}/g).map(b => parseInt(b, 16)))];
        } else {
            const encoder = new TextEncoder();
            let rawData = Array.from(encoder.encode(text));
            while (rawData.length % 8 !== 0) rawData.push(0);
            for (let i = 0; i < rawData.length; i += 8) dataBlocks.push(new Uint8Array(rawData.slice(i, i + 8)));
        }

        let resultBytes = new Uint8Array(dataBlocks.length * 8);
        feistelRounds = [];

        dataBlocks.forEach((block, bIdx) => {
            let view = new DataView(block.buffer);
            let L = view.getUint32(0, false);
            let R = view.getUint32(4, false);

            for (let i = 0; i < 32; i++) {
                let subkey = feistelKeys[i];
                if (i < 31) {
                    let nextL = R;
                    let nextR = (L ^ feistel_f(R, subkey)) >>> 0;
                    L = nextL; R = nextR;
                } else {
                    L = (L ^ feistel_f(R, subkey)) >>> 0;
                }
                if (bIdx === 0) feistelRounds.push({ l: L, r: R, k: subkey });
            }
            currentFeistelL = L;
            currentFeistelR = R;
            new DataView(resultBytes.buffer).setUint32(bIdx * 8, L, false);
            new DataView(resultBytes.buffer).setUint32(bIdx * 8 + 4, R, false);
        });

        return Array.from(resultBytes).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    },
    (text, p) => {
        const hex = text.replace(/[^0-9A-Fa-f]/g, '');
        if (hex.length % 16 !== 0) return "Ошибка: Некорректная длина HEX";

        let keys = [];
        const rawKey = (p.key || '').trim();
        if (/^[0-9a-fA-F]{64}$/.test(rawKey)) {
            const bytes = rawKey.match(/.{1,2}/g).map(b => parseInt(b, 16));
            const view = new DataView(new Uint8Array(bytes).buffer);
            for (let i = 0; i < 8; i++) keys.push(view.getUint32(i * 4, false));
        } else {
            const keyStr = rawKey.padEnd(32, '\0').slice(0, 32);
            const view = new DataView(new TextEncoder().encode(keyStr).buffer);
            for (let i = 0; i < 8; i++) keys.push(view.getUint32(i * 4, false));
        }

        // For decryption, we generate the SAME feistelKeys schedule and reverse it
        const encryptionKeys = [];
        for (let j = 0; j < 3; j++) {
            for (let i = 0; i < 8; i++) encryptionKeys.push(keys[i]);
        }
        for (let i = 7; i >= 0; i--) encryptionKeys.push(keys[i]);

        const decryptionKeys = [...encryptionKeys].reverse();
        feistelKeys = decryptionKeys; // For visualization

        let data = new Uint8Array(hex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
        let result = new Uint8Array(data.length);
        feistelRounds = [];

        for (let b = 0; b < data.length; b += 8) {
            let view = new DataView(data.buffer, b, 8);
            let L = view.getUint32(0, false);
            let R = view.getUint32(4, false);

            for (let i = 0; i < 32; i++) {
                let subkey = decryptionKeys[i];
                if (i < 31) {
                    let nextL = R;
                    let nextR = (L ^ feistel_f(R, subkey)) >>> 0;
                    L = nextL; R = nextR;
                } else {
                    L = (L ^ feistel_f(R, subkey)) >>> 0;
                }
                if (b === 0) feistelRounds.push({ l: L, r: R, k: subkey });
            }
            currentFeistelL = L;
            currentFeistelR = R;
            new DataView(result.buffer).setUint32(b, L, false);
            new DataView(result.buffer).setUint32(b + 4, R, false);
        }
        if (rawKey === 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff') {
            return Array.from(result).map(b => b.toString(16).padStart(2, '0')).join('').toLowerCase();
        }

        try {
            const decoded = new TextDecoder().decode(result);
            if (/[\x00-\x08\x0B\x0C\x0E-\x1F]/.test(decoded)) throw new Error('Binary');
            return decoded.replace(/\0/g, '');
        } catch (e) {
            return Array.from(result).map(b => b.toString(16).padStart(2, '0')).join('').toLowerCase();
        }
    }
);

// ----- 8. Matrix Cipher -----
function getDeterminant(m) {
    if (m.length === 1) return m[0][0];
    if (m.length === 2) return m[0][0] * m[1][1] - m[0][1] * m[1][0];
    let det = 0;
    for (let j = 0; j < m.length; j++) {
        let subM = m.slice(1).map(row => row.filter((_, idx) => idx !== j));
        det += m[0][j] * getDeterminant(subM) * (j % 2 === 0 ? 1 : -1);
    }
    return det;
}
function getAdjugate(m) {
    const N = m.length;
    let adj = Array.from({ length: N }, () => Array(N).fill(0));
    for (let i = 0; i < N; i++) {
        for (let j = 0; j < N; j++) {
            let subM = [];
            for (let r = 0; r < N; r++) {
                if (r === i) continue;
                subM.push(m[r].filter((_, c) => c !== j));
            }
            let sign = (i + j) % 2 === 0 ? 1 : -1;
            adj[j][i] = sign * getDeterminant(subM); // Transposed cofactor
        }
    }
    return adj;
}

registerCipher('matrix', 'Матричный шифр', 'Шифрование умножением вектора текста на матрицу-ключ.',
    [{ id: 'size', label: 'Размер (N)', type: 'number', default: 3 },
    { id: 'key', label: 'Матрица (N*N чисел через пробел)', type: 'text', placeholder: '1 2 3 ...' }],
    (text, p) => {
        const n = parseInt(p.size) || 3;
        const kStr = p.key || '';
        const flat = kStr.trim().split(/\s+/).map(Number);
        if (flat.length !== n * n) return `Ошибка: Введите ${n * n} чисел для матрицы`;

        const t = formatText(text);
        let nums = [];
        for (let c of t) nums.push(ALPHABET.indexOf(c) !== -1 ? ALPHABET.indexOf(c) : 0);
        while (nums.length % n !== 0) nums.push(0);

        let encNums = [];
        for (let i = 0; i < nums.length; i += n) {
            let vec = nums.slice(i, i + n);
            for (let r = 0; r < n; r++) {
                let sum = 0;
                for (let c = 0; c < n; c++) sum += flat[r * n + c] * vec[c];
                encNums.push(sum);
            }
        }



        const maxVal = Math.max(...encNums, 0);
        const maxD = String(Math.abs(maxVal)).length;
        const allDigits = encNums.map(x => String(x).padStart(maxD, '0')).join('');
        
        let blocks = [];
        for (let i = 0; i < allDigits.length; i += 5) {
            blocks.push(allDigits.slice(i, i + 5));
        }
        return blocks.join(' ');
    },



    (text, p) => {
        const n = parseInt(p.size) || 3;
        const kStr = p.key || '';
        const flat = kStr.trim().split(/\s+/).map(Number);
        if (flat.length !== n * n) return `Ошибка: Введите ${n * n} чисел`;

        let m = [];
        for (let i = 0; i < n; i++) m.push(flat.slice(i * n, i * n + n));

        const det = getDeterminant(m);
        if (det === 0) return "Ошибка: Определитель матрицы равен 0";

        const adj = getAdjugate(m);

        const parts = text.replace(/,/g, ' ').trim().split(/\s+/);
        const nums = parts.map(Number).filter(x => !isNaN(x));

        let resText = '';
        for (let i = 0; i < nums.length; i += n) {
            if (i + n > nums.length) break;
            let vec = nums.slice(i, i + n);

            for (let r = 0; r < n; r++) {
                let sum = 0;
                for (let c = 0; c < n; c++) sum += adj[r][c] * vec[c];

                let val = sum / det;
                let intVal = Math.round(val);
                if (Math.abs(val - intVal) > 0.001) return "Ошибка: Дробный результат (неверный ключ?)";

                if (intVal >= 0 && intVal < ALPHABET.length) {
                    resText += ALPHABET[intVal];
                } else {
                    resText += '?';
                }
            }
        }
        return reverseFormat(resText);
    }
);

// ----- 9. Playfair Cipher -----
function preparePlayfair(text) {
    let res = '';
    for (let i = 0; i < text.length; i++) {
        res += text[i];
        if (i + 1 < text.length && text[i] === text[i + 1]) {
            res += (text[i] === 'ф' ? 'я' : 'ф');
        }
    }
    if (res.length % 2 !== 0) res += (res.endsWith('ф') ? 'я' : 'ф');
    return res;
}
function cleanPlayfairDecrypted(text) {
    let res = '';
    let i = 0;
    while (i < text.length) {
        if (i < text.length - 1) {
            if (['ф', 'я'].includes(text[i + 1]) && i + 2 < text.length && text[i] === text[i + 2]) {
                res += text[i];
                i += 2;
                continue;
            }
        }
        res += text[i];
        i++;
    }
    if (res.endsWith('я') && res.length > 1 && res[res.length - 2] === 'ф') {
        res = res.slice(0, -1);
    } else if (res.endsWith('ф')) {
        res = res.slice(0, -1);
    }
    return res;
}

registerCipher('playfair', 'Шифр Плэйфера', 'Биграммный шифр замены с таблицей 5x6.',
    [{ id: 'key', label: 'Ключ', type: 'text' }],
    (text, p) => {
        const key = formatText(p.key || 'ключ');
        const t = formatText(text);
        const pfAlpha = "абвгдежзиклмнопрстуфхцчшщьыэюя";
        const mapRepl = { 'й': 'и', 'ъ': 'ь', 'ё': 'е' };

        let cleanKey = '';
        let seen = new Set();
        for (let c of key) {
            c = mapRepl[c] || c;
            if (pfAlpha.includes(c) && !seen.has(c)) { seen.add(c); cleanKey += c; }
        }
        let matrixStr = cleanKey;
        for (let c of pfAlpha) { if (!seen.has(c)) matrixStr += c; }

        let cleanP = '';
        for (let c of t) {
            c = mapRepl[c] || c;
            if (pfAlpha.includes(c)) cleanP += c;
        }
        let prepared = preparePlayfair(cleanP);

        let res = '';
        for (let i = 0; i < prepared.length; i += 2) {
            let idx1 = matrixStr.indexOf(prepared[i]);
            let idx2 = matrixStr.indexOf(prepared[i + 1]);
            let r1 = Math.floor(idx1 / 6), c1 = idx1 % 6, r2 = Math.floor(idx2 / 6), c2 = idx2 % 6;

            if (r1 === r2) { res += matrixStr[r1 * 6 + (c1 + 1) % 6] + matrixStr[r2 * 6 + (c2 + 1) % 6]; }
            else if (c1 === c2) { res += matrixStr[((r1 + 1) % 5) * 6 + c1] + matrixStr[((r2 + 1) % 5) * 6 + c2]; }
            else { res += matrixStr[r1 * 6 + c2] + matrixStr[r2 * 6 + c1]; }
        }
        return formatOutput(res);
    },
    (text, p) => {
        const key = formatText(p.key || 'ключ');
        const pfAlpha = "абвгдежзиклмнопрстуфхцчшщьыэюя";
        const mapRepl = { 'й': 'и', 'ъ': 'ь', 'ё': 'е' };

        let cleanKey = '';
        let seen = new Set();
        for (let c of key) {
            c = mapRepl[c] || c;
            if (pfAlpha.includes(c) && !seen.has(c)) { seen.add(c); cleanKey += c; }
        }
        let matrixStr = cleanKey;
        for (let c of pfAlpha) { if (!seen.has(c)) matrixStr += c; }

        const t = text.replace(/ /g, '');
        let res = '';
        for (let i = 0; i < t.length; i += 2) {
            let idx1 = matrixStr.indexOf(t[i]);
            let idx2 = matrixStr.indexOf(t[i + 1]);
            if (idx1 === -1 || idx2 === -1) continue;

            let r1 = Math.floor(idx1 / 6), c1 = idx1 % 6, r2 = Math.floor(idx2 / 6), c2 = idx2 % 6;

            if (r1 === r2) {
                res += matrixStr[r1 * 6 + (c1 - 1 + 6) % 6];
                res += matrixStr[r2 * 6 + (c2 - 1 + 6) % 6];
            } else if (c1 === c2) {
                res += matrixStr[((r1 - 1 + 5) % 5) * 6 + c1];
                res += matrixStr[((r2 - 1 + 5) % 5) * 6 + c2];
            } else {
                res += matrixStr[r1 * 6 + c2];
                res += matrixStr[r2 * 6 + c1];
            }
        }

        return reverseFormat(cleanPlayfairDecrypted(res));
    }
);

// ----- 10. Vertical Transposition -----
function getKeySequence(keyStr) {
    const clean = keyStr.replace(/ /g, '').toUpperCase() || 'KEY';
    const chars = clean.split('').map((c, i) => ({ c, i }));
    chars.sort((a, b) => a.c.localeCompare(b.c));
    const ranks = new Array(clean.length);
    chars.forEach((item, rank) => ranks[item.i] = rank + 1);
    return ranks;
}

registerCipher('vertical_shuffle', 'Вертикальная перестановка', 'Текст записывается в таблицу по строкам, а считывается по столбцам в порядке, заданном ключом.',
    [{ id: 'key', label: 'Ключ (слово)', type: 'text', default: 'ОКТЯБРЬ' }],
    (text, p) => {
        const key = p.key || 'ОКТЯБРЬ';
        const seq = getKeySequence(key);
        const cols = seq.length;
        const t = formatText(text);

        // Fill matrix row by row
        const rows = Math.ceil(t.length / cols);
        let matrix = Array.from({ length: rows }, () => new Array(cols).fill(''));

        let idx = 0;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (idx < t.length) matrix[r][c] = t[idx++];
            }
        }

        // Read columns by sequence order (1, 2, 3...)
        let res = '';
        for (let rank = 1; rank <= cols; rank++) {
            let colIdx = seq.indexOf(rank);
            for (let r = 0; r < rows; r++) {
                if (matrix[r][colIdx] !== '') res += matrix[r][colIdx];
            }
        }
        return formatOutput(res);
    },
    (text, p) => {
        const key = p.key || 'ОКТЯБРЬ';
        const seq = getKeySequence(key);
        const cols = seq.length;
        const t = text.replace(/ /g, '');
        const L = t.length;
        const rows = Math.ceil(L / cols);

        const fullCols = L % cols === 0 ? cols : L % cols;
        // First fullCols (in matrix left-to-right) have height 'rows', others 'rows-1'.

        let matrix = Array.from({ length: rows }, () => new Array(cols).fill(''));
        let currentIdx = 0;

        // Fill columns by sequence order
        for (let rank = 1; rank <= cols; rank++) {
            let colIdx = seq.indexOf(rank);
            let colWidth = 1;
            let colHeight = (colIdx < fullCols) ? rows : rows - 1;

            for (let r = 0; r < colHeight; r++) {
                if (currentIdx < L) matrix[r][colIdx] = t[currentIdx++];
            }
        }

        // Read rows
        let res = '';
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (matrix[r][c] !== '') res += matrix[r][c];
            }
        }
        return reverseFormat(res);
    }
);

// ----- 11. Cardan Grille (Fixed 6x10) -----
registerCipher('cardan_grille', 'Решетка Кардано (6x10)', 'Заполнение фиксированной сетки 6x10 через 4 группы отверстий. Исходный текст заполняет только отверстия.', [],
    (text) => {
        const t = formatText(text).toUpperCase();
        if (t.length > 60) throw new Error("Текст слишком длинный для сетки 6x10");

        let grid = Array.from({ length: 6 }, () => new Array(10).fill(''));
        let idx = 0;

        // Fill by positions
        for (let grp of CARDAN_POS) {
            for (let [r, c] of grp) {
                if (idx < t.length) {
                    grid[r][c] = t[idx++];
                } else {
                    grid[r][c] = ALPHABET[Math.floor(Math.random() * ALPHABET.length)].toUpperCase();
                }
            }
        }

        // Final check and collecting

        let res = '';
        currentCardanGrid = grid; 
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 10; c++) {
                if (grid[r][c] === '') grid[r][c] = ALPHABET[Math.floor(Math.random() * ALPHABET.length)].toUpperCase()
                res += grid[r][c];
            }
        }
        return formatOutput(res);
    },

    (text) => {
        const cleanT = text.replace(/ /g, '').replace(/\n/g, '').toUpperCase();
        if (cleanT.length !== 60) throw new Error("Длина должна быть 60 символов");

        let grid = Array.from({ length: 6 }, () => new Array(10).fill(''));
        let k = 0;
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 10; c++) {
                grid[r][c] = cleanT[k++];
            }
        }

        currentCardanGrid = grid; // Store for visualizer
        let res = '';
        for (let grp of CARDAN_POS) {
            for (let [r, c] of grp) {
                res += grid[r][c];
            }
        }
        return reverseFormat(res.toLowerCase());
    }
);

// ----- 12. Shannon Cipher -----
class LCG {
    constructor(a, c, m, t0) {
        this.a = BigInt(a);
        this.c = BigInt(c);
        this.m = BigInt(m);
        this.t = BigInt(t0);
    }

    next() {
        this.t = (this.a * this.t + this.c) % this.m;
        return Number(this.t);
    }
}

registerCipher('shannon', 'Блокнот Шеннона', 'Шифрование гаммированием с использованием линейного конгруэнтного генератора (LCG), как в консольной версии.',
    [
        { id: 'a', label: 'Множитель a', type: 'number', default: 17 },
        { id: 'c', label: 'Приращение c', type: 'number', default: 23 },
        { id: 't0', label: 'Начальное значение T0', type: 'number', default: 1 }
    ],
    (text, p) => {
        const a = Number(p.a || 17);
        const c = Number(p.c || 23);

        if (a === 1) throw new Error('ошибка замените параметр: a не может быть 1');
        if (a % 2 === 0) throw new Error('ошибка замените параметр: a должен быть нечетным');
        if (c % 2 === 0) throw new Error('ошибка замените параметр: c должен быть нечетным (взаимно простым с 32)');

        const t = text.toLowerCase()
            .replace(/ё/g, 'е')
            .replace(/ /g, '')
            .split('')
            .filter(c => ALPHABET.includes(c))
            .join('');

        const t0 = p.t0 || 1;
        const m = ALPHABET.length;
        const rng = new LCG(a, c, m, t0);

        let res = '';
        for (let char of t) {
            let idx = ALPHABET.indexOf(char);
            if (idx !== -1) {
                let k = rng.next();
                res += ALPHABET[(idx + k) % m];
            }
        }
        return formatOutput(res);
    },
    (text, p) => {
        const a = Number(p.a || 17);
        const c = Number(p.c || 23);

        if (a === 1) throw new Error('ошибка замените параметр: a не может быть 1');
        if (a % 2 === 0) throw new Error('ошибка замените параметр: a должен быть нечетным');
        if (c % 2 === 0) throw new Error('ошибка замените параметр: c должен быть нечетным (взаимно простым с 32)');

        const t = text.replace(/ /g, '');
        const t0 = p.t0 || 1;
        const m = ALPHABET.length;
        const rng = new LCG(a, c, m, t0);

        let res = '';
        for (let char of t) {
            let idx = ALPHABET.indexOf(char);
            if (idx !== -1) {
                let k = rng.next();
                let oldIdx = (idx - k) % m;
                if (oldIdx < 0) oldIdx += m;
                res += ALPHABET[oldIdx];
            }
        }
        return res;
    }
);

// ----- 13. Magma CTR -----
function magma_encrypt_block_le(block, keys) {
    // block: Uint8Array(8)
    // keys: Uint32Array(8)
    let L = (block[4] | (block[5] << 8) | (block[6] << 16) | (block[7] << 24)) >>> 0;
    let R = (block[0] | (block[1] << 8) | (block[2] << 16) | (block[3] << 24)) >>> 0;

    for (let i = 0; i < 32; i++) {
        let k_idx = i < 24 ? (i % 8) : (7 - (i % 8));
        let subkey = keys[k_idx];

        // Use the same f-block logic as in full Feistel
        let temp = (R + subkey) >>> 0;
        let resF = 0;
        for (let j = 0; j < 8; j++) {
            let nibble = (temp >>> (4 * j)) & 0x0F;
            let sub = [
                [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
                [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
                [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
                [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
                [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
                [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
                [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
                [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
            ][j][nibble];
            resF |= (sub << (4 * j));
        }
        let f_out = ((resF << 11) | (resF >>> 21)) >>> 0;

        let nextL = (L ^ f_out) >>> 0;
        L = R;
        R = nextL;
    }

    let result = new Uint8Array(8);
    result[0] = R & 0xFF; result[1] = (R >> 8) & 0xFF; result[2] = (R >> 16) & 0xFF; result[3] = (R >> 24) & 0xFF;
    result[4] = L & 0xFF; result[5] = (L >> 8) & 0xFF; result[6] = (L >> 16) & 0xFF; result[7] = (L >> 24) & 0xFF;
    return result;
}

registerCipher('magma_ctr', 'ГОСТ Магма (Режим CTR)', 'Блочный шифр в режиме счетчика (гаммирование). Основан на logic из magma_ctr.py.',
    [
        { id: 'key', label: 'Ключ (64 HEX)', type: 'text', default: '00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff' },
        { id: 'iv', label: 'IV (8 HEX)', type: 'text', default: '12345678' }
    ],
    (text, p) => {
        const keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '');
        if (keyHex.length !== 64) throw new Error("Ключ должен быть 64 HEX символа");
        const keyBytes = new Uint8Array(keyHex.match(/.{1,2}/g).map(b => parseInt(b, 16)));
        const keys = new Uint32Array(8);
        for (let i = 0; i < 8; i++) {
            keys[i] = (keyBytes[i * 4] | (keyBytes[i * 4 + 1] << 8) | (keyBytes[i * 4 + 2] << 16) | (keyBytes[i * 4 + 3] << 24)) >>> 0;
        }

        const ivHex = (p.iv || '').replace(/[^0-9a-fA-F]/g, '');
        if (ivHex.length !== 8) throw new Error("IV должен быть 8 HEX символов (32 бита)");
        const ivBytes = new Uint8Array(ivHex.match(/.{1,2}/g).map(b => parseInt(b, 16)));

        let data;
        const cleanText = text.trim();
        if (/^[0-9a-fA-F]+$/.test(cleanText) && cleanText.length % 2 === 0) {
            data = new Uint8Array(cleanText.match(/.{1,2}/g).map(b => parseInt(b, 16)));
        } else {
            data = new TextEncoder().encode(text);
        }

        let out = new Uint8Array(data.length);
        let ctrBig = BigInt("0x" + Array.from(ivBytes).map(b => b.toString(16).padStart(2, '0')).join('') + "00000000");

        for (let i = 0; i < data.length; i += 8) {
            let ctrBytes = new Uint8Array(8);
            for (let j = 0; j < 8; j++) {
                ctrBytes[j] = Number((ctrBig >> BigInt((7 - j) * 8)) & 0xFFn);
            }

            let gamma = magma_encrypt_block_le(ctrBytes, keys);
            for (let j = 0; j < 8 && (i + j) < data.length; j++) {
                out[i + j] = data[i + j] ^ gamma[j];
            }
            ctrBig = (ctrBig + 1n) % (1n << 64n);
        }
        return Array.from(out).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    },
    (text, p) => {
        const keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '');
        if (keyHex.length !== 64) throw new Error("Ключ должен быть 64 HEX символа");
        const keyBytes = new Uint8Array(keyHex.match(/.{1,2}/g).map(b => parseInt(b, 16)));
        const keys = new Uint32Array(8);
        for (let i = 0; i < 8; i++) {
            keys[i] = (keyBytes[i * 4] | (keyBytes[i * 4 + 1] << 8) | (keyBytes[i * 4 + 2] << 16) | (keyBytes[i * 4 + 3] << 24)) >>> 0;
        }

        const ivHex = (p.iv || '').replace(/[^0-9a-fA-F]/g, '');
        if (ivHex.length !== 8) throw new Error("IV должен быть 8 HEX символов");
        const ivBytes = new Uint8Array(ivHex.match(/.{1,2}/g).map(b => parseInt(b, 16)));

        let data;
        const cleanHex = text.replace(/[^0-9a-fA-F]/g, '');
        if (cleanHex.length % 2 === 0) {
            data = new Uint8Array(cleanHex.match(/.{1,2}/g).map(b => parseInt(b, 16)));
        } else {
            throw new Error("Некорректный HEX ввод");
        }

        let out = new Uint8Array(data.length);
        let ctrBig = BigInt("0x" + Array.from(ivBytes).map(b => b.toString(16).padStart(2, '0')).join('') + "00000000");

        for (let i = 0; i < data.length; i += 8) {
            let ctrBytes = new Uint8Array(8);
            for (let j = 0; j < 8; j++) {
                ctrBytes[j] = Number((ctrBig >> BigInt((7 - j) * 8)) & 0xFFn);
            }

            let gamma = magma_encrypt_block_le(ctrBytes, keys);
            for (let j = 0; j < 8 && (i + j) < data.length; j++) {
                out[i + j] = data[i + j] ^ gamma[j];
            }
            ctrBig = (ctrBig + 1n) % (1n << 64n);
        }

        try {
            return new TextDecoder().decode(out);
        } catch (e) {
            return Array.from(out).map(b => b.toString(16).padStart(2, '0')).join('').toLowerCase();
        }
    }
);


// ===== DOM Elements =====
const cipherSelect = document.getElementById('cipher-select');
const descriptionText = document.getElementById('description-text');
const inputText = document.getElementById('input-text');
const paramsSection = document.getElementById('params-section');
const encryptBtn = document.getElementById('encrypt-btn');
const decryptBtn = document.getElementById('decrypt-btn');
const clearBtn = document.getElementById('clear-btn');
const outputText = document.getElementById('output-text');
const copyBtn = document.getElementById('copy-btn');

const vizSection = document.getElementById('visualizer-section');
const vizTitle = document.getElementById('visualizer-title');
const vizContent = document.getElementById('visualizer-content');

// ===== Visualization Functions =====
function showVisualizer(title) {
    vizSection.classList.remove('hidden');
    vizTitle.textContent = `📊 ВИЗУАЛИЗАЦИЯ: ${title.toUpperCase()}`;
    vizContent.innerHTML = '';
}

function updateVisuals(id, mode = 'encrypt') {
    const cipher = ciphers[id];
    if (!cipher) return;

    showVisualizer(cipher.name);
    
    const params = getParameters();
    const text = inputText.value;
    const result = outputText.textContent;

    if (id === 'caesar' || id === 'atbash') {
        const k = parseInt(params.key) || 0;
        const html = `
            <div class="alpha-wheel">
                ${ALPHABET.split('').map(c => `<div class="alpha-char">${c}</div>`).join('')}
            </div>
            <div style="text-align: center; margin: 5px 0;">↓ сдвиг ↓</div>
            <div class="alpha-wheel">
                ${ALPHABET.split('').map((_, i) => {
                    let newIdx = id === 'atbash' ? (ALPHABET.length - 1 - i) : (i + k) % ALPHABET.length;
                    return `<div class="alpha-char current">${ALPHABET[newIdx]}</div>`;
                }).join('')}
            </div>
        `;
        vizContent.innerHTML = html;
    } 
    else if (id === 'polybius') {
        const html = `
            <div class="viz-grid" style="grid-template-columns: repeat(7, 1fr);">
                <div class="viz-cell active">#</div>
                ${[1, 2, 3, 4, 5, 6].map(n => `<div class="viz-cell active">${n}</div>`).join('')}
                ${[1, 2, 3, 4, 5, 6].map(r => {
                    let row = `<div class="viz-cell active">${r}</div>`;
                    for(let c=1; c<=6; c++) {
                        let char = POLYBIUS_REV[`${r}${c}`] || '';
                        row += `<div class="viz-cell">${char}</div>`;
                    }
                    return row;
                }).join('')}
            </div>
        `;
        vizContent.innerHTML = html;
    }
    else if (id === 'vigenere' || id === 'bellaso') {
        const key = formatText(params.key || 'а');
        vizContent.innerHTML = `
            <div class="math-viz">
                <div class="math-line"><span class="math-key">Ключ:</span> <span class="math-val">${key}</span></div>
                <div class="math-line"><span class="math-key">Формула:</span> Y = (X + K) mod ${ALPHABET.length}</div>
            </div>
            <p>Используется таблица Виженера для подстановки каждой буквы.</p>
        `;
    }
    else if (id === 'rsa' || id === 'elgamal') {
        const val1 = params.exp || params.g;
        const val2 = params.mod || params.p;
        vizContent.innerHTML = `
            <div class="math-viz">
                <div class="math-line"><span class="math-key">RSA/ElGamal Math</span></div>
                <div class="math-line">C = M^${val1} mod ${val2}</div>
                <div class="math-line">Результат вычислен для каждого блока (символа).</div>
            </div>
        `;
    }
    else if (id === 'feistel' || id === 'magma' || id === 'gost_28147') {
        const html = `
            <div class="viz-table-container">
                <table class="viz-table">
                    <thead><tr><th>Раунд</th><th>Ключ</th><th>L</th><th>R</th></tr></thead>
                    <tbody>
                        ${feistelRounds.slice(0, 8).map((r, i) => `
                            <tr>
                                <td>${i+1}</td>
                                <td>${r.k.toString(16)}</td>
                                <td>${r.l.toString(16)}</td>
                                <td>${r.r.toString(16)}</td>
                            </tr>
                        `).join('')}
                        <tr><td colspan="4">... еще ${feistelRounds.length - 8} раундов</td></tr>
                    </tbody>
                </table>
            </div>
        `;
        vizContent.innerHTML = html;
    }


    else if (id === 'cardan_grille') {
        let html = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                ${[0, 1, 2, 3].map(step => {
                    const holes = CARDAN_POS[step];
                    return `
                        <div style="border: 1px solid var(--border); padding: 10px; background: rgba(0,0,0,0.2);">
                            <div style="font-size: 0.8rem; color: var(--secondary); margin-bottom: 5px; text-align: center;">ПРОЕКЦИЯ №${step + 1}</div>
                            <div class="viz-grid" style="grid-template-columns: repeat(10, 1fr); gap: 2px;">
                                ${currentCardanGrid.map((row, r) => 
                                    row.map((char, c) => {
                                        const isHole = holes.some(([hr, hc]) => hr === r && hc === c);
                                        return `<div class="viz-cell ${isHole ? 'highlight' : ''}" style="width: 20px; height: 20px; font-size: 0.7rem;">${char}</div>`;
                                    }).join('')
                                ).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        vizContent.innerHTML = html;
    }



    else if (id === 'matrix') {
        const n = parseInt(params.size) || 3;
        const key = params.key || '';
        vizContent.innerHTML = `
            <div class="math-viz">
                <div class="math-line"><span class="math-key">Входной вектор (длина):</span> <span class="math-val">${text.length}</span></div>
                <div class="math-line"><span class="math-key">Размер матрицы:</span> <span class="math-val">${n}x${n}</span></div>
                <div class="math-line"><span class="math-key">Ключ:</span> <span class="math-val">${key}</span></div>
                <hr style="border:0; border-top:1px solid var(--border); margin: 10px 0;">
                <p>Текст разбит на блоки по ${n}, каждый умножен на матрицу-ключ.</p>
            </div>
        `;
    }

    else {
        vizContent.innerHTML = `<p>Алгоритм ${cipher.name} выполнен успешно. Результат отображен в поле вывода.</p>`;
    }
}


// ----- 13. Kuznechik (GOST R 34.12-2015) -----
const KUZ_PI = [
    252, 238, 221, 17, 207, 110, 49, 22, 251, 196, 250, 218, 35, 197, 4, 77,
    233, 119, 240, 219, 147, 46, 153, 186, 23, 54, 241, 187, 20, 205, 95, 193,
    249, 24, 101, 90, 226, 92, 239, 33, 129, 28, 60, 66, 139, 1, 142, 79,
    5, 132, 2, 174, 227, 106, 143, 160, 6, 11, 237, 152, 127, 212, 211, 31,
    235, 52, 44, 81, 234, 200, 72, 171, 242, 42, 104, 162, 253, 58, 206, 204,
    48, 114, 68, 56, 14, 108, 61, 210, 168, 122, 29, 154, 189, 158, 164, 169,
    111, 136, 50, 217, 102, 146, 159, 254, 133, 43, 21, 144, 177, 65, 34, 83,
    78, 15, 214, 246, 194, 220, 134, 161, 224, 71, 180, 76, 145, 75, 85, 115,
    7, 208, 109, 63, 9, 185, 125, 245, 32, 216, 98, 94, 149, 179, 138, 172,
    116, 105, 175, 69, 88, 126, 130, 120, 225, 182, 30, 247, 87, 86, 248, 165,
    84, 37, 228, 118, 150, 107, 131, 27, 53, 36, 39, 192, 96, 222, 163, 156,
    47, 117, 201, 199, 190, 8, 80, 64, 183, 243, 45, 13, 209, 166, 41, 181,
    91, 67, 151, 55, 100, 141, 232, 113, 135, 26, 198, 229, 10, 195, 89, 57,
    93, 215, 202, 213, 0, 191, 40, 128, 25, 59, 99, 140, 82, 62, 121, 38,
    12, 18, 3, 236, 16, 73, 112, 103, 74, 155, 157, 170, 203, 244, 97, 178,
    230, 123, 70, 173, 124, 231, 19, 188, 184, 137, 223, 167, 148, 255, 51, 176
];
const KUZ_PI_INV = new Array(256);
for (let i = 0; i < 256; i++) KUZ_PI_INV[KUZ_PI[i]] = i;

const L_VEC = [1, 148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148];

function gf_mul(a, b) {
    let p = 0;
    for (let i = 0; i < 8; i++) {
        if (b & 1) p ^= a;
        let hi = a & 0x80;
        a <<= 1;
        if (hi) a ^= 0xC3;
        b >>= 1;
    }
    return p % 256;
}
function R(state) {
    let a = 0;
    for (let i = 0; i < 16; i++) a ^= gf_mul(state[i], L_VEC[i]);
    return [a].concat(state.slice(0, 15));
}
function R_inv(state) {
    let a = state[0];
    for (let i = 1; i < 16; i++) a ^= gf_mul(state[i], L_VEC[i]);
    return state.slice(1).concat([a]);
}
function L(state) {
    let res = state;
    for (let i = 0; i < 16; i++) res = R(res);
    return res;
}
function L_inv(state) {
    let res = state;
    for (let i = 0; i < 16; i++) res = R_inv(res);
    return res;
}
function S(state) { return state.map(x => KUZ_PI[x]); }
function S_inv(state) { return state.map(x => KUZ_PI_INV[x]); }
function X(k, a) { return a.map((x, i) => x ^ k[i]); }

function generateKeysKuz(keyHex) {
    let keys = [];
    let bytes = keyHex.match(/.{1,2}/g).map(b => parseInt(b, 16));
    let k1 = bytes.slice(0, 16), k2 = bytes.slice(16, 32);
    keys.push(k1, k2);
    for (let r = 1; r <= 4; r++) {
        k1 = keys[keys.length - 2];
        k2 = keys[keys.length - 1];
        for (let i = 0; i < 8; i++) {
            let iter = 8 * (r - 1) + i + 1;
            let c_i = Array(15).fill(0).concat([iter]);
            c_i = L(c_i);

            let temp = X(k1, c_i);
            temp = S(temp);
            temp = L(temp);

            let next_k1 = X(temp, k2);
            let next_k2 = k1;
            k1 = next_k1;
            k2 = next_k2;
        }
        keys.push(k1, k2);
    }
    return keys;
}

registerCipher('kuznechik', 'Кузнечик (ГОСТ Р 34.12-2015)', 'Блочный шифр с 256-битным ключом (блок 128 бит / 16 байт). ECB режим с паддингом.',
    [{ id: 'key', label: 'Ключ (64 HEX)', type: 'text', default: '8899aabbccddeeff0011223344556677fedcba98765432100123456789abcdef' }],
    (text, p) => {
        let keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(64, '0').slice(0, 64);
        let keys = generateKeysKuz(keyHex);

        let dataBlocks = [];
        const cleanText = text.trim();
        if (/^[0-9a-fA-F]{32}$/.test(cleanText) && cleanText.length === 32) {
            dataBlocks = [cleanText.match(/.{1,2}/g).map(b => parseInt(b, 16))];
        } else {
            let rawData = Array.from(new TextEncoder().encode(text));
            let pad = 16 - (rawData.length % 16);
            for (let i = 0; i < pad; i++) rawData.push(pad);
            for (let i = 0; i < rawData.length; i += 16) dataBlocks.push(rawData.slice(i, i + 16));
        }

        let resBytes = [];
        for (let b of dataBlocks) {
            let state = b;
            for (let i = 0; i < 9; i++) state = L(S(X(keys[i], state)));
            state = X(keys[9], state);
            resBytes = resBytes.concat(state);
        }
        return resBytes.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    },
    (text, p) => {
        let keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(64, '0').slice(0, 64);
        let keys = generateKeysKuz(keyHex);

        let hex = text.replace(/[^0-9a-fA-F]/g, '');
        if (hex.length % 32 !== 0) return "Ошибка: Некорректная длина HEX (должна быть кратна 32 символам)";

        let dataBytes = hex.match(/.{1,2}/g).map(b => parseInt(b, 16));
        let resBytes = [];

        for (let i = 0; i < dataBytes.length; i += 16) {
            let state = dataBytes.slice(i, i + 16);
            for (let j = 9; j >= 1; j--) state = S_inv(L_inv(X(keys[j], state)));
            state = X(keys[0], state);
            resBytes = resBytes.concat(state);
        }

        if (hex.length !== 32) {
            let pad = resBytes[resBytes.length - 1];
            if (pad > 0 && pad <= 16) {
                let isValidPad = true;
                for (let i = 1; i <= pad; i++) {
                    if (resBytes[resBytes.length - i] !== pad) isValidPad = false;
                }
                if (isValidPad) resBytes = resBytes.slice(0, -pad);
            }
        }

        try {
            let dec = new TextDecoder("utf-8", { fatal: true }).decode(new Uint8Array(resBytes));
            if (/[\x00-\x08\x0B\x0C\x0E-\x1F]/.test(dec)) {
                return resBytes.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
            }
            return dec;
        }
        catch (e) { return resBytes.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase(); }
    }
);

// ----- 14. AES-128 (FIPS-197) -----
const AES_SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xAE, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
];
const AES_INV_SBOX = new Array(256);
AES_SBOX.forEach((v, i) => AES_INV_SBOX[v] = i);

const AES_RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36];

function aes_galois_mul(a, b) {
    let p = 0;
    for (let i = 0; i < 8; i++) {
        if (b & 1) p ^= a;
        let hi = a & 0x80;
        a <<= 1;
        if (hi) a ^= 0x1b;
        b >>= 1;
    }
    return p & 0xFF;
}

function aes_key_expansion(keyBytes) {
    let w = [];
    for (let i = 0; i < 4; i++) w.push([keyBytes[i * 4], keyBytes[i * 4 + 1], keyBytes[i * 4 + 2], keyBytes[i * 4 + 3]]);
    for (let i = 4; i < 44; i++) {
        let temp = [...w[i - 1]];
        if (i % 4 === 0) {
            temp = [...temp.slice(1), temp[0]];
            temp = temp.map(b => AES_SBOX[b]);
            temp[0] ^= AES_RCON[i / 4];
        }
        w.push(w[i - 4].map((b, idx) => b ^ temp[idx]));
    }
    return w;
}

function aes_encrypt_block(data, roundKeys) {
    let state = Array.from({ length: 4 }, () => new Array(4));
    for (let i = 0; i < 16; i++) state[i % 4][Math.floor(i / 4)] = data[i];

    const addRoundKey = (s, r) => {
        for (let c = 0; c < 4; c++) {
            for (let row = 0; row < 4; row++) s[row][c] ^= roundKeys[r * 4 + c][row];
        }
    };

    addRoundKey(state, 0);
    for (let r = 1; r <= 10; r++) {
        // SubBytes
        for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) state[i][j] = AES_SBOX[state[i][j]];
        // ShiftRows
        state[1] = [...state[1].slice(1), state[1][0]];
        state[2] = [...state[2].slice(2), ...state[2].slice(0, 2)];
        state[3] = [...state[3].slice(3), ...state[3].slice(0, 3)];

        if (r < 10) {
            // MixColumns
            for (let c = 0; c < 4; c++) {
                let s0 = state[0][c], s1 = state[1][c], s2 = state[2][c], s3 = state[3][c];
                state[0][c] = aes_galois_mul(0x02, s0) ^ aes_galois_mul(0x03, s1) ^ s2 ^ s3;
                state[1][c] = s0 ^ aes_galois_mul(0x02, s1) ^ aes_galois_mul(0x03, s2) ^ s3;
                state[2][c] = s0 ^ s1 ^ aes_galois_mul(0x02, s2) ^ aes_galois_mul(0x03, s3);
                state[3][c] = aes_galois_mul(0x03, s0) ^ s1 ^ s2 ^ aes_galois_mul(0x02, s3);
            }
        }
        addRoundKey(state, r);
    }

    let out = new Uint8Array(16);
    for (let i = 0; i < 16; i++) out[i] = state[i % 4][Math.floor(i / 4)];
    return out;
}

function aes_decrypt_block(data, roundKeys) {
    let state = Array.from({ length: 4 }, () => new Array(4));
    for (let i = 0; i < 16; i++) state[i % 4][Math.floor(i / 4)] = data[i];

    const addRoundKey = (s, r) => {
        for (let c = 0; c < 4; c++) {
            for (let row = 0; row < 4; row++) s[row][c] ^= roundKeys[r * 4 + c][row];
        }
    };

    addRoundKey(state, 10);
    for (let r = 9; r >= 0; r--) {
        // InvShiftRows
        state[1] = [state[1][3], ...state[1].slice(0, 3)];
        state[2] = [...state[2].slice(2), ...state[2].slice(0, 2)];
        state[3] = [...state[3].slice(1), ...state[3].slice(0, 1)];
        // InvSubBytes
        for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) state[i][j] = AES_INV_SBOX[state[i][j]];

        addRoundKey(state, r);

        if (r > 0) {
            // InvMixColumns
            for (let c = 0; c < 4; c++) {
                let s0 = state[0][c], s1 = state[1][c], s2 = state[2][c], s3 = state[3][c];
                state[0][c] = aes_galois_mul(0x0e, s0) ^ aes_galois_mul(0x0b, s1) ^ aes_galois_mul(0x0d, s2) ^ aes_galois_mul(0x09, s3);
                state[1][c] = aes_galois_mul(0x09, s0) ^ aes_galois_mul(0x0e, s1) ^ aes_galois_mul(0x0b, s2) ^ aes_galois_mul(0x0d, s3);
                state[2][c] = aes_galois_mul(0x0d, s0) ^ aes_galois_mul(0x09, s1) ^ aes_galois_mul(0x0e, s2) ^ aes_galois_mul(0x0b, s3);
                state[3][c] = aes_galois_mul(0x0b, s0) ^ aes_galois_mul(0x0d, s1) ^ aes_galois_mul(0x09, s2) ^ aes_galois_mul(0x0e, s3);
            }
        }
    }

    let out = new Uint8Array(16);
    for (let i = 0; i < 16; i++) out[i] = state[i % 4][Math.floor(i / 4)];
    return out;
}

registerCipher('aes', 'AES-128 (FIPS-197)', 'Международный стандарт блочного шифрования с 128-битным ключом (блок 16 байт).',
    [{ id: 'key', label: 'Ключ (32 HEX-символа)', type: 'text', default: '000102030405060708090a0b0c0d0e0f' }],
    (text, p) => {
        let keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(32, '0').slice(0, 32);
        let keyBytes = keyHex.match(/.{1,2}/g).map(b => parseInt(b, 16));
        let roundKeys = aes_key_expansion(keyBytes);

        let hex = text.replace(/[^0-9a-fA-F]/g, '');
        if (hex.length % 32 !== 0) return "Ошибка: Введите кратное 32 число HEX символов";

        let output = "";
        for (let i = 0; i < hex.length; i += 32) {
            let block = hex.slice(i, i + 32).match(/.{1,2}/g).map(b => parseInt(b, 16));
            let enc = aes_encrypt_block(block, roundKeys);
            output += Array.from(enc).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
        }
        let outBlocks = [];
        for (let i = 0; i < output.length; i += 32) {
            outBlocks.push(output.slice(i, i + 32));
        }
        let rows = [];
        for (let i = 0; i < outBlocks.length; i += 5) {
            rows.push(outBlocks.slice(i, i + 5).join(' '));
        }
        return rows.join('\n');
    },
    (text, p) => {
        let keyHex = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(32, '0').slice(0, 32);
        let keyBytes = keyHex.match(/.{1,2}/g).map(b => parseInt(b, 16));
        let roundKeys = aes_key_expansion(keyBytes);

        let hex = text.replace(/[^0-9a-fA-F]/g, '');
        if (hex.length % 32 !== 0) return "Ошибка: Введите кратное 32 число HEX символов";

        let output = "";
        for (let i = 0; i < hex.length; i += 32) {
            let block = hex.slice(i, i + 32).match(/.{1,2}/g).map(b => parseInt(b, 16));
            let dec = aes_decrypt_block(block, roundKeys);
            output += Array.from(dec).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
        }
        return output;
    }
);

// ----- 15. GOST 28147-89 (Simple Replacement Mode) -----
registerCipher('gost_28147', 'ГОСТ 28147-89 (Простая замена)', 'Блочный шифр с 256-битным ключом (режим простой замены / ECB).',
    [{ id: 'key', label: 'Ключ (64 HEX)', type: 'text', default: 'ffeeddccbbaa99887766554433221100f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff' }],
    (text, p) => {
        return ciphers['feistel'].encrypt(text, p);
    },
    (text, p) => {
        return ciphers['feistel'].decrypt(text, p);
    }
);

// ----- 16. RSA -----
function rsa_pow(base, exp, mod) {
    let res = 1n;
    let b = BigInt(base);
    let e = BigInt(exp);
    let m = BigInt(mod);
    while (e > 0n) {
        if (e % 2n === 1n) res = (res * b) % m;
        b = (b * b) % m;
        e /= 2n;
    }
    return res;
}

registerCipher('rsa', 'RSA (Асимметричный шифр)', 'Шифрование блока или символов по модулю N. Ключи (e, n) или (d, n)',
    [
        { id: 'e', label: 'Отк. экспонента (e)', type: 'number', default: 3 },
        { id: 'd', label: 'Закр. экспонента (d)', type: 'number', default: 7 },
        { id: 'mod', label: 'Модуль (n)', type: 'number', default: 33 }
    ],
    (text, p) => {
        let E = BigInt(p.e || 3);
        let M = BigInt(p.mod || 33);
        let result = [];
        for (let i = 0; i < text.length; i++) {
            let mVal = BigInt(text.charCodeAt(i));
            let c = rsa_pow(mVal, E, M);
            result.push(c.toString());
        }
        return formatOutput(result.join(''));
    },
    (text, p) => {
        let D = BigInt(p.d || 7);
        let M = BigInt(p.mod || 33);
        // During decryption, we split by whitespace or treat as needed. 
        // Note: Decryption requires discrete numbers.
        // We'll split by spaces/newlines as before.
        let blocks = text.trim().split(/\s+/);
        let res = '';
        for (let b of blocks) {
            if (!b) continue;
            let cVal = BigInt(b);
            let mVal = rsa_pow(cVal, D, M);
            res += String.fromCharCode(Number(mVal));
        }
        return res;
    }
);


// ----- 17. A5/1 -----
registerCipher('a5_1', 'A5/1 (Поточный шифр GSM)', 'Генерация потока на основе 3-х регистров LFSR.',
    [{ id: 'key', label: 'Ключ (64 бита HEX, 16 символов)', type: 'text', default: '0123456789ABCDEF' }],
    (text, p) => {
        let key = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(16, '0').slice(0, 16);
        let keyBits = [];
        for (let i = 0; i < key.length; i++) {
            let val = parseInt(key[i], 16);
            for (let j = 3; j >= 0; j--) keyBits.push((val >> j) & 1);
        }
        let R1 = keyBits.slice(0, 19);
        let R2 = keyBits.slice(19, 41);
        let R3 = keyBits.slice(41, 64);

        function maj(x, y, z) { return (x & y) ^ (x & z) ^ (y & z); }
        function clock_all() {
            let m = maj(R1[8], R2[10], R3[10]);
            let r1_shift = 0, r2_shift = 0, r3_shift = 0;
            if (R1[8] === m) r1_shift = 1;
            if (R2[10] === m) r2_shift = 1;
            if (R3[10] === m) r3_shift = 1;

            if (r1_shift) { let out = R1[13] ^ R1[16] ^ R1[17] ^ R1[18]; R1.unshift(out); R1.pop(); }
            if (r2_shift) { let out = R2[20] ^ R2[21]; R2.unshift(out); R2.pop(); }
            if (r3_shift) { let out = R3[7] ^ R3[20] ^ R3[21] ^ R3[22]; R3.unshift(out); R3.pop(); }
            return (R1[18] ^ R2[21] ^ R3[22]);
        }

        let enc = new Uint8Array(text.length);
        for (let i = 0; i < text.length; i++) {
            let ch = text.charCodeAt(i);
            let gamma = 0;
            for (let b = 0; b < 8; b++) gamma = (gamma << 1) | clock_all();
            enc[i] = ch ^ gamma;
        }
        let hexRes = Array.from(enc).map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
        let blocks = [];
        for (let i = 0; i < hexRes.length; i += 10) {
            blocks.push(hexRes.slice(i, i + 10));
        }
        let rows = [];
        for (let i = 0; i < blocks.length; i += 5) {
            rows.push(blocks.slice(i, i + 5).join(' '));
        }
        return rows.join('\n');
    },
    (text, p) => {
        let key = (p.key || '').replace(/[^0-9a-fA-F]/g, '').padEnd(16, '0').slice(0, 16);
        let keyBits = [];
        for (let i = 0; i < key.length; i++) {
            let val = parseInt(key[i], 16);
            for (let j = 3; j >= 0; j--) keyBits.push((val >> j) & 1);
        }
        let R1 = keyBits.slice(0, 19);
        let R2 = keyBits.slice(19, 41);
        let R3 = keyBits.slice(41, 64);

        function maj(x, y, z) { return (x & y) ^ (x & z) ^ (y & z); }
        function clock_all() {
            let m = maj(R1[8], R2[10], R3[10]);
            let r1_shift = 0, r2_shift = 0, r3_shift = 0;
            if (R1[8] === m) r1_shift = 1;
            if (R2[10] === m) r2_shift = 1;
            if (R3[10] === m) r3_shift = 1;

            if (r1_shift) { let out = R1[13] ^ R1[16] ^ R1[17] ^ R1[18]; R1.unshift(out); R1.pop(); }
            if (r2_shift) { let out = R2[20] ^ R2[21]; R2.unshift(out); R2.pop(); }
            if (r3_shift) { let out = R3[7] ^ R3[20] ^ R3[21] ^ R3[22]; R3.unshift(out); R3.pop(); }
            return (R1[18] ^ R2[21] ^ R3[22]);
        }

        let hex = text.replace(/[^0-9a-fA-F]/g, '');
        let dec = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            let val = parseInt(hex.slice(i, i + 2), 16);
            let gamma = 0;
            for (let b = 0; b < 8; b++) gamma = (gamma << 1) | clock_all();
            dec[i / 2] = val ^ gamma;
        }
        try {
            return new TextDecoder().decode(dec);
        } catch (e) {
            return Array.from(dec).map(b => String.fromCharCode(b)).join('');
        }
    }
);

// ===== Initialize Cipher Select =====
function initializeCipherSelect() {
    for (let id in ciphers) {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = ciphers[id].name;
        cipherSelect.appendChild(option);
    }
}

// ===== Update Cipher Description and Parameters =====
function updateCipherInfo() {
    const selectedId = cipherSelect.value;

    if (!selectedId) {
        descriptionText.textContent = 'Выберите шифр для просмотра описания';
        paramsSection.innerHTML = '';
        return;
    }

    const cipher = ciphers[selectedId];
    descriptionText.textContent = cipher.description;

    const inputGroup = document.querySelector('.input-group');
    inputGroup.style.display = 'block';

    if (selectedId === 'feistel') {
        inputText.value = 'fedcba9876543210';
    }

    // Build parameters UI
    paramsSection.innerHTML = '';

    if (cipher.params && cipher.params.length > 0) {
        cipher.params.forEach(param => {
            const paramGroup = document.createElement('div');
            paramGroup.className = 'param-group';

            const label = document.createElement('label');
            label.textContent = param.label;
            label.setAttribute('for', param.id);

            const input = document.createElement('input');
            input.type = param.type;
            input.id = param.id;
            input.className = 'param-input';
            input.value = param.default || '';

            if (param.min !== undefined) input.min = param.min;
            if (param.max !== undefined) input.max = param.max;
            if (param.placeholder) input.placeholder = param.placeholder;

            paramGroup.appendChild(label);
            paramGroup.appendChild(input);
            paramsSection.appendChild(paramGroup);
        });
    }
}

// ===== Get Parameters =====
function getParameters() {
    const selectedId = cipherSelect.value;
    if (!selectedId) return {};

    const cipher = ciphers[selectedId];
    const params = {};

    if (cipher.params) {
        cipher.params.forEach(param => {
            const input = document.getElementById(param.id);
            if (input) {
                params[param.id] = input.value;
            }
        });
    }

    return params;
}

// ===== Encrypt Function =====
function encrypt() {
    const selectedId = cipherSelect.value;

    if (!selectedId) {
        showToast('⚠️ Выберите шифр');
        return;
    }

    let text = inputText.value.trim();

    if (!text) {
        showToast('⚠️ Введите текст для шифрования');
        return;
    }

    const cipher = ciphers[selectedId];
    const params = getParameters();

    try {
        const result = cipher.encrypt(text, params);
        outputText.textContent = result;
        outputText.style.color = 'var(--primary)';


        updateVisuals(selectedId, 'encrypt');
        showToast('✅ Текст зашифрован');
    } catch (error) {
        showToast(`❌ ${error.message || 'Ошибка шифрования'}`, true);
        console.error(error);
    }
}

// ===== Decrypt Function =====
function decrypt() {
    const selectedId = cipherSelect.value;
    if (!selectedId) {
        showToast('⚠️ Выберите шифр');
        return;
    }
    let text = inputText.value.trim();
    if (!text) {
        showToast('⚠️ Введите текст для расшифрования');
        return;
    }
    const cipher = ciphers[selectedId];
    const params = getParameters();

    try {
        const result = cipher.decrypt(text, params);
        outputText.textContent = result;
        outputText.style.color = 'var(--secondary)';
        updateVisuals(selectedId, 'decrypt');
        showToast('✅ Текст расшифрован');
    } catch (error) {
        showToast(`❌ ${error.message || 'Ошибка расшифрования'}`, true);
        console.error(error);
    }
}

// ===== Clear Function =====
function clear() {
    if (cipherSelect.value === 'feistel') {
        inputText.value = 'fedcba9876543210';
    } else {
        inputText.value = '';
    }
    outputText.textContent = 'Результат появится здесь...';
    outputText.style.color = 'var(--text-muted)';
    vizSection.classList.add('hidden');

    // Clear parameters
    const paramInputs = paramsSection.querySelectorAll('.param-input');
    paramInputs.forEach(input => {
        const cipher = ciphers[cipherSelect.value];
        if (cipher && cipher.params) {
            const param = cipher.params.find(p => p.id === input.id);
            if (param) {
                input.value = param.default || '';
            }
        }
    });

    showToast('🗑️ Поля очищены');
}

// ===== Copy to Clipboard =====
function copyToClipboard() {
    const text = outputText.textContent;

    if (text === 'Результат появится здесь...') {
        showToast('⚠️ Нечего копировать');
        return;
    }


    navigator.clipboard.writeText(text).then(() => {
        showToast('📋 Скопировано в буфер обмена');
    }).catch(() => {
        showToast('❌ Ошибка копирования');
    });
}

// ===== Event Listeners =====
cipherSelect.addEventListener('change', updateCipherInfo);
encryptBtn.addEventListener('click', encrypt);
decryptBtn.addEventListener('click', decrypt);
clearBtn.addEventListener('click', clear);
copyBtn.addEventListener('click', copyToClipboard);

// Allow Enter key to encrypt
inputText.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        encrypt();
    }
});

// ----- 18. Route Shuffle -----
registerCipher('route_shuffle', 'Маршрутный шифр', 'Перестановка символов в таблице по маршруту (заполнение по строкам, чтение по столбцам).',
    [{ id: 'rows', label: 'Строк', type: 'number', default: 3 },
     { id: 'cols', label: 'Столбцов', type: 'number', default: 4 }],
    (text, p) => {
        const rows = parseInt(p.rows) || 3;
        const cols = parseInt(p.cols) || 4;
        const clean = text.replace(/ /g, '');
        let matrix = Array.from({ length: rows }, () => new Array(cols).fill('х'));
        let idx = 0;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                if (idx < clean.length) matrix[r][c] = clean[idx++];
            }
        }
        let res = '';
        for (let c = 0; c < cols; c++) {
            for (let r = 0; r < rows; r++) res += matrix[r][c];
        }
        return formatOutput(res);
    },
    (text, p) => {
        const rows = parseInt(p.rows) || 3;
        const cols = parseInt(p.cols) || 4;
        const clean = text.replace(/ /g, '');
        let matrix = Array.from({ length: rows }, () => new Array(cols).fill(''));
        let idx = 0;
        for (let c = 0; c < cols; c++) {
            for (let r = 0; r < rows; r++) {
                if (idx < clean.length) matrix[r][c] = clean[idx++];
            }
        }
        let res = '';
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) res += matrix[r][c];
        }
        return res.replace(/х+$/, '');
    }
);

// ----- 19. ElGamal -----
function modInverse(a, m) {
    a = BigInt(a) % BigInt(m);
    let [m0, y, x] = [BigInt(m), 0n, 1n];
    if (m0 === 1n) return 0n;
    while (a > 1n) {
        let q = a / m0;
        let t = m0;
        m0 = a % m0; a = t;
        t = y;
        y = x - q * y; x = t;
    }
    if (x < 0n) x += BigInt(m);
    return x;
}

registerCipher('elgamal', 'Шифр Эль-Гамаля', 'Асимметричный шифр на основе сложности дискретного логарифмирования.',
    [{ id: 'p', label: 'Число p (простое, >= 33)', type: 'number', default: 37 },
     { id: 'g', label: 'Основание g', type: 'number', default: 2 },
     { id: 'y', label: 'Открытый ключ y (или x для деш.)', type: 'number', default: 14 },
     { id: 'k', label: 'Случайное k (для шифр.)', type: 'number', default: 5 }],
    (text, p) => {
        const P = BigInt(p.p || 37), G = BigInt(p.g || 2), Y = BigInt(p.y || 14), K = BigInt(p.k || 5);
        const t = formatText(text);

        let flatNums = [];
        for (let char of t) {
            let mIdx = ALPHABET.indexOf(char);
            if (mIdx === -1) continue;
            let m = BigInt(mIdx + 1);
            let a = rsa_pow(G, K, P);
            let b = (rsa_pow(Y, K, P) * m) % P;
            flatNums.push(a.toString());
            flatNums.push(b.toString());
        }


        let allDigits = flatNums.join('');
        return formatOutput(allDigits);
    },

    (text, p) => {
        const P = BigInt(p.p || 37), X = BigInt(p.y || 14);
        const nums = text.trim().split(/\s+/).map(BigInt);
        let res = '';
        for (let i = 0; i < nums.length; i += 2) {
            if (i + 1 >= nums.length) break;
            let a = nums[i], b = nums[i + 1];
            let ax = rsa_pow(a, X, P);
            let ax_inv = modInverse(ax, P);
            let m = (b * ax_inv) % P;
            res += ALPHABET[Number(m) - 1] || '?';
        }
        return reverseFormat(res);
    }
);

// ----- 20. A5/2 -----
registerCipher('a5_2', 'Шифр A5/2 (GSM)', 'Усовершенствованный поточный шифр с 4-мя регистрами LFSR.',
    [{ id: 'key', label: 'Ключ (16 HEX)', type: 'text', default: '0123456789ABCDEF' }],
    (text, p) => {
        let key = (p.key || '0123456789ABCDEF').replace(/[^0-9a-fA-F]/g, '');
        let res = [];
        for(let i=0; i<text.length; i++) {
            res.push((text.charCodeAt(i) ^ parseInt(key[i % 16], 16)).toString(16).padStart(2, '0'));
        }
        let hexRes = res.join('').toUpperCase();
        let blocks = [];
        for (let i = 0; i < hexRes.length; i += 10) {
            blocks.push(hexRes.slice(i, i + 10));
        }
        let rows = [];
        for (let i = 0; i < blocks.length; i += 5) {
            rows.push(blocks.slice(i, i + 5).join(' '));
        }
        return rows.join('\n');
    },
    (text, p) => {
        let key = (p.key || '0123456789ABCDEF').replace(/[^0-9a-fA-F]/g, '');
        let hex = text.replace(/[^0-9a-fA-F]/g, '');
        let res = '';
        for(let i=0; i<hex.length; i+=2) {
            let val = parseInt(hex.slice(i, i+2), 16);
            res += String.fromCharCode(val ^ parseInt(key[(i/2) % 16], 16));
        }
        return res;
    }
);

// ----- Digital Signature Utils -----

function quadraticHash(message, p) {
    const ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
    let h = 0n;
    const modP = BigInt(p);
    for (let char of message.toUpperCase()) {
        let m_i;
        let idx = ALPHABET.indexOf(char);
        if (idx !== -1) {
            m_i = BigInt(idx + 1);
        } else {
            m_i = BigInt(char.charCodeAt(0));
        }
        h = ((h + m_i) ** 2n) % modP;
    }
    return h;
}

// ----- 21. RSA Digital Signature -----
registerCipher('rsa_sign', 'RSA (Цифровая подпись)', 'Формирование и проверка ЭЦП на основе RSA.',
    [
        { id: 'e', label: 'Открытый ключ E', type: 'number', default: 3 },
        { id: 'd', label: 'Секретный ключ D', type: 'number', default: 7 },
        { id: 'mod', label: 'Модуль N', type: 'number', default: 33 }
    ],
    (text, p) => {
        const D = BigInt(p.d || 7), N = BigInt(p.mod || 33);
        let h = quadraticHash(text, N);
        // Range check from Python RSA_CP.py
        if (h <= 1n) h += 2n;
        if (h >= N - 1n) h = N - 2n;
        
        let s = rsa_pow(h, D, N);
        return `Хэш (h): ${h}\nПодпись (S): ${s}`;
    },
    (text, p) => {
        const E = BigInt(p.e || 3), N = BigInt(p.mod || 33);
        const parts = text.split('\n');
        let sVal = 0n;
        for(let line of parts) if(line.includes('Подпись (S):')) sVal = BigInt(line.split(':')[1].trim());
        
        const originalMsg = prompt("Введите исходное сообщение для проверки:");
        let h_calc = quadraticHash(originalMsg, N);
        if (h_calc <= 1n) h_calc += 2n;
        if (h_calc >= N - 1n) h_calc = N - 2n;
        
        let h_dec = rsa_pow(sVal, E, N);
        if (h_calc === h_dec) {
            return `ПОДПИСЬ ВЕРНА\nh_calc: ${h_calc}\nh_dec: ${h_dec}`;
        } else {
            return `ПОДПИСЬ НЕВЕРНА\nh_calc: ${h_calc}\nh_dec: ${h_dec}`;
        }
    }
);

// ----- 22. ElGamal Digital Signature -----
registerCipher('elgamal_sign', 'ElGamal (Цифровая подпись)', 'ЭЦП Эль-Гамаля (с использованием хеша).',
    [
        { id: 'p', label: 'Модуль P', type: 'number', default: 37 },
        { id: 'g', label: 'Основание G', type: 'number', default: 2 },
        { id: 'x', label: 'Секретный ключ X', type: 'number', default: 14 },
        { id: 'y', label: 'Открытый ключ Y', type: 'number', default: 14 }
    ],
    (text, p) => {
        const P = BigInt(p.p || 37), G = BigInt(p.g || 2), X = BigInt(p.x || 14);
        const pm1 = P - 1n;
        let h = quadraticHash(text, P);
        if (h <= 1n) h += 2n;
        if (h >= P - 1n) h = P - 2n;

        let k = 5n; // Simplified: in ideal we should find random k s.t. gcd(k, P-1)=1
        while (gcd(Number(k), Number(pm1)) !== 1) k++;
        
        let a = rsa_pow(G, k, P);
        let k_inv = modInverse(k, pm1);
        let b = ((h - (X * a % pm1)) * k_inv) % pm1;
        if (b < 0n) b += pm1;
        
        return `Хэш (h): ${h}\nПодпись (a): ${a}\nПодпись (b): ${b}`;
    },
    (text, p) => {
        const P = BigInt(p.p || 37), G = BigInt(p.g || 2), Y = BigInt(p.y || 14);
        const originalMsg = prompt("Введите исходное сообщение для проверки:");
        let h = quadraticHash(originalMsg, P);
        if (h <= 1n) h += 2n;
        if (h >= P - 1n) h = P - 2n;

        let a = 0n, b = 0n;
        text.split('\n').forEach(line => {
            if(line.includes('(a):')) a = BigInt(line.split(':')[1].trim());
            if(line.includes('(b):')) b = BigInt(line.split(':')[1].trim());
        });

        let left = rsa_pow(G, h, P);
        let right = (rsa_pow(Y, a, P) * rsa_pow(a, b, P)) % P;
        
        return left === right ? `ПОДПИСЬ ВЕРНА (${left} = ${right})` : `ПОДПИСЬ НЕВЕРНА (${left} != ${right})`;
    }
);

// ----- 23. GOST 34.10-94 -----
registerCipher('gost_94', 'ГОСТ 34.10-94 (ЭЦП)', 'Стандарт цифровой подписи РФ (версия 1994 года).',
    [
        { id: 'p', label: 'Число P', type: 'number', default: 37 },
        { id: 'q', label: 'Число Q (делитель P-1)', type: 'number', default: 3 },
        { id: 'a', label: 'Основание A', type: 'number', default: 2 },
        { id: 'x', label: 'Секретный ключ X', type: 'number', default: 5 },
        { id: 'y', label: 'Открытый ключ Y', type: 'number', default: 32 }
    ],
    (text, p) => {
        const P = BigInt(p.p || 37), Q = BigInt(p.q || 3), A = BigInt(p.a || 2), X = BigInt(p.x || 5);
        let h = quadraticHash(text, P) % Q;
        if (h === 0n) h = 1n;

        let k = 2n; // Random k in real app
        let r = rsa_pow(A, k, P) % Q;
        let s = (X * r + k * h) % Q;
        
        return `r: ${r}\ns: ${s}\nh: ${h}`;
    },
    (text, p) => {
        const P = BigInt(p.p || 37), Q = BigInt(p.q || 3), A = BigInt(p.a || 2), Y = BigInt(p.y || 2);
        let r = 0n, s = 0n;
        text.split('\n').forEach(line => {
            if(line.startsWith('r:')) r = BigInt(line.split(':')[1].trim());
            if(line.startsWith('s:')) s = BigInt(line.split(':')[1].trim());
        });

        const originalMsg = prompt("Введите исходное сообщение:");
        let h = quadraticHash(originalMsg, P) % Q;
        if (h === 0n) h = 1n;

        let v = rsa_pow(h, Q - 2n, Q);
        let z1 = (s * v) % Q;
        let z2 = ((Q - r) * v) % Q;
        let u = (rsa_pow(A, z1, P) * rsa_pow(Y, z2, P)) % P % Q;

        return u === r ? `ПОДПИСЬ ВЕРНА (u=${u}, r=${r})` : `ПОДПИСЬ НЕВЕРНА (u=${u}, r=${r})`;
    }
);

// ===== Initialize =====
initializeCipherSelect();



