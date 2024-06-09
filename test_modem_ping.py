from logic.sms_center import *

phone = 9994492792

x = send_sms(phone=phone)

y = "9994492792-lhWmON.txt"

msgid = check_sent_failed(y)

print(msgid)

# report = check_report(*msgid)
# print(report)