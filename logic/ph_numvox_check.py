import requests

URL = "http://num.voxlink.ru/get/?num="

def get_phone_info(phone10: str) -> dict:
    """
    Принимает номер телефона России
    Возвращает массив:
    """
    response = requests.get(url=URL+str(phone10))
    if response.status_code == 200:
        return response.json()
    else:
        return None