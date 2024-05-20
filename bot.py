"""Запуск бота, получение Телеграм токена"""

import asyncio
import logging
import json
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import shell

# Доступ к Ключу Телеграм
with open("source/keys.json", "r", encoding="utf-8") as f:
    TELEGRAM_TOKEN = json.load(f)["telegram_token"]


# Логирование бота
logging.basicConfig(
    level=logging.INFO,
    filename="logs/aiogram.log",
    filemode="w",
)
logging.info("An Info")
logging.error("An error")


# Запуск бота
async def main():
    """Запуск бота"""
    storage = MemoryStorage()
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
    dp = Dispatcher(storage=storage)

    dp.include_router(shell.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
