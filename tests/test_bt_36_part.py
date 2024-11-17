import pytest
from ted_and_doffin_to_ocds.converters.bt_36_part import (
    parse_part_duration,
    merge_part_duration,
    calculate_duration_in_days,
)


@pytest.fixture
def base_xml():
    """Base XML template for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="{unit}">{value}</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>"""


def test_parse_duration_days(base_xml):
    """Test parsing duration specified in days."""
    xml = base_xml.format(unit="DAY", value="3")
    result = parse_part_duration(xml)
    assert result == {"tender": {"contractPeriod": {"durationInDays": 3}}}


def test_parse_duration_months(base_xml):
    """Test parsing duration specified in months."""
    xml = base_xml.format(unit="MONTH", value="2")
    result = parse_part_duration(xml)
    assert result == {
        "tender": {
            "contractPeriod": {
                "durationInDays": 60  # 2 months * 30 days
            }
        }
    }


def test_parse_duration_years(base_xml):
    """Test parsing duration specified in years."""
    xml = base_xml.format(unit="YEAR", value="1")
    result = parse_part_duration(xml)
    assert result == {
        "tender": {
            "contractPeriod": {
                "durationInDays": 365  # 1 year * 365 days
            }
        }
    }


def test_parse_duration_weeks(base_xml):
    """Test parsing duration specified in weeks."""
    xml = base_xml.format(unit="WEEK", value="2")
    result = parse_part_duration(xml)
    assert result == {
        "tender": {
            "contractPeriod": {
                "durationInDays": 14  # 2 weeks * 7 days
            }
        }
    }


def test_parse_duration_weekdays(base_xml):
    """Test parsing duration specified in specific weekdays."""
    for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
        xml = base_xml.format(unit=day, value="3")
        result = parse_part_duration(xml)
        assert result == {
            "tender": {
                "contractPeriod": {
                    "durationInDays": 21  # 3 weeks * 7 days
                }
            }
        }


def test_parse_invalid_unit(base_xml):
    """Test parsing with invalid unit code."""
    xml = base_xml.format(unit="INVALID", value="3")
    result = parse_part_duration(xml)
    assert result is None


def test_parse_invalid_value(base_xml):
    """Test parsing with invalid duration value."""
    xml = base_xml.format(unit="DAY", value="invalid")
    result = parse_part_duration(xml)
    assert result is None


def test_parse_missing_unit():
    """Test parsing with missing unit code."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure>3</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>"""
    result = parse_part_duration(xml)
    assert result is None


def test_merge_duration():
    """Test merging duration data into release JSON."""
    release = {}
    duration_data = {"tender": {"contractPeriod": {"durationInDays": 30}}}
    merge_part_duration(release, duration_data)
    assert release == {"tender": {"contractPeriod": {"durationInDays": 30}}}


def test_merge_duration_existing_tender():
    """Test merging duration data with existing tender section."""
    release = {"tender": {"id": "123", "contractPeriod": {}}}
    duration_data = {"tender": {"contractPeriod": {"durationInDays": 30}}}
    merge_part_duration(release, duration_data)
    assert release == {
        "tender": {"id": "123", "contractPeriod": {"durationInDays": 30}}
    }


def test_merge_none_duration():
    """Test merging None duration data."""
    release = {"tender": {"id": "123"}}
    merge_part_duration(release, None)
    assert release == {"tender": {"id": "123"}}


def test_calculate_duration_days():
    """Test duration calculation for different unit codes."""
    assert calculate_duration_in_days(3, "DAY") == 3
    assert calculate_duration_in_days(2, "MONTH") == 60
    assert calculate_duration_in_days(1, "YEAR") == 365
    assert calculate_duration_in_days(2, "WEEK") == 14
    for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
        assert calculate_duration_in_days(3, day) == 21
    assert calculate_duration_in_days(3, "INVALID") is None


def test_part_duration_integration():
    """Integration test with full XML structure"""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">6</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractNotice>"""

    result = parse_part_duration(xml)
    expected = {
        "tender": {
            "contractPeriod": {
                "durationInDays": 180  # 6 months * 30 days
            }
        }
    }
    assert result == expected


def test_merge_duration_with_existing_data():
    """Test merging duration with pre-existing release data"""
    existing_release = {
        "tender": {
            "id": "test-tender",
            "title": "Test Tender",
            "contractPeriod": {"startDate": "2024-01-01"},
        }
    }

    duration_data = {"tender": {"contractPeriod": {"durationInDays": 90}}}

    merge_part_duration(existing_release, duration_data)

    assert existing_release["tender"]["contractPeriod"]["durationInDays"] == 90
    assert existing_release["tender"]["contractPeriod"]["startDate"] == "2024-01-01"
    assert existing_release["tender"]["id"] == "test-tender"
