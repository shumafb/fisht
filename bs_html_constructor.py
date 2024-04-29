from bs4 import BeautifulSoup
from bs_yandex_locator import push_yalocator_api

operators = {1: "red", 2: "green", 20: "black", 99: "yellow"}

def bs_html_constructor(bs_list: list) -> str:
    """
    Строит html-файл с нанесенными базовыми станциями на карте
    Принимает список со значениями:
    {"mnc": mnc, "lac": lac, "cid": cid, "locator": "{'position': {'latitude': 44.62639999389648, 'longitude': 40.06010818481445, 'altitude': 0.0, 'precision': 1038.5439453125, 'altitude_precision': 30.0, 'type': 'gsm'}}"}
    Возвращает путь к htmtl файлу
    """
    with open("source/main.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    body = soup.find(id="locator")

    basestation_list = "        var map = L.map('map');\n"
    basestation_list += "        var coords = [\n"
    for bs in bs_list:
        basestation_list += f"            [{str(bs["locator"]["position"]["latitude"])[:9]}, {str(bs["locator"]["position"]["longitude"])[:9]}, '{bs["lac"]}-{bs["cid"]}', '{operators[bs["mnc"]]}'],\n" 
    basestation_list += "        ]\n"
    body.string = basestation_list + body.string


    with open("source/test.html", "w", encoding="utf-8") as f:
        f.write(str(soup))



x = list()
x.append(push_yalocator_api(2, 10106, 1294881))
x.append(push_yalocator_api(1, 10141, 59764))

bs_html_constructor(x)