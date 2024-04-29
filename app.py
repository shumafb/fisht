from aiogram import Bot, Dispatcher
import json
import logging
import asyncio

# Доступ к Ключу Телеграм
with open("source/keys.json") as f:
    TELEGRAM_TOKEN = json.load(f)["telegram_token"]

bot = Bot(token=TELEGRAM_TOKEN, parse_mode="Markdown")
dp = Dispatcher()

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
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

