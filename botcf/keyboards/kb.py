from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def phone_menu_kb(phone: int):
    phone_menu_but = [
        [
            InlineKeyboardButton(text="📫 SMSC", callback_data="ping_smsc"),
            InlineKeyboardButton(text="📮 Модем", callback_data="ping_modem"),
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

def phone_menu_kb_world(phone: int):
    phone_menu_but = [
        [
            InlineKeyboardButton(text="📮🔴 Модем [МТС]", callback_data="forced__ping_modem_forced__1"),
            InlineKeyboardButton(text="📮🟡 Модем [Билайн]", callback_data="forced__ping_modem_forced__2"),
        ],
        [
            InlineKeyboardButton(text="🟢 WhatsApp", url=f"https://wa.me/+{phone}"),
            InlineKeyboardButton(text="🔵 Telegram", url=f"https://t.me/+{phone}"),
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
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="agree_send_ping_modem"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=send_ping)
    return keyboard

def update_status_list_modem():
    modem_menu = [
        [
        InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_ping__modem__list")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=modem_menu)
    return keyboard

def update_status_smsc():
    smsc_menu = [
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_ping__smsc__alone")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=smsc_menu)
    return keyboard

def update_status_modem():
    modem_menu = [
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="update_status_ping__modem__alone")
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=modem_menu)
    return keyboard

def imei_keyboard(imei_device, imei):
    imei_kb = [
        [
            InlineKeyboardButton(text='🟣 IMEI.info', url=f"https://www.imei.info/?imei={imei}"),
            InlineKeyboardButton(text='🔴 Яндекс', url=f"https://ya.ru/search/?text={imei_device}"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=imei_kb)
    return keyboard
