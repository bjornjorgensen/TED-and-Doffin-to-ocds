# tests/test_bt_13_part.py

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


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


def test_bt_13_part_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_additional_information_deadline_part.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result
    assert "enquiryPeriod" in result["tender"]
    assert "endDate" in result["tender"]["enquiryPeriod"]
    assert result["tender"]["enquiryPeriod"]["endDate"] == "2019-11-08T18:00:00+01:00"


if __name__ == "__main__":
    pytest.main(["-v"])

import unittest
from lxml import etree
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.ted_and_doffin_to_ocds.converters.eforms.bt_13_part import (
    parse_additional_info_deadline_part,
    convert_to_iso_format,
)


class TestBT13Part(unittest.TestCase):
    def test_convert_to_iso_format(self):
        # Test with timezone in date only
        self.assertEqual(
            convert_to_iso_format("2019-11-08+01:00", "18:00:00"),
            "2019-11-08T18:00:00+01:00"
        )
        
        # Test with timezone in time only
        self.assertEqual(
            convert_to_iso_format("2019-11-08", "18:00:00+01:00"),
            "2019-11-08T18:00:00+01:00"
        )
        
        # Test with timezone in both (time should win)
        self.assertEqual(
            convert_to_iso_format("2019-11-08+02:00", "18:00:00+01:00"),
            "2019-11-08T18:00:00+01:00"
        )
        
        # Test without timezone
        self.assertEqual(
            convert_to_iso_format("2019-11-08", "18:00:00"),
            "2019-11-08T18:00:00"
        )
        
        # Test with negative timezone
        self.assertEqual(
            convert_to_iso_format("2019-11-08", "18:00:00-05:00"),
            "2019-11-08T18:00:00-05:00"
        )
        
        # Test with Z timezone
        self.assertEqual(
            convert_to_iso_format("2019-11-08Z", "18:00:00"),
            "2019-11-08T18:00:00Z"
        )
        
        # Test with milliseconds
        self.assertEqual(
            convert_to_iso_format("2019-11-08", "18:00:00.123+01:00"),
            "2019-11-08T18:00:00.123+01:00"
        )

    def test_parse_additional_info_deadline_part(self):
        # Test with correct case 'Part'
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:ProcurementProjectLot>
                <cbc:ID schemeName="Part">1</cbc:ID>
                <cac:TenderingProcess>
                    <cac:AdditionalInformationRequestPeriod>
                        <cbc:EndDate>2019-11-08+01:00</cbc:EndDate>
                        <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                    </cac:AdditionalInformationRequestPeriod>
                </cac:TenderingProcess>
            </cac:ProcurementProjectLot>
        </ContractAwardNotice>
        """
        result = parse_additional_info_deadline_part(xml_content)
        self.assertEqual(result, "2019-11-08T18:00:00+01:00")
        
        # Test with lowercase 'part' (should not match)
        xml_content_lowercase = """<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:ProcurementProjectLot>
                <cbc:ID schemeName="Part">1</cbc:ID>
                <cac:TenderingProcess>
                    <cac:AdditionalInformationRequestPeriod>
                        <cbc:EndDate>2019-11-08+01:00</cbc:EndDate>
                        <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                    </cac:AdditionalInformationRequestPeriod>
                </cac:TenderingProcess>
            </cac:ProcurementProjectLot>
        </ContractAwardNotice>
        """
        result_lowercase = parse_additional_info_deadline_part(xml_content_lowercase)
        self.assertIsNone(result_lowercase)
        
        # Test with different timezones
        xml_content_diff_tz = """<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:ProcurementProjectLot>
                <cbc:ID schemeName="Part">1</cbc:ID>
                <cac:TenderingProcess>
                    <cac:AdditionalInformationRequestPeriod>
                        <cbc:EndDate>2019-11-08+02:00</cbc:EndDate>
                        <cbc:EndTime>18:00:00+01:00</cbc:EndTime>
                    </cac:AdditionalInformationRequestPeriod>
                </cac:TenderingProcess>
            </cac:ProcurementProjectLot>
        </ContractAwardNotice>
        """
        result_diff_tz = parse_additional_info_deadline_part(xml_content_diff_tz)
        self.assertEqual(result_diff_tz, "2019-11-08T18:00:00+01:00")
        
        # Test with Z timezone
        xml_content_z = """<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:ProcurementProjectLot>
                <cbc:ID schemeName="Part">1</cbc:ID>
                <cac:TenderingProcess>
                    <cac:AdditionalInformationRequestPeriod>
                        <cbc:EndDate>2019-11-08Z</cbc:EndDate>
                        <cbc:EndTime>18:00:00Z</cbc:EndTime>
                    </cac:AdditionalInformationRequestPeriod>
                </cac:TenderingProcess>
            </cac:ProcurementProjectLot>
        </ContractAwardNotice>
        """
        result_z = parse_additional_info_deadline_part(xml_content_z)
        self.assertEqual(result_z, "2019-11-08T18:00:00Z")


if __name__ == "__main__":
    unittest.main()
