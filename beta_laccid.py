from logic.bs_yandex_locator import push_yalocator_api, get_longcid
from logic.bs_html_constructor import bs_html_constructor

x = "99 2523 59330311\n" +\
    "99 2523 60175335\n" +\
    "99 3223 59504485\n" +\
    "99 63212 63976\n" +\
    "99 3223 60555131\n" +\
    "2 4737 9983\n" +\
    "2 4737 99832"


def yaloc(message: str):
    bslist = message.split("\n")
    yalocator_list = []
    for bs in bslist:
        mnc = bs.split(" ")[0]
        lac = bs.split(" ")[1]
        cid = bs.split(" ")[2]
        if len(bs.split(" ")[2]) == 5:
            cid = get_longcid(mnc, cid)
        if cid is None:
            continue
        yalocator_list.append(push_yalocator_api(mnc=mnc, lac=lac, cid=cid))
    bs_html_constructor(yalocator_list)

    return yalocator_list

print(yaloc(x))