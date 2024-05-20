import requests


def check_imei(imei: int) -> dict:
    """
    Принимает IMEI из 15 цифр (14 + контрольный)
    Возвращает массив значений
    """
    response = requests.get(f"https://alpha.imeicheck.com/api/modelBrandName?imei={imei}&format=json")

    model_dict = dict()

    if response.status_code == 200:
        if response.json()["status"] == "succes":
            response = response.json()
            img_path = f"https://fdn2.gsmarena.com/vv/bigpic/{response['object']["brand"].lower()}-{response['object']["name"].replace(" ", "-").lower()}.jpg"
            if requests.get(img_path).status_code == 200:
                response["object"]["image"] = img_path
            else:
                response["object"]["image"] = None
            return response
        else:
            return None
    else:
        return None
    
print(check_imei(356645114692355))