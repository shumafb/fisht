"""Очищение абонетских номеров"""

import re


def clean_phone_number(phone_number: str) -> int:
    """Удаляет все ненужные символы из телефонного номера и возвращает только цифры."""
    if re.match(
        r"(?:([+]\d{1,4})[-.\s]?)?(?:[(](\d{1,3})[)][-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})",
        phone_number,
    ):
        edit_phone_number = "".join(char for char in phone_number if char.isdigit())
        if len(edit_phone_number) == 10:
            return f"7{edit_phone_number[-10:]}"
        if len(edit_phone_number) == 11 and (edit_phone_number.startswith(("8", "7"))):
            return f"7{edit_phone_number[-10:]}"
        return edit_phone_number
