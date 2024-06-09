"""Модудь для работы с sms"""

import os
import os.path
import random
import string
from .smsc_api import SMSC
import pandas as pd


def send_sms(phone: int, modem_id=1, send_mode=True) -> str:
    """
    Создает файл для последующей отправки sms server tools
    phone - номер телефона
    modem_id - номер модема, с которого осуществляется отправка
    send_mode - True для российских номеров,
                False - строгий режим для ин. номеров
    Возвращает название созданного файла
    """
    path_file = f"sms/outgoing/{modem_id}/{phone}-{''.join(random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for x in range(6))}.txt"
    with open(path_file, "w", encoding="utf-8") as file:
        x = f"To: {phone}\n"
        x += "Report: yes\n"
        x += "Ping: yes\n\n"
        file.write(x)
    return {"path_file": path_file[path_file.find("/outgoing/") + 12 :]}


def check_sent_failed(path_file: str) -> dict:
    """
    Проверка на наличие файла отправки в папках sent и failed
    Если есть в failed -> ошибка в отправки с нашей стороны
    Если есть в sent -> отправлено
    """
    try:
        info = {}
        if os.path.isfile(f"sms/sent/{path_file}"):
            with open(f"sms/sent/{path_file}", "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    if len(line.split(":", 1)) > 1:
                        info[line.strip("\n").split(":", 1)[0]] = line.strip("\n").split(":", 1)[1].strip()
            return {"status": "Send", "info": info, "path_file": f"sms/sent/{path_file}"}
        if os.path.isfile(f"sms/failed/{path_file}"):
            with open(f"sms/failed/{path_file}", "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    if len(line.split(":", 1)) > 1:
                        info[line.strip("\n").split(":", 1)[0]] = line.strip("\n").split(":", 1)[1].strip()
            return {"status": "Local_Failed", "info": info, "path_file": f"sms/failed/{path_file}"}
    except FileNotFoundError:
        pass
    else:
        return {"status": "None", "info": None, "path_file": None}


def get_message_id(path_file: str) -> dict:
    """
    Возвращает message_id файла в папке sent и id модема
    path_file - название отчета о запросе отпраки смс
    """
    try:
        with open(f"sms/sent/{path_file}", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                if "Message_id" in line:
                    message_id = line.strip("\n").split(":", 1)[1].strip()
                if "Modem" in line:
                    modem_id = line.strip("\n").split(":", 1)[1].strip()[-1:]
            return [message_id, modem_id]
    except FileNotFoundError:
        return None


def check_report(message_id: str, modem_id: str) -> dict:
    """
    Проверка статуса о доставке смс в папке report
    message_id - id статуса об отправке
    modem_id - id модема
    Возвращает словарь с данными отчета
    """
    for filename in os.listdir("sms/report"):
        if filename.startswith(f"GSM{modem_id}"):
            with open(f"sms/report/{filename}", "r", encoding="utf-8") as f:
                info = {}
                for line in f.readlines():
                    if len(line.strip().split(": ")[1:]) > 0:
                        info[line.strip().split(": ")[0]] = line.strip("\n").split(": ")[1:][0]
                        # Поиск и сравнение заданного message_id и message_id файла
                if str(message_id) == info["Message_id"]:
                    return {
                        "status": "Report",
                        "info": info,
                        "path_file": f"sms/report/{filename}",
                    }


def give_report_content(x: dict) -> str:
    y = {}
    for key in x:
        y[key] = {}
        for k, v in x[key].items():
            if k == 'info':
                y[key][k] = {}
                for info_key, info_value in v.items():
                    y[key][k][info_key] = info_value
            else:
                y[key][k] = v

    for key, value in y.items():
        if isinstance(value.get('info', {}), dict):
            y[key].update(value.pop('info'))

    df = pd.DataFrame(y)
    file_path = f"source/reports/output-{''.join(random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for x in range(3))}.csv"
    df.to_csv(file_path)
    return file_path


# Функционал SMSC

smsc = SMSC()


def get_balance():
    """Запрос баланса в ЛК SMSC"""
    return smsc.get_balance()


def send_sms_smsc(phone: str) -> int:
    """Отправка ping через сервис SMSC"""
    ping = smsc.send_sms(f"7{phone}", "", format=6)
    smsc_id = ping[0]
    return int(smsc_id)


def update_status(smsc_id, phone):
    """Запрос отчета о доставке ping"""
    return smsc.get_status(id=smsc_id, phone=f"7{phone},", all=1)
