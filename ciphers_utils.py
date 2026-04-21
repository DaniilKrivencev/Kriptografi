# -*- coding: utf-8 -*-
"""
Общие функции для шифров: преобразование текста, форматирование.
"""

# Русский алфавит (33 буквы)
RUSSIAN_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

# Для обратной совместимости
TRITHEMIUS_ALPHABET = RUSSIAN_ALPHABET

# Замена знаков препинания на коды
PUNCT_TO_WORD = {
    ",": "зпт",   # запятая
    ".": "тчк",   # точка
    "!": "вск",   # восклицательный знак
    "?": "впр",   # вопросительный знак
    ":": "двт",   # двоеточие
    ";": "тзп",   # точка с запятой
    " ": "прб",   # пробел
    "\n": "прб",
    "\r": "прб",
    "\t": "прб",
}

# Обратное соответствие
WORD_TO_PUNCT = {"прб": " ", "ПРБ": " "}
for k, v in PUNCT_TO_WORD.items():
    if v == "прб":
        continue
    WORD_TO_PUNCT[v] = k
    WORD_TO_PUNCT[v.upper()] = k


def text_to_letters_only(text: str) -> str:
    """Заменяет знаки препинания и пробелы на сокращённые слова."""
    result = []
    for char in text:
        if char in PUNCT_TO_WORD:
            result.append(PUNCT_TO_WORD[char])
            result.append(" ")
        else:
            result.append(char)
    return "".join(result)


def letters_only_to_text(text: str) -> str:
    """Восстанавливает знаки препинания и пробелы из сокращённых слов."""
    text = text.replace("ЗПТПРБ", ", ").replace("зптпрб", ", ")
    text = text.replace("ТЧК", ".").replace("тчк", ".")
    text = text.replace("ПРБ", " ").replace("прб", " ")
    
    for code, punct in sorted(WORD_TO_PUNCT.items(), key=lambda x: -len(x[0])):
        if code in ("прб", "ПРБ"):
            continue
        text = text.replace(code + " прб ", punct + " ")
        text = text.replace(code + " ПРБ ", punct + " ")
    
    for code, punct in sorted(WORD_TO_PUNCT.items(), key=lambda x: -len(x[0])):
        if code in ("прб", "ПРБ"):
            continue
        text = text.replace(code + " ", punct)
    
    text = text.replace("прб ", " ").replace("ПРБ ", " ")
    text = text.replace("прб", " ").replace("ПРБ", " ")
    return text


def format_output(s: str, block_size: int = 5) -> str:
    """Вставляет пробел между каждыми block_size символами."""
    blocks = [s[i : i + block_size] for i in range(0, len(s), block_size)]
    return " ".join(blocks)


def unformat_input(s: str) -> str:
    """Убирает пробелы из строки."""
    return s.replace(" ", "")


def _norm_text(text: str, alphabet: str) -> str:
    """Оставляет в тексте только символы из алфавита; приведение к верхнему регистру."""
    return "".join(c.upper() for c in text if c.upper() in alphabet)