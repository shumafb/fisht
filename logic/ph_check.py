import requests
from bs4 import BeautifulSoup


url_numvox = "http://num.voxlink.ru/get/?num="
url_smsbox = "https://mysmsbox.ru/phone-search/"
url_kodysu = 'https://www.kody.su/check-tel/'


def numvox(phone10: str) -> dict:
    """
    Определение оператора и региона российского номера
    """
    response = requests.get(url=url_numvox + str(phone10))
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_kodysu(phone: str) -> str | None:
    """_summary_

    Args:
        phone (_type_): _description_
    """
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'})
    data = {"number": phone}
    response = s.post(url=url_kodysu, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    info = soup.find_all("tr")[1].find_all("td")
    cards = []
    for card in info:
        cards.append(card.text)
    if response.status_code == 200:
        return cards[:-1]
    else:
        return None


def get_smsbox(phone: str) -> str:
    """Определение СПАМ-номеров

    Args:
        phone (str): номер телефона

    Returns:
        str: строка с информацией с mysmsbox.ru
    """
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
    )
    response = s.get(url_smsbox + phone)
    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.find("div", class_="breadcrumbs").find("h1").text
    phone_smsbox, info_smsbox = data.split("-")
    if response.status_code == 200:
        return phone_smsbox, info_smsbox
    else:
        return None

