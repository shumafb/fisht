import os.path
import random
import string
import os


def send_sms(phone: int, modem_id=1, send_mode=True) -> str:
    """
    Создает файл для последующей отправки sms server tools
    phone - номер телефона
    modem_id - номер модема, с которого осуществляется отправка
    send_mode - True для российских номеров, False - строгий режим для иностранных номеров
    Возвращает название созданного файла
    """
    send_file = f"sms/outgoing/{modem_id}/{phone}-{"".join(random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for x in range(6))}.txt"
    with open(send_file, "w", encoding="utf-8") as file:
        x = f"To: 7{phone}\n" if send_mode else f"To: {phone}\n"
        x += "Report: yes\n"
        x += "Ping: yes\n\n"
        file.write(x)
    return send_file[send_file.find("/outgoing/") + 12:]

def check_sent_failed(send_file: str) -> dict:
    """
    Проверка на наличие файла отправки в папках sent и failed
    Если есть в failed -> ошибка в отправки с нашей стороны
    Если есть в sent -> отправлено
    """
    try:
        if os.path.isfile(f"sms/sent/{send_file}"):
            return {"status": "Send", "path_file": f"sms/sent/{send_file}"}
        elif os.path.isfile(f"sms/failed/{send_file}"):
            return {"status": "Failed", "path_file": f"sms/failed/{send_file}"}
    except FileNotFoundError:
        pass
    else:
        return {"status": "None", "path_file": None}


def get_message_id(send_file: str) -> dict:
    """
    Возвращает message_id репорта и id модема
    send_file - название отчета о запросе отпраки смс
    """
    try:
        with open(f"sms/sent/{send_file}") as file:
            lines = file.readlines()
            for line in lines:
                modem_id = line.split()[1] if "Modem" in line else None
                message_id =line.split()[1] if "Message_id" in line else None
            return {"message_id": message_id, "modem_id": modem_id}
    except FileNotFoundError:
            pass


def check_report(message_id: int, send_file: str, modem_id: int) -> dict:
    """
    Проверка статуса о доставке смс в папке report
    message_id - id статуса об отправке
    send_file - название отчета о запросе отпраки смс
    modem_id - id модема
    Возвращает словарь с данными отчета    
    """
    for filename in os.listdir("sms/report"):
        if filename.startswith(f"GSM{modem_id}"):
            with open(f"sms/report/{filename}", "r", encoding="utf-8") as f:
                info = dict()
                for line in f.readlines():
                    if len(line.strip().split(": ")[1:]) > 0:
                        info[line.split(": ")[0]] = line.strip("\n").split(": ")[1:][0]
                        if str(message_id) == str(line.strip().split(": ")[1:][0]): # Поиск и сравнение заданного message_id и message_id в файле
                            return {"status": "Report", "info": info}
                    


def give_report_content(path_file: str) -> str:
    """
    Принимает путь к файлу
    Возвращает содержимое файла
    """
    with open(path_file, "r", encoding="utf-8") as f:
        return f.read()
