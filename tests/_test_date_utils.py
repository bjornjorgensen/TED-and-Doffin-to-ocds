# tests/test_date_utils.py

import pytest
import pytest
import json
import os
import sys
# Add the parent directory to sys.path to import main and the converter functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.date_utils import convert_to_iso_format

def test_full_iso_date_time_utc():
    assert convert_to_iso_format('2014-10-21T09:30:00Z') == '2014-10-21T09:30:00Z'

def test_full_iso_date_time_with_offset():
    assert convert_to_iso_format('2014-11-18T18:00:00-06:00') == '2014-11-18T18:00:00-06:00'

def test_date_only():
    assert convert_to_iso_format('2014-10-21') == '2014-10-21T23:59:59Z'

def test_date_time_without_seconds():
    assert convert_to_iso_format('2014-10-21T18:00') == '2014-10-21T18:00:00Z'

def test_date_time_without_timezone():
    assert convert_to_iso_format('2014-11-18T18:00:00') == '2014-11-18T18:00:00Z'

def test_date_time_with_positive_offset():
    assert convert_to_iso_format('2014-11-18T18:00:00+02:00') == '2014-11-18T18:00:00+02:00'

def test_date_with_time_z():
    assert convert_to_iso_format('2014-11-18T18:00:00Z') == '2014-11-18T18:00:00Z'

def test_invalid_format():
    with pytest.raises(ValueError):
        convert_to_iso_format('11/18/2014 18:00')

def test_invalid_date():
    with pytest.raises(ValueError):
        convert_to_iso_format('2014-13-45')

def test_invalid_time():
    with pytest.raises(ValueError):
        convert_to_iso_format('2014-11-18T25:00:00')

def test_invalid_timezone():
    with pytest.raises(ValueError):
        convert_to_iso_format('2014-11-18T18:00:00+24:00')

def test_date_with_milliseconds():
    assert convert_to_iso_format('2014-11-18T18:00:00.123Z') == '2014-11-18T18:00:00.123000Z'

def test_date_with_microseconds():
    assert convert_to_iso_format('2014-11-18T18:00:00.123456Z') == '2014-11-18T18:00:00.123456Z'

def test_leap_year_date():
    assert convert_to_iso_format('2020-02-29') == '2020-02-29T23:59:59Z'

def test_non_leap_year_date():
    with pytest.raises(ValueError):
        convert_to_iso_format('2019-02-29')