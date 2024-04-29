def clean_phone_number(phone_number: int) -> str:
    """
    Удаляет все ненужные символы из телефонного номера и возвращает только цифры.
    """
    return ''.join(char for char in phone_number if char.isdigit())[1:]


y = "+7 999 449 27 92"
z = "8 (999) 449 27 92"
u = "7-999-449-27-92"
x = clean_phone_number(z)

print(x)