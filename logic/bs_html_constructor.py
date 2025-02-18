from bs4 import BeautifulSoup
import random
import string

operators = {"1": "red",
             "2": "green",
             "20": "black",
             "99": "yellow",
             '32': 'white',
             '62': 'lightblue',
             '60': 'white',
             '34': 'white',
             '33': 'white'}

62|32|60|34|33


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

    with open("source/bs_maps/map.html", "w", encoding="utf-8") as f:
        f.write(str(soup))