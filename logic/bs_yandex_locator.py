import json
import requests

# Запрос API-ключа Яндекс.Локатора
with open("./source/keys.json", "r", encoding="utf-8") as keys:
    YANDEX_LOCATOR_TOKEN = json.load(keys)["yandex_locator_token"]

# RNC 3G БС Республики Адыгея
RNC = {'1': 1651, '2': 233, '2046': 139, '2048': 106, '99': 1323}

URL = "https://api.lbs.yandex.net/geolocation"


def get_longcid(mnc, cid):
    """
    Принимает mnc, cid
    По значению cid подбирает RNC
    Формирует longcid из cid * RNC перемноженных в 16 системе счисления
    Возвращает longcid
    """

    if int(mnc) == 20 and cid[:2] == '48':
        cellid16 = f"{RNC['2048']:x}{int(cid):x}"
        return int(cellid16, 16)
    elif int(mnc) == 20 and cid[:2] == '46':
        cellid16 = f"{RNC['2046']:x}{int(cid):x}"
        return int(cellid16, 16)
    elif int(mnc) == 1:
        cellid16 = f"{RNC['1']:x}{int(cid):x}"
        return int(cellid16, 16)
    elif int(mnc) == 2:
        cellid16 = f"{RNC['2']:x}{int(cid):x}"
        return int(cellid16, 16)

def push_yalocator_api(mnc, lac, cid):
    """
    Принимает три параметра: mnc, lac, cid базовой станции
    Отправляет Запрос к API Яндекс.Локатора
    Возвращает словарь из mnc, координат и радиуса базовой станции
    Пример:
    {'position': {'latitude': 44.62639999389648, 'longitude': 40.06010818481445, 'altitude': 0.0, 'precision': 1038.5439453125, 'altitude_precision': 30.0, 'type': 'gsm'}}
    """

    data = f'json={{"common": {{"version": "1.0", "api_key": "{YANDEX_LOCATOR_TOKEN}"}}, "gsm_cells": [ {{ "countrycode": 250, "operatorid": {mnc}, "cellid": {cid}, "lac": {lac}, "signal_strength": -80, "age": 1000}} ]}}'

    # if len(str(cid)) == 5:
    #     cid = get_longcid(mnc, cid)

    response = requests.post(url=URL, data=data)

    if response.status_code == 200 and response.json()["position"]["latitude"] != 44.60668182373047:
        return {"mnc": mnc, "lac": lac, "cid": cid, "locator": response.json()}
    else:
        return None
