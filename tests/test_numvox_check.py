import pytest
import sys
sys.path.append("..")
import ph_numvox_check

def test_get_phone_info():
    assert ph_numvox_check.get_phone_info(9994442244) == {'code': '999', 'num': '4442244', 'full_num': '9994442244', 'operator': 'Интернод', 'region': 'г. Москва и Московская область'}