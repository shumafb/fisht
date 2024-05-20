"""События для взаимодействия с ботом"""

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb
from logic.ph_clean_phone_number import clean_phone_number
from logic.ph_numvox_check import get_phone_info
from logic.sms_center import send_sms, send_sms_smsc, check_report, check_sent_failed, get_message_id

router = Router() # [1]

loop = asyncio.get_event_loop()


operator_color = {"мтс": "🔴", "мегафон": "🟢", "билайн": "🟡", "теле2": "⚫", "йота": "🔵"}
ping_sender = {"модем": send_sms, "смсц": send_sms_smsc}
ping_status = {"Send": "🟡 Отправлено", "Local_Failed": "⭕ Вн. ошибка", "Report": "🟢 Доставлено", "Failed": "🔴 Ошибка"}

class BotStatesStorage(StatesGroup):
    list_phone = State() # Состояние списка номеров

@router.message(F.text.regexp(r"^(\+7|7|8|)?\d{10}"))
async def phone_menu(message: Message):
    """Взаимодействие с российским номером телефона"""
    if len(message.text) in [10, 11] and message.text.isdigit():
        phone = clean_phone_number(message.text.strip())
        info = f"▶️📱<b>ТЕЛЕФОН</b>\n├<b>Номер</b>: {phone}\n"
        numvox = get_phone_info(phone10=phone)
        if numvox is not None:
            color_operator = operator_color[numvox["operator"].lower()] if numvox["operator"].lower() in operator_color else "❔"
            try:
                old_operator = f"├<b>Бывший оператор</b>: {numvox['old_operator']}\n"
            except KeyError:
                old_operator = ""

            info += f"├<b>Оператор</b>: {color_operator} {numvox["operator"].title()}\n" + \
                    f"{old_operator}"+ \
                    f"└<b>Емкость</b>: {numvox["region"]}\n"
        await message.answer(
            text=info,
            reply_markup=kb.phone_menu_kb(phone=phone),
            parse_mode="html"
            )
    elif len(message.text.split(" ")) == 2 and message.text.split(" ")[1].lower() in ['модем', 'смсц']:
        sms_server = message.text.split(" ")[1]
        if sms_server == "смсц":
            smsc_id = await loop.run_in_executor(None, ping_sender[sms_server],  phone)
            await message.answer(text=f"🟠📩[*SMSC*]\n Отправлен Ping\nНомер:{phone}",
                                 reply_markup=kb.update_status_smsc(),
                                 )
        elif sms_server == "модем":
            modem_id = 2 if numvox["operator"].lower() == "билайн" else 1
            send_file_name = await loop.run_in_executor(None, ping_sender[sms_server], phone, modem_id)
            await message.answer(text=f"🟠📩[*МОДЕМ*]\n Отправлен Ping\nНомер:{phone}",
                                reply_markup=kb.update_status_modem(),
                                )
        else:
            await message.answer("Некорректная команда")
        await message.answer(f"Отправлено смс через {message.text.split(" ")[1]}")
    else:
        await message.answer("Некорректная команда")


@router.callback_query(F.data == "modem_ping")
async def send_modem_ping(message: Message):
    pass
    
@router.message(F.text.startswith("модем"))
async def modem_ping_menu(message: Message, state: FSMContext):
    if len(message.text) > 5:
        phone_list = message.text.split("\n")[1:]
        cleaned_phones = []
        for phone in phone_list:
            cleaned_phones.append(clean_phone_number(phone))
        await state.update_data(phones=cleaned_phones)
        info = f"▶️📮*МОДЕМ*\n\n📤 *Отправить на*\n{"\n".join(cleaned_phones)}\n\nПодтвердите отправку:"
        await state.set_state(BotStatesStorage.list_phone)
        await message.answer(
            text=info,
            reply_markup=kb.agree_send_modem(),
        )
    else:
        await message.answer("Некорректный запрос")

@router.callback_query(F.data == "agree_send_modem")
async def send_modem_phones(callback: CallbackQuery, state: FSMContext):
    """Отправка смс по списку номеров"""
    state_data = await state.get_data()
    phones_info = state_data["phones"]
    paths = {}
    phones_states = ""
    for phone in phones_info:
        phone_data = get_phone_info(phone)
        if phone_data:
            modem_id = 2 if phone_data["operator"].lower() in ["билайн", "beeline", "вымпелком"] else 1
            path = send_sms(phone=phone, modem_id=modem_id)
        else:
            path = send_sms(phone=phone, modem_id=1)
        paths[phone] = path
        phones_states += f"{phone} / {ping_status['Send']}\n"
    await state.update_data(paths=paths)
    await state.set_state(BotStatesStorage.list_phone)
    await callback.message.answer(
        text="▶️📮*МОДЕМ*\n\n📥 *Состояние*\n\n" +\
            "*Номер / Статус*\n" +\
            f"{phones_states}",
        reply_markup=kb.update_status_list_modem()
    )

@router.callback_query(F.data == "update_status_list_modem")
async def update_momed_phones(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    paths = state_data["paths"]
    for phone, phone_data in paths.items():
        paths[phone].update(get_message_id(phone_data["path_file"]))
    print(paths)




@router.message(Command("help"))
async def help(message: Message):
    await message.answer("Привет")


@router.message(Command("id"))
async def cmd_get_id(message: Message):
    await message.answer(f"Твой Telegram ID: `{message.from_user.id}`")
