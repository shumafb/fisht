from logic.sms_center import *


x = "79894495498-mqiSjj.txt"

y = check_sent_failed(x)

message_id = y["info"]["Message_id"]
modem_id = y["info"]["Modem"][-1:]

print(y)
print(message_id, modem_id)
z = check_report(message_id, modem_id)
print(z)
if z is not None:
    y.update(z)

print(y)
