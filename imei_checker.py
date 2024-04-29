import requests


def check_imei(imei: int) -> dict:
    """
    Принимает IMEI из 15 цифр (14 + контрольный)
    Возвращает массив значений
    """
    response = requests.get(f"https://alpha.imeicheck.com/api/modelBrandName?imei={imei}&format=json")
    if response.status_code == 200:
        if response.json()["status"] == "succes":
            return response.json()
        else:
            return None
    else:
        return None
