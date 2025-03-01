# tests/test_bt_13_Lot.py

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_13_lot import convert_to_iso_format


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_13_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AdditionalInformationRequestPeriod>
                    <cbc:EndDate>2019-11-08+01:00</cbc:EndDate>
                    <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                </cac:AdditionalInformationRequestPeriod>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_additional_information_deadline.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "enquiryPeriod" in lot
    assert "endDate" in lot["enquiryPeriod"]
    assert lot["enquiryPeriod"]["endDate"] == "2019-11-08T18:00:00+01:00"


def test_convert_to_iso_format_timezone_in_date():
    """Test convert_to_iso_format with timezone information in date string."""
    date_string = "2023-05-15+02:00"
    time_string = "14:30:00"
    expected = "2023-05-15T14:30:00+02:00"
    result = convert_to_iso_format(date_string, time_string)
    assert result == expected

def test_convert_to_iso_format_timezone_in_time():
    """Test convert_to_iso_format with timezone information in time string."""
    date_string = "2023-05-15"
    time_string = "14:30:00+02:00"
    expected = "2023-05-15T14:30:00+02:00"
    result = convert_to_iso_format(date_string, time_string)
    assert result == expected

def test_convert_to_iso_format_timezone_in_both():
    """Test convert_to_iso_format with timezone information in both strings (date should take precedence)."""
    date_string = "2023-05-15+02:00"
    time_string = "14:30:00+01:00"
    expected = "2023-05-15T14:30:00+02:00"
    result = convert_to_iso_format(date_string, time_string)
    assert result == expected

def test_convert_to_iso_format_no_timezone():
    """Test convert_to_iso_format with no timezone information."""
    date_string = "2023-05-15"
    time_string = "14:30:00"
    expected = "2023-05-15T14:30:00"
    result = convert_to_iso_format(date_string, time_string)
    assert result == expected

def test_convert_to_iso_format_invalid_format():
    """Test convert_to_iso_format with invalid date/time format."""
    date_string = "2023/05/15+02:00"  # Invalid format
    time_string = "14:30:00"
    expected = "2023/05/15T14:30:00+02:00"  # Should use fallback
    result = convert_to_iso_format(date_string, time_string)
    assert result == expected


if __name__ == "__main__":
    pytest.main(["-v"])
