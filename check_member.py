import json
from aiogram import Message

with open("source/members.json", "r", encoding="utf-8") as members:
    MEMBERS_ID = json.load(members)
    ADMIN_ID = MEMBERS_ID["admin"]
    USER_ID = MEMBERS_ID["user"]

# def restricted(func):
#     async def wrapper(message, *args, **kwargs):
#         if message.from.user.id in USER_ID