import requests

URL = "http://num.voxlink.ru/get/?num="

def get_phone_info(phone10: int) -> dict:
    """
    Принимает номер телефона России
    Возвращает массив:
    """
    return requests.get(url=URL+str(phone10)).json()