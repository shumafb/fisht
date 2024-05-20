import sys
sys.path.append("..")
from ph_numvox_check import get_phone_info
from ph_clean_phone_number import clean_phone_number
from imei_luhn_alg import luhn
from imei_checker import check_imei


def test_get_phone_info():
    assert get_phone_info(9994442244) == {'code': '999', 'num': '4442244', 'full_num': '9994442244', 'operator': 'Интернод', 'region': 'г. Москва и Московская область'}
    assert get_phone_info(1992224422) == None


def test_clean_phone_number():
    assert clean_phone_number("+ 7 999 444 22 44") == "9994442244"
    assert clean_phone_number("8(999)4442222") == "9994442222"
    assert clean_phone_number("79998882424") == "9998882424"
    assert clean_phone_number("+7-999-444-25-25") == "9994442525"

def test_imei_luhn():
    assert luhn(35664511469235) == 356645114692355
    assert luhn("35664511469235") == 356645114692355

def test_imei_checker():
    assert check_imei(233500000000008) == None