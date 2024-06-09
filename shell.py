"""События для взаимодействия с ботом"""

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message, URLInputFile


from bot import USERS_IDS
import logic.sms_center as sms_center
from botcf.keyboards import kb
from logic.bs_html_constructor import bs_html_constructor
from logic.bs_html_preview import get_preview
from logic.bs_yandex_locator import push_yalocator_api
from logic.imei_checker import check_imei, check_taclist
from logic.imei_luhn_alg import luhn
from logic.ph_check import get_kodysu, get_smsbox, numvox
from logic.ph_clean_phone_number import clean_phone_number
from logic.sms_center import (check_sent_failed, get_message_id,
                              send_sms, send_sms_smsc)

router = Router() # [1]



operator_color = {"мтс": "🔴", "мегафон": "🟢", "билайн": "🟡", "теле2": "⚫", "йота": "🔵"}
ping_sender = {"модем": send_sms, "смсц": send_sms_smsc}
ping_status = {"Send": "🟡 Отправлено", "Local_Failed": "⭕ Локальная ошибка", "Report": "🟢 Доставлено", "Failed": "🔴 Ошибка", "Undefined": "⚠ Неопределенно"}


class BotStatesStorage(StatesGroup):
    """Машина состояний бота"""
    list_phone = State() # Состояние списка номеров


@router.message(F.text.regexp(r"^(1|2|20|99) (\d{1,8}) (\d+)"))
async def api_locator(message: Message):
    """Работа с базовыми станциями, возвращает превью, html-файл, статус ответов по API
    """
    if message.from_user.id not in USERS_IDS:
        return message.answer("Нет доступа")
    
    bslist = message.text.split("\n")
    yalocator_list = []
    text = "📡\n├Статус:\n"
    flag = False
    for bs in bslist:
        mnc = bs.split(" ")[0]
        lac = bs.split(" ")[1]
        cid = bs.split(" ")[2]
        yalocator_card = push_yalocator_api(mnc=mnc, lac=lac, cid=cid)
        if yalocator_card is not None:
            yalocator_list.append(yalocator_card)
            text += f"├{lac}/{cid} ✅\n"
            flag = True
        else:
            text += f"├{lac}/{cid} ❌\n"
    text += f"└Всего: {len(yalocator_list)}"
    if flag:
        bs_html_constructor(yalocator_list)
        await get_preview()
        await message.answer_photo(photo=FSInputFile("source/screen.png"))
    await message.answer(text=text)
    if flag:
        await message.answer_document(
            document=FSInputFile("source/bs_maps/map.html",
            filename="map.html"))


@router.message(F.text.regexp(r"^\d{14,15}$"))
async def imei_menu(message: Message):
    """Работа с imei-номерами, возвращает превью модели и модель телефона
    """
    if message.from_user.id not in USERS_IDS:
        return message.answer("Нет доступа")
    
    imei = message.text.strip()
    imei = luhn(imei[:14])
    tac = int(str(imei)[:8])
    imei_info = check_imei(imei=imei)
    tac_info = check_taclist(tac_code=tac)
    info = ""
    if imei_info is not None:
        imei_device = f"{imei_info["object"]["brand"]} {imei_info["object"]["name"]}"
        if imei_info["object"]["image"] is not None:
            image = URLInputFile(imei_info["object"]["image"])
            await message.answer_photo(image)
        info += f"🆔\n*├IMEI*: {imei}\n└Модель: {imei_device}\n"
    if tac_info is not None:
        info += f"\n🆑\n*├TAC*: {tac}\n└Модель: {tac_info}"
    await message.answer(
        text=info,
        reply_markup=kb.imei_keyboard(imei_device=imei_device, imei=imei))


# @router.message(F.text.regexp(r"^(\+7|7|8|)?\d{10}"))
@router.message(F.text.regexp(r"(?:([+]\d{1,4})[-.\s]?)?(?:[(](\d{1,3})[)][-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})"))
async def phone_menu(message: Message, state: FSMContext):
    """Работа с номером телефона России

    Args:
        message (Message): российский номер телефона
    """
    if message.from_user.id not in USERS_IDS:
        return message.answer("Нет доступа")

    loop = asyncio.get_event_loop()
    phone = clean_phone_number(message.text.strip())
    info = f"📱\n├<b>Номер</b>: {phone}\n"
    if len(message.text.split(" ")) == 2 and message.text.split(" ")[1].lower() in ["смсц", "smsc", "s", "c", "смс", "sms", "модем", "м", "modem", "m", "можем"]:
        sms_server = message.text.split(" ")[1]
        phone = clean_phone_number(message.text.strip())
        numvox_data = numvox(phone10=phone)
        if sms_server in ["смсц", "smsc", "s", "c", "смс", "sms"]:
            smsc_id = await loop.run_in_executor(None, sms_center.send_sms_smsc, phone)
            await message.answer(text=f"📫 *SMSC*\n└Номер:{phone}",
                                 reply_markup=kb.update_status_smsc(),
                                 )
            await state.update_data(smsc_info=smsc_id)
        elif sms_server in ["модем", "м", "modem", "m", "можем"]:
            modem_id = 2 if numvox_data["operator"].lower() in ["билайн", "beeline", "вымпелком"] else 1
            sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone, modem_id)
            await message.answer(text=f"📮 *Модем*\n└Номер:{phone}",
                                reply_markup=kb.update_status_modem(),
                                )
            await state.update_data(modem_info=sending_info)
    elif len(phone) in [10, 11] and phone.isdigit():
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
                    f"├Регион: {numvox_data["region"]}\n" +\
                    f"└Источник: 🦊 numvox\n"
        elif numvox_data is None:
            kodysu_data = get_kodysu(phone)
            if kodysu_data is not None:
                for card in kodysu_data:
                    info += f"├{card}\n"
                info += f"└Источник: ☎ kodysu\n"
                await message.answer(
                    text=info,
                    reply_markup=kb.phone_menu_kb_world(phone=phone),
                    parse_mode="html"
                )
        if smsbox_data is not None:
            if smsbox_data[1].strip().lower() == "кто звонит с номера, зачем и как часто":
                pass
            else:
                info += f"\n📦 mysmsbox\n└⛔ {smsbox_data[1].strip()}"
        if numvox_data is not None:
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
            info +="└Источник: ☎ kodysu\n"
        await message.answer(
            text=info,
            parse_mode="html",
            reply_markup=kb.phone_menu_kb_world(phone=phone)
            )
        await state.update_data(phone=phone)
    else:
        await message.answer("Некорректная команда2")

# Пинг через кнопку
@router.callback_query(F.data.startswith("ping"))
async def send_modem_ping(callback: CallbackQuery, state: FSMContext):
    """_summary_

    Args:
        callback (CallbackQuery): _description_
        state (FSMContext): _description_

    Returns:
        _type_: _description_
    """
    if callback.from_user.id not in USERS_IDS:
        return callback.answer("Нет доступа")
    
    action = callback.data.split("_")[1]
    if action.lower() == "modem":
        loop = asyncio.get_event_loop()
        phone = await state.get_data()
        phone = phone["phone"]
        sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone)
        await callback.answer("❗Запрос на ping отправлен, ожидайте")
        await callback.message.answer(
            f"📮 Модем\n├*Номер*: {phone}\n└Статус: ⚪ Отправлен на СМС сервер",
        )
        try:
            await asyncio.sleep(5)
            sending_info.update(await loop.run_in_executor(None, sms_center.check_sent_failed, sending_info["path_file"]))
            await state.update_data(sending_info=sending_info)
            await callback.message.answer(
                text=f"📮 Модем\n├<b>Номер</b>: {sending_info["info"]["To"]}\n├Отправлен: {sending_info["info"]['Sent']}\n└Статус: {ping_status[sending_info["status"]]}",
                reply_markup=kb.update_status_modem(),
                parse_mode="HTML"
            )
        except (TypeError, KeyError):
            await callback.message.answer(
                text=f"📮 Модем\n<b>├Номер</b>: {sending_info["info"]["To"]}\n├Время ошибки: {sending_info['info']["Failed"]}\n├Причина: {sending_info["info"]["Fail_reason"]}\n└Статус: {ping_status['Local_Failed']}\n\nОбратитесь к администратору",
                parse_mode="HTML")
    elif action.lower() == "smsc":
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, send_sms_smsc, phone)
        await state.update_data(sms_id=result)
        await callback.message.answer(
            f"📫 SMSC\n├*Номер*: {phone}\n└Статус: ⚪ Отправлен на СМС сервер",
        )

@router.callback_query(F.data == "update_status_ping")
async def update_modem(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in USERS_IDS:
        return callback.answer("Нет доступа")

    loop = asyncio.get_event_loop()

    sending_info = await state.get_data()
    sending_info = sending_info["sending_info"]

    action = callback.data.split("__")[1]
    amount = callback.data.split("__")[2]

    message_id = sending_info["info"]["Message_id"]
    modem_id = sending_info["info"]["Modem"][-1:]
    print(message_id, modem_id)

    if action == "modem" and amount == "alone":
        try:
            sending_info.update(loop.run_in_executor(None, sms_center.check_report, message_id, modem_id))
            print(sending_info)
            await callback.message.answer(
                text=f"📮 Модем\n├<b>Номер</b>: {sending_info["info"]["To"]}\n├Отправлен: {sending_info["info"]['Sent']}\n\├Вернулся: {sending_info["info"]["Received"]}\n└Статус: {ping_status[sending_info["status"]] if sending_info["info"]["Status"].split(",", 1) == "0" else ping_status["Undefined"]}",
                parse_mode="HTML"
            )


        except FileNotFoundError:
            await callback.message.answer(
                text=f"📮 Модем\n├<b>Номер</b>: {sending_info["info"]["To"]}\n├Отправлен: {sending_info["info"]['Sent']}\n└Статус: {ping_status[sending_info["status"]]}",
                reply_markup=kb.update_status_modem(),
                parse_mode="HTML"
            )
    elif action == "smsc":
        pass


# @router.callback_query(F.data.startswith("forced_modem_ping__"))
# async def forced_send_modem_ping(callback: CallbackQuery, state: FSMContext):
#     if callback.from_user.id not in USERS_IDS:
#         return callback.answer("Нет доступа")
    
#     modem_id = callback.data.split("__")[1]
#     loop = asyncio.get_event_loop()
#     phone = await state.get_data()
#     phone = phone["phone"]
#     sending_info = await loop.run_in_executor(None, sms_center.send_sms, phone, modem_id)
#     await callback.answer("❗Запрос на ping отправлен, ожидайте")
#     await asyncio.sleep(10)
#     try:
#         await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
#     except TypeError:
#         await callback.answer("‼ Продолжается попытка, ожидайте")
#         try:
#             await asyncio.sleep(8)
#             await sending_info.update(await loop.run_in_executor(None, sms_center.get_message_id, sending_info["path_file"]))
#         except TypeError:
#             await callback.message.answer(f"📮 Модем\n├*Номер*: {phone}\n└Статус: {ping_status['Local_Failed']}\n\nОбратитесь к администратору")




# @router.message(F.text.startswith("модем"))
# async def modem_ping_menu(message: Message, state: FSMContext):
#     if len(message.text) > 5:
#         phone_list = message.text.split("\n")[1:]
#         cleaned_phones = []
#         for phone in phone_list:
#             cleaned_phones.append(clean_phone_number(phone))
#         await state.update_data(phones=cleaned_phones)
#         info = f"📮 *МОДЕМ*\n\n📤 *Отправить на*\n{"\n".join(cleaned_phones)}\n\nПодтвердите отправку:"
#         await state.set_state(BotStatesStorage.list_phone)
#         await message.answer(
#             text=info,
#             reply_markup=kb.agree_send_modem(),
#         )
#     else:
#         await message.answer("Некорректный запрос")

# @router.callback_query(F.data == "agree_send_modem")
# async def send_modem_phones(callback: CallbackQuery, state: FSMContext):
#     """Отправка смс по списку номеров"""
#     if callback.from_user.id not in USERS_IDS:
#         return callback.answer("Нет доступа")
    
#     state_data = await state.get_data()
#     phones_info = state_data["phones"]
#     paths = {}
#     phones_states = ""
#     for phone in phones_info:
#         phone_data = numvox(phone)
#         if phone_data:
#             modem_id = 2 if phone_data["operator"].lower() in ["билайн", "beeline", "вымпелком"] else 1
#             path = send_sms(phone=phone, modem_id=modem_id)
#         else:
#             path = send_sms(phone=phone, modem_id=1)
#         paths[phone] = path
#         phones_states += f"{phone} / {ping_status['Send']}\n"
#     await state.update_data(paths=paths)
#     await state.set_state(BotStatesStorage.list_phone)
#     await callback.message.answer(
#         text="▶️📮*МОДЕМ*\n\n📥 *Состояние*\n\n" +\
#             "*Номер / Статус*\n" +\
#             f"{phones_states}",
#         reply_markup=kb.update_status_list_modem()
#     )

# @router.callback_query(F.data == "update_status_list_modem")
# async def update_modem_phones(callback: CallbackQuery, state: FSMContext):
#     if callback.from_user.id not in USERS_IDS:
#         return callback.answer("Нет доступа")
    
#     state_data = await state.get_data()
#     paths = state_data["paths"]
#     for phone, phone_data in paths.items():
#         paths[phone].update(get_message_id(phone_data["path_file"]))


@router.message(Command("help"))
async def get_help(message: Message):
    """Возвращает справку по функциям бота
    """
    if message.from_user.id not in USERS_IDS:
        return message.answer("Нет доступа")
    
    with open("source/texts/help.txt", "r", encoding="utf-8") as f:
        help_text = f.read()
        await message.answer(help_text)


@router.message(Command("id"))
async def cmd_get_id(message: Message):
    """Возвращает id телеграм аккаунта юзера
    """
    await message.answer(f"Твой Telegram ID: `{message.from_user.id}`")

@router.message(F.text.regexp(r"."))
async def try_again(message: Message):
    """Заглушка от 'левых' запросов"""
    if message.from_user.id not in USERS_IDS:
        return message.answer("Нет доступа")
    
    await message.answer(
        "Запрос не распознан"
    )