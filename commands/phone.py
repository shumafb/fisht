from app import bot, dp
from aiogram import F
import asyncio


loop = asyncio.get_event_loop()

@dp.message(F.text.regexp(r"^(\+7|7|8|)?\d{10}"))
def phone_menu(phone: str) -> str:
    pass