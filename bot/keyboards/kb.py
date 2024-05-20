from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def phone_menu_kb(phone: int):
    phone_menu_but = [
        [
            InlineKeyboardButton(text="🟠📧SMSC", callback_data="smsc_ping"),
            InlineKeyboardButton(text="🟣📧 Модем", callback_data="modem_ping"),
        ],
        [
            InlineKeyboardButton(text="🟢 WhatsApp", url=f"https://wa.me/+7{phone}"),
            InlineKeyboardButton(text="🔵 Telegram", url=f"https://t.me/+7{phone}"),
        ],
        [
            InlineKeyboardButton(text="🔴 Yandex", url=f"https://ya.ru/search/?text={phone}")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=phone_menu_but)
    return keyboard

def agree_send_modem():
    send_ping = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="agree_send_modem"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=send_ping)
    return keyboard

def update_status_list_modem():
    modem_menu = [
        [
        InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_list_modem")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=modem_menu)
    return keyboard

def update_status_smsc():
    smsc_menu = [
        InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_smsc")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=smsc_menu)
    return keyboard

def update_status_modem():
    modem_menu = [
        InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_modem")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=modem_menu)
    return keyboard