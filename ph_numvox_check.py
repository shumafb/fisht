import requests

URL = "http://num.voxlink.ru/get/?num="

def get_phone_info(phone10):
    """
    Принимает номер телефона России
    Возвращает массив:
    {'code': '999', 'num': '4449922', 'full_num': '9994449922', 'operator': 'МЕГАФОН', 'region': 'Республика Адыгея'
    """
    return requests.get(url=URL+phone10).json()
