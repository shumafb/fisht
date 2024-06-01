"""События для взаимодействия с ботом"""

import asyncio
import json

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, URLInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.keyboards import kb
from logic.ph_clean_phone_number import clean_phone_number
from logic.ph_check import numvox, get_smsbox, get_kodysu
from logic.sms_center import send_sms, send_sms_smsc, check_report, check_sent_failed, get_message_id
import logic.sms_center as sms_center
from logic.imei_luhn_alg import luhn
from logic.imei_checker import check_imei

router = Router() # [1]



operator_color = {"мтс": "🔴", "мегафон": "🟢", "билайн": "🟡", "теле2": "⚫", "йота": "🔵"}
ping_sender = {"модем": send_sms, "смсц": send_sms_smsc}
ping_status = {"Send": "🟡 Отправлено", "Local_Failed": "⭕ Локальная ошибка", "Report": "🟢 Доставлено", "Failed": "🔴 Ошибка"}


class BotStatesStorage(StatesGroup):
    list_phone = State() # Состояние списка номеров


@router.message(F.text.regexp(r"^\d{14,15}$"))
async def imei_menu(message: Message):
    imei = message.text.strip()
    imei = luhn(imei[:14])
    imei_info = check_imei(imei=imei)
    imei_device = f"{imei_info["object"]["brand"]} {imei_info["object"]["name"]}"

    if imei_info["object"]["image"] is not None:
        image = URLInputFile(imei_info["object"]["image"])
        await message.answer_photo(image)
    await message.answer(
        text=f"🆔\n*├IMEI*: {imei}\n└Модель: {imei_device}",
        reply_markup=kb.imei_keyboard(imei_device=imei_device, imei=imei))


# @router.message(F.text.regexp(r"^(\+7|7|8|)?\d{10}"))
@router.message(F.text.regexp(r"(?:([+]\d{1,4})[-.\s]?)?(?:[(](\d{1,3})[)][-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})"))
async def phone_menu(message: Message, state: FSMContext):
    """Работа с номером телефона России

    Args:
        message (Message): российский номер телефона
    """
    loop = asyncio.get_event_loop()
    phone = clean_phone_number(message.text.strip())
    info = f"📱\n├<b>Номер</b>: {phone}\n"
    if len(phone) in [10, 11] and phone.isdigit():
        numvox_data = numvox(phone10=phone)
        smsbox_data = get_smsbox(phone=phone)
        if numvox_data is not None:
            color_operator = operator_color[numvox_data["operator"].lower()] if numvox_data["operator"].lower() in operator_color else "⚪"
            try:
                old_operator = f"├Старый оператор: {numvox_data['old_operator']}\n"
            except KeyError:
                old_operator = ""

            info += f"├Оператор: {color_operator} {numvox_data["operator"].title()}\n" + \
                    f"{old_operator}"+ \
                    f"└Регион: {numvox_data["region"]}\n"
        elif numvox_data is None:
            kodysu_data = get_kodysu(phone)
            if kodysu_data is not None:
                for card in kodysu_data:
                    info += f"├{card}\n"
        if smsbox_data is not None:
            if smsbox_data[1].strip().lower() == "кто звонит с номера, зачем и как часто":
                # info += "\n📦 mysmsbox\n└ ✅ не обнаружен в спам-списках"
                pass
            else:
                info += f"\n📦 mysmsbox\n└⛔ {smsbox_data[1].strip()}"
        await message.answer(
            text=info,
            reply_markup=kb.phone_menu_kb(phone=phone),
            parse_mode="html"
            )
        await state.update_data(phone=phone)
    elif len(phone) == 12 and phone.isdigit():
        kodysu_data = get_kodysu(phone)
        if kodysu_data is not None:
            for card in kodysu_data:
                info += f"├{card}\n"
        await message.answer(info, parse_mode="html", reply_markup=kb.phone_menu_kb_world(phone=phone))
        await state.update_data(phone=phone)
    elif len(message.text.split(" ")) == 2 and message.text.split(" ")[1].lower() in ["смсц", "smsc", "s", "c", "смс", "sms", "модем", "м", "modem", "m", "можем"]:
        sms_server = message.text.split(" ")[1]
        phone = clean_phone_number(message.text.strip())
        numvox_data = numvox(phone10=phone)
        if sms_server in ["смсц", "smsc", "s", "c", "смс", "sms"]:
            smsc_id = await loop.run_in_executor(None, sms_center.send_sms_smsc, phone)
            await message.answer(text=f"📫 *SMSC*\n├Отправлен Ping\n└Номер:{phone}",
                                 reply_markup=kb.update_status_smsc(),
                                 )
            await state.update_data(smsc_info=smsc_id)
        elif sms_server in ["модем", "м", "modem", "m", "можем"]:
            modem_id = 2 if numvox_data["operator"].lower() == "билайн" else 1
            sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone, modem_id)
            await message.answer(text=f"📮 *Модем*\n├Отправлен Ping\n└Номер:{phone}",
                                reply_markup=kb.update_status_modem(),
                                )
            await state.update_data(modem_info=sending_info)
        else:
            await message.answer("Некорректная команда1")
    else:
        await message.answer("Некорректная команда2")

@router.callback_query(F.data == "modem_ping")
async def send_modem_ping(callback: CallbackQuery, state: FSMContext):
    loop = asyncio.get_event_loop()
    phone = await state.get_data()
    phone = phone["phone"]
    sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone)
    await callback.answer("❗Запрос на ping отправлен, ожидайте")
    await asyncio.sleep(5)
    try:
        await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
    except TypeError:
        await callback.answer("‼ Продолжается попытка, ожидайте")
        try:
            await asyncio.sleep(8)
            await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
        except TypeError:
            await callback.message.answer(f"📮 Модем\n├*Номер*: {phone}\n└Статус: {ping_status['Local_Failed']}\n\nОбратитесь к администратору")


@router.callback_query(F.data.startswith("forced_modem_ping__"))
async def forced_send_modem_ping(callback: CallbackQuery, state: FSMContext):
    modem_id = callback.data.split("__")[1]
    loop = asyncio.get_event_loop()
    phone = await state.get_data()
    phone = phone["phone"]
    sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone, modem_id)
    await callback.answer("❗Запрос на ping отправлен, ожидайте")
    await asyncio.sleep(10)
    try:
        await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
    except TypeError:
        await callback.answer("‼ Продолжается попытка, ожидайте")
        try:
            await asyncio.sleep(8)
            await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
        except TypeError:
            await callback.message.answer(f"📮 Модем\n├*Номер*: {phone}\n└Статус: {ping_status['Local_Failed']}\n\nОбратитесь к администратору")



@router.callback_query(F.data == "update_status_modem")
async def update_modem(callback: CallbackQuery, state: FSMContext):
    sending_info = await state.get_data()
    sending_info = sending_info["modem_info"]
    try:
        if sending_info["message_id"]:
            await sending_info.update(check_sent_failed(sending_info["path_file"]))
    except KeyError:
        await sending_info.update(get_message_id(sending_info["path_file"]))
    except FileNotFoundError:
        pass


@router.message(F.text.startswith("модем"))
async def modem_ping_menu(message: Message, state: FSMContext):
    if len(message.text) > 5:
        phone_list = message.text.split("\n")[1:]
        cleaned_phones = []
        for phone in phone_list:
            cleaned_phones.append(clean_phone_number(phone))
        await state.update_data(phones=cleaned_phones)
        info = f"📮 *МОДЕМ*\n\n📤 *Отправить на*\n{"\n".join(cleaned_phones)}\n\nПодтвердите отправку:"
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
        phone_data = numvox(phone)
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
async def update_modem_phones(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    paths = state_data["paths"]
    for phone, phone_data in paths.items():
        paths[phone].update(get_message_id(phone_data["path_file"]))


@router.message(Command("help"))
async def get_help(message: Message):
    """Возвращает справку по функциям бота
    """
    with open("source/texts/help.txt", "r", encoding="utf-8") as f:
        help = f.read()
        await message.answer(help)


@router.message(Command("id"))
async def cmd_get_id(message: Message):
    """Возвращает id телеграм аккаунта юзера
    """
    await message.answer(f"Твой Telegram ID: `{message.from_user.id}`")

@router.message(Command("adduser"))
async def add_user(message: Message):
    # with open("source/members.json", "w", encoding="utf-8") as f:
    pass
